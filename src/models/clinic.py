class Clinic:
    """
    This class represents a clinic.
    The class uses the Singleton design pattern,
    so only one clinic object can be created.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, clinic_name):
        """
        Clinic constructor.

        Args:
            clinic_name (str): the name of the clinic.
        """
        if not hasattr(self, "initialized"):
            self.clinic_name = clinic_name
            self.patients = {}
            self.medical_records = {}
            self.initialized = True
    #a method that adds a patient object and its medical record object to the clinic by patient ID.
    def add_patient(self,patient, medical_record):
        self.patients[patient.patient_id] = patient
        self.medical_records[patient.patient_id] = medical_record
    #a method that enables searching a specific patient by his ID
    def get_patient_by_id(self,patient_id):
        if patient_id in self.patients:
            return self.patients[patient_id]
        else:
            return None
    # a method that enables searching a specific medical record by the patient's ID
    def get_medical_record(self, patient_id):
        if patient_id in self.medical_records:
            return self.medical_records[patient_id]
        else:
            return None
    #a method that returns a list of all high risk patients.
    def get_high_risk_patients(self):
        high_risk_patients = []
        for patient_id, record in self.medical_records.items():
            if record.is_high_risk():
                high_risk_patients.append(self.patients[patient_id])
        return high_risk_patients
    #a method that returns a list of all the patients in this clinic.
    def get_all_patients(self):
        return list(self.patients.values())



