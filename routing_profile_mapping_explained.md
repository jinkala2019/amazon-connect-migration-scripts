# Routing Profile Configuration Mapping - Detailed Explanation

## **How Routing Profile Configurations Are Captured & Recreated**

### **Step 1: Export Process - Complete Configuration Capture**

When exporting, the script calls `describe_routing_profile()` for each user's assigned routing profile:

```python
routing_response = self.connect_client.describe_routing_profile(
    InstanceId=self.instance_id,
    RoutingProfileId=user_data['RoutingProfileId']
)
routing_profile = routing_response['RoutingProfile']
```

**This captures ALL routing profile configurations:**

```json
{
  "RoutingProfile": {
    "InstanceId": "source-instance-123",
    "Name": "Sales Agent Profile",
    "Description": "Profile for sales team agents",
    "DefaultOutboundQueueId": "queue-456",
    "QueueConfigs": [
      {
        "QueueReference": {
          "QueueId": "queue-789",
          "Channel": "VOICE"
        },
        "Priority": 1,
        "Delay": 0
      },
      {
        "QueueReference": {
          "QueueId": "queue-101",
          "Channel": "CHAT"
        },
        "Priority": 2,
        "Delay": 30
      }
    ],
    "MediaConcurrencies": [
      {
        "Channel": "VOICE",
        "Concurrency": 1
      },
      {
        "Channel": "CHAT",
        "Concurrency": 3
      },
      {
        "Channel": "TASK",
        "Concurrency": 5
      }
    ],
    "Tags": {
      "Department": "Sales",
      "Region": "US-East"
    }
  }
}
```

### **Step 2: Import Process - Configuration Recreation**

When the routing profile doesn't exist in target, it recreates using the exported configuration:

```python
create_params = {
    'InstanceId': self.instance_id,
    'Name': routing_profile['Name'],                    # "Sales Agent Profile"
    'Description': routing_profile.get('Description', ''), # "Profile for sales team agents"
    'DefaultOutboundQueueId': routing_profile['DefaultOutboundQueueId'], # queue-456
    'MediaConcurrencies': routing_profile['MediaConcurrencies'] # Full concurrency config
}

# Add queue configurations if they exist
if routing_profile.get('QueueConfigs'):
    create_params['QueueConfigs'] = routing_profile['QueueConfigs'] # All queue mappings
```

## **What Gets Recreated vs What Doesn't**

### **✅ RECREATED (Exact Copy)**
- **Name**: "Sales Agent Profile"
- **Description**: "Profile for sales team agents"  
- **Media Concurrencies**: Voice=1, Chat=3, Task=5
- **Queue Configurations**: All queue priorities and delays
- **Default Outbound Queue**: Reference to default queue

### **⚠️ POTENTIAL ISSUES**
- **Queue IDs**: Source queue IDs may not exist in target instance
- **Default Outbound Queue**: May reference non-existent queue
- **Tags**: May not be recreated (depends on API version)

### **❌ NOT HANDLED AUTOMATICALLY**
- **Queue Creation**: If queues don't exist in target, routing profile creation fails
- **Queue Mapping**: No automatic mapping of queue names between instances

## **Real-World Example**

### **Source Instance Export:**
```json
{
  "User": {
    "Username": "john.doe",
    "RoutingProfileId": "rp-source-123"
  },
  "RoutingProfile": {
    "Name": "Customer Service Agent",
    "Description": "Handles customer inquiries",
    "DefaultOutboundQueueId": "queue-outbound-456",
    "QueueConfigs": [
      {
        "QueueReference": {"QueueId": "queue-general-789", "Channel": "VOICE"},
        "Priority": 1,
        "Delay": 0
      },
      {
        "QueueReference": {"QueueId": "queue-support-101", "Channel": "CHAT"},
        "Priority": 2,
        "Delay": 15
      }
    ],
    "MediaConcurrencies": [
      {"Channel": "VOICE", "Concurrency": 1},
      {"Channel": "CHAT", "Concurrency": 2}
    ]
  }
}
```

### **Target Instance Creation:**
```python
# Script attempts to create with EXACT same configuration
create_routing_profile(
    Name="Customer Service Agent",
    Description="Handles customer inquiries",
    DefaultOutboundQueueId="queue-outbound-456",  # ⚠️ Must exist in target
    QueueConfigs=[
        {
            "QueueReference": {"QueueId": "queue-general-789", "Channel": "VOICE"}, # ⚠️ Must exist
            "Priority": 1,
            "Delay": 0
        }
    ],
    MediaConcurrencies=[
        {"Channel": "VOICE", "Concurrency": 1},
        {"Channel": "CHAT", "Concurrency": 2}
    ]
)
```

## **Common Issues & Solutions**

### **Issue 1: Queue IDs Don't Exist in Target**
```
Error: InvalidParameterException - Queue queue-general-789 not found
```

**Solution**: Pre-create queues or modify script to map queue names

### **Issue 2: Default Outbound Queue Missing**
```
Error: InvalidParameterException - DefaultOutboundQueueId queue-outbound-456 not found
```

**Solution**: Ensure basic queues exist in target instance first

### **Issue 3: Partial Recreation**
If queue creation fails, the routing profile creation fails entirely.

**Solution**: The script falls back to warning and skips the user:
```python
except Exception as e:
    logger.error(f"Failed to create routing profile {routing_profile_name}: {e}")
    # User creation will be skipped
```

## **Best Practices**

1. **Pre-Migration Setup**: Ensure basic queues exist in target instance
2. **Queue Mapping**: Consider creating a queue mapping strategy
3. **Validation**: Always run dry-run first to identify missing dependencies
4. **Fallback Strategy**: Have default routing profiles ready in target instance

## **Summary**

**Yes, the script captures and recreates ALL routing profile configurations from the source system**, including:
- Media concurrency settings
- Queue configurations and priorities
- Default outbound queue settings
- Descriptions and metadata

**However**, it requires that referenced queues already exist in the target instance, or the creation will fail.