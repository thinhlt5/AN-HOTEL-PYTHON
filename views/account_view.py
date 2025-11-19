import customtkinter as ctk
from customtkinter import FontManager
import os

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


class AccountView(ctk.CTkFrame):
    def __init__(self, parent, controller=None, account=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        
        self.configure(fg_color="white")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Load account data from controller's current user
        self.account_data = account or self._load_user_data()

        # Main container with sidebar + content
        self.main_container = ctk.CTkFrame(self, fg_color="white")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=0)  # Sidebar
        self.main_container.grid_columnconfigure(1, weight=5)  # Content

        self.sidebar = None  # Initialize sidebar variable
        self.create_account_tabview()
        self.create_sidebar()  # Create sidebar after main content
    
    def _load_user_data(self):
        """Load user data from controller's current user"""
        if self.controller:
            current_user = self.controller.get_current_user()
            if current_user:
                # Map user data fields to account_data format
                return {
                    "full_name": current_user.get("name", ""),
                    "phone": current_user.get("phone", ""),
                    "identity": current_user.get("identity", ""),
                    "email": current_user.get("email", ""),
                    "customerID": current_user.get("customerID"),
                    "role": current_user.get("role", "customer")
                }
        # Default dummy data if no user logged in
        return {
            "full_name": "Nguyen Van A",
            "phone": "0912 345 678",
            "identity": "012345678901",
            "email": "",
            "customerID": None,
            "role": "customer"
        }

    def create_sidebar(self):
        """Left navigation sidebar (reused layout)."""
        # Destroy existing sidebar if it exists
        if self.sidebar:
            self.sidebar.destroy()
        
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            fg_color="#E5E5E5",
            width=150,
            corner_radius=0,
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

        nav_items = [
            "Home",
            "Room",
            "My Bookings",
            "Account Settings",
            "Sign out",
        ]

        for item in nav_items:
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
                command=lambda x=item: self.on_nav_click(x),
            )
            btn.pack(fill="x", padx=10, pady=5)

    def create_account_tabview(self):
        """Main tabbed content (Account Info / Update / Password)."""
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="white")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=(20, 0))

        self.tabview = ctk.CTkTabview(
            self.content_frame,
            segmented_button_fg_color="#E5E5E5",
            segmented_button_selected_color="#3A7BFF",
            segmented_button_unselected_color="#A9A9A9",
        )
        
        self.tabview.pack(fill="both", expand=True)

        self.tab_info = self.tabview.add("Account Information")
        self.tab_update = self.tabview.add("Change Information")
        self.tab_password = self.tabview.add("Change Password")

        self.build_account_info_tab()
        self.build_update_info_tab()
        self.build_change_password_tab()

    def build_account_info_tab(self):
        # Reload user data to ensure it's up to date
        self.account_data = self._load_user_data()
        
        info_container = ctk.CTkFrame(self.tab_info, fg_color="white", corner_radius=50)
        info_container.pack(fill="both", expand=True, padx=20, pady=20)

        info_frame = ctk.CTkFrame(
            info_container,
            fg_color="white",
            corner_radius=50,
            border_width=2,
            border_color="white",
        )
        info_frame.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkLabel(
            info_frame,
            text="Personal Details",
            font=("SVN-Gilroy", 20, "bold"),
            text_color="black",
        )
        header.pack(anchor="w", padx=20, pady=(20, 10))

        # Get actual values from account_data
        full_name = self.account_data.get("full_name", "") or "Not updated"
        phone = self.account_data.get("phone", "") or "Not updated"
        email = self.account_data.get("email", "") or "Not updated"

        info_items = [
            ("Full Name", full_name),
            ("Phone Number", phone),
            ("Email", email)
        ]

        for label_text, value_text in info_items:
            row = ctk.CTkFrame(info_frame, fg_color="white")
            row.pack(fill="x", padx=20, pady=8)

            label = ctk.CTkLabel(
                row,
                text=label_text,
                font=("SVN-Gilroy", 14),
                text_color="#555555",
                anchor="w",
            )
            label.pack(side="left", anchor="w")

            value = ctk.CTkLabel(
                row,
                text=value_text,
                font=("SVN-Gilroy", 14, "bold"),
                text_color="black",
                anchor="e",
            )
            value.pack(side="right", anchor="e")

    def build_update_info_tab(self):
        # Reload user data to ensure it's up to date
        self.account_data = self._load_user_data()
        
        form_container = ctk.CTkFrame(self.tab_update, fg_color="white", corner_radius=50)
        form_container.pack(fill="both", expand=True, padx=20, pady=20)

        form_frame = ctk.CTkFrame(
            form_container,
            fg_color="white",
            corner_radius=50,
            border_width=2,
            border_color="white"
        )
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkLabel(
            form_frame,
            text="Update Personal Information",
            font=("SVN-Gilroy", 20, "bold"),
            text_color="black",
        )
        header.pack(anchor="w", padx=20, pady=(20, 5))

        subtitle = ctk.CTkLabel(
            form_frame,
            text="Enter new information and save changes",
            font=("SVN-Gilroy", 14),
            text_color="#777777",
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 15))

        self.update_entries = {}
        fields = [
            ("Full Name", "full_name"),
            ("Phone Number", "phone"),
        ]

        for label_text, key in fields:
            row = ctk.CTkFrame(form_frame, fg_color="white")
            row.pack(fill="x", padx=20, pady=8)

            label = ctk.CTkLabel(
                row,
                text=label_text,
                font=("SVN-Gilroy", 13),
                text_color="#333333",
            )
            label.pack(anchor="w", pady=(10, 5))

            entry = ctk.CTkEntry(
                row,
                placeholder_text=f"Enter {label_text.lower()}",
                font=("SVN-Gilroy", 13),
                height=40,
            )
            entry.pack(fill="x", pady=(0, 10))
            # Pre-fill with current user data
            current_value = self.account_data.get(key, "")
            if current_value:
                entry.insert(0, current_value)
            self.update_entries[key] = entry

        save_btn = ctk.CTkButton(
            form_frame,
            text="Save Changes",
            font=("SVN-Gilroy", 15, "bold"),
            fg_color="#3A7BFF",
            hover_color="#335FCC",
            height=45,
            corner_radius=10,
            command=self.save_account_changes,
        )
        save_btn.pack(anchor="e", padx=20, pady=(10, 20))

    def build_change_password_tab(self):
        pwd_container = ctk.CTkFrame(self.tab_password, fg_color="white", corner_radius=50)
        pwd_container.pack(fill="both", expand=True, padx=20, pady=20)

        pwd_frame = ctk.CTkFrame(
            pwd_container,
            fg_color="white",
            corner_radius=20,
            border_width=2,
            border_color="white",
        )
        pwd_frame.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkLabel(
            pwd_frame,
            text="Change Password",
            font=("SVN-Gilroy", 20, "bold"),
            text_color="black",
        )
        header.pack(anchor="w", padx=20, pady=(20, 5))

        subtitle = ctk.CTkLabel(
            pwd_frame,
            text="Enter current password and new password",
            font=("SVN-Gilroy", 14),
            text_color="#777777",
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 15))

        self.password_entries = {}
        pwd_fields = [
            ("Current Password", "old_password"),
            ("New Password", "new_password"),
            ("Confirm New Password", "confirm_password"),
        ]

        for label_text, key in pwd_fields:
            row = ctk.CTkFrame(pwd_frame, fg_color="white")
            row.pack(fill="x", padx=20, pady=8)

            label = ctk.CTkLabel(
                row,
                text=label_text,
                font=("SVN-Gilroy", 13),
                text_color="#333333",
            )
            label.pack(anchor="w", pady=(10, 5))

            entry = ctk.CTkEntry(
                row,
                placeholder_text=f"{label_text}...",
                font=("SVN-Gilroy", 13),
                height=40,
                show="*",
            )
            entry.pack(fill="x", pady=(0, 10))
            self.password_entries[key] = entry

        change_btn = ctk.CTkButton(
            pwd_frame,
            text="Update Password",
            font=("SVN-Gilroy", 15, "bold"),
            fg_color="#3A7BFF",
            hover_color="#335FCC",
            height=45,
            corner_radius=10,
            command=self.change_password,
        )
        change_btn.pack(anchor="e", padx=20, pady=(10, 20))

    def save_account_changes(self):
        """Save updated account information - UI only, delegates to AuthService."""
        if not self.controller:
            return
        
        current_user = self.controller.get_current_user()
        if not current_user:
            self._show_message("Error", "You need to log in to update information", "error")
            return
        
        # Get data from UI entries
        name_entry = self.update_entries.get("full_name")
        phone_entry = self.update_entries.get("phone")
        
        if not name_entry or not phone_entry:
            self._show_message("Error", "Error occurred while getting data", "error")
            return
        
        new_name = name_entry.get().strip()
        new_phone = phone_entry.get().strip()
        
        # Basic UI validation
        if not new_name:
            self._show_message("Error", "Please enter full name", "error")
            return
        
        if not new_phone:
            self._show_message("Error", "Please enter phone number", "error")
            return
        
        # Delegate to AuthService
        try:
            auth_service = self.controller.get_auth_service()
            success, updated_user, error_msg = auth_service.update_user_info(
                current_user, new_name, new_phone
            )
            
            if success and updated_user:
                # Update controller with new user data
                self.controller.set_current_user(updated_user)
                # Reload account data
                self.account_data = self._load_user_data()
                # Show success message
                self._show_message("Success", "Information updated successfully!", "success")
                # Refresh account info tab
                self._refresh_account_info_tab()
            else:
                self._show_message("Error", error_msg or "Unable to update information", "error")
        except Exception as e:
            self._show_message("Error", f"An error occurred: {str(e)}", "error")
    
    def _show_message(self, title, message, msg_type="info"):
        """Show a message dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self)
        dialog.grab_set()
        
        color = "green" if msg_type == "success" else "red" if msg_type == "error" else "blue"
        
        label = ctk.CTkLabel(
            dialog,
            text=message,
            font=("SVN-Gilroy", 16),
            text_color=color,
            wraplength=350
        )
        label.pack(padx=20, pady=20)
        
        ok_btn = ctk.CTkButton(
            dialog,
            text="OK",
            font=("SVN-Gilroy", 14),
            command=dialog.destroy
        )
        ok_btn.pack(pady=10)
    
    def _refresh_account_info_tab(self):
        """Refresh the account information tab with updated data"""
        # Clear existing widgets in tab_info
        for widget in self.tab_info.winfo_children():
            widget.destroy()
        
        # Rebuild the tab
        self.build_account_info_tab()

    def change_password(self):
        """Change user password - UI only, delegates to AuthService."""
        if not self.controller:
            return
        
        current_user = self.controller.get_current_user()
        if not current_user:
            self._show_message("Error", "You need to log in to change password", "error")
            return
        
        # Get password entries from UI
        old_pwd_entry = self.password_entries.get("old_password")
        new_pwd_entry = self.password_entries.get("new_password")
        confirm_pwd_entry = self.password_entries.get("confirm_password")
        
        if not old_pwd_entry or not new_pwd_entry or not confirm_pwd_entry:
            self._show_message("Error", "Error occurred while getting data", "error")
            return
        
        old_password = old_pwd_entry.get()
        new_password = new_pwd_entry.get()
        confirm_password = confirm_pwd_entry.get()
        
        # Basic UI validation
        if not old_password:
            self._show_message("Error", "Please enter current password", "error")
            return
        
        if not new_password:
            self._show_message("Error", "Please enter new password", "error")
            return
        
        if len(new_password) < 6:
            self._show_message("Error", "New password must be at least 6 characters", "error")
            return
        
        if new_password != confirm_password:
            self._show_message("Error", "New password and confirmation do not match", "error")
            return
        
        if old_password == new_password:
            self._show_message("Error", "New password must be different from current password", "error")
            return
        
        # Delegate to AuthService
        try:
            auth_service = self.controller.get_auth_service()
            success, updated_user, error_msg = auth_service.change_password(
                current_user, old_password, new_password
            )
            
            if success and updated_user:
                # Update controller with new user data
                self.controller.set_current_user(updated_user)
                # Clear password fields
                old_pwd_entry.delete(0, 'end')
                new_pwd_entry.delete(0, 'end')
                confirm_pwd_entry.delete(0, 'end')
                # Show success message
                self._show_message("Success", "Password changed successfully!", "success")
            else:
                self._show_message("Error", error_msg or "Unable to change password", "error")
        except Exception as e:
            self._show_message("Error", f"An error occurred: {str(e)}", "error")

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
        """Called when this view is shown - refresh sidebar and reload user data"""
        # Reload user data
        self.account_data = self._load_user_data()
        
        # Refresh sidebar
        self.create_sidebar()
        
        # Refresh tabs to show updated data
        # Clear and rebuild account info tab
        for widget in self.tab_info.winfo_children():
            widget.destroy()
        self.build_account_info_tab()
        
        # Clear and rebuild update info tab
        for widget in self.tab_update.winfo_children():
            widget.destroy()
        self.build_update_info_tab()


if __name__ == "__main__":
    app = AccountView()
    app.mainloop()

