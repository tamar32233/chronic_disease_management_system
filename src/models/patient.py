#Submitted by: Tamar Levitan and Ayelet Yehezkel
#In this project we created 3 classes.
#the first one is patient- it contains all the basic information of a patient,
#including his diagnosis and the date he was diagnosed. (part of basic info.)
#the second class is medical record- it contains all the checks and tests of the patient.
#The last class is Clinic. It connects each patient object with its medical record by patient ID.
#Singleton was used in the Clinic class, so only one clinic object can be created.
#more files:
#data_loader - cleans the data, creates Patient and MedicalRecord objects, and adds them into the clinic.
#Factory functions were used there to create objects from each CSV row.
#Statistics - all the requested analysis
#Visualizations - all the requested graphs.
#main - runs the system.


class Patient:
    """
    this class defines a patient
    """

    def __init__(self, patient_id, name, age, gender, diagnosis, diagnosis_date):
        """
         Patient constructor
         Args:
             patient_id (str): a string of letters and numbers which are the patient's ID
             name(str): the name of the patient
             age(int): a number that represents the patient's age.
             gender(str): M for male and F for female
             diagnosis(str): Diabetes or HeartDisease or Hypertension
             diagnosis_date(str): when was the diagnosis determined.
         """
        #some validity checks
        if not isinstance(age, int):
            raise ValueError("Invalid Age.")
        if age < 0:
            raise ValueError("Invalid Age.")
        if diagnosis not in ["Diabetes", "HeartDisease", "Hypertension"]:
            raise ValueError("Invalid Diagnosis.")
        if gender not in ["M", "F"]:
            raise ValueError("Invalid Gender.")

        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.gender = gender
        self.diagnosis = diagnosis
        self.diagnosis_date = diagnosis_date

    #a method that returns the profile of the patient
    def get_profile(self):
        return (f"Name: {self.name}, ID: {self.patient_id}, "
                f"age: {self.age}, gender: {self.gender}, "
                f"diagnosis: {self.diagnosis}, diagnosis_date: {self.diagnosis_date}")
    #a method that returns whether the patient is a senior (above 65) or not.
    def is_senior(self):
        return self.age > 65
    #a method that returns the age group of the patient. (4 options)
    def age_group(self):
        if self.age <= 40:
            return "0-40"
        elif self.age <= 60:
            return "41-60"
        elif self.age <= 80:
            return "61-80"
        else:
            return "81+"
    #a method that returns a dictionary of the values in the class.
    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "diagnosis": self.diagnosis,
            "diagnosis_date": self.diagnosis_date
        }

