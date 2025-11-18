from .db_manager import DBManager
from datetime import datetime, date

class BookingService:
    def __init__(self, db_manager=None):
        self.db = db_manager or DBManager("db")

    def create_booking(self, room_id, checkin_date, checkout_date, num_guests, guest_name, guest_phone, guest_email, guest_national_id, total_amount):
        """
        Create a new booking
        
        Args:
            room_id: Room ID to book
            checkin_date: Check-in date (date object or string)
            checkout_date: Check-out date (date object or string)
            num_guests: Number of guests
            guest_name: Guest full name
            guest_phone: Guest phone number
            guest_email: Guest email
            guest_national_id: Guest national ID
            total_amount: Total booking amount
            
        Returns:
            Booking data with auto-generated bookingID
        """
        bookings = self.db.get_all_bookings()
        new_booking_id = len(bookings) + 1
        
        # Convert dates to ISO format if they are date objects
        if isinstance(checkin_date, date) and not isinstance(checkin_date, datetime):
            checkin_date = datetime.combine(checkin_date, datetime.min.time()).isoformat()
        if isinstance(checkout_date, date) and not isinstance(checkout_date, datetime):
            checkout_date = datetime.combine(checkout_date, datetime.min.time()).isoformat()
        
        booking_data = {
            "bookingID": new_booking_id,
            "customerID": None,  # Will be set when customer logs in
            "roomId": room_id,
            "checkInDate": checkin_date,
            "checkOutDate": checkout_date,
            "numGuests": num_guests,
            "totalAmount": total_amount,
            "status": "Pending",
            "guestName": guest_name,
            "guestPhone": guest_phone,
            "guestEmail": guest_email,
            "guestNationalID": guest_national_id
        }
        
        # Save booking
        self.db.add_booking(booking_data)
        
        # Update room status to "Booked"
        self.db.update_room_status(room_id, "Booked")
        
        return booking_data
    
    def calculate_total_amount(self, room_type_price, checkin_date, checkout_date, num_guests=1):
        """
        Calculate total booking amount
        
        Args:
            room_type_price: Price per night
            checkin_date: Check-in date (date object)
            checkout_date: Check-out date (date object)
            num_guests: Number of guests (for potential discount)
            
        Returns:
            Total amount (price * number of nights)
        """
        if isinstance(checkin_date, str):
            checkin_date = datetime.fromisoformat(checkin_date).date()
        if isinstance(checkout_date, str):
            checkout_date = datetime.fromisoformat(checkout_date).date()
        
        nights = (checkout_date - checkin_date).days
        total = room_type_price * nights
        return total

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

    def view_booking_list(self, customer_id):
        return self.db.get_customer_bookings(customer_id)

    def view_booking_details(self, booking_id, customer_id=None):
        bookings = self.db.get_all_bookings()
        for booking in bookings:
            if booking.get("bookingID") == booking_id:
                if customer_id is None or booking.get("customerID") == customer_id:
                    return booking
        return None

    def cancel_booking(self, booking_id, customer_id):
        booking = self.view_booking_details(booking_id, customer_id)
        if booking and booking.get("status") in ["Awaiting Confirmation", "Pending"]:
            self.db.update_booking_status(booking_id, "Canceled")
            # Restore room status to Available
            self.db.update_room_status(booking["roomId"], "Available")
            return True
        return False

    def get_all_bookings(self):
        return self.db.get_all_bookings()

    def update_booking_status(self, booking_id, new_status):
        self.db.update_booking_status(booking_id, new_status)
        return True

    def check_room_availability(self, room_id, check_in, check_out):
        return self.db.is_room_available(room_id, check_in, check_out)
