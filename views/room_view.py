import customtkinter as ctk
from PIL import Image
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.db_manager import DBManager

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class RoomView(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set window properties
        self.title("AN Hotel - Rooms")
        self.geometry("1000x750")
        self.resizable(False, False)
        
        # Initialize DB Manager
        self.db = DBManager(data_folder="db")
        
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
                image = image.resize((300, 200))
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
        print(f"Navigation clicked: {item}")
        # TODO: Implement navigation functionality


if __name__ == "__main__":
    app = RoomView()
    app.mainloop()

