# Setting Up Credentials for Gram-Vani

This guide explains how to configure API credentials for both local development and Streamlit Cloud deployment.

## Required Credentials

### 1. Bhashini ULCA API (Required for STT/TTS)
- **BHASHINI_API_KEY**: Your Bhashini API key
- **BHASHINI_USER_ID**: Your Bhashini user ID

### 2. AWS Credentials (Required for Bedrock/Answer Generation)
- **AWS_ACCESS_KEY_ID**: Your AWS access key
- **AWS_SECRET_ACCESS_KEY**: Your AWS secret key
- **AWS_REGION**: AWS region (default: us-east-1)

## Setup Methods

### Method 1: Local Development (Using .env file)

1. **Create a `.env` file** in the project root:
```bash
# .env file
BHASHINI_API_KEY=your-bhashini-api-key-here
BHASHINI_USER_ID=your-bhashini-user-id-here

AWS_ACCESS_KEY_ID=your-aws-access-key-here
AWS_SECRET_ACCESS_KEY=your-aws-secret-key-here
AWS_REGION=us-east-1
```

2. **Install python-dotenv** (if not already installed):
```bash
pip install python-dotenv
```

3. **Load environment variables** (add to your script):
```python
from dotenv import load_dotenv
load_dotenv()
```

### Method 2: Local Development (Using Environment Variables)

**Windows PowerShell:**
```powershell
$env:BHASHINI_API_KEY="your-api-key"
$env:BHASHINI_USER_ID="your-user-id"
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_REGION="us-east-1"
```

**Linux/Mac:**
```bash
export BHASHINI_API_KEY="your-api-key"
export BHASHINI_USER_ID="your-user-id"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

### Method 3: Streamlit Cloud Deployment

1. **Go to your Streamlit Cloud dashboard**
2. **Click on your app** → "Settings" → "Secrets"
3. **Add secrets in TOML format**:

```toml
# Bhashini ULCA API Credentials
BHASHINI_API_KEY = "your-bhashini-api-key-here"
BHASHINI_USER_ID = "your-bhashini-user-id-here"

# AWS Credentials
AWS_ACCESS_KEY_ID = "your-aws-access-key-here"
AWS_SECRET_ACCESS_KEY = "your-aws-secret-key-here"
AWS_REGION = "us-east-1"
```

4. **Save** and the app will automatically restart with new credentials

## Getting API Credentials

### Bhashini ULCA API

1. **Visit**: https://bhashini.gov.in/
2. **Register** for an account
3. **Navigate** to API section
4. **Generate** API key and note your User ID
5. **Copy** both values to your configuration

### AWS Credentials

1. **Sign in** to AWS Console: https://console.aws.amazon.com/
2. **Go to IAM** → Users → Your User
3. **Create Access Key**:
   - Click "Security credentials" tab
   - Click "Create access key"
   - Choose "Application running outside AWS"
   - Download or copy the credentials
4. **Enable Bedrock Access**:
   - Go to AWS Bedrock console
   - Request model access for Claude 3.5 Sonnet
   - Wait for approval (usually instant)

### Required IAM Permissions

Your AWS user needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name/*",
                "arn:aws:s3:::your-bucket-name"
            ]
        }
    ]
}
```

## Verification

### Test Bhashini Credentials

```bash
python test_bhashini_stt.py
```

Expected output:
```
✅ Credentials found
✅ Bhashini client initialized
```

### Test AWS Bedrock Credentials

```bash
python test_bedrock.py
```

Expected output:
```
✅ AWS credentials found
✅ Bedrock client initialized
✅ Generation successful!
```

### Test in Streamlit App

```bash
streamlit run app.py
```

1. Record audio
2. Click "Process Question"
3. Should see: "🎤 AI Avenger is listening..."
4. No error about missing credentials

## Troubleshooting

### "Bhashini credentials not configured"

**Cause**: BHASHINI_API_KEY or BHASHINI_USER_ID not set

**Solutions**:
1. Check `.env` file exists and has correct values
2. Verify environment variables are set: `echo $env:BHASHINI_API_KEY` (Windows) or `echo $BHASHINI_API_KEY` (Linux/Mac)
3. For Streamlit Cloud: Check secrets are added in dashboard
4. Restart terminal/IDE after setting environment variables

### "AWS Bedrock not available"

**Cause**: boto3 not installed

**Solution**:
```bash
pip install boto3
```

### "The security token included in the request is invalid"

**Cause**: Invalid AWS credentials

**Solutions**:
1. Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are correct
2. Check credentials haven't expired
3. Ensure IAM user has necessary permissions
4. Try creating new access keys

### "Could not resolve the foundation model"

**Cause**: Model not available in region or access not granted

**Solutions**:
1. Go to AWS Bedrock console
2. Click "Model access" in left sidebar
3. Request access to Claude 3.5 Sonnet
4. Wait for approval (usually instant)
5. Verify region supports the model (use us-east-1, us-west-2, or eu-west-1)

## Security Best Practices

### ⚠️ NEVER commit credentials to Git!

1. **Add to .gitignore**:
```
.env
.streamlit/secrets.toml
*.key
*.pem
```

2. **Use secrets management**:
   - Streamlit Cloud: Use built-in secrets
   - AWS: Use AWS Secrets Manager
   - Local: Use .env files (gitignored)

3. **Rotate credentials regularly**:
   - Change API keys every 90 days
   - Use temporary credentials when possible

4. **Limit permissions**:
   - Only grant necessary IAM permissions
   - Use separate credentials for dev/prod

## File Structure

```
gram-vani/
├── .env                          # Local credentials (gitignored)
├── .streamlit/
│   └── secrets.toml             # Streamlit Cloud secrets (gitignored)
├── .env.example                 # Template (committed to git)
├── SETUP_CREDENTIALS.md         # This file
└── app.py                       # Uses get_credential() helper
```

## Quick Start Checklist

- [ ] Get Bhashini API credentials from https://bhashini.gov.in/
- [ ] Get AWS credentials from AWS Console
- [ ] Enable Bedrock model access for Claude 3.5 Sonnet
- [ ] Create `.env` file with all credentials
- [ ] Test with `python test_bhashini_stt.py`
- [ ] Test with `python test_bedrock.py`
- [ ] Run app with `streamlit run app.py`
- [ ] For Streamlit Cloud: Add secrets in dashboard

## Support

If you're still having issues:

1. Check the logs for detailed error messages
2. Run test scripts to isolate the problem
3. Verify credentials are correct and active
4. Check AWS service health dashboard
5. Review Bhashini API documentation

## Resources

- **Bhashini**: https://bhashini.gov.in/
- **AWS Bedrock**: https://docs.aws.amazon.com/bedrock/
- **Streamlit Secrets**: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
- **IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
