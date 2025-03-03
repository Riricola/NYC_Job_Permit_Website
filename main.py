from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import pandas as pd
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Set up template rendering
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")



# Ensure static directory exists before mounting
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    raise FileNotFoundError(f"Static directory not found: {static_dir}")


# Mount static files (for CSS, if needed)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# NYC Open Data API endpoint for DOB Job Applications
NYC_DATA_URL = "https://data.cityofnewyork.us/resource/ipu4-2q9a.json"


@app.get("/", response_class=HTMLResponse)
async def serve_form(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})

@app.post("/filter")
async def filter_data(request: Request, start_date: str = Form(...)):
    # Fetch data from NYC Open Data API
    response = requests.get(NYC_DATA_URL)
    data = response.json()

    # Convert to DataFrame for filtering
    df = pd.DataFrame(data)

    # Ensure 'filing_date' exists and filter by the start date
    if "filing_date" in df.columns:
        df["filing_date"] = pd.to_datetime(df["filing_date"], errors='coerce')
        df_filtered = df[df["filing_date"] >= pd.to_datetime(start_date)]
        filtered_data = df_filtered.to_dict(orient="records")
    else:
        filtered_data = []

    return templates.TemplateResponse("index2.html", 
            {"request": request, "data": filtered_data, "selected_date": start_date})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
