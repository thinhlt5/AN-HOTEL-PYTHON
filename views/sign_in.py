import customtkinter as ctk
from customtkinter import FontManager
from PIL import Image
import os
import re
import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

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

class SignInView(ctk.CTkFrame):
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.configure(fg_color="white")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="white")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=3)
        self.main_container.grid_columnconfigure(1, weight=2)
        # Left side - Image frame
        self.left_frame = ctk.CTkFrame(self.main_container, fg_color="#D3D3D3")
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_propagate(False)
        self.load_image()
        # Right side - Content frame
        self.right_frame = ctk.CTkFrame(self.main_container, fg_color="white")
        self.right_frame.grid(row=0, column=1, sticky="nsew", pady=(50, 0))
        self.right_frame.grid_propagate(False)
        self.create_content()
        # Auth service
        self.auth_service = controller.get_auth_service() if controller else AuthService()
    
    def load_image(self):
        """Load and display image on the left side"""
        try:
            # Path to image - adjust this path as needed
            image_path = "assets/images/hotel.png"
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
            text="Sign In",
            font=("1FTV HF Gesco", 64, "bold"),
            text_color="black"
        )
        get_label.pack(pady=(0, 20))

        subtitle_label = ctk.CTkLabel(
            self.right_frame,
            text="Welcome back!",
            font=("SVN-Gilroy", 24),
            text_color="black"
        )
        subtitle_label.pack(pady=(0, 30))
        
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
        self.password_entry.pack(fill="x", padx=35, pady=(0, 30))
        self.password_entry.bind("<KeyRelease>", lambda e: self.clear_error())
        
        # Sign In Button
        sign_in_btn = ctk.CTkButton(
            self.right_frame,
            text="SIGN IN",
            font=("SVN-Gilroy", 20, "bold"),
            fg_color="#E5E5E5",
            text_color="black",
            hover_color="#D0D0D0",
            height=50,
            corner_radius=10,
            command=self.on_sign_in
        )
        sign_in_btn.pack(fill="x", padx=35, pady=(0, 15))
        
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

        sign_up_label = ctk.CTkLabel(
            self.right_frame,
            text="Don't have an account? Sign up here",
            font=("SVN-Gilroy", 13),
            text_color="gray",
            cursor="hand2"
        )
        sign_up_label.pack()
        sign_up_label.bind("<Button-1>", lambda e: self.on_sign_up_link())

    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def show_error(self, message, field=None):
        """Show error message and highlight field with red border"""
        self.error_label.configure(text=message, text_color="red")
        self.error_label.update_idletasks()
        
        # Reset all borders to default
        self.email_entry.configure(border_color="#E5E5E5")
        self.password_entry.configure(border_color="#E5E5E5")
        
        # Highlight the field with error (red border)
        if field == "email":
            self.email_entry.configure(border_color="red")
        elif field == "password":
            self.password_entry.configure(border_color="red")
        elif field == "all":
            self.email_entry.configure(border_color="red")
            self.password_entry.configure(border_color="red")
    
    def clear_error(self):
        """Clear error message and reset borders"""
        self.error_label.configure(text="")
        self.email_entry.configure(border_color="#E5E5E5")
        self.password_entry.configure(border_color="#E5E5E5")

    def on_sign_in(self):
        """Handle sign in button click"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        self.clear_error()
        if not email or not password:
            self.show_error("Please fill in all fields", field="all")
            return
        if not self.validate_email(email):
            self.show_error("Invalid email format.\n Please enter a valid email address.", field="email")
            return
        
        # Dùng unified_login thay vì login
        user = self.auth_service.unified_login(email, password)
        
        if user:
            role = user.get("role")
            name = user.get("name", email)
            print(f"Login successful! Welcome {name} ({role})")
            self.show_error("Login successful! Redirecting...", field=None)
            self.error_label.configure(text_color="green")
            
            if self.controller:
                self.controller.set_current_user(user)
                
                # Navigate based on role
                if role == "admin":
                    self.controller.show_frame("AdminBookingView")
                else:  # customer
                    self.controller.show_frame("MainAppView")
        else:
            self.show_error("Invalid email or password.\n Please try again.", field="all")
    
    def on_sign_up_link(self):
        """Handle sign up link click"""
        print("Sign up link clicked")
        if self.controller:
            self.controller.show_frame("RegisterView")

## Do not run as standalone window, managed by App
