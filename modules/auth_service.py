import json
import bcrypt
from typing import Optional


class AuthService:
    def __init__(self, user_file_path: str = "db/customer.json"):
        self.user_file = user_file_path

    # ----------------------- Helper: Load / Save JSON -----------------------
    def load_users(self) -> list:
        try:
            with open(self.user_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_users(self, users: list):
        with open(self.user_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)

    # ----------------------- Hash / Verify Password -------------------------
    def hash_password(self, plain_password: str) -> str:
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password using bcrypt."""
        if not hashed_password:
            return False
        
        # Fix hash if missing $ prefix (backward compatibility)
        if hashed_password.startswith("2b$") or hashed_password.startswith("2a$"):
            hashed_password = "$" + hashed_password
        
        # Only verify if it's a valid bcrypt hash
        if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
            try:
                return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
            except (ValueError, TypeError):
                return False
        
        return False

    # --------------------------- Register -----------------------------------
    def register(self, name: str, email: str, phone: str, password: str) -> bool:
        users = self.load_users()

        # Check email exists
        if any(u["email"].lower() == email.lower() for u in users):
            return False  # Email already exists

        # Find max customerID and auto increment
        max_id = 0
        for u in users:
            if "customerID" in u:
                if u["customerID"] > max_id:
                    max_id = u["customerID"]
        
        new_customer_id = max_id + 1
        hashed_pw = self.hash_password(password)

        new_user = {
            "customerID": new_customer_id,
            "name": name,
            "email": email,
            "phone": phone,
            "passwordHash": hashed_pw
        }

        users.append(new_user)
        self.save_users(users)
        return True

    # --------------------------- Login --------------------------------------
    def login(self, email: str, password: str) -> Optional[dict]:
        users = self.load_users()

        for u in users:
            if u["email"].lower() == email.lower():
                # Check both passwordHash (new format) and password (old format)
                password_field = u.get("passwordHash") or u.get("password")
                if password_field and self.verify_password(password, password_field):
                    return u  # Login success
                return None  # Wrong password

        return None  # Email not found

    # --------------------------- Unified Login ------------------------------
    def unified_login(self, email: str, password: str) -> Optional[dict]:
        """
        Try to login as admin first, then as customer.
        Both use email for authentication.
        
        Args:
            email: email address
            password: password
        
        Returns:
            User dict with role field (from JSON or inferred), or None if not found
        """
        # Step 1: Try admin.json first
        try:
            with open("db/admin.json", "r", encoding="utf-8") as f:
                admins = json.load(f)
        except FileNotFoundError:
            admins = []
        
        for admin in admins:
            if admin.get("email", "").lower() == email.lower():
                password_field = admin.get("passwordHash")
                if password_field and self.verify_password(password, password_field):
                    admin_data = admin.copy()
                    # Use role from JSON if exists, otherwise default to "admin"
                    if "role" not in admin_data:
                        admin_data["role"] = "admin"
                    return admin_data
                return None  # Wrong password for admin
        
        # Step 2: Try customer.json if not found in admin
        users = self.load_users()
        for user in users:
            if user.get("email", "").lower() == email.lower():
                password_field = user.get("passwordHash") or user.get("password")
                if password_field and self.verify_password(password, password_field):
                    user_data = user.copy()
                    # Use role from JSON if exists, otherwise default to "customer"
                    if "role" not in user_data:
                        user_data["role"] = "customer"
                    return user_data
                return None  # Wrong password for customer
        
        return None  # Not found in both

    # ----------------------- Change Password --------------------------------
    def change_password(self, user_data: dict, old_pw: str, new_pw: str) -> tuple:
        """
        Change password for both customer and admin.
        
        Args:
            user_data: Current user data dict with role, email, customerID/adminID
            old_pw: Old password
            new_pw: New password
        
        Returns:
            Tuple of (success: bool, updated_user: Optional[dict], error_message: Optional[str])
        """
        user_role = user_data.get("role", "customer")
        user_email = user_data.get("email")
        
        if not user_email:
            return False, None, "Email không tồn tại"
        
        # Verify old password
        current_hash = user_data.get("passwordHash", "")
        if not current_hash or not self.verify_password(old_pw, current_hash):
            return False, None, "Mật khẩu hiện tại không đúng"
        
        # Update password
        if user_role == "admin":
            # Update admin in admin.json
            try:
                with open("db/admin.json", "r", encoding="utf-8") as f:
                    admins = json.load(f)
            except FileNotFoundError:
                return False, None, "Không tìm thấy file admin.json"
            
            admin_id = user_data.get("adminID")
            found = False
            for admin in admins:
                if admin.get("adminID") == admin_id:
                    admin["passwordHash"] = self.hash_password(new_pw)
                    found = True
                    # Return updated admin data
                    updated_user = admin.copy()
                    if "role" not in updated_user:
                        updated_user["role"] = "admin"
                    break
            
            if not found:
                return False, None, "Không tìm thấy tài khoản admin"
            
            # Save admin.json
            with open("db/admin.json", "w", encoding="utf-8") as f:
                json.dump(admins, f, indent=4, ensure_ascii=False)
            
            return True, updated_user, None
        else:
            # Update customer in customer.json
            users = self.load_users()
            found = False
            for user in users:
                if user.get("email", "").lower() == user_email.lower():
                    # Check both passwordHash (new format) and password (old format)
                    password_field = user.get("passwordHash") or user.get("password")
                    if not password_field or not self.verify_password(old_pw, password_field):
                        return False, None, "Mật khẩu hiện tại không đúng"
                    
                    # Update to passwordHash format
                    user["passwordHash"] = self.hash_password(new_pw)
                    # Remove old password field if exists
                    if "password" in user:
                        del user["password"]
                    
                    found = True
                    updated_user = user.copy()
                    if "role" not in updated_user:
                        updated_user["role"] = "customer"
                    break
            
            if not found:
                return False, None, "Không tìm thấy tài khoản customer"
            
            self.save_users(users)
            return True, updated_user, None

    # ----------------------- Admin Change Password (No Old Password) --------
    def admin_change_password(self, user_data: dict, new_pw: str) -> tuple:
        """
        Admin can change user password without requiring old password.
        
        Args:
            user_data: User data dict with customerID/adminID, email, role
            new_pw: New password
        
        Returns:
            Tuple of (success: bool, updated_user: Optional[dict], error_message: Optional[str])
        """
        if not new_pw or len(new_pw) < 6:
            return False, None, "Password must be at least 6 characters long"
        
        user_role = user_data.get("role", "customer")
        user_email = user_data.get("email")
        
        if not user_email:
            return False, None, "Email không tồn tại"
        
        # Update password
        if user_role == "admin":
            # Update admin in admin.json
            try:
                with open("db/admin.json", "r", encoding="utf-8") as f:
                    admins = json.load(f)
            except FileNotFoundError:
                return False, None, "Không tìm thấy file admin.json"
            
            admin_id = user_data.get("adminID")
            found = False
            for admin in admins:
                if admin.get("adminID") == admin_id:
                    admin["passwordHash"] = self.hash_password(new_pw)
                    found = True
                    updated_user = admin.copy()
                    if "role" not in updated_user:
                        updated_user["role"] = "admin"
                    break
            
            if not found:
                return False, None, "Không tìm thấy tài khoản admin"
            
            # Save admin.json
            with open("db/admin.json", "w", encoding="utf-8") as f:
                json.dump(admins, f, indent=4, ensure_ascii=False)
            
            return True, updated_user, None
        else:
            # Update customer in customer.json
            users = self.load_users()
            found = False
            for user in users:
                if user.get("email", "").lower() == user_email.lower():
                    user["passwordHash"] = self.hash_password(new_pw)
                    # Remove old password field if exists
                    if "password" in user:
                        del user["password"]
                    
                    found = True
                    updated_user = user.copy()
                    if "role" not in updated_user:
                        updated_user["role"] = "customer"
                    break
            
            if not found:
                return False, None, "Không tìm thấy tài khoản customer"
            
            self.save_users(users)
            return True, updated_user, None

    # ----------------------- Update User Info -------------------------------
    def update_user_info(self, user_data: dict, name: str, phone: str, identity: str = None) -> tuple:
        """
        Update user information for both customer and admin.
        
        Args:
            user_data: Current user data dict with role, customerID/adminID
            name: New name
            phone: New phone
            identity: New identity (optional, can be None)
        
        Returns:
            Tuple of (success: bool, updated_user: Optional[dict], error_message: Optional[str])
        """
        if not name or not phone:
            return False, None, "Tên và số điện thoại là bắt buộc"
        
        user_role = user_data.get("role", "customer")
        user_id = user_data.get("customerID") or user_data.get("adminID")
        
        update_data = {
            "name": name,
            "phone": phone
        }
        
        if identity is not None and identity:
            update_data["identity"] = identity
        
        if user_role == "admin":
            # Update admin in admin.json
            try:
                with open("db/admin.json", "r", encoding="utf-8") as f:
                    admins = json.load(f)
            except FileNotFoundError:
                return False, None, "Không tìm thấy file admin.json"
            
            found = False
            for admin in admins:
                if admin.get("adminID") == user_id:
                    admin.update(update_data)
                    found = True
                    # Return updated admin data
                    updated_user = admin.copy()
                    if "role" not in updated_user:
                        updated_user["role"] = "admin"
                    break
            
            if not found:
                return False, None, "Không tìm thấy tài khoản admin"
            
            # Save admin.json
            with open("db/admin.json", "w", encoding="utf-8") as f:
                json.dump(admins, f, indent=4, ensure_ascii=False)
            
            return True, updated_user, None
        else:
            # Update customer using DBManager
            # We need to import it here to avoid circular import
            from modules.db_manager import DBManager
            db_manager = DBManager("db")
            db_manager.update_customer(user_id, update_data)
            
            # Get updated user data
            customers = db_manager.get_all_customers()
            for customer in customers:
                if customer.get("customerID") == user_id:
                    updated_user = customer.copy()
                    if "role" not in updated_user:
                        updated_user["role"] = "customer"
                    return True, updated_user, None
            
            return False, None, "Không tìm thấy user sau khi cập nhật"