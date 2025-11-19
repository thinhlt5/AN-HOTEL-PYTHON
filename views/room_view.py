import customtkinter as ctk
from customtkinter import FontManager
from PIL import Image
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

class RoomView(ctk.CTkFrame):
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.db = DBManager(data_folder="db")
        self.configure(fg_color="white")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.main_container = ctk.CTkFrame(self, fg_color="white")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=0)
        self.main_container.grid_columnconfigure(1, weight=5)
        self.sidebar = None  # Initialize sidebar variable
        self.create_main_content()
        self.create_sidebar()  # Create sidebar after main content
    
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
        """Create main content area with room list"""
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="white"
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="white"
        )
        self.scrollable_frame.pack(fill="both", expand=True)
        
        # Load and display room types
        self.load_and_display_rooms()
    
    def load_and_display_rooms(self):
        """Load room types from database and display them"""
        room_types = self.db.get_all_room_types()
        
        for room_type in room_types:
            self.create_room_card(room_type)
    
    def create_room_card(self, room_type):
        """Create a room card for each room type"""
        # Main card frame
        room_card = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="white",
            corner_radius=10
        )
        room_card.pack(fill="x", padx=10, pady=15)
        room_card.grid_columnconfigure(0, weight=0)  # Image column
        room_card.grid_columnconfigure(1, weight=1)  # Content column
        
        # Left side - Image
        image_frame = ctk.CTkFrame(
            room_card,
            fg_color="#E5E5E5",
            width=300,
            height=200,
            corner_radius=10
        )
        image_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        image_frame.pack_propagate(False)
        
        # Try to load image
        try:
            image_path = room_type.get("imagePath", "")
            if image_path and os.path.exists(image_path) and image_path != "hi chua co tai anh ve":
                image = Image.open(image_path)
                # Center crop to maintain aspect ratio
                image = self.center_crop_image(image, 300, 200)
                photo = ctk.CTkImage(light_image=image, size=(300, 200))
                img_label = ctk.CTkLabel(image_frame, image=photo, text="")
                img_label.image = photo
                img_label.pack(fill="both", expand=True)
            else:
                # Default placeholder
                img_label = ctk.CTkLabel(
                    image_frame,
                    text="IMAGE",
                    font=("SVN-Gilroy", 16, "bold"),
                    text_color="gray"
                )
                img_label.pack(expand=True)
        except Exception as e:
            img_label = ctk.CTkLabel(
                image_frame,
                text="IMAGE",
                font=("SVN-Gilroy", 16, "bold"),
                text_color="gray"
            )
            img_label.pack(expand=True)
        
        # Right side - Content
        content_frame = ctk.CTkFrame(room_card, fg_color="white")
        content_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Room title
        room_name = room_type.get("typeName", "Room") + " Room"
        title_label = ctk.CTkLabel(
            content_frame,
            text=room_name,
            font=("SVN-Gilroy", 28, "bold"),
            text_color="black",
            anchor="w"
        )
        title_label.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="w")
        
        # Description
        description = room_type.get("description", "No description available.")
        desc_label = ctk.CTkLabel(
            content_frame,
            text=description,
            font=("SVN-Gilroy", 14),
            text_color="black",
            anchor="w",
            justify="left",
            wraplength=500
        )
        desc_label.grid(row=1, column=0, padx=0, pady=(0, 10), sticky="w")
        
        # Services (placeholder for now)
        services_label = ctk.CTkLabel(
            content_frame,
            text="Services:",
            font=("SVN-Gilroy", 14, "bold"),
            text_color="black",
            anchor="w"
        )
        services_label.grid(row=2, column=0, padx=0, pady=(0, 5), sticky="w")
        
        services_text = "WiFi, Air Conditioning, TV, Mini Bar"
        services_value = ctk.CTkLabel(
            content_frame,
            text=services_text,
            font=("SVN-Gilroy", 14),
            text_color="gray",
            anchor="w"
        )
        services_value.grid(row=3, column=0, padx=0, pady=(0, 10), sticky="w")
        
        # Price
        price_label = ctk.CTkLabel(
            content_frame,
            text="Price:",
            font=("SVN-Gilroy", 14, "bold"),
            text_color="black",
            anchor="w"
        )
        price_label.grid(row=4, column=0, padx=0, pady=(0, 5), sticky="w")
        
        price = room_type.get("price", 0)
        formatted_price = f"{price:,} VND" if price > 0 else "Contact for price"
        price_value = ctk.CTkLabel(
            content_frame,
            text=formatted_price,
            font=("SVN-Gilroy", 16, "bold"),
            text_color="#8B4513",
            anchor="w"
        )
        price_value.grid(row=5, column=0, padx=0, pady=(0, 15), sticky="w")
        
        
        # The "BOOK NOW" button has been removed.
        pass
    
    
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
    
    def center_crop_image(self, image, target_width, target_height):
        """
        Center crop image to target size while maintaining aspect ratio
        
        Args:
            image: PIL Image object
            target_width: Target width
            target_height: Target height
            
        Returns:
            Cropped PIL Image
        """
        img_width, img_height = image.size
        target_ratio = target_width / target_height
        img_ratio = img_width / img_height
        
        # Calculate crop size
        if img_ratio > target_ratio:
            # Image is wider, crop width
            new_height = img_height
            new_width = int(img_height * target_ratio)
        else:
            # Image is taller, crop height
            new_width = img_width
            new_height = int(img_width / target_ratio)
        
        # Calculate crop box (center crop)
        left = (img_width - new_width) // 2
        top = (img_height - new_height) // 2
        right = left + new_width
        bottom = top + new_height
        
        # Crop and resize
        cropped = image.crop((left, top, right, bottom))
        return cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    def on_show(self):
        """Called when this view is shown - refresh sidebar to reflect login status"""
        self.create_sidebar()
        # Refresh room cards to show updated images
        # Clear existing cards and reload
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.load_and_display_rooms()


if __name__ == "__main__":
    app = RoomView()
    app.mainloop()

