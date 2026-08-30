
#This script runs the Chronic Disease Management System.
#It loads the data, creates the clinic object, generates reports,
#creates visualizations and runs the interactive menu if the user chooses it.
import argparse
import os
from src.models.clinic import Clinic
from src.utils.data_loader import load_patients_data
from src.analysis.statistics import (generate_full_report,diagnosis_statistics,age_group_analysis,
                                     risk_factor_correlation,medication_burden_analysis,
                                     time_since_diagnosis_analysis)
from src.analysis import visualizations

def parse_arguments():
    #Handles the command line arguments for the system,
    #allowing the user to choose between reports, visualizations, or the menu.
    parser = argparse.ArgumentParser(description="Chronic Disease Management System")

    parser.add_argument( "--data",
                         default="data/patients_data.csv",
                         help="Path to the patients CSV file")
    parser.add_argument("--report",
                        action="store_true",
                        help="Generate a statistical report")
    parser.add_argument("--visualize",
                        action="store_true",
                        help="Generate visualizations")
    parser.add_argument("--interactive",
                        action="store_true",
                        help="Run interactive menu")
    return parser.parse_args()

def run_visualizations(clinic):

#Goes through the list of visualization functions and generates all the
#necessary charts. The results are saved directly into the reports folder.

    print("Generating graphs...")
    # Call each visualization function directly
    visualizations.plot_glucose_distribution(clinic)
    visualizations.plot_bmi_vs_glucose(clinic)
    visualizations.plot_risk_score_boxplot(clinic)
    visualizations.plot_age_distribution(clinic)
    visualizations.plot_correlation_heatmap(clinic)
    visualizations.generate_dashboard(clinic)
    print("All visualizations were saved in the reports folder.")

def show_full_patient_profile(clinic):
    #Asks the user for a patient ID and shows their full information,
    #including personal details and all medical tests.
    patient_id = input("Enter patient ID: ")
    patient = clinic.get_patient_by_id(patient_id)
    record = clinic.get_medical_record(patient_id)
    if patient is None or record is None:
        print("Patient not found.")
        return
    print("\nPatient profile:")
    print(patient.get_profile())
    print(f"Blood glucose: {record.blood_glucose}")
    print(f"Blood pressure: {record.blood_pressure_systolic}/{record.blood_pressure_diastolic}")
    print(f"BMI: {record.bmi}")
    print(f"Hba1c: {record.hba1c}")
    print(f"Cholesterol: {record.cholesterol}")
    print(f"Last visit: {record.last_visit}")
    print(f"Smoker: {record.is_smoker}")
    print(f"Medication count: {record.medication_count}")
    print(f"Risk score: {record.risk_score}")

def search_patient_by_id(clinic):
    #A simple search tool that checks if a patient exists in the system
    #by their ID and prints their basic profile if found.
    patient_id = input("Enter the patient's ID: ")
    patient = clinic.get_patient_by_id(patient_id)
    if patient is None:
        print("Patient was not found.")
    else:
        print("Patient found:")
        print(patient.get_profile())

def run_specific_analysis(clinic):

    #Displays a list of statistical analyses and runs the one chosen by the user.

    print("\nChoose analysis:")
    print("1.Diagnosis statistics")
    print("2.Age group analysis")
    print("3.Risk factor correlation")
    print("4.Medication burden analysis")
    print("5.Time since diagnosis analysis")
    choice = input("Enter the number of the analysis you want to run (1-5): ")
    if choice == "1":
        print(diagnosis_statistics(clinic))
    elif choice == "2":
        print(age_group_analysis(clinic))
    elif choice == "3":
        print(risk_factor_correlation(clinic))
    elif choice == "4":
        print(medication_burden_analysis(clinic))
    elif choice == "5":
        print(time_since_diagnosis_analysis(clinic))
    else:
        print("Invalid choice.")

def interactive_menu(clinic):
    #Runs the main interactive loop. This menu keeps the program active,
    #allowing the user to perform multiple tasks until they choose to exit.
    while True:
        print("\nInteractive Menu")
        print("1.Search patient by ID")
        print("2.Show full patient profile")
        print("3.Run specific analysis")
        print("4. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            search_patient_by_id(clinic)
        elif choice == "2":
            show_full_patient_profile(clinic)
        elif choice == "3":
            run_specific_analysis(clinic)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    #The starting point of the script. It coordinates the data loading process,
    #sets up the clinic object, and calls the requested functions according to the arguments.
    args = parse_arguments()
    os.makedirs("reports", exist_ok=True)
    clinic = Clinic("Chronic Disease Clinic")
    try:
        load_patients_data(args.data, clinic)
        print(f"Data loaded successfully. {len(clinic.get_all_patients())} patients found.")
    except Exception as e:
        print(f"Error: Could not load data from {args.data}. Details: {e}")
        return
    #print("Data loaded successfully.")
    #print(f"Number of patients: {len(clinic.get_all_patients())}")

    if args.report:
        message = generate_full_report(clinic)
        print(message)
    if args.visualize:
        run_visualizations(clinic)
    if args.interactive:
        interactive_menu(clinic)

    print("Project finished successfully.")

if __name__ == "__main__":
    main()











































































