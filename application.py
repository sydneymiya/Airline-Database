#!python3
import sys, os
import datetime
import pyodbc
from datetime import datetime as dt

conn = pyodbc.connect('driver={SQL Server};server=cypress.csil.sfu.ca;uid=s_smiyashi;pwd=7mM7fe2THAArar2h')
conn.setencoding('utf-8')
     
def main_menu():
    os.system('clear')
    print("Welcome,")
    print("1- Add new passenger")
    print("2- View passengers for a flight instance")
    print("3- Add booking records\n")
    choice = input("Please enter the option number to start: ")
    exec_menu(choice)
    return

def exec_menu(choice):    
    if choice == '1':
        addPassenger()
    elif choice == '2':
        viewPassenger()
    elif choice == '3':
        addBooking()
    else:
        print("\nError: Please enter one of the given options\n")
        main_menu()
    return

# Create profile for a new passenger
def addPassenger():
    mycursor = conn.cursor()

    # Retrieve largest passenger_id in database
    SQLRetrieval = ("SELECT MAX(passenger_id)" "FROM Passenger")
    mycursor.execute(SQLRetrieval)
    results = mycursor.fetchone()
    newPassenger_id = int(results[0]) + 1
    mycursor.close()

    print("Create a profile for a new passenger")
    firstName = input("Please enter first name: ")
    lastName = input("Please enter last name: ")
    mycursor = conn.cursor()
    SQLCommand = ("INSERT INTO Passenger(passenger_id, first_name, last_name, miles) VALUES (?,?,?,?)")
    Values = [newPassenger_id,firstName,lastName,0]
    
    mycursor.execute(SQLCommand,Values)
    conn.commit() #commit any pending transactions to the database
    print("The profile for passenger " + str(newPassenger_id) + " " + firstName + " " + lastName + " was created.\n")
    mycursor.close()
    main_menu()
    return

# View passenger records and available seats 
def viewPassenger():
    mycursor = conn.cursor()

    # Retrieve all passengers who booked a certain flight instance
    flightCode = input("Please enter a flight code: ")
    departDate = input("Please enter a depart date <mm/dd/yy>: ")
    mycursor.execute("SELECT P.passenger_id, P.first_name, P.last_name, P.miles FROM Passenger P, Booking B WHERE P.passenger_id = B.passenger_id AND B.flight_code = ? AND B.depart_date = ?", (flightCode, departDate))
    rows = mycursor.fetchall()
    if rows is None:
        print("This flight is empty. Please try again")
        viewPassenger()
    
    for row in rows:
        print("Passenger ID = " + str(row[0]) + ", First Name = " + str(row[1]) + ", Last Name = " + str(row[2]) + ", Miles = " + str(row[3]) )
    mycursor.close()

    # Retrieve number of available seats left
    mycursor = conn.cursor()
    mycursor.execute("SELECT FI.available_seats FROM Flight_instance FI, Booking B WHERE FI.flight_code = B.flight_code AND FI.depart_date = B.depart_date AND B.flight_code = ? AND B.depart_date = ?", (flightCode, departDate))
    results = mycursor.fetchone()
    if results is None:
        print("This flight is empty. Please try again")
        viewPassenger()
        
    print(str(results[0]) + " seat(s) are still available for this flight instance")
    mycursor.close()
    main_menu()
    return

# Test functions: Add Booking Records
# existence of specified flight instances
def testFlightCode(flightCode, departDate):
    flight = flightCode
    date = departDate
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM Flight_instance WHERE flight_code = ? AND depart_date = ?", (flight, date))
    results = mycursor.fetchone()
    if results is None:
        exists =  0
    else:
        exists = 1
    mycursor.close()
    return exists

# availability of seats for the flight instances
def testSeatAvail(flightCode, departDate):
    flight = flightCode
    date = departDate
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM Flight_instance WHERE available_seats > 0 AND flight_code = ? AND depart_date = ?", (flight, date))
    results = mycursor.fetchone()
    if results is None:
        exists =  0
    else:
        exists = 1
    mycursor.close()
    return exists

# feasibility of the depart date of the legs if multitrip is selected
def testDepartDate(departDate1, departDate2):
    # second depart date must be no earlier than the first depart date
    # flights already exist so just verify that the second date is after the first
    date1 = departDate1
    date2 = departDate2
    one = dt.strptime(date1, "%m/%d/%y")
    two = dt.strptime(date2, "%m/%d/%y")
    if (one > two):
        feasible = 0 # second date is earlier than the first
    else:
        feasible = 1

    return feasible

# Add single trip booking record
def singleTrip(passengerID):
    flightCode = input("Please enter a flight code: ")
    departDate = input("Please enter a depart date <mm/dd/yy>: ")    

    test1 = testFlightCode(flightCode, departDate)
    if test1 != 1: 
        print("Error: This flight does not exist.\n")
        singleTrip(passengerID)

    test2 = testSeatAvail(flightCode, departDate)
    if test2 != 1:
        print("Error: There are no available seats for this flight.\n")
        singleTrip(passengerID)
        
    mycursor = conn.cursor()
    SQLCommand = ("INSERT INTO Booking(flight_code, depart_date, passenger_id) VALUES (?,?,?)")
    Values = [flightCode,departDate,passengerID]
    mycursor.execute(SQLCommand,Values)
    conn.commit()
    mycursor.close()
    return

# Add multi trip booking record
def multiTrip(passengerID):
    flightCode1 = input("Please enter a flight code for the first leg: ")
    departDate1 = input("Please enter a depart date for the first leg <mm/dd/yy>: ")
    flightCode2 = input("Please enter a flight code for the second leg: ")
    departDate2 = input("Please enter a depart date for the second leg <mm/dd/yy>: ")
    
    # testing
    test1 = testFlightCode(flightCode1, departDate1)
    if test1 != 1: 
        print("Error: Flight 1 does not exist.\n")
        multiTrip(passengerID)
    test2 = testFlightCode(flightCode2, departDate2)
    if test2 != 1: 
        print("Error: Flight 2 does not exist.\n")
        multiTrip(passengerID)

    test3 = testDepartDate(departDate1, departDate2)
    if test3 != 1: 
        print("Error: This depart date is not feasible. Second departure date must be no earlier than the first.\n")
        multiTrip(passengerID)

    test4 = testSeatAvail(flightCode1, departDate1)
    if test4 != 1:
        print("Error: There are no available seats for flight 1.\n")
        multiTrip(passengerID)
    test5 = testSeatAvail(flightCode2, departDate2)
    if test5 != 1:
        print("Error: There are no available seats for flight 2.\n")
        multiTrip(passengerID)
    
    # insert records
    
    mycursor = conn.cursor()
    SQLCommand1 = ("INSERT INTO Booking(flight_code, depart_date, passenger_id) VALUES (?,?,?)")
    Values1 = [flightCode1,departDate1,passengerID]
    mycursor.execute(SQLCommand1,Values1)

    SQLCommand2 = ("INSERT INTO Booking(flight_code, depart_date, passenger_id) VALUES (?,?,?)")
    Values2 = [flightCode2,departDate2,passengerID]
    mycursor.execute(SQLCommand2,Values2)
    
    # insert in one transaction
    conn.commit()
    mycursor.close()
    return

# Get user input, call to proper function 
def addBooking():
    passengerID = input("Please enter a passenger id: ")
    
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM Passenger WHERE passenger_id = ?", (passengerID))
    results = mycursor.fetchone()
    if results is None:
        print("This passenger does not exist.")
        addBooking()
    
    type = input("Enter 'S' for Single Trip or 'M' for Multi-City Trip: ") 
    if type == 'S':
        singleTrip(passengerID)
        print("Successfully inserted booking record\n")
        main_menu()
    elif type == 'M':
        multiTrip(passengerID)
        print("Successfully inserted 2 booking records\n")
        main_menu()
    else:
        print("Error: Enter 'S' or 'M'.\n")
        addBooking()      
    return


### Main ###
main_menu()

conn.close()
