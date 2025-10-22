#!/usr/bin/env python3
"""
Example usage of Amazon Connect user migration scripts
Demonstrates how to use the export and import functionality programmatically
"""

import logging
from connect_user_export import ConnectUserExporter
from connect_user_import import ConnectUserImporter

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
    
    print("Amazon Connect User Migration Examples")
    print("=====================================")
    print("Update the configuration variables and uncomment the desired example function to run:")
    print("1. migrate_users_example() - Complete migration workflow")
    print("2. export_only_example() - Export users only")
    print("3. import_only_example() - Import users only")
    print("4. validate_export_file_example() - Validate export file")
    print("5. performance_optimization_example() - Optimize batch sizes")
    print("6. tag_preservation_example() - Demonstrate tag handling")