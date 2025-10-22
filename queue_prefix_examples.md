# Queue Prefix Filtering Examples

## Overview

The enhanced queue export script now supports filtering by both BU tag AND queue name prefix, giving you precise control over which queues to export.

## Real-World Scenarios

### Scenario 1: QC (Quality Control) Queues Only

**Requirement**: Export only Quality Control queues for the Sales BU

```bash
# Export queues that:
# 1. Have BU tag = "Sales" 
# 2. Queue name starts with "Q_QC_"
python connect_queue_export.py --instance-id abc123 --bu-tag "Sales" --queue-prefix "Q_QC_"
```

**Queues in Instance**:
- `Q_QC_Sales_General` (BU=Sales) → ✅ **Exported** (matches both filters)
- `Q_QC_Sales_Priority` (BU=Sales) → ✅ **Exported** (matches both filters)
- `Sales_General` (BU=Sales) → ❌ **Skipped** (no Q_QC_ prefix)
- `Q_QC_Support_General` (BU=Support) → ❌ **Skipped** (wrong BU tag)
- `Marketing_Queue` (BU=Marketing) → ❌ **Skipped** (wrong BU and no prefix)

**Result**: Only 2 queues exported

### Scenario 2: Department-Specific Queues

**Requirement**: Export all Sales department queues (not QC)

```bash
# Export queues that:
# 1. Have BU tag = "Sales"
# 2. Queue name starts with "SALES_"
python connect_queue_export.py --instance-id abc123 --bu-tag "Sales" --queue-prefix "SALES_"
```

**Queues in Instance**:
- `SALES_General` (BU=Sales) → ✅ **Exported**
- `SALES_VIP` (BU=Sales) → ✅ **Exported**
- `SALES_Escalation` (BU=Sales) → ✅ **Exported**
- `Q_QC_Sales_General` (BU=Sales) → ❌ **Skipped** (wrong prefix)
- `Support_General` (BU=Support) → ❌ **Skipped** (wrong BU)

**Result**: Only SALES_ prefixed queues exported

### Scenario 3: All Queues for a BU (No Prefix Filter)

**Requirement**: Export ALL queues for Sales BU regardless of name

```bash
# Export queues that:
# 1. Have BU tag = "Sales"
# 2. Any queue name (no prefix filter)
python connect_queue_export.py --instance-id abc123 --bu-tag "Sales"
```

**Queues in Instance**:
- `Q_QC_Sales_General` (BU=Sales) → ✅ **Exported**
- `SALES_General` (BU=Sales) → ✅ **Exported**
- `Sales_VIP` (BU=Sales) → ✅ **Exported**
- `Custom_Sales_Queue` (BU=Sales) → ✅ **Exported**
- `Support_General` (BU=Support) → ❌ **Skipped** (wrong BU)

**Result**: All Sales BU queues exported regardless of name

## Advanced Examples

### Multiple Prefix Exports

```bash
# Export QC queues for Sales
python connect_queue_export.py --instance-id abc123 --bu-tag "Sales" --queue-prefix "Q_QC_" --output sales_qc_queues.json

# Export regular Sales queues  
python connect_queue_export.py --instance-id abc123 --bu-tag "Sales" --queue-prefix "SALES_" --output sales_regular_queues.json

# Export Support QC queues
python connect_queue_export.py --instance-id abc123 --bu-tag "Support" --queue-prefix "Q_QC_" --output support_qc_queues.json
```

### Filename Generation

The script automatically generates descriptive filenames:

```bash
# Without prefix
--bu-tag "Sales"
# Creates: connect_queues_export_abc123_Sales_20240115_143025.json

# With prefix "Q_QC_"  
--bu-tag "Sales" --queue-prefix "Q_QC_"
# Creates: connect_queues_export_abc123_Sales_QQC_20240115_143025.json

# With prefix "SALES_"
--bu-tag "Sales" --queue-prefix "SALES_"  
# Creates: connect_queues_export_abc123_Sales_SALES_20240115_143025.json
```

## Log Output Examples

### With Prefix Filter
```
2024-01-15 14:30:25,123 - INFO - Initialized queue exporter for instance: abc123, BU: Sales, Queue prefix: Q_QC_ in region: us-east-1
2024-01-15 14:30:26,456 - INFO - Starting queue export process for BU tag: Sales, Queue prefix: Q_QC_...
2024-01-15 14:30:27,789 - INFO - Queue matches BU tag 'Sales' and prefix 'Q_QC_': Q_QC_Sales_General
2024-01-15 14:30:28,012 - INFO - Queue matches BU tag 'Sales' and prefix 'Q_QC_': Q_QC_Sales_Priority
2024-01-15 14:30:29,234 - INFO - Found 2 queues matching BU tag 'Sales' and prefix 'Q_QC_'
```

### Without Prefix Filter
```
2024-01-15 14:30:25,123 - INFO - Initialized queue exporter for instance: abc123, BU: Sales (all queues) in region: us-east-1
2024-01-15 14:30:26,456 - INFO - Starting queue export process for BU tag: Sales (all queues)...
2024-01-15 14:30:27,789 - INFO - Queue matches BU tag 'Sales': Q_QC_Sales_General
2024-01-15 14:30:28,012 - INFO - Queue matches BU tag 'Sales': SALES_General
2024-01-15 14:30:29,234 - INFO - Found 15 queues matching BU tag 'Sales'
```

## Best Practices

### 1. Use Descriptive Prefixes
```bash
# Good prefixes
--queue-prefix "Q_QC_"      # Quality Control queues
--queue-prefix "SALES_"     # Sales department queues  
--queue-prefix "SUP_"       # Support queues
--queue-prefix "VIP_"       # VIP customer queues

# Avoid generic prefixes
--queue-prefix "Q_"         # Too broad
--queue-prefix "A"          # Too generic
```

### 2. Test with Dry Run First
```bash
# Always test filtering logic first
python connect_queue_import.py --instance-id target-id --export-file queues_export.json --dry-run
```

### 3. Combine with Custom Output Names
```bash
# Use descriptive output filenames
python connect_queue_export.py --instance-id abc123 --bu-tag "Sales" --queue-prefix "Q_QC_" --output sales_qc_queues_$(date +%Y%m%d).json
```

This enhancement gives you precise control over queue selection, making migrations more targeted and efficient!