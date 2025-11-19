import customtkinter as ctk
from customtkinter import FontManager
from PIL import Image
import os
import re
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.auth_service import AuthService

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


class RegisterView(ctk.CTkFrame):
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        # Initialize auth service (fallback for standalone usage)
        self.auth_service = (
            controller.get_auth_service() if controller else AuthService()
        )

        # Main container
        self.configure(fg_color="white")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_container = ctk.CTkFrame(self, fg_color="white")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=3)  # 3/5 width
        self.main_container.grid_columnconfigure(1, weight=2)  # 2/5 width

        # Left side - Image frame (3/5 of window)
        self.left_frame = ctk.CTkFrame(self.main_container, fg_color="#D3D3D3")
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_propagate(False)

        # Load and display image
        self.load_image()

        # Right side - Content frame (2/5 of window)
        self.right_frame = ctk.CTkFrame(self.main_container, fg_color="white")
        self.right_frame.grid(row=0, column=1, sticky="nsew", pady=(50, 0))
        self.right_frame.grid_propagate(False)

        # Create content
        self.create_content()
    
    def load_image(self):
        """Load and display image on the left side"""
        try:
            # Path to image - adjust this path as needed
            image_path = "assets/images/hotel.png"  # Update this path
            if os.path.exists(image_path):
                image = Image.open(image_path)
                # Resize image to fit the frame (3/5 of 1000 = 600)
                image = image.resize((600, 750))
                photo = ctk.CTkImage(light_image=image, size=(600, 750))
                
                image_label = ctk.CTkLabel(self.left_frame, image=photo, text="")
                image_label.image = photo  # Keep a reference
                image_label.pack(fill="both", expand=True)
        except Exception as e:
            print(f"Could not load image: {e}")
    
    def create_content(self):
        """Create the right side content"""
        
        get_label = ctk.CTkLabel(
            self.right_frame,
            text="Sign Up",
            font=("1FTV HF Gesco", 64, "bold"),
            text_color="black"
        )
        get_label.pack(pady=(0, 20))
        

        subtitle_label = ctk.CTkLabel(
            self.right_frame,
            text="Hello. Let's join with us.",
            font=("SVN-Gilroy", 24),
            text_color="black"
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Name input field
        self.name_entry = ctk.CTkEntry(
            self.right_frame,
            placeholder_text="Name",
            font=("SVN-Gilroy", 16),
            height=50,
            corner_radius=10,
            border_color="#E5E5E5",
            fg_color="white",
            text_color="black"
        )
        self.name_entry.pack(fill="x", padx=35, pady=(0, 15))
        self.name_entry.bind("<KeyRelease>", lambda e: self.clear_error())
        
        # Phone input field
        self.phone_entry = ctk.CTkEntry(
            self.right_frame,
            placeholder_text="Phone",
            font=("SVN-Gilroy", 16),
            height=50,
            corner_radius=10,
            border_color="#E5E5E5",
            fg_color="white",
            text_color="black"
        )
        self.phone_entry.pack(fill="x", padx=35, pady=(0, 15))
        self.phone_entry.bind("<KeyRelease>", lambda e: self.clear_error())
        
        # Email input field
        self.email_entry = ctk.CTkEntry(
            self.right_frame,
            placeholder_text="Email",
            font=("SVN-Gilroy", 16),
            height=50,
            corner_radius=10,
            border_color="#E5E5E5",
            fg_color="white",
            text_color="black"
        )
        self.email_entry.pack(fill="x", padx=35, pady=(0, 15))
        self.email_entry.bind("<KeyRelease>", lambda e: self.clear_error())
        
        # Password input field
        self.password_entry = ctk.CTkEntry(
            self.right_frame,
            placeholder_text="Password",
            font=("SVN-Gilroy", 16),
            height=50,
            corner_radius=10,
            border_color="#E5E5E5",
            fg_color="white",
            text_color="black",
            show="*"
        )
        self.password_entry.pack(fill="x", padx=35, pady=(0, 15))
        self.password_entry.bind("<KeyRelease>", lambda e: self.clear_error())
        
        # Confirm Password input field
        self.confirm_password_entry = ctk.CTkEntry(
            self.right_frame,
            placeholder_text="Confirm Password",
            font=("SVN-Gilroy", 16),
            height=50,
            corner_radius=10,
            border_color="#E5E5E5",
            fg_color="white",
            text_color="black",
            show="*"
        )
        self.confirm_password_entry.pack(fill="x", padx=35, pady=(0, 30))
        self.confirm_password_entry.bind("<KeyRelease>", lambda e: self.clear_error())
        
        # Sign Up Button
        sign_up_btn = ctk.CTkButton(
            self.right_frame,
            text="SIGN UP",
            font=("SVN-Gilroy", 20, "bold"),
            fg_color="#E5E5E5",
            text_color="black",
            hover_color="#D0D0D0",
            height=50,
            corner_radius=10,
            command=self.on_sign_up
        )
        sign_up_btn.pack(fill="x", padx=35, pady=(0, 15))
        
        self.error_label = ctk.CTkLabel(
            self.right_frame,
            text="",
            font=("SVN-Gilroy", 16, "bold"),
            text_color="red",
            wraplength=300,
            anchor="center",
            justify="center",
            height=25
        )
        self.error_label.pack(fill="x", padx=35, pady=(0, 10))

        continue_label = ctk.CTkLabel(
            self.right_frame,
            text="Already have an account? Sign in here",
            font=("SVN-Gilroy", 13),
            text_color="gray",
            cursor="hand2"
        )
        continue_label.pack()
        continue_label.bind("<Button-1>", lambda e: self.on_sign_in_link())

    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def show_error(self, message, field=None):
        """Show error message and highlight field with red border"""
        self.error_label.configure(text=message, text_color="red")
        self.error_label.update_idletasks()  # Force update display
        
        # Reset all borders to default
        self.name_entry.configure(border_color="#E5E5E5")
        self.phone_entry.configure(border_color="#E5E5E5")
        self.email_entry.configure(border_color="#E5E5E5")
        self.password_entry.configure(border_color="#E5E5E5")
        self.confirm_password_entry.configure(border_color="#E5E5E5")
        
        # Highlight the field with error (red border)
        if field == "name":
            self.name_entry.configure(border_color="red")
        elif field == "phone":
            self.phone_entry.configure(border_color="red")
        elif field == "email":
            self.email_entry.configure(border_color="red")
        elif field == "password":
            self.password_entry.configure(border_color="red")
            self.confirm_password_entry.configure(border_color="red")
        elif field == "all":
            self.name_entry.configure(border_color="red")
            self.phone_entry.configure(border_color="red")
            self.email_entry.configure(border_color="red")
            self.password_entry.configure(border_color="red")
            self.confirm_password_entry.configure(border_color="red")
    
    def clear_error(self):
        """Clear error message and reset borders"""
        self.error_label.configure(text="")
        self.name_entry.configure(border_color="#E5E5E5")
        self.phone_entry.configure(border_color="#E5E5E5")
        self.email_entry.configure(border_color="#E5E5E5")
        self.password_entry.configure(border_color="#E5E5E5")
        self.confirm_password_entry.configure(border_color="#E5E5E5")

    def on_sign_up(self):
        """Handle sign up button click"""
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Clear previous errors
        self.clear_error()
        
        # Validate input fields are not empty
        if not name or not phone or not email or not password or not confirm_password:
            self.show_error("Please fill in all fields", field="all")
            return
        
        # Validate email format
        if not self.validate_email(email):
            self.show_error("Invalid email format.\n Please enter a valid email address.", field="email")
            return
        
        # Validate password match
        if password != confirm_password:
            self.show_error("Passwords do not match.\n Please try again.", field="password")
            return
        
        # Validate password strength
        if len(password) < 6:
            self.show_error("Password must be at least\n 6 characters long.", field="password")
            return
        
        # Register user using auth_service
        if self.auth_service.register(name, email, phone, password):
            print(f"Sign up successful with email: {email}")
            # Auto login after registration
            user_data = self.auth_service.login(email, password)
            if user_data and self.controller:
                # Set current user
                self.controller.set_current_user(user_data)
                # Redirect based on role
                role = user_data.get("role", "customer")
                if role == "admin":
                    self.controller.show_frame("AdminBookingView")
                else:
                    self.controller.show_frame("MainAppView")
            else:
                # Fallback to login if auto-login fails
                self.show_error("Registration successful! Redirecting to login...", field=None)
                self.error_label.configure(text_color="green")
                self.after(1500, self.on_sign_in_link)
        else:
            self.show_error("The email has already been registered!\n Please try another email", field="email")
    
    def on_sign_in_link(self):
        """Handle sign in link click"""
        if self.controller:
            self.controller.show_frame("LoginView")
