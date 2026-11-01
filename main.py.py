import requests

url = "http://hapi.fhir.org/baseR4/Patient?_count=1"
response = requests.get(url)
data = response.json()

# Ελέγχουμε αν ο server επέστρεψε δεδομένα (το FHIR τα ονομάζει 'entry')
if 'entry' in data:
    # Απομονώνουμε τον ιατρικό φάκελο του πρώτου ασθενούς
    patient = data['entry'][0]['resource']
    
    # Εξαγωγή του ID
    patient_id = patient.get('id', 'Δεν βρέθηκε')
    
    # Εξαγωγή του Ονόματος (το FHIR αποθηκεύει τα ονόματα σε λίστες)
    name_list = patient.get('name', [{}])[0]
    first_name = name_list.get('given', ['Άγνωστο'])[0]
    last_name = name_list.get('family', 'Άγνωστο')
    
    # Εξαγωγή φύλου
    gender = patient.get('gender', 'Δεν δηλώθηκε')

    print("\n--- ΚΑΡΤΕΛΑ ΑΣΘΕΝΟΥΣ ---")
    print(f"ID: {patient_id}")
    print(f"Όνομα: {first_name}")
    print(f"Επώνυμο: {last_name}")
    print(f"Φύλο: {gender}\n")
else:
    print("Δεν βρέθηκαν δεδομένα.")