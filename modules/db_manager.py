import json
import os
from datetime import datetime


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
            b_in = datetime.fromisoformat(b["checkInDate"].replace("Z", "+00:00"))
            b_out = datetime.fromisoformat(b["checkOutDate"].replace("Z", "+00:00"))
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




