# Amazon Connect Queue Migration Guide with BU Tag Filtering

## Overview

This guide covers the migration of Queues between Amazon Connect instances with advanced BU (Business Unit) tag-based filtering. Export only queues that match specific BU tag values and import them with all associated quick connects and configurations.

## Scripts Included

- **`connect_queue_export.py`** - Export queues filtered by BU tag value
- **`connect_queue_import.py`** - Import queues with associated quick connects

## Key Features

- ✅ **BU Tag Filtering** - Export only queues matching specific BU tag values
- ✅ **Standard Queue Focus** - Exports only STANDARD queues (excludes AGENT queues)
- ✅ **Runtime BU Parameter** - Pass BU tag value at runtime
- ✅ **Case-Insensitive Matching** - Matches BU tags regardless of case
- ✅ **Multiple Tags Support** - Handles queues with multiple tags
- ✅ **Associated Quick Connects** - Automatically exports/imports linked quick connects
- ✅ **Complete Configuration** - All queue settings, outbound caller config, tags
- ✅ **Automatic Resource Creation** - Creates missing quick connects during import
- ✅ **Dry Run Mode** - Validate imports without making changes

## Quick Start

### 1. Export Queues by BU Tag
```bash
# Export all queues tagged with BU="Sales"
python connect_queue_export.py --instance-id source-instance-id --bu-tag "Sales"

# Creates: connect_queues_export_source-instance-id_Sales_YYYYMMDD_HHMMSS.json
```

### 2. Validate Import
```bash
# Test import without making changes
python connect_queue_import.py --instance-id target-instance-id --export-file queues_export.json --dry-run
```

### 3. Import Queues
```bash
# Actually import queues and associated quick connects
python connect_queue_import.py --instance-id target-instance-id --export-file queues_export.json
```

## BU Tag Filtering

### How BU Tag Filtering Works

The queue export script filters queues based on the `BU` tag (Business Unit):

1. **Queue Type Filtering**: Only processes STANDARD queues (AGENT queues are automatically excluded)
2. **Tag Key Matching**: Looks for tag keys `BU`, `bu`, `Bu` (case-insensitive)
3. **Value Matching**: Compares tag values (case-insensitive)
4. **Multiple Tags Support**: Queues can have multiple tags; only BU tag is used for filtering
5. **Complete Export**: Exports all configurations and associated quick connects for matching queues

### Queue Types Supported

**STANDARD Queues Only**: The script automatically filters for standard queues and excludes agent queues to prevent ARN format issues and ensure proper migration compatibility.

## Queue Name Prefix Filtering

### How Queue Prefix Filtering Works

The `--queue-prefix` parameter allows you to export only queues whose names start with a specific string, in addition to matching the BU tag.

**Filtering Logic**: Queue must match BOTH conditions:
1. **BU Tag Match**: Queue has the specified BU tag value
2. **Name Prefix Match**: Queue name starts with the specified prefix (case-sensitive)

### Queue Prefix Examples

#### Example 1: Export QC Queues Only
```bash
# Export only queues starting with "Q_QC_" and BU tag "Sales"
python connect_queue_export.py --instance-id abc123 --bu-tag "Sales" --queue-prefix "Q_QC_"

# This will match:
# - Q_QC_Sales_General (BU=Sales, starts with Q_QC_) ✅
# - Q_QC_Sales_Priority (BU=Sales, starts with Q_QC_) ✅

# This will NOT match:
# - Sales_General (BU=Sales, but doesn't start with Q_QC_) ❌
# - Q_QC_Support_General (starts with Q_QC_, but BU=Support) ❌
```

#### Example 2: Export Department-Specific Queues
```bash
# Export only sales department queues
python connect_queue_export.py --instance-id abc123 --bu-tag "Sales" --queue-prefix "SALES_"

# Export only support department queues  
python connect_queue_export.py --instance-id abc123 --bu-tag "Support" --queue-prefix "SUP_"
```

#### Example 3: Export All Queues (No Prefix Filter)
```bash
# Export all queues with BU tag "Sales" (any name)
python connect_queue_export.py --instance-id abc123 --bu-tag "Sales"
# No --queue-prefix parameter = exports all queue names
```

### BU Tag Examples

#### Example 1: Standard BU Tag
```json
Queue Tags: {
  "BU": "Sales",
  "Environment": "Production",
  "Owner": "john.doe@company.com",
  "Priority": "High"
}
```
**Command**: `--bu-tag "Sales"` ✅ **Matches**

#### Example 2: Case Variations
```json
Queue Tags: {
  "bu": "support",
  "Department": "Customer Service",
  "Region": "US-East"
}
```
**Command**: `--bu-tag "Support"` ✅ **Matches** (case-insensitive)

#### Example 3: Different BU Value
```json
Queue Tags: {
  "BU": "Marketing",
  "Campaign": "Q1-2024",
  "Budget": "50000"
}
```
**Command**: `--bu-tag "Sales"` ❌ **No Match**

#### Example 4: No BU Tag
```json
Queue Tags: {
  "Environment": "Production",
  "Owner": "jane.smith@company.com"
}
```
**Command**: `--bu-tag "Sales"` ❌ **No Match**

### Multiple BU Export Examples
```bash
# Export different BUs separately
python connect_queue_export.py --instance-id source-id --bu-tag "Sales" --output sales_queues.json
python connect_queue_export.py --instance-id source-id --bu-tag "Support" --output support_queues.json
python connect_queue_export.py --instance-id source-id --bu-tag "Marketing" --output marketing_queues.json
```

## Command Line Options

### Queue Export Script
```bash
python connect_queue_export.py [OPTIONS]

Required:
  --instance-id TEXT    Source Amazon Connect instance ID
  --bu-tag TEXT         BU tag value to filter queues

Optional:
  --queue-prefix TEXT   Queue name prefix to filter (e.g., "Q_QC_" for queues starting with Q_QC_)
  --region TEXT         AWS region (default: us-east-1)
  --profile TEXT        AWS profile name
  --output TEXT         Output file path (auto-generated if not specified)
```

### Queue Import Script
```bash
python connect_queue_import.py [OPTIONS]

Required:
  --instance-id TEXT    Target Amazon Connect instance ID
  --export-file TEXT    Path to the export file

Optional:
  --region TEXT         AWS region (default: us-east-1)
  --profile TEXT        AWS profile name
  --dry-run            Validate without creating queues
  --phone-mapping TEXT  Path to phone number mapping file (see Phone Number Mapping section)
```

## Usage Examples

### Export Examples
```bash
# Basic export with BU tag filtering (all queues)
python connect_queue_export.py --instance-id abc123-def456 --bu-tag "Sales"

# Export queues with specific prefix and BU tag
python connect_queue_export.py --instance-id abc123 --bu-tag "Sales" --queue-prefix "Q_QC_"

# Export queues starting with "SALES_" and BU tag "Sales"
python connect_queue_export.py --instance-id abc123 --bu-tag "Sales" --queue-prefix "SALES_"

# Export with custom filename
python connect_queue_export.py --instance-id abc123 --bu-tag "Support" --queue-prefix "SUP_" --output support_queues.json

# Export using specific AWS profile
python connect_queue_export.py --instance-id abc123 --bu-tag "Marketing" --queue-prefix "MKT_" --profile production

# Export from different region
python connect_queue_export.py --instance-id abc123 --bu-tag "Sales" --region eu-west-1

# Case-insensitive BU tag matching (prefix is case-sensitive)
python connect_queue_export.py --instance-id abc123 --bu-tag "sales" --queue-prefix "Q_QC_"  # Matches BU="Sales"
```

### Import Examples
```bash
# Dry run to validate import (recommended first step)
python connect_queue_import.py --instance-id target-123 --export-file sales_queues.json --dry-run

# Import queues with associated quick connects
python connect_queue_import.py --instance-id target-123 --export-file sales_queues.json

# Import with phone number mapping (recommended for production)
python connect_queue_import.py --instance-id target-123 --export-file sales_queues.json --phone-mapping phone_mappings.json

# Import using specific AWS profile
python connect_queue_import.py --instance-id target-123 --export-file queues.json --profile staging

# Import to different region
python connect_queue_import.py --instance-id target-123 --export-file queues.json --region ap-southeast-1
```

## Export File Structure

The export file contains complete queue configurations with BU filtering results:

```json
{
  "InstanceId": "source-instance-id",
  "BUTagValue": "Sales",
  "QueuePrefix": "Q_QC_",
  "ExportTimestamp": "2024-01-15T14:30:25Z",
  "TotalQueuesScanned": 100,
  "MatchingQueues": 15,
  "SuccessfulExports": 14,
  "FailedExports": 1,
  "Queues": [
    {
      "Queue": {
        "QueueId": "queue-12345678-1234-1234-1234-123456789012",
        "QueueArn": "arn:aws:connect:us-east-1:123456789012:instance/abc123/queue/queue-12345678",
        "Name": "Sales General Queue",
        "Description": "General sales inquiries and support",
        "Status": "ENABLED",
        "MaxContacts": 50,
        "HoursOfOperationId": "hours-87654321-4321-4321-4321-210987654321",
        "OutboundCallerConfig": {
          "OutboundCallerIdName": "Sales Team",
          "OutboundCallerIdNumberId": "phone-11111111-2222-3333-4444-555555555555"
        }
      },
      "Tags": {
        "BU": "Sales",
        "Priority": "High",
        "Region": "US-East",
        "Manager": "sales.manager@company.com"
      },
      "QuickConnects": [
        {
          "QuickConnect": {
            "QuickConnectId": "qc-11111111-2222-3333-4444-555555555555",
            "QuickConnectARN": "arn:aws:connect:us-east-1:123456789012:instance/abc123/quick-connect/qc-11111111",
            "Name": "Sales Manager",
            "Description": "Escalate to sales manager",
            "QuickConnectConfig": {
              "QuickConnectType": "USER",
              "UserConfig": {
                "UserId": "user-22222222-3333-4444-5555-666666666666",
                "ContactFlowId": "flow-33333333-4444-5555-6666-777777777777"
              }
            }
          },
          "Tags": {
            "Role": "Manager",
            "Department": "Sales"
          }
        },
        {
          "QuickConnect": {
            "QuickConnectId": "qc-22222222-3333-4444-5555-666666666666",
            "QuickConnectARN": "arn:aws:connect:us-east-1:123456789012:instance/abc123/quick-connect/qc-22222222",
            "Name": "Sales Support Line",
            "Description": "External sales support number",
            "QuickConnectConfig": {
              "QuickConnectType": "PHONE_NUMBER",
              "PhoneConfig": {
                "PhoneNumber": "+1-800-SALES-01"
              }
            }
          },
          "Tags": {
            "Type": "External",
            "Department": "Sales"
          }
        }
      ],
      "OutboundCallerConfig": {
        "OutboundCallerIdName": "Sales Team",
        "OutboundCallerIdNumberId": "phone-11111111-2222-3333-4444-555555555555"
      },
      "ExportTimestamp": "2024-01-15T14:30:25Z"
    }
  ],
  "FailedQueues": [
    {
      "QueueId": "queue-failed-1234",
      "Name": "Failed Queue",
      "Error": "AccessDenied: Insufficient permissions to read queue configuration"
    }
  ]
}
```

## Phone Number Mapping

### Why Phone Number Mapping is Needed

Queues often have outbound caller ID configurations that reference phone number IDs from the source instance. These IDs don't exist in the target instance, even if the same phone numbers are available.

**Example Issue**:
```json
{
  "OutboundCallerConfig": {
    "OutboundCallerIdName": "Sales Team",
    "OutboundCallerIdNumberId": "phone-source-12345678"  // Doesn't exist in target
  }
}
```

### Phone Number Mapping Process

**Simple Approach (Recommended):**

1. **Create simple mapping file**:
```json
{
  "source-phone-id-1": "target-phone-id-1",
  "source-phone-id-2": "target-phone-id-2"
}
```

2. **Import queues with mapping**:
```bash
python connect_queue_import.py --instance-id target-id \
  --export-file queues_export.json \
  --phone-mapping my_phone_mappings.json
```

**For step-by-step instructions, see `SIMPLE_PHONE_MAPPING_GUIDE.md`**

**For advanced mapping features, see `PHONE_NUMBER_MAPPING_GUIDE.md`**

## Migration Workflow

### Complete BU Migration Process
```bash
# Step 1: Export queues for specific BU
python connect_queue_export.py --instance-id source-instance-id --bu-tag "Sales"

# Step 2: Validate import with dry run
python connect_queue_import.py --instance-id target-instance-id --export-file queues_export.json --dry-run

# Step 3: Review dry run results and fix any issues

# Step 4: Import queues (creates missing quick connects automatically)
python connect_queue_import.py --instance-id target-instance-id --export-file queues_export.json
```

### Multi-BU Migration Strategy
```bash
# Export each BU separately for organized migration
python connect_queue_export.py --instance-id source-id --bu-tag "Sales" --output sales_queues.json
python connect_queue_export.py --instance-id source-id --bu-tag "Support" --output support_queues.json
python connect_queue_export.py --instance-id source-id --bu-tag "Marketing" --output marketing_queues.json

# Import to same target instance
python connect_queue_import.py --instance-id target-id --export-file sales_queues.json
python connect_queue_import.py --instance-id target-id --export-file support_queues.json
python connect_queue_import.py --instance-id target-id --export-file marketing_queues.json

# Or import to different target instances per BU
python connect_queue_import.py --instance-id sales-target-id --export-file sales_queues.json
python connect_queue_import.py --instance-id support-target-id --export-file support_queues.json
python connect_queue_import.py --instance-id marketing-target-id --export-file marketing_queues.json
```

## Log Files and Monitoring

### Log File Locations
- **Export Log**: `connect_queue_export.log`
- **Import Log**: `connect_queue_import.log`

### Sample Log Output

#### Export Process with BU Filtering
```
2024-01-15 14:30:25,123 - INFO - Initialized queue exporter for instance: abc123, BU: Sales in region: us-east-1
2024-01-15 14:30:26,456 - INFO - Fetching queues page 1...
2024-01-15 14:30:27,789 - INFO - Retrieved 100 queues from page 1
2024-01-15 14:30:28,012 - INFO - Total queues retrieved: 100
2024-01-15 14:30:29,234 - INFO - Queue matches BU tag 'Sales': Sales General Queue
2024-01-15 14:30:30,456 - INFO - Queue matches BU tag 'Sales': Sales Priority Queue
2024-01-15 14:30:31,678 - DEBUG - Queue does not match BU tag: Support General Queue (tags: {'BU': 'Support', 'Priority': 'Medium'})
2024-01-15 14:30:32,890 - INFO - Queue matches BU tag 'Sales': Sales VIP Queue
2024-01-15 14:30:35,123 - INFO - Found 15 queues matching BU tag 'Sales'
2024-01-15 14:30:36,345 - INFO - Exporting queue 1/15: Sales General Queue (queue-12345678)
2024-01-15 14:30:37,567 - INFO - Exporting queue 2/15: Sales Priority Queue (queue-87654321)
2024-01-15 14:35:45,890 - INFO - Export completed successfully!
2024-01-15 14:35:45,891 - INFO - Scanned 100 total queues
2024-01-15 14:35:45,892 - INFO - Found 15 queues matching BU tag 'Sales'
2024-01-15 14:35:45,893 - INFO - Exported 14 queues to connect_queues_export_abc123_Sales_20240115_143025.json
2024-01-15 14:35:45,894 - INFO - Failed exports: 1
```

#### Import Process
```
2024-01-15 16:00:00,123 - INFO - Initialized queue importer for instance: xyz789 in region: us-east-1
2024-01-15 16:00:01,234 - INFO - Starting queue import process (dry_run=False)...
2024-01-15 16:00:02,345 - INFO - Loaded export data from sales_queues.json
2024-01-15 16:00:02,346 - INFO - Source instance: abc123
2024-01-15 16:00:02,347 - INFO - BU tag value: Sales
2024-01-15 16:00:02,348 - INFO - Total queues in export: 14
2024-01-15 16:00:03,456 - INFO - Fetching existing queues...
2024-01-15 16:00:04,567 - INFO - Fetching existing quick connects...
2024-01-15 16:00:05,678 - INFO - Found 5 queues, 10 quick connects, 3 hours of operations
2024-01-15 16:00:06,789 - INFO - Created queue: Sales General Queue -> queue-new-12345678
2024-01-15 16:00:07,890 - INFO - Creating missing quick connect: Sales Manager
2024-01-15 16:00:08,012 - INFO - Created quick connect: Sales Manager -> qc-new-11111111
2024-01-15 16:00:09,123 - INFO - Will associate quick connect Sales Manager (qc-new-11111111) to queue
2024-01-15 16:00:10,234 - INFO - Associated 2 quick connects to queue queue-new-12345678
2024-01-15 16:00:11,345 - WARNING - Queue already exists: Sales Priority Queue
2024-01-15 16:00:25,567 - INFO - Import process completed!
2024-01-15 16:00:25,568 - INFO - Successful: 13
2024-01-15 16:00:25,569 - INFO - Failed: 0
2024-01-15 16:00:25,570 - INFO - Skipped: 1
```

#### Dry Run Process
```
2024-01-15 15:30:00,123 - INFO - Starting queue import process (dry_run=True)...
2024-01-15 15:30:05,456 - INFO - [DRY RUN] Would create queue: Sales General Queue
2024-01-15 15:30:06,567 - INFO - [DRY RUN] Would create queue: Sales VIP Queue
2024-01-15 15:30:07,678 - WARNING - Queue already exists: Sales Priority Queue
2024-01-15 15:30:10,890 - INFO - Import process completed!
2024-01-15 15:30:10,891 - INFO - Successful: 13
2024-01-15 15:30:10,892 - INFO - Failed: 0
2024-01-15 15:30:10,893 - INFO - Skipped: 1
```

## Troubleshooting

### Common Issues and Solutions

#### 1. BU Tag Filtering Issues

**No Queues Found with BU Tag**
```
2024-01-15 14:30:30,123 - WARNING - No queues found with BU tag 'InvalidBU'
```
**Solutions**:
- Verify BU tag values exist in source instance
- Check tag spelling and case (though matching is case-insensitive)
- Use AWS Console to verify queue tags
- Try listing all queues first to see available BU values

**Case Sensitivity Confusion**
```bash
# These all work the same (case-insensitive)
--bu-tag "Sales"
--bu-tag "sales" 
--bu-tag "SALES"
--bu-tag "SaLeS"
```

#### 2. Export Issues

**Permission Denied for Queue Tags**
```
2024-01-15 14:30:31,456 - WARNING - Could not fetch tags for queue arn:aws:connect:...: AccessDenied
```
**Solution**: Add `connect:ListTagsForResource` permission to IAM policy

**Queue ARN Format Errors** ✅ **FIXED**
```
2024-01-15 14:30:32,123 - WARNING - Invalid ARN format for queue tagging: invalid-arn-format
```
**Solution**: Enhanced ARN validation now handles inconsistent ARN field names and validates format before API calls

**BadRequestException on Queue Tags** ✅ **FIXED**
```
2024-01-15 14:30:33,456 - WARNING - Invalid ARN format for queue tagging: arn:aws:connect:...
```
**Solution**: Script now tries multiple ARN field names and gracefully handles invalid ARNs without stopping the export

**Queue Access Issues**
```
2024-01-15 14:30:32,789 - ERROR - AWS API error while fetching queue details for queue-123: AccessDenied
```
**Solution**: Ensure `connect:DescribeQueue` permission for source instance

**Missing Queue ARNs** ✅ **FIXED**
```
2024-01-15 14:30:34,567 - WARNING - No valid ARN found for queue Sales Queue (queue-123), skipping tag check
```
**Solution**: Script now continues processing queues even when ARNs are unavailable, using empty tags as fallback

#### 3. Import Issues

**Hours of Operation Missing**
```
2024-01-15 16:00:10,234 - ERROR - Cannot create queue Sales Queue: No valid hours of operation
```
**Solutions**:
- Create basic hours of operation in target instance first
- Use AWS Console to set up default 24/7 hours of operation
- Import hours of operation before queues

**Quick Connect Creation Failures**
```
2024-01-15 16:00:11,345 - ERROR - Error creating quick connect Sales Manager: InvalidParameterException
```
**Solutions**:
- Ensure referenced users exist in target instance
- Verify contact flow IDs are valid in target instance
- Check quick connect configuration for invalid parameters

**Resource Mapping Issues**
```
2024-01-15 16:00:12,456 - WARNING - Using default hours of operation: Basic Hours (hours-default-123)
```
**Solution**: This is expected behavior when exact hours of operation mapping isn't available

#### 4. Performance Issues

**Large Dataset Processing**
```bash
# For instances with many queues, increase logging to monitor progress
# The script automatically handles pagination and rate limiting
```

**API Throttling**
```
2024-01-15 14:30:35,123 - WARNING - Rate limit detected, extending wait time...
```
**Solution**: Script automatically handles this, but you can reduce concurrent operations if needed

### Validation Steps

#### Pre-Export Validation
```bash
# Verify source instance access
aws connect list-queues --instance-id source-instance-id --region us-east-1

# Check available BU tag values (manual verification)
# Use AWS Console to review queue tags before export
```

#### Post-Export Validation
```bash
# Check export file size and content
ls -la connect_queues_export_*.json

# Verify BU filtering worked correctly
grep -c "\"BU\": \"Sales\"" connect_queues_export_*.json
```

#### Post-Import Validation
```bash
# Verify queues were created in target instance
aws connect list-queues --instance-id target-instance-id --region us-east-1

# Check queue count matches expectations
# Test queue functionality in Connect console
```

## Best Practices

### Pre-Migration Planning
1. **Inventory BU Tags**: Document all BU tag values in source instance
2. **Dependency Mapping**: Identify hours of operation and contact flow dependencies
3. **Resource Prerequisites**: Ensure basic resources exist in target instance
4. **Access Verification**: Test IAM permissions for both source and target instances

### Migration Execution
1. **Start Small**: Test with one BU before migrating all
2. **Use Dry Run**: Always validate with `--dry-run` first
3. **Monitor Progress**: Watch logs during export/import processes
4. **Batch Processing**: Migrate one BU at a time for better control

### Post-Migration Verification
1. **Count Verification**: Compare queue counts between source and target
2. **Functionality Testing**: Test queue routing and quick connect functionality
3. **Tag Verification**: Confirm all BU tags and other tags were preserved
4. **Integration Testing**: Verify queues work with routing profiles and contact flows

## Required IAM Permissions

Add these permissions to your IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "connect:ListQueues",
        "connect:DescribeQueue",
        "connect:CreateQueue",
        "connect:ListQuickConnects",
        "connect:DescribeQuickConnect",
        "connect:CreateQuickConnect",
        "connect:ListQueueQuickConnects",
        "connect:AssociateQueueQuickConnects",
        "connect:ListHoursOfOperations",
        "connect:ListTagsForResource"
      ],
      "Resource": "*"
    }
  ]
}
```

## Integration with Other Migrations

Queue migration works best when coordinated with other Amazon Connect resource migrations:

### Recommended Migration Order
1. **Hours of Operations** (prerequisite for queues)
2. **Contact Flows** (referenced by quick connects)
3. **Users** (referenced by user-type quick connects)
4. **Quick Connects** (can be created automatically during queue import)
5. **Queues** ← This guide
6. **Routing Profiles** (reference queues)

### BU-Based Migration Strategy
When migrating by Business Unit, consider this approach:

1. **Export all BUs separately** for organized migration
2. **Migrate shared resources first** (hours of operations, contact flows)
3. **Import BU-specific queues** one at a time
4. **Validate each BU** before proceeding to the next
5. **Update routing profiles** to reference new queue IDs