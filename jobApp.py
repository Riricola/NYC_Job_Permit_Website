from flask import Flask, render_template, request
import pandas as pd
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
    "HVAC": ["HVAC", "Heating", "Air conditioning", "Ductwork", "Ventilation"],
    "Environmental": ["Asbestos", "Demolition", "Excavation", "Environmental"]
}


def check_search_match(row, search_query):
    try:
        return search_query.lower() in str(row['Job Description']).lower() or search_query.lower() in str(row['Job Address']).lower()
    except AttributeError:  # In case a value is completely missing
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    data = pd.read_excel(r"C:\Users\Maria.Rodriguez\VSCode Projects\testingDownload\mergedDOB.xlsx")
    data = data[~data["Job Description"].str.contains(r"\bno[-\s]work\b", case=False, na=False)]

    boroughs = data['Borough'].unique().tolist()
    job_statuses = data['Job Status Descrp'].dropna().unique().tolist()

    # Determine which HTTP method is being used and get parameters accordingly
    if request.method == 'POST':
        form_data = request.form
    else:
        form_data = request.args

    # Default values for filters
    selected_date = request.form.get("date_filter", "2024-01-01")
    selected_boroughs = request.form.getlist("boroughs")
    selected_keywords = request.form.getlist("description_keywords")
    selected_job_status = request.form.getlist("job_status")
    search_query = request.form.get('search', '')  # Get user input
    # After initial filtering, determine available contractor names
    #contractor_names = data["Permittee's Business Name"].dropna().unique().tolist()

    # Apply second-level filtering (Contractor Name) only if the initial filter was used
    #selected_contractor_name = form_data.get("contractor_name", "")

    filtered_data = data.copy()
    # Convert Filing Date to datetime format
    filtered_data["Pre- Filing Date"] = pd.to_datetime(filtered_data["Pre- Filing Date"], format="%m/%d/%Y", errors="coerce")
        
    

    # Apply date filter if provided
    if selected_date:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
        filtered_data = filtered_data[filtered_data["Pre- Filing Date"] >= selected_date]

    print(selected_boroughs)
    if selected_boroughs:
        filtered_data = filtered_data[filtered_data["Borough"].isin(selected_boroughs)]
        #contractor_names = filtered_data["Permittee's Business Name"].dropna().unique().tolist()

    print(selected_job_status)
    if selected_job_status:
        filtered_data = filtered_data[filtered_data["Job Status Descrp"].isin(selected_job_status)]

    #if initial_filter_applied and selected_contractor_name:
    #   filtered_data = filtered_data[filtered_data["Permittee's Business Name"].str.contains(selected_contractor_name, case=False, na=False)]

    #Get user input for keywords:
    if search_query:
        filtered_data = filtered_data[filtered_data.apply(lambda row: check_search_match(row, search_query), axis=1)]

    if selected_keywords:
            pattern = "|".join(re.escape(word) for word in selected_keywords)
            filtered_data = filtered_data[filtered_data["Job Description"].str.contains(pattern, case=False, na=False)]


    print(filtered_data.head())
    

    # Pagination Logic
    page = int(form_data.get("page", 1))
    per_page = 100

    if filtered_data.empty:
        total_pages = 0
        paginated_data = pd.DataFrame()
    else:
        
        # Calculate total pages only if we have filtered_data
        total_pages = max(1, (len(filtered_data) // per_page) + (1 if len(filtered_data) % per_page else 0))
        
        # Make sure page is within valid range
        page = max(1, min(page, total_pages))
        
        # Slice filtered_data for Current Page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, len(filtered_data))
        paginated_data = filtered_data.iloc[start_idx:end_idx]

    date_str = selected_date.strftime("%Y-%m-%d") if isinstance(selected_date, datetime) else selected_date


    return render_template("index.html", 
                           data=paginated_data.to_dict(orient="records"), 
                           boroughs=boroughs, 
                           job_statuses=job_statuses,
                           selected_job_status = selected_job_status, 
                           #contractor_names=contractor_names,
                           selected_date=date_str,
                           selected_boroughs=selected_boroughs,
                           selected_keywords=selected_keywords,
                           keyword_dict=keyword_dict,
                           search_query=search_query,
                           #selected_contractor_name=selected_contractor_name,
                           initial_filter_applied=bool(selected_boroughs),
                           page=page,
                           total_pages=total_pages)



# New route for the other tab
@app.route('/other', methods=['GET', 'POST'])
def other_page():
    boroughs = ["MANHATTAN", "BROOKLYN", "QUEENS", "BRONX", "STATEN ISLAND"]
    job_statuses = []
    contractor_names = []
    selected_keywords = []
    
    try:
        data = pd.read_excel(r"C:\Users\Maria.Rodriguez\VSCode Projects\mergedDOB_NOWjobs.xlsx")
        data = data.drop_duplicates(subset=["Job Filing Number"])
        data = data[~data["Job Description"].str.contains(r"\bno[-\s]work\b", case=False, na=False)]
    except Exception as e:
        print(f"Error loading data: {e}")
        data = pd.DataFrame()  # Create empty DataFrame if file not found
    
    # Determine which HTTP method is being used and get parameters accordingly
    if request.method == 'POST':
        form_data = request.form
    else:
        form_data = request.args
    
    # Get Filters from Request
    selected_date = form_data.get("date_filter", "2024-01-01")
    selected_boroughs = form_data.getlist("boroughs")
    selected_keywords = form_data.getlist("description_keywords")
    search_query = form_data.get('search', '')
    selected_contractor_name = form_data.get("contractor_name", "")
    
    filtered_data = data.copy()
    # Apply Filters only if we have data and boroughs selected
    if not filtered_data.empty:
        # Convert to datetime
        try:
            print("Filtering data\n")
            filtered_data["Filing Date"] = pd.to_datetime(filtered_data["Filing Date"], errors="coerce")
            #filtered_data["Filing Date"] = pd.to_datetime(filtered_data["Filing Date"], format="%m/%d/%Y")

            if selected_date:
                try:
                    selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
                    filtered_data = filtered_data[filtered_data["Filing Date"] >= selected_date]
                except ValueError:
                    # If date parsing fails, don't apply the date filter
                    pass
                
            job_statuses = filtered_data['Filing Status'].dropna().unique().tolist()
            if selected_boroughs:
                filtered_data = filtered_data[filtered_data["Borough"].isin(selected_boroughs)]
            
            # Get available contractor names after borough filtering
            contractor_names = filtered_data["Contractor Business Name"].dropna().unique().tolist()
            
            # Apply search filter if provided
            if search_query:
                filtered_data = filtered_data[filtered_data.apply(lambda row: check_search_match(row, search_query), axis=1)]
            
            # Apply contractor filter if provided
            if selected_contractor_name:
                filtered_data = filtered_data[filtered_data["Contractor Business Name"].str.contains(selected_contractor_name, case=False, na=False)]
            
            # Apply keyword filters if provided
            if selected_keywords:
                pattern = "|".join(re.escape(word) for word in selected_keywords)
                filtered_data = filtered_data[filtered_data["Job Description"].str.contains(pattern, case=False, na=False)]
        except Exception as e:
            print(f"Error filtering data: {e}")
    
    # Pagination Logic
    page = int(form_data.get("page", 1))
    per_page = 100
    
    # Calculate total pages only if we have data
    if filtered_data.empty:
        total_pages = 0
        paginated_data = pd.DataFrame()
    else:
        total_pages = max(1, (len(filtered_data) // per_page) + (1 if len(filtered_data) % per_page else 0))
        
        # Make sure page is within valid range
        page = max(1, min(page, total_pages))
        
        # Slice Data for Current Page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, len(filtered_data))
        paginated_data = filtered_data.iloc[start_idx:end_idx]
    
    # Format date for template
    date_str = selected_date.strftime("%Y-%m-%d") if isinstance(selected_date, datetime) else selected_date
    
    return render_template("dobNOW.html",
                           data=paginated_data.to_dict(orient="records"),
                           boroughs=boroughs,
                           job_statuses=job_statuses,
                           contractor_names=contractor_names,
                           selected_date=date_str,
                           selected_boroughs=selected_boroughs,
                           selected_keywords=selected_keywords,
                           keyword_dict=keyword_dict,
                           search_query=search_query,
                           selected_contractor_name=selected_contractor_name,
                           initial_filter_applied=bool(selected_boroughs),
                           page=page,
                           total_pages=total_pages)

if __name__ == '__main__':
    app.run(debug=True)
