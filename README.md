# Fulfillment Center Daily P&L Analysis

This repository provides an automated pipeline for analyzing daily P&L data from a fulfillment center, flagging anomalies, generating actionable insights, and dispatching alerts via email. The workflow is modular, using agents for data ingestion, anomaly detection, insight generation (via LLM), and alerting.

## Features

- **Data Ingestion:** Loads and processes daily P&L data from CSV.
- **Anomaly Detection:** Flags line items that breach target thresholds.
- **Insight Generation:** Uses LLM (Groq API) to generate concise business insights for flagged anomalies.
- **Alert Dispatch:** Sends daily digest emails and logs alerts locally.

## Folder Structure

```
.
├── agent3.py
├── alert.py
├── daily_status_log.csv
├── Entreprenuer in Residence _ EIR _ Case Study 2 - Day Wise PnL copy.csv
├── flagged_anomalies_log.csv
├── main.py
├── requirements.txt
├── .env
```

## Setup

1. **Clone the repository**

2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the root directory with the following keys:
   ```
   GROQ_API_KEY = 'your_groq_api_key'
   APP_PASSWORD = 'your_app_password'
   SENDER_EMAIL = 'your_email@example.com'
   ```

   - `GROQ_API_KEY`: API key for Groq LLM.
   - `APP_PASSWORD`: App password for your email (for Gmail, generate an App Password).
   - `SENDER_EMAIL`: The sender's email address.

4. **Prepare input data**

   Ensure your daily P&L data is in the file:
   ```
   Entreprenuer in Residence _ EIR _ Case Study 2 - Day Wise PnL copy.csv
   ```

## Usage

Run the main pipeline:
```sh
python main.py
```

- The script will process the data, flag anomalies, generate insights, and send a daily digest email (if credentials are set).
- Logs and outputs are saved to `flagged_anomalies_log.csv` and `daily_status_log.csv`.

## Main Components

- [`main.py`](main.py): Orchestrates the pipeline.
- [`agent3.py`](agent3.py): Insight generation using Groq LLM.
- [`alert.py`](alert.py): Email dispatch and local logging.
- [`Entreprenuer in Residence _ EIR _ Case Study 2 - Day Wise PnL copy.csv`](Entreprenuer%20in%20Residence%20_%20EIR%20_%20Case%20Study%202%20-%20Day%20Wise%20PnL%20copy.csv): Input data file.

## Customization

- **Target Ranges:** Modify in [`PnLAnalyzerAgent`](main.py) for different line items.
- **Email Recipients:** Set the recipient in the call to `alert.dispatch_digest()` in [`main.py`](main.py).

## Notes

- The LLM-based insight generation requires a valid Groq API key.
- Email dispatch uses Gmail SMTP; for other providers, adjust settings in [`alert.py`](alert.py).

## License

This project is for educational and demonstration purposes.
