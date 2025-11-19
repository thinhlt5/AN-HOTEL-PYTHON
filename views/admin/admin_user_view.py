import customtkinter as ctk
from customtkinter import FontManager
import os
import sys
from tkinter import messagebox

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.db_manager import DBManager
from modules.auth_service import AuthService

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


class AdminUserView(ctk.CTkFrame):
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        # Initialize services
        if controller:
            self.db_manager = controller.get_db_manager()
            self.auth_service = controller.get_auth_service()
        else:
            self.db_manager = DBManager("db")
            self.auth_service = AuthService()

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
        """Create main content area"""
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
            text="User Management",
            font=("SVN-Gilroy", 24, "bold"),
            text_color="black"
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Scrollable frame for user cards
        self.scrollable_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="#F5F5F5")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(1, weight=1)

        # Load users
        self.load_users()

    def load_users(self):
        """Load and display all users"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Get all customers
        customers = self.db_manager.get_all_customers()

        if not customers:
            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No users",
                font=("SVN-Gilroy", 14),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return

        # Create user cards
        for customer in customers:
            self.create_user_card(customer)

    def create_user_card(self, user):
        """Create a user card"""
        card = ctk.CTkFrame(self.scrollable_frame, fg_color="white", border_color="#E5E5E5", border_width=2, corner_radius=15)
        card.pack(fill="x", pady=10, padx=10)

        # Title - Customer ID
        title = ctk.CTkLabel(
            card,
            text=f"Customer ID: {user.get('customerID', '')}",
            font=("SVN-Gilroy", 16, "bold"),
            text_color="black",
            anchor="w"
        )
        title.pack(anchor="w", pady=(10, 5), padx=20)

        # User information
        name = user.get("name", "")
        email = user.get("email", "")
        phone = user.get("phone", "")

        summary_items = [
            ("Name", name),
            ("Email", email),
            ("Phone", phone)
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
                text_color="gray",
                anchor="e"
            )
            value.pack(side="right", anchor="e", fill="x", expand=True, padx=(20, 0))

        # Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="white")
        btn_frame.pack(fill="x", pady=(10, 15), padx=20)

        update_info_btn = ctk.CTkButton(
            btn_frame,
            text="Update Personal Info",
            font=("SVN-Gilroy", 14),
            fg_color="#3A7BFF",
            text_color="white",
            hover_color="#2A5BCC",
            corner_radius=10,
            width=150,
            command=lambda u=user: self.show_update_info_dialog(u)
        )
        update_info_btn.pack(side="left", padx=(0, 10))

        change_password_btn = ctk.CTkButton(
            btn_frame,
            text="Change Password",
            font=("SVN-Gilroy", 14),
            fg_color="#28A745",
            text_color="white",
            hover_color="#218838",
            corner_radius=10,
            width=150,
            command=lambda u=user: self.show_change_password_dialog(u)
        )
        change_password_btn.pack(side="left", padx=(0, 10))

        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            font=("SVN-Gilroy", 14),
            fg_color="#DC3545",
            text_color="white",
            hover_color="#C82333",
            corner_radius=10,
            width=150,
            command=lambda u=user: self.delete_user(u)
        )
        delete_btn.pack(side="left")

    def show_update_info_dialog(self, user):
        """Show dialog to update user personal information"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Update Personal Information")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()

        # Name
        ctk.CTkLabel(dialog, text="Name:", font=("SVN-Gilroy", 12)).pack(pady=(20, 5), padx=20, anchor="w")
        name_entry = ctk.CTkEntry(dialog, font=("SVN-Gilroy", 12), width=300)
        name_entry.insert(0, user.get("name", ""))
        name_entry.pack(padx=20, pady=(0, 10))

        # Phone
        ctk.CTkLabel(dialog, text="Phone:", font=("SVN-Gilroy", 12)).pack(pady=(10, 5), padx=20, anchor="w")
        phone_entry = ctk.CTkEntry(dialog, font=("SVN-Gilroy", 12), width=300)
        phone_entry.insert(0, user.get("phone", ""))
        phone_entry.pack(padx=20, pady=(0, 20))

        def update_info():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()

            if not name or not phone:
                messagebox.showerror("Error", "Name and phone are required")
                return

            # Prepare user_data for auth_service
            user_data = {
                "customerID": user.get("customerID"),
                "role": user.get("role", "customer")
            }

            success, updated_user, error = self.auth_service.update_user_info(user_data, name, phone)
            if success:
                self.load_users()
                dialog.destroy()
                messagebox.showinfo("Success", "User information updated successfully")
            else:
                messagebox.showerror("Error", error or "Failed to update user information")

        ctk.CTkButton(dialog, text="Update", command=update_info, width=100).pack(pady=10)

    def show_change_password_dialog(self, user):
        """Show dialog to change user password (admin can change without current password)"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Password")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()

        # New password
        ctk.CTkLabel(dialog, text="New Password:", font=("SVN-Gilroy", 12)).pack(pady=(20, 5), padx=20, anchor="w")
        new_password_entry = ctk.CTkEntry(dialog, font=("SVN-Gilroy", 12), width=300, show="*")
        new_password_entry.pack(padx=20, pady=(0, 10))

        # Confirm password
        ctk.CTkLabel(dialog, text="Confirm New Password:", font=("SVN-Gilroy", 12)).pack(pady=(10, 5), padx=20, anchor="w")
        confirm_password_entry = ctk.CTkEntry(dialog, font=("SVN-Gilroy", 12), width=300, show="*")
        confirm_password_entry.pack(padx=20, pady=(0, 20))

        def change_password():
            new_pw = new_password_entry.get()
            confirm_pw = confirm_password_entry.get()

            if not new_pw or not confirm_pw:
                messagebox.showerror("Error", "All fields are required")
                return

            if new_pw != confirm_pw:
                messagebox.showerror("Error", "New passwords do not match")
                return

            if len(new_pw) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long")
                return

            # Use admin_change_password which doesn't require old password
            success, updated_user, error = self.auth_service.admin_change_password(user, new_pw)
            if success:
                self.load_users()
                dialog.destroy()
                messagebox.showinfo("Success", "Password changed successfully")
            else:
                messagebox.showerror("Error", error or "Failed to change password")

        ctk.CTkButton(dialog, text="Change Password", command=change_password, width=100).pack(pady=10)

    def delete_user(self, user):
        """Delete a user"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user {user.get('name', '')} (ID: {user.get('customerID', '')})?"):
            success = self.db_manager.delete_customer(user.get("customerID"))
            if success:
                self.load_users()
                messagebox.showinfo("Success", "User deleted successfully")
            else:
                messagebox.showerror("Error", "Failed to delete user")

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
        self.load_users()
