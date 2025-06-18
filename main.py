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
    print(f"No data file found ({DATA_FILE}). Starting with empty data.")
    # Initialize some default classrooms if no file exists
    classrooms.extend([
      {"id": "C00", "name": "Test", "capacity": 30}
    ])
    print("Default classrooms added. You can add/remove more via the admin menu.")
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
    print("2. Book Classroom")              
    print("3. Show Bookings")              
    print("4. Cancel Booking")              
    print("5. [ADMIN] Edit Classrooms")       
    print("6. Exit")
    print("==============================")

    choice = input("Enter your choice: ").strip()

    if choice == '1':
      show_classrooms() # The existing function that shows classroom details
    elif choice == '2':
      book_classroom()
    elif choice == '3':
      show_bookings() # The existing function that shows all bookings
    elif choice == '4':
      cancel_booking()
    elif choice == '5':
      admin_edit_classrooms() # The existing function for admin options (add/remove classrooms)
    elif choice == '6':
      print("Exiting CWY Booking System. Goodbye!")
      break
    else:
      print("Invalid choice. Please try again.")




if __name__ == "__main__":
  load_data()
  main_menu()
