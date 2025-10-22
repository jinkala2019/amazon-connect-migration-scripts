# Simple Phone Number Mapping Guide

## Overview

When migrating queues between Amazon Connect instances, you need to map phone number IDs from the source instance to corresponding phone number IDs in the target instance.

## Simple 3-Step Process

### Step 1: Get Phone Number IDs

**From Source Instance:**
1. Go to AWS Connect Console → Source Instance → Phone Numbers
2. Copy the phone number IDs you want to map

**From Target Instance:**
1. Go to AWS Connect Console → Target Instance → Phone Numbers  
2. Copy the corresponding phone number IDs

### Step 2: Create Mapping File

Create a simple JSON file with source → target mappings:

**File: `my_phone_mappings.json`**
```json
{
  "phone-12345678-1234-1234-1234-123456789012": "phone-87654321-4321-4321-4321-210987654321",
  "11111111-2222-3333-4444-555555555555": "22222222-3333-4444-5555-666666666666",
  "abcd1234-5678-90ef-ghij-klmnopqrstuv": "wxyz9876-5432-10fe-dcba-zyxwvutsrqpo"
}
```

**Format**: `"source-phone-id": "target-phone-id"`

**IMPORTANT**: Use whatever Phone Number IDs AWS returns - format varies by region and creation date!

### Step 3: Import Queues with Phone Mapping

```bash
python connect_queue_import.py \
  --instance-id target-instance-id \
  --export-file queues_export.json \
  --phone-mapping my_phone_mappings.json
```

## Template Files Available

### Option 1: Use Template File
Copy `phone_number_mapping_template.json` and edit it:

```json
{
  "description": "Phone number mapping from source to target instance",
  "phone_number_mappings": {
    "source-phone-id-1": "target-phone-id-1",
    "source-phone-id-2": "target-phone-id-2"
  }
}
```

### Option 2: Use Simple Format
Create your own simple JSON file:

```json
{
  "phone-12345678-1234-1234-1234-123456789012": "phone-87654321-4321-4321-4321-210987654321",
  "phone-11111111-2222-3333-4444-555555555555": "phone-22222222-3333-4444-5555-666666666666"
}
```

**Remember**: Use actual Phone Number IDs from AWS Connect!

**Both formats work with the import script!**

## How to Find Phone Number IDs

**IMPORTANT**: You need Phone Number IDs, not the actual phone numbers!

**Phone Number ID Formats** (AWS Connect uses different formats):
- `phone-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (newer format)
- `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (UUID format without prefix)
- Other AWS-generated unique identifiers

### Method 1: AWS Console
1. Open AWS Connect Console
2. Go to your instance → Phone Numbers
3. Click on a phone number to see its details
4. Look for **"Phone number ID"** field
5. Copy the ID (starts with `phone-` followed by UUID format)

**Examples**:
- Phone Number: `+1-800-555-0101`
- Phone Number ID: `phone-12345678-1234-1234-1234-123456789012` ← **Use this in mapping**
- Or: `12345678-1234-1234-1234-123456789012` ← **Also valid format**
- Or: `arn:aws:connect:us-east-1:123456789012:phone-number/12345678-1234-1234-1234-123456789012` ← **Extract the ID part**

### Method 2: AWS CLI
```bash
# List phone numbers for source instance
aws connect list-phone-numbers --instance-id source-instance-id

# List phone numbers for target instance  
aws connect list-phone-numbers --instance-id target-instance-id
```

**CLI Output Examples**:

**Format 1 (with phone- prefix):**
```json
{
  "Id": "phone-12345678-1234-1234-1234-123456789012",
  "PhoneNumber": "+18005550101"
}
```

**Format 2 (UUID only):**
```json
{
  "Id": "12345678-1234-1234-1234-123456789012",
  "PhoneNumber": "+18005550101"
}
```

**Format 3 (other AWS formats):**
```json
{
  "Id": "abcd1234-5678-90ef-ghij-klmnopqrstuv",
  "PhoneNumber": "+18005550101"
}
```

**Always use whatever is in the "Id" field** - the format varies by AWS region and when the phone number was created!

### Method 3: Use the Mapper Utility (Optional)
If you want to see all phone numbers at once:

```bash
python connect_phone_number_mapper.py --action template \
  --source-instance source-id --target-instance target-id
```

This creates a detailed template with all phone numbers listed.

## Real Example

**Scenario**: You have a sales queue that uses phone number `+1-800-555-SALES` for outbound calls.

**Source Instance Phone Numbers:**
- `+1-800-555-SALES` → ID: `phone-12345678-1234-1234-1234-123456789012`
- `+1-555-123-4567` → ID: `phone-11111111-2222-3333-4444-555555555555`

**Target Instance Phone Numbers:**
- `+1-800-555-SALES` → ID: `phone-87654321-4321-4321-4321-210987654321`
- `+1-555-987-6543` → ID: `phone-22222222-3333-4444-5555-666666666666`

**Mapping File (`sales_phone_mapping.json`):**
```json
{
  "phone-12345678-1234-1234-1234-123456789012": "phone-87654321-4321-4321-4321-210987654321"
}
```

**Import Command:**
```bash
python connect_queue_import.py \
  --instance-id target-instance-id \
  --export-file sales_queues.json \
  --phone-mapping sales_phone_mapping.json
```

## What Happens Without Phone Mapping?

If you don't provide phone mapping:
- ✅ Queues will still be created
- ⚠️ Script will use the first available phone number in target instance
- ⚠️ You'll see warnings in logs about using default phone numbers

**Log Example:**
```
2024-01-15 16:00:12,234 - WARNING - Using default phone number for outbound caller ID: +1-555-987-6543 (phone-default-789)
```

## Quick Commands

### Export queues
```bash
python connect_queue_export.py --instance-id source-id --bu-tag "Sales"
```

### Import without phone mapping (uses defaults)
```bash
python connect_queue_import.py --instance-id target-id --export-file queues_export.json
```

### Import with phone mapping (recommended)
```bash
python connect_queue_import.py --instance-id target-id --export-file queues_export.json --phone-mapping my_mappings.json
```

## Common Mistakes to Avoid

### ❌ DON'T Use These Formats:

**Phone Numbers**:
```json
{
  "+1-800-555-0101": "+1-800-555-0102"  // WRONG - These are phone numbers
}
```

**ARNs**:
```json
{
  "arn:aws:connect:us-east-1:123456789012:phone-number/phone-12345678": "arn:aws:connect:us-east-1:123456789012:phone-number/phone-87654321"  // WRONG - These are ARNs
}
```

**10-Digit Numbers**:
```json
{
  "8005550101": "8005550102"  // WRONG - These are just numbers
}
```

### ✅ DO Use Phone Number IDs (Whatever AWS Returns):

```json
{
  "phone-12345678-1234-1234-1234-123456789012": "phone-87654321-4321-4321-4321-210987654321",  // Format 1
  "11111111-2222-3333-4444-555555555555": "22222222-3333-4444-5555-666666666666",              // Format 2  
  "abcd1234-ef56-7890-ghij-klmnopqrstuv": "wxyz9876-5432-10fe-dcba-zyxwvutsrqpo"               // Format 3
}
```

## Tips

1. **Use Phone Number IDs**: Always use IDs starting with `phone-` followed by UUID format
2. **Start Simple**: Create a basic JSON file with just the mappings you need
3. **Test First**: Always use `--dry-run` to test your mapping file
4. **One-to-One**: Each source phone ID should map to exactly one target phone ID
5. **Case Sensitive**: Phone number IDs are case-sensitive
6. **Keep Backups**: Save your mapping files for future use

This approach is much simpler than running the mapper utility - just create a JSON file with your mappings and use it directly!

## Contributing

Found an issue or want to improve this guide? Please contribute:
- Report issues on GitHub
- Submit pull requests with improvements
- Share your migration experiences and tips