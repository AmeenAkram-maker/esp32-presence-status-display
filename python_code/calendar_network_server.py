# import requests 
# from calendar_data_store import master_activity_dictionary
# from calendar_logic import get_current_date_information # same here cna just load old!!
# from datetime import date
# from json_storage import load_existing_data # can just reuse my old loading function!!!

# master_activity_dictionary = load_existing_data()




# # test_calendar_data = {
# #     "Date": "2026-08-10",
# #     "Activity": "BOXING",
# #     "Start_Time": "14:00",
# #     "End_Time": "15:00",
# #     "Category": "SPORT"
# # }

# year, month, day, grid = get_current_date_information()

# current_date = date(year, month, day)
# current_date_string = str(current_date)

# list_of_currentday_activities = master_activity_dictionary[current_date_string]
# # this causes the information to not be displayed because im getting a list of dictionaries, not just one dictionary. 
# print(list_of_currentday_activities)
# while True:
#     try:
#         response = requests.post("http://192.168.0.108/data", json=list_of_currentday_activities, timeout=5 )
#         print("esp32 reponse", response.text)
        
#     except requests.exceptions.RequestException:
#         print("could not connect to the esp32s wifi network, waiting.....")



# this file is the bridge between the esxp32 hardware and the json data. it simply constantly sends  post requests to the http server, sending the STRING master activitonary dctionary data. since wifi sends bytes and does not dnerstand what a python date is.

import requests # we need the requests library to send the requests to the http server
import time # we also need time because we need to wait before sending another request (instwead of hammering the esp32 wiht requests every second)

from calendar_logic import get_current_date_information
from datetime import date
from json_storage import load_existing_data
# and similarly to other files we need certain functions 

year, month, day, grid = get_current_date_information() # get the current date information so that we can form a current date string 

current_date = date(year, month, day) 
current_date_string = str(current_date) # which we do right here 

 # then i create an indefinite loop to constantly request the esp32 to send data
while True:

    
    master_activity_dictionary = load_existing_data() # load the existing data inside of the calendar 
   
    list_of_currentday_activities = master_activity_dictionary.get(current_date_string,[]) # then i get the list of activities for the current day since that is exaclt ywhat the responsibility of the display is  
    print("Current activities:", list_of_currentday_activities) # just for debugging puirpsoes, to see if there were any json parsing issues. 

    try:
        response = requests.post("http://192.168.0.108/data",json=list_of_currentday_activities,timeout=5) # i use the ip and the ednpoint defiend in the esp32 sender program at /data. and the ip assigned to server by my router. the json being sent is the list of the activities and i have a timeout. 
        #' requests.post sends the json packet to the esp32s ip address. and when the esp32 recieves it a response is reated. this contains headers status codes and the actual message. then the .text takes the message from teh reply package as a python string and then we can print it to the terminal to see what the esp32 said. 
        print("esp32 response:", response.text) 

    except requests.exceptions.RequestException: # if the esp32 does not respond in 5 seconds or fails to connect then python will skip the try block and print that we could not connect to teh esp32s wifi network. helps fr debugging btu allso makes the system functional since without it with a crash we wold be waiting for 5 seconds every time .

        print("could not connect to the esp32s wifi network, waiting.....")
    # Don't hammer the ESP32 with requests constantly.
    time.sleep(5)

