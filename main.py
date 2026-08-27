import tkinter as tk
from tkinter import messagebox
import secrets
import string


def generate_password():
    try:
        length = int(length_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Enter a valid password length.")
        return

    if length < 4:
        messagebox.showerror("Error", "Password length must be at least 4.")
        return

    characters = ""

    if uppercase_var.get():
        characters += string.ascii_uppercase

    if lowercase_var.get():
        characters += string.ascii_lowercase

    if numbers_var.get():
        characters += string.digits

    if symbols_var.get():
        characters += string.punctuation

    if not characters:
        messagebox.showerror(
            "Error",
            "Select at least one character type."
        )
        return

    password = "".join(
        secrets.choice(characters)
        for _ in range(length)
    )

    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)


def copy_password():
    password = password_entry.get()

    if not password:
        messagebox.showwarning("Warning", "Generate a password first.")
        return

    root.clipboard_clear()
    root.clipboard_append(password)
    root.update()

    messagebox.showinfo("Copied", "Password copied to clipboard!")


def toggle_password():
    if password_entry.cget("show") == "":
        password_entry.config(show="*")
        show_button.config(text="Show")
    else:
        password_entry.config(show="")
        show_button.config(text="Hide")


# ---------------- GUI ----------------

root = tk.Tk()
root.title("Password Generator")
root.geometry("450x500")
root.resizable(False, False)

title = tk.Label(
    root,
    text="Password Generator",
    font=("Arial", 24, "bold")
)
title.pack(pady=25)

# Password length
length_label = tk.Label(
    root,
    text="Password Length",
    font=("Arial", 12)
)
length_label.pack()

length_entry = tk.Entry(
    root,
    font=("Arial", 14),
    justify="center"
)
length_entry.insert(0, "16")
length_entry.pack(pady=10)

# Options
uppercase_var = tk.BooleanVar(value=True)
lowercase_var = tk.BooleanVar(value=True)
numbers_var = tk.BooleanVar(value=True)
symbols_var = tk.BooleanVar(value=True)

options_frame = tk.Frame(root)
options_frame.pack(pady=10)

tk.Checkbutton(
    options_frame,
    text="Uppercase (A-Z)",
    variable=uppercase_var,
    font=("Arial", 11)
).pack(anchor="w")

tk.Checkbutton(
    options_frame,
    text="Lowercase (a-z)",
    variable=lowercase_var,
    font=("Arial", 11)
).pack(anchor="w")

tk.Checkbutton(
    options_frame,
    text="Numbers (0-9)",
    variable=numbers_var,
    font=("Arial", 11)
).pack(anchor="w")

tk.Checkbutton(
    options_frame,
    text="Symbols (!@#$...)",
    variable=symbols_var,
    font=("Arial", 11)
).pack(anchor="w")

# Generate button
generate_button = tk.Button(
    root,
    text="Generate Password",
    command=generate_password,
    font=("Arial", 13, "bold"),
    width=22,
    height=2
)
generate_button.pack(pady=15)

# Password display
password_entry = tk.Entry(
    root,
    font=("Arial", 14),
    justify="center",
    show="*"
)
password_entry.pack(pady=5, padx=30, fill="x")

# Show/Hide
show_button = tk.Button(
    root,
    text="Show",
    command=toggle_password
)
show_button.pack(pady=5)

# Copy
copy_button = tk.Button(
    root,
    text="Copy Password",
    command=copy_password,
    font=("Arial", 11),
    width=18
)
copy_button.pack(pady=10)

root.mainloop()