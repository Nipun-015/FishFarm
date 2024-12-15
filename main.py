import sys
import os
from tkinter import Tk, Entry, StringVar, Canvas
from tkinter.ttk import Frame, Label, Button
from PIL import Image, ImageTk  # For handling images

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import admin and customer panels


from utils.auth import login_user


def main():
    def login():
        user_id = user_id_var.get()
        password = password_var.get()

        # Validate inputs
        if not user_id or not password:
            feedback_label.config(text="Both User ID and Password are required.", foreground="red")
            return

        # Debug: print entered credentials
        print(f"Attempting login with User ID: {user_id}")

        # Attempt login
        try:
            user_role, is_logged_in = login_user(user_id, password)

            if is_logged_in:
                print(f"Login successful. User role: {user_role}")
                root.destroy()  # Close the login window
                if user_role == "admin":
                    from admin import admin_panel
                    admin_panel()  # Open admin dashboard

                else:
                    from customer import customer_panel
                    customer_panel()  # Open customer dashboard
            
            else:
                feedback_label.config(text="Invalid credentials, please try again.", foreground="red")
        except Exception as e:
            print(f"Error during login: {e}")
            feedback_label.config(text="An error occurred. Please try again.", foreground="red")

    root = Tk()
    root.title("Fish Firm Management")
    root.geometry("1000x800")

    # Canvas for background
    canvas = Canvas(root, width=1000, height=800, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Load and display background image
    try:
        bg_image = Image.open("background.jpg")  # Replace with your background image
        bg_image = bg_image.resize((1000, 800), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    except FileNotFoundError:
        print("Error: 'background.jpg' not found. Please provide a valid image.")

    # Glass panel effect
    canvas.create_rectangle(
        250, 150, 750, 650,
        fill="#ffffff", outline="", stipple="gray25"  # Simulated semi-transparent effect
    )

    # Main Frame for widgets (placed over the glass panel)
    frame = Frame(canvas, padding=20)
    frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame

    # Header
    Label(frame, text="LOGIN", font=("Helvetica", 24, "bold"), foreground="#333").pack(pady=20)

    # Username Entry
    Label(frame, text="User ID", font=("Helvetica", 12), foreground="#333").pack(anchor="w", padx=10, pady=5)
    user_id_var = StringVar()
    user_id_entry = Entry(frame, textvariable=user_id_var, width=30, font=("Helvetica", 14))
    user_id_entry.pack(pady=5)

    # Password Entry
    Label(frame, text="Password", font=("Helvetica", 12), foreground="#333").pack(anchor="w", padx=10, pady=5)
    password_var = StringVar()
    password_entry = Entry(frame, textvariable=password_var, show="*", width=30, font=("Helvetica", 14))
    password_entry.pack(pady=5)

    # Login Button
    Button(frame, text="LOGIN", command=login, width=15).pack(pady=20)

    # Feedback Label
    feedback_label = Label(frame, text="", font=("Helvetica", 10), foreground="red")
    feedback_label.pack()

    root.mainloop()


if __name__ == "__main__":
    main()
