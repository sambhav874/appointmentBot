import re
from datetime import datetime

class UserInputCollector:
    @staticmethod
    def collect_user_details(insurance_types, context=None):
        """Collect comprehensive user details with structured input."""
        print("\n--- Insurance Consultation Details ---")
        
        # Provide context if available
        if context:
            print(f"{context}")
        
        # Name collection with validation
        while True:
            name = input("Full Name: ").strip()
            if re.match(r'^[A-Za-z\s]{2,50}$', name):
                break
            print("Invalid name. Use only alphabets (2-50 characters).")
        
        # Email collection with basic validation (optional)
        while True:
            email = input("Email (optional, press Enter to skip): ").strip()
            if email == "" or re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                break
            print("Invalid email format. Please try again.")
        
        # Mobile number collection
        while True:
            mobile = input("Mobile Number: ").strip()
            if re.match(r'^[0-9]{10}$', mobile):
                break
            print("Invalid mobile number. Use 10 digits.")
        
        # Insurance type selection
        print("\nSelect Insurance Type:")
        for i, ins_type in enumerate(insurance_types, 1):
            print(f"{i}. {ins_type}")
        
        while True:
            try:
                type_choice = input("Enter the number of your insurance type: ").strip()
                insurance_type = insurance_types[int(type_choice) - 1]
                break
            except (ValueError, IndexError):
                print("Invalid selection. Please choose a number from the list.")
        
        # Date selection
        while True:
            date = input("Preferred Date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(date, '%Y-%m-%d')
                break
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")
        
        # Time selection
        while True:
            time = input("Preferred Time (HH:MM, 24-hour format): ").strip()
            try:
                datetime.strptime(time, '%H:%M')
                break
            except ValueError:
                print("Invalid time format. Use HH:MM in 24-hour format.")
        
        return {
            'name': name,
            'email': email or 'Not Provided',
            'mobile': mobile,
            'insurance_type': insurance_type,
            'preferred_date': date,
            'preferred_time': time,
            'appointment_needed': True
        }