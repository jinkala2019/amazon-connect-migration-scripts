# Phone Number ID Quick Reference

## What You Need for Phone Mapping

### ✅ CORRECT Format - Phone Number IDs (Any of these)
```
phone-12345678-1234-1234-1234-123456789012  (Format 1: with phone- prefix)
12345678-1234-1234-1234-123456789012        (Format 2: UUID only)
abcd1234-ef56-7890-ghij-klmnopqrstuv        (Format 3: other AWS formats)
```

### ❌ WRONG Formats

**Phone Numbers**:
```
+1-800-555-0101
8005550101
1-800-555-0101
```

**ARNs**:
```
arn:aws:connect:us-east-1:123456789012:phone-number/phone-12345678-1234-1234-1234-123456789012
```

## How to Get Phone Number IDs

### AWS Console Method
1. AWS Connect Console → Your Instance → Phone Numbers
2. Click on any phone number
3. Copy the **"Phone number ID"** field
4. Copy whatever ID format AWS shows (varies by region/creation date)

### AWS CLI Method
```bash
aws connect list-phone-numbers --instance-id your-instance-id
```

Look for the `"Id"` field in the response (format varies):
```json
{
  "Id": "phone-12345678-1234-1234-1234-123456789012",  ← Use this (Format 1)
  "PhoneNumber": "+18005550101",                        ← Not this
  "Arn": "arn:aws:connect:..."                         ← Not this
}
```

Or:
```json
{
  "Id": "12345678-1234-1234-1234-123456789012",        ← Use this (Format 2)
  "PhoneNumber": "+18005550101",                        ← Not this
}
```

## Example Mapping File

```json
{
  "phone-12345678-1234-1234-1234-123456789012": "phone-87654321-4321-4321-4321-210987654321",
  "11111111-2222-3333-4444-555555555555": "22222222-3333-4444-5555-666666666666",
  "abcd1234-ef56-7890-ghij-klmnopqrstuv": "wxyz9876-5432-10fe-dcba-zyxwvutsrqpo"
}
```

## Quick Test
Your phone number IDs should:
- ✅ Come from the "Id" field in AWS Connect Console or CLI
- ✅ Be unique identifiers (not phone numbers like +1-800-555-0101)
- ✅ Match one of these patterns:
  - `phone-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (with prefix)
  - `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (UUID format)
  - Other AWS-generated unique identifiers
- ✅ NOT be ARNs or actual phone numbers

**The key is to use whatever AWS returns in the "Id" field - don't assume the format!**