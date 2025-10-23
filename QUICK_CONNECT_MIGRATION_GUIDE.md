# Amazon Connect Quick Connect Migration Guide

## Overview

This guide covers the migration of Quick Connects between Amazon Connect instances, including complete configuration preservation and tag handling.

## Scripts Included

- **`connect_quick_connect_export.py`** - Export all quick connects from source instance
- **`connect_quick_connect_import.py`** - Import quick connects to target instance

## Features

- ✅ **Complete Configuration Export** - All quick connect settings and configurations
- ✅ **Tag Preservation** - Maintains all custom tags during migration
- ✅ **Conflict Resolution** - Handles existing quick connects gracefully
- ✅ **Dry Run Mode** - Validate imports without making changes
- ✅ **Automatic Logging** - Comprehensive progress tracking and error reporting
- ✅ **Resource Mapping** - Maps user and queue references between instances

## Quick Start

### 1. Export Quick Connects
```bash
# Export all quick connects (auto-generated filename)
python connect_quick_connect_export.py --instance-id source-instance-id

# Creates: connect_quick_connects_export_source-instance-id_YYYYMMDD_HHMMSS.json
```

### 2. Validate Import
```bash
# Test import without making changes
python connect_quick_connect_import.py --instance-id target-instance-id --export-file quick_connects_export.json --dry-run
```

### 3. Import Quick Connects
```bash
# Actually import quick connects
python connect_quick_connect_import.py --instance-id target-instance-id --export-file quick_connects_export.json
```

## Command Line Options

### Export Script
```bash
python connect_quick_connect_export.py [OPTIONS]

Required:
  --instance-id TEXT    Source Amazon Connect instance ID

Optional:
  --region TEXT         AWS region (default: us-east-1)
  --profile TEXT        AWS profile name
  --output TEXT         Output file path (auto-generated if not specified)
```

### Import Script
```bash
python connect_quick_connect_import.py [OPTIONS]

Required:
  --instance-id TEXT    Target Amazon Connect instance ID
  --export-file TEXT    Path to the export file

Optional:
  --region TEXT         AWS region (default: us-east-1)
  --profile TEXT        AWS profile name
  --dry-run            Validate without creating quick connects
```

## Usage Examples

### Export Examples
```bash
# Basic export with auto-generated filename
python connect_quick_connect_export.py --instance-id abc123-def456-ghi789

# Export with custom filename
python connect_quick_connect_export.py --instance-id abc123 --output my_quick_connects.json

# Export using specific AWS profile
python connect_quick_connect_export.py --instance-id abc123 --profile production --region eu-west-1

# Export from different region
python connect_quick_connect_export.py --instance-id abc123 --region ap-southeast-1
```

### Import Examples
```bash
# Dry run to validate import (recommended first step)
python connect_quick_connect_import.py --instance-id target-123 --export-file quick_connects_export.json --dry-run

# Import quick connects
python connect_quick_connect_import.py --instance-id target-123 --export-file quick_connects_export.json

# Import using specific AWS profile
python connect_quick_connect_import.py --instance-id target-123 --export-file qc_export.json --profile staging

# Import to different region
python connect_quick_connect_import.py --instance-id target-123 --export-file qc_export.json --region eu-central-1
```

## Export File Structure

The export file contains complete quick connect configurations:

```json
{
  "InstanceId": "source-instance-id",
  "ExportTimestamp": "2024-01-15T14:30:25Z",
  "TotalQuickConnects": 50,
  "SuccessfulExports": 48,
  "FailedExports": 2,
  "QuickConnects": [
    {
      "QuickConnect": {
        "QuickConnectId": "qc-12345678-1234-1234-1234-123456789012",
        "QuickConnectARN": "arn:aws:connect:us-east-1:123456789012:instance/abc123/quick-connect/qc-12345678",
        "Name": "Sales Team Lead",
        "Description": "Connect directly to sales team lead",
        "QuickConnectConfig": {
          "QuickConnectType": "USER",
          "UserConfig": {
            "UserId": "user-87654321-4321-4321-4321-210987654321",
            "ContactFlowId": "flow-11111111-2222-3333-4444-555555555555"
          }
        }
      },
      "Tags": {
        "Department": "Sales",
        "Priority": "High",
        "CreatedBy": "admin@company.com"
      },
      "ExportTimestamp": "2024-01-15T14:30:25Z"
    },
    {
      "QuickConnect": {
        "QuickConnectId": "qc-87654321-4321-4321-4321-210987654321",
        "QuickConnectARN": "arn:aws:connect:us-east-1:123456789012:instance/abc123/quick-connect/qc-87654321",
        "Name": "Support Queue",
        "Description": "Transfer to support queue",
        "QuickConnectConfig": {
          "QuickConnectType": "QUEUE",
          "QueueConfig": {
            "QueueId": "queue-11111111-2222-3333-4444-555555555555",
            "ContactFlowId": "flow-22222222-3333-4444-5555-666666666666"
          }
        }
      },
      "Tags": {
        "Department": "Support",
        "Priority": "Medium"
      },
      "ExportTimestamp": "2024-01-15T14:30:25Z"
    },
    {
      "QuickConnect": {
        "QuickConnectId": "qc-11111111-2222-3333-4444-555555555555",
        "QuickConnectARN": "arn:aws:connect:us-east-1:123456789012:instance/abc123/quick-connect/qc-11111111",
        "Name": "External Number",
        "Description": "Transfer to external phone number",
        "QuickConnectConfig": {
          "QuickConnectType": "PHONE_NUMBER",
          "PhoneConfig": {
            "PhoneNumber": "+1234567890"
          }
        }
      },
      "Tags": {
        "Type": "External",
        "Region": "US"
      },
      "ExportTimestamp": "2024-01-15T14:30:25Z"
    }
  ],
  "FailedQuickConnects": [
    {
      "QuickConnectId": "qc-failed-1234",
      "Name": "Failed QC",
      "Error": "AccessDenied: Insufficient permissions"
    }
  ]
}
```

## Quick Connect Types Supported

### 1. User Quick Connects
**Purpose**: Direct transfer to specific agents
```json
"QuickConnectConfig": {
  "QuickConnectType": "USER",
  "UserConfig": {
    "UserId": "user-id-in-source-instance",
    "ContactFlowId": "contact-flow-id"
  }
}
```

### 2. Queue Quick Connects
**Purpose**: Transfer to specific queues
```json
"QuickConnectConfig": {
  "QuickConnectType": "QUEUE",
  "QueueConfig": {
    "QueueId": "queue-id-in-source-instance",
    "ContactFlowId": "contact-flow-id"
  }
}
```

### 3. Phone Number Quick Connects
**Purpose**: Transfer to external phone numbers
```json
"QuickConnectConfig": {
  "QuickConnectType": "PHONE_NUMBER",
  "PhoneConfig": {
    "PhoneNumber": "+1234567890"
  }
}
```

## Resource Mapping

### How Resource Mapping Works

The import script handles resource ID mapping between source and target instances:

1. **User Quick Connects**: Maps user IDs (requires users to exist in target)
2. **Queue Quick Connects**: Maps queue IDs (requires queues to exist in target)
3. **Phone Number Quick Connects**: No mapping needed (phone numbers are universal)

### Current Limitations

- **User/Queue Mapping**: Currently uses original IDs (enhancement needed for name-based mapping)
- **Contact Flow Mapping**: Uses original contact flow IDs (may need manual adjustment)

## Log Files and Monitoring

### Log File Locations
- **Export Log**: `connect_quick_connect_export.log`
- **Import Log**: `connect_quick_connect_import.log`

### Sample Log Output

#### Export Process
```
2024-01-15 14:30:25,123 - INFO - Initialized quick connect exporter for instance: abc123 in region: us-east-1
2024-01-15 14:30:26,456 - INFO - Fetching quick connects page 1...
2024-01-15 14:30:27,789 - INFO - Retrieved 50 quick connects from page 1
2024-01-15 14:30:28,012 - INFO - Total quick connects retrieved: 50
2024-01-15 14:30:29,234 - INFO - Exporting quick connect 1/50: Sales Team Lead (qc-12345678)
2024-01-15 14:30:30,456 - INFO - Exporting quick connect 2/50: Support Queue (qc-87654321)
2024-01-15 14:30:31,678 - WARNING - Could not fetch tags for quick connect qc-failed-1234: AccessDenied
2024-01-15 14:35:45,890 - INFO - Export completed successfully!
2024-01-15 14:35:45,891 - INFO - Exported 48 quick connects to connect_quick_connects_export_abc123_20240115_143025.json
2024-01-15 14:35:45,892 - INFO - Failed exports: 2
```

#### Import Process
```
2024-01-15 16:00:00,123 - INFO - Initialized quick connect importer for instance: xyz789 in region: us-east-1
2024-01-15 16:00:01,234 - INFO - Starting quick connect import process (dry_run=False)...
2024-01-15 16:00:02,345 - INFO - Loaded export data from quick_connects_export.json
2024-01-15 16:00:02,346 - INFO - Total quick connects in export: 48
2024-01-15 16:00:03,456 - INFO - Fetching existing quick connects...
2024-01-15 16:00:04,567 - INFO - Found 10 existing quick connects
2024-01-15 16:00:05,678 - INFO - Created quick connect: Sales Team Lead -> qc-new-12345678
2024-01-15 16:00:06,789 - WARNING - Quick connect already exists: Support Queue
2024-01-15 16:00:07,890 - INFO - Created quick connect: External Number -> qc-new-87654321
2024-01-15 16:00:15,123 - INFO - Import process completed!
2024-01-15 16:00:15,124 - INFO - Successful: 46
2024-01-15 16:00:15,125 - INFO - Failed: 1
2024-01-15 16:00:15,126 - INFO - Skipped: 1
```

#### Dry Run Process
```
2024-01-15 15:30:00,123 - INFO - Starting quick connect import process (dry_run=True)...
2024-01-15 15:30:05,456 - INFO - [DRY RUN] Would create quick connect: Sales Team Lead
2024-01-15 15:30:06,567 - INFO - [DRY RUN] Would create quick connect: External Number
2024-01-15 15:30:07,678 - WARNING - Quick connect already exists: Support Queue
2024-01-15 15:30:10,890 - INFO - Import process completed!
2024-01-15 15:30:10,891 - INFO - Successful: 47
2024-01-15 15:30:10,892 - INFO - Failed: 0
2024-01-15 15:30:10,893 - INFO - Skipped: 1
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Export Issues

**No Quick Connects Found**
```
2024-01-15 14:30:30,123 - WARNING - No quick connects found to export
```
**Solution**: Verify instance ID and ensure quick connects exist in source instance

**Permission Denied During Export**
```
2024-01-15 14:30:31,456 - ERROR - AWS API error while fetching quick connects: AccessDenied
```
**Solution**: Check IAM permissions for `connect:ListQuickConnects` and `connect:DescribeQuickConnect`

**Tag Access Issues**
```
2024-01-15 14:30:32,789 - WARNING - Could not fetch tags for quick connect qc-123: AccessDenied
```
**Solution**: Add `connect:ListTagsForResource` permission to IAM policy

#### 2. Import Issues

**Quick Connect Creation Failures**
```
2024-01-15 16:00:10,234 - ERROR - Error creating quick connect Sales Lead: InvalidParameterException
```
**Solution**: Check that referenced users/queues exist in target instance

**Quick Connect 'Name' Field Errors** ✅ **FIXED**
```
2024-01-15 16:00:09,123 - ERROR - Quick connect missing 'Name' field in data: {...}
```
**Solution**: Enhanced error handling now gracefully handles malformed export data and provides detailed error messages

**Resource Mapping Issues**
```
2024-01-15 16:00:11,345 - WARNING - User mapping for quick connect not fully implemented
```
**Solution**: Ensure users and queues exist in target instance with same IDs, or manually map resources

**Duplicate Quick Connects**
```
2024-01-15 16:00:12,456 - WARNING - Quick connect already exists: Support Queue
```
**Solution**: This is normal behavior - existing quick connects are skipped (not overwritten)

**Malformed Export Data** ✅ **FIXED**
```
2024-01-15 16:00:08,789 - ERROR - Quick connect missing 'Name' field, skipping: Unknown - Missing Name
```
**Solution**: Script now validates data structure and continues processing other quick connects when individual items are malformed

### Performance Optimization

#### Large Datasets
- Export processes quick connects in batches with rate limiting
- Import includes automatic delays between operations
- Monitor logs for throttling warnings

#### Network Issues
- Scripts include retry logic for transient failures
- Use `--region` parameter to specify closest AWS region
- Consider running from EC2 instance in same region for better performance

## Best Practices

### Pre-Migration Checklist
1. **Verify Permissions**: Ensure IAM permissions for both source and target instances
2. **Test Connectivity**: Run a small export/import test first
3. **Document Dependencies**: Note which users/queues quick connects reference
4. **Backup Strategy**: Keep export files as backup of quick connect configurations

### Migration Process
1. **Export First**: Always export before making any changes
2. **Dry Run**: Use `--dry-run` to validate import before execution
3. **Monitor Logs**: Watch logs during import for any issues
4. **Verify Results**: Check target instance to confirm quick connects were created correctly

### Post-Migration Validation
1. **Count Verification**: Compare total counts between source and target
2. **Functionality Testing**: Test quick connect functionality in target instance
3. **Tag Verification**: Confirm all tags were preserved
4. **Resource References**: Verify user/queue references work correctly

## Required IAM Permissions

Add these permissions to your IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "connect:ListQuickConnects",
        "connect:DescribeQuickConnect",
        "connect:CreateQuickConnect",
        "connect:ListTagsForResource",
        "connect:ListUsers",
        "connect:ListQueues"
      ],
      "Resource": "*"
    }
  ]
}
```

## Integration with Other Migrations

Quick Connect migration works well with other Amazon Connect resource migrations:

1. **User Migration**: Import users before quick connects that reference them
2. **Queue Migration**: Import queues before quick connects that reference them
3. **Contact Flow Migration**: Import contact flows before quick connects that use them

### Recommended Migration Order
1. Contact Flows
2. Users
3. Queues
4. **Quick Connects** ← This guide
5. Routing Profiles (that reference quick connects)