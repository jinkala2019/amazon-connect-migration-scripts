#!/usr/bin/env python3
"""
Amazon Connect Queue Import Script
Imports queues and associated quick connect configurations into an Amazon Connect instance.
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
        logging.FileHandler('connect_queue_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConnectQueueImporter:
    def __init__(self, instance_id: str, region: str = 'us-east-1', profile: Optional[str] = None, phone_number_mapping: Optional[Dict[str, str]] = None):
        """
        Initialize the Connect Queue Importer
        
        Args:
            instance_id: Target Amazon Connect instance ID
            region: AWS region
            profile: AWS profile name (optional)
            phone_number_mapping: Dictionary mapping source phone number IDs to target phone number IDs
        """
        self.instance_id = instance_id
        self.region = region
        self.phone_number_mapping = phone_number_mapping or {}
        
        # Initialize AWS session and client
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.connect_client = session.client('connect', region_name=region)
        
        logger.info(f"Initialized queue importer for instance: {instance_id} in region: {region}")
        if self.phone_number_mapping:
            logger.info(f"Phone number mapping provided: {len(self.phone_number_mapping)} mappings")
    
    def load_export_data(self, export_file: str) -> Dict:
        """
        Load exported queue data from JSON file
        
        Args:
            export_file: Path to the export file
            
        Returns:
            Parsed export data
        """
        try:
            with open(export_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loaded export data from {export_file}")
            logger.info(f"Source instance: {data.get('InstanceId')}")
            logger.info(f"BU tag value: {data.get('BUTagValue')}")
            logger.info(f"Total queues in export: {data.get('SuccessfulExports', 0)}")
            
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
            'queues': {},
            'quick_connects': {},
            'hours_of_operations': {},
            'phone_numbers': {}
        }
        
        try:
            # Get existing queues
            logger.info("Fetching existing queues...")
            queue_paginator = self.connect_client.get_paginator('list_queues')
            for page in queue_paginator.paginate(InstanceId=self.instance_id):
                for queue in page.get('QueueSummaryList', []):
                    resources['queues'][queue['Name']] = queue['Id']
            
            # Get existing quick connects
            logger.info("Fetching existing quick connects...")
            qc_paginator = self.connect_client.get_paginator('list_quick_connects')
            for page in qc_paginator.paginate(InstanceId=self.instance_id):
                for qc in page.get('QuickConnectSummaryList', []):
                    resources['quick_connects'][qc['Name']] = qc['Id']
            
            # Get hours of operations
            logger.info("Fetching existing hours of operations...")
            hours_paginator = self.connect_client.get_paginator('list_hours_of_operations')
            for page in hours_paginator.paginate(InstanceId=self.instance_id):
                for hours in page.get('HoursOfOperationSummaryList', []):
                    resources['hours_of_operations'][hours['Name']] = hours['Id']
            
            # Get phone numbers
            logger.info("Fetching existing phone numbers...")
            try:
                phone_paginator = self.connect_client.get_paginator('list_phone_numbers')
                for page in phone_paginator.paginate(InstanceId=self.instance_id):
                    for phone in page.get('PhoneNumberSummaryList', []):
                        # Map by phone number value for easier lookup
                        resources['phone_numbers'][phone['PhoneNumber']] = phone['Id']
            except ClientError as e:
                logger.warning(f"Could not fetch phone numbers: {e}")
            
            logger.info(f"Found {len(resources['queues'])} queues")
            logger.info(f"Found {len(resources['quick_connects'])} quick connects")
            logger.info(f"Found {len(resources['hours_of_operations'])} hours of operations")
            logger.info(f"Found {len(resources['phone_numbers'])} phone numbers")
            
            return resources
            
        except ClientError as e:
            logger.error(f"Error fetching existing resources: {e}")
            raise
    
    def create_missing_quick_connect(self, qc_data: Dict) -> Optional[str]:
        """
        Create a quick connect if it doesn't exist
        
        Args:
            qc_data: Quick connect data from export
            
        Returns:
            Quick connect ID if created/found, None if failed
        """
        qc_info = qc_data.get('QuickConnect', {})
        qc_name = qc_info.get('Name')
        
        if not qc_name:
            logger.error(f"Quick connect missing 'Name' field: {qc_data}")
            return None
        
        try:
            # Prepare quick connect creation parameters
            create_params = {
                'InstanceId': self.instance_id,
                'Name': qc_name,
                'Description': qc_info.get('Description', ''),
                'QuickConnectConfig': qc_info['QuickConnectConfig']
            }
            
            # Add tags if they exist
            if qc_data.get('Tags'):
                create_params['Tags'] = qc_data['Tags']
            
            response = self.connect_client.create_quick_connect(**create_params)
            
            new_qc_id = response['QuickConnectId']
            logger.info(f"Created quick connect: {qc_name} -> {new_qc_id}")
            
            return new_qc_id
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'DuplicateResourceException':
                logger.warning(f"Quick connect already exists: {qc_name}")
                # Try to find the existing quick connect
                return self.find_quick_connect_by_name(qc_name)
            else:
                logger.error(f"Error creating quick connect {qc_name}: {e}")
                return None
        except Exception as e:
            logger.error(f"Unexpected error creating quick connect {qc_name}: {e}")
            return None
    
    def find_quick_connect_by_name(self, name: str) -> Optional[str]:
        """Find quick connect ID by name"""
        try:
            paginator = self.connect_client.get_paginator('list_quick_connects')
            for page in paginator.paginate(InstanceId=self.instance_id):
                for qc in page.get('QuickConnectSummaryList', []):
                    if qc['Name'] == name:
                        return qc['Id']
            return None
        except Exception as e:
            logger.error(f"Error finding quick connect by name {name}: {e}")
            return None
    
    def map_hours_of_operation(self, hours_of_operation_id: str, existing_resources: Dict) -> Optional[str]:
        """
        Map hours of operation ID to target instance
        
        Args:
            hours_of_operation_id: Source hours of operation ID
            existing_resources: Existing resources in target instance
            
        Returns:
            Mapped hours of operation ID or None
        """
        # For now, we'll use a basic mapping strategy
        # In a real implementation, you'd want to map by name or create missing ones
        
        # Try to find a default hours of operation
        if existing_resources['hours_of_operations']:
            # Use the first available hours of operation as default
            default_name = list(existing_resources['hours_of_operations'].keys())[0]
            default_id = existing_resources['hours_of_operations'][default_name]
            logger.warning(f"Using default hours of operation: {default_name} ({default_id})")
            return default_id
        
        logger.error("No hours of operations found in target instance")
        return None
    
    def map_outbound_caller_config(self, outbound_config: Dict, existing_resources: Dict) -> Optional[Dict]:
        """
        Map outbound caller configuration to target instance phone numbers
        
        Args:
            outbound_config: Source outbound caller configuration
            existing_resources: Existing resources in target instance
            
        Returns:
            Mapped outbound caller configuration or None
        """
        if not outbound_config:
            return None
        
        mapped_config = outbound_config.copy()
        
        # Map outbound caller ID number
        source_phone_id = outbound_config.get('OutboundCallerIdNumberId')
        if source_phone_id:
            # Check if we have a specific mapping for this phone number ID
            if source_phone_id in self.phone_number_mapping:
                mapped_phone_id = self.phone_number_mapping[source_phone_id]
                mapped_config['OutboundCallerIdNumberId'] = mapped_phone_id
                logger.info(f"Mapped phone number ID: {source_phone_id} -> {mapped_phone_id}")
            else:
                # Try to find a default phone number in target instance
                if existing_resources['phone_numbers']:
                    # Use the first available phone number as default
                    default_phone_number = list(existing_resources['phone_numbers'].keys())[0]
                    default_phone_id = existing_resources['phone_numbers'][default_phone_number]
                    mapped_config['OutboundCallerIdNumberId'] = default_phone_id
                    logger.warning(f"Using default phone number for outbound caller ID: {default_phone_number} ({default_phone_id})")
                else:
                    logger.error(f"No phone number mapping found for {source_phone_id} and no default phone numbers available")
                    # Remove the phone number configuration to avoid creation failure
                    mapped_config.pop('OutboundCallerIdNumberId', None)
        
        return mapped_config
    
    def create_queue(self, queue_data: Dict, existing_resources: Dict) -> bool:
        """
        Create a single queue in the target instance
        
        Args:
            queue_data: Complete queue data from export
            existing_resources: Existing resources for mapping
            
        Returns:
            True if successful, False otherwise
        """
        queue_info = queue_data['Queue']
        queue_name = queue_info['Name']
        
        try:
            # Map hours of operation
            hours_of_operation_id = self.map_hours_of_operation(
                queue_info.get('HoursOfOperationId'), 
                existing_resources
            )
            
            if not hours_of_operation_id:
                logger.error(f"Cannot create queue {queue_name}: No valid hours of operation")
                return False
            
            # Prepare queue creation parameters
            create_params = {
                'InstanceId': self.instance_id,
                'Name': queue_name,
                'Description': queue_info.get('Description', ''),
                'HoursOfOperationId': hours_of_operation_id
            }
            
            # Add optional parameters
            if queue_info.get('MaxContacts'):
                create_params['MaxContacts'] = queue_info['MaxContacts']
            
            # Map outbound caller configuration with phone number mapping
            if queue_info.get('OutboundCallerConfig'):
                mapped_outbound_config = self.map_outbound_caller_config(
                    queue_info['OutboundCallerConfig'], 
                    existing_resources
                )
                if mapped_outbound_config:
                    create_params['OutboundCallerConfig'] = mapped_outbound_config
            
            # Add tags if they exist
            if queue_data.get('Tags'):
                create_params['Tags'] = queue_data['Tags']
            
            # Create the queue
            response = self.connect_client.create_queue(**create_params)
            
            new_queue_id = response['QueueId']
            logger.info(f"Created queue: {queue_name} -> {new_queue_id}")
            
            # Associate quick connects with the queue
            self.associate_quick_connects_to_queue(new_queue_id, queue_data, existing_resources)
            
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'DuplicateResourceException':
                logger.warning(f"Queue already exists: {queue_name}")
                return True  # Consider existing queue as success
            else:
                logger.error(f"Error creating queue {queue_name}: {e}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error creating queue {queue_name}: {e}")
            return False
    
    def associate_quick_connects_to_queue(self, queue_id: str, queue_data: Dict, existing_resources: Dict):
        """
        Associate quick connects to a queue
        
        Args:
            queue_id: Target queue ID
            queue_data: Queue data containing quick connects
            existing_resources: Existing resources for mapping
        """
        quick_connects = queue_data.get('QuickConnects', [])
        
        if not quick_connects:
            logger.info(f"No quick connects to associate with queue {queue_id}")
            return
        
        quick_connect_ids = []
        
        for qc_data in quick_connects:
            # Safely extract quick connect name
            qc_info = qc_data.get('QuickConnect', {})
            qc_name = qc_info.get('Name')
            
            if not qc_name:
                logger.warning(f"Quick connect missing 'Name' field, skipping: {qc_data}")
                continue
            
            # Check if quick connect exists in target
            qc_id = existing_resources['quick_connects'].get(qc_name)
            
            if not qc_id:
                # Try to create the quick connect
                logger.info(f"Creating missing quick connect: {qc_name}")
                qc_id = self.create_missing_quick_connect(qc_data)
                
                if qc_id:
                    # Update existing resources cache
                    existing_resources['quick_connects'][qc_name] = qc_id
            
            if qc_id:
                quick_connect_ids.append(qc_id)
                logger.info(f"Will associate quick connect {qc_name} ({qc_id}) to queue")
            else:
                logger.warning(f"Could not create/find quick connect: {qc_name}")
        
        # Associate quick connects to queue
        if quick_connect_ids:
            try:
                self.connect_client.associate_queue_quick_connects(
                    InstanceId=self.instance_id,
                    QueueId=queue_id,
                    QuickConnectIds=quick_connect_ids
                )
                logger.info(f"Associated {len(quick_connect_ids)} quick connects to queue {queue_id}")
            except ClientError as e:
                logger.error(f"Error associating quick connects to queue {queue_id}: {e}")
        else:
            logger.warning(f"No quick connects could be associated to queue {queue_id}")
    
    def import_queues(self, export_file: str, dry_run: bool = False, phone_number_mapping_file: str = None) -> Dict:
        """
        Import queues from export file
        
        Args:
            export_file: Path to the export file
            dry_run: If True, only validate without creating queues
            phone_number_mapping_file: Path to JSON file containing phone number ID mappings
            
        Returns:
            Import results summary
        """
        logger.info(f"Starting queue import process (dry_run={dry_run})...")
        
        # Load phone number mapping if provided
        if phone_number_mapping_file:
            try:
                with open(phone_number_mapping_file, 'r', encoding='utf-8') as f:
                    mapping_data = json.load(f)
                
                # Handle both simple format and template format
                if 'phone_number_mappings' in mapping_data:
                    # Template format with phone_number_mappings section
                    phone_mappings = mapping_data['phone_number_mappings']
                else:
                    # Simple format - direct mappings
                    phone_mappings = mapping_data
                
                # Filter out instruction/example entries
                clean_mappings = {}
                for source_id, target_id in phone_mappings.items():
                    if not source_id.startswith('#') and not source_id.startswith('source-phone-id'):
                        clean_mappings[source_id] = target_id
                
                self.phone_number_mapping.update(clean_mappings)
                logger.info(f"Loaded {len(clean_mappings)} phone number mappings from {phone_number_mapping_file}")
                
            except Exception as e:
                logger.error(f"Error loading phone number mapping file: {e}")
                raise
        
        # Load export data
        export_data = self.load_export_data(export_file)
        queues_to_import = export_data.get('Queues', [])
        
        if not queues_to_import:
            logger.warning("No queues found in export file")
            return {'success': 0, 'failed': 0, 'skipped': 0}
        
        # Get existing resources for mapping
        existing_resources = self.get_existing_resources()
        
        # Import statistics
        results = {
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'failed_queues': []
        }
        
        # Process queues
        for queue_data in queues_to_import:
            queue_name = queue_data['Queue']['Name']
            
            try:
                # Check if queue already exists
                if queue_name in existing_resources['queues']:
                    logger.warning(f"Queue already exists: {queue_name}")
                    results['skipped'] += 1
                    continue
                
                if dry_run:
                    logger.info(f"[DRY RUN] Would create queue: {queue_name}")
                    results['success'] += 1
                else:
                    # Actually create the queue
                    if self.create_queue(queue_data, existing_resources):
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        results['failed_queues'].append(queue_name)
            
            except Exception as e:
                logger.error(f"Error processing queue {queue_name}: {e}")
                results['failed'] += 1
                results['failed_queues'].append(queue_name)
            
            # Rate limiting
            time.sleep(0.5)
        
        # Log final results
        logger.info("Import process completed!")
        logger.info(f"Successful: {results['success']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Skipped: {results['skipped']}")
        
        if results['failed_queues']:
            logger.info(f"Failed queues: {', '.join(results['failed_queues'][:10])}")
            if len(results['failed_queues']) > 10:
                logger.info(f"... and {len(results['failed_queues']) - 10} more")
        
        return results

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import Amazon Connect queues')
    parser.add_argument('--instance-id', required=True, help='Target Amazon Connect instance ID')
    parser.add_argument('--export-file', required=True, help='Path to the export file')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--profile', help='AWS profile name')
    parser.add_argument('--dry-run', action='store_true', help='Validate without creating queues')
    parser.add_argument('--phone-mapping', help='Path to JSON file with phone number ID mappings')
    
    args = parser.parse_args()
    
    try:
        importer = ConnectQueueImporter(
            instance_id=args.instance_id,
            region=args.region,
            profile=args.profile
        )
        
        results = importer.import_queues(
            export_file=args.export_file,
            dry_run=args.dry_run,
            phone_number_mapping_file=args.phone_mapping
        )
        
        print(f"Import completed - Success: {results['success']}, Failed: {results['failed']}, Skipped: {results['skipped']}")
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()