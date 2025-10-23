# Amazon Connect User Migration - File Overview

## Core Migration Scripts

### User Migration
#### `connect_user_export.py` - **User Export Script**
- **Purpose**: Exports all users with complete configurations from source Amazon Connect instance
- **Features**: 
  - Handles 10K+ users with pagination
  - Captures all user data, routing profiles, security profiles, hierarchy groups
  - Preserves all custom tags
  - Comprehensive error handling and logging
- **Usage**: `python connect_user_export.py --instance-id source-id`

#### `connect_user_import.py` - **User Import Script**
- **Purpose**: Imports users into target Amazon Connect instance with smart resource mapping
- **Features**:
  - Maps existing resources by name (no overwriting)
  - Creates missing routing profiles automatically with full configuration
  - Preserves all user and routing profile tags
  - Configurable batch processing (10-250 users per batch)
  - Dry-run mode for validation
  - Handles existing users gracefully
- **Usage**: `python connect_user_import.py --instance-id target-id --export-file users.json`

### Quick Connect Migration
#### `connect_quick_connect_export.py` - **Quick Connect Export Script**
- **Purpose**: Exports all quick connects with complete configurations
- **Features**:
  - Captures all quick connect types (User, Queue, Phone Number)
  - Preserves all custom tags
  - Handles resource references and configurations
- **Usage**: `python connect_quick_connect_export.py --instance-id source-id`

#### `connect_quick_connect_import.py` - **Quick Connect Import Script**
- **Purpose**: Imports quick connects into target instance
- **Features**:
  - Resource mapping between instances (optional)
  - Cross-region optimization with `--skip-mapping` flag
  - Conflict resolution for existing quick connects
  - Tag preservation during import
  - ✅ **Enhanced**: Fixed 'Name' field access errors and improved data validation
- **Usage**: 
  - Same-region: `python connect_quick_connect_import.py --instance-id target-id --export-file qc_export.json`
  - Cross-region: `python connect_quick_connect_import.py --instance-id target-id --export-file qc_export.json --skip-mapping`

### Queue Migration with BU Tag Filtering
#### `connect_queue_export.py` - **Queue Export Script with BU Filtering**
- **Purpose**: Exports queues filtered by Business Unit (BU) tag values
- **Features**:
  - Runtime BU tag parameter filtering
  - Case-insensitive BU tag matching
  - Exports associated quick connects automatically
  - Complete queue configuration preservation
  - ✅ **Enhanced**: Fixed ARN tagging errors and improved queue prefix filtering
- **Usage**: `python connect_queue_export.py --instance-id source-id --bu-tag "Sales" --queue-prefix "Q_QC_"`

#### `connect_queue_import.py` - **Queue Import Script**
- **Purpose**: Imports queues with associated quick connects
- **Features**:
  - Automatic quick connect creation for missing resources
  - Hours of operation mapping
  - Complete configuration restoration including tags
  - ✅ **Enhanced**: Fixed quick connect name access errors and improved error handling
- **Usage**: `python connect_queue_import.py --instance-id target-id --export-file queues_export.json`

## Helper & Optimization Scripts

### `performance_tuning.py` - **Performance Optimization Tool**
- **Purpose**: Benchmarks different batch sizes to find optimal performance settings
- **Features**:
  - Tests multiple batch sizes automatically
  - Measures users processed per second
  - Provides recommendations based on dataset size
  - Memory usage monitoring
- **Usage**: `python performance_tuning.py`

### `example_usage.py` - **Programming Examples**
- **Purpose**: Shows how to use the migration scripts programmatically in Python code
- **Features**:
  - Complete migration workflow examples (same-region and cross-region)
  - Export/import only examples
  - Validation and performance optimization examples
  - Tag preservation demonstrations
  - Security profile analysis and creation examples
  - Queue export with prefix filtering examples
  - Phone number mapping for cross-region migrations
- **Usage**: Modify configuration and uncomment desired examples (10 total examples)

## Documentation & Guides

### `README.md` - **Main Documentation**
- **Purpose**: Comprehensive guide for using the migration scripts
- **Contents**:
  - Installation and setup instructions
  - Usage examples and command-line options
  - Performance recommendations and batch size optimization
  - Resource mapping and tag handling explanations
  - Troubleshooting guide

### `MIGRATION_CHECKLIST.md` - **Step-by-Step Migration Guide**
- **Purpose**: Detailed checklist for planning and executing migrations
- **Contents**:
  - Pre-migration setup and validation steps
  - Phase-by-phase migration process
  - Post-migration validation procedures
  - Troubleshooting and rollback plans
  - Success criteria and documentation requirements

### `QUICK_CONNECT_MIGRATION_GUIDE.md` - **Quick Connect Migration Guide**
- **Purpose**: Comprehensive guide for migrating Quick Connects between instances
- **Contents**:
  - Export/import process for quick connects
  - Resource mapping and configuration preservation
  - Tag handling and conflict resolution
  - Troubleshooting and best practices

### `QUEUE_MIGRATION_GUIDE.md` - **Queue Migration Guide with BU Tag Filtering**
- **Purpose**: Advanced queue migration with Business Unit tag-based filtering
- **Contents**:
  - BU tag filtering logic and examples
  - Queue export/import with associated quick connects
  - Multi-BU migration strategies
  - Complete configuration preservation

### `aws_setup_guide.md` - **AWS Configuration Guide**
- **Purpose**: Detailed instructions for setting up AWS credentials and permissions
- **Contents**:
  - Multiple credential configuration methods
  - Required IAM permissions
  - Usage examples with different credential setups

### `LOG_FORMAT_GUIDE.md` - **Logging Details**
- **Purpose**: Comprehensive guide to log file formats and analysis
- **Contents**:
  - Log file locations for all scripts
  - Log format structure and examples
  - Success/failure/warning message formats
  - Log analysis commands and troubleshooting tips

### `SIMPLE_PHONE_MAPPING_GUIDE.md` - **Simple Phone Number Mapping**
- **Purpose**: Easy 3-step process for phone number mapping during queue migration
- **Contents**:
  - Simple JSON file creation for phone mappings
  - How to find phone number IDs in AWS Console
  - Real-world examples and quick commands
  - No complex utilities required

### `PHONE_NUMBER_MAPPING_GUIDE.md` - **Advanced Phone Number Mapping**
- **Purpose**: Comprehensive phone number mapping with utilities and automation
- **Contents**:
  - Phone number mapper utility usage
  - Template generation and validation
  - Multiple mapping strategies and troubleshooting

## Analysis & Reference Documents

### `routing_profile_mapping_explained.md` - **Technical Deep Dive**
- **Purpose**: Detailed explanation of how routing profile configurations are captured and recreated
- **Contents**:
  - Step-by-step export and import process
  - Complete configuration examples
  - Common issues and solutions
  - Best practices for queue dependencies

### `tag_handling_analysis.py` - **Tag Support Analysis**
- **Purpose**: Technical analysis of tag handling capabilities
- **Contents**:
  - Breakdown of tag support by resource type
  - Current implementation details
  - Missing functionality identification

### `security_profile_helper.py` - **Security Profile Management Tool**
- **Purpose**: Analyze and create missing security profiles for cross-region migrations
- **Features**:
  - Analyze export files to identify required security profiles
  - Compare with target instance to find missing profiles
  - Generate AWS CLI scripts to create missing profiles
  - Support for cross-region migration scenarios
- **Usage**: `python security_profile_helper.py --action compare --export-file users.json --target-instance target-id`

### `FILE_OVERVIEW.md` - **This Document**
- **Purpose**: Overview of all files in the project and their purposes

## Configuration Files

### `requirements.txt` - **Python Dependencies**
- **Purpose**: Lists all required Python packages
- **Contents**:
  - boto3 (AWS SDK)
  - botocore (AWS core library)
  - psutil (system monitoring for performance tuning)

## Usage Workflow

### For First-Time Users:
1. Read `README.md` for overview
2. Follow `aws_setup_guide.md` for credential setup
3. Use `MIGRATION_CHECKLIST.md` for step-by-step process
4. Start with `example_usage.py` for learning

### For Large Migrations (10K+ users):
1. Use `performance_tuning.py` to optimize batch sizes
2. Follow `MIGRATION_CHECKLIST.md` for systematic approach
3. Reference `routing_profile_mapping_explained.md` for troubleshooting

### For Quick Connect Migration:
1. Read `QUICK_CONNECT_MIGRATION_GUIDE.md` for complete process
2. Understand resource mapping requirements
3. Test with dry-run before actual migration

### For Queue Migration with BU Filtering:
1. Read `QUEUE_MIGRATION_GUIDE.md` for BU tag filtering
2. Plan multi-BU migration strategy
3. Ensure hours of operations exist in target instance

### For Developers:
1. Study `example_usage.py` for programmatic usage
2. Reference `tag_handling_analysis.py` for technical details
3. Use core scripts as building blocks for custom solutions
4. Check `LOG_FORMAT_GUIDE.md` for log analysis and monitoring

## File Dependencies

```
Core Migration Scripts (Independent):
├── connect_user_export.py
├── connect_user_import.py
├── connect_quick_connect_export.py
├── connect_quick_connect_import.py
├── connect_queue_export.py
├── connect_queue_import.py
└── requirements.txt

Helper Scripts (Use Core Scripts):
├── performance_tuning.py → imports connect_user_import.py
├── example_usage.py → imports user migration scripts
├── security_profile_helper.py → standalone security profile management
└── tag_handling_analysis.py → analysis only, no imports

Documentation (Reference Only):
├── README.md
├── MIGRATION_CHECKLIST.md
├── QUICK_CONNECT_MIGRATION_GUIDE.md
├── QUEUE_MIGRATION_GUIDE.md
├── aws_setup_guide.md
├── LOG_FORMAT_GUIDE.md
├── routing_profile_mapping_explained.md
└── FILE_OVERVIEW.md
```

## Quick Start Commands

### Initial Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure AWS credentials
aws configure
```

### User Migration
```bash
# 3. Export users
python connect_user_export.py --instance-id source-instance-id

# 4. Check security profiles (for cross-region migrations)
python security_profile_helper.py --action compare --export-file users_export.json --target-instance target-instance-id

# 5. Create missing security profiles if needed
python security_profile_helper.py --action create-script --export-file users_export.json --target-instance target-instance-id
./create_security_profiles_*.sh

# 6. Validate user import (dry run)
python connect_user_import.py --instance-id target-instance-id --export-file users_export.json --dry-run

# 7. Optimize performance (optional)
python performance_tuning.py

# 8. Import users
python connect_user_import.py --instance-id target-instance-id --export-file users_export.json --batch-size 50
```

### Quick Connect Migration
```bash
# 7. Export quick connects
python connect_quick_connect_export.py --instance-id source-instance-id

# 8. Validate quick connect import (dry run)
python connect_quick_connect_import.py --instance-id target-instance-id --export-file quick_connects_export.json --dry-run

# 9. Import quick connects
python connect_quick_connect_import.py --instance-id target-instance-id --export-file quick_connects_export.json
```

### Queue Migration with BU Tag Filtering
```bash
# 10. Export queues by BU tag
python connect_queue_export.py --instance-id source-instance-id --bu-tag "Sales"

# 11. Create simple phone number mapping file (optional)
# Edit phone_mapping_example.json with your phone number IDs

# 12. Validate queue import (dry run)
python connect_queue_import.py --instance-id target-instance-id --export-file queues_export.json --dry-run

# 13. Import queues with phone number mapping
python connect_queue_import.py --instance-id target-instance-id --export-file queues_export.json --phone-mapping my_phone_mappings.json
```

### Complete Migration Workflow Example
```bash
# Full migration sequence for a specific BU
python connect_user_export.py --instance-id source-id
python connect_quick_connect_export.py --instance-id source-id
python connect_queue_export.py --instance-id source-id --bu-tag "Sales"

# Validate all imports
python connect_user_import.py --instance-id target-id --export-file users_export.json --dry-run
python connect_quick_connect_import.py --instance-id target-id --export-file quick_connects_export.json --dry-run
python connect_queue_import.py --instance-id target-id --export-file queues_export.json --dry-run

# Execute imports
python connect_user_import.py --instance-id target-id --export-file users_export.json
python connect_quick_connect_import.py --instance-id target-id --export-file quick_connects_export.json
python connect_queue_import.py --instance-id target-id --export-file queues_export.json
```