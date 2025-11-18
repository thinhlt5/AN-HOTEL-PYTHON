import customtkinter as ctk

from modules.db_manager import DBManager
from modules.auth_service import AuthService
from modules.booking_service import BookingService
from views.login_view import LoginView
from views.register_view import RegisterView
from views.main_app_view import MainAppView
from views.sign_in import SignInView


class App(ctk.CTk):
    """Main application window acting as controller/state manager."""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("An Hotel Booking System")
        self.geometry("1000x750")
        self.resizable(False, False)

        # Dependency injection
        self.db_manager = DBManager()
        self.auth_service = AuthService("db/customer.json")
        self.booking_service = BookingService(self.db_manager)

        # Session state
        self.current_user = None

        # Main container for stacked frames
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # View registry
        self.frames = {}
        for FrameClass in (LoginView, RegisterView, MainAppView, SignInView):
            frame = FrameClass(parent=self.container, controller=self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[FrameClass.__name__] = frame

        # Initial screen
        self.show_frame("LoginView")

    # -------------------------------------------------------------------------
    # Session helpers
    # -------------------------------------------------------------------------
    def set_current_user(self, user_data):
        """Store current logged-in user data."""
        self.current_user = user_data

    def get_current_user(self):
        """Return current logged-in user data (or None)."""
        return self.current_user

    def logout(self):
        """Clear session state and return to login screen."""
        self.current_user = None
        self.show_frame("LoginView")

    # -------------------------------------------------------------------------
    # Navigation helpers
    # -------------------------------------------------------------------------
    def show_frame(self, page_name):
        """Bring the specified frame to the front."""
        frame = self.frames.get(page_name)
        if frame is None:
            raise ValueError(f"Frame '{page_name}' not found")
        frame.tkraise()
        if hasattr(frame, "on_show") and callable(frame.on_show):
            frame.on_show()

    # -------------------------------------------------------------------------
    # Service accessors
    # -------------------------------------------------------------------------
    def get_auth_service(self):
        return self.auth_service

    def get_booking_service(self):
        return self.booking_service


if __name__ == "__main__":
    app = App()
    app.mainloop()

