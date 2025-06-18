import json
import datetime
import os
import re # Import regex module for time slot validation

# --- Constants ---
DATA_FILE = 'classroom_bookings.json'
DATE_FORMAT = '%Y-%m-%d'
# TIME_SLOTS now represent standard, preferred booking intervals.
# Users can book outside these, but will be prompted for confirmation.
TIME_SLOTS = [
  "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00",
  "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00"
]
TIME_FORMAT = '%H:%M' # Format for parsing individual times within a slot
TIME_SLOT_PATTERN = re.compile(r'^(\d{2}:\d{2})-(\d{2}:\d{2})$') # Regex for HH:MM-HH:MM format

# --- Data Structures (will be loaded/saved) ---
classrooms = [] # List of dictionaries: {"id": "C101", "name": "Science Lab", "capacity": 30}
# Bookings now store "time_slot" as "HH:MM-HH:MM" string, e.g., "09:00-10:00" or "17:00-18:00"
bookings = []   # List of dictionaries: {"classroom_id": "C101", "date": "2023-10-27", "time_slot": "09:00-10:00", "teacher": "Mr. Smith", "subject": "Chemistry", "class_name": "5E"}

# --- File Operations ---

def load_data():
  """Loads classroom and booking data from the JSON file."""
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
      {"id": "C101", "name": "Science Lab", "capacity": 30},
      {"id": "C102", "name": "Art Studio", "capacity": 25},
      {"id": "C201", "name": "Lecture Hall 1", "capacity": 100},
      {"id": "C202", "name": "Computer Lab", "capacity": 40},
      {"id": "C301", "name": "Meeting Room A", "capacity": 10}
    ])
    print("Default classrooms added. You can add/remove more via the admin menu.")
    save_data() # Save initial data

def save_data():
  """Saves current classroom and booking data to the JSON file."""
  data = {
    'classrooms': classrooms,
    'bookings': bookings
  }
  with open(DATA_FILE, 'w') as f:
    json.dump(data, f, indent=4)
  print(f"Data saved to {DATA_FILE}")

# --- Helper Functions ---

def get_classroom_by_id(classroom_id):
  """Returns a classroom dictionary given its ID, or None if not found."""
  for room in classrooms:
    if room['id'].lower() == classroom_id.lower():
      return room
  return None

def display_classrooms():
  """Displays all registered classrooms, including their capacity."""
  if not classrooms:
    print("\nNo classrooms registered yet.")
    return
  print("\n--- Available Classrooms ---")
  for room in classrooms:
    # Displaying capacity as requested
    print(f"  ID: {room['id']}, Name: {room['name']}, Capacity: {room['capacity']}")
  print("-" * 30)

def display_bookings(filter_by_classroom_id=None, filter_by_date=None):
  """
  Displays all existing bookings, optionally filtered by classroom ID or date.
  Now includes 'Class' in the output.
  """
  if not bookings:
    print("\nNo bookings yet.")
    return

  print("\n--- Current Bookings ---")
  found_bookings = False
  for i, booking in enumerate(bookings):
    room = get_classroom_by_id(booking['classroom_id'])
    room_name = room['name'] if room else "Unknown Classroom"

    if (filter_by_classroom_id and booking['classroom_id'].lower() != filter_by_classroom_id.lower()) or \
       (filter_by_date and booking['date'] != filter_by_date):
      continue # Skip if filters don't match

    print(f"  [{i+1}] Classroom: {room_name} ({booking['classroom_id']})")
    print(f"    Date: {booking['date']}, Time: {booking['time_slot']}")
    # Displaying class_name as requested
    print(f"    Booked by: {booking['teacher']} for {booking['subject']} (Class: {booking.get('class_name', 'N/A')})")
    print("-" * 30)
    found_bookings = True
  
  if not found_bookings:
    print("  No bookings found matching the criteria.")
  print("-" * 30)

def is_time_overlap(start1_str, end1_str, start2_str, end2_str):
  """
  Checks if two time intervals overlap.
  Times are expected in HH:MM format strings.
  """
  try:
    start1 = datetime.datetime.strptime(start1_str, TIME_FORMAT).time()
    end1 = datetime.datetime.strptime(end1_str, TIME_FORMAT).time()
    start2 = datetime.datetime.strptime(start2_str, TIME_FORMAT).time()
    end2 = datetime.datetime.strptime(end2_str, TIME_FORMAT).time()

    # Check for overlap: (start1 < end2 AND start2 < end1)
    # This covers all overlap scenarios including touching at endpoints
    return (start1 < end2 and start2 < end1)
  except ValueError:
    # Should not happen with prior validation, but good for robustness
    print("Error: Invalid time format encountered during overlap check.")
    return False

def is_classroom_available(classroom_id, date_str, requested_time_slot):
  """
  Checks if a classroom is available for a given date and time slot (HH:MM-HH:MM).
  Performs overlap detection.
  """
  # Extract requested start and end times from the time_slot string
  match = TIME_SLOT_PATTERN.match(requested_time_slot)
  if not match:
    print(f"Internal error: Requested time slot '{requested_time_slot}' has invalid format.")
    return False # Should be caught by get_valid_time_slot_input

  req_start_str, req_end_str = match.groups()

  for booking in bookings:
    # Check if it's the same classroom and date
    if booking['classroom_id'].lower() == classroom_id.lower() and \
       booking['date'] == date_str:
      
      # Extract start and end times from the existing booking's time_slot
      existing_match = TIME_SLOT_PATTERN.match(booking['time_slot'])
      if not existing_match:
        print(f"Warning: Existing booking time slot '{booking['time_slot']}' has invalid format. Skipping.")
        continue

      existing_start_str, existing_end_str = existing_match.groups()

      # Check for overlap with the existing booking
      if is_time_overlap(req_start_str, req_end_str, existing_start_str, existing_end_str):
        return False # Not available (overlap found)
  return True # Available

def get_valid_date_input(prompt="Enter date (YYYY-MM-DD): "):
  """Prompts user for a date and validates it."""
  while True:
    date_str = input(prompt).strip()
    try:
      booking_date = datetime.datetime.strptime(date_str, DATE_FORMAT).date()
      if booking_date < datetime.date.today():
        print("Error: Cannot book for a past date.")
        continue
      return date_str
    except ValueError:
      print("Invalid date format. Please use YYYY-MM-DD.")

def get_valid_time_slot_input():
  """
  Prompts user for a time slot in HH:MM-HH:MM format and validates it.
  Does not restrict to predefined TIME_SLOTS for input, but validates format.
  """
  while True:
    time_slot_str = input("Enter time slot (HH:MM-HH:MM, e.g., 09:00-10:00): ").strip()
    
    match = TIME_SLOT_PATTERN.match(time_slot_str)
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
      
      return time_slot_str
    except ValueError:
      print("Invalid time format within the slot (e.g., '25:00' is invalid).")
      continue

# --- Core Booking Functions ---

def book_classroom():
  """Guides the user through booking a classroom."""
  display_classrooms()
  if not classrooms:
    print("Cannot book: No classrooms available. Please add classrooms first.")
    return

  classroom_id = input("Enter Classroom ID to book: ").strip()
  room = get_classroom_by_id(classroom_id)

  if not room:
    print(f"Error: Classroom with ID '{classroom_id}' not found.")
    return

  date_str = get_valid_date_input()
  time_slot = get_valid_time_slot_input() # User types HH:MM-HH:MM

  teacher_name = input("Enter Teacher's Name: ").strip()
  subject_name = input("Enter Subject Name: ").strip()
  class_name = input("Enter Class Name (e.g., 5E): ").strip() # New field

  if not teacher_name or not subject_name or not class_name:
    print("Teacher name, subject, and class name cannot be empty.")
    return

  # "Are you sure" for booking times outside standard school hours
  if time_slot not in TIME_SLOTS:
    confirm = input(f"Warning: This time slot ({time_slot}) is outside standard school hours. Are you sure? (yes/no): ").strip().lower()
    if confirm != 'yes':
      print("Booking cancelled.")
      return

  if is_classroom_available(classroom_id, date_str, time_slot):
    new_booking = {
      "classroom_id": classroom_id,
      "date": date_str,
      "time_slot": time_slot,
      "teacher": teacher_name,
      "subject": subject_name,
      "class_name": class_name # Add class name to booking
    }
    bookings.append(new_booking)
    save_data()
    print(f"\nSuccessfully booked {room['name']} for {date_str} at {time_slot}.")
  else:
    print(f"\nError: {room['name']} is already booked for {date_str} during {time_slot} (overlap detected).")

def view_available_classrooms():
  """Shows which classrooms are available for a chosen date and time."""
  date_str = get_valid_date_input()
  time_slot = get_valid_time_slot_input() # User types HH:MM-HH:MM

  print(f"\n--- Availability for {date_str} at {time_slot} ---")
  found_available = False
  for room in classrooms:
    # Pass the typed time_slot directly to is_classroom_available
    if is_classroom_available(room['id'], date_str, time_slot):
      print(f"  Available: {room['name']} (ID: {room['id']}, Capacity: {room['capacity']})")
      found_available = True
  
  if not found_available:
    print("  No classrooms available for this time slot.")
  print("-" * 45)


def cancel_booking():
  """Allows the user to cancel an existing booking."""
  if not bookings:
    print("\nNo bookings to cancel.")
    return

  display_bookings()
  try:
    booking_index = int(input("Enter the number of the booking to cancel: ")) - 1
    if 0 <= booking_index < len(bookings):
      canceled_booking = bookings.pop(booking_index)
      save_data()
      room = get_classroom_by_id(canceled_booking['classroom_id'])
      room_name = room['name'] if room else "Unknown Classroom"
      print(f"\nBooking for {room_name} on {canceled_booking['date']} at {canceled_booking['time_slot']} by {canceled_booking['teacher']} (Class: {canceled_booking.get('class_name', 'N/A')}) has been cancelled.")
    else:
      print("Invalid booking number.")
  except ValueError:
    print("Invalid input. Please enter a number.")

# --- Admin Functions ---

def add_classroom():
  """Adds a new classroom to the system."""
  display_classrooms()
  while True:
    new_id = input("Enter new Classroom ID (e.g., C401): ").strip().upper()
    if not new_id:
      print("Classroom ID cannot be empty.")
      continue
    if get_classroom_by_id(new_id):
      print(f"Error: Classroom with ID '{new_id}' already exists.")
    else:
      break
  
  new_name = input("Enter Classroom Name (e.g., Media Center): ").strip()
  while not new_name:
    new_name = input("Classroom name cannot be empty. Enter Classroom Name: ").strip()

  while True:
    try:
      new_capacity = int(input("Enter Classroom Capacity: ").strip())
      if new_capacity <= 0:
        print("Capacity must be a positive number.")
      else:
        break
    except ValueError:
      print("Invalid input. Please enter a number for capacity.")

  classrooms.append({"id": new_id, "name": new_name, "capacity": new_capacity})
  save_data()
  print(f"\nClassroom '{new_name}' (ID: {new_id}) added successfully.")

def remove_classroom():
  """Removes an existing classroom from the system."""
  display_classrooms()
  if not classrooms:
    print("No classrooms to remove.")
    return

  room_id_to_remove = input("Enter the ID of the classroom to remove: ").strip().upper()
  room_to_remove = get_classroom_by_id(room_id_to_remove)

  if not room_to_remove:
    print(f"Error: Classroom with ID '{room_id_to_remove}' not found.")
    return

  # Check if there are any active bookings for this classroom
  active_bookings_for_room = [b for b in bookings if b['classroom_id'].lower() == room_id_to_remove.lower()]
  if active_bookings_for_room:
    print(f"Error: Cannot remove '{room_to_remove['name']}' ({room_id_to_remove}). It has active bookings.")
    print("Please cancel all bookings for this classroom before removing it.")
    return

  classrooms[:] = [room for room in classrooms if room['id'].lower() != room_id_to_remove.lower()]
  save_data()
  print(f"\nClassroom '{room_to_remove['name']}' (ID: {room_id_to_remove}) removed successfully.")

# --- Main Menu ---

def main_menu():
  """Displays the main menu and handles user choices."""
  while True:
    print("\n===== Classroom Booking Manager =====")
    print("1. Book a Classroom")
    print("2. View All Bookings")
    print("3. View Available Classrooms (by date/time)")
    print("4. Cancel a Booking")
    print("5. Admin Options (Add/Remove Classrooms)")
    print("6. Exit")
    print("====================================")

    choice = input("Enter your choice: ").strip()

    if choice == '1':
      book_classroom()
    elif choice == '2':
      display_bookings()
    elif choice == '3':
      view_available_classrooms()
    elif choice == '4':
      cancel_booking()
    elif choice == '5':
      admin_menu()
    elif choice == '6':
      print("Exiting Classroom Booking Manager. Goodbye!")
      break
    else:
      print("Invalid choice. Please try again.")
    input("\nPress Enter to continue...") # Pause for user to read output

def admin_menu():
  """Displays the admin menu and handles user choices."""
  while True:
    print("\n--- Admin Options ---")
    print("1. Add New Classroom")
    print("2. Remove Classroom")
    print("3. Back to Main Menu")
    print("---------------------")

    choice = input("Enter your choice: ").strip()

    if choice == '1':
      add_classroom()
    elif choice == '2':
      remove_classroom()
    elif choice == '3':
      break
    else:
      print("Invalid choice. Please try again.")
    input("\nPress Enter to continue...")


# --- Script Execution ---

if __name__ == "__main__":
  load_data() # Load data when the script starts
  main_menu() # Start the main application loop
  # Data is automatically saved after each modification
