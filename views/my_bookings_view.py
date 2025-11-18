import customtkinter as ctk
from PIL import Image
import os
from datetime import datetime, date
import re
import sys
import json

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.db_manager import DBManager
from modules.search_service import SearchService
from book_view import BookView

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class MyBookingsView(ctk.CTk):
    def __init__(self, checkin=None, checkout=None, guests=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set window properties
        self.title("AN Hotel - Search Results")
        self.geometry("1000x750")
        self.resizable(False, False)
        
        # Initialize database manager
        self.db_manager = DBManager("db")
        
        # Initialize search service
        self.search_service = SearchService()
        
        # Store search parameters
        self.search_checkin = checkin
        self.search_checkout = checkout
        self.search_guests = guests
        
        # Parse dates if provided
        self.checkin_date = None
        self.checkout_date = None
        if checkin:
            self.checkin_date = self.search_service.parse_date(checkin)
        if checkout:
            self.checkout_date = self.search_service.parse_date(checkout)
        
        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color="white")
        self.main_container.pack(side="top", fill="both", expand=True)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=0)  # Sidebar
        self.main_container.grid_columnconfigure(1, weight=5)  # Main content
        
        # Left sidebar - Navigation
        self.create_sidebar()
        
        # Right side - Main content (TabView for bookings)
        self.create_bookings_tabview()
    
    def create_sidebar(self):
        """Create left sidebar navigation"""
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            fg_color="#E5E5E5",
            width=150,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Navigation items
        nav_items = [
            "Home",
            "Rooms",
            "Our Services",
            "My Bookings",
            "Account settings",
            "Sign out"
        ]
        
        # Create navigation buttons
        for i, item in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=item,
                font=("SVN-Gilroy", 14),
                fg_color="transparent",
                text_color="black",
                hover_color="#D0D0D0",
                height=50,
                corner_radius=5,
                anchor="w",
                command=lambda x=item: self.on_nav_click(x)
            )
            btn.pack(fill="x", padx=10, pady=5)
    
    def create_bookings_tabview(self):
        """Create TabView for bookings (Upcoming, Completed, Canceled)"""
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="white"
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=(20,0))

        self.tabview = ctk.CTkTabview(self.content_frame, fg_color="white", segmented_button_fg_color="#E5E5E5", segmented_button_selected_color="#3A7BFF", segmented_button_unselected_color="#A9A9A9")
        self.tabview.pack(fill="both", expand=True)

        self.tab_upcoming = self.tabview.add("Upcoming")
        self.tab_completed = self.tabview.add("Completed")
        self.tab_canceled = self.tabview.add("Canceled")

        # Scrollable frames for each tab
        self.upcoming_frame = ctk.CTkScrollableFrame(self.tab_upcoming, fg_color="#F5F5F5")
        self.upcoming_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.completed_frame = ctk.CTkScrollableFrame(self.tab_completed, fg_color="#F5F5F5")
        self.completed_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.canceled_frame = ctk.CTkScrollableFrame(self.tab_canceled, fg_color="#F5F5F5")
        self.canceled_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_bookings_data()

    def load_bookings_data(self):
        """Load bookings from booking.json and display in tabs"""
        bookings = []
        try:
            with open(os.path.join("db", "booking.json"), "r", encoding="utf-8") as f:
                bookings = json.load(f)
        except Exception as e:
            print("Error loading bookings:", e)
            return

        # Clear frames
        for frame in [self.upcoming_frame, self.completed_frame, self.canceled_frame]:
            for widget in frame.winfo_children():
                widget.destroy()

        upcoming_status = ["pending", "confirmed", "in_sstay"]
        completed_status = ["completed"]
        canceled_status = ["canceled"]

        for booking in bookings:
            status = str(booking.get("status", "")).strip().lower()
            if status in [s.lower() for s in upcoming_status]:
                self.create_booking_card(self.upcoming_frame, booking, show_cancel=(status=="pending"))
            elif status in [s.lower() for s in completed_status]:
                self.create_booking_card(self.completed_frame, booking, show_cancel=False)
            elif status in [s.lower() for s in canceled_status]:
                self.create_booking_card(self.canceled_frame, booking, show_cancel=False)

    def create_booking_card(self, parent, booking, show_cancel=False):
        """Create a booking card widget styled like trip summary, with all required fields"""
        card = ctk.CTkFrame(parent, fg_color="white", border_color="#E5E5E5", border_width=2, corner_radius=15)
        card.pack(fill="x", pady=10, padx=10)

        # Title
        title = ctk.CTkLabel(card, text=f"Booking ID: {booking.get('bookingID', '')}", font=("SVN-Gilroy", 16, "bold"), text_color="black", anchor="w")
        title.pack(anchor="w", pady=(10, 5), padx=20)

        # Get room number from room.json
        room_number = ""
        try:
            room_id = booking.get("roomId")
            if room_id:
                with open(os.path.join("db", "room.json"), "r", encoding="utf-8") as f:
                    rooms = json.load(f)
                for r in rooms:
                    if r.get("roomId") == room_id:
                        room_number = r.get("roomNumber", "")
                        break
        except Exception:
            room_number = ""

        # Format dates
        def format_date(dt):
            try:
                from datetime import datetime
                if dt:
                    if "T" in dt:
                        dt = dt.split("T")[0]
                    return datetime.strptime(dt, "%Y-%m-%d").strftime("%d/%m/%Y")
            except Exception:
                pass
            return dt

        checkin = format_date(booking.get("checkInDate", ""))
        checkout = format_date(booking.get("checkOutDate", ""))
        guests = booking.get("numGuests", booking.get("guests", ""))
        total = booking.get("totalAmount", booking.get("total", 0))
        status = booking.get("status", "")

        # Summary items
        summary_items = [
            ("Room number", room_number),
            ("Check-in date", checkin),
            ("Check-out date", checkout),
            ("Guests", str(guests)),
            ("Total", f"{total:,} VND"),
            ("Status", status)
        ]

        for label_text, value_text in summary_items:
            item_frame = ctk.CTkFrame(card, fg_color="white")
            item_frame.pack(fill="x", pady=2, padx=20)
            label = ctk.CTkLabel(item_frame, text=label_text, font=("SVN-Gilroy", 13), text_color="black", anchor="w")
            label.pack(side="left", anchor="w")
            value = ctk.CTkLabel(item_frame, text=value_text, font=("SVN-Gilroy", 13) if label_text=="Total" else ("SVN-Gilroy", 12), text_color="black" if label_text in ["Total", "Status"] else "gray", anchor="e")
            value.pack(side="right", anchor="e", fill="x", expand=True, padx=(20,0))

        if show_cancel:
            btn_frame = ctk.CTkFrame(card, fg_color="white")
            btn_frame.pack(fill="x", pady=(10, 15), padx=20)
            cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", font=("SVN-Gilroy", 14), fg_color="#555555", text_color="white", hover_color="#A0522D", corner_radius=10, command=lambda b=booking: self.cancel_booking(b))
            cancel_btn.pack(anchor="e")

    def cancel_booking(self, booking):
        """Call BookingService to cancel booking, then refresh UI"""
        from modules.booking_service import BookingService
        service = BookingService()
        booking_id = booking.get("bookingID")
        # If you have customer_id, pass it, else None
        service.cancel_booking(booking_id, None)
        self.load_bookings_data()
    
    def on_nav_click(self, item):
        """Handle navigation item click"""
        print(f"Navigation clicked: {item}")
        # TODO: Implement navigation functionality


if __name__ == "__main__":
    app = MyBookingsView()
    app.mainloop()

