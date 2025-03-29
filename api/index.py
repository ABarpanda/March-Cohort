import sys
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import Main

app = FastAPI(
    title="Om Tour API",
    description="This the API documentation for Om tours",
    version="1.0.0",
    docs_url="/docs/",
    redoc_url="/redoc/"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_json_parse(json_str):
    try:
        # First try direct parse
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            fixed = json_str.replace("\'", '\"')  # Single to double quotes
            fixed = fixed.replace(",}", "}")    # Remove trailing commas
            return json.loads(fixed)
        except json.JSONDecodeError as e:
            print(f"Could not parse JSON. Error: {e}")
            print(f"Problematic JSON: {json_str[:200]}...")
            return None

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"}
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Om tours API!"}

@app.get("/itinerary/", response_model=dict)
async def get_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    number_of_people: int,
    purpose: str,
    budget: float,
    location: str,
    mode_of_transport: str,
):
    """
    Generate a travel itinerary with budget allocation
    
    Parameters:
    - destination: Destination city/country
    - start_date: Trip start date (YYYY-MM-DD)
    - end_date: Trip end date (YYYY-MM-DD)
    - number_of_people: Number of travelers
    - purpose: Trip purpose (vacation/business/etc)
    - budget: Total trip budget
    - location: Current location of travelers
    - mode_of_transport: Preferred transport mode
    
    Returns:
    - JSON itinerary with budget allocation
    """
    try:
        itenary = Main(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            number_of_people=number_of_people,
            purpose=purpose,
            budget=budget,
            location=location,
            mode_of_transport=mode_of_transport
        )
        itenary_data = safe_json_parse(str(itenary))
        print("Itenary data =", itenary_data)
        return JSONResponse(content=itenary_data)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to parse itinerary data"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate itinerary"
        )
