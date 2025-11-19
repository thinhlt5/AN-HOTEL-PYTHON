import customtkinter as ctk
from customtkinter import FontManager
from PIL import Image
import os
from datetime import datetime, date
import re
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.db_manager import DBManager
from modules.search_service import SearchService

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

class SearchView(ctk.CTkFrame):
    def __init__(self, parent, controller=None, checkin=None, checkout=None, guests=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        # Use controller's services if available
        if controller:
            self.db_manager = controller.get_db_manager()
        else:
            self.db_manager = DBManager("db")
        self.search_service = SearchService()
        self.search_checkin = checkin
        self.search_checkout = checkout
        self.search_guests = guests
        self.checkin_date = None
        self.checkout_date = None
        if checkin:
            self.checkin_date = self.search_service.parse_date(checkin)
        if checkout:
            self.checkout_date = self.search_service.parse_date(checkout)
        self.configure(fg_color="white")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.main_container = ctk.CTkFrame(self, fg_color="white")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=0)
        self.main_container.grid_columnconfigure(1, weight=5)
        self.create_sidebar()
        self.create_main_content()
    
    def set_search_criteria_and_reload(self, checkin, checkout, guests):
        """Set new search criteria and reload the view."""
        self.search_checkin = checkin
        self.search_checkout = checkout
        self.search_guests = guests

        # Update entry widgets
        if hasattr(self, 'checkin_entry'):
            self.checkin_entry.delete(0, 'end')
            self.checkin_entry.insert(0, checkin)
        if hasattr(self, 'checkout_entry'):
            self.checkout_entry.delete(0, 'end')
            self.checkout_entry.insert(0, checkout)
        if hasattr(self, 'guests_entry'):
            self.guests_entry.delete(0, 'end')
            self.guests_entry.insert(0, guests)

        # Reload rooms with new data
        self.reload_rooms()

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
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=(20,0))
        
        # Create scrollable frame for content
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="white"
        )
        self.scrollable_frame.pack(fill="both", expand=True)
        
        # Search section at top
        self.create_search_section()
        
        # Filters section
        self.create_filters_section()
        
        # Rooms results section
        self.create_rooms_results_section()
    
    def create_search_section(self):
        """Create search form with date inputs"""
        search_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="white"
        )
        search_frame.pack(fill="x", pady=5)
        
        # Check-in date
        checkin_label = ctk.CTkLabel(
            search_frame,
            text="Check in date:",
            font=("SVN-Gilroy", 14),
            text_color="black",
            anchor="w"
        )
        checkin_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.checkin_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="DD/MM/YYYY",
            font=("SVN-Gilroy", 14),
            height=40,
            corner_radius=5,
            border_color="#E5E5E5",
            fg_color="white",
            text_color="black"
        )
        self.checkin_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        # Set value if provided
        if self.search_checkin:
            self.checkin_entry.insert(0, self.search_checkin)
        self.checkin_entry.bind("<KeyRelease>", lambda e: self.validate_dates())
        self.checkin_entry.bind("<FocusOut>", lambda e: self.validate_dates())
        
        # Check-out date
        checkout_label = ctk.CTkLabel(
            search_frame,
            text="Check out date:",
            font=("SVN-Gilroy", 14),
            text_color="black",
            anchor="w"
        )
        checkout_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        self.checkout_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="DD/MM/YYYY",
            font=("SVN-Gilroy", 14),
            height=40,
            corner_radius=5,
            border_color="#E5E5E5",
            fg_color="white",
            text_color="black"
        )
        self.checkout_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        # Set value if provided
        if self.search_checkout:
            self.checkout_entry.insert(0, self.search_checkout)
        self.checkout_entry.bind("<KeyRelease>", lambda e: self.validate_dates())
        self.checkout_entry.bind("<FocusOut>", lambda e: self.validate_dates())
        
        # Number of guests
        guests_label = ctk.CTkLabel(
            search_frame,
            text="Number of guests:",
            font=("SVN-Gilroy", 14),
            text_color="black",
            anchor="w"
        )
        guests_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        self.guests_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="1",
            font=("SVN-Gilroy", 14),
            height=40,
            corner_radius=5,
            border_color="#E5E5E5",
            fg_color="white",
            text_color="black"
        )
        self.guests_entry.grid(row=1, column=2, padx=10, pady=5, sticky="ew")
        # Set value if provided
        if self.search_guests:
            self.guests_entry.insert(0, str(self.search_guests))
        
        # Search button
        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            font=("SVN-Gilroy", 16, "bold"),
            fg_color="#8B4513",
            text_color="white",
            hover_color="#A0522D",
            height=40,
            corner_radius=5,
            command=self.reload_rooms
        )
        search_btn.grid(row=1, column=3, padx=10, pady=5, sticky="ew")
        
        # Configure grid weights
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=1)
        search_frame.grid_columnconfigure(2, weight=1)
        search_frame.grid_columnconfigure(3, weight=1)
        
        # Error label for date validation
        self.date_error_label = ctk.CTkLabel(
            search_frame,
            text="",
            font=("SVN-Gilroy", 12),
            text_color="red",
            anchor="w"
        )
        self.date_error_label.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="w")
    
    def create_filters_section(self):
        """Create filters section"""
        filters_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="#F5F5F5",
            corner_radius=10
        )
        filters_frame.pack(fill="x", pady=(20, 10), padx=10)
        
        filters_label = ctk.CTkLabel(
            filters_frame,
            text="Filters",
            font=("SVN-Gilroy", 16, "bold"),
            text_color="black",
            anchor="w"
        )
        filters_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Filter controls container
        filters_controls = ctk.CTkFrame(filters_frame, fg_color="#F5F5F5")
        filters_controls.pack(fill="x", padx=15, pady=(5, 10))
        filters_controls.grid_columnconfigure(0, weight=1)
        filters_controls.grid_columnconfigure(1, weight=1)
        filters_controls.grid_columnconfigure(2, weight=2)
        
        # Price filter
        price_label = ctk.CTkLabel(
            filters_controls,
            text="Price Range:",
            font=("SVN-Gilroy", 12),
            text_color="black"
        )
        price_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        price_frame = ctk.CTkFrame(filters_controls, fg_color="#F5F5F5")
        price_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        self.min_price_entry = ctk.CTkEntry(
            price_frame,
            placeholder_text="0",
            font=("SVN-Gilroy", 11),
            width=80,
            height=30,
            corner_radius=5,
            fg_color="white",
            text_color="black",
            border_color="#E5E5E5"
        )
        self.min_price_entry.pack(side="left", padx=5)
        self.min_price_entry.insert(0, "0")
        
        max_price_label = ctk.CTkLabel(price_frame, text="Max:", font=("SVN-Gilroy", 11), text_color="black")
        max_price_label.pack(side="left", padx=(10, 5))
        
        self.max_price_entry = ctk.CTkEntry(
            price_frame,
            placeholder_text="3000000",
            font=("SVN-Gilroy", 11),
            width=80,
            height=30,
            corner_radius=5,
            fg_color="white",
            text_color="black",
            border_color="#E5E5E5"
        )
        self.max_price_entry.pack(side="left", padx=5)
        self.max_price_entry.insert(0, "3000000")
        
        # Room type filter
        type_label = ctk.CTkLabel(
            filters_controls,
            text="Room Type:",
            font=("SVN-Gilroy", 12),
            text_color="black"
        )
        type_label.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Get all room types
        self.room_types = self.search_service.get_all_room_types()
        type_options = ["All Types"] + [rt["typeName"] for rt in self.room_types]
        
        self.room_type_var = ctk.StringVar(value="All Types")
        
        type_menu = ctk.CTkComboBox(
            filters_controls,
            values=type_options,
            variable=self.room_type_var,
            font=("SVN-Gilroy", 11),
            height=30,
            corner_radius=5,
            fg_color="white",
            text_color="black",
            border_color="#E5E5E5",
            dropdown_font=("SVN-Gilroy", 11)
        )
        type_menu.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        # Apply filters button
        apply_btn = ctk.CTkButton(
            filters_controls,
            text="Apply Filters",
            font=("SVN-Gilroy", 12, "bold"),
            fg_color="#8B4513",
            text_color="white",
            hover_color="#A0522D",
            height=35,
            corner_radius=5,
            command=self.apply_filters
        )
        apply_btn.grid(row=1, column=2, sticky="e", padx=10, pady=5)
    
    def create_rooms_results_section(self):
        """Create rooms results section"""
        self.rooms_results_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="white"
        )
        self.rooms_results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Section title
        title_label = ctk.CTkLabel(
            self.rooms_results_frame,
            text="Available Rooms",
            font=("SVN-Gilroy", 24, "bold"),
            text_color="black",
            anchor="w"
        )
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Rooms container
        self.rooms_container = ctk.CTkFrame(
            self.rooms_results_frame,
            fg_color="white"
        )
        self.rooms_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load and display available rooms
        self.load_available_rooms()
    
    def parse_date(self, date_str):
        """Parse date string in DD/MM/YYYY format"""
        try:
            # Try DD/MM/YYYY format
            return datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
        except ValueError:
            try:
                # Try YYYY-MM-DD format
                return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
            except ValueError:
                return None
    
    def validate_date_format(self, date_str):
        """Validate date format"""
        if not date_str or not date_str.strip():
            return False
        
        # Check DD/MM/YYYY format
        pattern1 = r'^\d{2}/\d{2}/\d{4}$'
        # Check YYYY-MM-DD format
        pattern2 = r'^\d{4}-\d{2}-\d{2}$'
        
        return bool(re.match(pattern1, date_str.strip()) or re.match(pattern2, date_str.strip()))
    
    def validate_dates(self):
        """Validate check-in and check-out dates"""
        checkin_str = self.checkin_entry.get().strip()
        checkout_str = self.checkout_entry.get().strip()
        
        # Clear previous errors
        self.date_error_label.configure(text="")
        self.checkin_entry.configure(border_color="#E5E5E5")
        self.checkout_entry.configure(border_color="#E5E5E5")
        
        # If both fields are empty, no error
        if not checkin_str and not checkout_str:
            return True
        
        # Validate check-in date
        if checkin_str:
            if not self.validate_date_format(checkin_str):
                self.date_error_label.configure(text="Check-in date must be in DD/MM/YYYY format")
                self.checkin_entry.configure(border_color="red")
                return False
            
            checkin_date = self.parse_date(checkin_str)
            if checkin_date is None:
                self.date_error_label.configure(text="Invalid check-in date format")
                self.checkin_entry.configure(border_color="red")
                return False
            
            # Check if check-in date is not in the past
            today = date.today()
            if checkin_date < today:
                self.date_error_label.configure(text="Check-in date cannot be in the past")
                self.checkin_entry.configure(border_color="red")
                return False
        
        # Validate check-out date
        if checkout_str:
            if not self.validate_date_format(checkout_str):
                self.date_error_label.configure(text="Check-out date must be in DD/MM/YYYY format")
                self.checkout_entry.configure(border_color="red")
                return False
            
            checkout_date = self.parse_date(checkout_str)
            if checkout_date is None:
                self.date_error_label.configure(text="Invalid check-out date format")
                self.checkout_entry.configure(border_color="red")
                return False
        
        # Validate check-out is after check-in
        if checkin_str and checkout_str:
            checkin_date = self.parse_date(checkin_str)
            checkout_date = self.parse_date(checkout_str)
            
            if checkin_date and checkout_date:
                if checkout_date <= checkin_date:
                    self.date_error_label.configure(text="Check-out date must be after check-in date")
                    self.checkout_entry.configure(border_color="red")
                    return False
        
        return True
    
    def reload_rooms(self):
        """Reload rooms based on current search parameters"""
        # Validate dates first
        if not self.validate_dates():
            # Clear rooms if validation fails
            for widget in self.rooms_container.winfo_children():
                widget.destroy()
            return
        
        # Update search parameters from current entries
        self.search_checkin = self.checkin_entry.get().strip()
        self.search_checkout = self.checkout_entry.get().strip()
        self.search_guests = self.guests_entry.get().strip()
        
        # Parse dates using search service
        if self.search_checkin:
            self.checkin_date = self.search_service.parse_date(self.search_checkin)
        if self.search_checkout:
            self.checkout_date = self.search_service.parse_date(self.search_checkout)
        
        # Reload rooms only if dates are valid
        if self.checkin_date and self.checkout_date:
            self.load_available_rooms()
    
    def load_available_rooms(self):
        """Load and display available rooms from database"""
        # Clear existing rooms
        for widget in self.rooms_container.winfo_children():
            widget.destroy()
        
        # Check if we have valid search parameters
        if not self.checkin_date or not self.checkout_date:
            no_rooms_label = ctk.CTkLabel(
                self.rooms_container,
                text="Please enter valid check-in and check-out dates to see available rooms",
                font=("SVN-Gilroy", 14),
                text_color="gray"
            )
            no_rooms_label.pack(pady=20)
            return
        
        # Get room type filter if applicable
        selected_type = self.room_type_var.get() if hasattr(self, 'room_type_var') else "All Types"
        
        # Find available rooms using search service
        available_rooms = self.search_service.find_available_rooms(
            self.checkin_date, self.checkout_date, selected_type
        )
        
        if not available_rooms:
            no_rooms_label = ctk.CTkLabel(
                self.rooms_container,
                text="No available rooms found for the selected dates",
                font=("SVN-Gilroy", 16),
                text_color="gray"
            )
            no_rooms_label.pack(pady=20)
            return
        
        # Display rooms
        for room in available_rooms:
            self.create_room_card(room)
    
    def create_room_card(self, room):
        """Create a room card widget"""
        room_type = room.get("roomType", {})
        
        # Main room card frame
        card_frame = ctk.CTkFrame(
            self.rooms_container,
            fg_color="white",
            border_color="#E5E5E5",
            border_width=2,
            corner_radius=10
        )
        card_frame.pack(fill="x", pady=10)
        
        # Inner container with grid layout
        inner_frame = ctk.CTkFrame(card_frame, fg_color="white")
        inner_frame.pack(fill="x", padx=15, pady=15)
        inner_frame.grid_columnconfigure(0, weight=0)
        inner_frame.grid_columnconfigure(1, weight=3)
        
        # Image placeholder on the left
        image_frame = ctk.CTkFrame(
            inner_frame,
            fg_color="#E5E5E5",
            width=180,
            height=180,
            corner_radius=8
        )
        image_frame.grid(row=0, column=0, rowspan=3, padx=(0, 15), pady=0, sticky="nsew")
        image_frame.pack_propagate(False)
        
        try:
            image_path = room_type.get("imagePath", "")
            if image_path and os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize((180, 180))
                photo = ctk.CTkImage(light_image=image, size=(180, 180))
                img_label = ctk.CTkLabel(image_frame, image=photo, text="")
                img_label.image = photo
                img_label.pack(fill="both", expand=True)
            else:
                img_label = ctk.CTkLabel(
                    image_frame,
                    text="Room Image",
                    font=("SVN-Gilroy", 14),
                    text_color="gray"
                )
                img_label.pack(fill="both", expand=True)
        except Exception as e:
            img_label = ctk.CTkLabel(
                image_frame,
                text="Room Image",
                font=("SVN-Gilroy", 14),
                text_color="gray"
            )
            img_label.pack(fill="both", expand=True)
        
        # Right side - Room details
        details_frame = ctk.CTkFrame(inner_frame, fg_color="white")
        details_frame.grid(row=0, column=1, sticky="ew", pady=0)
        details_frame.grid_columnconfigure(0, weight=1)
        
        # Room type and room number
        header_frame = ctk.CTkFrame(details_frame, fg_color="white")
        header_frame.pack(fill="x", pady=(0, 5))
        
        room_type_label = ctk.CTkLabel(
            header_frame,
            text=room_type.get("typeName", "Unknown Type"),
            font=("SVN-Gilroy", 20, "bold"),
            text_color="black",
            anchor="w"
        )
        room_type_label.pack(anchor="w", side="left")
        
        room_number_label = ctk.CTkLabel(
            header_frame,
            text=f"Room #{room['roomNumber']}",
            font=("SVN-Gilroy", 12),
            text_color="gray",
            anchor="w"
        )
        room_number_label.pack(anchor="w", side="left", padx=(10, 0))
        
        # Description
        desc_text = room_type.get("description", "No description available")
        desc_label = ctk.CTkLabel(
            details_frame,
            text=desc_text,
            font=("SVN-Gilroy", 12),
            text_color="#555555",
            anchor="w",
            justify="left",
            wraplength=500
        )
        desc_label.pack(anchor="w", fill="x", pady=(0, 10))
        
        # Services label (placeholder)
        services_label = ctk.CTkLabel(
            details_frame,
            text="Services: Lorem ipsum dolor sit amet consectetur",
            font=("SVN-Gilroy", 11),
            text_color="black",
            anchor="w"
        )
        services_label.pack(anchor="w", fill="x", pady=(5, 0))
        
        # Bottom row - Price and Book button
        bottom_frame = ctk.CTkFrame(inner_frame, fg_color="white")
        bottom_frame.grid(row=1, column=1, sticky="ew", pady=(10, 0))
        bottom_frame.grid_columnconfigure(0, weight=1)
        
        # Price section
        price = room_type.get("price", 0)
        price_label = ctk.CTkLabel(
            bottom_frame,
            text=f"Price: {price:,} VND",
            font=("SVN-Gilroy", 14, "bold"),
            text_color="black",
            anchor="w"
        )
        price_label.pack(anchor="w", fill="x", pady=(10, 5))
        
        # Button row
        button_frame = ctk.CTkFrame(bottom_frame, fg_color="white")
        button_frame.pack(fill="x", pady=(5, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Book Now button
        book_btn = ctk.CTkButton(
            button_frame,
            text="BOOK NOW",
            font=("SVN-Gilroy", 12, "bold"),
            fg_color="#8B4513",
            text_color="white",
            hover_color="#A0522D",
            height=35,
            corner_radius=5,
            command=lambda r=room: self.on_book_now(r)
        )
        book_btn.pack(side="left", padx=(0, 10))
    
    def apply_filters(self):
        """Apply filters and reload rooms"""
        # Get filter values
        try:
            min_price = int(self.min_price_entry.get()) if self.min_price_entry.get() else 0
        except ValueError:
            min_price = 0
        
        try:
            max_price = int(self.max_price_entry.get()) if self.max_price_entry.get() else 999999999
        except ValueError:
            max_price = 999999999
        
        selected_type = self.room_type_var.get()
        
        # Clear existing rooms
        for widget in self.rooms_container.winfo_children():
            widget.destroy()
        
        # Check if we have valid search parameters
        if not self.checkin_date or not self.checkout_date:
            no_rooms_label = ctk.CTkLabel(
                self.rooms_container,
                text="Please enter valid check-in and check-out dates to see available rooms",
                font=("SVN-Gilroy", 14),
                text_color="gray"
            )
            no_rooms_label.pack(pady=20)
            return
        
        # Find available rooms using search service
        available_rooms = self.search_service.find_available_rooms(
            self.checkin_date, self.checkout_date
        )
        
        # Apply filters using search service
        filtered_rooms = self.search_service.apply_filters(
            available_rooms, min_price, max_price, selected_type
        )
        
        if not filtered_rooms:
            no_rooms_label = ctk.CTkLabel(
                self.rooms_container,
                text="No available rooms match your filters",
                font=("SVN-Gilroy", 16),
                text_color="gray"
            )
            no_rooms_label.pack(pady=20)
            return
        
        # Display filtered rooms
        for room in filtered_rooms:
            self.create_room_card(room)
    
    def on_book_now(self, room):
        """Handle book now button click - Show BookView frame"""
        if not self.controller:
            return
        
        # Get number of guests from entry
        try:
            num_guests = int(self.guests_entry.get()) if self.guests_entry.get() else 1
        except ValueError:
            num_guests = 1
        
        # Use controller's show_book_view method to update and show BookView
        self.controller.show_book_view(
            room=room,
            checkin_date=self.checkin_date,
            checkout_date=self.checkout_date,
            num_guests=num_guests
        )
    
    def on_nav_click(self, item):
        """Handle navigation item click"""
        if not self.controller:
            return
        
        nav_map = {
            "Home": "MainAppView",
            "Rooms": "RoomView",
            "My Bookings": "MyBookingsView",
            "Account settings": "AccountView",
            "Sign out": lambda: self.controller.logout()
        }
        
        target = nav_map.get(item)
        if target:
            if callable(target):
                target()
            else:
                self.controller.show_frame(target)


if __name__ == "__main__":
    app = SearchView()
    app.mainloop()
