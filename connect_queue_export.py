#!/usr/bin/env python3
"""
Amazon Connect Queue Export Script with BU Tag Filtering
Exports queues and associated quick connect configurations based on BU tag filtering.
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
        logging.FileHandler('connect_queue_export.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConnectQueueExporter:
    def __init__(self, instance_id: str, bu_tag_value: str, region: str = 'us-east-1', profile: Optional[str] = None):
        """
        Initialize the Connect Queue Exporter with BU tag filtering
        
        Args:
            instance_id: Amazon Connect instance ID
            bu_tag_value: BU tag value to filter queues
            region: AWS region
            profile: AWS profile name (optional)
        """
        self.instance_id = instance_id
        self.bu_tag_value = bu_tag_value
        self.region = region
        
        # Initialize AWS session and client
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.connect_client = session.client('connect', region_name=region)
        
        logger.info(f"Initialized queue exporter for instance: {instance_id}, BU: {bu_tag_value} in region: {region}")
    
    def get_all_queues(self) -> List[Dict]:
        """
        Retrieve all queues from the Connect instance with pagination support
        
        Returns:
            List of queue summaries
        """
        queues = []
        next_token = None
        page_count = 0
        
        try:
            while True:
                page_count += 1
                logger.info(f"Fetching queues page {page_count}...")
                
                params = {
                    'InstanceId': self.instance_id,
                    'MaxResults': 1000  # Maximum allowed by API
                }
                
                if next_token:
                    params['NextToken'] = next_token
                
                response = self.connect_client.list_queues(**params)
                
                page_queues = response.get('QueueSummaryList', [])
                queues.extend(page_queues)
                
                logger.info(f"Retrieved {len(page_queues)} queues from page {page_count}")
                
                next_token = response.get('NextToken')
                if not next_token:
                    break
                
                # Rate limiting to avoid throttling
                time.sleep(0.1)
            
            logger.info(f"Total queues retrieved: {len(queues)}")
            return queues
            
        except ClientError as e:
            logger.error(f"AWS API error while fetching queues: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching queues: {e}")
            raise
    
    def get_queue_tags(self, queue_arn: str) -> Dict[str, str]:
        """
        Get tags for a specific queue
        
        Args:
            queue_arn: Queue ARN
            
        Returns:
            Dictionary of tags
        """
        try:
            response = self.connect_client.list_tags_for_resource(resourceArn=queue_arn)
            return response.get('tags', {})
        except ClientError as e:
            logger.warning(f"Could not fetch tags for queue {queue_arn}: {e}")
            return {}
        except Exception as e:
            logger.warning(f"Unexpected error fetching tags for queue {queue_arn}: {e}")
            return {}
    
    def queue_matches_bu_tag(self, queue_tags: Dict[str, str]) -> bool:
        """
        Check if queue has the specified BU tag value
        
        Args:
            queue_tags: Dictionary of queue tags
            
        Returns:
            True if queue matches BU tag, False otherwise
        """
        # Check for BU tag (case-insensitive)
        for tag_key, tag_value in queue_tags.items():
            if tag_key.lower() == 'bu' and tag_value.lower() == self.bu_tag_value.lower():
                return True
        return False
    
    def get_queue_details(self, queue_id: str) -> Dict:
        """
        Get detailed queue information including all configurations
        
        Args:
            queue_id: Queue ID to fetch details for
            
        Returns:
            Complete queue data
        """
        try:
            # Get basic queue info
            response = self.connect_client.describe_queue(
                InstanceId=self.instance_id,
                QueueId=queue_id
            )
            
            queue_data = response['Queue']
            
            # Get tags for the queue
            tags = self.get_queue_tags(queue_data['QueueArn'])
            
            # Get quick connects associated with this queue
            quick_connects = []
            try:
                qc_response = self.connect_client.list_queue_quick_connects(
                    InstanceId=self.instance_id,
                    QueueId=queue_id
                )
                
                # Get detailed info for each quick connect
                for qc_summary in qc_response.get('QuickConnectSummaryList', []):
                    try:
                        qc_detail_response = self.connect_client.describe_quick_connect(
                            InstanceId=self.instance_id,
                            QuickConnectId=qc_summary['Id']
                        )
                        
                        # Get quick connect tags
                        qc_tags = {}
                        try:
                            qc_tags_response = self.connect_client.list_tags_for_resource(
                                resourceArn=qc_detail_response['QuickConnect']['QuickConnectARN']
                            )
                            qc_tags = qc_tags_response.get('tags', {})
                        except ClientError:
                            pass
                        
                        quick_connects.append({
                            'QuickConnect': qc_detail_response['QuickConnect'],
                            'Tags': qc_tags
                        })
                        
                    except ClientError as e:
                        logger.warning(f"Could not fetch quick connect details for {qc_summary['Id']}: {e}")
                        
            except ClientError as e:
                logger.warning(f"Could not fetch quick connects for queue {queue_id}: {e}")
            
            # Get outbound caller config
            outbound_caller_config = {}
            try:
                caller_response = self.connect_client.describe_queue(
                    InstanceId=self.instance_id,
                    QueueId=queue_id
                )
                outbound_caller_config = caller_response['Queue'].get('OutboundCallerConfig', {})
            except ClientError as e:
                logger.warning(f"Could not fetch outbound caller config for queue {queue_id}: {e}")
            
            # Compile complete queue profile
            complete_profile = {
                'Queue': queue_data,
                'Tags': tags,
                'QuickConnects': quick_connects,
                'OutboundCallerConfig': outbound_caller_config,
                'ExportTimestamp': datetime.utcnow().isoformat()
            }
            
            return complete_profile
            
        except ClientError as e:
            logger.error(f"AWS API error while fetching queue details for {queue_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching queue details for {queue_id}: {e}")
            raise
    
    def export_queues_by_bu_tag(self, output_file: str = None) -> str:
        """
        Export queues matching the BU tag with complete configurations
        
        Args:
            output_file: Output file path (optional)
            
        Returns:
            Path to the exported file
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"connect_queues_export_{self.instance_id}_{self.bu_tag_value}_{timestamp}.json"
        
        logger.info(f"Starting queue export process for BU tag: {self.bu_tag_value}...")
        
        # Get all queues
        all_queues = self.get_all_queues()
        
        if not all_queues:
            logger.warning("No queues found to export")
            return output_file
        
        # Filter queues by BU tag
        matching_queues = []
        for queue_summary in all_queues:
            queue_id = queue_summary['Id']
            queue_name = queue_summary.get('Name', 'Unknown')
            
            try:
                # Get queue tags to check BU tag
                queue_arn = queue_summary.get('Arn')
                if not queue_arn:
                    # If ARN not in summary, get it from detailed info
                    queue_detail = self.connect_client.describe_queue(
                        InstanceId=self.instance_id,
                        QueueId=queue_id
                    )
                    queue_arn = queue_detail['Queue']['QueueArn']
                
                queue_tags = self.get_queue_tags(queue_arn)
                
                if self.queue_matches_bu_tag(queue_tags):
                    matching_queues.append(queue_summary)
                    logger.info(f"Queue matches BU tag '{self.bu_tag_value}': {queue_name}")
                else:
                    logger.debug(f"Queue does not match BU tag: {queue_name} (tags: {queue_tags})")
                    
            except Exception as e:
                logger.warning(f"Error checking BU tag for queue {queue_name}: {e}")
        
        logger.info(f"Found {len(matching_queues)} queues matching BU tag '{self.bu_tag_value}'")
        
        if not matching_queues:
            logger.warning(f"No queues found with BU tag '{self.bu_tag_value}'")
            # Still create export file with empty results
            export_data = {
                'InstanceId': self.instance_id,
                'BUTagValue': self.bu_tag_value,
                'ExportTimestamp': datetime.utcnow().isoformat(),
                'TotalQueuesScanned': len(all_queues),
                'MatchingQueues': 0,
                'SuccessfulExports': 0,
                'FailedExports': 0,
                'Queues': [],
                'FailedQueues': []
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            return output_file
        
        # Export matching queues with full details
        exported_queues = []
        failed_exports = []
        
        for i, queue_summary in enumerate(matching_queues, 1):
            queue_id = queue_summary['Id']
            queue_name = queue_summary.get('Name', 'Unknown')
            
            try:
                logger.info(f"Exporting queue {i}/{len(matching_queues)}: {queue_name} ({queue_id})")
                
                queue_details = self.get_queue_details(queue_id)
                exported_queues.append(queue_details)
                
                # Rate limiting
                if i % 5 == 0:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Failed to export queue {queue_name} ({queue_id}): {e}")
                failed_exports.append({
                    'QueueId': queue_id,
                    'Name': queue_name,
                    'Error': str(e)
                })
        
        # Prepare export data
        export_data = {
            'InstanceId': self.instance_id,
            'BUTagValue': self.bu_tag_value,
            'ExportTimestamp': datetime.utcnow().isoformat(),
            'TotalQueuesScanned': len(all_queues),
            'MatchingQueues': len(matching_queues),
            'SuccessfulExports': len(exported_queues),
            'FailedExports': len(failed_exports),
            'Queues': exported_queues,
            'FailedQueues': failed_exports
        }
        
        # Write to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Export completed successfully!")
            logger.info(f"Scanned {len(all_queues)} total queues")
            logger.info(f"Found {len(matching_queues)} queues matching BU tag '{self.bu_tag_value}'")
            logger.info(f"Exported {len(exported_queues)} queues to {output_file}")
            logger.info(f"Failed exports: {len(failed_exports)}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to write export file: {e}")
            raise

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Export Amazon Connect queues by BU tag')
    parser.add_argument('--instance-id', required=True, help='Amazon Connect instance ID')
    parser.add_argument('--bu-tag', required=True, help='BU tag value to filter queues')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--profile', help='AWS profile name')
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    try:
        exporter = ConnectQueueExporter(
            instance_id=args.instance_id,
            bu_tag_value=args.bu_tag,
            region=args.region,
            profile=args.profile
        )
        
        output_file = exporter.export_queues_by_bu_tag(args.output)
        print(f"Export completed: {output_file}")
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()