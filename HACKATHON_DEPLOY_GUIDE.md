# 🚀 2-Minute Deployment Guide (Streamlit Cloud)

Since we pivoted to the lightweight **Gemini + Bhashini Web STT** architecture, deploying your MVP is incredibly simple. You do **not** need to configure AWS IAM, Bedrock, or S3 for this hackathon demo.

Here is exactly how to get your app live on the internet so the judges can use it:

## Step 1: Log in to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click **Continue with GitHub** and authorize it.

## Step 2: Deploy the App
1. Click the **New app** button (top right).
2. Select **Use existing repo**.
3. Fill in the deployment details:
   - **Repository:** `mahimasisodiya049-blip/Gram_vani`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **Deploy!**

*Wait about 1-2 minutes. You will see an error on the screen saying "API Key Error" — this is normal because we haven't added your secret key yet!*

## Step 3: Add Your Gemini API Key
1. Once deployed, click the **Settings** button (gear icon ⚙️) in the bottom right corner or top right of your app dashboard.
2. Click on **Secrets** in the left menu.
3. Paste your Gemini API key exactly like this:
   ```toml
   GRAMVANI_GEMINI_KEY = "AIzaSy..."
   ```
4. Click **Save**.

## Step 4: Reboot & Test
1. The app will automatically reboot. (If it doesn't, click the three dots `⋮` in the top right and select **Reboot**).
2. **You are live!** Share the URL with the hackathon judges.

---
*Note: The old `DEPLOYMENT_CHECKLIST.md` in this repo refers to the legacy AWS setup and can be ignored for this MVP.*
