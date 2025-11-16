import json
import bcrypt
from typing import Optional


class AuthService:
    def __init__(self, user_file_path: str = "data/users.json"):
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
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    # --------------------------- Register -----------------------------------
    def register(self, name: str, email: str, phone: str, password: str) -> bool:
        users = self.load_users()

        # Check email exists
        if any(u["email"].lower() == email.lower() for u in users):
            return False  # Email already exists

        hashed_pw = self.hash_password(password)

        new_user = {
            "name": name,
            "email": email,
            "phone": phone,
            "password": hashed_pw,
            "role": "customer"
        }

        users.append(new_user)
        self.save_users(users)
        return True

    # --------------------------- Login --------------------------------------
    def login(self, email: str, password: str) -> Optional[dict]:
        users = self.load_users()

        for u in users:
            if u["email"].lower() == email.lower():
                if self.verify_password(password, u["password"]):
                    return u  # Login success
                return None  # Wrong password

        return None  # Email not found

    # ----------------------- Change Password --------------------------------
    def change_password(self, email: str, old_pw: str, new_pw: str) -> bool:
        users = self.load_users()

        for user in users:
            if user["email"].lower() == email.lower():
                if not self.verify_password(old_pw, user["password"]):
                    return False  # Wrong current password

                user["password"] = self.hash_password(new_pw)
                self.save_users(users)
                return True

        return False
