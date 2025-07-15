
import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="LogSleuth", layout="wide")

st.title("🔍 LogSleuth Security Analyst Dashboard")
st.markdown("Upload log files, detect security events, and map them to MITRE ATT&CK techniques.")

uploaded_file = st.file_uploader("Upload a log file (.log or .txt or .csv)", type=["log", "txt", "csv"])

def parse_logs(file_content):
    lines = file_content.decode("utf-8").splitlines()
    parsed = []
    for line in lines:
        entry = {
            "timestamp": re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", line),
            "message": line
        }
        parsed.append({
            "timestamp": entry["timestamp"].group() if entry["timestamp"] else "",
            "message": entry["message"]
        })
    return pd.DataFrame(parsed)

def detect_threats(df):
    alerts = []
    for _, row in df.iterrows():
        msg = row['message'].lower()
        if "failed password" in msg or "authentication failure" in msg:
            alerts.append({
                "type": "Brute Force Attempt",
                "technique": "T1110",
                "log": row["message"]
            })
        if "sudo" in msg and "denied" in msg:
            alerts.append({
                "type": "Privilege Escalation Attempt",
                "technique": "T1068",
                "log": row["message"]
            })
    return pd.DataFrame(alerts)

if uploaded_file:
    content = uploaded_file.read()
    logs_df = parse_logs(content)
    st.subheader("📜 Parsed Logs")
    st.dataframe(logs_df, use_container_width=True)

    alerts_df = detect_threats(logs_df)
    if not alerts_df.empty:
        st.subheader("⚠️ Detected Threats")
        st.dataframe(alerts_df, use_container_width=True)

        st.subheader("🎯 MITRE ATT&CK Techniques Detected")
        st.write(alerts_df['technique'].unique().tolist())
    else:
        st.success("✅ No threats detected in the uploaded logs.")
