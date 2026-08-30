class MedicalRecord:
    """
    this class defines the medical record
    """

    def __init__(self, blood_glucose, blood_pressure_systolic, blood_pressure_diastolic,
                 bmi, hba1c, cholesterol, last_visit, is_smoker, medication_count, risk_score):
        """
         Medical record constructor
         Args:
             blood_glucose (float): a number that describes the glucose in the blood.
             blood_pressure_systolic(int): a number that describes the systolic blood pressure
             blood_pressure_diastolic(int):a number that describes the diastolic blood pressure
             bmi(float): body mass...
             hba1c(float or nan): sugared hemoglobin (relevant for diabetic mainly.)
             cholesterol(int): a number that describes the cholesterol.
             last_visit(str): the date of the last visit.
             is_smoker(bool): is the patient a smoker? (True or False)
             medication_count(int): number of medications that the patient takes.
             risk_score(float): a number that describes the risk score.

                 """
        #some validity checks:
        if not isinstance(blood_glucose, (int, float)):
            raise ValueError("Invalid blood_glucose.")
        if blood_glucose < 0:
            raise ValueError("Invalid blood_glucose.")
        if not isinstance(blood_pressure_systolic, int):
            raise ValueError("Invalid blood_pressure_systolic.")
        if not isinstance(blood_pressure_diastolic, int):
            raise ValueError("Invalid blood_pressure_diastolic.")
        if not isinstance(bmi, (int, float)):
            raise ValueError("Invalid bmi.")
        if bmi < 0:
            raise ValueError("Invalid bmi.")
        if not isinstance(cholesterol, int):
            raise ValueError("Invalid cholesterol.")
        if cholesterol < 0:
            raise ValueError("Invalid cholesterol.")
        if not isinstance(is_smoker, bool):
            raise ValueError("Invalid Value.")
        if not isinstance(medication_count, int):
            raise ValueError("Invalid medication_count.")
        if medication_count < 0:
            raise ValueError("Invalid medication_count.")
        if not isinstance(risk_score, (int, float)):
            raise ValueError("Invalid risk_score.")
        if not (0 <= risk_score <= 100):
            raise ValueError("Invalid risk_score.")
        #If hba1c is not NaN, the code goes inside this block.
        if hba1c == hba1c:
            if not isinstance(hba1c, (int, float)):
                raise ValueError("Invalid hba1c.")
            if hba1c < 0:
                raise ValueError("Invalid hba1c.")

        self.blood_glucose = blood_glucose
        self.blood_pressure_systolic = blood_pressure_systolic
        self.blood_pressure_diastolic = blood_pressure_diastolic
        self.bmi = bmi
        self.hba1c = hba1c
        self.cholesterol = cholesterol
        self.last_visit = last_visit
        self.is_smoker = is_smoker
        self.medication_count = medication_count
        self.risk_score = risk_score
    #returns whether the patient is high risk (above 50) or not.
    def is_high_risk(self):
        return self.risk_score > 50
    #returns one of the 3 categories of BMI.
    def bmi_category(self):
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 25:
            return "Normal"
        else:
            return "Overweight"
    #returns whether the patient is hypertensive or not
    def is_hypertensive(self):
        if self.blood_pressure_systolic >= 140 or self.blood_pressure_diastolic >= 90:
            return True
        else:
            return False

    #returns all the values in this class as a dictionary.
    def to_dict(self):
        return {
            "blood_glucose": self.blood_glucose,
            "blood_pressure_systolic": self.blood_pressure_systolic,
            "blood_pressure_diastolic": self.blood_pressure_diastolic,
            "bmi": self.bmi,
            "hba1c": self.hba1c,
            "cholesterol": self.cholesterol,
            "last_visit": self.last_visit,
            "is_smoker": self.is_smoker,
            "medication_count": self.medication_count,
            "risk_score": self.risk_score,

        }







