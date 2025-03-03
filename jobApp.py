from flask import Flask, render_template, request
import pandas as pd
import os
import re
from datetime import datetime

app = Flask(__name__)

# Keyword categories
keyword_dict = {
    "Plumbing": ["Pipes", "Plumbing", "Drainage", "Sewer", "Water supply"],
    "Roofing and Exterior Work": ["Roof", "Siding", "Shingles", "Marquee"],
    "Construction and Structural": ["Framing", "Foundation", "Drywall", "Beams", "Concrete", "Load-bearing"],
    "Electrical": ["Lighting", "Illuminated", "Wiring", "Circuit", "Electrical"],
    "Renovation": ["Kitchen", "Bathroom", "Renovation", "Remodel", "Extension"],
    "Landscaping and Yard Work": ["Yard work", "Landscaping", "Fencing", "Paving", "Tree removal"],
    "HVAC": ["HVAC", "Heating", "Air conditioning", "Ductwork", "Ventilation"],
    "Environmental": ["Asbestos", "Demolition", "Excavation", "Environmental"]
}



@app.route('/', methods=['GET', 'POST'])
def index():
    #data = pd.read_excel(r"C:/Users/Maria.Rodriguez/VSCode Projects/dobJobs_report.xlsx")
    data = pd.read_excel(r"C:\Users\Maria.Rodriguez\VSCode Projects\testingDownload\mergedDOB.xlsx")
    boroughs = data['Borough'].unique().tolist()
    job_statuses = data['Job Status Descrp'].dropna().unique().tolist()  
    contractor_names = data["Permittee's Business Name"].dropna().unique().tolist()  # Get unique contractor names
    filtered_data = data.copy()
    filtered_data["Filing Date"] = pd.to_datetime(filtered_data["Filing Date"], format="%m/%d/%Y")
    filtered_data = filtered_data[~filtered_data["Job Description"].str.contains(r"\bno[-\s]work\b", case=False, na=False)]

    
    selected_date = request.form.get("date_filter", "2024-01-01")
    selected_boroughs = request.form.getlist("boroughs")
    selected_keywords = request.form.getlist("description_keywords")
    selected_contractor_name = request.form.get("contractor_name", "")
    selected_job_status = request.form.get("job_status", "")
    
    if selected_date:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
        filtered_data = filtered_data[filtered_data["Filing Date"] >= selected_date]
    
    if selected_boroughs:
        filtered_data = filtered_data[filtered_data["Borough"].isin(selected_boroughs)]
    
    if selected_keywords:
        pattern = "|".join(re.escape(word) for word in selected_keywords)  # Case-insensitive regex pattern
        filtered_data = filtered_data[filtered_data["Job Description"].str.contains(pattern, case=False, na=False)]

    if selected_contractor_name:
        filtered_data = filtered_data[filtered_data["Permittee's Business Name"].str.contains(selected_contractor_name, case=False, na=False)]

    if selected_job_status:
        filtered_data = filtered_data[filtered_data["Job Status Descrp"] == selected_job_status]

    return render_template("index.html", 
                           data=filtered_data.to_dict(orient="records"), 
                           boroughs=boroughs, 
                           job_statuses=job_statuses,
                           contractor_names=contractor_names,
                           selected_date=selected_date.strftime("%Y-%m-%d"),
                           selected_boroughs=selected_boroughs,
                           keyword_dict=keyword_dict,
                           selected_keywords=selected_keywords,
                           selected_contractor_name=selected_contractor_name,
                           selected_job_status=selected_job_status)


# New route for the other tab
@app.route('/other', methods=['GET', 'POST'])
def other_page():
    data = pd.read_excel(r"C:\Users\Maria.Rodriguez\VSCode Projects\mergedDOB_NOWjobs.xlsx")
    boroughs = data['Borough'].unique().tolist()
    job_statuses = data['Filing Status'].dropna().unique().tolist()  
    contractor_names = data["Contractor Business Name"].dropna().unique().tolist()  # Get unique contractor names
    filtered_data = data.copy()

    #change filtered date column to a datetime type rather than string
    filtered_data["Filing Date"] = pd.to_datetime(filtered_data["Filing Date"])
    filtered_data = filtered_data[~filtered_data["Job Description"].str.contains(r"\bno[-\s]work\b", case=False, na=False)]

    
    selected_date = request.form.get("date_filter", "2024-01-01")
    selected_boroughs = request.form.getlist("boroughs")
    selected_keywords = request.form.getlist("description_keywords")
    selected_contractor_name = request.form.get("contractor_name", "")
    selected_job_status = request.form.get("job_status", "")
    
    if selected_date:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
        filtered_data = filtered_data[filtered_data["Filing Date"] >= selected_date]
    
    if selected_boroughs:
        filtered_data = filtered_data[filtered_data["Borough"].isin(selected_boroughs)]
    
    if selected_keywords:
        pattern = "|".join(re.escape(word) for word in selected_keywords)  # Case-insensitive regex pattern
        filtered_data = filtered_data[filtered_data["Job Description"].str.contains(pattern, case=False, na=False)]

    if selected_contractor_name:
        filtered_data = filtered_data[filtered_data["Contractor Business Name"].str.contains(selected_contractor_name, case=False, na=False)]

    if selected_job_status:
        filtered_data = filtered_data[filtered_data["Filing Status"] == selected_job_status]

    return render_template("dobNOW.html",
                           data=filtered_data.to_dict(orient="records"), 
                           boroughs=boroughs, 
                           job_statuses=job_statuses,
                           contractor_names=contractor_names,
                           selected_date=selected_date.strftime("%Y-%m-%d"),
                           selected_boroughs=selected_boroughs,
                           keyword_dict=keyword_dict,
                           selected_keywords=selected_keywords,
                           selected_contractor_name=selected_contractor_name,
                           selected_job_status=selected_job_status)


if __name__ == '__main__':
    app.run(debug=True)
