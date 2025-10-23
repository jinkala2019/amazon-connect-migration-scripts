#!/usr/bin/env python3
"""
Amazon Connect Quick Connect Import Script
Imports quick connects with complete configurations into an Amazon Connect instance.
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
        logging.FileHandler('connect_quick_connect_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConnectQuickConnectImporter:
    def __init__(self, instance_id: str, region: str = 'us-east-1', profile: Optional[str] = None):
        """
        Initialize the Connect Quick Connect Importer
        
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
        
        logger.info(f"Initialized quick connect importer for instance: {instance_id} in region: {region}")
    
    def load_export_data(self, export_file: str) -> Dict:
        """
        Load exported quick connect data from JSON file
        
        Args:
            export_file: Path to the export file
            
        Returns:
            Parsed export data
        """
        try:
            with open(export_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loaded export data from {export_file}")
            logger.info(f"Total quick connects in export: {data.get('TotalQuickConnects', 0)}")
            
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
    
    def get_existing_quick_connects(self) -> Dict[str, str]:
        """
        Get existing quick connects in the target instance for mapping
        
        Returns:
            Dictionary mapping quick connect names to IDs
        """
        existing_qcs = {}
        
        try:
            logger.info("Fetching existing quick connects...")
            paginator = self.connect_client.get_paginator('list_quick_connects')
            for page in paginator.paginate(InstanceId=self.instance_id):
                for qc in page.get('QuickConnectSummaryList', []):
                    existing_qcs[qc['Name']] = qc['Id']
            
            logger.info(f"Found {len(existing_qcs)} existing quick connects")
            return existing_qcs
            
        except ClientError as e:
            logger.error(f"Error fetching existing quick connects: {e}")
            raise
    
    def get_existing_resources(self) -> Dict:
        """
        Get existing resources (users, queues) for quick connect mapping
        
        Returns:
            Dictionary of existing resources
        """
        resources = {
            'users': {},
            'queues': {}
        }
        
        try:
            # Get users
            logger.info("Fetching existing users for quick connect mapping...")
            user_paginator = self.connect_client.get_paginator('list_users')
            for page in user_paginator.paginate(InstanceId=self.instance_id):
                for user in page.get('UserSummaryList', []):
                    resources['users'][user['Username']] = user['Id']
            
            # Get queues
            logger.info("Fetching existing queues for quick connect mapping...")
            queue_paginator = self.connect_client.get_paginator('list_queues')
            for page in queue_paginator.paginate(InstanceId=self.instance_id):
                for queue in page.get('QueueSummaryList', []):
                    resources['queues'][queue['Name']] = queue['Id']
            
            logger.info(f"Found {len(resources['users'])} users and {len(resources['queues'])} queues")
            return resources
            
        except ClientError as e:
            logger.error(f"Error fetching existing resources: {e}")
            raise
    
    def map_quick_connect_config(self, qc_config: Dict, existing_resources: Dict) -> Dict:
        """
        Map quick connect configuration to target instance resources
        
        Args:
            qc_config: Quick connect configuration
            existing_resources: Existing resources in target instance
            
        Returns:
            Mapped quick connect configuration
        """
        mapped_config = qc_config.copy()
        
        if qc_config['QuickConnectType'] == 'USER':
            # Map user ID
            user_id = qc_config.get('UserConfig', {}).get('UserId')
            if user_id:
                # Try to find user by username (would need additional lookup)
                logger.warning(f"User mapping for quick connect not fully implemented - using original ID: {user_id}")
        
        elif qc_config['QuickConnectType'] == 'QUEUE':
            # Map queue ID
            queue_id = qc_config.get('QueueConfig', {}).get('QueueId')
            if queue_id:
                # Try to find queue by name (would need additional lookup)
                logger.warning(f"Queue mapping for quick connect not fully implemented - using original ID: {queue_id}")
        
        elif qc_config['QuickConnectType'] == 'PHONE_NUMBER':
            # Phone number configs don't need mapping
            pass
        
        return mapped_config
    
    def create_quick_connect(self, qc_data: Dict, existing_resources: Dict) -> bool:
        """
        Create a single quick connect in the target instance
        
        Args:
            qc_data: Complete quick connect data from export
            existing_resources: Existing resources for mapping
            
        Returns:
            True if successful, False otherwise
        """
        qc_info = qc_data.get('QuickConnect', {})
        qc_name = qc_info.get('Name')
        
        if not qc_name:
            logger.error(f"Quick connect missing 'Name' field: {qc_data}")
            return False
        
        try:
            # Map quick connect configuration
            mapped_config = self.map_quick_connect_config(qc_info['QuickConnectConfig'], existing_resources)
            
            # Prepare quick connect creation parameters
            create_params = {
                'InstanceId': self.instance_id,
                'Name': qc_name,
                'Description': qc_info.get('Description', ''),
                'QuickConnectConfig': mapped_config
            }
            
            # Add tags if they exist
            if qc_data.get('Tags'):
                create_params['Tags'] = qc_data['Tags']
            
            # Create the quick connect
            response = self.connect_client.create_quick_connect(**create_params)
            
            new_qc_id = response['QuickConnectId']
            logger.info(f"Created quick connect: {qc_name} -> {new_qc_id}")
            
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'DuplicateResourceException':
                logger.warning(f"Quick connect already exists: {qc_name}")
                return True  # Consider existing as success
            else:
                logger.error(f"Error creating quick connect {qc_name}: {e}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error creating quick connect {qc_name}: {e}")
            return False
    
    def import_quick_connects(self, export_file: str, dry_run: bool = False) -> Dict:
        """
        Import quick connects from export file
        
        Args:
            export_file: Path to the export file
            dry_run: If True, only validate without creating quick connects
            
        Returns:
            Import results summary
        """
        logger.info(f"Starting quick connect import process (dry_run={dry_run})...")
        
        # Load export data
        export_data = self.load_export_data(export_file)
        qcs_to_import = export_data.get('QuickConnects', [])
        
        if not qcs_to_import:
            logger.warning("No quick connects found in export file")
            return {'success': 0, 'failed': 0, 'skipped': 0}
        
        # Get existing resources for mapping
        existing_qcs = self.get_existing_quick_connects()
        existing_resources = self.get_existing_resources()
        
        # Import statistics
        results = {
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'failed_quick_connects': []
        }
        
        # Process quick connects
        for qc_data in qcs_to_import:
            try:
                # Safely extract quick connect name with error handling
                qc_info = qc_data.get('QuickConnect', {})
                qc_name = qc_info.get('Name')
                
                if not qc_name:
                    logger.error(f"Quick connect missing 'Name' field in data: {qc_data}")
                    results['failed'] += 1
                    results['failed_quick_connects'].append('Unknown - Missing Name')
                    continue
                
                # Check if quick connect already exists
                if qc_name in existing_qcs:
                    logger.warning(f"Quick connect already exists: {qc_name}")
                    results['skipped'] += 1
                    continue
                
                if dry_run:
                    logger.info(f"[DRY RUN] Would create quick connect: {qc_name}")
                    results['success'] += 1
                else:
                    # Actually create the quick connect
                    if self.create_quick_connect(qc_data, existing_resources):
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        results['failed_quick_connects'].append(qc_name)
            
            except Exception as e:
                logger.error(f"Error processing quick connect {qc_name}: {e}")
                results['failed'] += 1
                results['failed_quick_connects'].append(qc_name)
            
            # Rate limiting
            time.sleep(0.2)
        
        # Log final results
        logger.info("Import process completed!")
        logger.info(f"Successful: {results['success']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Skipped: {results['skipped']}")
        
        if results['failed_quick_connects']:
            logger.info(f"Failed quick connects: {', '.join(results['failed_quick_connects'][:10])}")
            if len(results['failed_quick_connects']) > 10:
                logger.info(f"... and {len(results['failed_quick_connects']) - 10} more")
        
        return results

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import Amazon Connect quick connects')
    parser.add_argument('--instance-id', required=True, help='Target Amazon Connect instance ID')
    parser.add_argument('--export-file', required=True, help='Path to the export file')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--profile', help='AWS profile name')
    parser.add_argument('--dry-run', action='store_true', help='Validate without creating quick connects')
    
    args = parser.parse_args()
    
    try:
        importer = ConnectQuickConnectImporter(
            instance_id=args.instance_id,
            region=args.region,
            profile=args.profile
        )
        
        results = importer.import_quick_connects(
            export_file=args.export_file,
            dry_run=args.dry_run
        )
        
        print(f"Import completed - Success: {results['success']}, Failed: {results['failed']}, Skipped: {results['skipped']}")
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()