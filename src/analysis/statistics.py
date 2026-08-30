import pandas as pd
from datetime import datetime
import pika
import json
#clinic is the main class that stores all patients.
from src.models.clinic import Clinic
#this function loads the CSV data into the clinic object.
from src.utils.data_loader import load_patients_data
#import sys to work with sys.path.
#We needed this because when we ran the file directly, Python could not find the src folder
#and we got ModuleNotFoundError.
import sys
import os
#manually add the project root folder to sys.path.
#We had to do this because imports like: from src.models.clinic import Clinic did not work when running statistics.py directly.
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..")
    )
)



#Convert the data kept inside the clinic object into a DataFrame.
#This makes it easier to analyze the data with pandas functions.
def clinic_to_dataframe(clinic):
    data = []

    #Go over all the patients in the clinic.
    #Each patient_id is the key, and patient is the patient object.
    for patient_id, patient in clinic.patients.items():

        #Get the medical record that belongs to the same patient.
        medical_record = clinic.medical_records[patient_id]

        #Create one row that contains patient details and medical details.
        row = {
            "patient_id": patient.patient_id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "diagnosis": patient.diagnosis,
            "diagnosis_date": patient.diagnosis_date,
            #Medical record values
            "blood_glucose": medical_record.blood_glucose,
            "blood_pressure_systolic": medical_record.blood_pressure_systolic,
            "blood_pressure_diastolic": medical_record.blood_pressure_diastolic,
            "bmi": medical_record.bmi,
            "hba1c": medical_record.hba1c,
            "cholesterol": medical_record.cholesterol,
            "last_visit": medical_record.last_visit,
            "is_smoker": medical_record.is_smoker,
            "medication_count": medical_record.medication_count,
            "risk_score": medical_record.risk_score,
            #Add the age group by using the method from the Patient class.
            "age_group": patient.age_group()
        }

        #Add the row to the list of rows.
        data.append(row)

    #Get the list of rows into a dataframe
    return pd.DataFrame(data)


#This function calculates mean, median and standard deviation for medical values by diagnosis.
def diagnosis_statistics(clinic):
    df = clinic_to_dataframe(clinic)

    #Group the patients by diagnosis and calculate statistics for each group.
    result = df.groupby("diagnosis")[[
        "blood_glucose",
        "bmi",
        "blood_pressure_systolic",
        "blood_pressure_diastolic"
    ]].agg(["mean", "median", "std"])

    return result

#Analyze the data by age groups, this helps us see if different age groups have different medical patterns.
def age_group_analysis(clinic):
    df = clinic_to_dataframe(clinic)

    #divide by age group and calculate statistics for risk and medical values.
    result = df.groupby("age_group")[[
        "risk_score",
        "bmi",
        "blood_glucose",
        "medication_count"
    ]].agg(["mean", "median", "std"])

    return result


#Correlation between risk factors
def risk_factor_correlation(clinic):
    df = clinic_to_dataframe(clinic)

    #Choose only numeric columns.
    result = df[[
        "age",
        "bmi",
        "blood_glucose",
        "blood_pressure_systolic",
        "blood_pressure_diastolic",
        "medication_count",
        "risk_score"
    ]].corr()

    return result


#Check if the time since diagnosis is related to the risk score.
def time_since_diagnosis_analysis(clinic):
    df = clinic_to_dataframe(clinic)
    #Get diagnosis_date from text into a real date format.
    df["diagnosis_date"] = pd.to_datetime(df["diagnosis_date"])
    #Get today's date.
    today = datetime.now()
    #Calculate how many years passed since the patient was diagnosed.
    df["years_since_diagnosis"] = (today - df["diagnosis_date"]).dt.days / 365
    # Create a correlation matrix between years since diagnosis and risk score.
    result = df[[
        "years_since_diagnosis",
        "risk_score",
    ]].corr()
    return result


#Check the connection between number of medications and risk score.
#This can show if patients with higher risk usually take more medications.
def medication_burden_analysis(clinic):
    df = clinic_to_dataframe(clinic)
    # Create a correlation matrix between medication count and risk score.
    result = df[[
        "medication_count",
        "risk_score"
    ]].corr()
    return result


def generate_full_report(clinic):
    """
    Generates a full statistical report and saves it as a text file.
    """

    #Run all the statistical analysis functions.
    diagnosis_result = diagnosis_statistics(clinic)
    age_group_result = age_group_analysis(clinic)
    correlation_result = risk_factor_correlation(clinic)
    medication_result = medication_burden_analysis(clinic)
    time_result = time_since_diagnosis_analysis(clinic)

    #Open a text file and write the report into it, if the file does not exist, Python will create it.
    with open("reports/summary_report.txt", "w", encoding="utf-8") as file:

        #Write the title of the report.
        file.write("Chronic Disease System - Statistical Report\n")
        #Write the diagnosis statistics section.
        file.write("1. Diagnosis Statistics:\n")
        file.write(str(diagnosis_result))
        file.write("\n\n")
        #Write the age group analysis section.
        file.write("2. Age Group Analysis\n")
        file.write(str(age_group_result))
        file.write("\n\n")
        #Write the correlation matrix of the risk factors.
        file.write("3. Risk Factor Correlation\n")
        file.write(str(correlation_result))
        file.write("\n\n")
        #Write the medication burden analysis section.
        file.write("4. Medication Burden Analysis\n")
        file.write(str(medication_result))
        file.write("\n\n")
        #Write the time since diagnosis analysis section.
        file.write("5. Time Since Diagnosis Analysis\n")
        file.write(str(time_result))
        file.write("\n")
    return "Report saved to reports/summary_report.txt"




#This consumer works as the Statistics Consumer in our EDA system.
#Flask sends tasks to RabbitMQ,
#RabbitMQ routes the tasks using routing keys,
#And this consumer receives and handles only statistics related tasks.
def statistics_consumer(clinic):
    #Open connection to RabbitMQ.
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    #channel is the communication channel with RabbitMQ.
    #all RabbitMQ actions happen through the channel.

    channel = connection.channel()
    #here we create a Direct Exchange.
    channel.exchange_declare(
        exchange='tasks_exchange',
        exchange_type='direct' )
    #create a queue for statistics tasks.
    channel.queue_declare(queue='statistics_queue')
    #connect the queue to the exchange.
    #if a message arrives with routing_key='statistics'
    #RabbitMQ will send it to statistics_queue.
    channel.queue_bind(
        exchange='tasks_exchange',
        queue='statistics_queue',
        routing_key='statistics')
    #callback runs every time a new message arrives.
    def callback(ch, method, properties, body):
        #we added try except so the consumer will not crash. without that one bad task could stop the whole consumer
        try:
            # RabbitMQ sends bytes, decode converts bytes to string, json.loads converts JSON to dictionary.
            message = json.loads(body.decode())
            #get the task name.
            task = message["task"]
            #print task for debugging.
            print(f"Received task: {task}")
            #run the correct statistics function.
            if task == "diagnosis_statistics":
                result = diagnosis_statistics(clinic)

            elif task == "age_group_analysis":
                result = age_group_analysis(clinic)

            elif task == "risk_factor_correlation":
                result = risk_factor_correlation(clinic)

            elif task == "time_since_diagnosis_analysis":
                result = time_since_diagnosis_analysis(clinic)

            elif task == "generate_full_report":
                result = generate_full_report(clinic)
            else:
                result = f"Unknown task: {task}"

            print(result)

            # Acknowledge the message only after the task was completed successfully.
            ch.basic_ack(delivery_tag=method.delivery_tag)

        #print errors instead of crashing the consumer.
        except Exception as e:

            print(f"Error while processing task: {e}")

    #connect queue to callback.
    #when a message arrives in statistics_queue, callback will run automatically.
    channel.basic_consume(
        queue='statistics_queue',
        on_message_callback=callback,
        # We use manual acknowledgement so RabbitMQ does not remove the message
        # immediately when the consumer receives it.
        # The message is acknowledged only after the task has been processed successfully
        # by calling basic_ack().
        auto_ack=False)
    #message to show the consumer is running.
    print("Statistics consumer is waiting for messages...")
    #start listening for messages forever.
    channel.start_consuming()
#check if this file runs directly.
if __name__ == "__main__":
    #create clinic object.
    clinic = Clinic("Chronic Disease Clinic")
    # Build full path to the CSV file ( We had to do this because at first we got FileNotFoundError when running directly.)
    data_path = os.path.abspath(
        os.path.join( os.path.dirname(__file__), "../../data/patients_data.csv"))
    #load CSV data into clinic.
    load_patients_data(data_path, clinic)
    #start the consumer.
    statistics_consumer(clinic)




