Assignment 7

This is a simple application program for the Airline database.



Version of Python: 3.6 (64 bit)



How to use this application: 

1. Right click on the file to 'Edit with IDLE 3.6'. Then simply press 'run module' to start.
	Alternatively, user can also enter "py \\sphinx.sfu.ca\smiyashi\354\finalProject\application.py" from the command prompt. 
	If this doesn't work on your system, enter "py application.py".
	
2. A command line interface menu will be displayed. 

3. User can select from 3 options: 
	
	"1- Add new passenger"
	
	"2- View passengers for a flight instance"
	
	"3- Add booking records"
   enter either the number 1, 2, or 3 to choose an option.


If user selects 1 (add new passenger): 
	
	a. Enter the first name and last name when prompted.
	
	b. New passenger record will be created and displayed and user will be routed back to the main menu screen  
  

If user selects 2 (view passengers for a flight instance):
	
	a. Enter flight code and depart date in the format <mm/dd/yy> when prompted.
	
	b. If no passengers exist for flight instance, 
		then "No results" will be displayed and user will be prompted to enter flight code and depart date again.
	   
		User must enter a valid flight instance in order to continue.
	
	c. Once a valid flight instance has been given, passenger_id, flight_name, last_name, and miles will be 
		displayed for each of the passengers with a booking of that flight instance.
	
	d. Available seats for this flight instance will be displayed.

	e. Then user will be returned to main menu. 

 
  
If user selects 3 (add booking records):
	
	a. Enter a passenger_id for the passenger you would like to add a booking record for.
	
	b. User will be prompted to select either single trip or multi-city trip.
	  
		Enter either 'S' or 'M', respectively. 
	
	c. Then user must enter flight code and depart date if single trip was chosen.
 
		Otherwise, user must enter flight code and depart date for the first leg and
 
		flight code and depart date for the second leg. 
	
	d. If insert is successful, user will see a success message. If insert is unsuccessful, 
		an error message will be displayed and user will be prompted to
	enter flight 
		code and depart date again, until they are successful. 
	
	e. Upon completion of this function, user will be returned to main menu.

