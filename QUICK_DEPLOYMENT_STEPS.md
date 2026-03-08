# Quick Deployment Steps - Gram-Vani AWS Migration

## ✅ DONE: Code Pushed to GitHub

Your code is now live on GitHub! 🎉

---

## 🚀 Next Steps (Manual Actions Required)

### 1️⃣ Update Streamlit Cloud Secrets (5 minutes)

**Go to**: https://share.streamlit.io/ → Your App → Settings → Secrets

**Replace all secrets with**:
```toml
AWS_ACCESS_KEY_ID = "your-aws-access-key-here"
AWS_SECRET_ACCESS_KEY = "your-aws-secret-key-here"
AWS_REGION = "us-east-1"
```

**Remove**: Any BHASHINI_* secrets

---

### 2️⃣ Add IAM Permissions (10 minutes)

**Go to**: https://console.aws.amazon.com/iam/ → Users → Your User → Permissions

**Add this inline policy** (name it `GramVaniAWSServices`):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockAccess",
            "Effect": "Allow",
            "Action": ["bedrock:InvokeModel"],
            "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
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
            "Action": ["polly:SynthesizeSpeech"],
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
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::gram-vani-transcribe-*",
                "arn:aws:s3:::gram-vani-transcribe-*/*"
            ]
        }
    ]
}
```

---

### 3️⃣ Enable Bedrock Model Access (2 minutes)

**Go to**: https://console.aws.amazon.com/bedrock/ (region: us-east-1)

**Steps**:
1. Click **Model access** (left sidebar)
2. Click **Manage model access**
3. Check ☑️ **Claude 3.5 Sonnet v2**
4. Click **Request model access**
5. Wait for approval (usually instant) ✅

---

### 4️⃣ Test Your App (5 minutes)

**Go to**: https://gramvani-xvz2ced5pf7tnjmgneaeaw.streamlit.app/

**Test Flow**:
1. Select "Hindi" language
2. Click microphone 🎤
3. Record: "यह दस्तावेज़ क्या है?"
4. Click "Process Question"
5. ✅ Verify transcription appears
6. ✅ Verify answer is generated
7. ✅ Verify audio plays automatically

---

## 📋 Quick Checklist

- [ ] Streamlit secrets updated (AWS only)
- [ ] IAM permissions added (Bedrock, Transcribe, Polly, S3)
- [ ] Bedrock model access granted (Claude 3.5 Sonnet v2)
- [ ] App tested and working

---

## 🆘 Quick Troubleshooting

| Error | Fix |
|-------|-----|
| "AWS services not available" | Check boto3 in requirements.txt |
| "Invalid security token" | Verify AWS credentials in secrets |
| "Model not found" | Enable Bedrock model access |
| "Access Denied" | Check IAM permissions |
| "Transcription timeout" | Audio too long (keep < 60 sec) |

---

## 📚 Full Documentation

- **Detailed Steps**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Setup Guide**: [SETUP_CREDENTIALS.md](SETUP_CREDENTIALS.md)
- **Migration Info**: [AWS_MIGRATION.md](AWS_MIGRATION.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## ⏱️ Estimated Time

- **Total**: ~25 minutes
- **Step 1**: 5 min (Update secrets)
- **Step 2**: 10 min (IAM permissions)
- **Step 3**: 2 min (Bedrock access)
- **Step 4**: 5 min (Testing)
- **Buffer**: 3 min

---

## 🎯 Success = All Green Checkmarks

When you see:
- ✅ "🎤 AI Avenger is listening..."
- ✅ Transcribed text appears
- ✅ "🤖 AI Avenger is thinking..."
- ✅ Answer is generated
- ✅ "🔊 AI Avenger is speaking..."
- ✅ Audio plays automatically

**You're done! 🎉**

---

**Current Status**: Code pushed ✅ | Manual steps pending ⏳

**Next Action**: Go to Streamlit Cloud and update secrets (Step 1)
