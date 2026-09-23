# in this file i essnetially deal with converting the master dictionary to and froma  string to the real native python data type dictionary and a couple other functions to load and save the calendar
# quite essential to the persistence fo the program

import json
from datetime import datetime
from datetime import date
# to save the data as json il need the json library


def load_existing_data():
    master_activity_dictionary_string = {}
    with open("calendar_data.json", "r") as file:
         master_activity_dictionary_string = json.load(file)
         return master_activity_dictionary_string
# load existing data simply returns the master activity dictionary string taht currently exists inside of the json file  

def save_calendar(master_activity_dictionary_string):
     with open("calendar_data.json", "w") as f:
          json.dump(master_activity_dictionary_string, f, indent=2)
# this opens the json file note the w meaning write, and then it simply dumps the mastewr activity dictionary string version into the file which is calendar_data.json with an indent of 2. this simply splits the json data by 2 spaces. by json data i mean specific dates with their list of activitiy dictiaonres 


def convert_string_to_date(master_activity_dictionary_string):
     master_activity_dictionary = {}
     for date in master_activity_dictionary_string:
        converted_date = datetime.strptime(date,"%Y-%m-%d").date()
        master_activity_dictionary[converted_date] = master_activity_dictionary_string[date]
     return master_activity_dictionary
# the above function is quite important, it makes sense to have two seperate dictionaries, one string one native python types (along wiht the "date" data type, used to access a specific dates lsit of activity dictionarys)
# anyway this function literally just converts the master activity dictionary string versin back into the native python type. again, important for when we are actually adding and editing the calendar. u

def convert_dictkey_to_string(master_activity_dictionary, master_activity_dictionary_string): # okay finally did this omds 
     for date in master_activity_dictionary:
          date_string = str(date)
          master_activity_dictionary_string[date_string] = []
          for activity_index in range (len(master_activity_dictionary[date])): # loops throough each date key inside of the mater activity ditionary. these are actual python date keys and not strings
            #    activity_to_add = master_activity_dictionary[date][activity_index]["Activity"]
            #    Start_Time_to_add = master_activity_dictionary[date][activity_index]["Start_Time"]
            #    End_Time_to_add = master_activity_dictionary[date][activity_index]["End_Time"]
            #    Category_to_add = master_activity_dictionary[date][activity_index]["Category"] # dont actualyl ened any of this can just do it directly.
              
                    
            # temp_master_activity_string_dict = {"Activity": master_activity_dictionary[date][activity_index]["Activity"], "Start_Time" : master_activity_dictionary[date][activity_index]["Start_Time"], "End_Time" : master_activity_dictionary[date][activity_index]["End_Time"], "Category" : master_activity_dictionary[date][activity_index]["Category"]}
            # okayt with the line above i actually did not need it, all that is really doing is picking items up out of a box and then moving the items and then the box rather than the entire box. im taking the activities out, then adding them back
            # instead as you can see bellow the temporary activity string dict can just have the origional master activity dictionary information for a given date. because above you can see its the same thing, start time end time etc using the activity index and the date. but now i just use that idrectly. 
            # and then lastly i can just add that directly to the final master activity dictionary of strings. 


                temp_master_activity_string_dict = master_activity_dictionary[date][activity_index] # this goes into the old master actvitiy ddctionary, and gets the activity dictionary at that index (since one dayt has many activities) and then stores it in a variable
                master_activity_dictionary_string[date_string].append(temp_master_activity_string_dict) # then we take taht same temporary dictionary, access the master activity dictionary string witht he correspondign date, and then add the temporary diacitonary to taht date 
     return master_activity_dictionary_string
# and last but not least this does the opposite, converts the native python dictinoary type into a string. it does this in the opposite way. iterate through the master activity dictionary and then 




