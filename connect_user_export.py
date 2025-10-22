#!/usr/bin/env python3
"""
Amazon Connect User Profile Export Script
Exports all user profiles with complete configurations from an Amazon Connect instance.
Handles pagination and large datasets (10K+ users).
"""

import boto3
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
from botocore.exceptions import ClientError, BotoCoreError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('connect_export.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConnectUserExporter:
    def __init__(self, instance_id: str, region: str = 'us-east-1', profile: Optional[str] = None):
        """
        Initialize the Connect User Exporter
        
        Args:
            instance_id: Amazon Connect instance ID
            region: AWS region
            profile: AWS profile name (optional)
        """
        self.instance_id = instance_id
        self.region = region
        
        # Initialize AWS session and client
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.connect_client = session.client('connect', region_name=region)
        
        logger.info(f"Initialized exporter for instance: {instance_id} in region: {region}")
    
    def get_all_users(self) -> List[Dict]:
        """
        Retrieve all users from the Connect instance with pagination support
        
        Returns:
            List of user summaries
        """
        users = []
        next_token = None
        page_count = 0
        
        try:
            while True:
                page_count += 1
                logger.info(f"Fetching users page {page_count}...")
                
                params = {
                    'InstanceId': self.instance_id,
                    'MaxResults': 1000  # Maximum allowed by API
                }
                
                if next_token:
                    params['NextToken'] = next_token
                
                response = self.connect_client.list_users(**params)
                
                page_users = response.get('UserSummaryList', [])
                users.extend(page_users)
                
                logger.info(f"Retrieved {len(page_users)} users from page {page_count}")
                
                next_token = response.get('NextToken')
                if not next_token:
                    break
                
                # Rate limiting to avoid throttling
                time.sleep(0.1)
            
            logger.info(f"Total users retrieved: {len(users)}")
            return users
            
        except ClientError as e:
            logger.error(f"AWS API error while fetching users: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching users: {e}")
            raise
    
    def get_user_details(self, user_id: str) -> Dict:
        """
        Get detailed user information including all configurations
        
        Args:
            user_id: User ID to fetch details for
            
        Returns:
            Complete user profile data
        """
        try:
            # Get basic user info
            user_response = self.connect_client.describe_user(
                UserId=user_id,
                InstanceId=self.instance_id
            )
            
            user_data = user_response['User']
            
            # Get user hierarchy group if assigned
            hierarchy_group = None
            if user_data.get('HierarchyGroupId'):
                try:
                    hierarchy_response = self.connect_client.describe_user_hierarchy_group(
                        HierarchyGroupId=user_data['HierarchyGroupId'],
                        InstanceId=self.instance_id
                    )
                    hierarchy_group = hierarchy_response['HierarchyGroup']
                except ClientError as e:
                    logger.warning(f"Could not fetch hierarchy group for user {user_id}: {e}")
            
            # Get routing profile details
            routing_profile = None
            if user_data.get('RoutingProfileId'):
                try:
                    routing_response = self.connect_client.describe_routing_profile(
                        InstanceId=self.instance_id,
                        RoutingProfileId=user_data['RoutingProfileId']
                    )
                    routing_profile = routing_response['RoutingProfile']
                except ClientError as e:
                    logger.warning(f"Could not fetch routing profile for user {user_id}: {e}")
            
            # Get security profile details
            security_profiles = []
            for security_profile_id in user_data.get('SecurityProfileIds', []):
                try:
                    security_response = self.connect_client.describe_security_profile(
                        SecurityProfileId=security_profile_id,
                        InstanceId=self.instance_id
                    )
                    security_profiles.append(security_response['SecurityProfile'])
                except ClientError as e:
                    logger.warning(f"Could not fetch security profile {security_profile_id} for user {user_id}: {e}")
            
            # Compile complete user profile
            complete_profile = {
                'User': user_data,
                'HierarchyGroup': hierarchy_group,
                'RoutingProfile': routing_profile,
                'SecurityProfiles': security_profiles,
                'ExportTimestamp': datetime.utcnow().isoformat()
            }
            
            return complete_profile
            
        except ClientError as e:
            logger.error(f"AWS API error while fetching user details for {user_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching user details for {user_id}: {e}")
            raise
    
    def export_users(self, output_file: str = None) -> str:
        """
        Export all users with complete configurations
        
        Args:
            output_file: Output file path (optional)
            
        Returns:
            Path to the exported file
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"connect_users_export_{self.instance_id}_{timestamp}.json"
        
        logger.info("Starting user export process...")
        
        # Get all users
        users = self.get_all_users()
        
        if not users:
            logger.warning("No users found to export")
            return output_file
        
        exported_users = []
        failed_exports = []
        
        for i, user_summary in enumerate(users, 1):
            user_id = user_summary['Id']
            username = user_summary.get('Username', 'Unknown')
            
            try:
                logger.info(f"Exporting user {i}/{len(users)}: {username} ({user_id})")
                
                user_details = self.get_user_details(user_id)
                exported_users.append(user_details)
                
                # Rate limiting
                if i % 10 == 0:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Failed to export user {username} ({user_id}): {e}")
                failed_exports.append({
                    'UserId': user_id,
                    'Username': username,
                    'Error': str(e)
                })
        
        # Prepare export data
        export_data = {
            'InstanceId': self.instance_id,
            'ExportTimestamp': datetime.utcnow().isoformat(),
            'TotalUsers': len(users),
            'SuccessfulExports': len(exported_users),
            'FailedExports': len(failed_exports),
            'Users': exported_users,
            'FailedUsers': failed_exports
        }
        
        # Write to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Export completed successfully!")
            logger.info(f"Exported {len(exported_users)} users to {output_file}")
            logger.info(f"Failed exports: {len(failed_exports)}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to write export file: {e}")
            raise

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Export Amazon Connect user profiles')
    parser.add_argument('--instance-id', required=True, help='Amazon Connect instance ID')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--profile', help='AWS profile name')
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    try:
        exporter = ConnectUserExporter(
            instance_id=args.instance_id,
            region=args.region,
            profile=args.profile
        )
        
        output_file = exporter.export_users(args.output)
        print(f"Export completed: {output_file}")
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()