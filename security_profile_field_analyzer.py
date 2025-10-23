#!/usr/bin/env python3
"""
Security Profile Field Format Analyzer
Analyzes the field names used in security profile API responses across different AWS regions
"""

import boto3
import json
import logging
from typing import Dict, List
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityProfileFieldAnalyzer:
    def __init__(self, instance_id: str, profile: str = None):
        """
        Initialize the analyzer
        
        Args:
            instance_id: Amazon Connect instance ID
            profile: AWS profile name (optional)
        """
        self.instance_id = instance_id
        self.profile = profile
    
    def analyze_region(self, region: str) -> Dict:
        """
        Analyze security profile field formats in a specific region
        
        Args:
            region: AWS region to analyze
            
        Returns:
            Analysis results for the region
        """
        logger.info(f"Analyzing security profile fields in region: {region}")
        
        try:
            # Initialize AWS session and client for this region
            session = boto3.Session(profile_name=self.profile) if self.profile else boto3.Session()
            connect_client = session.client('connect', region_name=region)
            
            # Get security profiles using list_security_profiles
            logger.info(f"Fetching security profiles via list_security_profiles in {region}...")
            
            security_profiles = []
            paginator = connect_client.get_paginator('list_security_profiles')
            
            for page in paginator.paginate(InstanceId=self.instance_id):
                profiles_page = page.get('SecurityProfileSummaryList', [])
                security_profiles.extend(profiles_page)
                logger.info(f"Retrieved {len(profiles_page)} security profiles from page")
            
            logger.info(f"Total security profiles found in {region}: {len(security_profiles)}")
            
            # Analyze field structures
            analysis = {
                'region': region,
                'total_profiles': len(security_profiles),
                'field_analysis': {},
                'sample_profiles': [],
                'field_patterns': {
                    'has_SecurityProfileName': 0,
                    'has_Name': 0,
                    'has_both': 0,
                    'has_neither': 0
                }
            }
            
            # Analyze each profile
            for i, profile in enumerate(security_profiles):
                # Store first 3 profiles as samples
                if i < 3:
                    analysis['sample_profiles'].append(profile)
                
                # Check field patterns
                has_security_profile_name = 'SecurityProfileName' in profile
                has_name = 'Name' in profile
                
                if has_security_profile_name and has_name:
                    analysis['field_patterns']['has_both'] += 1
                elif has_security_profile_name:
                    analysis['field_patterns']['has_SecurityProfileName'] += 1
                elif has_name:
                    analysis['field_patterns']['has_Name'] += 1
                else:
                    analysis['field_patterns']['has_neither'] += 1
                
                # Collect all field names
                for field_name in profile.keys():
                    if field_name not in analysis['field_analysis']:
                        analysis['field_analysis'][field_name] = 0
                    analysis['field_analysis'][field_name] += 1
            
            return analysis
            
        except ClientError as e:
            logger.error(f"AWS API error in region {region}: {e}")
            return {
                'region': region,
                'error': str(e),
                'error_code': e.response.get('Error', {}).get('Code', 'Unknown')
            }
        except Exception as e:
            logger.error(f"Unexpected error in region {region}: {e}")
            return {
                'region': region,
                'error': str(e)
            }
    
    def compare_regions(self, regions: List[str]) -> Dict:
        """
        Compare security profile field formats across multiple regions
        
        Args:
            regions: List of AWS regions to compare
            
        Returns:
            Comparison results
        """
        logger.info(f"Comparing security profile fields across regions: {regions}")
        
        results = {
            'instance_id': self.instance_id,
            'regions_analyzed': regions,
            'region_results': {},
            'comparison': {
                'field_consistency': {},
                'recommendations': []
            }
        }
        
        # Analyze each region
        for region in regions:
            results['region_results'][region] = self.analyze_region(region)
        
        # Compare results
        self.generate_comparison_analysis(results)
        
        return results
    
    def generate_comparison_analysis(self, results: Dict):
        """
        Generate comparison analysis between regions
        
        Args:
            results: Results dictionary to populate with analysis
        """
        region_results = results['region_results']
        comparison = results['comparison']
        
        # Check for errors
        error_regions = [region for region, data in region_results.items() if 'error' in data]
        success_regions = [region for region, data in region_results.items() if 'error' not in data]
        
        if error_regions:
            comparison['recommendations'].append(f"⚠️  Errors in regions: {error_regions}")
        
        if len(success_regions) < 2:
            comparison['recommendations'].append("❌ Need at least 2 successful regions for comparison")
            return
        
        # Compare field patterns
        logger.info("Generating field pattern comparison...")
        
        for region in success_regions:
            data = region_results[region]
            patterns = data['field_patterns']
            
            comparison['field_consistency'][region] = {
                'SecurityProfileName_usage': f"{patterns['has_SecurityProfileName']} profiles",
                'Name_usage': f"{patterns['has_Name']} profiles", 
                'Both_fields': f"{patterns['has_both']} profiles",
                'Neither_field': f"{patterns['has_neither']} profiles",
                'total_profiles': data['total_profiles']
            }
        
        # Generate recommendations
        self.generate_recommendations(results)
    
    def generate_recommendations(self, results: Dict):
        """
        Generate recommendations based on analysis
        
        Args:
            results: Results dictionary with analysis data
        """
        recommendations = results['comparison']['recommendations']
        region_results = results['region_results']
        
        # Check consistency across regions
        security_profile_name_counts = []
        name_counts = []
        
        for region, data in region_results.items():
            if 'error' not in data:
                patterns = data['field_patterns']
                security_profile_name_counts.append(patterns['has_SecurityProfileName'])
                name_counts.append(patterns['has_Name'])
        
        if len(set(security_profile_name_counts)) > 1:
            recommendations.append("⚠️  Inconsistent SecurityProfileName field usage across regions")
        
        if len(set(name_counts)) > 1:
            recommendations.append("⚠️  Inconsistent Name field usage across regions")
        
        # Check for mixed usage within regions
        for region, data in region_results.items():
            if 'error' not in data:
                patterns = data['field_patterns']
                if patterns['has_both'] > 0:
                    recommendations.append(f"✅ {region}: Profiles have both SecurityProfileName and Name fields")
                elif patterns['has_SecurityProfileName'] > 0 and patterns['has_Name'] > 0:
                    recommendations.append(f"⚠️  {region}: Mixed field usage - some profiles use SecurityProfileName, others use Name")
                elif patterns['has_SecurityProfileName'] > 0:
                    recommendations.append(f"📋 {region}: All profiles use SecurityProfileName field")
                elif patterns['has_Name'] > 0:
                    recommendations.append(f"📋 {region}: All profiles use Name field")
                
                if patterns['has_neither'] > 0:
                    recommendations.append(f"❌ {region}: {patterns['has_neither']} profiles missing both name fields!")

def print_analysis_results(results: Dict):
    """
    Print formatted analysis results
    
    Args:
        results: Analysis results to print
    """
    print("\n" + "="*80)
    print("SECURITY PROFILE FIELD FORMAT ANALYSIS")
    print("="*80)
    
    print(f"Instance ID: {results['instance_id']}")
    print(f"Regions Analyzed: {', '.join(results['regions_analyzed'])}")
    print()
    
    # Print region-by-region results
    for region, data in results['region_results'].items():
        print(f"📍 REGION: {region.upper()}")
        print("-" * 40)
        
        if 'error' in data:
            print(f"❌ Error: {data['error']}")
            if 'error_code' in data:
                print(f"   Error Code: {data['error_code']}")
        else:
            print(f"Total Profiles: {data['total_profiles']}")
            print()
            
            # Field patterns
            patterns = data['field_patterns']
            print("Field Usage Patterns:")
            print(f"  • SecurityProfileName only: {patterns['has_SecurityProfileName']} profiles")
            print(f"  • Name only: {patterns['has_Name']} profiles")
            print(f"  • Both fields: {patterns['has_both']} profiles")
            print(f"  • Neither field: {patterns['has_neither']} profiles")
            print()
            
            # Sample profile structure
            if data['sample_profiles']:
                print("Sample Profile Structure:")
                sample = data['sample_profiles'][0]
                for field_name in sorted(sample.keys()):
                    field_value = sample[field_name]
                    if isinstance(field_value, str) and len(field_value) > 50:
                        field_value = field_value[:47] + "..."
                    print(f"  • {field_name}: {field_value}")
            print()
        
        print()
    
    # Print comparison analysis
    print("🔍 COMPARISON ANALYSIS")
    print("-" * 40)
    
    if results['comparison']['field_consistency']:
        print("Field Consistency Across Regions:")
        for region, consistency in results['comparison']['field_consistency'].items():
            print(f"  {region}:")
            for metric, value in consistency.items():
                print(f"    - {metric}: {value}")
        print()
    
    # Print recommendations
    if results['comparison']['recommendations']:
        print("📋 RECOMMENDATIONS:")
        for i, rec in enumerate(results['comparison']['recommendations'], 1):
            print(f"  {i}. {rec}")
    else:
        print("✅ No specific recommendations - field usage appears consistent")
    
    print("\n" + "="*80)

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze security profile field formats across AWS regions')
    parser.add_argument('--instance-id', required=True, help='Amazon Connect instance ID')
    parser.add_argument('--regions', nargs='+', default=['us-east-1', 'us-west-2'], 
                       help='AWS regions to analyze (default: us-east-1 us-west-2)')
    parser.add_argument('--profile', help='AWS profile name')
    parser.add_argument('--output', help='Output file path for JSON results')
    
    args = parser.parse_args()
    
    try:
        analyzer = SecurityProfileFieldAnalyzer(args.instance_id, args.profile)
        results = analyzer.compare_regions(args.regions)
        
        # Print results to console
        print_analysis_results(results)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Detailed results saved to: {args.output}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()