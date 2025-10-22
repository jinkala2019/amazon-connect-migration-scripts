#!/usr/bin/env python3
"""
Performance tuning examples and batch size optimization for Connect user migration
"""

import time
import logging
from connect_user_export import ConnectUserExporter
from connect_user_import import ConnectUserImporter

logger = logging.getLogger(__name__)

class PerformanceTuner:
    """Helper class for optimizing batch sizes and performance"""
    
    def __init__(self, instance_id: str, region: str = 'us-east-1', profile: str = None):
        self.instance_id = instance_id
        self.region = region
        self.profile = profile
    
    def benchmark_batch_sizes(self, export_file: str, test_sizes: list = None):
        """
        Test different batch sizes to find optimal performance
        
        Args:
            export_file: Path to export file
            test_sizes: List of batch sizes to test (default: [10, 25, 50, 100])
        """
        if not test_sizes:
            test_sizes = [10, 25, 50, 100]
        
        results = {}
        
        for batch_size in test_sizes:
            logger.info(f"Testing batch size: {batch_size}")
            
            try:
                importer = ConnectUserImporter(
                    instance_id=self.instance_id,
                    region=self.region,
                    profile=self.profile
                )
                
                start_time = time.time()
                
                # Run dry run to measure performance without creating users
                result = importer.import_users(
                    export_file=export_file,
                    batch_size=batch_size,
                    dry_run=True
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                results[batch_size] = {
                    'duration': duration,
                    'users_per_second': result['success'] / duration if duration > 0 else 0,
                    'success_count': result['success']
                }
                
                logger.info(f"Batch size {batch_size}: {duration:.2f}s, {results[batch_size]['users_per_second']:.2f} users/sec")
                
            except Exception as e:
                logger.error(f"Error testing batch size {batch_size}: {e}")
                results[batch_size] = {'error': str(e)}
        
        # Find optimal batch size
        best_batch_size = max(
            [size for size, result in results.items() if 'users_per_second' in result],
            key=lambda x: results[x]['users_per_second'],
            default=50
        )
        
        logger.info(f"Recommended batch size: {best_batch_size}")
        return results, best_batch_size

def optimized_export_example():
    """Example of optimized export for large datasets"""
    
    instance_id = "your-instance-id"
    
    # Configure for high performance
    exporter = ConnectUserExporter(instance_id=instance_id)
    
    logger.info("Starting optimized export for large dataset...")
    
    start_time = time.time()
    export_file = exporter.export_users()
    end_time = time.time()
    
    logger.info(f"Export completed in {end_time - start_time:.2f} seconds")
    logger.info(f"Export file: {export_file}")

def optimized_import_example():
    """Example of optimized import with different batch sizes"""
    
    instance_id = "your-target-instance-id"
    export_file = "users_export.json"
    
    # Test different configurations
    configurations = [
        {'batch_size': 25, 'description': 'Conservative (safest)'},
        {'batch_size': 50, 'description': 'Balanced (recommended)'},
        {'batch_size': 100, 'description': 'Aggressive (fastest)'},
    ]
    
    for config in configurations:
        logger.info(f"Testing {config['description']} - Batch size: {config['batch_size']}")
        
        try:
            importer = ConnectUserImporter(instance_id=instance_id)
            
            # Dry run first
            start_time = time.time()
            results = importer.import_users(
                export_file=export_file,
                batch_size=config['batch_size'],
                dry_run=True
            )
            end_time = time.time()
            
            duration = end_time - start_time
            users_per_second = results['success'] / duration if duration > 0 else 0
            
            logger.info(f"Performance: {users_per_second:.2f} users/second")
            logger.info(f"Results: {results}")
            
        except Exception as e:
            logger.error(f"Error with batch size {config['batch_size']}: {e}")

def memory_efficient_processing():
    """Example of memory-efficient processing for very large datasets"""
    
    instance_id = "your-instance-id"
    
    # For datasets larger than 50K users, consider processing in chunks
    exporter = ConnectUserExporter(instance_id=instance_id)
    
    # The exporter already handles memory efficiently with pagination
    # But you can monitor memory usage during export
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    logger.info(f"Initial memory usage: {initial_memory:.2f} MB")
    
    export_file = exporter.export_users()
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    logger.info(f"Final memory usage: {final_memory:.2f} MB")
    logger.info(f"Memory increase: {final_memory - initial_memory:.2f} MB")

# Recommended batch sizes based on dataset size
BATCH_SIZE_RECOMMENDATIONS = {
    'small': {       # < 1K users
        'batch_size': 100,
        'description': 'Small dataset - can use larger batches'
    },
    'medium': {      # 1K - 5K users
        'batch_size': 50,
        'description': 'Medium dataset - balanced approach'
    },
    'large': {       # 5K - 20K users
        'batch_size': 25,
        'description': 'Large dataset - conservative batching'
    },
    'very_large': {  # > 20K users
        'batch_size': 10,
        'description': 'Very large dataset - small batches for stability'
    }
}

def get_recommended_batch_size(user_count: int) -> dict:
    """Get recommended batch size based on user count"""
    
    if user_count < 1000:
        return BATCH_SIZE_RECOMMENDATIONS['small']
    elif user_count < 5000:
        return BATCH_SIZE_RECOMMENDATIONS['medium']
    elif user_count < 20000:
        return BATCH_SIZE_RECOMMENDATIONS['large']
    else:
        return BATCH_SIZE_RECOMMENDATIONS['very_large']

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    print("Performance tuning examples:")
    print("1. Uncomment optimized_export_example() to test export performance")
    print("2. Uncomment optimized_import_example() to test import performance")
    print("3. Uncomment memory_efficient_processing() to monitor memory usage")
    
    # optimized_export_example()
    # optimized_import_example()
    # memory_efficient_processing()
    
    # Show recommendations
    test_counts = [500, 2000, 10000, 50000]
    print("\nBatch size recommendations:")
    for count in test_counts:
        rec = get_recommended_batch_size(count)
        print(f"{count:,} users: {rec['batch_size']} batch size - {rec['description']}")