# Deployment Checklist for Gram-Vani AWS Migration

## ✅ Step 4: Push to GitHub - COMPLETE

Code has been successfully pushed to GitHub repository.

**Commit**: Migrate from Bhashini to AWS Transcribe and Polly for audio processing
**Files Changed**: 11 files (1577 insertions, 172 deletions)
**Status**: ✅ DONE

---

## 📋 Step 1: Update Streamlit Cloud Secrets

### Instructions:

1. **Go to Streamlit Cloud Dashboard**
   - URL: https://share.streamlit.io/
   - Login with your credentials

2. **Navigate to Your App**
   - Find "Gram-Vani" in your apps list
   - Click on the app name

3. **Open Secrets Settings**
   - Click the **⚙️ Settings** button (top right)
   - Select **Secrets** from the menu

4. **Remove Old Secrets**
   - Delete these lines if they exist:
     ```toml
     BHASHINI_API_KEY = "..."
     BHASHINI_USER_ID = "..."
     ```

5. **Add/Update AWS Secrets**
   - Replace all content with:
     ```toml
     # AWS Credentials
     AWS_ACCESS_KEY_ID = "your-aws-access-key-here"
     AWS_SECRET_ACCESS_KEY = "your-aws-secret-key-here"
     AWS_REGION = "us-east-1"
     ```

6. **Save Changes**
   - Click **Save** button
   - App will automatically restart (takes 2-3 minutes)

### Verification:
- [ ] Old Bhashini secrets removed
- [ ] AWS credentials added
- [ ] Secrets saved successfully
- [ ] App restarted without errors

**Status**: ⏳ PENDING

---

## 🔐 Step 2: Verify IAM Permissions

### Instructions:

1. **Go to AWS IAM Console**
   - URL: https://console.aws.amazon.com/iam/
   - Login with your AWS account

2. **Find Your IAM User**
   - Click **Users** in left sidebar
   - Find the user whose credentials you're using
   - Click on the username

3. **Check Current Permissions**
   - Click **Permissions** tab
   - Review attached policies

4. **Add Required Permissions**
   
   **Option A: Create Custom Policy (Recommended)**
   
   a. Click **Add permissions** → **Create inline policy**
   
   b. Click **JSON** tab
   
   c. Paste this policy:
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
   
   d. Click **Review policy**
   
   e. Name it: `GramVaniAWSServices`
   
   f. Click **Create policy**

   **Option B: Attach AWS Managed Policies (Simpler but broader permissions)**
   
   - Click **Add permissions** → **Attach policies directly**
   - Search and attach:
     - `AmazonTranscribeFullAccess`
     - `AmazonPollyFullAccess`
     - `AmazonS3FullAccess` (or create custom S3 policy)
   - For Bedrock, you'll still need a custom policy

5. **Verify Permissions**
   - Go back to user's **Permissions** tab
   - Confirm all required services are listed

### Required Services Checklist:
- [ ] Amazon Bedrock (InvokeModel)
- [ ] Amazon Transcribe (Start/Get/Delete TranscriptionJob)
- [ ] Amazon Polly (SynthesizeSpeech)
- [ ] Amazon S3 (CreateBucket, Get/Put/Delete Object)

**Status**: ⏳ PENDING

---

## 🤖 Step 3: Enable Bedrock Model Access

### Instructions:

1. **Go to AWS Bedrock Console**
   - URL: https://console.aws.amazon.com/bedrock/
   - Select region: **us-east-1** (or your preferred region)

2. **Navigate to Model Access**
   - Click **Model access** in the left sidebar
   - You'll see a list of available models

3. **Request Access to Claude 3.5 Sonnet**
   - Find **Anthropic** section
   - Look for **Claude 3.5 Sonnet v2**
   - Click **Manage model access** (top right)

4. **Enable the Model**
   - Check the box next to:
     - ☑️ **Claude 3.5 Sonnet v2** (anthropic.claude-3-5-sonnet-20241022-v2:0)
   - Optionally enable other Claude models for backup

5. **Submit Request**
   - Click **Request model access** button
   - Wait for approval (usually instant, but can take a few minutes)

6. **Verify Access**
   - Refresh the page
   - Status should show **Access granted** with a green checkmark ✅

### Model Details:
- **Model ID**: `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Region**: us-east-1 (recommended)
- **Use Case**: RAG-based question answering
- **Pricing**: $3/1M input tokens, $15/1M output tokens

### Verification:
- [ ] Bedrock console accessible
- [ ] Model access page opened
- [ ] Claude 3.5 Sonnet v2 requested
- [ ] Access granted (green checkmark)

**Status**: ⏳ PENDING

---

## 🧪 Step 5: Test in Production

### Instructions:

1. **Wait for Deployment**
   - Streamlit Cloud should auto-deploy after secrets update
   - Check deployment status in Streamlit dashboard
   - Wait for "App is running" status (2-3 minutes)

2. **Open Your App**
   - URL: https://gramvani-xvz2ced5pf7tnjmgneaeaw.streamlit.app/
   - App should load without errors

3. **Test Complete Audio Flow**

   **Test 1: Hindi Voice Query**
   - [ ] Select "Hindi" from language dropdown
   - [ ] Click microphone button
   - [ ] Record a question in Hindi (e.g., "यह दस्तावेज़ क्या है?")
   - [ ] Click "Process Question"
   - [ ] Verify: "🎤 AI Avenger is listening..." appears
   - [ ] Verify: Transcribed text appears correctly
   - [ ] Verify: "🤖 AI Avenger is thinking..." appears
   - [ ] Verify: Answer is generated
   - [ ] Verify: "🔊 AI Avenger is speaking..." appears
   - [ ] Verify: Audio plays automatically (Aditi voice)

   **Test 2: English Voice Query**
   - [ ] Select "English" from language dropdown
   - [ ] Record a question in English (e.g., "What is this document about?")
   - [ ] Click "Process Question"
   - [ ] Verify: Complete flow works
   - [ ] Verify: Audio plays (Joanna voice)

   **Test 3: Error Handling**
   - [ ] Try recording very short audio (< 1 second)
   - [ ] Verify: Appropriate error message appears
   - [ ] Try recording without speaking
   - [ ] Verify: Error handling works gracefully

4. **Check for Errors**
   - [ ] No "AWS services not available" error
   - [ ] No "Credentials not configured" error
   - [ ] No "Access Denied" errors
   - [ ] No "Model not found" errors

5. **Monitor AWS Services**
   
   **Check CloudWatch Logs** (optional but recommended):
   - Go to CloudWatch console
   - Check logs for:
     - Transcribe jobs
     - Polly requests
     - Bedrock invocations
   - Verify no errors in logs

   **Check S3 Buckets**:
   - Go to S3 console
   - Look for bucket: `gram-vani-transcribe-us-east-1`
   - Verify bucket exists (created automatically)
   - Verify bucket is empty (files should be deleted after use)

6. **Performance Check**
   - [ ] Transcription completes in < 15 seconds
   - [ ] Answer generation completes in < 10 seconds
   - [ ] Audio synthesis completes in < 5 seconds
   - [ ] Total flow completes in < 30 seconds

### Verification Checklist:
- [ ] App loads successfully
- [ ] No credential errors
- [ ] Audio recording works
- [ ] Transcription appears correctly
- [ ] Answer is generated
- [ ] Audio response plays automatically
- [ ] All loading spinners work
- [ ] Error handling works
- [ ] Performance is acceptable

**Status**: ⏳ PENDING

---

## 📊 Post-Deployment Monitoring

### First 24 Hours:

1. **Monitor Costs**
   - Go to AWS Billing Dashboard
   - Check costs for:
     - Amazon Transcribe
     - Amazon Polly
     - Amazon Bedrock
     - Amazon S3
   - Expected: < $1 for testing

2. **Monitor Usage**
   - Check CloudWatch metrics
   - Track number of:
     - Transcription jobs
     - Polly requests
     - Bedrock invocations

3. **Monitor Errors**
   - Check CloudWatch logs
   - Look for any error patterns
   - Address any issues immediately

### Set Up Alerts (Recommended):

1. **Cost Alert**
   - Go to AWS Billing → Budgets
   - Create budget: $10/month
   - Set alert at 80% threshold

2. **Error Alert**
   - Go to CloudWatch → Alarms
   - Create alarm for error rates
   - Set SNS notification

**Status**: ⏳ PENDING

---

## 🎉 Success Criteria

All items must be checked for successful deployment:

### Configuration:
- [ ] Streamlit secrets updated (AWS only)
- [ ] IAM permissions verified and added
- [ ] Bedrock model access granted
- [ ] Code pushed to GitHub
- [ ] App deployed to Streamlit Cloud

### Functionality:
- [ ] App loads without errors
- [ ] Audio recording works
- [ ] Transcription is accurate
- [ ] Answer generation works
- [ ] Audio playback works
- [ ] All languages tested
- [ ] Error handling verified

### Performance:
- [ ] Response time < 30 seconds
- [ ] No timeout errors
- [ ] Audio quality is good
- [ ] UI is responsive

### Monitoring:
- [ ] CloudWatch logs accessible
- [ ] Cost tracking enabled
- [ ] No unexpected errors
- [ ] S3 cleanup working

---

## 🆘 Troubleshooting Guide

### Issue: "AWS services not available"
**Solution**: Check boto3 is in requirements.txt and installed

### Issue: "The security token included in the request is invalid"
**Solution**: 
1. Verify AWS credentials in Streamlit secrets
2. Check credentials haven't expired
3. Try creating new access keys

### Issue: "Could not resolve the foundation model"
**Solution**:
1. Go to Bedrock console
2. Verify Claude 3.5 Sonnet access is granted
3. Check region is us-east-1

### Issue: "S3 upload failed" or "Access Denied"
**Solution**:
1. Check S3 permissions in IAM policy
2. Verify bucket name pattern: `gram-vani-transcribe-*`
3. Check region supports S3

### Issue: "Transcription timeout"
**Solution**:
1. Check audio length (should be < 60 seconds)
2. Verify audio format is WAV
3. Check Transcribe service status

### Issue: "Polly error"
**Solution**:
1. Check Polly permissions in IAM
2. Verify language is supported
3. Ensure text is not empty

---

## 📞 Support Resources

- **Documentation**: 
  - [SETUP_CREDENTIALS.md](SETUP_CREDENTIALS.md)
  - [AWS_MIGRATION.md](AWS_MIGRATION.md)
  - [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

- **AWS Documentation**:
  - [Transcribe](https://docs.aws.amazon.com/transcribe/)
  - [Polly](https://docs.aws.amazon.com/polly/)
  - [Bedrock](https://docs.aws.amazon.com/bedrock/)

- **Streamlit**:
  - [Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

---

## ✅ Completion Status

- [x] **Step 4**: Push to GitHub - ✅ COMPLETE
- [ ] **Step 1**: Update Streamlit Cloud secrets - ⏳ PENDING
- [ ] **Step 2**: Verify IAM permissions - ⏳ PENDING
- [ ] **Step 3**: Enable Bedrock model access - ⏳ PENDING
- [ ] **Step 5**: Test in production - ⏳ PENDING

**Overall Status**: 🚧 IN PROGRESS (1/5 complete)

---

**Last Updated**: 2026-03-02
**Next Action**: Update Streamlit Cloud secrets (Step 1)
