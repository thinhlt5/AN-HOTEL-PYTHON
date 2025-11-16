from .db_manager import DBManager

class BookingService:
    def __init__(self):
        self.db = DBManager()

    def book_room(self, customer_id, room_id, check_in, check_out, num_guests, total_amount, guest_name, guest_phone):
        bookings = self.db.get_all_bookings()
        new_booking_id = len(bookings) + 1
        
        booking_data = {
            "bookingID": new_booking_id,
            "customerID": customer_id,
            "roomId": room_id,
            "checkInDate": check_in,
            "checkOutDate": check_out,
            "numGuests": num_guests,
            "totalAmount": total_amount,
            "status": "Awaiting Confirmation",
            "guestName": guest_name,
            "guestPhone": guest_phone
        }
        
        self.db.add_booking(booking_data)
        return booking_data

    def get_user_bookings(self, customer_id):
        return self.db.get_customer_bookings(customer_id)

    def get_booking_by_id(self, booking_id):
        bookings = self.db.get_all_bookings()
        for booking in bookings:
            if booking.get("bookingID") == booking_id:
                return booking
        return None

    def cancel_booking(self, booking_id, customer_id):
        booking = self.get_booking_by_id(booking_id)
        if booking and booking.get("customerID") == customer_id:
            if booking.get("status") == "Awaiting Confirmation":
                self.db.update_booking_status(booking_id, "Canceled")
                return True
        return False

    def get_all_bookings(self):
        return self.db.get_all_bookings()

    def update_booking_status(self, booking_id, new_status):
        self.db.update_booking_status(booking_id, new_status)
        return True

    def check_room_availability(self, room_id, check_in, check_out):
        return self.db.is_room_available(room_id, check_in, check_out)
