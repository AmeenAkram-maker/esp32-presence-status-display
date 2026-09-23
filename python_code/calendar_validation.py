# this file mostly hadnles errors inside of the program with a variety of validate methods. those beign anctivity, time and the category. NOTE THAT THE CATEGORY VALIDATION HAS NOT FULLY BEEN IMPLEMENTEDM, ILL DO THAT IN THE FUTURE 


def Validate_Activity(Date_Of_Activity, Activity_Start, Activity_End, Editing_Index, master_activity_dictionary): 
    counter_for_current_activity_for_edit_activity = 0
    Activites_On_The_Day = master_activity_dictionary.get(Date_Of_Activity, [])
    new_activity_start_time_converted = convert_time_to_minutes(Activity_Start) # use my dedicated converting funciton to convert the clock time to acctual minutes so the computer can easily compare them
    new_activity_end_time_converted = convert_time_to_minutes(Activity_End) # do same for end time
    if(new_activity_start_time_converted >= new_activity_end_time_converted): # if the user tries to start an activity at 4 and end it at 2 that doesnt make sense, so reject that activiy
        return False
    for Activity in Activites_On_The_Day: # then i iterate through every activity on a given date.
        if counter_for_current_activity_for_edit_activity != Editing_Index: # this ciompares iuf the current activity is not the same as the activity we are editing
            existing_start_activity_time = convert_time_to_minutes(Activity["Start_Time"]) # if not then that means we ignore the activity we are editing because that would cause clashing issues comparing the activity againt itself. so convert the current start and end time to minutes 
            existing_end_time = convert_time_to_minutes(Activity["End_Time"])
            if(new_activity_start_time_converted < existing_end_time and new_activity_end_time_converted > existing_start_activity_time): # and now we actually check if there is a time clash. if there is return fals,e otherwise increment the editing activity index and do the loop again,. 
                return False
        counter_for_current_activity_for_edit_activity += 1
    return True
# as suggested by the name the valdiate activity validates an activity. it does this by checking start adn edn times. since an activity name can be anyhting, the only thing that cnan go wrong with it is the timing, and by that i mean clashes. two activities (in my calendar model cannot happen simultaneously.)
# 
def validate_time(time_to_validate): # validate time fucntion, this validates the actual time itself. someon cannot enter aa:55 or a%:5a or any other erroneous data. they also cannot enter 555:555 or any more numbers for example
    parts_of_time = time_to_validate.split(":")
    if(len(parts_of_time) != 2):
        return False
    try:
        hours, minutes = map(int, time_to_validate.split(":"))

    except ValueError:
        print("you did not enter a valid data type, you must enter a time in the format 00:00 - 23:59") # cannot enter invalid data like a string for either side of the colon for the time. 
        return False

    if(hours > 23 or hours < 0): # the user of course cannot enter a time taht is greate rthan 24 hours too sinuce tahts how many hours are in a day
        return False
    if(minutes > 59 or minutes < 0):
        return False
    return True

def validate_category(category_to_validate, categories): # this is the validate category function. the whole validate category and general category functionality needs to be implemented. but the vision is taht the user can only enter certain categories like "random", or "sport", or "UNIVERSITY", or "WORK"
    for category in categories:
        if(category_to_validate not in categories):
            print("the category you choose is invalid, try again")
            return False
    return True


def convert_time_to_minutes(time): # this of course creates an error. if the user enters a string. so ill use a try catch to make sure it is an integer, and then make sure it cna fall into a certain range. 
    hours, minutes = map(int, time.split(":"))
    return hours * 60 + minutes


