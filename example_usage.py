#!/usr/bin/env python3
"""
Example usage of Amazon Connect migration scripts
Demonstrates how to use the export, import, and helper utilities programmatically
"""

import json
import logging
from connect_user_export import ConnectUserExporter
from connect_user_import import ConnectUserImporter
from security_profile_helper import SecurityProfileHelper
from connect_queue_export import ConnectQueueExporter
from connect_queue_import import ConnectQueueImporter
from connect_phone_number_mapper import ConnectPhoneNumberMapper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_users_example():
    """
    Example of complete user migration workflow
    """
    # Configuration
    source_instance_id = "your-source-instance-id"
    target_instance_id = "your-target-instance-id"
    region = "us-east-1"
    aws_profile = None  # Use default credentials
    
    try:
        # Step 1: Export users from source instance
        logger.info("Starting user export...")
        exporter = ConnectUserExporter(
            instance_id=source_instance_id,
            region=region,
            profile=aws_profile
        )
        
        export_file = exporter.export_users("users_migration.json")
        logger.info(f"Export completed: {export_file}")
        
        # Step 2: Import users to target instance
        logger.info("Starting user import...")
        importer = ConnectUserImporter(
            instance_id=target_instance_id,
            region=region,
            profile=aws_profile
        )
        
        # First, run a dry run to validate
        logger.info("Running dry run validation...")
        dry_run_results = importer.import_users(
            export_file=export_file,
            batch_size=25,
            dry_run=True
        )
        
        logger.info(f"Dry run results: {dry_run_results}")
        
        # If dry run looks good, proceed with actual import
        if dry_run_results['success'] > 0:
            logger.info("Proceeding with actual import...")
            import_results = importer.import_users(
                export_file=export_file,
                batch_size=25,
                dry_run=False
            )
            
            logger.info(f"Import completed: {import_results}")
        else:
            logger.warning("Dry run showed no successful users, skipping import")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

def export_only_example():
    """
    Example of exporting users only
    """
    instance_id = "your-instance-id"
    
    try:
        exporter = ConnectUserExporter(instance_id=instance_id)
        
        # Export with custom filename
        export_file = exporter.export_users("my_users_backup.json")
        
        print(f"Users exported to: {export_file}")
        
    except Exception as e:
        print(f"Export failed: {e}")

def import_only_example():
    """
    Example of importing users only
    """
    instance_id = "your-target-instance-id"
    export_file = "users_export.json"
    
    try:
        importer = ConnectUserImporter(instance_id=instance_id)
        
        # Import with larger batch size for faster processing
        results = importer.import_users(
            export_file=export_file,
            batch_size=100,
            dry_run=False
        )
        
        print(f"Import results: {results}")
        
    except Exception as e:
        print(f"Import failed: {e}")

def validate_export_file_example():
    """
    Example of validating an export file before import
    """
    export_file = "users_export.json"
    target_instance_id = "your-target-instance-id"
    
    try:
        importer = ConnectUserImporter(instance_id=target_instance_id)
        
        # Load and validate the export file
        export_data = importer.load_export_data(export_file)
        
        print(f"Export file validation:")
        print(f"- Source instance: {export_data.get('InstanceId')}")
        print(f"- Export timestamp: {export_data.get('ExportTimestamp')}")
        print(f"- Total users: {export_data.get('TotalUsers')}")
        print(f"- Successful exports: {export_data.get('SuccessfulExports')}")
        print(f"- Failed exports: {export_data.get('FailedExports')}")
        
        # Analyze user data for tags and configurations
        users = export_data.get('Users', [])
        if users:
            sample_user = users[0]
            print(f"\nSample user analysis:")
            print(f"- Username: {sample_user['User'].get('Username')}")
            print(f"- Has user tags: {'Yes' if sample_user['User'].get('Tags') else 'No'}")
            print(f"- Has routing profile: {'Yes' if sample_user.get('RoutingProfile') else 'No'}")
            print(f"- Has routing profile tags: {'Yes' if sample_user.get('RoutingProfile', {}).get('Tags') else 'No'}")
            print(f"- Security profiles count: {len(sample_user.get('SecurityProfiles', []))}")
        
        # Run dry run to check compatibility
        results = importer.import_users(
            export_file=export_file,
            dry_run=True
        )
        
        print(f"\nCompatibility check results:")
        print(f"- Would succeed: {results['success']}")
        print(f"- Would fail: {results['failed']}")
        print(f"- Would skip: {results['skipped']}")
        
        if results['failed_users']:
            print(f"- Failed users sample: {results['failed_users'][:5]}")
        
    except Exception as e:
        print(f"Validation failed: {e}")

def performance_optimization_example():
    """
    Example of using performance optimization features
    """
    from performance_tuning import PerformanceTuner, get_recommended_batch_size
    
    export_file = "users_export.json"
    target_instance_id = "your-target-instance-id"
    
    try:
        # Load export data to get user count
        importer = ConnectUserImporter(instance_id=target_instance_id)
        export_data = importer.load_export_data(export_file)
        user_count = export_data.get('TotalUsers', 0)
        
        print(f"Optimizing for {user_count:,} users...")
        
        # Get recommended batch size
        recommendation = get_recommended_batch_size(user_count)
        print(f"Recommended batch size: {recommendation['batch_size']} - {recommendation['description']}")
        
        # Run performance benchmark
        tuner = PerformanceTuner(target_instance_id)
        results, best_batch = tuner.benchmark_batch_sizes(export_file)
        
        print(f"Benchmark results:")
        for batch_size, result in results.items():
            if 'users_per_second' in result:
                print(f"  Batch {batch_size}: {result['users_per_second']:.2f} users/sec")
        
        print(f"Optimal batch size for your environment: {best_batch}")
        
    except Exception as e:
        print(f"Performance optimization failed: {e}")

def tag_preservation_example():
    """
    Example demonstrating tag preservation during migration
    """
    source_instance_id = "your-source-instance-id"
    target_instance_id = "your-target-instance-id"
    
    try:
        # Export with focus on tag preservation
        exporter = ConnectUserExporter(instance_id=source_instance_id)
        export_file = exporter.export_users("tagged_users_export.json")
        
        # Analyze tags in export
        export_data = exporter.load_export_data if hasattr(exporter, 'load_export_data') else None
        if not export_data:
            importer = ConnectUserImporter(instance_id=target_instance_id)
            export_data = importer.load_export_data(export_file)
        
        users_with_tags = 0
        routing_profiles_with_tags = 0
        
        for user_data in export_data.get('Users', []):
            if user_data['User'].get('Tags'):
                users_with_tags += 1
            if user_data.get('RoutingProfile', {}).get('Tags'):
                routing_profiles_with_tags += 1
        
        print(f"Tag analysis:")
        print(f"- Users with tags: {users_with_tags}")
        print(f"- Routing profiles with tags: {routing_profiles_with_tags}")
        
        # Import with tag preservation
        importer = ConnectUserImporter(instance_id=target_instance_id)
        results = importer.import_users(
            export_file=export_file,
            batch_size=25,  # Conservative for tag-heavy imports
            dry_run=True
        )
        
        print(f"Import simulation results:")
        print(f"- Users that would be created with tags: {results['success']}")
        
    except Exception as e:
        print(f"Tag preservation example failed: {e}")

def cross_region_migration_example():
    """
    Example of complete cross-region migration workflow with security profile handling
    """
    # Configuration
    source_instance_id = "your-source-instance-id"
    target_instance_id = "your-target-instance-id"
    source_region = "us-east-1"
    target_region = "eu-west-1"
    aws_profile = None
    
    try:
        # Step 1: Export users from source region
        logger.info("Step 1: Exporting users from source region...")
        exporter = ConnectUserExporter(
            instance_id=source_instance_id,
            region=source_region,
            profile=aws_profile
        )
        
        export_file = exporter.export_users("cross_region_users_export.json")
        logger.info(f"Export completed: {export_file}")
        
        # Step 2: Analyze security profiles for target region
        logger.info("Step 2: Analyzing security profiles...")
        security_helper = SecurityProfileHelper(region=target_region, profile=aws_profile)
        
        # Compare security profiles between regions
        comparison = security_helper.compare_security_profiles(export_file, target_instance_id)
        
        print(f"Security Profile Analysis:")
        print(f"- Required profiles: {len(comparison['required_profiles'])}")
        print(f"- Missing profiles: {len(comparison['missing_profiles'])}")
        print(f"- Available profiles: {len(comparison['existing_profiles'])}")
        
        # Step 3: Create missing security profiles if needed
        if comparison['missing_profiles']:
            logger.info("Step 3: Creating missing security profiles...")
            commands = security_helper.generate_security_profile_commands(export_file, target_instance_id)
            
            # Save commands to script file
            script_file = f"create_security_profiles_{target_instance_id}.sh"
            with open(script_file, 'w') as f:
                f.write("#!/bin/bash\n")
                f.write("# Auto-generated security profile creation script\n\n")
                for command in commands:
                    f.write(f"{command}\n")
            
            print(f"Security profile creation script saved: {script_file}")
            print("Run this script to create missing security profiles before importing users")
        
        # Step 4: Import users to target region (dry run first)
        logger.info("Step 4: Running import dry run...")
        importer = ConnectUserImporter(
            instance_id=target_instance_id,
            region=target_region,
            profile=aws_profile
        )
        
        dry_run_results = importer.import_users(
            export_file=export_file,
            batch_size=25,
            dry_run=True
        )
        
        print(f"Cross-region migration dry run results:")
        print(f"- Would succeed: {dry_run_results['success']}")
        print(f"- Would fail: {dry_run_results['failed']}")
        print(f"- Would skip: {dry_run_results['skipped']}")
        
        if dry_run_results['success'] > 0 and not comparison['missing_profiles']:
            logger.info("Step 5: Proceeding with actual import...")
            import_results = importer.import_users(
                export_file=export_file,
                batch_size=25,
                dry_run=False
            )
            
            print(f"Cross-region migration completed:")
            print(f"- Successfully migrated: {import_results['success']} users")
            print(f"- Failed: {import_results['failed']} users")
        else:
            print("Create missing security profiles first, then run import manually")
        
    except Exception as e:
        logger.error(f"Cross-region migration failed: {e}")
        raise

def security_profile_analysis_example():
    """
    Example of using the security profile helper for analysis and creation
    """
    export_file = "users_export.json"
    target_instance_id = "your-target-instance-id"
    region = "us-east-1"
    
    try:
        # Initialize security profile helper
        security_helper = SecurityProfileHelper(region=region)
        
        # Step 1: Analyze export file
        print("Step 1: Analyzing export file for security profile requirements...")
        analysis = security_helper.analyze_export_file(export_file)
        
        print(f"Export Analysis Results:")
        print(f"- Total users: {analysis['total_users']}")
        print(f"- Unique security profiles required: {len(analysis['required_profiles'])}")
        print(f"- Security profiles by name:")
        for profile_name, count in analysis['profile_usage'].items():
            print(f"  - {profile_name}: {count} users")
        
        # Step 2: Compare with target instance
        print("\nStep 2: Comparing with target instance...")
        comparison = security_helper.compare_security_profiles(export_file, target_instance_id)
        
        print(f"Comparison Results:")
        print(f"- Existing profiles: {len(comparison['existing_profiles'])}")
        print(f"- Missing profiles: {len(comparison['missing_profiles'])}")
        
        if comparison['missing_profiles']:
            print(f"Missing profiles:")
            for profile in comparison['missing_profiles']:
                print(f"  - {profile}")
        
        # Step 3: Generate creation commands if needed
        if comparison['missing_profiles']:
            print("\nStep 3: Generating creation commands...")
            commands = security_helper.generate_security_profile_commands(export_file, target_instance_id)
            
            print(f"Generated {len(commands)} AWS CLI commands:")
            for i, command in enumerate(commands[:3], 1):  # Show first 3 as examples
                print(f"  {i}. {command}")
            
            if len(commands) > 3:
                print(f"  ... and {len(commands) - 3} more commands")
        
    except Exception as e:
        print(f"Security profile analysis failed: {e}")

def queue_migration_with_prefix_example():
    """
    Example of exporting queues with BU tag and queue name prefix filtering
    """
    instance_id = "your-instance-id"
    bu_tag_value = "YourBU"
    queue_prefix = "Q_QC_"  # Only export queues starting with Q_QC_
    region = "us-east-1"
    
    try:
        # Export queues with both BU tag and prefix filtering
        print(f"Exporting queues with BU tag '{bu_tag_value}' and prefix '{queue_prefix}'...")
        
        queue_exporter = ConnectQueueExporter(
            instance_id=instance_id,
            bu_tag_value=bu_tag_value,
            queue_prefix=queue_prefix,
            region=region
        )
        
        export_file = queue_exporter.export_queues()
        print(f"Queue export completed: {export_file}")
        
        # Load and analyze the export
        with open(export_file, 'r') as f:
            export_data = json.load(f)
        
        print(f"Export Summary:")
        print(f"- Total queues scanned: {export_data['TotalQueuesScanned']}")
        print(f"- Matching queues exported: {export_data['TotalQueues']}")
        print(f"- BU tag filter: {export_data['BUTagValue']}")
        print(f"- Queue prefix filter: {export_data['QueuePrefix']}")
        
        # Show sample queue names
        if export_data['Queues']:
            print(f"Sample exported queue names:")
            for queue in export_data['Queues'][:5]:
                print(f"  - {queue['Queue']['Name']}")
        
        # Example without prefix filtering (all queues for BU)
        print(f"\nComparing with export of all queues for BU '{bu_tag_value}'...")
        
        queue_exporter_all = ConnectQueueExporter(
            instance_id=instance_id,
            bu_tag_value=bu_tag_value,
            region=region
        )
        
        export_file_all = queue_exporter_all.export_queues("all_queues_export.json")
        
        with open(export_file_all, 'r') as f:
            export_data_all = json.load(f)
        
        print(f"All queues export: {export_data_all['TotalQueues']} queues")
        print(f"Prefix filtered export: {export_data['TotalQueues']} queues")
        print(f"Filtering saved: {export_data_all['TotalQueues'] - export_data['TotalQueues']} queues")
        
    except Exception as e:
        print(f"Queue migration with prefix example failed: {e}")

def phone_number_mapping_example():
    """
    Example of creating phone number mappings for cross-region migration
    """
    source_instance_id = "your-source-instance-id"
    target_instance_id = "your-target-instance-id"
    source_region = "us-east-1"
    target_region = "eu-west-1"
    
    try:
        # Step 1: Create mapping template
        print("Step 1: Creating phone number mapping template...")
        
        phone_mapper = ConnectPhoneNumberMapper(region=source_region)
        template_file = phone_mapper.create_mapping_template(
            source_instance_id, 
            target_instance_id,
            target_region=target_region
        )
        
        print(f"Mapping template created: {template_file}")
        
        # Step 2: Load and show template structure
        with open(template_file, 'r') as f:
            template_data = json.load(f)
        
        print(f"Template contains:")
        print(f"- Source instance: {template_data['source_instance']}")
        print(f"- Target instance: {template_data['target_instance']}")
        print(f"- Source region: {template_data['source_region']}")
        print(f"- Target region: {template_data['target_region']}")
        print(f"- Phone numbers to map: {len(template_data['phone_mappings'])}")
        
        # Show sample mappings
        if template_data['phone_mappings']:
            print(f"Sample phone number mappings needed:")
            for phone_number, mapping in list(template_data['phone_mappings'].items())[:3]:
                print(f"  {phone_number}: {mapping['source_id']} -> [TARGET_ID_NEEDED]")
        
        # Step 3: Validate mapping (assuming user filled it out)
        print(f"\nStep 3: Validating mapping file...")
        
        # For demo, create a sample filled mapping
        sample_mapping = template_file.replace('.json', '_filled.json')
        filled_data = template_data.copy()
        
        # Simulate filling out target IDs (in real usage, user would do this)
        for phone_number, mapping in filled_data['phone_mappings'].items():
            mapping['target_id'] = f"target-{mapping['source_id'][-8:]}"  # Demo target ID
        
        with open(sample_mapping, 'w') as f:
            json.dump(filled_data, f, indent=2)
        
        # Validate the filled mapping
        validation_result = phone_mapper.validate_mapping_file(sample_mapping)
        
        print(f"Validation results:")
        print(f"- Valid mappings: {validation_result['valid_mappings']}")
        print(f"- Invalid mappings: {validation_result['invalid_mappings']}")
        print(f"- Missing target IDs: {validation_result['missing_target_ids']}")
        
        if validation_result['valid_mappings'] > 0:
            print(f"Mapping file is ready for use in queue import!")
            print(f"Use: --phone-mapping {sample_mapping}")
        
    except Exception as e:
        print(f"Phone number mapping example failed: {e}")

if __name__ == "__main__":
    # Uncomment the example you want to run
    
    # Full migration example
    # migrate_users_example()
    
    # Export only
    # export_only_example()
    
    # Import only
    # import_only_example()
    
    # Validate export file
    # validate_export_file_example()
    
    # Performance optimization
    # performance_optimization_example()
    
    # Tag preservation demonstration
    # tag_preservation_example()
    
    # Cross-region migration with security profiles
    # cross_region_migration_example()
    
    # Security profile analysis and creation
    # security_profile_analysis_example()
    
    # Queue export with prefix filtering
    # queue_migration_with_prefix_example()
    
    # Phone number mapping for cross-region
    # phone_number_mapping_example()
    
    print("Amazon Connect Migration Examples")
    print("=================================")
    print("Update the configuration variables and uncomment the desired example function to run:")
    print("1. migrate_users_example() - Complete migration workflow")
    print("2. export_only_example() - Export users only")
    print("3. import_only_example() - Import users only")
    print("4. validate_export_file_example() - Validate export file")
    print("5. performance_optimization_example() - Optimize batch sizes")
    print("6. tag_preservation_example() - Demonstrate tag handling")
    print("7. cross_region_migration_example() - Cross-region migration with security profiles")
    print("8. security_profile_analysis_example() - Analyze and create security profiles")
    print("9. queue_migration_with_prefix_example() - Export queues with prefix filtering")
    print("10. phone_number_mapping_example() - Create phone number mappings for cross-region")