# Amazon Connect Phone Number Mapping Guide

## Overview

When migrating queues between Amazon Connect instances, phone numbers assigned to queues (outbound caller ID) need to be mapped from source instance phone number IDs to target instance phone number IDs. This guide explains how to handle phone number mapping during queue migration.

## The Problem

Queue configurations include `OutboundCallerConfig` which references phone number IDs:

```json
{
  "Queue": {
    "Name": "Sales Queue",
    "OutboundCallerConfig": {
      "OutboundCallerIdName": "Sales Team",
      "OutboundCallerIdNumberId": "phone-12345678-source-instance"
    }
  }
}
```

**Issue**: `phone-12345678-source-instance` doesn't exist in the target instance, even if the same phone number is available.

## Solution: Phone Number Mapping

### Scripts Involved

1. **`connect_phone_number_mapper.py`** - Utility to create phone number mappings
2. **Enhanced `connect_queue_import.py`** - Now supports phone number mapping during import

## Step-by-Step Process

### Step 1: Create Phone Number Mapping Template

```bash
# Generate mapping template between source and target instances
python connect_phone_number_mapper.py --action template \
  --source-instance source-instance-id \
  --target-instance target-instance-id \
  --output phone_mapping_template.json
```

**This creates a template file with:**
- All phone numbers from source instance
- All phone numbers from target instance  
- Auto-detected mappings for matching phone numbers
- Template for manual mappings

### Step 2: Review and Edit Mapping Template

The generated template looks like this:

```json
{
  "description": "Phone number ID mapping from source to target instance",
  "source_instance_id": "source-abc123",
  "target_instance_id": "target-xyz789",
  "instructions": {
    "1": "Review the source_phone_numbers and target_phone_numbers sections",
    "2": "Create mappings in the phone_number_mappings section",
    "3": "Map source phone number IDs to target phone number IDs"
  },
  "source_phone_numbers": {
    "phone-12345678-1234-1234": {
      "phone_number": "+1-800-555-0101",
      "type": "TOLL_FREE",
      "country_code": "US"
    },
    "phone-87654321-4321-4321": {
      "phone_number": "+1-555-123-4567",
      "type": "DID",
      "country_code": "US"
    }
  },
  "target_phone_numbers": {
    "phone-11111111-2222-3333": {
      "phone_number": "+1-800-555-0101",
      "type": "TOLL_FREE",
      "country_code": "US"
    },
    "phone-22222222-3333-4444": {
      "phone_number": "+1-555-987-6543",
      "type": "DID",
      "country_code": "US"
    }
  },
  "auto_detected_mappings": {
    "phone-12345678-1234-1234": "phone-11111111-2222-3333"
  },
  "phone_number_mappings": {
    "phone-12345678-1234-1234": "phone-11111111-2222-3333",
    "phone-87654321-4321-4321": "phone-22222222-3333-4444",
    "# Add your mappings here": "# source_id: target_id"
  }
}
```

**Edit the `phone_number_mappings` section** to map source phone IDs to target phone IDs.

### Step 3: Validate Mapping File

```bash
# Validate your mapping file
python connect_phone_number_mapper.py --action validate \
  --mapping-file phone_mapping_template.json
```

### Step 4: Extract Clean Mappings (Optional)

```bash
# Extract only the mappings for use with queue import
python connect_phone_number_mapper.py --action extract \
  --mapping-file phone_mapping_template.json \
  --output clean_phone_mappings.json
```

### Step 5: Import Queues with Phone Number Mapping

```bash
# Import queues with phone number mapping
python connect_queue_import.py \
  --instance-id target-instance-id \
  --export-file queues_export.json \
  --phone-mapping clean_phone_mappings.json \
  --dry-run

# If dry run looks good, run actual import
python connect_queue_import.py \
  --instance-id target-instance-id \
  --export-file queues_export.json \
  --phone-mapping clean_phone_mappings.json
```

## Phone Number Mapping Strategies

### Strategy 1: Exact Phone Number Matching (Automatic)

**Best for**: Same phone numbers exist in both instances

```json
{
  "phone-source-123": "phone-target-456"  // Both map to +1-800-555-0101
}
```

**Pros**: Automatic detection, maintains same caller ID
**Cons**: Requires same phone numbers in both instances

### Strategy 2: Manual Phone Number Assignment

**Best for**: Different phone numbers, specific business requirements

```json
{
  "phone-source-sales": "phone-target-main",     // Sales line -> Main line
  "phone-source-support": "phone-target-support" // Support line -> Support line
}
```

**Pros**: Full control over phone number assignment
**Cons**: Requires manual mapping for each phone number

### Strategy 3: Default Phone Number Fallback

**Best for**: When specific mapping isn't critical

**Configuration**: Don't provide mapping file, script uses first available phone number

**Pros**: Simple, no mapping required
**Cons**: May not preserve intended caller ID

## Command Line Options

### Phone Number Mapper Utility

```bash
python connect_phone_number_mapper.py [OPTIONS]

Actions:
  --action template     Create mapping template
  --action validate     Validate mapping file  
  --action extract      Extract clean mappings

Required for template:
  --source-instance TEXT    Source instance ID
  --target-instance TEXT    Target instance ID

Required for validate/extract:
  --mapping-file TEXT       Path to mapping file

Optional:
  --output TEXT            Output file path
  --region TEXT            AWS region (default: us-east-1)
  --profile TEXT           AWS profile name
```

### Enhanced Queue Import

```bash
python connect_queue_import.py [OPTIONS]

New Option:
  --phone-mapping TEXT     Path to phone number mapping file

Existing Options:
  --instance-id TEXT       Target instance ID (required)
  --export-file TEXT       Queue export file (required)
  --region TEXT            AWS region (default: us-east-1)
  --profile TEXT           AWS profile name
  --dry-run               Validate without creating queues
```

## Example Workflows

### Workflow 1: Complete Phone Number Mapping

```bash
# 1. Export queues from source
python connect_queue_export.py --instance-id source-id --bu-tag "Sales"

# 2. Create phone number mapping template
python connect_phone_number_mapper.py --action template \
  --source-instance source-id --target-instance target-id

# 3. Edit the template file manually (map phone numbers)

# 4. Validate mapping
python connect_phone_number_mapper.py --action validate \
  --mapping-file phone_mapping_template.json

# 5. Extract clean mappings
python connect_phone_number_mapper.py --action extract \
  --mapping-file phone_mapping_template.json

# 6. Import queues with phone mapping
python connect_queue_import.py --instance-id target-id \
  --export-file queues_export.json \
  --phone-mapping phone_mappings_clean.json
```

### Workflow 2: Auto-Detection Only

```bash
# 1. Create template (auto-detects matching phone numbers)
python connect_phone_number_mapper.py --action template \
  --source-instance source-id --target-instance target-id

# 2. Extract auto-detected mappings
python connect_phone_number_mapper.py --action extract \
  --mapping-file phone_mapping_template.json

# 3. Import with auto-detected mappings
python connect_queue_import.py --instance-id target-id \
  --export-file queues_export.json \
  --phone-mapping phone_mappings_clean.json
```

### Workflow 3: Default Fallback (No Mapping)

```bash
# Import without phone mapping (uses default phone number)
python connect_queue_import.py --instance-id target-id \
  --export-file queues_export.json
```

## Mapping File Formats

### Template File (Full)
```json
{
  "description": "Phone number ID mapping from source to target instance",
  "source_instance_id": "source-abc123",
  "target_instance_id": "target-xyz789",
  "source_phone_numbers": { /* All source phone numbers */ },
  "target_phone_numbers": { /* All target phone numbers */ },
  "phone_number_mappings": {
    "source-phone-id-1": "target-phone-id-1",
    "source-phone-id-2": "target-phone-id-2"
  }
}
```

### Clean Mappings File (Import Ready)
```json
{
  "source-phone-id-1": "target-phone-id-1",
  "source-phone-id-2": "target-phone-id-2"
}
```

## Log Output Examples

### Phone Number Mapping Creation
```
2024-01-15 14:30:25,123 - INFO - Fetching phone numbers from instance: source-abc123
2024-01-15 14:30:26,456 - INFO - Found 5 phone numbers in instance source-abc123
2024-01-15 14:30:27,789 - INFO - Fetching phone numbers from instance: target-xyz789
2024-01-15 14:30:28,012 - INFO - Found 3 phone numbers in instance target-xyz789
2024-01-15 14:30:29,234 - INFO - Auto-mapped phone number: +1-800-555-0101
2024-01-15 14:30:30,456 - INFO - Created 1 automatic mappings
2024-01-15 14:30:31,678 - INFO - Phone number mapping template created: phone_mapping_template.json
```

### Queue Import with Phone Mapping
```
2024-01-15 16:00:00,123 - INFO - Loaded 3 phone number mappings from clean_phone_mappings.json
2024-01-15 16:00:05,456 - INFO - Found 2 phone numbers in target instance
2024-01-15 16:00:10,789 - INFO - Mapped phone number ID: phone-source-123 -> phone-target-456
2024-01-15 16:00:11,012 - INFO - Created queue: Sales Queue -> queue-new-12345678
2024-01-15 16:00:12,234 - WARNING - Using default phone number for outbound caller ID: +1-555-987-6543 (phone-default-789)
```

## Troubleshooting

### Common Issues

#### No Phone Numbers Found
```
2024-01-15 14:30:30,123 - WARNING - Could not fetch phone numbers: AccessDenied
```
**Solution**: Add `connect:ListPhoneNumbers` permission to IAM policy

#### Phone Number Mapping Not Found
```
2024-01-15 16:00:15,456 - ERROR - No phone number mapping found for phone-source-123 and no default phone numbers available
```
**Solutions**:
- Add mapping for the specific phone number ID
- Ensure target instance has at least one phone number
- Check phone number mapping file format

#### Invalid Mapping File
```
2024-01-15 15:30:20,789 - ERROR - Invalid JSON in mapping file: Expecting ',' delimiter
```
**Solution**: Validate JSON syntax in mapping file

### Best Practices

1. **Always create mapping template first** to see available phone numbers
2. **Use auto-detection when possible** for exact phone number matches
3. **Validate mapping files** before using them for import
4. **Test with dry-run** to verify phone number mapping works
5. **Keep mapping files** for future migrations or rollbacks

## Required IAM Permissions

Add this permission to your existing IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "connect:ListPhoneNumbers"
      ],
      "Resource": "*"
    }
  ]
}
```

## Integration with Queue Migration

Phone number mapping integrates seamlessly with the existing queue migration process:

1. **Export queues** (captures outbound caller config with source phone IDs)
2. **Create phone mapping** (maps source phone IDs to target phone IDs)
3. **Import queues** (applies phone number mapping during queue creation)

This ensures that queue outbound caller ID configurations work correctly in the target instance with the appropriate phone numbers.