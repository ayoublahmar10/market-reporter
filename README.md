# Market Reporter

An automated daily financial report delivered to your inbox — powered by Python, Groq AI, and AWS Lambda.

Every day the bot fetches live market data, runs an AI analysis, and sends **3 separate HTML emails**:
- 🇺🇸 US markets (S&P 500, Nasdaq, top tech stocks)
- 🇪🇺 European markets (CAC 40, DAX, ETFs, commodities)
- ₿ Crypto (BTC, ETH, top altcoins)

---

## Features

- **Live data** — stock prices, indices, crypto via yfinance
- **EUR/USD rate** — fetched daily, embedded in US report header
- **AI analysis** — market commentary and outlook via Groq (LLaMA 3)
- **Investment plan** — personalized portfolio advice per scope
- **Top picks** — scored stock screener
- **Alerts** — triggers on significant price moves
- **HTML email** — clean, styled report sent via Gmail SMTP
- **Cloud-native** — runs on AWS Lambda + EventBridge (no PC needed)

---

## Project Structure

```
market-reporter/
├── main.py                  # Entry point — orchestrates everything
├── lambda_handler.py        # AWS Lambda handler
├── analyzer.py              # AI market analysis (Groq)
├── report_generator.py      # HTML report builder
├── emailer.py               # Gmail SMTP sender
├── alerts.py                # Price alert rules
├── screener.py              # Stock scoring / top picks
├── portfolio_advisor.py     # AI investment plan
├── config.py                # Loads env variables
├── collectors/
│   ├── market_data.py       # Fetches stocks, indices, EUR/USD
│   ├── crypto_data.py       # Fetches crypto prices
│   └── news_collector.py    # Fetches financial RSS news
├── deploy/
│   └── build_lambda.sh      # Lambda build script (run in AWS CloudShell)
├── setup_scheduler.py       # Windows Task Scheduler setup (local alternative)
└── requirements.txt
```

---

## Setup

### 1. Clone & install

```bash
git clone https://github.com/your-username/market-reporter.git
cd market-reporter
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file at the project root:

```env
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
EMAIL_TO=recipient@email.com
GROQ_API_KEY=gsk_...
```

> **Gmail App Password**: Google Account → Security → 2-Step Verification → App passwords

> **Groq API key**: free at [console.groq.com](https://console.groq.com)

### 3. Run locally

```bash
python main.py
```

---

## Deploy to AWS Lambda (cloud scheduling)

The Lambda runs daily via EventBridge — no PC needed.

### Build the package (in AWS CloudShell)

1. Open **AWS Console → CloudShell**
2. Upload your project zip: **Actions → Upload file**
3. Run:

```bash
unzip market-reporter.zip && cd market-reporter
bash deploy/build_lambda.sh
```

4. Download `lambda_package.zip`: **Actions → Download file**

### Configure Lambda

| Setting | Value |
|---|---|
| Runtime | Python 3.12 |
| Handler | `lambda_handler.handler` |
| Timeout | 5 minutes |
| Memory | 256 MB |

**Environment variables** to set in Lambda → Configuration → Environment variables:

```
GMAIL_USER         = your@gmail.com
GMAIL_APP_PASSWORD = xxxx xxxx xxxx xxxx
EMAIL_TO           = recipient@email.com
GROQ_API_KEY       = gsk_...
```

### EventBridge Scheduler

Create a schedule with cron expression (UTC):

```
0 14 * * ? *   →  14:00 UTC = 15:00 Paris (winter)
```

---

## Local Scheduling (Windows alternative)

Run once as Administrator to create a daily Windows Task:

```bash
python setup_scheduler.py
```

Edit `SEND_TIME` in [setup_scheduler.py](setup_scheduler.py) to change the daily send time.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.12 | Core language |
| yfinance | Stock & crypto data |
| feedparser | Financial RSS news |
| Groq (LLaMA 3) | AI analysis |
| smtplib | Email sending |
| AWS Lambda | Serverless execution |
| AWS EventBridge | Cron scheduling |

---

## License

MIT
