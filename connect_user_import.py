#!/usr/bin/env python3
"""
Amazon Connect User Profile Import Script
Imports user profiles with complete configurations into an Amazon Connect instance.
Handles batch processing and large datasets (10K+ users).
"""

import boto3
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from botocore.exceptions import ClientError, BotoCoreError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('connect_import.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_run_separator(script_name: str, action: str = "START"):
    """
    Log a clear separator for run identification
    
    Args:
        script_name: Name of the script
        action: START or END
    """
    separator = "=" * 80
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if action == "START":
        logger.info(separator)
        logger.info(f">> {script_name} - RUN STARTED at {timestamp}")
        logger.info(separator)
    elif action == "END":
        logger.info(separator)
        logger.info(f"<< {script_name} - RUN COMPLETED at {timestamp}")
        logger.info(separator)
        logger.info("")  # Empty line for visual separation

class ConnectUserImporter:
    def __init__(self, instance_id: str, region: str = 'us-east-1', profile: Optional[str] = None):
        """
        Initialize the Connect User Importer
        
        Args:
            instance_id: Target Amazon Connect instance ID
            region: AWS region
            profile: AWS profile name (optional)
        """
        self.instance_id = instance_id
        self.region = region
        
        # Initialize AWS session and client
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.connect_client = session.client('connect', region_name=region)
        
        # Cache for mapping old IDs to new IDs
        self.routing_profile_map = {}
        self.security_profile_map = {}
        self.hierarchy_group_map = {}
        
        logger.info(f"Initialized importer for instance: {instance_id} in region: {region}")
    
    def load_export_data(self, export_file: str) -> Dict:
        """
        Load exported user data from JSON file
        
        Args:
            export_file: Path to the export file
            
        Returns:
            Parsed export data
        """
        try:
            with open(export_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loaded export data from {export_file}")
            logger.info(f"Total users in export: {data.get('TotalUsers', 0)}")
            
            return data
            
        except FileNotFoundError:
            logger.error(f"Export file not found: {export_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in export file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading export file: {e}")
            raise
    
    def get_existing_resources(self) -> Dict:
        """
        Get existing resources in the target instance for mapping
        
        Returns:
            Dictionary of existing resources
        """
        resources = {
            'routing_profiles': {},
            'security_profiles': {},
            'hierarchy_groups': {}
        }
        
        try:
            # Get routing profiles
            logger.info("Fetching existing routing profiles...")
            routing_paginator = self.connect_client.get_paginator('list_routing_profiles')
            for page in routing_paginator.paginate(InstanceId=self.instance_id):
                for profile in page.get('RoutingProfileSummaryList', []):
                    resources['routing_profiles'][profile['Name']] = profile['Id']
            
            # Get security profiles
            logger.info("Fetching existing security profiles...")
            security_paginator = self.connect_client.get_paginator('list_security_profiles')
            for page in security_paginator.paginate(InstanceId=self.instance_id):
                for profile in page.get('SecurityProfileSummaryList', []):
                    # Handle different possible field names for security profile name
                    profile_name = profile.get('SecurityProfileName') or profile.get('Name')
                    if profile_name:
                        resources['security_profiles'][profile_name] = profile['Id']
                    else:
                        logger.warning(f"Security profile missing name field in target instance: {profile}")
            
            # Get hierarchy groups
            logger.info("Fetching existing hierarchy groups...")
            hierarchy_paginator = self.connect_client.get_paginator('list_user_hierarchy_groups')
            for page in hierarchy_paginator.paginate(InstanceId=self.instance_id):
                for group in page.get('UserHierarchyGroupSummaryList', []):
                    resources['hierarchy_groups'][group['Name']] = group['Id']
            
            logger.info(f"Found {len(resources['routing_profiles'])} routing profiles")
            logger.info(f"Found {len(resources['security_profiles'])} security profiles")
            logger.info(f"Found {len(resources['hierarchy_groups'])} hierarchy groups")
            
            return resources
            
        except ClientError as e:
            logger.error(f"Error fetching existing resources: {e}")
            raise
    
    def create_missing_routing_profile(self, routing_profile: Dict) -> str:
        """
        Create a routing profile if it doesn't exist
        
        Args:
            routing_profile: Routing profile configuration
            
        Returns:
            Routing profile ID
        """
        try:
            # Prepare routing profile creation parameters
            create_params = {
                'InstanceId': self.instance_id,
                'Name': routing_profile['Name'],
                'Description': routing_profile.get('Description', ''),
                'DefaultOutboundQueueId': routing_profile['DefaultOutboundQueueId'],
                'MediaConcurrencies': routing_profile['MediaConcurrencies']
            }
            
            # Add optional parameters if they exist
            if routing_profile.get('QueueConfigs'):
                create_params['QueueConfigs'] = routing_profile['QueueConfigs']
            
            # Add tags if they exist
            if routing_profile.get('Tags'):
                create_params['Tags'] = routing_profile['Tags']
            
            response = self.connect_client.create_routing_profile(**create_params)
            
            new_id = response['RoutingProfileId']
            logger.info(f"Created routing profile: {routing_profile['Name']} -> {new_id}")
            
            return new_id
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'DuplicateResourceException':
                logger.warning(f"Routing profile already exists: {routing_profile['Name']}")
                # Try to find the existing profile
                return self.find_routing_profile_by_name(routing_profile['Name'])
            else:
                logger.error(f"Error creating routing profile {routing_profile['Name']}: {e}")
                raise
    
    def find_routing_profile_by_name(self, name: str) -> Optional[str]:
        """Find routing profile ID by name"""
        try:
            paginator = self.connect_client.get_paginator('list_routing_profiles')
            for page in paginator.paginate(InstanceId=self.instance_id):
                for profile in page.get('RoutingProfileSummaryList', []):
                    if profile['Name'] == name:
                        return profile['Id']
            return None
        except Exception as e:
            logger.error(f"Error finding routing profile by name {name}: {e}")
            return None
    
    def map_resource_ids(self, user_data: Dict, existing_resources: Dict) -> Tuple[str, List[str], Optional[str]]:
        """
        Map old resource IDs to new instance IDs
        
        Args:
            user_data: User data from export
            existing_resources: Existing resources in target instance
            
        Returns:
            Tuple of (routing_profile_id, security_profile_ids, hierarchy_group_id)
        """
        routing_profile_id = None
        security_profile_ids = []
        hierarchy_group_id = None
        
        # Map routing profile
        if user_data.get('RoutingProfile'):
            routing_profile_name = user_data['RoutingProfile']['Name']
            routing_profile_id = existing_resources['routing_profiles'].get(routing_profile_name)
            
            if not routing_profile_id:
                logger.warning(f"Routing profile not found: {routing_profile_name}")
                # Optionally create the routing profile
                try:
                    routing_profile_id = self.create_missing_routing_profile(user_data['RoutingProfile'])
                except Exception as e:
                    logger.error(f"Failed to create routing profile {routing_profile_name}: {e}")
        
        # Map security profiles
        for security_profile in user_data.get('SecurityProfiles', []):
            # Handle different possible field names for security profile name
            security_profile_name = None
            if 'SecurityProfileName' in security_profile:
                security_profile_name = security_profile['SecurityProfileName']
            elif 'Name' in security_profile:
                security_profile_name = security_profile['Name']
            else:
                logger.error(f"Security profile missing name field. Available fields: {list(security_profile.keys())}")
                continue
            
            security_profile_id = existing_resources['security_profiles'].get(security_profile_name)
            
            if security_profile_id:
                security_profile_ids.append(security_profile_id)
                logger.debug(f"Mapped security profile: {security_profile_name} -> {security_profile_id}")
            else:
                logger.warning(f"Security profile not found in target instance: '{security_profile_name}'")
                logger.info(f"Available security profiles in target: {list(existing_resources['security_profiles'].keys())}")
        
        # Map hierarchy group
        if user_data.get('HierarchyGroup'):
            hierarchy_group_name = user_data['HierarchyGroup']['Name']
            hierarchy_group_id = existing_resources['hierarchy_groups'].get(hierarchy_group_name)
            
            if not hierarchy_group_id:
                logger.warning(f"Hierarchy group not found: {hierarchy_group_name}")
        
        return routing_profile_id, security_profile_ids, hierarchy_group_id
    
    def create_user(self, user_data: Dict, existing_resources: Dict) -> bool:
        """
        Create a single user in the target instance
        
        Args:
            user_data: Complete user data from export
            existing_resources: Existing resources for mapping
            
        Returns:
            True if successful, False otherwise
        """
        user_info = user_data['User']
        username = user_info['Username']
        
        try:
            # Map resource IDs
            routing_profile_id, security_profile_ids, hierarchy_group_id = self.map_resource_ids(
                user_data, existing_resources
            )
            
            if not routing_profile_id:
                logger.error(f"Cannot create user {username}: No valid routing profile")
                return False
            
            if not security_profile_ids:
                # Log detailed information about missing security profiles
                user_security_profiles = [
                    sp.get('SecurityProfileName') or sp.get('Name', 'Unknown') 
                    for sp in user_data.get('SecurityProfiles', [])
                ]
                logger.error(f"Cannot create user {username}: No valid security profiles found")
                logger.error(f"User {username} requires security profiles: {user_security_profiles}")
                logger.error(f"Available security profiles in target instance: {list(existing_resources['security_profiles'].keys())}")
                return False
            
            # Prepare user creation parameters
            create_params = {
                'Username': username,
                'InstanceId': self.instance_id,
                'RoutingProfileId': routing_profile_id,
                'SecurityProfileIds': security_profile_ids
            }
            
            # Add optional parameters
            if user_info.get('IdentityInfo'):
                create_params['IdentityInfo'] = user_info['IdentityInfo']
            
            if user_info.get('PhoneConfig'):
                create_params['PhoneConfig'] = user_info['PhoneConfig']
            
            if hierarchy_group_id:
                create_params['HierarchyGroupId'] = hierarchy_group_id
            
            if user_info.get('DirectoryUserId'):
                create_params['DirectoryUserId'] = user_info['DirectoryUserId']
            
            if user_info.get('Tags'):
                create_params['Tags'] = user_info['Tags']
            
            # Create the user
            response = self.connect_client.create_user(**create_params)
            
            new_user_id = response['UserId']
            logger.info(f"Created user: {username} -> {new_user_id}")
            
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'DuplicateResourceException':
                logger.warning(f"User already exists: {username}")
                return True  # Consider existing user as success
            else:
                logger.error(f"Error creating user {username}: {e}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error creating user {username}: {e}")
            return False
    
    def analyze_security_profiles(self, users_data: List[Dict], existing_resources: Dict) -> Dict:
        """
        Analyze security profile requirements and availability
        
        Args:
            users_data: List of user data from export
            existing_resources: Existing resources in target instance
            
        Returns:
            Analysis results with missing profiles and affected users
        """
        required_profiles = set()
        profile_usage = {}
        
        # Collect all required security profiles
        for user_data in users_data:
            username = user_data['User']['Username']
            user_profiles = []
            
            for security_profile in user_data.get('SecurityProfiles', []):
                # Handle different possible field names
                profile_name = security_profile.get('SecurityProfileName') or security_profile.get('Name')
                if profile_name:
                    required_profiles.add(profile_name)
                    user_profiles.append(profile_name)
                    
                    if profile_name not in profile_usage:
                        profile_usage[profile_name] = []
                    profile_usage[profile_name].append(username)
        
        available_profiles = set(existing_resources['security_profiles'].keys())
        missing_profiles = required_profiles - available_profiles
        
        # Analyze impact
        affected_users = set()
        for missing_profile in missing_profiles:
            affected_users.update(profile_usage.get(missing_profile, []))
        
        analysis = {
            'required_profiles': required_profiles,
            'available_profiles': available_profiles,
            'missing_profiles': missing_profiles,
            'affected_users': affected_users,
            'profile_usage': profile_usage
        }
        
        # Log analysis results
        logger.info(f"Security Profile Analysis:")
        logger.info(f"  Required profiles: {len(required_profiles)}")
        logger.info(f"  Available in target: {len(available_profiles)}")
        logger.info(f"  Missing profiles: {len(missing_profiles)}")
        logger.info(f"  Users affected by missing profiles: {len(affected_users)}")
        
        if missing_profiles:
            logger.warning(f"Missing security profiles: {sorted(missing_profiles)}")
            for missing_profile in sorted(missing_profiles):
                users_with_profile = profile_usage.get(missing_profile, [])
                logger.warning(f"  '{missing_profile}' needed by {len(users_with_profile)} users: {users_with_profile[:5]}{'...' if len(users_with_profile) > 5 else ''}")
        
        return analysis
    
    def import_users(self, export_file: str, batch_size: int = 50, dry_run: bool = False) -> Dict:
        """
        Import users from export file
        
        Args:
            export_file: Path to the export file
            batch_size: Number of users to process in each batch
            dry_run: If True, only validate without creating users
            
        Returns:
            Import results summary
        """
        # Log run start
        log_run_separator("USER IMPORT", "START")
        
        logger.info(f"Starting user import process (dry_run={dry_run})...")
        
        # Load export data
        export_data = self.load_export_data(export_file)
        users_to_import = export_data.get('Users', [])
        
        if not users_to_import:
            logger.warning("No users found in export file")
            log_run_separator("USER IMPORT", "END")
            return {'success': 0, 'failed': 0, 'skipped': 0}
        
        # Get existing resources for mapping
        existing_resources = self.get_existing_resources()
        
        # Analyze security profile requirements
        security_analysis = self.analyze_security_profiles(users_to_import, existing_resources)
        
        if security_analysis['missing_profiles'] and not dry_run:
            logger.error("Cannot proceed with import due to missing security profiles!")
            logger.error("Please create the missing security profiles in the target instance first.")
            logger.error("Or run with --dry-run to see detailed analysis.")
            return {
                'success': 0, 
                'failed': len(security_analysis['affected_users']), 
                'skipped': 0,
                'failed_users': list(security_analysis['affected_users']),
                'missing_security_profiles': list(security_analysis['missing_profiles'])
            }
        
        # Import statistics
        results = {
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'failed_users': []
        }
        
        # Process users in batches
        total_users = len(users_to_import)
        
        for i in range(0, total_users, batch_size):
            batch = users_to_import[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_users + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} users)")
            
            for user_data in batch:
                username = user_data['User']['Username']
                
                try:
                    if dry_run:
                        # Validate mapping without creating
                        routing_profile_id, security_profile_ids, hierarchy_group_id = self.map_resource_ids(
                            user_data, existing_resources
                        )
                        
                        if routing_profile_id and security_profile_ids:
                            logger.info(f"[DRY RUN] Would create user: {username}")
                            results['success'] += 1
                        else:
                            logger.warning(f"[DRY RUN] Would skip user: {username} (missing resources)")
                            results['skipped'] += 1
                    else:
                        # Actually create the user
                        if self.create_user(user_data, existing_resources):
                            results['success'] += 1
                        else:
                            results['failed'] += 1
                            results['failed_users'].append(username)
                
                except Exception as e:
                    logger.error(f"Error processing user {username}: {e}")
                    results['failed'] += 1
                    results['failed_users'].append(username)
            
            # Rate limiting between batches
            if not dry_run and batch_num < total_batches:
                logger.info("Waiting between batches...")
                time.sleep(2)
        
        # Log final results
        logger.info("Import process completed!")
        logger.info(f"Successful: {results['success']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Skipped: {results['skipped']}")
        
        if results['failed_users']:
            logger.info(f"Failed users: {', '.join(results['failed_users'][:10])}")
            if len(results['failed_users']) > 10:
                logger.info(f"... and {len(results['failed_users']) - 10} more")
        
        # Log run end
        log_run_separator("USER IMPORT", "END")
        
        return results

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import Amazon Connect user profiles')
    parser.add_argument('--instance-id', required=True, help='Target Amazon Connect instance ID')
    parser.add_argument('--export-file', required=True, help='Path to the export file')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--profile', help='AWS profile name')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for processing')
    parser.add_argument('--dry-run', action='store_true', help='Validate without creating users')
    
    args = parser.parse_args()
    
    try:
        importer = ConnectUserImporter(
            instance_id=args.instance_id,
            region=args.region,
            profile=args.profile
        )
        
        results = importer.import_users(
            export_file=args.export_file,
            batch_size=args.batch_size,
            dry_run=args.dry_run
        )
        
        print(f"Import completed - Success: {results['success']}, Failed: {results['failed']}, Skipped: {results['skipped']}")
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()