import json
import os
from datetime import datetime, date


class DBManager:
    def __init__(self, data_folder="data"):
        self.data_folder = data_folder
        self.room_type_file = os.path.join(data_folder, "roomType.json")
        self.room_file = os.path.join(data_folder, "room.json")
        self.customer_file = os.path.join(data_folder, "customer.json")
        self.booking_file = os.path.join(data_folder, "booking.json")
        self.admin_file = os.path.join(data_folder, "admin.json")

    def load_json(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def save_json(self, file_path, data):
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory:  # Only create if directory path is not empty
            os.makedirs(directory, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_all_room_types(self):
        return self.load_json(self.room_type_file)

    def add_room_type(self, type_data):
        room_types = self.load_json(self.room_type_file)
        room_types.append(type_data)
        self.save_json(self.room_type_file, room_types)

    def update_room_type(self, typeID, new_data):
        room_types = self.load_json(self.room_type_file)
        for rt in room_types:
            if rt["typeID"] == typeID:
                rt.update(new_data)
                break
        self.save_json(self.room_type_file, room_types)

    def delete_room_type(self, typeID):
        room_types = self.load_json(self.room_type_file)
        room_types = [rt for rt in room_types if rt["typeID"] != typeID]
        self.save_json(self.room_type_file, room_types)

    def get_all_rooms(self):
        return self.load_json(self.room_file)

    def update_room_status(self, roomId, new_status):
        rooms = self.load_json(self.room_file)
        for r in rooms:
            if r["roomId"] == roomId:
                r["Status"] = new_status
        self.save_json(self.room_file, rooms)

    def get_all_customers(self):
        return self.load_json(self.customer_file)

    def get_customer_by_email(self, email):
        customers = self.load_json(self.customer_file)
        for c in customers:
            if c["email"] == email:
                return c
        return None

    def add_customer(self, customer_data):
        customers = self.load_json(self.customer_file)
        customers.append(customer_data)
        self.save_json(self.customer_file, customers)

    def update_customer(self, customerID, new_data):
        customers = self.load_json(self.customer_file)
        for c in customers:
            if c["customerID"] == customerID:
                c.update(new_data)
        self.save_json(self.customer_file, customers)
    
    def delete_customer(self, customerID):
        """Delete a customer by ID"""
        customers = self.load_json(self.customer_file)
        customers = [c for c in customers if c.get("customerID") != customerID]
        self.save_json(self.customer_file, customers)
        return True

    def get_admin_by_username(self, username):
        admins = self.load_json(self.admin_file)
        for a in admins:
            if a["username"] == username:
                return a
        return None

    def get_all_bookings(self):
        return self.load_json(self.booking_file)

    def add_booking(self, booking_data):
        bookings = self.load_json(self.booking_file)
        bookings.append(booking_data)
        self.save_json(self.booking_file, bookings)

    def update_booking_status(self, bookingID, new_status):
        bookings = self.load_json(self.booking_file)
        for b in bookings:
            if b["bookingID"] == bookingID:
                b["status"] = new_status
        self.save_json(self.booking_file, bookings)

    def get_customer_bookings(self, customerID):
        bookings = self.load_json(self.booking_file)
        return [b for b in bookings if b["customerID"] == customerID]

    def is_room_available(self, roomId, check_in, check_out):
        bookings = self.load_json(self.booking_file)
        for b in bookings:
            if b["roomId"] != roomId:
                continue
            if b["status"] == "Canceled":
                continue
            
            # Convert booking dates from ISO format
            try:
                b_in = datetime.fromisoformat(b["checkInDate"].replace("Z", "+00:00"))
                b_out = datetime.fromisoformat(b["checkOutDate"].replace("Z", "+00:00"))
            except:
                continue
            
            # Convert to naive datetime (remove timezone info) for comparison
            if b_in.tzinfo is not None:
                b_in = b_in.replace(tzinfo=None)
            if b_out.tzinfo is not None:
                b_out = b_out.replace(tzinfo=None)
            
            # Convert check_in and check_out to datetime if they are date objects
            if isinstance(check_in, date) and not isinstance(check_in, datetime):
                check_in = datetime.combine(check_in, datetime.min.time())
            if isinstance(check_out, date) and not isinstance(check_out, datetime):
                check_out = datetime.combine(check_out, datetime.max.time())
            
            # Check for overlap
            if not (check_out <= b_in or check_in >= b_out):
                return False
        return True
      
    def find_available_rooms(self, typeID, check_in, check_out):
        rooms = self.get_all_rooms()
        available = []
        for r in rooms:
            if r["typeID"] != typeID:
                continue
            if self.is_room_available(r["roomId"], check_in, check_out):
                available.append(r)
        return available
    
    def find_available_rooms_by_date(self, check_in, check_out, typeID=None):
        """Find all available rooms for given dates, optionally filtered by room type"""
        rooms = self.get_all_rooms()
        available = []
        for r in rooms:
            # Filter by typeID if provided
            if typeID is not None and r["typeID"] != typeID:
                continue
            # Check if room is available for the given dates
            if self.is_room_available(r["roomId"], check_in, check_out):
                available.append(r)
        return available
    
    def add_room(self, room_data):
        """Add a new room"""
        rooms = self.load_json(self.room_file)
        rooms.append(room_data)
        self.save_json(self.room_file, rooms)
    
    def update_room(self, roomId, new_data):
        """Update room information"""
        rooms = self.load_json(self.room_file)
        for r in rooms:
            if r["roomId"] == roomId:
                r.update(new_data)
                break
        self.save_json(self.room_file, rooms)
    
    def delete_room(self, roomId):
        """Delete a room"""
        rooms = self.load_json(self.room_file)
        rooms = [r for r in rooms if r["roomId"] != roomId]
        self.save_json(self.room_file, rooms)
    
    def get_room_by_number(self, room_number):
        """Get room by room number"""
        rooms = self.load_json(self.room_file)
        for r in rooms:
            if r.get("roomNumber") == room_number:
                return r
        return None
    
    def get_room_type_by_id(self, typeID):
        """Get room type by ID"""
        room_types = self.load_json(self.room_type_file)
        for rt in room_types:
            if rt.get("typeID") == typeID:
                return rt
        return None




