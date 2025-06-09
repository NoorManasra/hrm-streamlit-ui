import streamlit as st
import requests

st.title("📂 Human Rights Case Management")

# جلب البيانات من FastAPI
st.header("🔍 عرض الحالات")
response = requests.get("https://hrm-streamlit-ui.onrender.com/cases/")
if response.status_code == 200:
    cases = response.json()
    for case in cases:
        with st.expander(case["title"]):
            st.write("📅 تاريخ الحدوث:", case["date_occurred"])
            st.write("📍 الموقع:", case["location"]["country"], "-", case["location"].get("region", ""))
            st.write("🚨 نوع الانتهاك:", ", ".join(case["violation_types"]))
            st.write("📝 الوصف:", case["description"])
else:
    st.error("فشل في جلب البيانات")

# إضافة حالة جديدة (مثال مبسط)
st.header("➕ إضافة حالة جديدة")
if st.checkbox("عرض النموذج"):
    title = st.text_input("العنوان")
    description = st.text_area("الوصف")
    if st.button("إرسال"):
        payload = {
            "case_id": "ID-001",  # مؤقتًا، عدله لاحقًا
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
            st.success("تمت إضافة الحالة بنجاح")
        else:
            st.error("فشل في إضافة الحالة")

