import customtkinter as ctk
from PIL import Image
import os
from datetime import datetime, date
import re
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.booking_service import BookingService
from modules.db_manager import DBManager

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class AdminBookingView(ctk.CTkFrame):
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        # Initialize services
        if controller:
            self.db_manager = controller.get_db_manager()
            self.booking_service = controller.get_booking_service()
        else:
            self.db_manager = DBManager("db")
            self.booking_service = BookingService(self.db_manager)

        self.configure(fg_color="white")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color="white")
        self.main_container.grid(row=0, column=0, sticky="nsew")
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
            "Bookings",
            "Rooms",
            "Users",
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
        """Create main content area with tabview"""
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="white"
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=(20, 0))
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Booking Management",
            font=("SVN-Gilroy", 24, "bold"),
            text_color="black"
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # TabView
        self.tabview = ctk.CTkTabview(
            self.content_frame,
            fg_color="white",
            segmented_button_fg_color="#E5E5E5",
            segmented_button_selected_color="#3A7BFF",
            segmented_button_unselected_color="#A9A9A9"
        )
        self.tabview.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(1, weight=1)

        # Create tabs
        self.tabs = {}
        tab_names = ["Pending", "Confirmed", "In stay", "Completed", "Cancelled"]
        
        for tab_name in tab_names:
            tab = self.tabview.add(tab_name)
            self.tabs[tab_name] = tab
            
            # Create scrollable frame for cards
            scrollable_frame = ctk.CTkScrollableFrame(tab, fg_color="#F5F5F5")
            scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Store reference to scrollable frame
            setattr(self, f"scrollable_frame_{tab_name.replace(' ', '_')}", scrollable_frame)

        # Load initial data
        self.load_bookings_data()
        
        # Auto-complete checkouts on load
        self.booking_service.auto_complete_checkouts()
        self.load_bookings_data()

    def load_bookings_data(self):
        """Load and display bookings in each tab"""
        # Load bookings for each tab
        for tab_name in ["Pending", "Confirmed", "In stay", "Completed", "Cancelled"]:
            self.load_tab_bookings(tab_name)

    def load_tab_bookings(self, tab_name):
        """Load bookings for a specific tab"""
        # Get scrollable frame for this tab
        frame_attr = f"scrollable_frame_{tab_name.replace(' ', '_')}"
        scrollable_frame = getattr(self, frame_attr, None)
        
        if not scrollable_frame:
            return

        # Clear existing widgets
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        # Get bookings filtered by status
        bookings = self.booking_service.get_bookings_by_status(tab_name)

        if not bookings:
            # Show empty message
            empty_label = ctk.CTkLabel(
                scrollable_frame,
                text="No bookings",
                font=("SVN-Gilroy", 14),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return

        # Create booking cards
        for booking in bookings:
            self.create_booking_card(scrollable_frame, booking, tab_name)

    def create_booking_card(self, parent, booking, tab_name):
        """Create a booking card widget styled like my_bookings_view"""
        card = ctk.CTkFrame(parent, fg_color="white", border_color="#E5E5E5", border_width=2, corner_radius=15)
        card.pack(fill="x", pady=10, padx=10)

        # Title - BookingID
        title = ctk.CTkLabel(
            card,
            text=f"Booking ID: {booking.get('bookingID', '')}",
            font=("SVN-Gilroy", 16, "bold"),
            text_color="black",
            anchor="w"
        )
        title.pack(anchor="w", pady=(10, 5), padx=20)

        # Get booking information
        guest_name = booking.get("guestName", "")
        guest_email = booking.get("guestEmail", "")
        guest_national_id = booking.get("guestNationalID", "")
        total_amount = booking.get("totalAmount", 0)
        status = booking.get("status", "")
        
        # Format check-in and check-out dates
        check_in_date_str = booking.get("checkInDate", "")
        check_out_date_str = booking.get("checkOutDate", "")
        
        def format_date(date_str):
            """Format date string to readable format"""
            if not date_str:
                return "N/A"
            try:
                # Handle ISO format with time
                if "T" in date_str:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    return dt.strftime("%d/%m/%Y")
                # Handle date-only format
                else:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    return dt.strftime("%d/%m/%Y")
            except Exception:
                return date_str
        
        check_in_formatted = format_date(check_in_date_str)
        check_out_formatted = format_date(check_out_date_str)
        
        # Normalize status display
        status_map = {
            "Canceled": "Cancelled",
            "In Stay": "In stay"
        }
        status_display = status_map.get(status, status)

        # Summary items - only show required fields
        summary_items = [
            ("Guest Name", guest_name),
            ("Email", guest_email),
            ("National ID", guest_national_id),
            ("Check-in Date", check_in_formatted),
            ("Check-out Date", check_out_formatted),
            ("Status", status_display),
            ("Total Amount", f"{total_amount:,} VND")
        ]

        for label_text, value_text in summary_items:
            item_frame = ctk.CTkFrame(card, fg_color="white")
            item_frame.pack(fill="x", pady=2, padx=20)
            label = ctk.CTkLabel(
                item_frame,
                text=label_text,
                font=("SVN-Gilroy", 13),
                text_color="black",
                anchor="w"
            )
            label.pack(side="left", anchor="w")
            value = ctk.CTkLabel(
                item_frame,
                text=value_text,
                font=("SVN-Gilroy", 13) if label_text == "Total Amount" else ("SVN-Gilroy", 12),
                text_color="black" if label_text in ["Total Amount", "Status"] else "gray",
                anchor="e"
            )
            value.pack(side="right", anchor="e", fill="x", expand=True, padx=(20, 0))

        # Action buttons based on tab - only create btn_frame if needed
        booking_id = booking.get("bookingID")

        if tab_name == "Pending":
            btn_frame = ctk.CTkFrame(card, fg_color="white")
            btn_frame.pack(fill="x", pady=(10, 15), padx=20)
            
            confirm_btn = ctk.CTkButton(
                btn_frame,
                text="Confirm",
                font=("SVN-Gilroy", 14),
                fg_color="#28A745",
                text_color="white",
                hover_color="#218838",
                corner_radius=10,
                width=100,
                command=lambda bid=booking_id: self.confirm_booking(bid)
            )
            confirm_btn.pack(side="left", padx=(0, 10))

            cancel_btn = ctk.CTkButton(
                btn_frame,
                text="Cancel",
                font=("SVN-Gilroy", 14),
                fg_color="#DC3545",
                text_color="white",
                hover_color="#C82333",
                corner_radius=10,
                width=100,
                command=lambda bid=booking_id: self.cancel_booking(bid)
            )
            cancel_btn.pack(side="left")

        elif tab_name == "Confirmed":
            btn_frame = ctk.CTkFrame(card, fg_color="white")
            btn_frame.pack(fill="x", pady=(10, 15), padx=20)
            
            check_in_btn = ctk.CTkButton(
                btn_frame,
                text="Confirm",
                font=("SVN-Gilroy", 14),
                fg_color="#28A745",
                text_color="white",
                hover_color="#218838",
                corner_radius=10,
                width=100,
                command=lambda bid=booking_id: self.check_in_booking(bid)
            )
            check_in_btn.pack(side="left", padx=(0, 10))

            cancel_btn = ctk.CTkButton(
                btn_frame,
                text="Cancel",
                font=("SVN-Gilroy", 14),
                fg_color="#DC3545",
                text_color="white",
                hover_color="#C82333",
                corner_radius=10,
                width=100,
                command=lambda bid=booking_id: self.cancel_booking(bid)
            )
            cancel_btn.pack(side="left")

        elif tab_name == "In stay":
            btn_frame = ctk.CTkFrame(card, fg_color="white")
            btn_frame.pack(fill="x", pady=(10, 15), padx=20)
            
            # Auto-complete is handled automatically
            info_label = ctk.CTkLabel(
                btn_frame,
                text="Auto-complete on checkout date",
                font=("SVN-Gilroy", 12),
                text_color="gray"
            )
            info_label.pack(anchor="w", pady=(0, 10))
            
            cancel_btn = ctk.CTkButton(
                btn_frame,
                text="Cancel",
                font=("SVN-Gilroy", 14),
                fg_color="#DC3545",
                text_color="white",
                hover_color="#C82333",
                corner_radius=10,
                width=100,
                command=lambda bid=booking_id: self.cancel_booking(bid)
            )
            cancel_btn.pack(side="left")

        # For Completed and Cancelled tabs, no buttons needed - no extra space

    def confirm_booking(self, booking_id):
        """Confirm a pending booking"""
        success = self.booking_service.confirm_booking(booking_id)
        if success:
            self.load_bookings_data()

    def check_in_booking(self, booking_id):
        """Check in a confirmed booking"""
        success = self.booking_service.check_in_booking(booking_id)
        if success:
            self.load_bookings_data()

    def cancel_booking(self, booking_id):
        """Cancel a booking"""
        success = self.booking_service.cancel_booking_admin(booking_id)
        if success:
            self.load_bookings_data()
    
    def on_nav_click(self, item):
        """Handle navigation item click"""
        if not self.controller:
            return
        
        # Handle Sign out
        if item == "Sign out":
            self.controller.logout()
            return
        
        nav_map = {
            "Bookings": "AdminBookingView",
            "Rooms": "AdminRoomView",
            "Users": "AdminUserView"
        }
        
        target = nav_map.get(item)
        if target:
            self.controller.show_frame(target)

    def on_show(self):
        """Called when this view is shown - reload data and auto-complete checkouts"""
        # Auto-complete checkouts
        self.booking_service.auto_complete_checkouts()
        # Reload bookings
        self.load_bookings_data()
