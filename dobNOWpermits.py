import glob
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time


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

def create_address(houseNumber, streetName, borough, zipcode):
    address = f"{houseNumber} {streetName}, {borough} {zipcode}"
    return address

#''''''''''''''''''''''''''''''''''''''
#   Pull report from website
#''''''''''''''''''''''''''''''''''''''

#open permit and job application links
#v original data
#"https://data.cityofnewyork.us/Housing-Development/DOB-NOW-Build-Job-Application-Filings/w9ak-ipjd/explore/query/SELECT%0A%20%20%60job_filing_number%60%2C%0A%20%20%60filing_status%60%2C%0A%20%20%60house_no%60%2C%0A%20%20%60street_name%60%2C%0A%20%20%60borough%60%2C%0A%20%20%60block%60%2C%0A%20%20%60lot%60%2C%0A%20%20%60bin%60%2C%0A%20%20%60commmunity_board%60%2C%0A%20%20%60work_on_floor%60%2C%0A%20%20%60apt_condo_no_s%60%2C%0A%20%20%60applicant_professional_title%60%2C%0A%20%20%60applicant_license%60%2C%0A%20%20%60applicant_first_name%60%2C%0A%20%20%60applicants_middle_initial%60%2C%0A%20%20%60applicant_last_name%60%2C%0A%20%20%60owner_s_business_name%60%2C%0A%20%20%60owner_s_street_name%60%2C%0A%20%20%60city%60%2C%0A%20%20%60state%60%2C%0A%20%20%60zip%60%2C%0A%20%20%60filing_representative_first_name%60%2C%0A%20%20%60filing_representative_middle_initial%60%2C%0A%20%20%60filing_representative_last_name%60%2C%0A%20%20%60filing_representative_business_name%60%2C%0A%20%20%60filing_representative_street_name%60%2C%0A%20%20%60filing_representative_city%60%2C%0A%20%20%60filing_representative_state%60%2C%0A%20%20%60filing_representative_zip%60%2C%0A%20%20%60sprinkler_work_type%60%2C%0A%20%20%60plumbing_work_type%60%2C%0A%20%20%60initial_cost%60%2C%0A%20%20%60total_construction_floor_area%60%2C%0A%20%20%60review_building_code%60%2C%0A%20%20%60little_e%60%2C%0A%20%20%60unmapped_cco_street%60%2C%0A%20%20%60request_legalization%60%2C%0A%20%20%60includes_permanent_removal%60%2C%0A%20%20%60in_compliance_with_nycecc%60%2C%0A%20%20%60exempt_from_nycecc%60%2C%0A%20%20%60building_type%60%2C%0A%20%20%60existing_stories%60%2C%0A%20%20%60existing_height%60%2C%0A%20%20%60existing_dwelling_units%60%2C%0A%20%20%60proposed_no_of_stories%60%2C%0A%20%20%60proposed_height%60%2C%0A%20%20%60proposed_dwelling_units%60%2C%0A%20%20%60specialinspectionrequirement%60%2C%0A%20%20%60special_inspection_agency_number%60%2C%0A%20%20%60progressinspectionrequirement%60%2C%0A%20%20%60built_1_information_value%60%2C%0A%20%20%60built_2_information_value%60%2C%0A%20%20%60built_2_a_information_value%60%2C%0A%20%20%60built_2_b_information_value%60%2C%0A%20%20%60standpipe%60%2C%0A%20%20%60antenna%60%2C%0A%20%20%60curb_cut%60%2C%0A%20%20%60sign%60%2C%0A%20%20%60fence%60%2C%0A%20%20%60scaffold%60%2C%0A%20%20%60shed%60%2C%0A%20%20%60postcode%60%2C%0A%20%20%60latitude%60%2C%0A%20%20%60longitude%60%2C%0A%20%20%60council_district%60%2C%0A%20%20%60census_tract%60%2C%0A%20%20%60bbl%60%2C%0A%20%20%60nta%60%2C%0A%20%20%60filing_date%60%2C%0A%20%20%60current_status_date%60%2C%0A%20%20%60first_permit_date%60%2C%0A%20%20%60boiler_equipment_work_type_%60%2C%0A%20%20%60earth_work_work_type_%60%2C%0A%20%20%60foundation_work_type_%60%2C%0A%20%20%60general_construction_work_type_%60%2C%0A%20%20%60mechanical_systems_work_type_%60%2C%0A%20%20%60place_of_assembly_work_type_%60%2C%0A%20%20%60protection_mechanical_methods_work_type_%60%2C%0A%20%20%60sidewalk_shed_work_type_%60%2C%0A%20%20%60structural_work_type_%60%2C%0A%20%20%60support_of_excavation_work_type_%60%2C%0A%20%20%60temporary_place_of_assembly_work_type_%60%2C%0A%20%20%60job_type%60/page/filter"
#v filtered columns
#"https://data.cityofnewyork.us/Housing-Development/DOB-NOW-Build-Job-Application-Filings/w9ak-ipjd/explore/query/SELECT%0A%20%20%60job_filing_number%60%2C%0A%20%20%60filing_status%60%2C%0A%20%20%60house_no%60%2C%0A%20%20%60street_name%60%2C%0A%20%20%60borough%60%2C%0A%20%20%60applicant_professional_title%60%2C%0A%20%20%60applicant_license%60%2C%0A%20%20%60applicant_first_name%60%2C%0A%20%20%60applicant_last_name%60%2C%0A%20%20%60owner_s_business_name%60%2C%0A%20%20%60owner_s_street_name%60%2C%0A%20%20%60city%60%2C%0A%20%20%60state%60%2C%0A%20%20%60zip%60%2C%0A%20%20%60filing_representative_first_name%60%2C%0A%20%20%60filing_representative_last_name%60%2C%0A%20%20%60filing_representative_business_name%60%2C%0A%20%20%60filing_representative_street_name%60%2C%0A%20%20%60filing_representative_city%60%2C%0A%20%20%60filing_representative_state%60%2C%0A%20%20%60filing_representative_zip%60%2C%0A%20%20%60plumbing_work_type%60%2C%0A%20%20%60initial_cost%60%2C%0A%20%20%60filing_date%60%2C%0A%20%20%60current_status_date%60%2C%0A%20%20%60first_permit_date%60%2C%0A%20%20%60job_type%60/page/filter"
#v filtered columns and by time
#"https://data.cityofnewyork.us/Housing-Development/DOB-NOW-Build-Job-Application-Filings/w9ak-ipjd/explore/query/SELECT%0A%20%20%60job_filing_number%60%2C%0A%20%20%60filing_status%60%2C%0A%20%20%60house_no%60%2C%0A%20%20%60street_name%60%2C%0A%20%20%60borough%60%2C%0A%20%20%60applicant_professional_title%60%2C%0A%20%20%60applicant_license%60%2C%0A%20%20%60applicant_first_name%60%2C%0A%20%20%60applicant_last_name%60%2C%0A%20%20%60owner_s_business_name%60%2C%0A%20%20%60owner_s_street_name%60%2C%0A%20%20%60city%60%2C%0A%20%20%60state%60%2C%0A%20%20%60zip%60%2C%0A%20%20%60filing_representative_first_name%60%2C%0A%20%20%60filing_representative_last_name%60%2C%0A%20%20%60filing_representative_business_name%60%2C%0A%20%20%60filing_representative_street_name%60%2C%0A%20%20%60filing_representative_city%60%2C%0A%20%20%60filing_representative_state%60%2C%0A%20%20%60filing_representative_zip%60%2C%0A%20%20%60plumbing_work_type%60%2C%0A%20%20%60initial_cost%60%2C%0A%20%20%60filing_date%60%2C%0A%20%20%60current_status_date%60%2C%0A%20%20%60first_permit_date%60%2C%0A%20%20%60job_type%60%0AWHERE%0A%20%20%60current_status_date%60%0A%20%20%20%20BETWEEN%20%222024-01-01T01%3A00%3A00%22%20%3A%3A%20floating_timestamp%0A%20%20%20%20AND%20%222025-02-13T08%3A00%3A00%22%20%3A%3A%20floating_timestamp/page/filter"


# Set your desired download folder path
download_path = r"C:\Users\Maria.Rodriguez\VSCode Projects\testingDownload\dobNOWjobs"  # Change this to your preferred path
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
url = 'https://data.cityofnewyork.us/Housing-Development/DOB-NOW-Build-Job-Application-Filings/w9ak-ipjd/explore/query/SELECT%0A%20%20%60job_filing_number%60%2C%0A%20%20%60filing_status%60%2C%0A%20%20%60house_no%60%2C%0A%20%20%60street_name%60%2C%0A%20%20%60borough%60%2C%0A%20%20%60applicant_professional_title%60%2C%0A%20%20%60applicant_license%60%2C%0A%20%20%60applicant_first_name%60%2C%0A%20%20%60applicant_last_name%60%2C%0A%20%20%60owner_s_business_name%60%2C%0A%20%20%60owner_s_street_name%60%2C%0A%20%20%60city%60%2C%0A%20%20%60state%60%2C%0A%20%20%60zip%60%2C%0A%20%20%60filing_representative_first_name%60%2C%0A%20%20%60filing_representative_last_name%60%2C%0A%20%20%60filing_representative_business_name%60%2C%0A%20%20%60filing_representative_street_name%60%2C%0A%20%20%60filing_representative_city%60%2C%0A%20%20%60filing_representative_state%60%2C%0A%20%20%60filing_representative_zip%60%2C%0A%20%20%60plumbing_work_type%60%2C%0A%20%20%60initial_cost%60%2C%0A%20%20%60postcode%60%2C%0A%20%20%60general_construction_work_type_%60%2C%0A%20%20%60filing_date%60%2C%0A%20%20%60current_status_date%60%2C%0A%20%20%60first_permit_date%60%2C%0A%20%20%60job_type%60%0AWHERE%0A%20%20%60filing_date%60%0A%20%20%20%20BETWEEN%20"2024-08-30T16%3A20%3A35"%20%3A%3A%20floating_timestamp%0A%20%20%20%20AND%20"2025-02-13T16%3A20%3A35"%20%3A%3A%20floating_timestamp/page/filter'


driver.get(url)

# Wait for the page to load
time.sleep(5)  

# Locate the export button using its unique attributes (update this selector)
try:
    export_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Export')]")
    export_button.click()
    print("Clicked the export button successfully!")

    download_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Download')]")
    download_button.click()
    print("Downloading data")
    time.sleep(10) # wait for download to complete

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
time.sleep(10)

# Close the browser
#driver.quit() # the download will continue in the background if you close the browser
# Open the website
url2 = 'https://data.cityofnewyork.us/Housing-Development/DOB-NOW-Build-Approved-Permits/rbx6-tga4/explore/query/SELECT%0A%20%20%60job_filing_number%60%2C%0A%20%20%60filing_reason%60%2C%0A%20%20%60house_no%60%2C%0A%20%20%60street_name%60%2C%0A%20%20%60borough%60%2C%0A%20%20%60lot%60%2C%0A%20%20%60bin%60%2C%0A%20%20%60block%60%2C%0A%20%20%60c_b_no%60%2C%0A%20%20%60apt_condo_no_s%60%2C%0A%20%20%60work_on_floor%60%2C%0A%20%20%60work_type%60%2C%0A%20%20%60permittee_s_license_type%60%2C%0A%20%20%60applicant_license%60%2C%0A%20%20%60applicant_first_name%60%2C%0A%20%20%60applicant_middle_name%60%2C%0A%20%20%60applicant_last_name%60%2C%0A%20%20%60applicant_business_name%60%2C%0A%20%20%60applicant_business_address%60%2C%0A%20%20%60filing_representative_first_name%60%2C%0A%20%20%60filing_representative_middle_initial%60%2C%0A%20%20%60filing_representative_last_name%60%2C%0A%20%20%60filing_representative_business_name%60%2C%0A%20%20%60work_permit%60%2C%0A%20%20%60approved_date%60%2C%0A%20%20%60issued_date%60%2C%0A%20%20%60expired_date%60%2C%0A%20%20%60job_description%60%2C%0A%20%20%60estimated_job_costs%60%2C%0A%20%20%60owner_business_name%60%2C%0A%20%20%60owner_name%60%2C%0A%20%20%60owner_street_address%60%2C%0A%20%20%60owner_city%60%2C%0A%20%20%60owner_state%60%2C%0A%20%20%60owner_zip_code%60%0AWHERE%20%60expired_date%60%20>%20"2025-02-13T12%3A02%3A28"%20%3A%3A%20floating_timestamp/page/filter'
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
time.sleep(20)


# if the driver quit
job_data = pd.read_csv(r"C:\Users\Maria.Rodriguez\VSCode Projects\testingDownload\dobNOWjobs\DOB_job_Permit_Report.csv") # link data #! gotta change the end of the path
job_data[["Owner Name"]] = job_data.apply(lambda row: pd.Series(format_name(row["Applicant First Name"], row["Applicant Last Name"])), axis=1)
job_data["Job Address"] = job_data.apply(lambda row: pd.Series(create_address(row["House No"], row["Street Name"], row["Borough"], row["Postcode"])), axis=1)
#* For job: The Applicant is the owner of the house, the "owner" is the contractor

job_data = job_data[["Job Filing Number", "Filing Status", "Job Address", "Owner Name", "Filing Date", "Current Status Date", "First Permit Date", "Plumbing (Work Type)", "General Construction (Work Type)"]]

# filter out
job_data_filter = job_data[~job_data["Current Status Date"].isin(["Disapproved", "Filing Withdrawn", "Incomplete", "Intent to Revoke"])]

#job_data.to_excel('testingggg.xlsx', index=False)

#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Permit data
#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
permit_data = pd.read_csv(r"C:\Users\Maria.Rodriguez\VSCode Projects\testingDownload\dobNOWjobs\DOB_Permit_Report.csv") # link data #! gotta change the end of the path

permit_data["Contractor Name"] = permit_data.apply(lambda row: pd.Series(format_name(row["Applicant First Name"], row["Applicant Last Name"])), axis=1)
permit_data = permit_data.rename(columns={"Applicant Business Address": "Contractor Address", "Applicant Business Name": "Contractor Business Name"})
permit_data = permit_data[["Job Filing Number", "Work Type", "Contractor Name", "Contractor Business Name", "Job Description", "Approved Date", "Borough"]]

# Sort permits by date or other criteria and keep only the first permit per job
permits_unique = permit_data.drop_duplicates(subset=['Job Filing Number'], keep='first')


merged_DOB_NOW = pd.merge(job_data, permits_unique, on='Job Filing Number', how ='inner')
merged_DOB_NOW = merged_DOB_NOW[~merged_DOB_NOW["Filing Status"].isin(["LOC Issued", "Filing Withdrawn"])]

merged_DOB_NOW.to_excel('mergedDOB_NOWjobs.xlsx', index=False)
