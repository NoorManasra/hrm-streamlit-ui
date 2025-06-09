import streamlit as st
import requests

st.title("📂 Human Rights Case Management")

# Fetch cases from FastAPI
st.header("🔍 View Cases")
response = requests.get("https://hrm-streamlit-ui.onrender.com/cases/")
if response.status_code == 200:
    cases = response.json()
    for case in cases:
        with st.expander(case["title"]):
            st.write("📅 Date of Incident:", case["date_occurred"])
            st.write("📍 Location:", case["location"]["country"], "-", case["location"].get("region", ""))
            st.write("🚨 Violation Type(s):", ", ".join(case["violation_types"]))
            st.write("📝 Description:", case["description"])
else:
    st.error("Failed to fetch cases from the server.")

# Add a new case (simple example)
st.header("➕ Add a New Case")
if st.checkbox("Show Form"):
    title = st.text_input("Title")
    description = st.text_area("Description")
    if st.button("Submit"):
        payload = {
            "case_id": "ID-001",  # Temporary, replace with actual logic later
            "title": title,
            "description": description,
            "violation_types": ["arbitrary detention"],
            "status": "open",
            "location": {
                "country": "Palestine",
                "region": "West Bank",
                "coordinates": {"type": "Point", "coordinates": [35.2, 31.9]}
            },
            "date_occurred": "2024-06-01",
            "date_reported": "2024-06-02"
        }
        res = requests.post("https://your-fastapi-app.onrender.com/cases/", json=payload)
        if res.status_code == 200:
            st.success("Case added successfully.")
        else:
            st.error("Failed to add the case.")
