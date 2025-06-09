import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime
from fpdf import FPDF

API_BASE = "https://hrm-streamlit-ui-1.onrender.com"  # غيّر للعنوان الصحيح للAPI عندك

st.set_page_config(page_title="Human Rights Violations Dashboard", layout="wide")

st.title("Human Rights Violations Dashboard")

# --- فلترة التاريخ ---
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date (optional)", value=None)
with col2:
    end_date = st.date_input("End date (optional)", value=None)

# --- تحميل بيانات الانتهاكات ---
@st.cache_data(ttl=300)
def fetch_violations():
    r = requests.get(f"{API_BASE}/violations")
    r.raise_for_status()
    return r.json()

# --- تحميل بيانات التايم لاين ---
@st.cache_data(ttl=300)
def fetch_timeline(start=None, end=None):
    params = {}
    if start:
        params["start_date"] = start.strftime("%Y-%m-%d")
    if end:
        params["end_date"] = end.strftime("%Y-%m-%d")
    r = requests.get(f"{API_BASE}/timeline", params=params)
    r.raise_for_status()
    return r.json()

# --- تحميل بيانات الجغرافيا ---
@st.cache_data(ttl=300)
def fetch_geodata():
    r = requests.get(f"{API_BASE}/geodata")
    r.raise_for_status()
    return r.json()

# جلب البيانات
violations_data = fetch_violations()
timeline_data = fetch_timeline(start_date, end_date)
geodata = fetch_geodata()

# تحويل للـ DataFrame
df_violations = pd.DataFrame(violations_data)
df_timeline = pd.DataFrame(timeline_data)
if not df_timeline.empty:
    df_timeline['date'] = pd.to_datetime(df_timeline['date'])
df_geo = pd.DataFrame(geodata)

# --- عرض المخططات ---
st.subheader("Violations by Type")
fig_violations = px.bar(df_violations, x='violation_type', y='count', labels={"violation_type":"Violation Type", "count":"Number of Cases"})
st.plotly_chart(fig_violations, use_container_width=True)

st.subheader("Reported Cases Over Time")
if not df_timeline.empty:
    fig_timeline = px.line(df_timeline, x='date', y='count', labels={"date":"Date", "count":"Number of Cases"})
    st.plotly_chart(fig_timeline, use_container_width=True)
else:
    st.write("No timeline data for the selected date range.")

st.subheader("Violations by Location")
if not df_geo.empty:
    fig_map = px.scatter_mapbox(
        df_geo,
        lat=df_geo['coordinates'].apply(lambda c: c[1]),
        lon=df_geo['coordinates'].apply(lambda c: c[0]),
        size='count',
        color='country',
        hover_name='region',
        zoom=3,
        mapbox_style="open-street-map",
        labels={"count": "Number of Cases"},
        title="Violations by Location"
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.write("No geographic data available.")

# --- دوال التصدير ---
def to_excel(df: pd.DataFrame) -> BytesIO:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

def create_pdf_report(violations_df, timeline_df, geo_df) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Human Rights Violations Report", ln=True, align="C")

    # Violations summary
    pdf.ln(10)
    pdf.cell(0, 10, "Violations by Type:", ln=True)
    for _, row in violations_df.iterrows():
        pdf.cell(0, 8, f"- {row['violation_type']}: {row['count']}", ln=True)

    # Timeline summary
    pdf.ln(10)
    pdf.cell(0, 10, "Cases Over Time:", ln=True)
    for _, row in timeline_df.iterrows():
        date_str = row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], pd.Timestamp) else str(row['date'])
        pdf.cell(0, 8, f"- {date_str}: {row['count']}", ln=True)

    # Geo summary
    pdf.ln(10)
    pdf.cell(0, 10, "Cases by Location:", ln=True)
    for _, row in geo_df.iterrows():
        region = row['region'] if row['region'] else "N/A"
        pdf.cell(0, 8, f"- {row['country']} / {region}: {row['count']}", ln=True)

    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

st.sidebar.header("Export Data")

export_format = st.sidebar.selectbox("Select export format", ["Excel", "PDF"])

if st.sidebar.button("Export current data"):
    if export_format == "Excel":
        combined_df = pd.concat([
            df_violations.assign(section="Violations"),
            df_timeline.assign(section="Timeline"),
            df_geo.assign(section="Geo")
        ], ignore_index=True, sort=False)
        excel_data = to_excel(combined_df)
        st.sidebar.download_button("Download Excel file", data=excel_data, file_name="hr_violations_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        pdf_data = create_pdf_report(df_violations, df_timeline, df_geo)
        st.sidebar.download_button("Download PDF file", data=pdf_data, file_name="hr_violations_report.pdf", mime="application/pdf")

