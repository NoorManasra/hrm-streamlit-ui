import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime
from fpdf import FPDF

API_BASE = "https://hrm-streamlit-ui-6.onrender.com"

st.set_page_config(page_title="Human Rights Violations Dashboard", layout="wide")
st.title("Human Rights Violations Dashboard")

# --- Sidebar Filters ---
st.sidebar.header("Filters")

start_date = st.sidebar.date_input("Start Date", value=datetime(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", value=datetime(2024, 12, 31))

start_date = datetime.combine(start_date, datetime.min.time())
end_date = datetime.combine(end_date, datetime.min.time())

# Fetch initial data without region/type filter to populate filter options
@st.cache_data(ttl=300)
def fetch_geodata(start=None, end=None, violation_type=None):
    params = {}
    if start:
        params["start_date"] = start.strftime("%Y-%m-%d")
    if end:
        params["end_date"] = end.strftime("%Y-%m-%d")
    if violation_type and violation_type != "All":
        params["violation_type"] = violation_type

    r = requests.get(f"{API_BASE}/analytics/geodata", params=params)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=300)
def fetch_violations(start=None, end=None, region=None):
    params = {}
    if start:
        params["start_date"] = start.strftime("%Y-%m-%d")
    if end:
        params["end_date"] = end.strftime("%Y-%m-%d")
    if region and region != "All":
        params["region"] = region

    r = requests.get(f"{API_BASE}/analytics/violations", params=params)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=300)
def fetch_timeline(start=None, end=None, region=None, violation_type=None):
    params = {}
    if start:
        params["start_date"] = start.strftime("%Y-%m-%d")
    if end:
        params["end_date"] = end.strftime("%Y-%m-%d")
    if region and region != "All":
        params["region"] = region
    if violation_type and violation_type != "All":
        params["violation_type"] = violation_type

    r = requests.get(f"{API_BASE}/analytics/timeline", params=params)
    r.raise_for_status()
    return r.json()

# جلب البيانات بدون فلترة للفلتر
geodata = fetch_geodata(start_date, end_date)
df_geo = pd.DataFrame(geodata)

violations_data = fetch_violations(start_date, end_date)
df_violations = pd.DataFrame(violations_data)

regions = df_geo['region'].dropna().unique().tolist() if not df_geo.empty else []
violation_types = df_violations['violation_type'].dropna().unique().tolist() if not df_violations.empty else []

selected_region = st.sidebar.selectbox("Region", ["All"] + regions)
selected_violation_type = st.sidebar.selectbox("Violation Type", ["All"] + violation_types)

# جلب البيانات المفلترة بناءً على اختيار المستخدم
violations_data = fetch_violations(start_date, end_date, selected_region)
df_violations = pd.DataFrame(violations_data)

timeline_data = fetch_timeline(start_date, end_date, selected_region, selected_violation_type)
df_timeline = pd.DataFrame(timeline_data)

geodata = fetch_geodata(start_date, end_date, selected_violation_type)
df_geo = pd.DataFrame(geodata)

# --- Visualization ---
# (تابع عرض الرسوم البيانية كما في كودك الأصلي)


# --- Visualization ---
st.subheader("Violations by Type")
fig_bar = px.bar(df_violations, x='violation_type', y='count', labels={"violation_type":"Violation Type", "count":"Number of Cases"})
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Violations by Type (Pie Chart)")
if not df_violations.empty:
    fig_pie = px.pie(df_violations, names='violation_type', values='count', title="Violations by Type")
    st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("Reported Cases Over Time")
if not df_timeline.empty:
    fig_line = px.line(df_timeline, x='date', y='count', labels={"date":"Date", "count":"Number of Cases"})
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.write("No timeline data for the selected filters.")

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
        labels={"count": "Number of Cases"}
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.write("No geographic data available.")

# --- Export buttons ---
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

    pdf.ln(10)
    pdf.cell(0, 10, "Violations by Type:", ln=True)
    for _, row in violations_df.iterrows():
        pdf.cell(0, 8, f"- {row['violation_type']}: {row['count']}", ln=True)

    pdf.ln(10)
    pdf.cell(0, 10, "Cases Over Time:", ln=True)
    for _, row in timeline_df.iterrows():
        date_str = row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], pd.Timestamp) else str(row['date'])
        pdf.cell(0, 8, f"- {date_str}: {row['count']}", ln=True)

    pdf.ln(10)
    pdf.cell(0, 10, "Cases by Location:", ln=True)
    for _, row in geo_df.iterrows():
        region = row['region'] if row['region'] else "N/A"
        pdf.cell(0, 8, f"- {row['country']} / {region}: {row['count']}", ln=True)

    pdf_bytes = BytesIO(pdf.output(dest='S').encode('latin1'))
    pdf_bytes.seek(0)
    return pdf_bytes

st.sidebar.subheader("Download Reports")
excel_file = to_excel(df_violations)
st.sidebar.download_button("Download Violations as Excel", data=excel_file, file_name="violations_report.xlsx")

pdf_file = create_pdf_report(df_violations, df_timeline, df_geo)
st.sidebar.download_button("Download Full Report as PDF", data=pdf_file, file_name="full_violations_report.pdf")

