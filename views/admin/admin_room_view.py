import customtkinter as ctk
from customtkinter import FontManager
from PIL import Image
import os
import sys
from tkinter import filedialog, messagebox

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.room_service import RoomService
from modules.db_manager import DBManager

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Load fonts from assets/font
current_dir = os.path.dirname(os.path.abspath(__file__))
assets_font_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "assets", "font")

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


class AdminRoomView(ctk.CTkFrame):
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        # Initialize services
        if controller:
            self.db_manager = controller.get_db_manager()
            self.room_service = controller.get_room_service() if hasattr(controller, 'get_room_service') else RoomService(self.db_manager)
        else:
            self.db_manager = DBManager("db")
            self.room_service = RoomService(self.db_manager)

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
            text="Room Management",
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
        tab_names = ["Room", "Room Type", "Room Status"]
        
        for tab_name in tab_names:
            tab = self.tabview.add(tab_name)
            self.tabs[tab_name] = tab
            
            # Create scrollable frame for cards
            scrollable_frame = ctk.CTkScrollableFrame(tab, fg_color="#F5F5F5")
            scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Store reference to scrollable frame
            setattr(self, f"scrollable_frame_{tab_name.replace(' ', '_')}", scrollable_frame)

        # Load initial data
        self.load_data()

    def load_data(self):
        """Load and display data in each tab"""
        self.load_room_tab()
        self.load_room_type_tab()
        self.load_room_status_tab()

    # Room Tab
    def load_room_tab(self):
        """Load rooms in Room tab"""
        scrollable_frame = getattr(self, "scrollable_frame_Room", None)
        if not scrollable_frame:
            return

        # Clear existing widgets
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        # Add button
        add_btn_frame = ctk.CTkFrame(scrollable_frame, fg_color="#F5F5F5")
        add_btn_frame.pack(fill="x", pady=(0, 10))
        
        add_btn = ctk.CTkButton(
            add_btn_frame,
            text="+ Add Room",
            font=("SVN-Gilroy", 14),
            fg_color="#28A745",
            hover_color="#218838",
            command=self.show_add_room_dialog
        )
        add_btn.pack(side="left")

        # Get rooms
        rooms = self.room_service.get_all_rooms()

        if not rooms:
            empty_label = ctk.CTkLabel(
                scrollable_frame,
                text="No rooms",
                font=("SVN-Gilroy", 14),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return

        # Create room cards
        for room in rooms:
            self.create_room_card(scrollable_frame, room)

    def create_room_card(self, parent, room):
        """Create a room card"""
        card = ctk.CTkFrame(parent, fg_color="white", border_color="#E5E5E5", border_width=2, corner_radius=15)
        card.pack(fill="x", pady=10, padx=10)

        # Title - Room Number
        title = ctk.CTkLabel(
            card,
            text=f"Room: {room.get('roomNumber', '')}",
            font=("SVN-Gilroy", 16, "bold"),
            text_color="black",
            anchor="w"
        )
        title.pack(anchor="w", pady=(10, 5), padx=20)

        # Room information
        room_type_name = room.get("typeName", "Unknown")
        status = room.get("Status", "")

        summary_items = [
            ("Room Type", room_type_name),
            ("Status", status)
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
                font=("SVN-Gilroy", 12),
                text_color="black" if label_text == "Status" else "gray",
                anchor="e"
            )
            value.pack(side="right", anchor="e", fill="x", expand=True, padx=(20, 0))

        # Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="white")
        btn_frame.pack(fill="x", pady=(10, 15), padx=20)

        edit_btn = ctk.CTkButton(
            btn_frame,
            text="Edit",
            font=("SVN-Gilroy", 14),
            fg_color="#3A7BFF",
            text_color="white",
            hover_color="#2A5BCC",
            corner_radius=10,
            width=100,
            command=lambda r=room: self.show_edit_room_dialog(r)
        )
        edit_btn.pack(side="left", padx=(0, 10))

        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            font=("SVN-Gilroy", 14),
            fg_color="#DC3545",
            text_color="white",
            hover_color="#C82333",
            corner_radius=10,
            width=100,
            command=lambda r=room: self.delete_room(r)
        )
        delete_btn.pack(side="left")

    def show_add_room_dialog(self):
        """Show dialog to add new room"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Room")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        # Room number
        ctk.CTkLabel(dialog, text="Room Number:", font=("SVN-Gilroy", 12)).pack(pady=(20, 5), padx=20, anchor="w")
        room_number_entry = ctk.CTkEntry(dialog, font=("SVN-Gilroy", 12), width=300)
        room_number_entry.pack(padx=20, pady=(0, 10))

        # Room type
        ctk.CTkLabel(dialog, text="Room Type:", font=("SVN-Gilroy", 12)).pack(pady=(10, 5), padx=20, anchor="w")
        room_types = self.room_service.get_all_room_types()
        type_names = [rt.get("typeName", "") for rt in room_types]
        type_dropdown = ctk.CTkComboBox(dialog, values=type_names, font=("SVN-Gilroy", 12), width=300)
        type_dropdown.pack(padx=20, pady=(0, 20))
        if type_names:
            type_dropdown.set(type_names[0])

        def add_room():
            room_number = room_number_entry.get().strip()
            selected_type = type_dropdown.get()
            
            if not room_number:
                messagebox.showerror("Error", "Room number is required")
                return
            
            # Find type ID
            type_id = None
            for rt in room_types:
                if rt.get("typeName") == selected_type:
                    type_id = rt.get("typeID")
                    break
            
            if not type_id:
                messagebox.showerror("Error", "Invalid room type")
                return
            
            result = self.room_service.create_room(room_number, type_id)
            if result:
                self.load_room_tab()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Room number already exists")

        ctk.CTkButton(dialog, text="Add", command=add_room, width=100).pack(pady=10)

    def show_edit_room_dialog(self, room):
        """Show dialog to edit room"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Room")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        # Room number
        ctk.CTkLabel(dialog, text="Room Number:", font=("SVN-Gilroy", 12)).pack(pady=(20, 5), padx=20, anchor="w")
        room_number_entry = ctk.CTkEntry(dialog, font=("SVN-Gilroy", 12), width=300)
        room_number_entry.insert(0, room.get("roomNumber", ""))
        room_number_entry.pack(padx=20, pady=(0, 10))

        # Room type
        ctk.CTkLabel(dialog, text="Room Type:", font=("SVN-Gilroy", 12)).pack(pady=(10, 5), padx=20, anchor="w")
        room_types = self.room_service.get_all_room_types()
        type_names = [rt.get("typeName", "") for rt in room_types]
        type_dropdown = ctk.CTkComboBox(dialog, values=type_names, font=("SVN-Gilroy", 12), width=300)
        type_dropdown.pack(padx=20, pady=(0, 20))
        
        # Set current type
        current_type_id = room.get("typeID")
        for rt in room_types:
            if rt.get("typeID") == current_type_id:
                type_dropdown.set(rt.get("typeName", ""))
                break

        def update_room():
            room_number = room_number_entry.get().strip()
            selected_type = type_dropdown.get()
            
            if not room_number:
                messagebox.showerror("Error", "Room number is required")
                return
            
            # Find type ID
            type_id = None
            for rt in room_types:
                if rt.get("typeName") == selected_type:
                    type_id = rt.get("typeID")
                    break
            
            if not type_id:
                messagebox.showerror("Error", "Invalid room type")
                return
            
            success = self.room_service.update_room(room.get("roomId"), room_number=room_number, type_id=type_id)
            if success:
                self.load_room_tab()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Room number already exists")

        ctk.CTkButton(dialog, text="Update", command=update_room, width=100).pack(pady=10)

    def delete_room(self, room):
        """Delete a room"""
        if messagebox.askyesno("Confirm", f"Delete room {room.get('roomNumber')}?"):
            success = self.room_service.delete_room(room.get("roomId"))
            if success:
                self.load_room_tab()
            else:
                messagebox.showerror("Error", "Cannot delete room (room is booked or not found)")

    # Room Type Tab
    def load_room_type_tab(self):
        """Load room types in Room Type tab"""
        scrollable_frame = getattr(self, "scrollable_frame_Room_Type", None)
        if not scrollable_frame:
            return

        # Clear existing widgets
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        # Add button
        add_btn_frame = ctk.CTkFrame(scrollable_frame, fg_color="#F5F5F5")
        add_btn_frame.pack(fill="x", pady=(0, 10))
        
        add_btn = ctk.CTkButton(
            add_btn_frame,
            text="+ Add Room Type",
            font=("SVN-Gilroy", 14),
            fg_color="#28A745",
            hover_color="#218838",
            command=self.show_add_room_type_dialog
        )
        add_btn.pack(side="left")

        # Get room types
        room_types = self.room_service.get_all_room_types()

        if not room_types:
            empty_label = ctk.CTkLabel(
                scrollable_frame,
                text="No room types",
                font=("SVN-Gilroy", 14),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return

        # Create room type cards
        for room_type in room_types:
            self.create_room_type_card(scrollable_frame, room_type)

    def create_room_type_card(self, parent, room_type):
        """Create a room type card"""
        card = ctk.CTkFrame(parent, fg_color="white", border_color="#E5E5E5", border_width=2, corner_radius=15)
        card.pack(fill="x", pady=10, padx=10)

        # Title - Type Name
        title = ctk.CTkLabel(
            card,
            text=f"Type: {room_type.get('typeName', '')}",
            font=("SVN-Gilroy", 16, "bold"),
            text_color="black",
            anchor="w"
        )
        title.pack(anchor="w", pady=(10, 5), padx=20)

        # Room type information
        description = room_type.get("description", "")
        price = room_type.get("price", 0)
        image_path = room_type.get("imagePath", "")

        summary_items = [
            ("Description", description),
            ("Price", f"{price:,} VND"),
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
                font=("SVN-Gilroy", 12),
                text_color="black" if label_text == "Price" else "gray",
                anchor="e"
            )
            value.pack(side="right", anchor="e", fill="x", expand=True, padx=(20, 0))

        # Image preview if exists
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img = img.resize((200, 150))
                photo = ctk.CTkImage(light_image=img, size=(200, 150))
                img_label = ctk.CTkLabel(card, image=photo, text="")
                img_label.pack(pady=10, padx=20)
            except:
                pass

        # Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="white")
        btn_frame.pack(fill="x", pady=(10, 15), padx=20)

        edit_btn = ctk.CTkButton(
            btn_frame,
            text="Edit",
            font=("SVN-Gilroy", 14),
            fg_color="#3A7BFF",
            text_color="white",
            hover_color="#2A5BCC",
            corner_radius=10,
            width=100,
            command=lambda rt=room_type: self.show_edit_room_type_dialog(rt)
        )
        edit_btn.pack(side="left", padx=(0, 10))

        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            font=("SVN-Gilroy", 14),
            fg_color="#DC3545",
            text_color="white",
            hover_color="#C82333",
            corner_radius=10,
            width=100,
            command=lambda rt=room_type: self.delete_room_type(rt)
        )
        delete_btn.pack(side="left")

    def show_add_room_type_dialog(self):
        """Show dialog to add new room type"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Room Type")
        dialog.geometry("500x500")
        dialog.transient(self)
        dialog.grab_set()

        # Type name
        ctk.CTkLabel(dialog, text="Type Name:", font=("SVN-Gilroy", 12)).pack(pady=(20, 5), padx=20, anchor="w")
        type_name_entry = ctk.CTkEntry(dialog, font=("SVN-Gilroy", 12), width=400)
        type_name_entry.pack(padx=20, pady=(0, 10))

        # Description
        ctk.CTkLabel(dialog, text="Description:", font=("SVN-Gilroy", 12)).pack(pady=(10, 5), padx=20, anchor="w")
        description_entry = ctk.CTkEntry(dialog, font=("SVN-Gilroy", 12), width=400)
        description_entry.pack(padx=20, pady=(0, 10))

        # Price
        ctk.CTkLabel(dialog, text="Price:", font=("SVN-Gilroy", 12)).pack(pady=(10, 5), padx=20, anchor="w")
        price_entry = ctk.CTkEntry(dialog, font=("SVN-Gilroy", 12), width=400)
        price_entry.pack(padx=20, pady=(0, 10))

        # Image
        image_path_var = ctk.StringVar(value="")
        ctk.CTkLabel(dialog, text="Image:", font=("SVN-Gilroy", 12)).pack(pady=(10, 5), padx=20, anchor="w")
        image_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        image_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        image_path_label = ctk.CTkLabel(image_frame, text="No image selected", font=("SVN-Gilroy", 11), text_color="gray")
        image_path_label.pack(side="left", padx=(0, 10))

        def select_image():
            filename = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if filename:
                image_path_var.set(filename)
                image_path_label.configure(text=os.path.basename(filename))

        ctk.CTkButton(image_frame, text="Browse", command=select_image, width=100).pack(side="left")

        def add_room_type():
            type_name = type_name_entry.get().strip()
            description = description_entry.get().strip()
            price_str = price_entry.get().strip()
            image_path = image_path_var.get()

            if not type_name or not description or not price_str:
                messagebox.showerror("Error", "All fields are required")
                return

            try:
                price = int(price_str)
            except ValueError:
                messagebox.showerror("Error", "Price must be a number")
                return

            result = self.room_service.create_room_type(type_name, description, price, image_path)
            if result:
                self.load_room_type_tab()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Type name already exists")

        ctk.CTkButton(dialog, text="Add", command=add_room_type, width=100).pack(pady=10)

    def show_edit_room_type_dialog(self, room_type):
        """Show dialog to edit room type"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Room Type")
        dialog.geometry("500x500")
        dialog.transient(self)
        dialog.grab_set()

        # Type name
        ctk.CTkLabel(dialog, text="Type Name:", font=("SVN-Gilroy", 12)).pack(pady=(20, 5), padx=20, anchor="w")
        type_name_entry = ctk.CTkEntry(dialog, font=("SVN-Gilroy", 12), width=400)
        type_name_entry.insert(0, room_type.get("typeName", ""))
        type_name_entry.pack(padx=20, pady=(0, 10))

        # Description
        ctk.CTkLabel(dialog, text="Description:", font=("SVN-Gilroy", 12)).pack(pady=(10, 5), padx=20, anchor="w")
        description_entry = ctk.CTkEntry(dialog, font=("SVN-Gilroy", 12), width=400)
        description_entry.insert(0, room_type.get("description", ""))
        description_entry.pack(padx=20, pady=(0, 10))

        # Price
        ctk.CTkLabel(dialog, text="Price:", font=("SVN-Gilroy", 12)).pack(pady=(10, 5), padx=20, anchor="w")
        price_entry = ctk.CTkEntry(dialog, font=("SVN-Gilroy", 12), width=400)
        price_entry.insert(0, str(room_type.get("price", 0)))
        price_entry.pack(padx=20, pady=(0, 10))

        # Image
        image_path_var = ctk.StringVar(value=room_type.get("imagePath", ""))
        ctk.CTkLabel(dialog, text="Image:", font=("SVN-Gilroy", 12)).pack(pady=(10, 5), padx=20, anchor="w")
        image_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        image_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        current_image = room_type.get("imagePath", "")
        image_path_label = ctk.CTkLabel(
            image_frame,
            text=os.path.basename(current_image) if current_image else "No image selected",
            font=("SVN-Gilroy", 11),
            text_color="gray"
        )
        image_path_label.pack(side="left", padx=(0, 10))

        def select_image():
            filename = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if filename:
                image_path_var.set(filename)
                image_path_label.configure(text=os.path.basename(filename))

        ctk.CTkButton(image_frame, text="Browse", command=select_image, width=100).pack(side="left")

        def update_room_type():
            type_name = type_name_entry.get().strip()
            description = description_entry.get().strip()
            price_str = price_entry.get().strip()
            image_path = image_path_var.get() if image_path_var.get() != current_image else None

            if not type_name or not description or not price_str:
                messagebox.showerror("Error", "All fields are required")
                return

            try:
                price = int(price_str)
            except ValueError:
                messagebox.showerror("Error", "Price must be a number")
                return

            success = self.room_service.update_room_type(
                room_type.get("typeID"),
                type_name=type_name,
                description=description,
                price=price,
                image_path=image_path if image_path and image_path != current_image else None
            )
            if success:
                self.load_room_type_tab()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Type name already exists")

        ctk.CTkButton(dialog, text="Update", command=update_room_type, width=100).pack(pady=10)

    def delete_room_type(self, room_type):
        """Delete a room type"""
        if messagebox.askyesno("Confirm", f"Delete room type {room_type.get('typeName')}?"):
            success = self.room_service.delete_room_type(room_type.get("typeID"))
            if success:
                self.load_room_type_tab()
            else:
                messagebox.showerror("Error", "Cannot delete room type (type is in use or not found)")

    # Room Status Tab
    def load_room_status_tab(self):
        """Load rooms in Room Status tab"""
        scrollable_frame = getattr(self, "scrollable_frame_Room_Status", None)
        if not scrollable_frame:
            return

        # Clear existing widgets
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        # Get rooms
        rooms = self.room_service.get_rooms_for_status_management()

        if not rooms:
            empty_label = ctk.CTkLabel(
                scrollable_frame,
                text="No rooms",
                font=("SVN-Gilroy", 14),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return

        # Create room cards
        for room in rooms:
            self.create_room_status_card(scrollable_frame, room)

    def create_room_status_card(self, parent, room):
        """Create a room status card"""
        card = ctk.CTkFrame(parent, fg_color="white", border_color="#E5E5E5", border_width=2, corner_radius=15)
        card.pack(fill="x", pady=10, padx=10)

        # Title - Room Number
        title = ctk.CTkLabel(
            card,
            text=f"Room: {room.get('roomNumber', '')}",
            font=("SVN-Gilroy", 16, "bold"),
            text_color="black",
            anchor="w"
        )
        title.pack(anchor="w", pady=(10, 5), padx=20)

        # Room information
        room_type_name = room.get("typeName", "Unknown")
        status = room.get("Status", "")

        summary_items = [
            ("Room Type", room_type_name),
            ("Status", status)
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
                font=("SVN-Gilroy", 12),
                text_color="black" if label_text == "Status" else "gray",
                anchor="e"
            )
            value.pack(side="right", anchor="e", fill="x", expand=True, padx=(20, 0))

        # Status update buttons (only for Available rooms)
        status = room.get("Status", "")
        if status == "Available":
            btn_frame = ctk.CTkFrame(card, fg_color="white")
            btn_frame.pack(fill="x", pady=(10, 15), padx=20)

            cleaning_btn = ctk.CTkButton(
                btn_frame,
                text="Set Cleaning",
                font=("SVN-Gilroy", 14),
                fg_color="#FFC107",
                text_color="white",
                hover_color="#E0A800",
                corner_radius=10,
                width=120,
                command=lambda r=room: self.update_room_status(r, "Cleaning")
            )
            cleaning_btn.pack(side="left", padx=(0, 10))

            maintenance_btn = ctk.CTkButton(
                btn_frame,
                text="Set Maintenance",
                font=("SVN-Gilroy", 14),
                fg_color="#FF9800",
                text_color="white",
                hover_color="#E68900",
                corner_radius=10,
                width=120,
                command=lambda r=room: self.update_room_status(r, "Maintenance")
            )
            maintenance_btn.pack(side="left")
        elif status in ["Cleaning", "Maintenance"]:
            btn_frame = ctk.CTkFrame(card, fg_color="white")
            btn_frame.pack(fill="x", pady=(10, 15), padx=20)

            available_btn = ctk.CTkButton(
                btn_frame,
                text="Set Available",
                font=("SVN-Gilroy", 14),
                fg_color="#28A745",
                text_color="white",
                hover_color="#218838",
                corner_radius=10,
                width=120,
                command=lambda r=room: self.update_room_status(r, "Available")
            )
            available_btn.pack(side="left")

    def update_room_status(self, room, new_status):
        """Update room status"""
        success = self.room_service.update_room_status(room.get("roomId"), new_status)
        if success:
            self.load_room_status_tab()
        else:
            messagebox.showerror("Error", "Cannot update room status (invalid status change)")

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
        """Called when this view is shown - reload data"""
        self.load_data()
