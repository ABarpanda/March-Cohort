import requests

url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotelsByCoordinates"

querystring = {
    "latitude":"19.24232736426361",
    "longitude":"72.85841985686734",
    "adults":"1",
    "children_age":"0,17",
    "room_qty":"1",
    "units":"metric",
    "page_number":"1",
    "temperature_unit":"c",
    "languagecode":"en-us",
    "currency_code":"EUR",
    "location":"US"}

headers = {
	"x-rapidapi-key": "6e21947f9fmshee9ad4e3e587570p17e864jsn0958834a65e2",
	"x-rapidapi-host": "booking-com15.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())