# Weather app using openweathermap

# Takes city or zip code and returns current conditions and 4-day forecast
# documentation found at https://openweathermap.org/api

import requests, json, calendar
import datetime as dt
import configparser
import os

def getWeekDayFromUTC(utcTime):
    """ 
    Function takes time in UTC format and returns the weekday name

    """
    value = dt.datetime.fromtimestamp(utcTime)
    return calendar.day_name[value.weekday()]



# get parameters from config file
# first get the current directory
cur_dir = os.path.dirname(__file__)

# generate the absolute filepath of the output file
config_filename = "weather_app_config.txt"
config_filepath = os.path.join(cur_dir, config_filename)

# now get the info from the config file and set variables
parser = configparser.ConfigParser()
parser.read_file(open(config_filepath))
api_key = parser.get('Settings', 'api_key')
base_url = parser.get('Settings', 'url') + "?"
base_forecast_url = parser.get('Settings', 'forecast_url') + "?"
units_url = "&units=Imperial"
full_forecast_url = ""

# Prompt for city or zip code and build the urls
search_type = "xyz"
while search_type.upper() not in ("C","Z"):
    search_type = input("Get weather for (c)ity or (z)ip code: ")

if search_type.upper() == "C":
    city_name = input("Enter city: ")
    url = base_url + "appid=" + api_key + "&q=" + city_name + units_url
    full_forecast_url = base_forecast_url + "appid=" + api_key + "&q=" + city_name + units_url

elif search_type.upper() == "Z":
    zipcode = ""	
    while not zipcode.isdigit():
        zipcode = input("Enter zip code: ")

    url = base_url + "appid=" + api_key + "&zip=" + zipcode + units_url
    full_forecast_url = base_forecast_url + "appid=" + api_key + "&zip=" + zipcode + units_url


# GET DATA FOR CURRENT CONDITIONS.....
# get response object
response = requests.get(url)

# get weather data
data = response.json()

if data["cod"] != "404":
	# store the value of "main" 
    main = data["main"] 
  
    # store data values
    city_from_json = data["name"]
    cur_temp = round(main["temp"]) 
    cur_pressure = main["pressure"] 
    cur_humidity = main["humidity"]
    cur_wind = round(data["wind"]["speed"])
    cur_cloudiness = data["clouds"]["all"]
    cur_desc = data["weather"][0]["description"]

    print(f"\nCurrent conditions for {city_from_json}.........")
    print(f"Temperature: {cur_temp}")
    print(f"Outlook: {cur_desc} ({cur_cloudiness}% clouds)")
    print(f"Wind: {cur_wind} mph")
    print(f"Humidity: {cur_humidity}%")

else: 
    if search_type.upper() == "C":
    	print("City not found")
    else:
        print("Zip code not found")

    exit()

# NOW GET FORECAST.....
response = requests.get(full_forecast_url)

# get weather data
data = response.json()

if data["cod"] != "404":
    main = data["list"]
    
    highTemp = 0.0
    curDay = ""
    curDesc = ""
    curWind = 0.0
    curHumidity = 0
    curClouds = 0
    day1 = dt.datetime.now().strftime("%A")
    print("\n4-day forecast.........")

    # loop through data for each day and determine the highest temp and report it
    for item in main:
        running_day = getWeekDayFromUTC(item["dt"])
        # skip today's forecast since already provided that info in current conditions above
        if running_day == day1:
            #curDay = running_day
            continue

        elif running_day != curDay:
        	# since this is different day than previous iteration, display the temp and desc of previous day
            # the first day is the "current conditions" day; it will not a value yet for curDesc, so don't display data for first day here
            if curDesc != "":
                print(f"{curDay}:")
                print(f"\t{round(highTemp)}, {curDesc} ({curClouds}% clouds), {round(curWind)} mph wind, {curHumidity}% humidity")	

            curDay = running_day

            # reset variables
            curDesc = ""
            highTemp = 0.0

            # store the data corresponding to the max temp for day currently being looped through
            running_temp = item["main"]["temp"]
            if running_temp > highTemp:
                highTemp = running_temp
                curDesc = item["weather"][0]["description"]
                curWind = item["wind"]["speed"]
                curHumidity = item["main"]["humidity"]
                curClouds = item["clouds"]["all"]
        else:
            running_temp = item["main"]["temp"]
            if running_temp > highTemp:
                highTemp = running_temp
                curDesc = item["weather"][0]["description"]
                curWind = item["wind"]["speed"]
                curHumidity = item["main"]["humidity"]
                curClouds = item["clouds"]["all"]

    # COMMENTED 5TH DAY BELOW BECAUSE DATA MAY BE MISLEADING BASED ON TIME OF DAY THIS PROGRAM IS RUN
    # EXAMPLE: if this script is run at 7am, then data returned from website only contains early morning hours of 5th day
    #           (the later this script is run, then more data is available from website)
    # need to print the data for the 5th day because above code will not handle it
    # print(f"{curDay}:")
    # print(f"\t{round(highTemp)}, {curDesc} ({curClouds}% clouds), {round(curWind)} mph wind, {curHumidity}% humidity")
