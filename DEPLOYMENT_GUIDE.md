# Deployment Guide - Gram-Vani with AWS Audio Services

## Quick Deployment to Streamlit Cloud

### Step 1: Update Secrets

1. Go to your Streamlit Cloud dashboard: https://share.streamlit.io/
2. Navigate to your app: **Gram-Vani**
3. Click **Settings** → **Secrets**
4. Replace all secrets with:

```toml
# AWS Credentials
AWS_ACCESS_KEY_ID = "your-aws-access-key-here"
AWS_SECRET_ACCESS_KEY = "your-aws-secret-key-here"
AWS_REGION = "us-east-1"
```

5. Click **Save**

### Step 2: Update IAM Permissions

Ensure your AWS IAM user has these permissions:

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

### Step 3: Enable Bedrock Model Access

1. Go to AWS Console → Bedrock
2. Click **Model access** in left sidebar
3. Click **Manage model access**
4. Enable **Claude 3.5 Sonnet v2**
5. Click **Save changes**
6. Wait for approval (usually instant)

### Step 4: Push to GitHub

```bash
git add .
git commit -m "Migrate to AWS Transcribe and Polly for audio processing"
git push origin main
```

### Step 5: Verify Deployment

1. Wait for Streamlit Cloud to rebuild (2-3 minutes)
2. Visit your app URL: https://gramvani-xvz2ced5pf7tnjmgneaeaw.streamlit.app/
3. Test the flow:
   - Select Hindi language
   - Click microphone and record a question
   - Click "Process Question"
   - Verify transcription appears
   - Verify answer is generated
   - Verify audio plays automatically

## Local Development Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Credentials

Create a `.env` file:

```bash
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

### Step 3: Run Application

```bash
# Basic version
streamlit run app.py

# Full version with audio flow
streamlit run app_improved.py
```

### Step 4: Test Integration

```bash
python test_aws_audio.py
```

Expected output:
```
✅ AWS_AVAILABLE: True
✅ AWSAudioClient imported successfully
✅ AWSAudioClient initialized successfully
✅ Supported languages: hi, en, ta, te, bn, mr, gu, kn
✅ app.py can be loaded
✅ app_improved.py can be loaded
🎉 All tests passed! Integration is complete.
```

## Troubleshooting

### "AWS services not available"

**Solution**: Install boto3
```bash
pip install boto3
```

### "The security token included in the request is invalid"

**Solution**: Check AWS credentials
1. Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are correct
2. Check credentials haven't expired
3. Try creating new access keys in IAM

### "Could not resolve the foundation model"

**Solution**: Enable Bedrock model access
1. Go to AWS Bedrock console
2. Request access to Claude 3.5 Sonnet
3. Wait for approval

### "S3 upload failed" or "Access Denied"

**Solution**: Check S3 permissions
1. Verify IAM policy includes S3 actions
2. Check bucket name pattern: `gram-vani-transcribe-*`
3. Ensure region supports S3

### "Transcription timeout"

**Solution**: Check audio length and format
1. Keep audio under 60 seconds
2. Use WAV format (16kHz recommended)
3. Check Transcribe service status

### "Polly error" or "Voice not found"

**Solution**: Verify language and voice
1. Hindi uses Aditi (female) or Madhav (male)
2. Other languages use Joanna (fallback)
3. Check Polly permissions in IAM

## Monitoring

### CloudWatch Logs

Monitor AWS service usage:
1. Go to CloudWatch console
2. Check logs for:
   - `/aws/transcribe/`
   - `/aws/polly/`
   - `/aws/bedrock/`

### Cost Monitoring

Track costs in AWS Cost Explorer:
1. Go to AWS Console → Billing
2. Click **Cost Explorer**
3. Filter by service:
   - Amazon Transcribe
   - Amazon Polly
   - Amazon Bedrock
   - Amazon S3

### Usage Metrics

Monitor in CloudWatch Metrics:
- Transcribe: Job count, duration
- Polly: Character count
- Bedrock: Token count
- S3: Storage, requests

## Performance Optimization

### Reduce Latency
1. Use same region for all services (us-east-1)
2. Keep audio files small (< 30 seconds)
3. Optimize prompt length for Bedrock

### Reduce Costs
1. Delete S3 objects immediately after use ✅ (already implemented)
2. Use standard Polly voices instead of neural (if acceptable)
3. Cache frequent queries
4. Implement rate limiting

### Improve Accuracy
1. Use high-quality audio (16kHz, WAV)
2. Reduce background noise
3. Speak clearly and at moderate pace
4. Use language-specific models

## Rollback Plan

If you need to revert to Bhashini:

1. **Revert code changes**:
```bash
git revert HEAD
git push origin main
```

2. **Update secrets**:
```toml
BHASHINI_API_KEY = "your-key"
BHASHINI_USER_ID = "your-id"
AWS_ACCESS_KEY_ID = "your-key"
AWS_SECRET_ACCESS_KEY = "your-secret"
AWS_REGION = "us-east-1"
```

3. **Redeploy**

Note: Not recommended due to Bhashini reliability issues.

## Support Resources

- **AWS Documentation**:
  - [Transcribe](https://docs.aws.amazon.com/transcribe/)
  - [Polly](https://docs.aws.amazon.com/polly/)
  - [Bedrock](https://docs.aws.amazon.com/bedrock/)
  
- **Project Documentation**:
  - [SETUP_CREDENTIALS.md](SETUP_CREDENTIALS.md) - Credential setup
  - [AWS_MIGRATION.md](AWS_MIGRATION.md) - Migration details
  - [INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md) - Integration summary

- **Streamlit**:
  - [Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
  - [Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

## Post-Deployment Checklist

- [ ] Secrets updated in Streamlit Cloud
- [ ] IAM permissions verified
- [ ] Bedrock model access enabled
- [ ] Code pushed to GitHub
- [ ] App deployed and running
- [ ] Audio recording tested
- [ ] Transcription verified
- [ ] Answer generation working
- [ ] Audio playback working
- [ ] CloudWatch monitoring enabled
- [ ] Cost alerts configured

## Success Criteria

✅ App loads without errors
✅ Audio can be recorded
✅ Transcription appears correctly
✅ Answer is generated by Bedrock
✅ Audio response plays automatically
✅ No credential errors
✅ All AWS services responding
✅ Costs within expected range

## Next Steps After Deployment

1. **Monitor for 24 hours**
   - Check CloudWatch logs
   - Monitor error rates
   - Track costs

2. **Gather user feedback**
   - Test with real users
   - Collect accuracy feedback
   - Note any issues

3. **Optimize based on usage**
   - Adjust timeout values
   - Optimize prompt templates
   - Fine-tune language models

4. **Plan enhancements**
   - Add more languages
   - Implement caching
   - Add analytics dashboard

## Contact

For deployment issues:
- Check GitHub Issues
- Review CloudWatch logs
- Contact AWS Support (if needed)

---

**Status**: Ready for deployment 🚀
**Last Updated**: 2026-03-02
