import glob
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os


'''
Notes:
- when merging data, one job application may have multiple permits, represented by multiple rows
- DOB NOW jobs simply do not have phone numbers associated with anyone or anything
        - or zip codes
- i didnt include sprinkler work because I assume you guys dont cover that (but I can change that)
- remove expired permits
'''
#run the following function on the merged dataset to format the owner and contractor names at once
def format_name(FirstName, LastName):
    full_name = f"{FirstName} {LastName}"
    return full_name

def create_address(houseNumber, streetName, zipcode):
    address = f"{houseNumber} {streetName}, {zipcode}"
    return address

def create_short_address(houseNumber, streetName):
    address = f"{houseNumber} {streetName}"
    return address

#''''''''''''''''''''''''''''''''''''''
#   Pull report from website
#''''''''''''''''''''''''''''''''''''''

#"https://data.cityofnewyork.us/Housing-Development/DOB-NOW-Build-Job-Application-Filings/w9ak-ipjd/explore/query/SELECT%0A%20%20%60job_filing_number%60%2C%0A%20%20%60filing_status%60%2C%0A%20%20%60house_no%60%2C%0A%20%20%60street_name%60%2C%0A%20%20%60borough%60%2C%0A%20%20%60applicant_professional_title%60%2C%0A%20%20%60applicant_license%60%2C%0A%20%20%60applicant_first_name%60%2C%0A%20%20%60applicant_last_name%60%2C%0A%20%20%60owner_s_business_name%60%2C%0A%20%20%60owner_s_street_name%60%2C%0A%20%20%60city%60%2C%0A%20%20%60state%60%2C%0A%20%20%60zip%60%2C%0A%20%20%60filing_representative_first_name%60%2C%0A%20%20%60filing_representative_last_name%60%2C%0A%20%20%60filing_representative_business_name%60%2C%0A%20%20%60filing_representative_street_name%60%2C%0A%20%20%60filing_representative_city%60%2C%0A%20%20%60filing_representative_state%60%2C%0A%20%20%60filing_representative_zip%60%2C%0A%20%20%60plumbing_work_type%60%2C%0A%20%20%60initial_cost%60%2C%0A%20%20%60filing_date%60%2C%0A%20%20%60current_status_date%60%2C%0A%20%20%60first_permit_date%60%2C%0A%20%20%60job_type%60/page/filter"
#v filtered columns and by time
#"https://data.cityofnewyork.us/Housing-Development/DOB-NOW-Build-Job-Application-Filings/w9ak-ipjd/explore/query/SELECT%0A%20%20%60job_filing_number%60%2C%0A%20%20%60filing_status%60%2C%0A%20%20%60house_no%60%2C%0A%20%20%60street_name%60%2C%0A%20%20%60borough%60%2C%0A%20%20%60applicant_professional_title%60%2C%0A%20%20%60applicant_license%60%2C%0A%20%20%60applicant_first_name%60%2C%0A%20%20%60applicant_last_name%60%2C%0A%20%20%60owner_s_business_name%60%2C%0A%20%20%60owner_s_street_name%60%2C%0A%20%20%60city%60%2C%0A%20%20%60state%60%2C%0A%20%20%60zip%60%2C%0A%20%20%60filing_representative_first_name%60%2C%0A%20%20%60filing_representative_last_name%60%2C%0A%20%20%60filing_representative_business_name%60%2C%0A%20%20%60filing_representative_street_name%60%2C%0A%20%20%60filing_representative_city%60%2C%0A%20%20%60filing_representative_state%60%2C%0A%20%20%60filing_representative_zip%60%2C%0A%20%20%60plumbing_work_type%60%2C%0A%20%20%60initial_cost%60%2C%0A%20%20%60filing_date%60%2C%0A%20%20%60current_status_date%60%2C%0A%20%20%60first_permit_date%60%2C%0A%20%20%60job_type%60%0AWHERE%0A%20%20%60current_status_date%60%0A%20%20%20%20BETWEEN%20%222024-01-01T01%3A00%3A00%22%20%3A%3A%20floating_timestamp%0A%20%20%20%20AND%20%222025-02-13T08%3A00%3A00%22%20%3A%3A%20floating_timestamp/page/filter"


# Set your desired download folder path
download_path = r"C:\Users\Maria.Rodriguez\VSCode Projects\testingDownload\dobJobs"  # Change this to your preferred path
desired_filename_job = "DOB_job_Permit_Report.csv"  # Set your desired filename
desired_filename_permit = "DOB_Permit_Report.csv"  # Set your desired filename

# set up Edge options 
edge_options = webdriver.EdgeOptions()
prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,  # Disable "Save As" prompt
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True # Enable safe browsing to prevent security warnings
}
edge_options.add_experimental_option("prefs", prefs)

# Set up WebDriver (Update the path to your WebDriver)
driver = webdriver.Edge(options=edge_options)  

# Open the website
url = 'https://data.cityofnewyork.us/Housing-Development/DOB-Job-Application-Filings/ic3t-wcy2/explore/query/SELECT%0A%20%20%60job__%60%2C%0A%20%20%60borough%60%2C%0A%20%20%60house__%60%2C%0A%20%20%60street_name%60%2C%0A%20%20%60job_status_descrp%60%2C%0A%20%20%60latest_action_date%60%2C%0A%20%20%60plumbing%60%2C%0A%20%20%60mechanical%60%2C%0A%20%20%60applicant_s_first_name%60%2C%0A%20%20%60applicant_s_last_name%60%2C%0A%20%20%60pre__filing_date%60%2C%0A%20%20%60owner_type%60%2C%0A%20%20%60owner_s_first_name%60%2C%0A%20%20%60owner_s_last_name%60%2C%0A%20%20%60owner_s_business_name%60%2C%0A%20%20%60owner_sphone__%60%2C%0A%20%20%60job_description%60%2C%0A%20%20%60gis_bin%60%0AWHERE%0A%20%20contains%28%60pre__filing_date%60%2C%20%222024%22%29%0A%20%20%20%20OR%20contains%28%60pre__filing_date%60%2C%20%222025%22%29/page/filter'

url2 = 'https://data.cityofnewyork.us/Housing-Development/DOB-Permit-Issuance/ipu4-2q9a/explore/query/SELECT%0A%20%20%60house__%60%2C%0A%20%20%60street_name%60%2C%0A%20%20%60job__%60%2C%0A%20%20%60zip_code%60%2C%0A%20%20%60work_type%60%2C%0A%20%20%60filing_status%60%2C%0A%20%20%60filing_date%60%2C%0A%20%20%60issuance_date%60%2C%0A%20%20%60expiration_date%60%2C%0A%20%20%60job_start_date%60%2C%0A%20%20%60permittee_s_first_name%60%2C%0A%20%20%60permittee_s_last_name%60%2C%0A%20%20%60permittee_s_business_name%60%2C%0A%20%20%60permittee_s_phone__%60%2C%0A%20%20%60owner_s_business_name%60%2C%0A%20%20%60owner_s_first_name%60%2C%0A%20%20%60owner_s_last_name%60%2C%0A%20%20%60owner_s_house__%60%2C%0A%20%20%60owner_s_house_street_name%60%2C%0A%20%20%60city%60%2C%0A%20%20%60state%60%2C%0A%20%20%60owner_s_zip_code%60%2C%0A%20%20%60owner_s_phone__%60%2C%0A%20%20%60gis_nta_name%60%0AWHERE%20contains%28%60filing_date%60%2C%20"2024"%29%20OR%20contains%28%60filing_date%60%2C%20"2025"%29/page/filter'

'''
driver.get(url)

# Wait for the page to load
time.sleep(15)  

# Locate the export button using its unique attributes (update this selector)
try:
    export_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Export')]")
    export_button.click()
    print("Clicked the export button successfully!")

    download_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Download')]")
    download_button.click()
    print("Downloading data")
    time.sleep(15) # wait for download to complete

    # Find the most recently downloaded file
    list_of_files = glob.glob(os.path.join(download_path, "*"))  # Get all files in the folder
    latest_file = max(list_of_files, key=os.path.getctime)  # Get the newest file

    # Construct the new file path
    new_file_path = os.path.join(download_path, desired_filename_job)
    # Rename the file
    os.rename(latest_file, new_file_path)


except Exception as e:
    print("Could not find or click the button:", e)

# Wait to ensure download starts
time.sleep(5)

# Close the browser
#driver.quit() # the download will continue in the background if you close the browser
# Open the website
driver.get(url2)

# Wait for the page to load
time.sleep(5)  

# Locate the export button using its unique attributes (update this selector)
try:
    export_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Export')]")
    export_button.click()
    print("Part 2")

    download_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Download')]")
    download_button.click()
    print("Downloading data")
    time.sleep(20) # wait for download to complete

    # Find the most recently downloaded file
    list_of_files = glob.glob(os.path.join(download_path, "*"))  # Get all files in the folder
    latest_file2 = max(list_of_files, key=os.path.getctime)  # Get the newest file

    # Construct the new file path
    new_file_path2 = os.path.join(download_path, desired_filename_permit)
    # Rename the file
    os.rename(latest_file2, new_file_path2)
except Exception as e:
    print("Could not find or click the button:", e)

# Wait to ensure download starts
time.sleep(10)
 '''
job_data = pd.read_csv(r"C:\Users\Maria.Rodriguez\VSCode Projects\testingDownload\dobJobs\DOB_job_Permit_Report.csv")
job_data[["Owner Name"]] = job_data.apply(lambda row: pd.Series(format_name(row["Owner's First Name"], row["Owner's Last Name"])), axis=1)
job_data[["Applicant Name"]] = job_data.apply(lambda row: pd.Series(format_name(row["Applicant's First Name"], row["Applicant's Last Name"])), axis=1)
job_data["Job Address"] = job_data.apply(lambda row: pd.Series(create_short_address(row["House #"], row["Street Name"])), axis=1)
#* For job: The Applicant is the owner of the house, the "owner" is the contractor
#! might have to change whos owner and whos applicant...... idk

job_data = job_data[["Job #", "Borough", "Job Status Descrp", "Job Address", "Owner Name", "Applicant Name", "Job Description"]]

# filter out
job_data_filter = job_data[~job_data["Job Status Descrp"].isin(["COMPLETED"])]

#job_data.to_excel('testingggg.xlsx', index=False)

#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Permit data
#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

permit_data = pd.read_csv(r"C:\Users\Maria.Rodriguez\VSCode Projects\testingDownload\dobJobs\DOB_Permit_Report.csv")
permit_data["Permittee's Name"] = permit_data.apply(lambda row: pd.Series(format_name(row["Permittee's First Name"], row["Permittee's Last Name"])), axis=1)
#format the permittee phone number
permit_data["Permittee's Phone #"] = permit_data["Permittee's Phone #"].astype('Int64').astype(str).apply(lambda x: f"({x[:3]})-{x[3:6]}-{x[6:]}")

permit_data = permit_data[["Job #","Permittee's Name", "Permittee's Business Name", "Permittee's Phone #", "Filing Date"]]

# Sort permits by date or other criteria and keep only the first permit per job
#permits_unique = permit_data.drop_duplicates(subset=['Job #'], keep='first')
#! uncomment?^

merged_DOB_NOW = pd.merge(job_data, permit_data, on='Job #', how ='inner')

merged_DOB_NOW.to_excel(r'C:\Users\Maria.Rodriguez\VSCode Projects\testingDownload\mergedDOB.xlsx', index=False)
