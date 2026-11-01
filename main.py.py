import streamlit as st
import requests
import pandas as pd
import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier

@st.cache_resource
def load_ml_model():
    np.random.seed(42)
    X = np.random.normal(loc=[50, 100, 25], scale=[15, 20, 4], size=(1000, 3))
    y = (X[:, 0]*0.2 + X[:, 1]*0.6 + X[:, 2]*0.4 > 85).astype(int)
    model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    model.fit(X, y)
    return model

model = load_ml_model()

@st.cache_data(ttl=3600)
def fetch_patient_directory():
    url = "http://hapi.fhir.org/baseR4/Patient?_count=50&_sort=-_lastUpdated"
    try:
        response = requests.get(url)
        data = response.json()
        patients = []
        if 'entry' in data:
            for entry in data['entry']:
                p = entry['resource']
                pid = p.get('id', 'N/A')
                names = p.get('name', [{}])[0]
                fname = names.get('given', [''])[0]
                lname = names.get('family', '')
                gender = p.get('gender', '-').capitalize()
                birth = p.get('birthDate', '-')
                if fname and lname:
                    patients.append({"ID": pid, "Επώνυμο": lname, "Όνομα": fname, "Φύλο": gender, "Ημ. Γέννησης": birth, "Raw": p})
        return patients
    except:
        return []

st.set_page_config(page_title="Γενικό Νοσοκομείο - EHR", page_icon="🏥", layout="wide")
patients_data = fetch_patient_directory()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063206.png", width=80)
    st.header("🏥 Κεντρικό Σύστημα Υγείας")
    st.write("Συνδεδεμένο στο δίκτυο HL7 FHIR")
    st.divider()
    if patients_data:
        patient_options = {f"{p['Επώνυμο']} {p['Όνομα']} (ID: {p['ID']})": p for p in patients_data}
        selected_patient = st.selectbox("🔍 Αναζήτηση Ασθενούς", ["-- Προβολή Μητρώου --"] + list(patient_options.keys()))
    else:
        st.error("Σφάλμα σύνδεσης με FHIR.")
        selected_patient = "-- Προβολή Μητρώου --"

if selected_patient == "-- Προβολή Μητρώου --":
    st.title("📂 Κεντρικό Μητρώο Ασθενών")
    st.write("Λίστα πρόσφατα ενημερωμένων φακέλων από το διαλειτουργικό δίκτυο. Επιλέξτε ασθενή από την αριστερή μπάρα για λεπτομέρειες.")
    if patients_data:
        df = pd.DataFrame(patients_data).drop(columns=["Raw"])
        st.dataframe(df, use_container_width=True, hide_index=True)
else:
    p = patient_options[selected_patient]
    st.title(f"⚕️ Ιατρικός Φάκελος: {p['Επώνυμο']} {p['Όνομα']}")
    random.seed(p['ID']) 
    age = random.randint(30, 80)
    glucose = random.randint(70, 160)
    bmi = round(random.uniform(18.5, 35.0), 1)

    tab1, tab2, tab3 = st.tabs(["📄 Κλινική Εικόνα", "🧠 AI CDSS (Διαβήτης)", "💻 JSON (FHIR)"])
    with tab1:
        st.subheader("Δημογραφικά & Βιομετρικά Στοιχεία")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Σύστημα ID", p['ID'])
        col2.metric("Φύλο", p['Φύλο'])
        col3.metric("Ημ. Γέννησης", p['Ημ. Γέννησης'])
        col4.metric("Ηλικία", f"{age} ετών")
        st.divider()
        st.subheader("Πρόσφατες Εργαστηριακές Μετρήσεις")
        c1, c2, c3 = st.columns(3)
        c1.metric("Σάκχαρο Αίματος (Fasting)", f"{glucose} mg/dL")
        c2.metric("Δείκτης Μάζας Σώματος", bmi)
        c3.metric("Αρτηριακή Πίεση", f"{random.randint(110,135)}/80 mmHg")

    with tab2:
        st.subheader("Σύστημα Υποστήριξης Κλινικών Αποφάσεων (CDSS)")
        st.write("Αξιολόγηση κινδύνου βάσει αλγορίθμου Random Forest.")
        input_data = np.array([[age, glucose, bmi]])
        risk_prob = model.predict_proba(input_data)[0][1] * 100
        st.progress(int(risk_prob), text=f"Πιθανότητα Εμφάνισης Διαβήτη: {risk_prob:.1f}%")
        if risk_prob > 60:
            st.error("⚠️ Υψηλός κίνδυνος. Απαιτείται παραπομπή σε ενδοκρινολόγο.")
        elif risk_prob > 30:
            st.warning("⚡ Μέτριος κίνδυνος. Συστήνεται αλλαγή διατροφής και άσκηση.")
        else:
            st.success("✅ Χαμηλός κίνδυνος. Διατήρηση τρέχουσας κλινικής εικόνας.")
            
    with tab3:
        st.write("Ακατέργαστο payload από τον server HAPI FHIR:")
        st.json(p['Raw'])
