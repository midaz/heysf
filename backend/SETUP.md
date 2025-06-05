# Quick Setup Guide

## 1. Environment Setup

Copy the environment template and fill in your credentials:

```bash
cp env.template .env
```

Then edit `.env` with your actual values:

- **OPENAI_API_KEY**: Get from https://platform.openai.com/api-keys
- **AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY**: Your AWS credentials
- **AWS_S3_BUCKET**: Name of your S3 bucket (must already exist)

## 2. Custom Prompts Setup

### To add your custom prompt:

1. Open `prompts.txt` and add your detailed analysis prompt
2. Copy your prompt from `prompts.txt`
3. Paste it into your `.env` file as `ANALYSIS_PROMPT="your prompt here"`
4. Save both files

### How it works:

- Keep your prompts organized in `prompts.txt` (git-ignored for privacy)
- Copy the one you want to use into your `.env` file
- Easy to switch between different prompt versions

### Example:

In `prompts.txt`:
```
[Your detailed analysis instructions here]

Focus on:
- Budget implications  
- Policy changes
- Timeline extraction
- Stakeholder analysis
```

In `.env`:
```
ANALYSIS_PROMPT="Your detailed analysis instructions here..."
```

## 3. Database Setup

Start PostgreSQL:
```bash
docker-compose up -d postgres
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Run the Application

Start the API:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Start the scheduler (in another terminal):
```bash
python scheduler.py
```

## 6. Test the Setup

Visit http://localhost:8000/docs to see the API documentation.

Test scraping:
```bash
curl -X POST http://localhost:8000/api/documents/scrape
```

## Security Notes

- `prompts.txt` is in `.gitignore` - your custom prompts won't be committed
- `.env` is also git-ignored - your credentials stay private
- Never commit API keys or credentials to version control 