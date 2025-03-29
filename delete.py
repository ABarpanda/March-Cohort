# import requests

# url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotelsByCoordinates"

# querystring = {
#     "latitude":"19.24232736426361",
#     "longitude":"72.85841985686734",
#     "adults":"1",
#     "children_age":"0,17",
#     "room_qty":"1",
#     "units":"metric",
#     "page_number":"1",
#     "temperature_unit":"c",
#     "languagecode":"en-us",
#     "currency_code":"EUR",
#     "location":"US"}

# headers = {
# 	"x-rapidapi-key": "6e21947f9fmshee9ad4e3e587570p17e864jsn0958834a65e2",
# 	"x-rapidapi-host": "booking-com15.p.rapidapi.com"
# }

# response = requests.get(url, headers=headers, params=querystring)

# print(response.json())

import json
response = {'trip_summary': {'from': 'Mumbai', 'to': 'Goa', 'travel_dates': ['2025-04-01', '2025-04-10'], 'total_budget': 20000.0, 'currency': 'INR'}, 'transport': {'selected': 'flight', 'options': [{'mode': 'flight', 'cost': 9000.0, 'duration': '1h30m'}]}, 'budget': {'transport': 9000.0, 'accommodation': 6000.0, 'activities': 4000.0, 'food': 3000.0, 'contingency': 2000.0, 'remaining': -4000.0}, 'itinerary': [{'day': 1, 'date': '2025-04-01', 'activities': ['Beach exploration'], 'transport_used': 'taxi'}, {'day': 2, 'date': '2025-04-02', 'activities': ['Museum visit'], 'transport_used': 'taxi'}, {'day': 3, 'date': '2025-04-03', 'activities': ['Waterfall visit'], 'transport_used': 'taxi'}, {'day': 4, 'date': '2025-04-04', 'activities': ['Waterfall visit'], 'transport_used': 'taxi'}, {'day': 5, 'date': '2025-04-05', 'activities': ['Waterfall visit'], 'transport_used': 'taxi'}, {'day': 6, 'date': '2025-04-06', 'activities': ['Waterfall visit'], 'transport_used': 'taxi'}, {'day': 7, 'date': '2025-04-07', 'activities': ['Waterfall visit'], 'transport_used': 'taxi'}, {'day': 8, 'date': '2025-04-08', 'activities': ['Waterfall visit'], 'transport_used': 'taxi'}, {'day': 9, 'date': '2025-04-09', 'activities': ['Waterfall visit'], 'transport_used': 'taxi'}, {'day': 10, 'date': '2025-04-10', 'activities': ['Waterfall visit'], 'transport_used': 'taxi'}]}
def safe_json_parse(json_str):
    try:
        # First try direct parse
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            fixed = json_str.replace("\'", '\"')  # Single to double quotes
            fixed = fixed.replace(",}", "}")    # Remove trailing commas
            return (fixed)
        except json.JSONDecodeError as e:
            print(f"Could not parse JSON. Error: {e}")
            print(f"Problematic JSON: {json_str[:200]}...")
            return None

response = safe_json_parse(str(response))
# print(response)
print(json.loads(str(response)))