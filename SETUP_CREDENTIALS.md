# Setting Up Credentials for Gram-Vani

This guide explains how to configure API credentials for both local development and Streamlit Cloud deployment.

## Required Credentials

### AWS Credentials (Required for all services)
- **AWS_ACCESS_KEY_ID**: Your AWS access key
- **AWS_SECRET_ACCESS_KEY**: Your AWS secret key
- **AWS_REGION**: AWS region (default: us-east-1)

**Note**: Bhashini API has been replaced with AWS Transcribe (STT) and AWS Polly (TTS) for better reliability.

## Setup Methods

### Method 1: Local Development (Using .env file)

1. **Create a `.env` file** in the project root:
```bash
# .env file
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
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_REGION="us-east-1"
```

**Linux/Mac:**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

### Method 3: Streamlit Cloud Deployment

1. **Go to your Streamlit Cloud dashboard**
2. **Click on your app** → "Settings" → "Secrets"
3. **Add secrets in TOML format**:

```toml
# AWS Credentials
AWS_ACCESS_KEY_ID = "your-aws-access-key-here"
AWS_SECRET_ACCESS_KEY = "your-aws-secret-key-here"
AWS_REGION = "us-east-1"
```

4. **Save** and the app will automatically restart with new credentials

## Getting API Credentials

### AWS Credentials

1. **Sign in** to AWS Console: https://console.aws.amazon.com/
2. **Go to IAM** → Users → Your User
3. **Create Access Key**:
   - Click "Security credentials" tab
   - Click "Create access key"
   - Choose "Application running outside AWS"
   - Download or copy the credentials
4. **Enable Required Services**:
   - **Bedrock**: Request model access for Claude 3.5 Sonnet
   - **Transcribe**: Enabled by default (no setup needed)
   - **Polly**: Enabled by default (no setup needed)
   - **S3**: Create bucket or allow auto-creation

### Required IAM Permissions

Your AWS user needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockAccess",
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
            "Sid": "TranscribeAccess",
            "Effect": "Allow",
            "Action": [
                "transcribe:StartTranscriptionJob",
                "transcribe:GetTranscriptionJob",
                "transcribe:DeleteTranscriptionJob"
            ],
            "Resource": "*"
        },
        {
            "Sid": "PollyAccess",
            "Effect": "Allow",
            "Action": [
                "polly:SynthesizeSpeech"
            ],
            "Resource": "*"
        },
        {
            "Sid": "S3Access",
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:HeadBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::gram-vani-transcribe-*",
                "arn:aws:s3:::gram-vani-transcribe-*/*"
            ]
        }
    ]
}
```

## Verification

### Test AWS Services

```bash
# Test all AWS services together
streamlit run app.py
```

1. Record audio
2. Click "Process Question"
3. Should see: "🎤 AI Avenger is listening..." → "🤖 AI Avenger is thinking..." → "🔊 AI Avenger is speaking..."
4. No error about missing credentials

## Troubleshooting

### "AWS services not available"

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

### "Transcription failed" or "S3 upload failed"

**Cause**: Missing Transcribe or S3 permissions

**Solutions**:
1. Verify IAM permissions include transcribe:* and s3:* actions
2. Check S3 bucket name doesn't conflict (auto-created as `gram-vani-transcribe-{region}`)
3. Ensure region supports Transcribe (most regions do)
4. Check audio format is supported (WAV recommended)

### "Polly error" or "TTS failed"

**Cause**: Missing Polly permissions or unsupported voice

**Solutions**:
1. Verify IAM permissions include polly:SynthesizeSpeech
2. Check language is supported (Hindi, English, Tamil, Telugu, Bengali)
3. For Hindi: Uses Aditi (female) or Madhav (male) voices
4. Ensure text is not empty

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

- [ ] Get AWS credentials from AWS Console
- [ ] Enable Bedrock model access for Claude 3.5 Sonnet
- [ ] Verify IAM permissions for Bedrock, Transcribe, Polly, and S3
- [ ] Create `.env` file with AWS credentials
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run app with `streamlit run app.py` or `streamlit run app_improved.py`
- [ ] For Streamlit Cloud: Add secrets in dashboard

## Support

If you're still having issues:

1. Check the logs for detailed error messages
2. Verify credentials are correct and active
3. Check AWS service health dashboard
4. Ensure IAM permissions are correctly configured
5. Test with simple audio recording first

## Resources

- **AWS Bedrock**: https://docs.aws.amazon.com/bedrock/
- **AWS Transcribe**: https://docs.aws.amazon.com/transcribe/
- **AWS Polly**: https://docs.aws.amazon.com/polly/
- **Streamlit Secrets**: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
- **IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
