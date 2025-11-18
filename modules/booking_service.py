from .db_manager import DBManager
from datetime import datetime, date

class BookingService:
    def __init__(self, db_manager=None):
        self.db = db_manager or DBManager("db")

    def create_booking(self, room_id, checkin_date, checkout_date, num_guests, guest_name, guest_phone, guest_email, guest_national_id, total_amount, customer_id=None):
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
            customer_id: Customer ID if user is logged in (optional)
            
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
            "customerID": customer_id,  # Set from logged-in user session
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
    
    def get_room_number_by_id(self, room_id):
        """Get room number by room ID"""
        rooms = self.db.get_all_rooms()
        for room in rooms:
            if room.get("roomId") == room_id:
                return room.get("roomNumber", "")
        return ""
    
    def get_bookings_by_status(self, status):
        """
        Get all bookings filtered by status
        
        Args:
            status: Booking status (Pending, Confirmed, In stay, Completed, Cancelled)
            
        Returns:
            List of bookings with the specified status
        """
        bookings = self.db.get_all_bookings()
        # Normalize status names
        status_map = {
            "Pending": "Pending",
            "Confirmed": "Confirmed",
            "In stay": "In stay",
            "In Stay": "In stay",
            "Completed": "Completed",
            "Cancelled": "Cancelled",
            "Canceled": "Cancelled"
        }
        normalized_status = status_map.get(status, status)
        
        filtered = []
        for booking in bookings:
            booking_status = booking.get("status", "")
            # Normalize booking status for comparison
            if booking_status in status_map:
                booking_status = status_map[booking_status]
            if booking_status == normalized_status:
                filtered.append(booking)
        return filtered
    
    def confirm_booking(self, booking_id):
        """
        Confirm a pending booking (Pending -> Confirmed)
        
        Args:
            booking_id: ID of the booking to confirm
            
        Returns:
            True if successful, False otherwise
        """
        booking = self.view_booking_details(booking_id)
        if booking and booking.get("status") == "Pending":
            self.db.update_booking_status(booking_id, "Confirmed")
            return True
        return False
    
    def check_in_booking(self, booking_id):
        """
        Check in a confirmed booking (Confirmed -> In stay)
        
        Args:
            booking_id: ID of the booking to check in
            
        Returns:
            True if successful, False otherwise
        """
        booking = self.view_booking_details(booking_id)
        if booking and booking.get("status") == "Confirmed":
            self.db.update_booking_status(booking_id, "In stay")
            return True
        return False
    
    def cancel_booking_admin(self, booking_id):
        """
        Cancel a booking (admin function - can cancel any booking)
        
        Args:
            booking_id: ID of the booking to cancel
            
        Returns:
            True if successful, False otherwise
        """
        booking = self.view_booking_details(booking_id)
        if booking:
            # Use "Canceled" to match existing data format (normalization handles display)
            self.db.update_booking_status(booking_id, "Canceled")
            # Restore room status to Available if booking was active
            if booking.get("status") in ["Pending", "Confirmed", "In stay"]:
                self.db.update_room_status(booking["roomId"], "Available")
            return True
        return False
    
    def auto_complete_checkouts(self):
        """
        Automatically change In stay bookings to Completed if checkout date has passed
        
        Returns:
            Number of bookings updated
        """
        today = date.today()
        bookings = self.get_bookings_by_status("In stay")
        updated_count = 0
        
        for booking in bookings:
            checkout_date_str = booking.get("checkOutDate", "")
            if not checkout_date_str:
                continue
            
            try:
                # Parse checkout date (handle both ISO format and date-only format)
                if "T" in checkout_date_str:
                    checkout_date = datetime.fromisoformat(checkout_date_str.replace("Z", "+00:00")).date()
                else:
                    checkout_date = datetime.strptime(checkout_date_str, "%Y-%m-%d").date()
                
                # If checkout date has passed, mark as completed
                if checkout_date <= today:
                    self.db.update_booking_status(booking.get("bookingID"), "Completed")
                    # Update room status to Available
                    self.db.update_room_status(booking.get("roomId"), "Available")
                    updated_count += 1
            except Exception:
                # Skip if date parsing fails
                continue
        
        return updated_count