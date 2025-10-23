#!/usr/bin/env python3
"""
Amazon Connect Quick Connect Export Script
Exports all quick connects with complete configurations from an Amazon Connect instance.
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
        logging.FileHandler('connect_quick_connect_export.log', encoding='utf-8'),
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

class ConnectQuickConnectExporter:
    def __init__(self, instance_id: str, region: str = 'us-east-1', profile: Optional[str] = None):
        """
        Initialize the Connect Quick Connect Exporter
        
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
        
        logger.info(f"Initialized quick connect exporter for instance: {instance_id} in region: {region}")
    
    def get_all_quick_connects(self) -> List[Dict]:
        """
        Retrieve all quick connects from the Connect instance with pagination support
        
        Returns:
            List of quick connect summaries
        """
        quick_connects = []
        next_token = None
        page_count = 0
        
        try:
            while True:
                page_count += 1
                logger.info(f"Fetching quick connects page {page_count}...")
                
                params = {
                    'InstanceId': self.instance_id,
                    'MaxResults': 1000  # Maximum allowed by API
                }
                
                if next_token:
                    params['NextToken'] = next_token
                
                response = self.connect_client.list_quick_connects(**params)
                
                page_quick_connects = response.get('QuickConnectSummaryList', [])
                quick_connects.extend(page_quick_connects)
                
                logger.info(f"Retrieved {len(page_quick_connects)} quick connects from page {page_count}")
                
                next_token = response.get('NextToken')
                if not next_token:
                    break
                
                # Rate limiting to avoid throttling
                time.sleep(0.1)
            
            logger.info(f"Total quick connects retrieved: {len(quick_connects)}")
            return quick_connects
            
        except ClientError as e:
            logger.error(f"AWS API error while fetching quick connects: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching quick connects: {e}")
            raise
    
    def get_quick_connect_details(self, quick_connect_id: str) -> Dict:
        """
        Get detailed quick connect information including all configurations
        
        Args:
            quick_connect_id: Quick Connect ID to fetch details for
            
        Returns:
            Complete quick connect data
        """
        try:
            # Get basic quick connect info
            response = self.connect_client.describe_quick_connect(
                InstanceId=self.instance_id,
                QuickConnectId=quick_connect_id
            )
            
            quick_connect_data = response['QuickConnect']
            
            # Get tags for the quick connect (avoid duplication if already in quick_connect_data)
            tags = {}
            if 'Tags' not in quick_connect_data:
                try:
                    tags_response = self.connect_client.list_tags_for_resource(
                        resourceArn=quick_connect_data['QuickConnectARN']
                    )
                    tags = tags_response.get('tags', {})
                except ClientError as e:
                    logger.warning(f"Could not fetch tags for quick connect {quick_connect_id}: {e}")
            else:
                logger.debug(f"Quick connect {quick_connect_id} already has tags in API response")
                tags = quick_connect_data.get('Tags', {})
            
            # Compile complete quick connect profile
            complete_profile = {
                'QuickConnect': quick_connect_data,
                'Tags': tags,
                'ExportTimestamp': datetime.utcnow().isoformat()
            }
            
            return complete_profile
            
        except ClientError as e:
            logger.error(f"AWS API error while fetching quick connect details for {quick_connect_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching quick connect details for {quick_connect_id}: {e}")
            raise
    
    def export_quick_connects(self, output_file: str = None) -> str:
        """
        Export all quick connects with complete configurations
        
        Args:
            output_file: Output file path (optional)
            
        Returns:
            Path to the exported file
        """
        # Log run start
        log_run_separator("QUICK CONNECT EXPORT", "START")
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"connect_quick_connects_export_{self.instance_id}_{timestamp}.json"
        
        logger.info("Starting quick connect export process...")
        
        # Get all quick connects
        quick_connects = self.get_all_quick_connects()
        
        if not quick_connects:
            logger.warning("No quick connects found to export")
            log_run_separator("QUICK CONNECT EXPORT", "END")
            return output_file
        
        exported_quick_connects = []
        failed_exports = []
        
        for i, qc_summary in enumerate(quick_connects, 1):
            qc_id = qc_summary['Id']
            qc_name = qc_summary.get('Name', 'Unknown')
            
            try:
                logger.info(f"Exporting quick connect {i}/{len(quick_connects)}: {qc_name} ({qc_id})")
                
                qc_details = self.get_quick_connect_details(qc_id)
                exported_quick_connects.append(qc_details)
                
                # Rate limiting
                if i % 10 == 0:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Failed to export quick connect {qc_name} ({qc_id}): {e}")
                failed_exports.append({
                    'QuickConnectId': qc_id,
                    'Name': qc_name,
                    'Error': str(e)
                })
        
        # Prepare export data
        export_data = {
            'InstanceId': self.instance_id,
            'ExportTimestamp': datetime.utcnow().isoformat(),
            'TotalQuickConnects': len(quick_connects),
            'SuccessfulExports': len(exported_quick_connects),
            'FailedExports': len(failed_exports),
            'QuickConnects': exported_quick_connects,
            'FailedQuickConnects': failed_exports
        }
        
        # Write to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Export completed successfully!")
            logger.info(f"Exported {len(exported_quick_connects)} quick connects to {output_file}")
            logger.info(f"Failed exports: {len(failed_exports)}")
            
            # Log run end
            log_run_separator("QUICK CONNECT EXPORT", "END")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to write export file: {e}")
            raise

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Export Amazon Connect quick connects')
    parser.add_argument('--instance-id', required=True, help='Amazon Connect instance ID')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--profile', help='AWS profile name')
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    try:
        exporter = ConnectQuickConnectExporter(
            instance_id=args.instance_id,
            region=args.region,
            profile=args.profile
        )
        
        output_file = exporter.export_quick_connects(args.output)
        print(f"Export completed: {output_file}")
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()