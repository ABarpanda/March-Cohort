from smolagents import tool
import requests
from datetime import datetime, date, timedelta
import json

@tool
def multiply_two_numbers(arg1:int, arg2:int)-> str: #it's import to specify the return type
    #Keep this format for the description / args / args description but feel free to modify the tool
    """A tool that multiplies 2 numbers
    Args:
        arg1: the first argument
        arg2: the second argument
    """
    return arg1*arg2

@tool
def next_seven_day_forecast(lat: float, long: float) -> list:
    """Fetches the weather forecast for the next seven days.

    Args:
        lat: Latitude of the location.
        long: Longitude of the location.

    Returns:
        A list of dictionaries containing date, max temperature, min temperature, and precipitation.
    """
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": long,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Asia/Kolkata"
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        daily_data = data.get("daily", {})

        return [
            {
                "date": date,
                "max_temperature": temp_max,
                "min_temperature": temp_min,
                "precipitation": precipitation
            }
            for date, temp_max, temp_min, precipitation in zip(
                daily_data.get("time", []),
                daily_data.get("temperature_2m_max", []),
                daily_data.get("temperature_2m_min", []),
                daily_data.get("precipitation_sum", [])
            )
        ]

    return {"error": "Unable to fetch data", "status_code": response.status_code}

@tool
def one_day_forecast(lat: float, long: float, target_date: str) -> list:
    """Fetches the weather forecast for a specific date.

    Args:
        lat: Latitude of the location.
        long: Longitude of the location.
        target_date: The target date in YYYY-MM-DD format.

    Returns:
        A list of dictionaries containing date, max temperature, min temperature, precipitation, and sunshine duration.
    """
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": long,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,sunshine_duration",
        "timezone": "Asia/Kolkata",
        "start_date": target_date,
        "end_date": target_date
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        daily_data = data.get("daily", {})

        return [
            {
                "date": date,
                "max_temperature": temp_max,
                "min_temperature": temp_min,
                "precipitation": precipitation,
                "sunshine_duration": f"{sunshine / 3600:.2f}"
            }
            for date, temp_max, temp_min, precipitation, sunshine in zip(
                daily_data.get("time", []),
                daily_data.get("temperature_2m_max", []),
                daily_data.get("temperature_2m_min", []),
                daily_data.get("precipitation_sum", []),
                daily_data.get("sunshine_duration", [])
            )
        ]

    return {"error": "Unable to fetch data", "status_code": response.status_code}


@tool
def ambient_judgement(lat: float, long: float, target_date: str) -> list:
    """Fetches weather data for four days before and after a specified date.

    Args:
        lat: Latitude of the location.
        long: Longitude of the location.
        target_date: The target date in YYYY-MM-DD format.

    Returns:
        A list of dictionaries containing date, max temperature, min temperature, precipitation, and sunshine duration.
    """
    date_obj = datetime.strptime(target_date, "%Y-%m-%d")
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": long,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,sunshine_duration",
        "timezone": "Asia/Kolkata",
        "start_date": (date_obj - timedelta(days=4)).strftime("%Y-%m-%d"),
        "end_date": (date_obj + timedelta(days=4)).strftime("%Y-%m-%d")
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        daily_data = data.get("daily", {})

        return [
            {
                "date": date,
                "max_temperature": temp_max,
                "min_temperature": temp_min,
                "precipitation": precipitation,
                "sunshine_duration": f"{sunshine / 3600:.2f}"
            }
            for date, temp_max, temp_min, precipitation, sunshine in zip(
                daily_data.get("time", []),
                daily_data.get("temperature_2m_max", []),
                daily_data.get("temperature_2m_min", []),
                daily_data.get("precipitation_sum", []),
                daily_data.get("sunshine_duration", [])
            )
        ]

    return response.json()


headers = {
    "x-rapidapi-key": "6e21947f9fmshee9ad4e3e587570p17e864jsn0958834a65e2",
    "x-rapidapi-host": "irctc1.p.rapidapi.com"
}

@tool
def trainBetweenStations(fromStationCode: str, toStationCode: str, dateOfJourney: str) -> str:
    """Fetches train details between two stations on a specified date.

    Args:
        fromStationCode: Source station code.
        toStationCode: Destination station code.
        dateOfJourney: Date of travel in YYYY-MM-DD format.

    Returns:
        JSON-formatted string with train information.
    """
    url = "https://irctc1.p.rapidapi.com/api/v3/trainBetweenStations"
    querystring = {"fromStationCode": fromStationCode, "toStationCode": toStationCode, "dateOfJourney": dateOfJourney}

    response = requests.get(url, headers=headers, params=querystring)
    return json.dumps(response.json(), indent=4)

@tool
def checkSeatAvailability(classType: str, quota: str, fromStationCode: str, toStationCode: str, trainNo: str, date: str) -> str:
    """Checks seat availability on a specific train.

    Args:
        classType: Class type (e.g., "SL", "3A").
        quota: Seat quota (e.g., "GN", "TQ").
        fromStationCode: Source station code.
        toStationCode: Destination station code.
        trainNo: Train number.
        date: Date of travel in YYYY-MM-DD format.

    Returns:
        JSON-formatted string with seat availability.
    """
    url = "https://irctc1.p.rapidapi.com/api/v1/checkSeatAvailability"
    querystring = {"classType": classType, "fromStationCode": fromStationCode, "quota": quota, "toStationCode": toStationCode, "trainNo": trainNo, "date": date}

    response = requests.get(url, headers=headers, params=querystring)
    return json.dumps(response.json(), indent=4)


if __name__=="__main__":
    print(trainBetweenStations("ROU","JSG","2025-03-23"))