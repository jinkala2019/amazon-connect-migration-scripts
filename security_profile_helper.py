#!/usr/bin/env python3
"""
Security Profile Helper for Amazon Connect Migration
Analyzes export files and helps create missing security profiles in target instance.
"""

import boto3
import json
import logging
from datetime import datetime
from typing import Dict, List, Set
from botocore.exceptions import ClientError

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_profile_helper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_run_separator(script_name: str, action: str = "START"):
    """
    Log a clear separator for run identification (Windows-compatible)
    
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

class SecurityProfileHelper:
    def __init__(self, region: str = 'us-east-1', profile: str = None):
        """
        Initialize Security Profile Helper
        
        Args:
            region: AWS region
            profile: AWS profile name (optional)
        """
        self.region = region
        
        # Initialize AWS session and client
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.connect_client = session.client('connect', region_name=region)
        
        logger.info(f"Initialized security profile helper in region: {region}")
    
    def analyze_export_file(self, export_file: str) -> Dict:
        """
        Analyze export file to identify required security profiles
        
        Args:
            export_file: Path to user export file
            
        Returns:
            Analysis results
        """
        log_run_separator("SECURITY PROFILE ANALYSIS", "START")
        
        try:
            with open(export_file, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
            
            users = export_data.get('Users', [])
            required_profiles = {}
            profile_usage = {}
            
            for user_data in users:
                username = user_data['User']['Username']
                
                for security_profile in user_data.get('SecurityProfiles', []):
                    # Handle different field names
                    profile_name = security_profile.get('SecurityProfileName') or security_profile.get('Name')
                    
                    if profile_name:
                        if profile_name not in required_profiles:
                            required_profiles[profile_name] = security_profile
                            profile_usage[profile_name] = []
                        
                        profile_usage[profile_name].append(username)
            
            logger.info(f"Analysis of {export_file}:")
            logger.info(f"  Total users: {len(users)}")
            logger.info(f"  Unique security profiles required: {len(required_profiles)}")
            
            for profile_name, users_list in profile_usage.items():
                logger.info(f"  '{profile_name}': used by {len(users_list)} users")
            
            result = {
                'required_profiles': required_profiles,
                'profile_usage': profile_usage,
                'total_users': len(users)
            }
            
            log_run_separator("SECURITY PROFILE ANALYSIS", "END")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing export file: {e}")
            raise
    
    def get_existing_security_profiles(self, instance_id: str) -> Dict[str, str]:
        """
        Get existing security profiles from target instance
        
        Args:
            instance_id: Connect instance ID
            
        Returns:
            Dictionary mapping profile names to IDs
        """
        existing_profiles = {}
        
        try:
            paginator = self.connect_client.get_paginator('list_security_profiles')
            for page in paginator.paginate(InstanceId=instance_id):
                for profile in page.get('SecurityProfileSummaryList', []):
                    # Handle different possible field names for security profile name
                    profile_name = profile.get('SecurityProfileName') or profile.get('Name')
                    if profile_name:
                        existing_profiles[profile_name] = profile['Id']
                    else:
                        logger.warning(f"Security profile missing name field in target instance: {profile}")
            
            logger.info(f"Found {len(existing_profiles)} existing security profiles in target instance")
            return existing_profiles
            
        except ClientError as e:
            logger.error(f"Error fetching security profiles: {e}")
            raise
    
    def compare_profiles(self, export_file: str, target_instance_id: str) -> Dict:
        """
        Compare required profiles with existing profiles in target
        
        Args:
            export_file: Path to user export file
            target_instance_id: Target instance ID
            
        Returns:
            Comparison results
        """
        log_run_separator("SECURITY PROFILE COMPARISON", "START")
        
        analysis = self.analyze_export_file(export_file)
        existing_profiles = self.get_existing_security_profiles(target_instance_id)
        
        required_names = set(analysis['required_profiles'].keys())
        existing_names = set(existing_profiles.keys())
        
        missing_profiles = required_names - existing_names
        available_profiles = required_names & existing_names
        
        comparison = {
            'required_profiles': required_names,
            'existing_profiles': existing_names,
            'missing_profiles': missing_profiles,
            'available_profiles': available_profiles,
            'profile_usage': analysis['profile_usage']
        }
        
        logger.info(f"Profile Comparison Results:")
        logger.info(f"  Required: {len(required_names)}")
        logger.info(f"  Available in target: {len(available_profiles)}")
        logger.info(f"  Missing from target: {len(missing_profiles)}")
        
        if missing_profiles:
            logger.warning(f"Missing security profiles:")
            for profile_name in sorted(missing_profiles):
                users_count = len(analysis['profile_usage'].get(profile_name, []))
                logger.warning(f"  - '{profile_name}' (needed by {users_count} users)")
        
        log_run_separator("SECURITY PROFILE COMPARISON", "END")
        return comparison
    
    def generate_security_profile_commands(self, export_file: str, target_instance_id: str) -> List[str]:
        """
        Generate AWS CLI commands to create missing security profiles
        
        Args:
            export_file: Path to user export file
            target_instance_id: Target instance ID
            
        Returns:
            List of AWS CLI commands
        """
        comparison = self.compare_profiles(export_file, target_instance_id)
        analysis = self.analyze_export_file(export_file)
        
        commands = []
        
        if not comparison['missing_profiles']:
            logger.info("No missing security profiles - all required profiles exist in target!")
            return commands
        
        logger.info("Generating AWS CLI commands for missing security profiles...")
        
        for profile_name in sorted(comparison['missing_profiles']):
            # Create basic security profile with minimal permissions
            command = f"""aws connect create-security-profile \\
  --instance-id {target_instance_id} \\
  --security-profile-name "{profile_name}" \\
  --description "Migrated security profile: {profile_name}" \\
  --permissions "BasicAgentAccess" \\
  --region {self.region}"""
            
            commands.append(command)
        
        return commands
    
    def create_missing_profiles_script(self, export_file: str, target_instance_id: str, output_file: str = None):
        """
        Create a shell script to create missing security profiles
        
        Args:
            export_file: Path to user export file
            target_instance_id: Target instance ID
            output_file: Output script file path
        """
        log_run_separator("SECURITY PROFILE SCRIPT CREATION", "START")
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"create_security_profiles_{timestamp}.sh"
        
        commands = self.generate_security_profile_commands(export_file, target_instance_id)
        
        if not commands:
            logger.info("No script needed - all security profiles exist!")
            log_run_separator("SECURITY PROFILE SCRIPT CREATION", "END")
            return
        
        script_content = f"""#!/bin/bash
# Auto-generated script to create missing security profiles
# Generated on: {datetime.now().isoformat()}
# Source export: {export_file}
# Target instance: {target_instance_id}

echo "Creating missing security profiles..."

"""
        
        for i, command in enumerate(commands, 1):
            script_content += f"""
echo "Creating security profile {i}/{len(commands)}..."
{command}

if [ $? -eq 0 ]; then
    echo "✅ Security profile created successfully"
else
    echo "❌ Failed to create security profile"
fi

"""
        
        script_content += """
echo "Security profile creation completed!"
echo "Note: You may need to configure specific permissions for each profile in the AWS Connect console."
"""
        
        with open(output_file, 'w') as f:
            f.write(script_content)
        
        logger.info(f"Created script: {output_file}")
        logger.info(f"Run: chmod +x {output_file} && ./{output_file}")
        
        log_run_separator("SECURITY PROFILE SCRIPT CREATION", "END")

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Security Profile Helper for Amazon Connect Migration')
    parser.add_argument('--action', required=True, choices=['analyze', 'compare', 'create-script'], 
                       help='Action to perform')
    parser.add_argument('--export-file', required=True, help='Path to user export file')
    parser.add_argument('--target-instance', help='Target instance ID (required for compare/create-script)')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--profile', help='AWS profile name')
    parser.add_argument('--output', help='Output file path for create-script action')
    
    args = parser.parse_args()
    
    try:
        helper = SecurityProfileHelper(region=args.region, profile=args.profile)
        
        if args.action == 'analyze':
            helper.analyze_export_file(args.export_file)
            
        elif args.action == 'compare':
            if not args.target_instance:
                logger.error("--target-instance required for compare action")
                exit(1)
            helper.compare_profiles(args.export_file, args.target_instance)
            
        elif args.action == 'create-script':
            if not args.target_instance:
                logger.error("--target-instance required for create-script action")
                exit(1)
            helper.create_missing_profiles_script(args.export_file, args.target_instance, args.output)
        
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()