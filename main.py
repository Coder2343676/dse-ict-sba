import json
import datetime
import os
import re

# INIT
DATA_FILE = 'data.json'
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M'
TIME_SLOT_PATTERN = re.compile(r'^(\d{2}:\d{2})-(\d{2}:\d{2})$') # thank you https://stackoverflow.com/questions/69806492/regex-d4-d2-d2
classrooms = [] 
bookings = [] 

def load_data():
  global classrooms, bookings

  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
      data = json.load(f)
      classrooms = data.get('classrooms', [])
      bookings = data.get('bookings', [])
    print(f"Data loaded from {DATA_FILE}")

  else:
    # Initialize some default stuff if no file exists
    print(f"No data file found ({DATA_FILE}). Starting with empty data.")
    classrooms.extend([
      {"roomID": "C01", "roomName": "Classroom 1A", "roomCapacity": 35},
      {"roomID": "C02", "roomName": "Classroom 1B", "roomCapacity": 35},
      {"roomID": "C03", "roomName": "Classroom 1C", "roomCapacity": 35},
      {"roomID": "D01", "roomName": "Hall", "roomCapacity": 1200},
      {"roomID": "D02", "roomName": "Covered Playground", "roomCapacity": 100},
    ])
    bookings.extend([
      {
        "roomID": "D02",
        "roomName": "Covered Playground",
        "bookDate": "2025-10-15",
        "bookTime": "10:00-20:00",
        "bookTeacher": "Ms Tse",
        "bookSubject": "Singing Performance",
        "bookRemarks": "好好聽"
      },
    ])
    print("Default classrooms added. You can edit the list via the admin menu.")
    save_data() # Save initial data

def save_data():
  data = {
    'classrooms': classrooms,
    'bookings': bookings
  }
  with open(DATA_FILE, 'w') as f:
    json.dump(data, f, indent=2)
  print(f"Data saved to {DATA_FILE}")

# MAIN
def main_menu():
  while True:
    print("\n===== CWY Booking System =====")
    print("  1. Show Classrooms")         
    print("  2. Show Bookings")              
    print("  3. Book Classroom")              
    print("  4. Cancel Booking")              
    print("  5. Exit")
    print("==============================")

    choice = input("Enter your choice: ").strip()

    if choice == '1':
      show_classrooms() 
    elif choice == '2':
      show_bookings() 
    elif choice == '3':
      book_classroom()
    elif choice == '4':
      cancel_booking()
    elif choice == '5':
      print("Exiting CWY Booking System. Goodbye!")
      break
    else:
      print("Invalid choice. Please try again.")
    
    input("\nPress Enter to continue...")

def show_classrooms():
  print("\n--- Available Classrooms ---")
  for room in classrooms:
    print(f"  ID: {room['roomID']}, Name: {room['roomName']}, Capacity: {room['roomCapacity']}")
  print("----------------------------")

def show_bookings():
  if not bookings:
    print("\nNo bookings yet.")
    return
  
  i = 0

  print("\n----- Current Bookings -----")
  for booking in bookings:
    i += 1
    print(f"  {i}. {_get_classroom_by_id(booking['roomID'])['roomName']} - {booking['roomID']}")
    print(f"     Date: {booking['bookDate']}, Time: {booking['bookTime']}")
    print(f"     Booked by: {booking['bookTeacher']} for {booking['bookSubject']} with class {booking['bookClass']})") 
    print(f"     Remarks: {booking.get('bookRemarks', 'N/A')}") # .get can handle missing keys
  print("----------------------------")

def book_classroom():
  show_classrooms()

  roomID = input("Enter Classroom ID to book: ").strip().upper()
  room = _get_classroom_by_id(roomID)
  if not room:
    print(f"Error: Classroom with ID '{roomID}' not found.")
    return

  bookDate = _get_valid_date_input()
  bookTime = _get_valid_time_slot_input()

  bookTeacher = input("Enter Teacher's Name: ").strip()
  bookSubject = input("Enter Subject Name: ").strip()
  bookClass = input("Enter Class Name (eg 5E): ").strip()
  bookRemarks = input("Enter Remarks (optional): ").strip()
  if not bookRemarks:
    bookRemarks = ""

  if not bookTeacher or not bookSubject or not bookClass:
    print("Teacher name, subject, and class name cannot be empty.")
    return

  if _is_classroom_available(roomID, bookDate, bookTime):
    new_booking = {
      "roomID": roomID,
      "bookDate": bookDate,
      "bookTime": bookTime,
      "bookTeacher": bookTeacher,
      "bookSubject": bookSubject,
      "bookClass": bookClass # Add class name to booking
    }
    bookings.append(new_booking)
    save_data()
    print(f"\nSuccessfully booked {roomID} for {bookDate} at {bookTime}.")
  else:
    print(f"\nError: {roomID} is already booked for {bookDate} during {bookTime} (overlap detected).")

def _get_classroom_by_id(roomID):
  for room in classrooms:
    if room['roomID'] == roomID:
      return room
  return None

def _get_valid_date_input(prompt="Enter date (YYYY-MM-DD): "):
  while True:
    date_str = input(prompt).strip()
    try:
      bookingDate = datetime.datetime.strptime(date_str, DATE_FORMAT).date()
      if bookingDate < datetime.date.today():
        print("Error: Cannot book for a past date.")
        continue
      return date_str
    except ValueError:
      print("Invalid date format. Please use YYYY-MM-DD.")

def _get_valid_time_slot_input():
  while True:
    time_slot_str = input("Enter time slot (HH:MM-HH:MM, e.g., 09:00-13:00): ").strip()
    
    match = TIME_SLOT_PATTERN.match(time_slot_str) # i learned regex for this smh
    if not match:
      print("Invalid time slot format. Please use HH:MM-HH:MM (e.g., 08:00-09:00).")
      continue
    start_time_str, end_time_str = match.groups()
    
    try:
      start_time = datetime.datetime.strptime(start_time_str, TIME_FORMAT).time()
      end_time = datetime.datetime.strptime(end_time_str, TIME_FORMAT).time()
      if start_time >= end_time:
        print("Error: End time must be after start time.")
        continue
    except ValueError: # catch invalid time format
      print("Invalid time format within the slot (from 00:00 to 23:59).")
      continue

    # check if the time slot is within standard school hours
    if start_time < datetime.time(7, 0) or end_time > datetime.time(17, 0): # 07:00 to 17:00
      confirm = input(f"Warning: This time slot is outside standard school hours. Continue? (y/n): ").strip().lower()
      if confirm != 'yes' and confirm != 'y':
        continue

    return time_slot_str

def _is_classroom_available(roomID, bookDate, bookTime):
  match = TIME_SLOT_PATTERN.match(bookTime)
  reqStart, reqEnd = match.groups()

  for booking in bookings:
    # Check if it's the same classroom and date
    if booking['roomID'] == roomID and booking['bookDate'] == bookDate:
      
      # Extract start and end times from the existing booking's bookTime
      existingMatch = TIME_SLOT_PATTERN.match(booking['bookTime'])
      existingStart, existingEnd = existingMatch.groups()

      # Check for overlap with the existing booking
      if _is_time_overlap(reqStart, reqEnd, existingStart, existingEnd):
        return False # Not available (overlap found)
      
  return True # Available

def _is_time_overlap(start1_str, end1_str, start2_str, end2_str):
  try:
    start1 = datetime.datetime.strptime(start1_str, TIME_FORMAT).time()
    end1 = datetime.datetime.strptime(end1_str, TIME_FORMAT).time()
    start2 = datetime.datetime.strptime(start2_str, TIME_FORMAT).time()
    end2 = datetime.datetime.strptime(end2_str, TIME_FORMAT).time()

    return (start1 < end2 and start2 < end1) # covers all overlap, includes touching at endpoints
  
  except ValueError:
    # just in case
    print("Error: Invalid time format encountered during overlap check. Problem on our side.")
    return False

def cancel_booking():
  if not bookings:
    print("\nNo bookings to cancel.")
    return

  show_bookings()
  try:
    booking_index = int(input("Enter the number of the booking to cancel: ")) - 1
    if 0 <= booking_index < len(bookings):
      canceled_booking = bookings.pop(booking_index)
      save_data()
      room = _get_classroom_by_id(canceled_booking['classroom_id'])
      room_name = room['name'] if room else "Unknown Classroom"
      print(f"\nBooking for {room_name} on {canceled_booking['date']} {canceled_booking['time_slot']} by {canceled_booking['teacher']} has been cancelled.")
    else:
      print("Invalid booking number.")
  except ValueError:
    print("Invalid input. Please enter a number.")






if __name__ == "__main__":
  load_data()
  main_menu()
