# Amazon Connect Migration - Log Format Guide

## Log File Locations

### Export Script Logs
- **File**: `connect_export.log` (created in current directory)
- **Console**: Also displays on screen in real-time
- **Script**: `connect_user_export.py`

### Import Script Logs
- **File**: `connect_import.log` (created in current directory)
- **Console**: Also displays on screen in real-time
- **Script**: `connect_user_import.py`

## Log Format Structure

### Standard Format
```
YYYY-MM-DD HH:MM:SS,mmm - LEVEL - MESSAGE
```

**Example:**
```
2024-01-15 14:30:25,123 - INFO - Initialized exporter for instance: abc123 in region: us-east-1
2024-01-15 14:30:26,456 - INFO - Fetching users page 1...
2024-01-15 14:30:27,789 - WARNING - Could not fetch routing profile for user user-123: AccessDenied
2024-01-15 14:30:28,012 - ERROR - AWS API error while fetching users: RateLimitExceeded
```

### Log Levels Used
- **INFO**: Normal operation progress and success messages
- **WARNING**: Non-critical issues that don't stop processing
- **ERROR**: Critical errors that may cause failures

## Export Script Log Examples

### Successful Export Process
```
2024-01-15 14:30:25,123 - INFO - Initialized exporter for instance: abc123 in region: us-east-1
2024-01-15 14:30:26,456 - INFO - Fetching users page 1...
2024-01-15 14:30:27,789 - INFO - Retrieved 1000 users from page 1
2024-01-15 14:30:28,012 - INFO - Fetching users page 2...
2024-01-15 14:30:29,234 - INFO - Retrieved 1000 users from page 2
2024-01-15 14:30:30,456 - INFO - Fetching users page 3...
2024-01-15 14:30:31,678 - INFO - Retrieved 500 users from page 3
2024-01-15 14:30:32,890 - INFO - Total users retrieved: 2500
2024-01-15 14:30:33,012 - INFO - Exporting user 1/2500: john.doe (user-123)
2024-01-15 14:30:34,234 - INFO - Exporting user 2/2500: jane.smith (user-456)
2024-01-15 14:30:35,456 - WARNING - Could not fetch hierarchy group for user user-789: ResourceNotFound
2024-01-15 14:30:36,678 - INFO - Exporting user 3/2500: bob.wilson (user-789)
...
2024-01-15 15:45:12,345 - INFO - Export completed successfully!
2024-01-15 15:45:12,346 - INFO - Exported 2495 users to connect_users_export_abc123_20240115_143025.json
2024-01-15 15:45:12,347 - INFO - Failed exports: 5
```

### Export Errors
```
2024-01-15 14:30:25,123 - ERROR - AWS API error while fetching users: InvalidInstanceId
2024-01-15 14:30:26,456 - ERROR - Failed to export user john.doe (user-123): AccessDenied
2024-01-15 14:30:27,789 - WARNING - Could not fetch routing profile for user user-456: ResourceNotFound
2024-01-15 14:30:28,012 - WARNING - Could not fetch security profile sp-789 for user user-456: AccessDenied
```

## Import Script Log Examples

### Successful Import Process
```
2024-01-15 16:00:00,123 - INFO - Initialized importer for instance: xyz789 in region: us-east-1
2024-01-15 16:00:01,234 - INFO - Starting user import process (dry_run=False)...
2024-01-15 16:00:02,345 - INFO - Loaded export data from users_export.json
2024-01-15 16:00:02,346 - INFO - Total users in export: 2500
2024-01-15 16:00:03,456 - INFO - Fetching existing routing profiles...
2024-01-15 16:00:04,567 - INFO - Fetching existing security profiles...
2024-01-15 16:00:05,678 - INFO - Fetching existing hierarchy groups...
2024-01-15 16:00:06,789 - INFO - Found 15 routing profiles
2024-01-15 16:00:06,790 - INFO - Found 8 security profiles
2024-01-15 16:00:06,791 - INFO - Found 5 hierarchy groups
2024-01-15 16:00:07,890 - INFO - Processing batch 1/50 (50 users)
2024-01-15 16:00:08,012 - INFO - Created user: john.doe -> user-new-123
2024-01-15 16:00:09,123 - INFO - Created user: jane.smith -> user-new-456
2024-01-15 16:00:10,234 - WARNING - User already exists: bob.wilson
2024-01-15 16:00:11,345 - INFO - Created routing profile: Custom Sales Profile -> rp-new-789
2024-01-15 16:00:12,456 - INFO - Created user: alice.johnson -> user-new-789
...
2024-01-15 16:00:15,678 - INFO - Waiting between batches...
2024-01-15 16:00:17,789 - INFO - Processing batch 2/50 (50 users)
...
2024-01-15 17:30:45,123 - INFO - Import process completed!
2024-01-15 17:30:45,124 - INFO - Successful: 2480
2024-01-15 17:30:45,125 - INFO - Failed: 15
2024-01-15 17:30:45,126 - INFO - Skipped: 5
2024-01-15 17:30:45,127 - INFO - Failed users: user1, user2, user3, user4, user5, user6, user7, user8, user9, user10
2024-01-15 17:30:45,128 - INFO - ... and 5 more
```

### Import Warnings and Errors
```
2024-01-15 16:00:10,234 - WARNING - Routing profile not found: Custom Agent Profile
2024-01-15 16:00:11,345 - WARNING - Security profile not found: Custom Security Profile
2024-01-15 16:00:12,456 - WARNING - Hierarchy group not found: Special Team
2024-01-15 16:00:13,567 - ERROR - Cannot create user john.doe: No valid routing profile
2024-01-15 16:00:14,678 - ERROR - Cannot create user jane.smith: No valid security profiles
2024-01-15 16:00:15,789 - ERROR - Error creating user bob.wilson: InvalidParameterException
2024-01-15 16:00:16,890 - ERROR - Failed to create routing profile Custom Profile: InvalidParameterException
2024-01-15 16:00:17,012 - ERROR - Unexpected error creating user alice.johnson: ConnectionTimeout
```

### Dry Run Mode Logs
```
2024-01-15 16:00:00,123 - INFO - Starting user import process (dry_run=True)...
2024-01-15 16:00:05,456 - INFO - Processing batch 1/50 (50 users)
2024-01-15 16:00:06,567 - INFO - [DRY RUN] Would create user: john.doe
2024-01-15 16:00:07,678 - INFO - [DRY RUN] Would create user: jane.smith
2024-01-15 16:00:08,789 - WARNING - [DRY RUN] Would skip user: bob.wilson (missing resources)
2024-01-15 16:00:09,890 - INFO - [DRY RUN] Would create user: alice.johnson
```

## Resource Mapping Logs

### Routing Profile Mapping
```
2024-01-15 16:00:10,123 - INFO - Created routing profile: Sales Agent Profile -> rp-new-123
2024-01-15 16:00:11,234 - WARNING - Routing profile already exists: Basic Agent Profile
2024-01-15 16:00:12,345 - ERROR - Error creating routing profile Custom Profile: InvalidParameterException
2024-01-15 16:00:13,456 - ERROR - Failed to create routing profile Special Profile: Queue queue-123 not found
```

### User Creation Logs
```
2024-01-15 16:00:15,123 - INFO - Created user: john.doe -> user-new-123
2024-01-15 16:00:16,234 - WARNING - User already exists: jane.smith
2024-01-15 16:00:17,345 - ERROR - Error creating user bob.wilson: DuplicateResourceException
2024-01-15 16:00:18,456 - ERROR - Cannot create user alice.johnson: No valid routing profile
```

## Performance and Progress Logs

### Batch Processing
```
2024-01-15 16:00:00,123 - INFO - Processing batch 1/100 (25 users)
2024-01-15 16:00:30,456 - INFO - Waiting between batches...
2024-01-15 16:00:32,789 - INFO - Processing batch 2/100 (25 users)
```

### Rate Limiting
```
2024-01-15 16:00:45,123 - INFO - Waiting between batches...
2024-01-15 16:01:00,456 - WARNING - Rate limit detected, extending wait time...
```

## Log Analysis Tips

### Finding Successful Operations
```bash
# Count successful user creations
grep "Created user:" connect_import.log | wc -l

# List all created users
grep "Created user:" connect_import.log
```

### Finding Errors
```bash
# Find all errors
grep "ERROR" connect_import.log

# Find specific error types
grep "Cannot create user" connect_import.log
grep "Error creating user" connect_import.log
```

### Finding Warnings
```bash
# Find all warnings
grep "WARNING" connect_import.log

# Find resource mapping issues
grep "not found" connect_import.log
```

### Performance Analysis
```bash
# Find batch processing times
grep "Processing batch" connect_import.log

# Find rate limiting events
grep "Waiting between batches" connect_import.log
```

## Log Rotation and Management

### File Sizes
- Export logs: Typically 1-10 MB for 10K users
- Import logs: Typically 2-20 MB for 10K users (more verbose)

### Cleanup
```bash
# Archive old logs
mv connect_export.log connect_export_$(date +%Y%m%d).log
mv connect_import.log connect_import_$(date +%Y%m%d).log

# Compress old logs
gzip connect_*_$(date +%Y%m%d).log
```

## Integration with Monitoring

### Log Parsing for Monitoring
```python
import re

def parse_import_results(log_file):
    with open(log_file, 'r') as f:
        content = f.read()
    
    # Extract final results
    success_match = re.search(r'Successful: (\d+)', content)
    failed_match = re.search(r'Failed: (\d+)', content)
    skipped_match = re.search(r'Skipped: (\d+)', content)
    
    return {
        'success': int(success_match.group(1)) if success_match else 0,
        'failed': int(failed_match.group(1)) if failed_match else 0,
        'skipped': int(skipped_match.group(1)) if skipped_match else 0
    }
```