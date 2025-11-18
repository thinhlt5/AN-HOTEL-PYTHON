import customtkinter as ctk

ctk.set_appearance_mode("light")

root = ctk.CTk()
root.geometry("1000x700")
root.title("Get Started UI")
root.resizable(False, False)


# --- CONFIG GRID ---
root.grid_columnconfigure(0, weight=7)  # left big area
root.grid_columnconfigure(1, weight=3)  # right small area
root.grid_rowconfigure(0, weight=1)

# --- LEFT SIDE ---
left_frame = ctk.CTkFrame(root, fg_color="#d9d9d9", corner_radius=0)
left_frame.grid(row=0, column=0, sticky="nsew")

# --- RIGHT SIDE ---
right_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=0)
right_frame.grid(row=0, column=1, sticky="nsew")

# Config inside right frame
right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_rowconfigure(0, weight=1)
right_frame.grid_rowconfigure(1, weight=1)
right_frame.grid_rowconfigure(2, weight=1)
right_frame.grid_rowconfigure(3, weight=1)
right_frame.grid_rowconfigure(4, weight=1)
right_frame.grid_rowconfigure(5, weight=2)  # bottom spacing

title = ctk.CTkLabel(right_frame, text="Get\nStarted", 
                     font=("1FTV HF Gesco", 64), text_color="black")
title.grid(row=1, column=0, pady=(40, 10), sticky="n", justify="left")

subtitle = ctk.CTkLabel(right_frame, text="Start with sign up or sign in",
                        font=("SVN-Gilroy", 24), text_color="black")
subtitle.grid(row=2, column=0, pady=10, sticky="n")

btn_signin = ctk.CTkButton(right_frame, text="SIGN IN", fg_color="#d9d9d9",
                           font =("SVN-Gilroy", 16), 
                           text_color="black", corner_radius=10, height=45)
btn_signin.grid(row=3, column=0, padx=60, pady=10, sticky="n")

btn_signup = ctk.CTkButton(right_frame, text="SIGN UP", fg_color="#d9d9d9",
                           text_color="black", corner_radius=10, height=45)
btn_signup.grid(row=4, column=0, padx=60, pady=10, sticky="n")

skip_label = ctk.CTkLabel(right_frame, text="Continue without login",
                          font=("Arial", 12), text_color="black")
skip_label.grid(row=5, column=0, pady=10, sticky="n")

root.mainloop()
