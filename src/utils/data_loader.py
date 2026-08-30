#imports
import pandas as pd
from src.models.patient import Patient
from src.models.medical_record import MedicalRecord


#a factory function that creates a patient object from the csv (one row)
def create_patient(row):
    return Patient(
        row["patient_id"],
        row["name"],
        row["age"],
        row["gender"],
        row["diagnosis"],
        row["diagnosis_date"])


#a factory function that creates a medical record object from one row in the csv.
def create_medical_record(row):
    return MedicalRecord(
        row["blood_glucose"],
        row["blood_pressure_systolic"],
        row["blood_pressure_diastolic"],
        row["bmi"],
        row["hba1c"],
        row["cholesterol"],
        row["last_visit"],
        row["is_smoker"],
        row["medication_count"],
        row["risk_score"])

#we chose to see this project as a program that could have been used in reality (In theory ofc)
#And that is the reason that the system gets all the patients in the data.
#Beacuse in reality, if a patient comes to a clinic and his medical record does not exist in the system
#because of a typing mistake, it's a serious problem.
#And that is the reason that the system tries to keep as many patients as possible after cleaning the data.
#load all the info from the csv.
def load_patients_data(file_path, clinic):
    df = pd.read_csv(file_path)

    #if one of the following values is missing, drop the entire line.
    df = df.dropna(subset=["patient_id", "name", "age", "gender", "diagnosis"])

    #checks that age, blood_glucose, bmi, risk_score, and hba1c are numeric. if not, replace with nan.    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["blood_glucose"] = pd.to_numeric(df["blood_glucose"], errors="coerce")
    df["bmi"] = pd.to_numeric(df["bmi"], errors="coerce")
    df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce")
    df["hba1c"] = pd.to_numeric(df["hba1c"], errors="coerce")

    #fill the nan values with the median in the columns that must have numeric values.
    df["age"] = df["age"].fillna(df["age"].median()).astype(int)
    df["blood_glucose"] = df["blood_glucose"].fillna(df["blood_glucose"].median())
    df["bmi"] = df["bmi"].fillna(df["bmi"].median())
    df["risk_score"] = df["risk_score"].fillna(df["risk_score"].median())

    #replace date columns with datetime. if the date is invalid, replace with nan.
    df["diagnosis_date"] = pd.to_datetime(df["diagnosis_date"], format="mixed", errors="coerce")
    df["last_visit"] = pd.to_datetime(df["last_visit"], format="mixed", errors="coerce")

    #if one of the important dates is invalid, drop the entire line.
    df = df.dropna(subset=["diagnosis_date", "last_visit"])

    #clean gender values so values like "m", "f", "Male", "Female" or spaces will not be removed.
    #I did this because I realized that when it was more simple, there were 3 missing patients.
    df["gender"] = df["gender"].astype(str).str.strip().str.upper()

    df["gender"] = df["gender"].replace({
        "MALE": "M",
        "FEMALE": "F"
    })

    #check that the gender is either M (male) or F (female).
    invalid_gender = df[~df["gender"].isin(["M", "F"])]
    if not invalid_gender.empty:
        print("Invalid gender values found:")
        print(invalid_gender[["patient_id", "name", "gender"]])
    df = df[df["gender"].isin(["M", "F"])]

    #checks that these values are numeric. if not, replace with nan.
    df["blood_pressure_systolic"] = pd.to_numeric(df["blood_pressure_systolic"], errors="coerce")
    df["blood_pressure_diastolic"] = pd.to_numeric(df["blood_pressure_diastolic"], errors="coerce")
    df["cholesterol"] = pd.to_numeric(df["cholesterol"], errors="coerce")
    df["medication_count"] = pd.to_numeric(df["medication_count"], errors="coerce")

    #replace the nan values with the median of each column. in medication_count replace nan with 0.
    df["blood_pressure_systolic"] = df["blood_pressure_systolic"].fillna(df["blood_pressure_systolic"].median()).astype(int)
    df["blood_pressure_diastolic"] = df["blood_pressure_diastolic"].fillna(df["blood_pressure_diastolic"].median()).astype(int)
    df["cholesterol"] = df["cholesterol"].fillna(df["cholesterol"].median()).astype(int)
    df["medication_count"] = df["medication_count"].fillna(0).astype(int)

    #if these values are negative, replace by absolute value.
    df["medication_count"] = df["medication_count"].abs()
    df["risk_score"] = df["risk_score"].abs()

    #check that the value of each diagnosis is one of the following diseases.
    df = df[df["diagnosis"].isin(["Diabetes", "HeartDisease", "Hypertension"])]

    #convert the text values "True" and "False" into boolean values.
    df["is_smoker"] = df["is_smoker"].replace({
        "True": True,
        "False": False})

    #replace nan with False.
    df["is_smoker"] = df["is_smoker"].fillna(False)

    #now our purpose is to take each patient and add him to our clinic.
    #we use factory functions to create Patient and MedicalRecord objects.
    #then we use the add_patient method to store the patient and the medical record by the same patient ID.
    for index, row in df.iterrows():
        try:
            patient = create_patient(row)
            medical_record = create_medical_record(row)

            clinic.add_patient(patient, medical_record)

        #if something went wrong, skip the row and give alert.
        except ValueError as error:
            print(f"Skipping row {index}: {error}")

    #return the clinic object after all valid patients were added.
    return clinic










