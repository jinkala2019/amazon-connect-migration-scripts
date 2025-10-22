# Amazon Connect Migration Scripts

This repository contains comprehensive Python scripts for migrating Amazon Connect resources between instances, including users, queues, and quick connects. Designed to handle large datasets (10K+ resources) efficiently with complete configuration preservation.

## Migration Types Supported

### 🧑‍💼 User Migration
- **Complete Profile Export**: All user configurations, routing profiles, security profiles, hierarchy groups
- **Batch Processing**: Handle 10K+ users with configurable batch sizes
- **Smart Resource Mapping**: Maps existing resources by name, creates missing routing profiles

### 📞 Quick Connect Migration  
- **All Quick Connect Types**: User, Queue, and Phone Number quick connects
- **Resource References**: Maintains user and queue references between instances
- **Configuration Preservation**: Complete quick connect settings and tags

### 🏢 Queue Migration with BU Tag Filtering
- **Business Unit Filtering**: Export only queues matching specific BU tag values
- **Associated Quick Connects**: Automatically exports/imports linked quick connects
- **Phone Number Mapping**: Maps outbound caller ID phone numbers between instances

### 🔧 Common Features
- **Tag Preservation**: Maintains all custom tags during migration
- **Dry Run Mode**: Validate imports without making changes
- **Error Handling**: Comprehensive error handling with detailed logging
- **Conflict Resolution**: Handles existing resources without overwriting
- **Performance Optimization**: Built-in rate limiting and memory-efficient processing

## Prerequisites

- Python 3.7+
- AWS CLI configured with appropriate permissions
- Amazon Connect instances with proper IAM permissions

## Required AWS Permissions

Your AWS credentials need the following permissions for all migration types:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "connect:ListUsers",
                "connect:DescribeUser", 
                "connect:CreateUser",
                "connect:ListRoutingProfiles",
                "connect:DescribeRoutingProfile",
                "connect:CreateRoutingProfile",
                "connect:ListSecurityProfiles",
                "connect:DescribeSecurityProfile",
                "connect:ListUserHierarchyGroups",
                "connect:DescribeUserHierarchyGroup",
                "connect:ListQueues",
                "connect:DescribeQueue",
                "connect:CreateQueue",
                "connect:ListQuickConnects",
                "connect:DescribeQuickConnect",
                "connect:CreateQuickConnect",
                "connect:ListQueueQuickConnects",
                "connect:AssociateQueueQuickConnects",
                "connect:ListHoursOfOperations",
                "connect:ListPhoneNumbers",
                "connect:ListTagsForResource"
            ],
            "Resource": "*"
        }
    ]
}
```

## Installation & Setup

### 1. System Requirements
- Python 3.7 or higher
- AWS CLI (optional but recommended)
- Stable internet connection for large migrations

### 2. Clone and Install
```bash
# Clone the repository
git clone https://github.com/your-username/amazon-connect-migration-scripts.git
cd amazon-connect-migration-scripts

# Install Python dependencies
pip install -r requirements.txt

# Install AWS CLI (optional)
pip install awscli
```

### 3. AWS Credentials Setup

Choose one of these methods:

#### Method A: AWS CLI Configuration (Recommended)
```bash
# Configure default profile
aws configure
# Enter: Access Key ID, Secret Access Key, Region (e.g., us-east-1), Output format (json)

# Or configure named profile
aws configure --profile connect-migration
```

#### Method B: Environment Variables
```bash
# Windows Command Prompt
set AWS_ACCESS_KEY_ID=your-access-key
set AWS_SECRET_ACCESS_KEY=your-secret-key
set AWS_DEFAULT_REGION=us-east-1

# Windows PowerShell
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_DEFAULT_REGION="us-east-1"

# Linux/Mac
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

### 4. Test Setup
```bash
# Test AWS connectivity
aws connect list-instances --region us-east-1

# Test script access
python connect_user_export.py --help
```

## Quick Start

### 1. Export Users from Source Instance
```bash
python connect_user_export.py --instance-id source-instance-id --region us-east-1
# Creates: connect_users_export_source-instance-id_YYYYMMDD_HHMMSS.json
```

### 2. Validate Import (Dry Run)
```bash
python connect_user_import.py --instance-id target-instance-id --export-file users_export.json --dry-run
# Shows what would be created/mapped without making changes
```

### 3. Optimize Performance (Optional)
```bash
python performance_tuning.py
# Finds optimal batch size for your environment
```

### 4. Import Users to Target Instance
```bash
python connect_user_import.py --instance-id target-instance-id --export-file users_export.json --batch-size 50
# Creates users with all configurations and tags
```

## Detailed Usage Examples

### Export Users with Custom Settings
```bash
# Export with custom filename and AWS profile
python connect_user_export.py --instance-id source-id --profile prod-profile --output my_users.json

# Export from different region
python connect_user_export.py --instance-id source-id --region eu-west-1
```

### Import Users with Different Batch Sizes
```bash
# Conservative approach for large datasets (10K+ users)
python connect_user_import.py --instance-id target-id --export-file users.json --batch-size 25

# Aggressive approach for faster processing
python connect_user_import.py --instance-id target-id --export-file users.json --batch-size 100

# Very conservative for stability (50K+ users)
python connect_user_import.py --instance-id target-id --export-file users.json --batch-size 10
```

### Command Line Options

#### Export Script (`connect_user_export.py`)
```bash
python connect_user_export.py [OPTIONS]

Required:
  --instance-id TEXT    Source Amazon Connect instance ID

Optional:
  --region TEXT         AWS region (default: us-east-1)
  --profile TEXT        AWS profile name
  --output TEXT         Output file path (auto-generated if not specified)
```

#### Import Script (`connect_user_import.py`)
```bash
python connect_user_import.py [OPTIONS]

Required:
  --instance-id TEXT    Target Amazon Connect instance ID
  --export-file TEXT    Path to the export file

Optional:
  --region TEXT         AWS region (default: us-east-1)
  --profile TEXT        AWS profile name
  --batch-size INTEGER  Users per batch (default: 50, range: 10-250)
  --dry-run            Validate without creating users
```

#### Performance Tuning (`performance_tuning.py`)
```bash
python performance_tuning.py [OPTIONS]

# Automatically benchmarks different batch sizes and recommends optimal settings
```

## Script Functionality

### Export Script (`connect_user_export.py`)

1. **User Discovery**: Uses pagination to retrieve all users from the source instance
2. **Complete Profile Extraction**: For each user, fetches:
   - Basic user information (username, email, phone config)
   - Routing profile configuration
   - Security profile assignments
   - Hierarchy group membership
   - Identity information and tags
3. **Error Handling**: Continues processing even if individual users fail
4. **Output Generation**: Creates a comprehensive JSON file with all user data

### Import Script (`connect_user_import.py`)

1. **Smart Resource Mapping**: Maps existing resources by name (never overwrites existing configurations)
2. **Automatic Resource Creation**: Creates missing routing profiles with complete configurations and tags
3. **Batch Processing**: Configurable batch sizes (10-250 users) with performance optimization
4. **Conflict Resolution**: Handles existing users gracefully without overwriting
5. **Tag Preservation**: Maintains all custom tags during user and routing profile creation
6. **Validation Mode**: Dry-run capability to test imports without making changes
7. **Dependency Checking**: Validates queue and resource dependencies before creation
8. **Progress Tracking**: Real-time progress updates with detailed error reporting

## Export File Structure

The export file contains complete user profiles with all configurations:

```json
{
  "InstanceId": "source-instance-id",
  "ExportTimestamp": "2024-01-01T12:00:00Z",
  "TotalUsers": 10000,
  "SuccessfulExports": 9995,
  "FailedExports": 5,
  "Users": [
    {
      "User": {
        "Username": "john.doe",
        "IdentityInfo": {
          "FirstName": "John",
          "LastName": "Doe",
          "Email": "john.doe@company.com"
        },
        "PhoneConfig": {
          "PhoneType": "SOFT_PHONE",
          "AutoAccept": false
        },
        "RoutingProfileId": "rp-source-123",
        "SecurityProfileIds": ["sp-456", "sp-789"],
        "HierarchyGroupId": "hg-101",
        "Tags": {
          "Department": "Sales",
          "Manager": "jane.smith",
          "CostCenter": "12345"
        }
      },
      "RoutingProfile": {
        "Name": "Sales Agent Profile",
        "Description": "Profile for sales team",
        "MediaConcurrencies": [
          {"Channel": "VOICE", "Concurrency": 1},
          {"Channel": "CHAT", "Concurrency": 3}
        ],
        "QueueConfigs": [...],
        "Tags": {
          "Team": "Sales",
          "Environment": "Production"
        }
      },
      "SecurityProfiles": [
        {
          "SecurityProfileName": "Agent",
          "Permissions": [...],
          "Tags": {...}
        }
      ],
      "HierarchyGroup": {
        "Name": "Sales Team",
        "Tags": {...}
      },
      "ExportTimestamp": "2024-01-01T12:00:00Z"
    }
  ],
  "FailedUsers": [...]
}
```

## Performance Considerations & Batch Size Optimization

### Recommended Batch Sizes by Dataset Size

| Dataset Size | Recommended Batch Size | Description |
|-------------|----------------------|-------------|
| < 1K users | 100 | Fast processing for small datasets |
| 1K-5K users | 50 | Balanced approach (default) |
| 5K-20K users | 25 | Conservative for large datasets |
| > 20K users | 10-15 | Very conservative for stability |

### Performance Features

- **Intelligent Rate Limiting**: Built-in delays to avoid API throttling
- **Configurable Batch Processing**: Optimize batch sizes based on your environment
- **Memory Efficiency**: Processes users incrementally to handle massive datasets
- **Performance Benchmarking**: Built-in tools to find optimal settings
- **Progress Monitoring**: Real-time performance metrics and ETA calculations

### Optimization Commands

```bash
# Test optimal batch size for your environment
python performance_tuning.py

# Conservative approach for 10K+ users
python connect_user_import.py --batch-size 25 --export-file users.json --dry-run

# Aggressive approach for faster processing (good network required)
python connect_user_import.py --batch-size 100 --export-file users.json --dry-run
```

## Error Handling

- **API Errors**: Graceful handling of AWS API errors with retry logic
- **Resource Conflicts**: Handles existing resources and naming conflicts
- **Partial Failures**: Continues processing even when individual operations fail
- **Detailed Logging**: Comprehensive error reporting and progress tracking

## Resource Mapping & Tag Handling

### How Resource Mapping Works

- **Name-Based Mapping**: Resources are mapped by name, not ID
- **No Overwriting**: Existing resources are never modified or overwritten
- **Automatic Creation**: Missing routing profiles are created automatically with full configuration
- **Dependency Validation**: Checks for required queues and resources before creation

### Tag Preservation

| Resource Type | Export | Import | Notes |
|--------------|--------|--------|-------|
| **User Tags** | ✅ Full | ✅ Full | All custom tags preserved |
| **Routing Profile Tags** | ✅ Full | ✅ Full | Tags recreated with new profiles |
| **Security Profile Tags** | ✅ Full | ⚠️ Captured | Not applied (profiles not auto-created) |
| **Hierarchy Group Tags** | ✅ Full | ⚠️ Captured | Not applied (groups not auto-created) |

### Resource Handling Examples

```bash
# Source: User has "Sales Agent" routing profile with custom tags
# Target: "Sales Agent" profile exists → Maps to existing profile
# Target: "Sales Agent" profile missing → Creates new profile with all configurations and tags

# Source: User "john.doe" exists
# Target: User "john.doe" exists → Skips creation, logs warning, continues processing
# Target: User "john.doe" missing → Creates new user with all tags and configurations
```

## Best Practices

1. **Always run dry-run first** to validate the import process and identify issues
2. **Ensure basic queues exist** in target instance before migration
3. **Start with small batch sizes** and optimize based on performance testing
4. **Monitor logs** during large imports for any dependency or mapping issues
5. **Backup target instance** before running imports
6. **Test with a subset** of users before full migration
7. **Use performance tuning script** to find optimal batch size for your environment

## Troubleshooting

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **Queue not found errors** | Routing profiles reference queues that don't exist in target | Pre-create basic queues or modify queue references |
| **API throttling** | Batch size too large or network issues | Reduce batch size, check network stability |
| **Permission denied** | Insufficient IAM permissions | Review and update IAM policy |
| **Routing profile creation fails** | Missing queue dependencies | Ensure referenced queues exist in target instance |
| **Users skipped** | Missing security profiles or routing profiles | Check resource mapping, create missing profiles manually |

### Diagnostic Commands

```bash
# Test AWS connectivity and permissions
aws connect list-instances --region us-east-1

# Validate export file before import
python example_usage.py  # Use validate_export_file_example()

# Test performance and find bottlenecks
python performance_tuning.py

# Run comprehensive dry-run validation
python connect_user_import.py --instance-id target-id --export-file users.json --dry-run --batch-size 10
```

### Log Analysis

- **Export logs**: `connect_export.log` - Shows export progress and any user-specific failures
- **Import logs**: `connect_import.log` - Shows resource mapping, creation attempts, and failures
- **Performance logs**: Check users/second metrics to optimize batch sizes
## C
ontributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute
- 🐛 **Report bugs** or issues you encounter
- 💡 **Suggest features** or improvements  
- 📖 **Improve documentation** with examples or clarifications
- 🔧 **Submit code** for new features or bug fixes
- 🌟 **Share your experience** with migration use cases

### Getting Started
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with dry-run mode
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## Support

- 📚 **Documentation**: Check the comprehensive guides in this repository
- 🐛 **Issues**: Report bugs or request features on GitHub Issues  
- 💬 **Discussions**: Join community discussions on GitHub Discussions
- 📧 **Enterprise Support**: Available for consulting and custom implementations

## Project Status

✅ **Production Ready** - All scripts are tested and ready for enterprise use
🚀 **Active Development** - Regular updates and new features
🤝 **Community Driven** - Open source with community contributions welcome

---

**Made with ❤️ for the Amazon Connect community**