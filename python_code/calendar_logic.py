# this is the file which contains all the core calendar logic, i.e manipulating days getting user input managing that input editing the days themselves, adding the activities removing activities etc
from datetime import datetime 
from datetime import date
import calendar
from calendar_validation import validate_time
from calendar_validation import Validate_Activity
from calendar_validation import validate_category
from calendar_UX import show_success
from calendar_UX import show_warning
from calendar_UX import show_prompt
from calendar_UX import display_day
from calendar_UX import show_edit_menu
from calendar_UX import Existing_Times_Of_Activity
from calendar_UX import get_user_menu_choice_for_none_empty_day
from calendar_data_store import master_activity_dictionary
# inside of this rather large file i need to reference most other files to access things. from calendar ux we require all the functions thods to of course make use of them.

months_of_year = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]
# i have an array of the months of the year so i can iterate through them and then use the index to mention the month the user chose 

def get_current_date_information():
    current_time = datetime.now() 

    current_year = current_time.year
    current_month = current_time.month
    current_day = current_time.day
    month_grid = calendar.monthcalendar(current_year, current_month)

    return current_year, current_month, current_day, month_grid
# the above method gets the year month day and month grid object for the current date. we need this for when the user clicks the menu option 1. that being they want the current month informatioun

def edit_activity_name(master_activity_dictionary, date_of_activity, date_to_edit):
     for index, activity_dict in enumerate(date_to_edit, start=1):
          print(index, " - ", activity_dict["Activity"])
     show_prompt("what is the activity you want to replace? :")
     What_Specific_Activities_On_The_Date = int(input("> "))
     Editing_Index = What_Specific_Activities_On_The_Date - 1
     show_prompt("Enter the new activity you want: ") 
     New_Activity = (input("> "))
     if(What_Specific_Activities_On_The_Date < 1 or What_Specific_Activities_On_The_Date > len(master_activity_dictionary[date_of_activity])):
        show_warning("you entered a number out of range, please try again")
        return
     master_activity_dictionary[date_of_activity][Editing_Index]["Activity"] = New_Activity # just realised all i needed to do is access the activcityt specifically, there was another layer i was missing 
     display_day(date_of_activity, master_activity_dictionary) # display the day after the user is done 
# a seperate edit activity funtion soley for editing the name e.g. from boxing to football. it does this by iterating through the activities indside of the day, getting the input it also performs checks to see if that activity is valid.


def edit_activity_time(master_activity_dictionary, Date_To_Edit, Date_of_Activity):
        for activity_dict in Date_To_Edit:
            print(activity_dict["Start_Time"], "-", activity_dict["End_Time"])
        try:
            show_prompt("what is the activity with the times you want to replace? : ")
            What_Specific_Times_On_The_Date = int(input("> "))
        except ValueError:
            show_warning("you did not enter a valid integer, try again.")

        show_prompt("Enter the new start you would like: ")
        New_Start_Time = input("> ")
        show_prompt("Enter the new end time you would like: ")
        New_End_Time = input("> ")
        Editing_Index = What_Specific_Times_On_The_Date - 1

        if(validate_time(New_Start_Time) and validate_time(New_End_Time)):
            if(Validate_Activity(Date_of_Activity, New_Start_Time, New_End_Time, Editing_Index, master_activity_dictionary)): # just realised again this function wont work for editing activity  because editing an activity will mean when writing a new time for the same activity the valdiate activity will treat both as seperate activities and hence reject them just as if it was adding a new activity. we dont want this, we want validate activity to allow functions that are being edited because there wont be a clash <== wrong that only works if theres one, checking against itself. 
                master_activity_dictionary[Date_of_Activity][Editing_Index]["Start_Time"] = New_Start_Time 
                master_activity_dictionary[Date_of_Activity][Editing_Index]["End_Time"] = New_End_Time # isntea dof editing index it was the what specific activities ont he date but that is not right because indexing starts at 0 so the user needs to pick 1 2 or 3, 1 means 0 which means the activity, 2 means 1 which is the time adn 3 means 2 whihc is teh category 
                display_day(Date_of_Activity, master_activity_dictionary)
            else: 
                 show_warning(message = "you did not enter a valid integer, try again.")
                 finished = False
# similarly a seperate edit activity function soley for editing the time, this has somewhat added complexity sincc there is two parts to the time, the star and edn time. 


def edit_activity_category(Date_of_Activity, Date_To_Edit, master_activity_dictionary):
    for index,activity_dict1 in enumerate(Date_To_Edit, start=1):
        print(index, " - ", activity_dict1["Category"])
    show_prompt("what is the activity with the category you want to replace? :")
    What_Specific_Category_On_The_Date = int(input("> "))
    Editing_Index = What_Specific_Category_On_The_Date - 1 # this was activities instead of category, caused an error 
    show_prompt("Enter the new category you would like: ")
    New_Category = input("> ")
    if(What_Specific_Category_On_The_Date < 1 or What_Specific_Category_On_The_Date > len(master_activity_dictionary[Date_of_Activity])):
        show_warning("you entered a number out of range, please try again")
        return
    master_activity_dictionary[Date_of_Activity][Editing_Index]["Category"] = New_Category
    display_day(Date_of_Activity, master_activity_dictionary)
# again, a similar funtion but for the category, the user may want to cahgne taht too.


def Edit_Activity(Date_of_Activity , master_activity_dictionary): 
            Date_To_Edit = master_activity_dictionary[Date_of_Activity] 
            Choice_of_what_to_edit = show_edit_menu()
            if(Choice_of_what_to_edit == 1):
                edit_activity_name(master_activity_dictionary, Date_of_Activity, Date_To_Edit)
            elif(Choice_of_what_to_edit == 2):
                 edit_activity_time(master_activity_dictionary, Date_To_Edit,  Date_of_Activity)
            elif(Choice_of_what_to_edit == 3): 
                 edit_activity_category(Date_of_Activity, Date_To_Edit, master_activity_dictionary)
            show_prompt("would you like to alter/change any other day/activity?  \n 1 - yes: \n 2 - no: \n")
            Finished_Number_Input = input("> ")
            if(Finished_Number_Input == 1):
                finished = False
            if(Finished_Number_Input == 2):
                finished = True   
# now before all of the sub edit activities all of the logic was inside of edit_activit. but i insetad made seperate functions and then based on what the user wants to edit via their input i simply call the corresponding fucntion 


def Add_Activity(master_activity_dictionary, Date_Of_Activity, name, start, end, category):
    # New_Activity = input(print("Write the name of the activity you would like to add: "))
    # Start_Time = input(print("Write the start time of the activity you would like to add: "))
    # End_Time = input(print("Write the end time of the activity you would like to add: "))
    # Category = input("What is the category of this activity: ")
    # just realised the above is actually bad practice. i should not be getting the activity data inside of the add activity function, all this function should do is just add the activity data to the dictionary. but ensure its valid so no time overlaps or dupliates / being in the correct format etc.
    Temp_Dictionary = {"Activity" : name , "Start_Time" : start , "End_Time" : end , "Category" : category} # okay this is actually the final function, we need to create a temporary small dictionary that has the new activity with all thed etails
    if(Date_Of_Activity not in master_activity_dictionary): # but then we need to checkf or teh case where there is not a date for that activity, if that is the case then just create an empty lsit for this date and then add a dictionary to the list. because remember, the core data structure is  adictionary of lists of dictionaries. where the entry to the list dictionaries is the date.
        master_activity_dictionary[Date_Of_Activity] = []

    master_activity_dictionary[Date_Of_Activity].append(Temp_Dictionary)
    # was jsut about to add to the master dictionary but i need to know the date for that, so im immeditately thinking of finding it dependong on whether the user picks 1 or 2 initially, and then what i need to od is use the pure date ob ject provided from the datetime librariy, it is dateime.date(year, month, day
    # now i can just add the activity right away, but what if the date does not exist yet in the dictionary, i need to do that check first 
    
def Get_Activity_Information():
    show_prompt("Enter the details of your new activity.")
    New_Activity = input("Activity name: ").upper()
    Start_Time = input("Start time (HH:MM): ").upper()
    End_Time = input("End time (HH:MM): ").upper()
    Category = input("Category: ").upper()
    return New_Activity, Start_Time, End_Time, Category
# this gets all information for the new activity that the user wants to add

def remove_activity(Date_of_Activity, master_activity_dictionary): # jsut realised that after you remove the activity you should show the day. after the activity has been removed. 
   if(does_a_given_day_have_activities(Date_of_Activity, master_activity_dictionary) == False):
    #    print("there are no activities on this day syou cannot remove activities.") had this but no, prints too many times. 
       return
   show_prompt("what is the activity you want to remove")
   Activity_to_remove_index = int(input("> "))
   if(Activity_to_remove_index < 1 or Activity_to_remove_index > len(master_activity_dictionary[Date_of_Activity])):# i was thinking of using length because we are checking the index. but tried not in which is wrong cus thats membership not like checking if the index is inside that date
       show_warning( "the number you just entered does not correspond to an activity, try again.")
       return
#    activities_on_the_Day = master_activity_dictionary.get(Date_of_Activity, [])
#    if(len(activities_on_the_Day)) == 0:
#     print("there are no activities on this day") # all of this checking was there before i made the new does_a_given_day_have_Activities function. 
#     return
   del master_activity_dictionary[Date_of_Activity][Activity_to_remove_index-1]
   return master_activity_dictionary


    
def does_a_given_day_have_activities(DATE_OF_ACTIVITY, master_activity_dictionary):
    activities_on_the_day = master_activity_dictionary.get(DATE_OF_ACTIVITY, [])
    if(len(activities_on_the_day)) == 0:
        return False
    else:
        return True
# we need to know if a given day has activities so that then we know for example if we even need to display the activities for that day.

def get_user_menu_choice_for_Day(date_of_activity, master_activity_dictionary):

    if does_a_given_day_have_activities(date_of_activity,master_activity_dictionary):
        display_day(date_of_activity,master_activity_dictionary)
        return get_user_menu_choice_for_none_empty_day()

    else:
        show_prompt("This day has no activities yet.\n""1 = Add Activity\n""4 = Exit and save")

        while True:
            try:
                choice = int(input("> "))
                if choice not in [1,4]:
                    show_warning("Please choose either 1 or 4.")
                    continue
                return choice
            except ValueError:
                show_warning("Please enter a valid number.")
# the above functiuon gets the user choice for a given day but uses the previous function does a given day have activities to determine waht to sayt to the user. (i.e simply add an ativity or exit)
# and now insid eof handle day you see the individual menu choice logic, im going to split that further so that i have one for each day 

def handle_add_activity(Date_Of_Activity, master_activity_dictionary):
    activity_name, start, end, category = Get_Activity_Information()
    if(validate_time(start) and validate_time(end)):
         if(Validate_Activity(Date_Of_Activity, start, end, -1, master_activity_dictionary)):
                Add_Activity(master_activity_dictionary, Date_Of_Activity, activity_name, start, end, category)
                show_success(f"You have added the activity {activity_name} "f"on {Date_Of_Activity} "f"from {start} to {end}.")
                display_day(Date_Of_Activity,master_activity_dictionary)
         else:
            show_warning("That activity clashes with an existing activity.")
            Existing_Times_Of_Activity(
    Date_Of_Activity,master_activity_dictionary)       
    else:
         show_warning("you entered an incorrect time")
# this handles the user adding ana ctivity since seeral things can go wrong, i.e entering an activity with invalid times etc. 

def handle_remove_activity(Date_Of_Activity, master_activity_dictionary):
        display_day(Date_Of_Activity, master_activity_dictionary)
        while True:
            try:
                remove_activity(Date_Of_Activity, master_activity_dictionary)
                break
            except ValueError:
                show_warning("you did not enter a valid input, you must enter a number corresponding with an activity on the day.")
        display_day(Date_Of_Activity, master_activity_dictionary)   
# now here i do the same but for rmeoving the activity, again this is also important because the remove activity function can break which is why we use error handling.  e.g. the user enters a string insetead of a number which corresponds to what activity they want to remove on a certain day


def handle_edit_activity(Date_Of_Activity, master_activity_dictionary):
    
    while True:
        try:
            Edit_Activity(Date_Of_Activity, master_activity_dictionary)
            break
        except ValueError:
            show_warning("you did not enter a valid integer, you must choose a correct activity to replace by a number.")
# handling the edit activity function needs a seperate method too, again because that can go wrong the user can enter erroenous data

def handle_main_month_choice():
      while True: # nver had this ebfore, added it during error handlign for string input to month_choice, reason why it exists is simply because we can repeatedly ask for the input. without while true month choice does not exist and hence we get an erorr. 
        try:
            show_prompt("Would you like the current month(1), or a month of your choice(2): ") # ask the user, this can easily fail hence the try except
            month_choice = int(input("> "))
                 # this technicalyl does catch the error BUT month_choice does not exist for the next if statement,s o i need to use a new technique of just breaking.
            if(month_choice != 1 and month_choice != 2): # only two valid options
                show_warning("you must enter either 1 or 2 for the current month or custom month respectively, try again")
                continue # so when 
            break
                 # okay just putting a commenbt here, wihtout while true if user enters 1 then it goes straight thourhg no problem, but if they enter a string
                 # then month_choice is never actually created hencewhy the code breaks and says it is not defiend, the while loop prevents that
                 # this is how, so basically finished == false, thats true, so while thats true, ask for input, if input is aiowdjoaiuwd then we jump to except and print. now that except has finished we dont break or continue. we are at the bottom of the while loop, so go back to the top
                 # is true true? yes, so keep asking, if the user enters 55, then the initial try doesnt break BUT that is not 1 or 2. so we print to console and then continue, this jumps to the beginning og the current loop iteration. this is all part of the while loop
                 # so cotinue basically runs to just after the while true bit.  where we ask again, so that works jsut fine. and finally if the user enters something valid, we dont enter that if statement, we just break, and break exits the current loop, at whihc point the month_choice exists so we can compare it.
        except ValueError:
            show_warning("you need to enter a number, do not enter a letter or symbol.")
      return month_choice
# by now youn shopuld see why i have these "handle" functions, they are all essentialy existing functions just used in a try except manner incase the user enters an incorrect or invalid input. 

def handle_user_choosing_day_of_month(year, month):
     print(calendar.month(year, month))
     while True:
        try:
            show_prompt("please choose a day of the month")
            choice_of_day = input("> ")
            integer_choice_of_day = int(choice_of_day)
            Date_Of_Activity = date(year, month, integer_choice_of_day)
            break
        except ValueError:
            show_warning("you did not enter a valid day. enter a value between 1 and 31. ")
     return Date_Of_Activity

def handle_user_choosing_custom_month():
     currentyear, currentmonth, currentday, monthgrid = get_current_date_information()
     print(calendar.calendar(currentyear))
     while True:
        try:
            show_prompt("choose a month you would like to see 1 - 12 :")
            choice_of_month = int(input("> "))
            if(choice_of_month > 12 or choice_of_month < 1):
                show_warning("enter a number within a valid range, 1 - 12:")
                continue
            break
        except ValueError:
            show_warning("you did not enter an integer try again")
     custom_month_choice = months_of_year[choice_of_month-1]
     show_success(f"You have chosen {custom_month_choice}")
     print(calendar.month(currentyear, choice_of_month))
     return choice_of_month
  
def handle_day(date_of_activity, master_activity_dictionary):
        
        menu_choice = get_user_menu_choice_for_Day(date_of_activity,master_activity_dictionary)

        if(menu_choice == 1):
            handle_add_activity(date_of_activity, master_activity_dictionary)
        elif(menu_choice == 2):
            handle_remove_activity(date_of_activity, master_activity_dictionary)
        elif(menu_choice == 3):
            handle_edit_activity(date_of_activity, master_activity_dictionary)
        elif(menu_choice == 4):
             return True
        
        return False

