import streamlit as st
import requests
from datetime import date

API_URL = "https://hrm-streamlit-ui.onrender.com"  

st.set_page_config(page_title="Case Management", layout="wide")
st.title("📂 Human Rights Case Management System")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📋 View All Cases", 
    "🔍 View Single Case", 
    "➕ Add Case", 
    "✏️ Edit Case", 
    "🔄 Update Status", 
    "🗑️ Archive Case", 
    "📈 Status History", 
    "📤 Upload Files"
])
with tab1:
    st.subheader("📋 All Cases")
    res = requests.get(f"{API_URL}/cases/")
    if res.status_code == 200:
        cases = res.json()
        for case in cases:
            with st.expander(case["title"]):
                st.write(case)
    else:
        st.error("❌ Failed to load cases")


with tab2:
    st.subheader("🔍 Retrieve Case by ID")
    case_id = st.text_input("Enter Case ID")
    if st.button("Get Case"):
        res = requests.get(f"{API_URL}/cases/{case_id}")
        if res.status_code == 200:
            st.json(res.json())
        else:
            st.error(res.json()["detail"])
with tab3:
    st.subheader("➕ Add New Case")
    with st.form("add_case_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        case_id = st.text_input("Case ID")
        status = st.selectbox("Status", ["open", "closed"])
        country = st.text_input("Country")
        region = st.text_input("Region")
        lat = st.number_input("Latitude", value=31.9)
        lon = st.number_input("Longitude", value=35.2)
        date_occurred = st.date_input("Date Occurred", value=date.today())
        date_reported = st.date_input("Date Reported", value=date.today())
        submitted = st.form_submit_button("Submit")

        if submitted:
            payload = {
                "case_id": case_id,
                "title": title,
                "description": description,
                "violation_types": ["arbitrary detention"],
                "status": status,
                "location": {
                    "country": country,
                    "region": region,
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    }
                },
                "date_occurred": str(date_occurred),
                "date_reported": str(date_reported)
            }
            res = requests.post(f"{API_URL}/cases/", json=payload)
            if res.status_code == 200:
                st.success("✅ Case added successfully")
            else:
                st.error("❌ Failed to add case")

with tab4:
    st.subheader("✏️ Edit Case")
    case_id = st.text_input("Case ID to Edit")
    if st.button("Load Case"):
        res = requests.get(f"{API_URL}/cases/{case_id}")
        if res.status_code == 200:
            case = res.json()
            new_title = st.text_input("Title", value=case["title"])
            new_desc = st.text_area("Description", value=case["description"])
            new_status = st.text_input("Status", value=case["status"])
            if st.button("Update Case"):
                case["title"] = new_title
                case["description"] = new_desc
                case["status"] = new_status
                res = requests.put(f"{API_URL}/cases/{case_id}", json=case)
                if res.status_code == 200:
                    st.success("✅ Case updated")
                else:
                    st.error("❌ Update failed")
with tab5:
    st.subheader("🔄 Update Case Status")
    case_id = st.text_input("Case ID for status update")
    new_status = st.text_input("New Status")
    if st.button("Update Status"):
        res = requests.patch(f"{API_URL}/cases/{case_id}/status", json={"new_status": new_status})
        if res.status_code == 200:
            st.success("✅ Status updated")
        else:
            st.error(res.json()["detail"])
with tab6:
    st.subheader("🗑️ Archive Case")
    case_id = st.text_input("Case ID to archive")
    if st.button("Archive"):
        res = requests.delete(f"{API_URL}/cases/{case_id}")
        if res.status_code == 200:
            st.success("✅ Case archived")
        else:
            st.error(res.json()["detail"])
with tab7:
    st.subheader("📈 View Status History")
    case_id = st.text_input("Case ID for status history")
    if st.button("Load History"):
        res = requests.get(f"{API_URL}/cases/{case_id}/status-history")
        if res.status_code == 200:
            history = res.json()
            for record in history:
                st.write(record)
        else:
            st.error(res.json()["detail"])
with tab8:
    st.subheader("📤 Upload Files")
    case_id = st.text_input("Case ID to upload to")
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
    if st.button("Upload"):
        files = [("files", (f.name, f.getvalue())) for f in uploaded_files]
        res = requests.post(f"{API_URL}/cases/{case_id}/upload", files=files)
        if res.status_code == 200:
            st.success("✅ Files uploaded")
        else:
            st.error("❌ Upload failed")
