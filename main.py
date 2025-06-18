import json
import datetime
import os

# INIT
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



