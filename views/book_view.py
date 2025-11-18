import customtkinter as ctk
from datetime import datetime, date
import sys
import os
import re

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.db_manager import DBManager
from modules.booking_service import BookingService

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class BookView(ctk.CTk):
    def __init__(self, room=None, checkin_date=None, checkout_date=None, num_guests=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set window properties
        self.title("AN Hotel - Book Room")
        self.geometry("630x750")
        self.resizable(False, False)
        
        # Initialize services
        self.db_manager = DBManager("db")
        self.booking_service = BookingService()
        
        # Store booking parameters
        self.room = room
        self.checkin_date = checkin_date
        self.checkout_date = checkout_date
        self.num_guests = num_guests
        
        # Get room type info
        self.room_type = None
        if room:
            room_types = self.db_manager.get_all_room_types()
            for rt in room_types:
                if rt["typeID"] == room["typeID"]:
                    self.room_type = rt
                    break
        
        # Calculate total amount
        self.total_amount = 0
        if self.room_type and self.checkin_date and self.checkout_date:
            self.total_amount = self.booking_service.calculate_total_amount(
                self.room_type.get("price", 0),
                self.checkin_date,
                self.checkout_date,
                self.num_guests
            )
        
        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color="white")
        self.main_container.pack(side="top", fill="both", expand=True)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=0)  # Sidebar
        self.main_container.grid_columnconfigure(1, weight=5)  # Main content
        
        # Left sidebar - Navigation
        self.create_sidebar()
        
        # Right side - Main content
        self.create_main_content()
    
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
    
    def create_main_content(self):
        """Create main content area"""
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="white"
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Create scrollable frame for content
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="white"
        )
        self.scrollable_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Enter your details",
            font=("SVN-Gilroy", 28, "bold"),
            text_color="black",
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 30))
        
        # Create form section
        self.create_booking_form()
        
        # Create trip summary section
        self.create_trip_summary()
        
        # Error message label (initially hidden)
        self.error_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="",
            font=("SVN-Gilroy", 16),
            text_color="red",
            anchor="w",
            wraplength=500
        )
        self.error_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        # Create book button
        self.create_book_button()
    
    def create_booking_form(self):
        """Create booking form with guest details"""
        form_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white")
        form_frame.pack(fill="x", pady=(0, 30))
        
        # Full name
        name_label = ctk.CTkLabel(
            form_frame,
            text="Full name",
            font=("SVN-Gilroy", 14),
            text_color="black",
            anchor="w"
        )
        name_label.pack(anchor="w", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your full name",
            font=("SVN-Gilroy", 13),
            height=40,
            corner_radius=5,
            border_color="#E5E5E5",
            fg_color="white",
            text_color="black"
        )
        self.name_entry.pack(fill="x", pady=(0, 20))
        
        # Phone number
        phone_label = ctk.CTkLabel(
            form_frame,
            text="Phone number",
            font=("SVN-Gilroy", 14),
            text_color="black",
            anchor="w"
        )
        phone_label.pack(anchor="w", pady=(0, 5))
        
        self.phone_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your phone number",
            font=("SVN-Gilroy", 13),
            height=40,
            corner_radius=5,
            border_color="#E5E5E5",
            fg_color="white",
            text_color="black"
        )
        self.phone_entry.pack(fill="x", pady=(0, 20))
        
        # Email Address
        email_label = ctk.CTkLabel(
            form_frame,
            text="Email Address",
            font=("SVN-Gilroy", 14),
            text_color="black",
            anchor="w"
        )
        email_label.pack(anchor="w", pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your email address",
            font=("SVN-Gilroy", 13),
            height=40,
            corner_radius=5,
            border_color="#E5E5E5",
            fg_color="white",
            text_color="black"
        )
        self.email_entry.pack(fill="x", pady=(0, 20))
        
        # National ID
        national_id_label = ctk.CTkLabel(
            form_frame,
            text="National ID",
            font=("SVN-Gilroy", 14),
            text_color="black",
            anchor="w"
        )
        national_id_label.pack(anchor="w", pady=(0, 5))
        
        self.national_id_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your national ID",
            font=("SVN-Gilroy", 13),
            height=40,
            corner_radius=5,
            border_color="#E5E5E5",
            fg_color="white",
            text_color="black"
        )
        self.national_id_entry.pack(fill="x", pady=(0, 20))
    
    def create_trip_summary(self):
        """Create trip summary section"""
        summary_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white")
        summary_frame.pack(fill="x", pady=(0, 30))
        
        # Title
        summary_title = ctk.CTkLabel(
            summary_frame,
            text="Your trip summary",
            font=("SVN-Gilroy", 18, "bold"),
            text_color="black",
            anchor="w"
        )
        summary_title.pack(anchor="w", pady=(0, 15))
        
        # Get room type name
        room_type_name = self.room_type.get("typeName", "Unknown") if self.room_type else "Unknown"
        room_number = self.room.get("roomNumber", "N/A") if self.room else "N/A"
        checkin_str = self.checkin_date.strftime("%d/%m/%Y") if self.checkin_date else "N/A"
        checkout_str = self.checkout_date.strftime("%d/%m/%Y") if self.checkout_date else "N/A"
        
        # Create summary items as label pairs
        summary_items = [
            ("Room type", room_type_name),
            ("Room number", str(room_number)),
            ("Check in", checkin_str),
            ("Check out", checkout_str),
            ("Guests", str(self.num_guests)),
            ("Total price", f"{self.total_amount:,} VND")
        ]
        
        # Display summary items
        for label_text, value_text in summary_items:
            item_frame = ctk.CTkFrame(summary_frame, fg_color="white")
            item_frame.pack(fill="x", pady=5)
            
            # Label on the left
            label = ctk.CTkLabel(
                item_frame,
                text=label_text,
                font=("SVN-Gilroy", 13),
                text_color="black",
                anchor="w"
            )
            label.pack(side="left", anchor="w")
            
            # Value on the right with dynamic spacing
            value = ctk.CTkLabel(
                item_frame,
                text=value_text,
                font=("SVN-Gilroy", 13) if label_text == "Total price" else ("SVN-Gilroy", 12),
                text_color="black" if label_text == "Total price" else "gray",
                anchor="e"
            )
            value.pack(side="right", anchor="e", fill="x", expand=True, padx=(20, 0))
    
    def create_book_button(self):
        """Create book button"""
        button_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white")
        button_frame.pack(fill="x", pady=(30, 0))
        
        self.book_btn = ctk.CTkButton(
            button_frame,
            text="BOOK ROOM",
            font=("SVN-Gilroy", 16, "bold"),
            fg_color="#8B4513",
            text_color="white",
            hover_color="#A0522D",
            height=50,
            corner_radius=5,
            command=self.on_book_room
        )
        self.book_btn.pack(fill="x")
    
    def validate_form(self):
        """Validate booking form"""
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        national_id = self.national_id_entry.get().strip()
        
        # Validate name
        if not name or len(name) < 2:
            self.show_error("Please enter a valid full name")
            return False
        
        # Validate phone
        if not phone or not re.match(r'^\d{10,}$', phone.replace('-', '').replace(' ', '')):
            self.show_error("Please enter a valid phone number")
            return False
        
        # Validate email
        if not email or not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            self.show_error("Please enter a valid email address")
            return False
        
        # Validate national ID
        if not national_id or len(national_id) < 8:
            self.show_error("Please enter a valid national ID")
            return False
        
        return True
    
    def show_error(self, message):
        """Show error message in the form"""
        self.error_label.configure(text=message)
        self.scrollable_frame._parent_canvas.yview_moveto(0.5)  # Scroll to show error
    
    def show_success(self, message):
        """Show success dialog"""
        success_window = ctk.CTkToplevel(self)
        success_window.title("Success")
        success_window.geometry("400x150")
        success_window.resizable(False, False)
        
        success_label = ctk.CTkLabel(
            success_window,
            text=message,
            font=("SVN-Gilroy", 20, "bold"),
            text_color="green",
            wraplength=350
        )
        success_label.pack(padx=20, pady=20)
        
        ok_btn = ctk.CTkButton(
            success_window,
            text="OK",
            font=("SVN-Gilroy", 20, "bold"),
            command=lambda: [success_window.destroy(), self.destroy()]
        )
        ok_btn.pack(pady=10)
    
    def on_book_room(self):
        """Handle book room button click"""
        # Validate form
        if not self.validate_form():
            return
        
        try:
            # Create booking using booking service
            guest_name = self.name_entry.get().strip()
            guest_phone = self.phone_entry.get().strip()
            guest_email = self.email_entry.get().strip()
            guest_national_id = self.national_id_entry.get().strip()
            
            booking = self.booking_service.create_booking(
                room_id=self.room["roomId"],
                checkin_date=self.checkin_date,
                checkout_date=self.checkout_date,
                num_guests=self.num_guests,
                guest_name=guest_name,
                guest_phone=guest_phone,
                guest_email=guest_email,
                guest_national_id=guest_national_id,
                total_amount=self.total_amount
            )
            
            # Show success message
            self.show_success(f"Booking successful!\nBooking ID: {booking['bookingID']}\nRoom: #{self.room['roomNumber']}")
            
        except Exception as e:
            self.show_error(f"Error creating booking: {str(e)}")
    
    def on_nav_click(self, item):
        """Handle navigation item click"""
        print(f"Navigation clicked: {item}")
        # TODO: Implement navigation functionality


if __name__ == "__main__":
    app = BookView()
    app.mainloop()
