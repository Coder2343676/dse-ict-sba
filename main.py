import json
import datetime
import os

# INIT
DATA_FILE = 'data.json'
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
        "bookClass": "All",
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
    print("1. Show Classrooms")         
    print("2. Show Bookings")              
    print("3. Book Classroom")              
    print("4. Cancel Booking")              
    print("5. [ADMIN] Edit Classrooms")       
    print("6. Exit")
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
      admin_edit_classrooms() 
    elif choice == '6':
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
  
  print("\n----- Current Bookings -----")
  for booking in bookings:
    print(f"  {booking['roomName']} ({booking['roomID']})")
    print(f"    Date: {booking['bookDate']}, Time: {booking['bookTime']}")
    print(f"    Booked by: {booking['bookTeacher']} for {booking['bookSubject']} (Class: {booking.get('bookClass', 'N/A')})")
    print(f"    Remarks: {booking['bookRemarks']}")
  print("----------------------------")


if __name__ == "__main__":
  load_data()
  main_menu()
