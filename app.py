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
        if cases:
            for case in cases:
                with st.expander(f"📌 {case['title']} (ID: {case['case_id']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Description:** {case['description']}")
                        st.markdown(f"**Status:** {case['status']}")
                        st.markdown(f"**Priority:** {case['priority']}")
                        st.markdown(f"**Date Occurred:** {case['date_occurred']}")
                        st.markdown(f"**Date Reported:** {case['date_reported']}")

                    with col2:
                        st.markdown(f"**Country:** {case['location']['country']}")
                        st.markdown(f"**Region:** {case['location']['region']}")
                        st.markdown(f"**Coordinates:** {case['location']['coordinates']['coordinates']}")
                        st.markdown(f"**Violation Types:** {', '.join(case['violation_types'])}")
                    
                    # Optionally show victims, perpetrators, evidence
                    st.markdown("### 👥 Victims")
                    if case['victims']:
                        st.write(", ".join(case['victims']))
                    else:
                        st.write("No victims listed.")

                    st.markdown("### 🚨 Perpetrators")
                    if case['perpetrators']:
                        for p in case['perpetrators']:
                            st.markdown(f"- **Name:** {p['name']} | **Type:** {p['type']}")
                    else:
                        st.write("No perpetrators listed.")

                    st.markdown("### 📄 Evidence")
                    if case['evidence']:
                        for ev in case['evidence']:
                            st.markdown(f"- **Type:** {ev['type']} | [Link]({ev['url']}) | **Date Captured:** {ev.get('date_captured', 'N/A')}")
                    else:
                        st.write("No evidence listed.")
        else:
            st.info("No cases found.")
    else:
        st.error("❌ Failed to load cases")


with tab2:
    st.subheader("🔍 Retrieve Case by ID")
    case_id = st.text_input("Enter Case ID")
    if st.button("Get Case"):
        res = requests.get(f"{API_URL}/cases/{case_id}")
        if res.status_code == 200:
            case = res.json()
            with st.expander(f"📌 {case['title']} (ID: {case['case_id']})", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Description:** {case['description']}")
                    st.markdown(f"**Status:** {case['status']}")
                    st.markdown(f"**Priority:** {case['priority']}")
                    st.markdown(f"**Date Occurred:** {case['date_occurred']}")
                    st.markdown(f"**Date Reported:** {case['date_reported']}")

                with col2:
                    st.markdown(f"**Country:** {case['location']['country']}")
                    st.markdown(f"**Region:** {case['location']['region']}")
                    st.markdown(f"**Coordinates:** {case['location']['coordinates']['coordinates']}")
                    st.markdown(f"**Violation Types:** {', '.join(case['violation_types'])}")

                # Victims
                st.markdown("### 👥 Victims")
                if case['victims']:
                    st.write(", ".join(case['victims']))
                else:
                    st.write("No victims listed.")

                # Perpetrators
                st.markdown("### 🚨 Perpetrators")
                if case['perpetrators']:
                    for p in case['perpetrators']:
                        st.markdown(f"- **Name:** {p['name']} | **Type:** {p['type']}")
                else:
                    st.write("No perpetrators listed.")

                # Evidence
                st.markdown("### 📄 Evidence")
                if case['evidence']:
                    for ev in case['evidence']:
                        st.markdown(f"- **Type:** {ev['type']} | [Link]({ev['url']}) | **Date Captured:** {ev.get('date_captured', 'N/A')}")
                else:
                    st.write("No evidence listed.")

        else:
            st.error(res.json()["detail"])

with tab3:
    st.subheader("➕ Add New Case")
    with st.form("add_case_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        case_id = st.text_input("Case ID")
        status = st.selectbox("Status", ["open", "closed"])
        priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"], index=1)
        
        # Location
        country = st.text_input("Country")
        region = st.text_input("Region")
        lat = st.number_input("Latitude", value=31.9)
        lon = st.number_input("Longitude", value=35.2)

        # Dates
        date_occurred = st.date_input("Date Occurred", value=date.today())
        date_reported = st.date_input("Date Reported", value=date.today())

        # Violation types
        violation_types = st.multiselect(
            "Violation Types",
            ["arbitrary detention", "torture", "forced disappearance", "extrajudicial killing"]
        )

        # Victims
        victims_input = st.text_area("Victim IDs (comma-separated)")
        victims = [v.strip() for v in victims_input.split(",")] if victims_input else []

        # Perpetrators
        st.markdown("### Perpetrators")
        perp_names = st.text_area("Names (comma-separated)")
        perp_types = st.text_area("Types (comma-separated, match order)")
        perpetrators = []
        if perp_names and perp_types:
            names = [n.strip() for n in perp_names.split(",")]
            types = [t.strip() for t in perp_types.split(",")]
            perpetrators = [{"name": n, "type": t} for n, t in zip(names, types)]

        # Evidence
        st.markdown("### Evidence")
        ev_types = st.text_area("Evidence Types (comma-separated)")
        ev_urls = st.text_area("Evidence URLs (comma-separated)")
        ev_descs = st.text_area("Evidence Descriptions (optional, comma-separated)")
        ev_dates = st.text_area("Evidence Capture Dates (YYYY-MM-DD, optional, comma-separated)")
        evidence = []
        if ev_types and ev_urls:
            types = [t.strip() for t in ev_types.split(",")]
            urls = [u.strip() for u in ev_urls.split(",")]
            descs = [d.strip() for d in ev_descs.split(",")] if ev_descs else ["" for _ in types]
            dates = [d.strip() for d in ev_dates.split(",")] if ev_dates else [None for _ in types]
            for i in range(len(types)):
                ev = {
                    "type": types[i],
                    "url": urls[i],
                    "description": descs[i] if i < len(descs) else "",
                    "date_captured": dates[i] if i < len(dates) and dates[i] else None
                }
                evidence.append(ev)

        submitted = st.form_submit_button("Submit")

        if submitted:
            payload = {
                "case_id": case_id,
                "title": title,
                "description": description,
                "violation_types": violation_types,
                "status": status,
                "priority": priority,
                "location": {
                    "country": country,
                    "region": region,
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    }
                },
                "date_occurred": str(date_occurred),
                "date_reported": str(date_reported),
                "victims": victims,
                "perpetrators": perpetrators,
                "evidence": evidence
            }

            res = requests.post(f"{API_URL}/cases/", json=payload)
            if res.status_code == 200:
                st.success("✅ Case added successfully")
            else:
                st.error(f"❌ Failed to add case\n{res.text}")


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
