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

class MainAppView(ctk.CTkFrame):
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        
        # Initialize database manager
        if controller:
            self.db_manager = controller.get_db_manager()
        else:
            self.db_manager = DBManager("db")
        
        self.configure(fg_color="white")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color="white")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=0)  # Sidebar
        self.main_container.grid_columnconfigure(1, weight=5)  # Main content
        
        # Left sidebar - Navigation (will be created in create_sidebar)
        self.sidebar = None
        
        # Right side - Main content
        self.create_main_content()
        
        # Create sidebar initially
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
        
        # Check if user is logged in
        is_logged_in = False
        user_name = "User"
        if self.controller:
            current_user = self.controller.get_current_user()
            if current_user:
                is_logged_in = True
                user_name = current_user.get("name", current_user.get("email", "User"))
        
        if is_logged_in:
            # Greeting label for logged-in users
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
        else:
            # Navigation items for non-logged-in users
            nav_items = [
                "Home",
                "Rooms",
                "Login"
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
        
        # Banner image section
        self.create_banner_section()
        
        # Hotel description section
        self.create_description_section()
        
        # Rooms section
        self.create_rooms_section()
    
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
            command=self.on_search
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
    
    def create_banner_section(self):
        """Create banner image section"""
        banner_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="#E5E5E5",
            height=300,
            corner_radius=10
        )
        banner_frame.pack(fill="x", pady=(0, 20))
        banner_frame.pack_propagate(False)
        
        # Try to load banner image
        try:
            image_path = "assets/images/hotelBanner.jpg"
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize((1200,675))
                photo = ctk.CTkImage(light_image=image, size=(1200, 675))
                banner_label = ctk.CTkLabel(banner_frame, image=photo, text="")
                banner_label.image = photo
                banner_label.pack(fill="both", expand=True)
            else:
                banner_label = ctk.CTkLabel(
                    banner_frame,
                    text="BANNER IMAGE",
                    font=("SVN-Gilroy", 24, "bold"),
                    text_color="gray"
                )
                banner_label.pack(expand=True)
        except Exception as e:
            banner_label = ctk.CTkLabel(
                banner_frame,
                text="BANNER IMAGE",
                font=("SVN-Gilroy", 24, "bold"),
                text_color="gray"
            )
            banner_label.pack(expand=True)
    
    def create_description_section(self):
        """Create hotel description section"""
        desc_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="white"
        )
        desc_frame.pack(fill="x", pady=(0, 20))
        
        # Image and text side by side
        desc_container = ctk.CTkFrame(desc_frame, fg_color="white")
        desc_container.pack(fill="x")
        desc_container.grid_columnconfigure(0, weight=1)
        desc_container.grid_columnconfigure(1, weight=2)
        
        # Left side - Image
        image_frame = ctk.CTkFrame(
            desc_container,
            fg_color="#E5E5E5",
            width=400,
            height=300,
            corner_radius=10
        )
        image_frame.grid(row=0, column=0, padx=0, pady=10, sticky="nsew")
        image_frame.pack_propagate(False)
        
        try:
            image_path = "assets/images/hotel.jpg"
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize((400, 300))
                photo = ctk.CTkImage(light_image=image, size=(400, 300))
                img_label = ctk.CTkLabel(image_frame, image=photo, text="")
                img_label.image = photo
                img_label.pack(fill="both", expand=True)
            else:
                img_label = ctk.CTkLabel(
                    image_frame,
                    text="IMAGE",
                    font=("SVN-Gilroy", 20, "bold"),
                    text_color="gray"
                )
                img_label.pack(expand=True)
        except Exception as e:
            img_label = ctk.CTkLabel(
                image_frame,
                text="IMAGE",
                font=("SVN-Gilroy", 20, "bold"),
                text_color="gray"
            )
            img_label.pack(expand=True)
        
        # Right side - Description text
        text_frame = ctk.CTkFrame(desc_container, fg_color="white")
        text_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        description_text = (
            "A stunning, wide-angle shot of the hotel's exterior (if it's architecturally interesting) or a luxurious lobby/lounge area.\nIt should feel inviting and high-end.Maybe a soft light coming through large windows."
        )
        
        desc_label = ctk.CTkLabel(
            text_frame,
            text=description_text,
            font=("SVN-Gilroy", 20),
            text_color="black",
            justify="left",
            wraplength=300
        )
        desc_label.grid(row=0, column=0, padx=20, pady=20, sticky="ws")
    
    def create_rooms_section(self):
        """Create rooms section"""
        rooms_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="white"
        )
        rooms_frame.pack(fill="x", pady=(0, 20))
        
        # Section title
        title_label = ctk.CTkLabel(
            rooms_frame,
            text="Rooms designed for you",
            font=("SVN-Gilroy", 32, "bold"),
            text_color="black",
            anchor="w"
        )
        title_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        subtitle_label = ctk.CTkLabel(
            rooms_frame,
            text="Choose the rooms that fit your journey",
            font=("SVN-Gilroy", 18),
            text_color="gray",
            anchor="w"
        )
        subtitle_label.pack(anchor="w", padx=20, pady=(0, 20))
        
        # Room cards container - store reference for refreshing
        self.rooms_container = ctk.CTkFrame(rooms_frame, fg_color="white")
        self.rooms_container.pack(fill="x", padx=10, pady=(0, 20))
        # Configure grid for children (room cards will use grid)
        self.rooms_container.grid_columnconfigure(0, weight=1)
        self.rooms_container.grid_columnconfigure(1, weight=1)
        self.rooms_container.grid_columnconfigure(2, weight=1)
        
        # Load and display room types from database
        self.load_room_type_cards()
    
    def load_room_type_cards(self):
        """Load room types from database and display them as cards"""
        # Clear existing cards
        for widget in self.rooms_container.winfo_children():
            widget.destroy()
        
        # Get room types from database
        if self.db_manager:
            room_types = self.db_manager.get_all_room_types()
        else:
            room_types = []
        
        # Limit to 3 room types for display
        room_types = room_types[:3]
        
        # Create room cards
        for i, room_type in enumerate(room_types):
            room_card = ctk.CTkFrame(
                self.rooms_container,
                fg_color="#E5E5E5",
                width=250,
                height=250,
                corner_radius=10
            )
            room_card.grid(row=0, column=i, padx=10, pady=(20,0), sticky="n")
            room_card.pack_propagate(False)
            
            try:
                image_path = room_type.get("imagePath", "")
                if image_path and os.path.exists(image_path) and image_path != "hi chua co tai anh ve":
                    image = Image.open(image_path)
                    image = image.resize((250, 250))
                    photo = ctk.CTkImage(light_image=image, size=(250, 250))
                    room_img = ctk.CTkLabel(room_card, image=photo, text="")
                    room_img.image = photo
                    room_img.pack(pady=0)
                else:
                    room_img = ctk.CTkLabel(
                        room_card,
                        text="IMAGE",
                        font=("SVN-Gilroy", 16, "bold"),
                        text_color="gray",
                        width=250,
                        height=250
                    )
                    room_img.pack(pady=0)
            except Exception as e:
                room_img = ctk.CTkLabel(
                    room_card,
                    text="IMAGE",
                    font=("SVN-Gilroy", 16, "bold"),
                    text_color="gray",
                    width=250,
                    height=250
                )
                room_img.pack(pady=0)
        
        # Fill remaining slots if less than 3 room types
        for i in range(len(room_types), 3):
            room_card = ctk.CTkFrame(
                self.rooms_container,
                fg_color="#E5E5E5",
                width=250,
                height=250,
                corner_radius=10
            )
            room_card.grid(row=0, column=i, padx=10, pady=(20,0), sticky="n")
            room_card.pack_propagate(False)
            
            placeholder = ctk.CTkLabel(
                room_card,
                text="IMAGE",
                font=("SVN-Gilroy", 16, "bold"),
                text_color="gray",
                width=250,
                height=250
            )
            placeholder.pack(pady=0)
    
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
    
    def on_search(self):
        """Handle search button click"""
        # Check if user is logged in
        if not self.controller:
            return
        
        current_user = self.controller.get_current_user()
        if not current_user:
            # User not logged in - redirect to login page
            self.controller.show_frame("SignInView")
            return
        
        # Validate dates before searching
        if not self.validate_dates():
            return
        
        checkin = self.checkin_entry.get().strip()
        checkout = self.checkout_entry.get().strip()
        guests = self.guests_entry.get().strip()
        
        # Additional validation
        if not checkin or not checkout:
            self.date_error_label.configure(text="Please fill in both check-in and check-out dates")
            return
        
        if not guests or not guests.isdigit() or int(guests) < 1:
            self.date_error_label.configure(text="Please enter a valid number of guests (at least 1)")
            return
        
        # All validations passed - navigate to SearchView with search parameters
        if self.controller:
            self.controller.show_search_view(checkin=checkin, checkout=checkout, guests=guests)
    
    def on_nav_click(self, item):
        """Handle navigation item click"""
        if not self.controller:
            return
        
        # Check if user is logged in
        current_user = self.controller.get_current_user()
        is_logged_in = current_user is not None
        
        if is_logged_in:
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
        else:
            nav_map = {
                "Home": "MainAppView",
                "Rooms": "RoomView",
                "Login": "SignInView"
            }
        
        target = nav_map.get(item)
        if target:
            self.controller.show_frame(target)
    
    def on_show(self):
        """Called when this view is shown - refresh sidebar to reflect login status"""
        self.create_sidebar()
        # Refresh room type cards to show updated images
        if hasattr(self, 'rooms_container'):
            self.load_room_type_cards()


if __name__ == "__main__":
    app = MainAppView()
    app.mainloop()

