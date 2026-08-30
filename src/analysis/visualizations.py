import sys
import os

analysis_path = os.path.dirname(__file__)
#We had a special problem with seaborn imports.
#Our project contains a file called: statistics.py
#But Python also has a built-in library called statistics...
#seaborn internally imports the built-in statistics library.
#So when we ran visualizations.py directly, Python accidentally imported our statistics.py instead.
#This caused: ImportError: cannot import name 'NormalDist'
#We didn't want to change the name because this is the required name in the instructions
#So to solve this, we temporarily removed src/analysis from sys.path.
if analysis_path in sys.path:
    sys.path.remove(analysis_path)
import matplotlib.pyplot as plt
import seaborn as sns
from src.analysis.statistics import clinic_to_dataframe
import pika
import json
from src.models.clinic import Clinic
from src.utils.data_loader import load_patients_data
import sys
import os
#Here we manually add the project root folder to sys.path.
#We had to do this because imports like:
#from src.models.clinic import Clinic
#did not work when running the file directly.
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")))

#a histogram graph that shows the blood glucose distribution by diagnosis.
def plot_glucose_distribution(clinic):
    df = clinic_to_dataframe(clinic)
    plt.figure(figsize=(10,6))
    sns.histplot(data = df, x = "blood_glucose", hue = "diagnosis", kde = True)
    plt.title("Glucose Distribution by Diagnosis")
    plt.xlabel("Blood Glucose")
    plt.ylabel("Number of Patients")
    #adjust the layout so the graphs will not be cut.
    plt.tight_layout()
    #save
    plt.savefig("reports/distribution_by_diagnosis_histogram_plot.png")
    plt.close()

#a scatter plot that shows the connection between bmi, blood glucose, diagnosis and risk score.
def plot_bmi_vs_glucose(clinic):
    df = clinic_to_dataframe(clinic)
    plt.figure(figsize=(12,8))
    sns.scatterplot(data = df, x = "bmi", y = "blood_glucose", hue = "diagnosis", size="risk_score")
    plt.title("BMI vs Blood Glucose by Diagnosis and Risk Score")
    plt.xlabel("BMI")
    plt.ylabel("Blood Glucose")
    plt.tight_layout()
    plt.savefig("reports/bmi_vs_glucose_scatter_plot.png")
    plt.close()

#a box plot that shows relationship between diagnosis, risk score and gender.
def plot_risk_score_boxplot(clinic):
    df = clinic_to_dataframe(clinic)
    plt.figure(figsize=(10,6))
    sns.boxplot(data = df, x = "diagnosis", y = "risk_score", hue = "gender")
    plt.title("Risk Score by Diagnosis and Gender")
    plt.xlabel("Diagnosis")
    plt.ylabel("Risk score")
    plt.tight_layout()
    plt.savefig("reports/risk_score_by_diagnosis_gender_boxplot.png")
    plt.close()

#a pyramid chart that shows the distribution of age groups by gender.
def plot_age_distribution(clinic):
    df = clinic_to_dataframe(clinic)
    age_gender_counts = df.groupby(["age_group", "gender"]).size()
    age_gender_table = age_gender_counts.unstack()
    age_gender_table = age_gender_table.fillna(0)
    plt.figure(figsize=(10, 6))
    plt.barh(age_gender_table.index, -age_gender_table["M"], label="Male")
    plt.barh(age_gender_table.index, age_gender_table["F"], label="Female")
    plt.title("Age Distribution by Gender")
    plt.xlabel("Number of Patients")
    plt.ylabel("Age Group")
    plt.legend()
    plt.tight_layout()
    plt.savefig("reports/age_distribution_pyramid_chart.png")
    plt.close()

#a heatmap that shows the correlation between age, bmi, glucose, blood pressure sys and dia, medication count and risk score.
def plot_correlation_heatmap(clinic):
    df = clinic_to_dataframe(clinic)
    columns = ["age","bmi","blood_glucose","blood_pressure_systolic",
               "blood_pressure_diastolic","medication_count","risk_score"]
    corr = df[columns].corr()
    plt.figure(figsize = (12,8))
    sns.heatmap(corr, annot = True, fmt = ".2f")
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig("reports/correlation_heatmap.png")
    plt.close()


#a function that creates one dashboard image with 4 graphs.
def generate_dashboard(clinic):
    df = clinic_to_dataframe(clinic)
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    #graph 1
    sns.histplot(data=df, x="blood_glucose", hue="diagnosis", kde=True, ax=axes[0, 0])
    axes[0, 0].set_title("Glucose Distribution by Diagnosis")
    #graph 2
    sns.scatterplot(
        data=df, x="bmi", y="blood_glucose", hue="diagnosis", size="risk_score", ax=axes[0, 1])
    axes[0, 1].set_title("BMI vs Glucose")
    #graph 3
    sns.boxplot(data=df, x="diagnosis", y="risk_score", hue="gender", ax=axes[1, 0])
    axes[1, 0].set_title("Risk Score by Diagnosis")
    #Graph 4:
    columns = ["age", "bmi", "blood_glucose", "blood_pressure_systolic",
               "blood_pressure_diastolic", "medication_count", "risk_score"]
    corr = df[columns].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", ax=axes[1, 1])
    axes[1, 1].set_title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig("reports/dashboard.png")
    #close
    plt.close(fig)


#This consumer works as the Visualizations Consumer in our EDA system.
#Flask sends tasks to rabbitMQ,
#RabbitMQ routes the tasks using routing keys,
#and this consumer receives and handles only visualization related tasks.

def visualizations_consumer(clinic):
    #Open connection to RabbitMQ.
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    # channel is the communication channel with RabbitMQ.
    # all RabbitMQ actions happen through the channel.

    channel = connection.channel()
    # here we create a direct exchange.
    channel.exchange_declare(
        exchange='tasks_exchange',
        exchange_type='direct')

    # create a queue for visualizations tasks.
    channel.queue_declare(queue='visualizations_queue')
    # connect the queue to the exchange
    # if a message arrives with routing_key='visualizations'
    #rabbitMQ will send it to visualizations_queue.
    channel.queue_bind(
        exchange='tasks_exchange',
        queue='visualizations_queue',
        routing_key='visualizations')

    # callback runs every time a new message arrives.
    def callback(ch, method, properties, body):
        #we added try except so the consumer will not crash. without that one bad task could stop the whole consumer
        try:
            #abbitMQ sends bytes, decode converts bytes to string, json.loads converts JSON to dictionary.
            message = json.loads(body.decode())
            #get the task name.
            task = message["task"]
            #print task for debugging
            print(f"Received task: {task}")
            #run the correct visualizations function.
            if task == "plot_glucose_distribution":

                plot_glucose_distribution(clinic)

            elif task == "plot_bmi_vs_glucose":

                plot_bmi_vs_glucose(clinic)

            elif task == "plot_risk_score_boxplot":

                plot_risk_score_boxplot(clinic)

            elif task == "plot_correlation_heatmap":

                plot_correlation_heatmap(clinic)

            elif task == "generate_dashboard":

                generate_dashboard(clinic)
            else:
                result = f"Unknown task: {task}"
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            #print errors instead of crashing the consumer.
            print(f"Error while processing task: {e}")

    #connect queue to callback.
    #when a message arrives in visualizations_queue, callback will run automatically.
    channel.basic_consume(
        queue='visualizations_queue',
        on_message_callback=callback,
        # We use manual acknowledgement so RabbitMQ does not remove the message
        # immediately when the consumer receives it.
        # The message is acknowledged only after the task is completed successfully.
        auto_ack=False)

    # message to show the consumer is running.
    print("visualizations consumer is waiting for messages...")
    #start listening for messages forever.
    channel.start_consuming()
#check if this file runs directly.

if __name__ == "__main__":
    # create clinic object.
    clinic = Clinic("Chronic Disease Clinic")
    #build full path to the CSV file ( We had to do this because at first we got FileNotFoundError when running directly.)
    data_path = os.path.abspath( os.path.join(os.path.dirname(__file__),"../../data/patients_data.csv"))
    # load CSV data into clinic.
    load_patients_data(
        data_path,
        clinic)
    #start the consumer.
    visualizations_consumer(clinic)








