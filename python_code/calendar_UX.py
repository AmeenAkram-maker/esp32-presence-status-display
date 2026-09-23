# this is a seperate file which mostly contaisn functions which make existing prompts and outputs to the terminal appear nicer. e.g. instead of simply writing 
# that the user enters erroneous data, the new fucntion show_warning prints it in bold red. with a red box/warning
from rich import print
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
# the above are all the libraries and moduels we need in order to make the ux file/

console = Console()


def show_success(message):
    console.print(Panel(f"[bold green]{message}[/bold green]",title="✓ Success",border_style="green"))
# for a sucessful mesage. i.e you have sucessfulyl added an event on x day from z time to y time. this new formatted function will be called.

def show_warning(message):
    console.print(Panel(f"[bold red]{message}[/bold red]",title="⚠ Warning",border_style="red"))
# similarly for a warning message, i.e you entered incorrect data this new function will wanr you.

def show_prompt(message):
    console.print(Panel(f"[bold blue]{message}[/bold blue]",title="Input Required",border_style="blue"))
# priompts specifically hvae a unique colour which makes them appweare to the user more clearly. 

def display_day(date_of_activity, master_activity_dictionary):
    activities = master_activity_dictionary.get(date_of_activity,[])

    if len(activities) == 0:
        console.print(Panel("[yellow]No activities scheduled for this day.\n""You can add a new activity.[/yellow]",title="Empty Day",border_style="yellow"))
        return
    
    table = Table(title=f"📅 {date_of_activity.strftime('%A %d %B %Y')}",title_style="bold cyan")

    table.add_column("#", justify="center")
    table.add_column("Activity", style="bold")
    table.add_column("Start", justify="center")
    table.add_column("End", justify="center")
    table.add_column("Category")

    for index, activity in enumerate(activities, start=1):
        table.add_row(str(index),activity["Activity"],activity["Start_Time"],activity["End_Time"],activity["Category"])
        console.print(table)

# this is simply a fucntion to show the day, before this function i would show the days by writing the different activities with their respective times. this creates a table object from the rich library which formats the data ina table (since of course there can be several activities and times so a table/matrix makes sense)

def show_empty_day():
    console.print(Panel("[yellow]No activities scheduled for this day.\n""You can add a new activity.[/yellow]",title="Empty Day",border_style="yellow"))
# before i had this just not explicitly. i would simply output that there are no activities in this day. but this jsut formats that nicer in again a distinct colour to make ti clearer for the user

def Existing_Times_Of_Activity(Date_Of_Activity,master_activity_dictionary):
    activities_on_day = master_activity_dictionary.get(Date_Of_Activity,[])

    table = Table(title="Existing Activities",title_style="bold red")
    table.add_column("Activity")
    table.add_column("Time")

    for activity in activities_on_day:
        table.add_row(activity["Activity"],f'{activity["Start_Time"]} - {activity["End_Time"]}')
        console.print( Panel(table,title="⚠ Time Conflict",border_style="red"))
# before i used text to show the user that there were existing actigites which clash with the activity that they want toa dd. this new method formats it 



def show_day_menu(has_activities):

    if has_activities:
        console.print(Panel("[green]1[/green] - Add Activity\n""[red]2[/red] - Remove Activity\n""[yellow]3[/yellow] - Edit Activity\n""[blue]4[/blue] - Exit",title="Day Actions",border_style="cyan"))

    else:
        console.print(Panel("[green]1[/green] - Add Activity\n""[blue]4[/blue] - Exit",title="Empty Day",border_style="blue"))
# a nicer method to show the user the options they cna do for taht day. a conditional is required with the has activities because on  n empty date yo cannot remove any activities sinc ethere are none  


def show_edit_menu():

    console.print(Panel("[green]1[/green] - Activity Name\n""[yellow]2[/yellow] - Time\n""[magenta]3[/magenta] - Category",title="Edit Activity",border_style="blue"))
    while True:
        try:
            Choice_of_what_to_edit = int(input("> "))

            if Choice_of_what_to_edit < 1 or Choice_of_what_to_edit > 3:
                show_warning("you must enter 1, 2, or 3. please try again")
                continue

            return Choice_of_what_to_edit

        except ValueError:
            show_warning("you must enter a number. please try again")
# in this method and in others inside of this file i do take inputs but i do not do anything with the input. i simply use other ux methods to convey to the user certain things so they are away of the flow of the program. i.e they enter something incorrect, a red message comes up telling them to enter again etc


def show_calendar_information(message):
    console.print(Panel(f"[cyan]{message}[/cyan]",title="Calendar",border_style="cyan"))
# here i show the claendar to the user  

def get_user_menu_choice_for_none_empty_day():

    console.print(Panel("[green]1[/green] - Add Activity\n""[red]2[/red] - Remove Activity\n""[yellow]3[/yellow] - Edit Activity\n""[blue]4[/blue] - Exit",title="Day Actions",border_style="cyan"))

    while True:
        try:
            choice = int(input("Choose an action: "))
            
            if choice not in [1,2,3,4]:
                show_warning("Enter a number between 1 and 4.")
                continue
            return choice
        
        except ValueError:
            show_warning("Please enter a valid number.")

# and lastly this method gets the choice from the user for a non empty day, again the distinction is made because the user can remove or edit existing activities.