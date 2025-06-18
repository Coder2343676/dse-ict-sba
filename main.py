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
    # Initialize some default classrooms if no file exists
    print(f"No data file found ({DATA_FILE}). Starting with empty data.")
    classrooms.extend([
      {"id": "C01", "name": "Classroom 1A", "capacity": 35},
      {"id": "C02", "name": "Classroom 1B", "capacity": 35},
      {"id": "C03", "name": "Classroom 1C", "capacity": 35},
      {"id": "D01", "name": "Hall", "capacity": 1200},
      {"id": "D02", "name": "Covered Playground", "capacity": 100},
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

def show_classrooms():
  print("\n--- Available Classrooms ---")
  for room in classrooms:
    print(f"  ID: {room['id']}, Name: {room['name']}, Capacity: {room['capacity']}")
  print("----------------------------")

def show_bookings():
  if not bookings:
    print("\nNo bookings yet.")
    return
  
  print("\n----- Current Bookings -----")
  for booking in bookings:
    print(f"  {booking['name']} ({booking['id']})")
    print(f"    Date: {booking['date']}, Time: {booking['time']}")
    print(f"    Booked by: {booking['teacher']} for {booking['subject']} (Class: {booking.get('class_name', 'N/A')})")
  print("----------------------------")


if __name__ == "__main__":
  load_data()
  main_menu()
