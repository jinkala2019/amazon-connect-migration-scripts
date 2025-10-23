# Cross-Region Migration Guide for Amazon Connect

## Overview

This guide covers migrating Amazon Connect resources between different AWS regions, with special focus on handling security profiles and other region-specific configurations.

## Why Cross-Region Migration?

Common scenarios for cross-region migration:
- **Disaster Recovery**: Setting up backup instances in different regions
- **Global Expansion**: Expanding operations to new geographic regions
- **Compliance Requirements**: Moving to regions with specific data residency requirements
- **Performance Optimization**: Moving closer to user base for better latency

## Key Challenges in Cross-Region Migration

### 1. Security Profiles
- **Issue**: Security profiles are region-specific and don't automatically exist in target regions
- **Solution**: Use the Security Profile Helper to analyze and create missing profiles

### 2. Resource IDs
- **Issue**: All AWS resource IDs are region-specific (users, queues, routing profiles, etc.)
- **Solution**: Scripts handle ID mapping automatically using resource names

### 3. Phone Numbers
- **Issue**: Phone numbers may not be available in target regions
- **Solution**: Use phone number mapping for queue outbound caller configurations

### 4. Hours of Operations
- **Issue**: Basic hours of operations may not exist in new instances
- **Solution**: Create basic 24/7 hours of operations in target instance first

## Step-by-Step Cross-Region Migration

### Phase 1: Pre-Migration Setup

#### 1. Verify Target Instance Access
```bash
# Test connection to target region
aws connect list-users --instance-id target-instance-id --region target-region --max-items 1
```

#### 2. Create Basic Resources in Target Instance
```bash
# Create basic hours of operations (24/7)
aws connect create-hours-of-operation \
  --instance-id target-instance-id \
  --name "24x7" \
  --description "24 hours, 7 days a week" \
  --time-zone "UTC" \
  --config "Day=MONDAY,StartTime={Hours=0,Minutes=0},EndTime={Hours=23,Minutes=59}" \
  --region target-region

# Repeat for other days or use AWS Console to create basic hours
```

### Phase 2: User Migration

#### 1. Export Users from Source Region
```bash
python connect_user_export.py \
  --instance-id source-instance-id \
  --region source-region \
  --output users_export_source_region.json
```

#### 2. Analyze Security Profile Requirements
```bash
python security_profile_helper.py \
  --action compare \
  --export-file users_export_source_region.json \
  --target-instance target-instance-id \
  --region target-region
```

**Example Output:**
```
INFO - Profile Comparison Results:
INFO -   Required: 8
INFO -   Available in target: 3
INFO -   Missing from target: 5
WARNING - Missing security profiles:
WARNING -   - 'Agent' (needed by 250 users)
WARNING -   - 'Supervisor' (needed by 15 users)
WARNING -   - 'CallCenterManager' (needed by 5 users)
WARNING -   - 'QualityAnalyst' (needed by 10 users)
WARNING -   - 'TeamLead' (needed by 20 users)
```

#### 3. Create Missing Security Profiles
```bash
# Generate creation script
python security_profile_helper.py \
  --action create-script \
  --export-file users_export_source_region.json \
  --target-instance target-instance-id \
  --region target-region \
  --output create_security_profiles_target_region.sh

# Execute the script
chmod +x create_security_profiles_target_region.sh
./create_security_profiles_target_region.sh
```

#### 4. Import Users with Dry Run
```bash
python connect_user_import.py \
  --instance-id target-instance-id \
  --region target-region \
  --export-file users_export_source_region.json \
  --dry-run \
  --batch-size 25
```

#### 5. Execute Actual Import
```bash
python connect_user_import.py \
  --instance-id target-instance-id \
  --region target-region \
  --export-file users_export_source_region.json \
  --batch-size 25
```

### Phase 3: Queue Migration

#### 1. Export Queues from Source Region
```bash
# Export all queues for a specific BU
python connect_queue_export.py \
  --instance-id source-instance-id \
  --region source-region \
  --bu-tag "Sales" \
  --output queues_export_sales_source_region.json

# Export specific queue types
python connect_queue_export.py \
  --instance-id source-instance-id \
  --region source-region \
  --bu-tag "Sales" \
  --queue-prefix "Q_QC_" \
  --output qc_queues_export_sales_source_region.json
```

#### 2. Handle Phone Number Mapping (if needed)
```bash
# Create phone number mapping for outbound caller ID
python connect_phone_number_mapper.py \
  --action template \
  --source-instance source-instance-id \
  --target-instance target-instance-id \
  --region target-region

# Edit the generated template and create clean mapping
python connect_phone_number_mapper.py \
  --action extract \
  --mapping-file phone_number_mapping_template.json \
  --output phone_mappings_clean.json
```

#### 3. Import Queues
```bash
# Import with phone number mapping
python connect_queue_import.py \
  --instance-id target-instance-id \
  --region target-region \
  --export-file queues_export_sales_source_region.json \
  --phone-mapping phone_mappings_clean.json \
  --dry-run

# Execute actual import
python connect_queue_import.py \
  --instance-id target-instance-id \
  --region target-region \
  --export-file queues_export_sales_source_region.json \
  --phone-mapping phone_mappings_clean.json
```

### Phase 4: Quick Connect Migration

#### 1. Export Quick Connects
```bash
python connect_quick_connect_export.py \
  --instance-id source-instance-id \
  --region source-region \
  --output quick_connects_export_source_region.json
```

#### 2. Import Quick Connects
```bash
python connect_quick_connect_import.py \
  --instance-id target-instance-id \
  --region target-region \
  --export-file quick_connects_export_source_region.json \
  --dry-run

python connect_quick_connect_import.py \
  --instance-id target-instance-id \
  --region target-region \
  --export-file quick_connects_export_source_region.json
```

## Common Cross-Region Issues and Solutions

### Issue 1: Security Profile Creation Fails
**Error**: `InvalidParameterException: Invalid permissions`

**Solution**: 
```bash
# Create with basic permissions first, then configure in AWS Console
aws connect create-security-profile \
  --instance-id target-instance-id \
  --security-profile-name "Agent" \
  --description "Basic agent profile" \
  --region target-region
```

### Issue 2: Phone Numbers Not Available
**Error**: `Phone number not found in target instance`

**Solution**:
- Purchase equivalent phone numbers in target region
- Update phone number mapping file
- Or remove phone number configuration from queues

### Issue 3: Hours of Operations Missing
**Error**: `Hours of operation not found`

**Solution**:
```bash
# Create basic 24/7 hours of operations
aws connect create-hours-of-operation \
  --instance-id target-instance-id \
  --name "24x7" \
  --description "24 hours, 7 days a week" \
  --time-zone "UTC" \
  --config file://hours-config.json \
  --region target-region
```

### Issue 4: Large Dataset Timeouts
**Error**: Connection timeouts during large imports

**Solution**:
- Reduce batch size: `--batch-size 10`
- Use regional AWS CLI endpoints
- Run from EC2 instance in target region

## Regional Considerations

### AWS Regions with Amazon Connect
- **US East (N. Virginia)**: us-east-1
- **US West (Oregon)**: us-west-2  
- **Europe (Frankfurt)**: eu-central-1
- **Europe (London)**: eu-west-2
- **Asia Pacific (Sydney)**: ap-southeast-2
- **Asia Pacific (Singapore)**: ap-southeast-1
- **Asia Pacific (Tokyo)**: ap-northeast-1

### Region-Specific Features
- Some Connect features may not be available in all regions
- Phone number availability varies by region
- Compliance and data residency requirements differ

## Best Practices for Cross-Region Migration

### 1. Planning Phase
- **Inventory Resources**: Document all resources in source instance
- **Check Feature Availability**: Verify all features are available in target region
- **Plan Phone Numbers**: Identify phone number requirements for target region
- **Test with Subset**: Always test with a small subset of users first

### 2. Execution Phase
- **Use Dry Run**: Always validate with dry-run before actual migration
- **Monitor Progress**: Watch logs for any region-specific issues
- **Batch Processing**: Use smaller batch sizes for cross-region stability
- **Verify Resources**: Check that all resources were created correctly

### 3. Post-Migration Phase
- **Functional Testing**: Test all functionality in target region
- **Performance Testing**: Verify acceptable performance from user locations
- **Update Documentation**: Document any region-specific configurations
- **Monitor Usage**: Watch for any region-specific issues in production

## Complete Cross-Region Migration Example

```bash
# Source: us-east-1, Target: eu-west-1

# 1. Export from us-east-1
python connect_user_export.py --instance-id source-us-east-1 --region us-east-1
python connect_queue_export.py --instance-id source-us-east-1 --region us-east-1 --bu-tag "Sales"
python connect_quick_connect_export.py --instance-id source-us-east-1 --region us-east-1

# 2. Analyze and create security profiles for eu-west-1
python security_profile_helper.py --action create-script --export-file users_export.json --target-instance target-eu-west-1 --region eu-west-1
./create_security_profiles_*.sh

# 3. Import to eu-west-1
python connect_user_import.py --instance-id target-eu-west-1 --region eu-west-1 --export-file users_export.json --dry-run
python connect_user_import.py --instance-id target-eu-west-1 --region eu-west-1 --export-file users_export.json

python connect_queue_import.py --instance-id target-eu-west-1 --region eu-west-1 --export-file queues_export.json --dry-run
python connect_queue_import.py --instance-id target-eu-west-1 --region eu-west-1 --export-file queues_export.json

python connect_quick_connect_import.py --instance-id target-eu-west-1 --region eu-west-1 --export-file quick_connects_export.json --skip-mapping --dry-run
python connect_quick_connect_import.py --instance-id target-eu-west-1 --region eu-west-1 --export-file quick_connects_export.json --skip-mapping
```

Cross-region migration is fully supported and reliable when following this systematic approach! 🌍