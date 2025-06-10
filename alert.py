from typing import List, Dict
import pandas as pd
from email.message import EmailMessage
import smtplib
import os

class AlertInsightDispatcherAgent:
    def __init__(self, sender_email: str, app_password: str, output_file: str = "daily_status_log.csv"):
        self.sender_email = sender_email
        self.app_password = app_password
        self.output_file = output_file

        # Create the file with headers if it doesn't exist
        if not os.path.exists(self.output_file):
            pd.DataFrame(columns=["Date", "CM2%", "Color Code", "Alert Sent", "Insight"]).to_csv(self.output_file, index=False)

    def send_email(self, recipient: str, subject: str, body: str):
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = recipient

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(self.sender_email, self.app_password)
                smtp.send_message(msg)
                print(f"✅ Email sent to {recipient} successfully!")

        except Exception as e:
            print(f"❌ Failed to send email")

    def update_local_sheet(self, alerts: list, insights: dict):
        existing_df = pd.read_csv(self.output_file)

        new_rows = []
        for alert in alerts:
            date = alert["Day"]
            cm2 = alert["CM2%"]
            color = alert["Color Code"]
            insight = insights.get(date, "No anomalies.")
            new_rows.append({
                "Color Code": color,
                "Date": date,
                "CM2%": cm2,
                "Alert Sent": "✅",
                "Insight": insight
            })

        updated_df = pd.concat([existing_df, pd.DataFrame(new_rows)], ignore_index=True)
        updated_df.to_csv(self.output_file, index=False)

    def dispatch_digest(self, insights: Dict[str, str], alerts: List[Dict], recipient: str):
        digest_body = "📬 Daily Digest Report\n-------------------------\n"
        for alert, (day, insight) in zip(alerts,insights.items()):
            digest_body += f"{alert['Color Code']} {alert['Day']}: CM2 = {alert['CM2%']}%\n"
            digest_body += "\n🔍 Insights:\n"
            digest_body += f"{insight}\n"
            break
        digest_body += "\nThank you for your attention!"

        # Send email
        print(digest_body)
        self.send_email(recipient, "Daily FC P&L Digest Report", digest_body)

        # Update local sheet
        self.update_local_sheet(alerts, insights)