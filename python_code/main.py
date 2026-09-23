# this is the main python file, in here ill use all the smaller files in order to create a simple indefinite loop where the entiore application ultoimately runs
from calendar_logic import handle_user_choosing_custom_month
from calendar_logic import handle_user_choosing_day_of_month
from calendar_logic import handle_day
from calendar_logic import get_current_date_information
from calendar_logic import handle_main_month_choice
from json_storage import save_calendar
from json_storage import convert_dictkey_to_string
from json_storage import convert_string_to_date
from json_storage import load_existing_data
from calendar_UX import display_day
from calendar_data_store import master_activity_dictionary, master_activity_dictionary_string
# all the necessary core fucntions needed to run the program (note said functions depend ont he smaller functions within them, they are composite functions)
 

finished = False # i create a flag variable to track when the program SHOULd end (i use the return value of the handle_day to change this value in the loop)

master_activity_dictionary_string = load_existing_data() # load the existing json data that the user has entered as a string dictionary
master_activity_dictionary = convert_string_to_date(master_activity_dictionary_string) # then  convert that string dictionary into a non string dictionary where the keys are actual dates etc so we c access the specific fields etc inside of the program
currentyear,currentmonth, currentday, monthgrid = get_current_date_information() # get the current date information to use inside the loop as we need current year.

while finished == False: # while the user has not entered 4 or terminated the program
    month_choice = handle_main_month_choice() # get the users choice for what month to pick, either current month or one of their choice
    if month_choice == 1:
        date_of_activity = handle_user_choosing_day_of_month(currentyear, currentmonth) # call the main function which handles the uesrs action when they choose the current month , it will ask them for a day to do this on 
    else:
        choice_of_month = handle_user_choosing_custom_month()# a seperate function is called to ahndle the user choosing a specific month and hence a specific day of that month
        date_of_activity = handle_user_choosing_day_of_month(currentyear, choice_of_month)
    finished = handle_day(date_of_activity, master_activity_dictionary) # the handle day is a crucial function whiich consists of several other handle functions to handle the user editing removing or adding an activity. the user can also press 4 to elave the program if they want too

master_activity_dictionary_string = convert_dictkey_to_string(master_activity_dictionary, master_activity_dictionary_string) # now that we have finished editing and manipulating the master dictionary (since this only runs when the whiole loop ends) we convert this back to the string version of the dictionary so that we can save it in json

save_calendar(master_activity_dictionary_string) # and lastly clal the save calendar function which saves the calendar in json
