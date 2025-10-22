#!/usr/bin/env python3
"""
Amazon Connect Phone Number Mapping Utility
Helps create phone number ID mappings between source and target instances.
"""

import boto3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('connect_phone_mapper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConnectPhoneNumberMapper:
    def __init__(self, region: str = 'us-east-1', profile: Optional[str] = None):
        """
        Initialize the Phone Number Mapper
        
        Args:
            region: AWS region
            profile: AWS profile name (optional)
        """
        self.region = region
        
        # Initialize AWS session and client
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.connect_client = session.client('connect', region_name=region)
        
        logger.info(f"Initialized phone number mapper in region: {region}")
    
    def get_phone_numbers(self, instance_id: str) -> Dict[str, Dict]:
        """
        Get all phone numbers from an instance
        
        Args:
            instance_id: Connect instance ID
            
        Returns:
            Dictionary mapping phone numbers to their details
        """
        phone_numbers = {}
        
        try:
            logger.info(f"Fetching phone numbers from instance: {instance_id}")
            
            paginator = self.connect_client.get_paginator('list_phone_numbers')
            for page in paginator.paginate(InstanceId=instance_id):
                for phone in page.get('PhoneNumberSummaryList', []):
                    phone_numbers[phone['PhoneNumber']] = {
                        'Id': phone['Id'],
                        'Arn': phone['Arn'],
                        'Type': phone.get('PhoneNumberType', 'Unknown'),
                        'CountryCode': phone.get('PhoneNumberCountryCode', 'Unknown')
                    }
            
            logger.info(f"Found {len(phone_numbers)} phone numbers in instance {instance_id}")
            return phone_numbers
            
        except ClientError as e:
            logger.error(f"Error fetching phone numbers from {instance_id}: {e}")
            raise
    
    def create_mapping_template(self, source_instance_id: str, target_instance_id: str, output_file: str = None) -> str:
        """
        Create a phone number mapping template
        
        Args:
            source_instance_id: Source instance ID
            target_instance_id: Target instance ID
            output_file: Output file path (optional)
            
        Returns:
            Path to the mapping template file
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"phone_number_mapping_template_{timestamp}.json"
        
        logger.info("Creating phone number mapping template...")
        
        # Get phone numbers from both instances
        source_phones = self.get_phone_numbers(source_instance_id)
        target_phones = self.get_phone_numbers(target_instance_id)
        
        # Create mapping template
        mapping_template = {
            "description": "Phone number ID mapping from source to target instance",
            "source_instance_id": source_instance_id,
            "target_instance_id": target_instance_id,
            "created_timestamp": datetime.utcnow().isoformat(),
            "instructions": {
                "1": "Review the source_phone_numbers and target_phone_numbers sections",
                "2": "Create mappings in the phone_number_mappings section",
                "3": "Map source phone number IDs to target phone number IDs",
                "4": "Save this file and use it with --phone-mapping parameter"
            },
            "source_phone_numbers": {},
            "target_phone_numbers": {},
            "phone_number_mappings": {
                "example_source_phone_id": "example_target_phone_id",
                "# Add your mappings here": "# source_id: target_id"
            }
        }
        
        # Add source phone numbers with details
        for phone_number, details in source_phones.items():
            mapping_template["source_phone_numbers"][details['Id']] = {
                "phone_number": phone_number,
                "type": details['Type'],
                "country_code": details['CountryCode']
            }
        
        # Add target phone numbers with details
        for phone_number, details in target_phones.items():
            mapping_template["target_phone_numbers"][details['Id']] = {
                "phone_number": phone_number,
                "type": details['Type'],
                "country_code": details['CountryCode']
            }
        
        # Try to create automatic mappings based on phone number matching
        auto_mappings = {}
        for source_phone, source_details in source_phones.items():
            if source_phone in target_phones:
                auto_mappings[source_details['Id']] = target_phones[source_phone]['Id']
                logger.info(f"Auto-mapped phone number: {source_phone}")
        
        if auto_mappings:
            mapping_template["auto_detected_mappings"] = auto_mappings
            mapping_template["phone_number_mappings"].update(auto_mappings)
            logger.info(f"Created {len(auto_mappings)} automatic mappings")
        
        # Write template to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(mapping_template, f, indent=2, default=str)
            
            logger.info(f"Phone number mapping template created: {output_file}")
            logger.info(f"Source instance has {len(source_phones)} phone numbers")
            logger.info(f"Target instance has {len(target_phones)} phone numbers")
            logger.info(f"Auto-detected {len(auto_mappings)} matching phone numbers")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to write mapping template: {e}")
            raise
    
    def validate_mapping_file(self, mapping_file: str) -> bool:
        """
        Validate a phone number mapping file
        
        Args:
            mapping_file: Path to the mapping file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping_data = json.load(f)
            
            logger.info(f"Validating mapping file: {mapping_file}")
            
            # Check required fields
            required_fields = ['source_instance_id', 'target_instance_id', 'phone_number_mappings']
            for field in required_fields:
                if field not in mapping_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            mappings = mapping_data['phone_number_mappings']
            valid_mappings = 0
            
            for source_id, target_id in mappings.items():
                if source_id.startswith('#') or target_id.startswith('#'):
                    continue  # Skip comments
                if source_id.startswith('example_'):
                    continue  # Skip examples
                
                valid_mappings += 1
                logger.info(f"Valid mapping: {source_id} -> {target_id}")
            
            logger.info(f"Validation completed: {valid_mappings} valid mappings found")
            return True
            
        except FileNotFoundError:
            logger.error(f"Mapping file not found: {mapping_file}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in mapping file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating mapping file: {e}")
            return False
    
    def extract_mappings_only(self, mapping_file: str, output_file: str = None) -> str:
        """
        Extract only the phone number mappings from a template file
        
        Args:
            mapping_file: Path to the mapping template file
            output_file: Output file path (optional)
            
        Returns:
            Path to the clean mappings file
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"phone_mappings_clean_{timestamp}.json"
        
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping_data = json.load(f)
            
            # Extract only the actual mappings
            clean_mappings = {}
            raw_mappings = mapping_data.get('phone_number_mappings', {})
            
            for source_id, target_id in raw_mappings.items():
                if source_id.startswith('#') or target_id.startswith('#'):
                    continue  # Skip comments
                if source_id.startswith('example_'):
                    continue  # Skip examples
                
                clean_mappings[source_id] = target_id
            
            # Write clean mappings
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(clean_mappings, f, indent=2)
            
            logger.info(f"Extracted {len(clean_mappings)} clean mappings to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error extracting mappings: {e}")
            raise

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Amazon Connect phone number mapping utility')
    parser.add_argument('--action', required=True, choices=['template', 'validate', 'extract'], 
                       help='Action to perform')
    parser.add_argument('--source-instance', help='Source Amazon Connect instance ID')
    parser.add_argument('--target-instance', help='Target Amazon Connect instance ID')
    parser.add_argument('--mapping-file', help='Path to mapping file')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--profile', help='AWS profile name')
    
    args = parser.parse_args()
    
    try:
        mapper = ConnectPhoneNumberMapper(
            region=args.region,
            profile=args.profile
        )
        
        if args.action == 'template':
            if not args.source_instance or not args.target_instance:
                logger.error("Source and target instance IDs required for template creation")
                exit(1)
            
            output_file = mapper.create_mapping_template(
                source_instance_id=args.source_instance,
                target_instance_id=args.target_instance,
                output_file=args.output
            )
            print(f"Mapping template created: {output_file}")
            
        elif args.action == 'validate':
            if not args.mapping_file:
                logger.error("Mapping file required for validation")
                exit(1)
            
            is_valid = mapper.validate_mapping_file(args.mapping_file)
            print(f"Mapping file validation: {'PASSED' if is_valid else 'FAILED'}")
            
        elif args.action == 'extract':
            if not args.mapping_file:
                logger.error("Mapping file required for extraction")
                exit(1)
            
            output_file = mapper.extract_mappings_only(
                mapping_file=args.mapping_file,
                output_file=args.output
            )
            print(f"Clean mappings extracted: {output_file}")
        
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()