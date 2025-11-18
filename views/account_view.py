import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class AccountView(ctk.CTk):
    def __init__(self, account=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Window properties
        self.title("AN Hotel - Account")
        self.geometry("1000x750")
        self.resizable(False, False)

        # Dummy account data (can be overwritten by passing `account`)
        self.account_data = account or {
            "full_name": "Nguyen Van A",
            "phone": "0912 345 678",
            "identity": "012345678901"
        }

        # Main container with sidebar + content
        self.main_container = ctk.CTkFrame(self, fg_color="white")
        self.main_container.pack(side="top", fill="both", expand=True)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=0)  # Sidebar
        self.main_container.grid_columnconfigure(1, weight=5)  # Content

        self.create_sidebar()
        self.create_account_tabview()

    def create_sidebar(self):
        """Left navigation sidebar (reused layout)."""
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            fg_color="#E5E5E5",
            width=150,
            corner_radius=0,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        nav_items = [
            "Home",
            "Rooms",
            "Our Services",
            "My Bookings",
            "Account settings",
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

        info_items = [
            ("Họ và Tên", self.account_data.get("full_name", "")),
            ("Số điện thoại", self.account_data.get("phone", "")),
            ("CCCD", self.account_data.get("identity", "")),
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
        form_container = ctk.CTkFrame(self.tab_update, fg_color="white", corner_radius=50)
        form_container.pack(fill="both", expand=True, padx=20, pady=20)

        form_frame = ctk.CTkFrame(
            form_container,
            fg_color="white",
            corner_radius=50,
            border_width=2,
        )
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkLabel(
            form_frame,
            text="Cập nhật thông tin cá nhân",
            font=("SVN-Gilroy", 20, "bold"),
            text_color="black",
        )
        header.pack(anchor="w", padx=20, pady=(20, 5))

        subtitle = ctk.CTkLabel(
            form_frame,
            text="Điền thông tin mới và lưu thay đổi",
            font=("SVN-Gilroy", 14),
            text_color="#777777",
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 15))

        self.update_entries = {}
        fields = [
            ("Họ và Tên", "full_name"),
            ("Số điện thoại", "phone"),
            ("CCCD", "identity"),
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
                placeholder_text=f"Nhập {label_text.lower()}",
                font=("SVN-Gilroy", 13),
                height=40,
            )
            entry.pack(fill="x", pady=(0, 10))
            entry.insert(0, self.account_data.get(key, ""))
            self.update_entries[key] = entry

        save_btn = ctk.CTkButton(
            form_frame,
            text="Lưu thay đổi",
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
            text="Đổi mật khẩu",
            font=("SVN-Gilroy", 20, "bold"),
            text_color="black",
        )
        header.pack(anchor="w", padx=20, pady=(20, 5))

        subtitle = ctk.CTkLabel(
            pwd_frame,
            text="Nhập mật khẩu hiện tại và mật khẩu mới",
            font=("SVN-Gilroy", 14),
            text_color="#777777",
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 15))

        self.password_entries = {}
        pwd_fields = [
            ("Mật khẩu hiện tại", "old_password"),
            ("Mật khẩu mới", "new_password"),
            ("Xác nhận mật khẩu mới", "confirm_password"),
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
            text="Cập nhật mật khẩu",
            font=("SVN-Gilroy", 15, "bold"),
            fg_color="#3A7BFF",
            hover_color="#335FCC",
            height=45,
            corner_radius=10,
            command=self.change_password,
        )
        change_btn.pack(anchor="e", padx=20, pady=(10, 20))

    def save_account_changes(self):
        """Placeholder for saving updated info."""
        new_data = {key: entry.get() for key, entry in self.update_entries.items()}
        print("Save account changes:", new_data)

    def change_password(self):
        """Placeholder for password change logic."""
        passwords = {key: entry.get() for key, entry in self.password_entries.items()}
        if passwords["new_password"] == passwords["confirm_password"]:
            print("Password changed successfully")
        else:
            print("New password and confirmation do not match")

    def on_nav_click(self, item):
        print(f"Navigation clicked: {item}")


if __name__ == "__main__":
    app = AccountView()
    app.mainloop()

