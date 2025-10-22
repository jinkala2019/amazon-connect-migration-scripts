# Amazon Connect User Migration Checklist

## Pre-Migration Setup

### 1. Environment Preparation
- [ ] Python 3.7+ installed
- [ ] AWS CLI configured with appropriate credentials
- [ ] Required IAM permissions configured for both source and target instances
- [ ] Network connectivity to AWS Connect APIs tested
- [ ] Backup of target instance created (if applicable)

### 2. Instance Preparation
- [ ] Source instance ID confirmed and accessible
- [ ] Target instance ID confirmed and accessible
- [ ] Basic queues exist in target instance (General, BasicQueue, etc.)
- [ ] Required security profiles exist in target instance
- [ ] Hierarchy groups exist in target instance (if used)

### 3. Dependencies Installation
```bash
pip install -r requirements.txt
aws configure  # or set environment variables
```

## Migration Process

### Phase 1: Export & Analysis
- [ ] Export users from source instance
```bash
python connect_user_export.py --instance-id source-instance-id --region us-east-1
```
- [ ] Review export file for completeness
- [ ] Check export logs for any failed users
- [ ] Validate export file structure

### Phase 2: Pre-Import Validation
- [ ] Run dry-run import to identify issues
```bash
python connect_user_import.py --instance-id target-instance-id --export-file users_export.json --dry-run
```
- [ ] Review dry-run results for mapping issues
- [ ] Create missing queues in target instance if needed
- [ ] Create missing security profiles manually if needed
- [ ] Resolve any dependency issues identified

### Phase 3: Performance Optimization
- [ ] Run performance benchmarking
```bash
python performance_tuning.py
```
- [ ] Determine optimal batch size for your environment
- [ ] Test with small batch first (10-25 users)
- [ ] Monitor system performance during test

### Phase 4: Production Migration
- [ ] Start with conservative batch size
- [ ] Monitor logs in real-time during migration
- [ ] Track progress and performance metrics
- [ ] Handle any failures or errors promptly
- [ ] Verify user creation in target instance

## Post-Migration Validation

### 1. User Verification
- [ ] Verify total user count matches expected numbers
- [ ] Spot-check user configurations (routing profiles, security profiles)
- [ ] Verify custom tags are preserved
- [ ] Test user login functionality
- [ ] Validate phone configurations

### 2. Resource Verification
- [ ] Confirm routing profiles were created/mapped correctly
- [ ] Verify routing profile configurations (queues, concurrency)
- [ ] Check that routing profile tags are preserved
- [ ] Validate hierarchy group assignments
- [ ] Confirm security profile assignments

### 3. Functionality Testing
- [ ] Test user login to Connect agent interface
- [ ] Verify phone functionality (if applicable)
- [ ] Test queue assignments and routing
- [ ] Validate permissions and access levels
- [ ] Check reporting and analytics data

## Troubleshooting Checklist

### Common Issues
- [ ] **Queue not found errors**: Create missing queues in target instance
- [ ] **API throttling**: Reduce batch size, check network stability
- [ ] **Permission denied**: Review IAM permissions
- [ ] **Users skipped**: Check for missing security profiles or routing profiles
- [ ] **Routing profile creation fails**: Verify queue dependencies

### Performance Issues
- [ ] **Slow processing**: Optimize batch size using performance_tuning.py
- [ ] **Memory issues**: Reduce batch size for very large datasets
- [ ] **Network timeouts**: Check internet connectivity and AWS region proximity

### Validation Issues
- [ ] **Missing users**: Check export logs for failed exports
- [ ] **Incorrect configurations**: Verify resource mapping in target instance
- [ ] **Missing tags**: Confirm tag support in your AWS region/instance version

## Rollback Plan

### If Migration Fails
- [ ] Stop import process immediately
- [ ] Review error logs to identify root cause
- [ ] Document failed users for manual processing
- [ ] Consider partial rollback if users were partially created
- [ ] Plan remediation strategy for next attempt

### Data Integrity
- [ ] Maintain export file as backup
- [ ] Keep detailed logs of all operations
- [ ] Document any manual changes made during migration
- [ ] Prepare for potential re-migration if needed

## Success Criteria

### Migration Complete When:
- [ ] All users successfully created or mapped
- [ ] All routing profiles created/mapped with correct configurations
- [ ] All custom tags preserved and applied
- [ ] No critical errors in migration logs
- [ ] User functionality validated in target instance
- [ ] Performance meets expected benchmarks

### Documentation Complete When:
- [ ] Migration summary report created
- [ ] Failed users documented (if any)
- [ ] Performance metrics recorded
- [ ] Lessons learned documented for future migrations
- [ ] Handover documentation provided to operations team

## Batch Size Recommendations

| Dataset Size | Recommended Batch Size | Expected Duration (estimate) |
|-------------|----------------------|----------------------------|
| < 1K users | 100 | 10-30 minutes |
| 1K-5K users | 50 | 1-3 hours |
| 5K-20K users | 25 | 3-8 hours |
| > 20K users | 10-15 | 8+ hours |

*Duration estimates depend on network speed, AWS region, and resource complexity*