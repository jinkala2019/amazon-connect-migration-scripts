# Changelog

All notable changes to the Amazon Connect Migration Scripts project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-01-16

### Added
- **Security Profile Helper**
  - `security_profile_helper.py` - Analyze and create missing security profiles
  - Cross-region security profile comparison and creation
  - AWS CLI command generation for missing profiles
  - Integration with user import workflow

- **Enhanced Queue Export**
  - Queue name prefix filtering (`--queue-prefix` parameter)
  - Dual filtering: BU tag AND queue name prefix
  - Enhanced logging for filtering results

- **Cross-Region Migration Support**
  - Phone number mapping utilities for cross-region migrations
  - `connect_phone_number_mapper.py` - Create and validate phone number mappings
  - Template generation for phone number ID mappings
  - Enhanced documentation for cross-region workflows

- **Enhanced Example Usage**
  - `example_usage.py` updated with 10 comprehensive examples
  - Cross-region migration workflow examples
  - Security profile analysis and creation examples
  - Queue prefix filtering examples
  - Phone number mapping examples

### Enhanced
- **User Import Script**
  - Automatic security profile analysis during import
  - Enhanced error handling for missing security profiles
  - Cross-region compatibility improvements

- **Documentation**
  - `CROSS_REGION_MIGRATION_GUIDE.md` - Comprehensive cross-region guide
  - Updated all documentation for new features
  - Enhanced troubleshooting sections

## [1.0.0] - 2024-01-15

### Added
- **User Migration Scripts**
  - `connect_user_export.py` - Export users with complete configurations
  - `connect_user_import.py` - Import users with batch processing and resource mapping
  - Support for 10K+ users with pagination and rate limiting
  - Automatic routing profile creation with full configuration
  - Tag preservation for users and routing profiles

- **Quick Connect Migration Scripts**
  - `connect_quick_connect_export.py` - Export all quick connect types
  - `connect_quick_connect_import.py` - Import with resource mapping
  - Support for User, Queue, and Phone Number quick connects
  - Complete configuration and tag preservation

- **Queue Migration Scripts with BU Tag Filtering**
  - `connect_queue_export.py` - Export queues filtered by Business Unit tags
  - `connect_queue_import.py` - Import queues with associated quick connects
  - Runtime BU tag parameter with case-insensitive matching
  - Phone number mapping for outbound caller ID configurations

- **Phone Number Mapping System**
  - `connect_phone_number_mapper.py` - Advanced mapping utility
  - Simple JSON file approach for easy phone number mapping
  - Support for multiple phone number ID formats
  - Auto-detection and template generation

- **Performance and Optimization Tools**
  - `performance_tuning.py` - Batch size optimization and benchmarking
  - Configurable batch processing (10-250 items per batch)
  - Memory-efficient processing for large datasets
  - Built-in rate limiting and API throttling prevention

- **Comprehensive Documentation**
  - `README.md` - Main project documentation
  - `QUICK_CONNECT_MIGRATION_GUIDE.md` - Quick connect migration guide
  - `QUEUE_MIGRATION_GUIDE.md` - Queue migration with BU filtering
  - `SIMPLE_PHONE_MAPPING_GUIDE.md` - Easy phone number mapping
  - `PHONE_NUMBER_MAPPING_GUIDE.md` - Advanced phone mapping features
  - `LOG_FORMAT_GUIDE.md` - Logging and troubleshooting guide
  - `MIGRATION_CHECKLIST.md` - Step-by-step migration process
  - `FILE_OVERVIEW.md` - Complete project overview

- **Configuration and Templates**
  - `requirements.txt` - Python dependencies
  - `phone_number_mapping_template.json` - Ready-to-edit template
  - `phone_mapping_example.json` - Real-world examples
  - AWS setup and IAM permission guides

### Features
- **Scalability**: Handle 10K+ resources efficiently
- **Safety**: Dry-run mode for all import operations
- **Reliability**: Comprehensive error handling and recovery
- **Flexibility**: Configurable batch sizes and AWS profiles
- **Completeness**: Full configuration preservation including tags
- **Intelligence**: Smart resource mapping without overwriting existing resources

### Security
- Proper AWS SDK usage with session management
- No hardcoded credentials or sensitive data
- Secure file handling with proper encoding
- Input validation and sanitization

### Performance
- Pagination for large datasets (1000 items per page)
- Memory-efficient processing
- Built-in rate limiting to avoid API throttling
- Configurable batch processing for optimization

## [Unreleased]

### Planned Features
- Contact flow migration support
- Hours of operations migration
- Cross-region migration capabilities
- GUI interface for non-technical users
- Enhanced reporting and progress tracking
- Automated testing framework

---

## Version History

- **v1.0.0** - Initial release with complete migration capabilities
- **Future versions** - Additional AWS Connect resources and enhanced features