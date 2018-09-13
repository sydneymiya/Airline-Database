/* Data is inserted in the following order: 
- Airport
- Flight
- Flight Instance
- Passenger
- Booking
*/

CREATE TABLE dbo.Airport
	(iata char(3) PRIMARY KEY,
	 airport_name char(30) NOT NULL UNIQUE,
	 city char(20) NOT NULL);
GO 

CREATE TABLE dbo.Flight 
	(flight_code char(6) PRIMARY KEY, 
	 distance int NOT NULL, 
	 departure_iata char(3) NOT NULL,
	 arrival_iata char(3) NOT NULL,
	 FOREIGN KEY (departure_iata) REFERENCES Airport(iata) ON DELETE NO ACTION ON UPDATE NO ACTION,
	 FOREIGN KEY (arrival_iata) REFERENCES Airport(iata) ON DELETE NO ACTION ON UPDATE NO ACTION,
	 CHECK (departure_iata <> arrival_iata));
GO 

CREATE FUNCTION checkAircraft() 
RETURNS INT 
AS
--Returns if an aircraft was used at most two times per day
BEGIN
	DECLARE @answer int;
	SELECT @answer = COUNT(*)
	FROM (SELECT aircraft_id, depart_date
		  FROM Flight_Instance    
		  GROUP BY aircraft_id, depart_date
		  HAVING COUNT(*) > 2) AS aircraftSummary
	if (@answer > 0) --there is at least 1 aircraft used more than twice in a day
		SET @answer=0 
	ELSE SET @answer=1
	RETURN @answer 
END;
GO

CREATE TABLE dbo.Flight_Instance
	(flight_code char(6),
	 depart_date date,
	 gate char(3),
	 aircraft_id tinyint,
	 PRIMARY KEY (flight_code, depart_date),
	 FOREIGN KEY (flight_code) REFERENCES Flight(flight_code) ON DELETE CASCADE ON UPDATE CASCADE,
	 --CONSTRAINT maxUsage UNIQUE (aircraft_id, depart_date));
	 CONSTRAINT air_id_twice CHECK(dbo.checkAircraft()=1));
GO

CREATE TABLE dbo.Passenger
	(passenger_id int PRIMARY KEY,
	 first_name char(20) NOT NULL, 
	 last_name char(20) NOT NULL,
	 miles int NOT NULL);
GO

CREATE TABLE dbo.Booking
	(flight_code char(6),
	 depart_date date,
	 passenger_id int,
	 PRIMARY KEY (flight_code, depart_date, passenger_id),
	 FOREIGN KEY (flight_code, depart_date) REFERENCES Flight_Instance(flight_code, depart_date) ON DELETE NO ACTION ON UPDATE CASCADE,
	 FOREIGN KEY (passenger_id) REFERENCES Passenger(passenger_id) ON DELETE NO ACTION ON UPDATE NO ACTION);
GO

CREATE TRIGGER deletePasssenger
	ON Passenger
    INSTEAD OF DELETE AS
		BEGIN
		  --Count number of bookings
			DECLARE @passWithBookings INT;
			SELECT @passWithBookings = COUNT(*)
			FROM deleted D, Booking B
		    WHERE D.passenger_id = B.passenger_id
			-- Passenger associated with at least 1 Booking, so raise error
			IF (@passWithBookings > 0)
				RAISERROR('Removing passenger is prevented by trigger. Total number of booking records: %d', 
							10, 1, @passWithBookings)
			--Passenger not associated with any booking, so delete
			ELSE IF (@passWithBookings = 0)
				DELETE FROM Passenger
				WHERE passenger_id IN (SELECT D.passenger_id
											FROM Deleted D)
		END;
		RETURN
GO

-- MilesUpdateTriggers
CREATE TRIGGER milesUpdate
ON dbo.Booking AFTER INSERT, DELETE, UPDATE
AS
BEGIN
	UPDATE passenger set miles = td.newMiles FROM
	(SELECT p.passenger_id,
		 p.miles + SUM(F.distance) AS newMiles
	FROM passenger p INNER JOIN inserted i
	ON i.passenger_id = p.passenger_id
	INNER JOIN Flight F ON F.flight_code = i.flight_code
	GROUP BY p.passenger_id, p.miles) AS td
	WHERE passenger.passenger_id = td.passenger_id
	
	UPDATE passenger SET miles = td.newMiles FROM
	(SELECT p.passenger_id,
		 p.miles - SUM(F.distance) AS newMiles
	FROM passenger p INNER JOIN deleted i
	ON i.passenger_id = p.passenger_id
	INNER JOIN Flight F ON F.flight_code = i.flight_code
	GROUP BY p.passenger_id, p.miles) AS td
	WHERE passenger.passenger_id = td.passenger_id
END

--UPDATE FLIGHT_INSTANCE TABLE
delete from booking;
alter table Flight_Instance add available_seats INTEGER;
update Flight_Instance set available_seats = 10;
GO

CREATE TRIGGER availableSeatsUpdated
ON dbo.Booking AFTER INSERT, DELETE, UPDATE
AS
BEGIN
	-- new flight is inserted/updated --
	UPDATE flight_instance set available_seats = td.newSeats FROM 
	(SELECT f.flight_code, f.depart_date, 
		f.available_seats - COUNT(*) AS newSeats
	FROM flight_instance f INNER JOIN inserted i 
	ON i.flight_code = f.flight_code AND i.depart_date = f.depart_date
	GROUP BY f.flight_code, f.depart_date, f.available_seats) AS td
	WHERE flight_instance.flight_code = td.flight_code AND flight_instance.depart_date = td.depart_date

	-- flight is deleted
	UPDATE flight_instance set available_seats = td.newSeats FROM  
	(SELECT f.flight_code, f.depart_date,
		f.available_seats + COUNT(*) AS newSeats
	FROM flight_instance f INNER JOIN deleted i 
	ON i.flight_code = f.flight_code AND i.depart_date = f.depart_date
	GROUP BY f.flight_code, f.depart_date, f.available_seats) AS td
	WHERE flight_instance.flight_code = td.flight_code AND flight_instance.depart_date = td.depart_date
END

