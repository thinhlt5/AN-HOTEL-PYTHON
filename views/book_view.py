import customtkinter as ctk
from customtkinter import FontManager
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

# Load fonts from assets/font
current_dir = os.path.dirname(os.path.abspath(__file__))
assets_font_dir = os.path.join(os.path.dirname(current_dir), "assets", "font")

# Load 1FTV HF Gesco font
gesco_font_path = os.path.join(assets_font_dir, "1FTV-HF-Gesco.ttf")
if os.path.exists(gesco_font_path):
    FontManager.load_font(gesco_font_path)

# Load SVN-Gilroy Regular font
gilroy_regular_path = os.path.join(assets_font_dir, "SVN-Gilroy Regular.otf")
if os.path.exists(gilroy_regular_path):
    FontManager.load_font(gilroy_regular_path)

# Load SVN-Gilroy Bold font
gilroy_bold_path = os.path.join(assets_font_dir, "SVN-Gilroy Bold.otf")
if os.path.exists(gilroy_bold_path):
    FontManager.load_font(gilroy_bold_path)


class BookView(ctk.CTkFrame):
    def __init__(self, parent, controller=None, room=None, checkin_date=None, checkout_date=None, num_guests=1, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        # Use controller's services if available, otherwise create new ones
        if controller:
            self.db_manager = controller.get_db_manager()
            self.booking_service = controller.get_booking_service()
        else:
            self.db_manager = DBManager("db")
            self.booking_service = BookingService(self.db_manager)
        self.room = room
        self.checkin_date = checkin_date
        self.checkout_date = checkout_date
        self.num_guests = num_guests
        self.room_type = None
        self.total_amount = 0
        self.is_booking_in_progress = False  # Flag to prevent spam clicking
        self._initialize_room_data()
        self.configure(fg_color="white")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.main_container = ctk.CTkFrame(self, fg_color="white")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=0)
        self.main_container.grid_columnconfigure(1, weight=5)
        
        # Left sidebar - Navigation
        self.sidebar = None  # Initialize sidebar variable
        
        # Right side - Main content
        self.create_main_content()
        
        # Create sidebar after main content
        self.create_sidebar()
    
    def create_sidebar(self):
        """Create left sidebar navigation"""
        # Destroy existing sidebar if it exists
        if self.sidebar:
            self.sidebar.destroy()
        
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            fg_color="#E5E5E5",
            width=150,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Get user name from controller
        user_name = "User"
        if self.controller:
            current_user = self.controller.get_current_user()
            if current_user:
                user_name = current_user.get("name", current_user.get("email", "User"))
        
        # Greeting label
        greeting_label = ctk.CTkLabel(
            self.sidebar,
            text=f"Hi, {user_name}",
            font=("SVN-Gilroy", 16, "bold"),
            text_color="black",
            anchor="w"
        )
        greeting_label.pack(fill="x", padx=10, pady=(20, 10))
        
        # Navigation items for logged-in users
        nav_items = [
            "Home",
            "Room",
            "My Bookings",
            "Account Settings",
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
        
        # Create trip summary section (before book button)
        self.summary_frame = None
        self.summary_widgets = {}
        self.create_trip_summary()
        
        # Error/Success message label (before book button)
        self.error_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="",
            font=("SVN-Gilroy", 16),
            text_color="red",
            anchor="w",
            wraplength=500
        )
        self.error_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        # Create book button (after trip summary and error message)
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
    
    def _initialize_room_data(self):
        """Initialize room type and total amount from current data"""
        self.room_type = None
        
        if self.room:
            # Check if room already has roomType nested object (from SearchView)
            if "roomType" in self.room and self.room["roomType"]:
                self.room_type = self.room["roomType"]
            elif self.db_manager and "typeID" in self.room:
                # Lookup room type by typeID
                room_types = self.db_manager.get_all_room_types()
                if room_types:
                    room_type_id = self.room.get("typeID")
                    # Handle both int and string comparison
                    for rt in room_types:
                        if rt.get("typeID") == room_type_id or str(rt.get("typeID")) == str(room_type_id):
                            self.room_type = rt
                            break
        
        self.total_amount = 0
        if self.room_type and self.checkin_date and self.checkout_date and self.booking_service:
            # Ensure dates are date objects, not strings
            checkin = self.checkin_date
            checkout = self.checkout_date
            
            # Convert string dates to date objects if needed
            if isinstance(checkin, str):
                try:
                    checkin = datetime.strptime(checkin.strip(), "%d/%m/%Y").date()
                except:
                    try:
                        checkin = datetime.strptime(checkin.strip(), "%Y-%m-%d").date()
                    except:
                        checkin = None
            
            if isinstance(checkout, str):
                try:
                    checkout = datetime.strptime(checkout.strip(), "%d/%m/%Y").date()
                except:
                    try:
                        checkout = datetime.strptime(checkout.strip(), "%Y-%m-%d").date()
                    except:
                        checkout = None
            
            if checkin and checkout:
                self.total_amount = self.booking_service.calculate_total_amount(
                    self.room_type.get("price", 0),
                    checkin,
                    checkout,
                    self.num_guests
                )
    
    def create_trip_summary(self):
        """Create trip summary section"""
        # Remove old summary if exists
        if self.summary_frame:
            self.summary_frame.destroy()
        
        # If error_label and button_frame exist, we need to maintain correct order:
        # summary -> error_label -> button
        # So we temporarily remove them, pack summary, then pack them back in order
        error_label_packed = False
        button_frame_packed = False
        
        if hasattr(self, 'error_label') and self.error_label:
            self.error_label.pack_forget()
            error_label_packed = True
        
        if hasattr(self, 'button_frame') and self.button_frame:
            self.button_frame.pack_forget()
            button_frame_packed = True
        
        # Pack summary frame
        self.summary_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white")
        self.summary_frame.pack(fill="x", pady=(0, 30))
        
        # Pack error_label back after summary
        if error_label_packed and hasattr(self, 'error_label') and self.error_label:
            self.error_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        # Pack button frame back after error_label
        if button_frame_packed and hasattr(self, 'button_frame') and self.button_frame:
            self.button_frame.pack(fill="x", pady=(0, 10))
        
        # Title
        summary_title = ctk.CTkLabel(
            self.summary_frame,
            text="Your trip summary",
            font=("SVN-Gilroy", 18, "bold"),
            text_color="black",
            anchor="w"
        )
        summary_title.pack(anchor="w", pady=(0, 15))
        
        # Get room type name
        room_type_name = self.room_type.get("typeName", "Unknown") if self.room_type else "Unknown"
        room_number = self.room.get("roomNumber", "N/A") if self.room else "N/A"
        checkin_str = self.checkin_date.strftime("%d/%m/%Y") if self.checkin_date and hasattr(self.checkin_date, 'strftime') else (str(self.checkin_date) if self.checkin_date else "N/A")
        checkout_str = self.checkout_date.strftime("%d/%m/%Y") if self.checkout_date and hasattr(self.checkout_date, 'strftime') else (str(self.checkout_date) if self.checkout_date else "N/A")
        
        # Create summary items as label pairs
        summary_items = [
            ("Room type", room_type_name),
            ("Room number", str(room_number)),
            ("Check in", checkin_str),
            ("Check out", checkout_str),
            ("Guests", str(self.num_guests)),
            ("Total price", f"{self.total_amount:,} VND")
        ]
        
        # Store widgets for updating
        self.summary_widgets = {}
        
        # Display summary items
        for label_text, value_text in summary_items:
            item_frame = ctk.CTkFrame(self.summary_frame, fg_color="white")
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
            self.summary_widgets[label_text] = value
    
    def update_booking_data(self, room=None, checkin_date=None, checkout_date=None, num_guests=1):
        """Update booking data and refresh the view"""
        if room is not None:
            self.room = room
        if checkin_date is not None:
            self.checkin_date = checkin_date
        if checkout_date is not None:
            self.checkout_date = checkout_date
        if num_guests is not None:
            self.num_guests = num_guests
        
        # Reset booking flag when updating data (new booking)
        self.is_booking_in_progress = False
        
        # Recalculate room data
        self._initialize_room_data()
        
        # Refresh trip summary (this will maintain correct order since it's packed before button)
        self.create_trip_summary()
        
        # Re-enable button if it was disabled
        if hasattr(self, 'book_btn'):
            self.book_btn.configure(state="normal", text="BOOK ROOM")
    
    def create_book_button(self):
        """Create book button"""
        # Store reference to button frame for reordering if needed
        self.button_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white")
        self.button_frame.pack(fill="x", pady=(0, 10))
        
        self.book_btn = ctk.CTkButton(
            self.button_frame,
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
        # Increase window size to prevent button cropping
        success_window.geometry("500x200")
        success_window.resizable(False, False)
        
        # Center the window
        success_window.transient(self)
        success_window.grab_set()
        
        # Main container with padding
        main_container = ctk.CTkFrame(success_window, fg_color="white")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        success_label = ctk.CTkLabel(
            main_container,
            text=message,
            font=("SVN-Gilroy", 18, "bold"),
            text_color="green",
            wraplength=450,
            justify="center"
        )
        success_label.pack(pady=(10, 20))
        
        def close_and_navigate():
            success_window.destroy()
            # Navigate to MyBookingsView instead of destroying frame
            if self.controller:
                self.controller.show_frame("MyBookingsView")
        
        # Button container with proper sizing
        button_container = ctk.CTkFrame(main_container, fg_color="white")
        button_container.pack(fill="x", pady=(10, 0))
        
        ok_btn = ctk.CTkButton(
            button_container,
            text="OK",
            font=("SVN-Gilroy", 16, "bold"),
            fg_color="#8B4513",
            text_color="white",
            hover_color="#A0522D",
            height=40,
            width=120,
            command=close_and_navigate
        )
        ok_btn.pack(pady=10)
    
    def on_book_room(self):
        """Handle book room button click"""
        # Prevent spam clicking - if already processing, ignore
        if self.is_booking_in_progress:
            return
        
        # Validate form
        if not self.validate_form():
            return
        
        # Set flag and disable button to prevent spam
        self.is_booking_in_progress = True
        self.book_btn.configure(state="disabled", text="Processing...")
        
        try:
            # Get customer ID from session if user is logged in
            customer_id = None
            if self.controller:
                current_user = self.controller.get_current_user()
                if current_user:
                    customer_id = current_user.get("customerID")
            
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
                total_amount=self.total_amount,
                customer_id=customer_id
            )
            
            # Show success message (will navigate away, so don't re-enable button)
            self.show_success(f"Booking successful!\nBooking ID: {booking['bookingID']}\nRoom: #{self.room['roomNumber']}")
            
        except Exception as e:
            # Re-enable button on error so user can try again
            self.is_booking_in_progress = False
            self.book_btn.configure(state="normal", text="BOOK ROOM")
            self.show_error(f"Error creating booking: {str(e)}")
    
    def on_nav_click(self, item):
        """Handle navigation item click"""
        if not self.controller:
            return
        
        nav_map = {
            "Home": "MainAppView",
            "Room": "RoomView",
            "My Bookings": "MyBookingsView",
            "Account Settings": "AccountView",
            "Sign out": None  # Special handling
        }
        
        if item == "Sign out":
            self.controller.logout()
            return
        
        target = nav_map.get(item)
        if target:
            self.controller.show_frame(target)
    
    def on_show(self):
        """Called when this view is shown - refresh sidebar to reflect login status"""
        self.create_sidebar()


if __name__ == "__main__":
    app = BookView()
    app.mainloop()
