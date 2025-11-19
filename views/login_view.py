import customtkinter as ctk
from customtkinter import FontManager
from PIL import Image
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


class LoginView(ctk.CTkFrame):
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        # Fill available space
        self.configure(fg_color="white")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Main container mimicking standalone window layout
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
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=40, pady=60)
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
        
        # Title - "Get Started" (split into two labels for better spacing)
        get_label = ctk.CTkLabel(
            self.right_frame,
            text="Get",
            font=("1FTV HF Gesco", 64, "bold"),
            text_color="black"
        )
        get_label.pack(pady=(0, 0))
        
        started_label = ctk.CTkLabel(
            self.right_frame,
            text="Started",
            font=("1FTV HF Gesco", 64, "bold"),
            text_color="black"
        )
        started_label.pack(pady=(0, 20))
        
        # Subtitle - "Start with sign up or sign in"
        subtitle_label = ctk.CTkLabel(
            self.right_frame,
            text="Start with sign up or sign in",
            font=("SVN-Gilroy", 24),
            text_color="black"
        )
        subtitle_label.pack(pady=(0, 30))
        
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
        sign_in_btn.pack(fill="x", pady=(0, 15))
        
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
        sign_up_btn.pack(fill="x", pady=(0, 30))
        
        # Continue without login link
        continue_label = ctk.CTkLabel(
            self.right_frame,
            text="Continue without login",
            font=("SVN-Gilroy", 13),
            text_color="gray",
            cursor="hand2"
        )
        continue_label.pack()
        continue_label.bind("<Button-1>", lambda e: self.on_continue_without_login())
    
    def on_sign_in(self):
        """Handle sign in button click"""
        if self.controller:
            self.controller.show_frame("SignInView")

    def on_sign_up(self):
        """Handle sign up button click"""
        if self.controller:
            self.controller.show_frame("RegisterView")

    def on_continue_without_login(self):
        """Handle continue without login"""
        if self.controller:
            self.controller.set_current_user(None)
            self.controller.show_frame("MainAppView")
