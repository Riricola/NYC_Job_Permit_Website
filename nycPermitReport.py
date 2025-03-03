import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
'''
Jop applications come first, then they file a permit

Looking at all job applications from 2024-2025 and all permits filed in 2025, I merge the two datasets
based on job# 

Questions:
What's the difference between the contractor and the owner
'''
#run the following function on the merged dataset to format the owner and contractor names at once
def format_name(FirstName, LastName):
    full_name = f"{FirstName} {LastName}"
    return full_name

def create_address(houseNumber, streetName, borough):
    address = f"{houseNumber} {streetName}, {borough}"
    return address

job_data = pd.read_csv(r"nycPermitReport\DOB_Job_Application_Filings_202425query.csv") #link data
permit_data = pd.read_csv(r"nycPermitReport\DOB_Permit_Issuance_2025query.csv")

# select specific columns

#* for job application filings
job_data[["Owner Name"]] = job_data.apply(lambda row: pd.Series(format_name(row["Owner's First Name"], row["Owner's Last Name"])), axis=1)
job_data["Job Address"] = job_data.apply(lambda row: pd.Series(create_address(row["House #"], row["Street Name"], row["Borough"])), axis = 1)

filtered_job_data = job_data[['Job #', 'Job Address', 
                    'Approved', "Fully Permitted", "Owner Name", "Owner's Business Name", 
                    "Owner'sPhone #", "Job Description", "Plumbing", "Borough"]]

#! uncoment below line if this is your first run
#filtered_job_data.to_excel('filtered_job_applications.xlsx', index=False) # save the data to an excel file named 'filtered_data.xlsx'
# might change approved variable to another

#* filter for permit issues
permit_data["Contractor Name"] = permit_data.apply(lambda row: pd.Series(format_name(row["Permittee's First Name"], row["Permittee's Last Name"])), axis = 1)
permit_data = permit_data.rename(columns={"Permittee's Business Name": "Contractor Business Name"})
filtered_permit_data = permit_data[["Job #", "Contractor Name", "Contractor Business Name",
                                    "Filing Date", "Job Start Date"]]

permits_unique = filtered_permit_data.drop_duplicates(subset=['Job #'], keep='first')

#! uncoment below line if this is your first run
#filtered_permit_data.to_excel('filtered_permit_issuance.xlsx', index=False) # save the data to an excel file named 'filtered_data.xlsx'

# Before merging, filter by date (After august 30, 2024)
filtered_permit_data["Filing Date"] = pd.to_datetime(filtered_permit_data["Filing Date"])
# Filter for rows between specific dates (e.g., February to June 2024)
start_date = '2024-08-30'
end_date = '2025-02-13'

filtered_permit_data = filtered_permit_data[(filtered_permit_data['Filing Date'] >= start_date) & (filtered_permit_data['Filing Date'] <= end_date)]


# merge by job#
merged_job_permit = pd.merge(filtered_job_data, filtered_permit_data, on='Job #', how ='inner')

desired_order = ["Job #", "Contractor Name", "Contractor Business Name", "Owner's Business Name", "Owner Name", "Owner'sPhone #", "Job Address", "Borough", 'Approved', "Fully Permitted", "Filing Date",  
                 "Job Start Date", "Job Description"]
merged_job_permit = merged_job_permit[desired_order]

#merged_job_permit.to_excel('merged_job_permit2025.xlsx', index=False) # save the data to an excel file named 'merged_data.xlsx'
merged_job_permit.to_excel('dobJobs_report.xlsx', index=False)