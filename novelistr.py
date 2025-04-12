#!/usr/bin/env python3

import customtkinter as ctk
from tkinter import filedialog
import tkinter.font as tkFont
import os, json

# ===== INIT ===== #

ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

# ----- Configure App
app = ctk.CTk() # create CTk window like you do with the Tk window
app.title("Novelistr")

# ----- Configure grid layout: 2 rows, 2 columns
app.grid_rowconfigure(1,weight=1)
app.grid_columnconfigure(1, weight=1)

# ----- Global variables
sidebar_expanded = True
sidebar_width = 250
how_recent = 25
current_file = None
recent_label = None

# ----- Functions and logic
def func_new():
	notepad.delete("1.0", "end")
	app.title("Novelistr - new file")

def on_closing():
	if current_file:
		with open(current_file, "w", encoding="utf-8") as f:
			f.write(notepad.get("1.0", "end-1c"))
		print(f"Autosaved to {current_file}")
	app.destroy()

def func_save():
	global current_file
	content = notepad.get("1.0", "end-1c")
	if not current_file:
		file_path = filedialog.asksaveasfilename(
			defaultextension=".txt",
			filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
			title="Save As"
		)
		if file_path:
			with open(file_path, "w", encoding="utf-8") as f:
				f.write(content)
			print(f"Saved to {file_path}")
			current_file = file_path
		else:
			print("Save cancelled.")
	else:
		file_path = current_file
		with open(file_path, "w", encoding="utf-8") as f:
			f.write(content)
	app.title(f"Novelistr - {os.path.basename(file_path)}")
	save_recent_file(file_path)

def func_load():
	global current_file
	file_path = filedialog.askopenfilename(
		defaultextension=".txt",
		filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
		title="Open File"
	)
	if file_path:
		with open(file_path, "r", encoding="utf-8") as f:
			content = f.read()
		notepad.delete("1.0", "end")
		notepad.insert("1.0", content)
		print(f"Loaded from {file_path}")
		current_file = file_path
	else:
		print("Load cancelled.")
	app.title(f"Novelistr - {os.path.basename(file_path)}")
	save_recent_file(file_path)

def collapse_sidebar():
	global sidebar_expanded, sidebar_width
	if sidebar_expanded:
		sidebar.grid_remove()
	else:
		sidebar.grid(row=1, column=0, sticky="ns")
	sidebar_expanded = not sidebar_expanded

def save_recent_file(path):
	try:
		with open(".recent.txt", "r") as f:
			recent = json.load(f)
			if not isinstance(recent, dict):
				recent = {"pinned": [], "recent": []}
	except:
		recent = {"pinned": [], "recent": []}
		
	if path in recent["recent"]:
		recent["recent"].remove(path)
		recent["recent"].insert(0, path)
	elif path not in recent["pinned"]:
		recent["recent"].insert(0, path)

	recent["recent"] = recent["recent"][:how_recent]  # Keep only the last 25
	
	with open(".recent.txt", "w") as f:
		json.dump(recent, f)
	refresh_recent_files()

def refresh_recent_files():
	for widget in recent_files_frame.winfo_children():
		widget.destroy()
	try:
		with open(".recent.txt", "r") as f:
			data = json.load(f)
			if not isinstance(data, dict):
				data = {"pinned": [], "recent": []}
	except:
		data = {"pinned": [], "recent": []}

	pinned = data.get("pinned", [])
	recent = data.get("recent", [])

	def toggle_pin(path):
		if path in pinned:
			pinned.remove(path)
			if path not in recent:
				recent.insert(0, path)
		else:
			pinned.insert(0, path)
			if path in recent:
				recent.remove(path)
		with open(".recent.txt", "w") as f:
			json.dump({"pinned": pinned, "recent": recent}, f)
		refresh_recent_files()

	def add_file_button(path, is_pinned=False):
		if not os.path.exists(path):
			return
		file_row = ctk.CTkFrame(recent_files_frame, fg_color="transparent")
		file_row.pack(fill="x", padx=5, pady=1)

		btn = ctk.CTkButton(
			master=file_row,
			text=os.path.basename(path),
			width=150,
			height=24,
			fg_color="transparent",
			text_color="white",
			anchor="w",
			font=ctk.CTkFont(size=12),
			corner_radius=0,
			command=lambda p=path: open_recent_file(p)
		)
		btn.pack(side="left", fill="x", expand=True)

		pin_btn = ctk.CTkButton(
			master=file_row,
			text="📌" if is_pinned else "📍",
			width=30,
			height=24,
			fg_color="transparent",
			text_color="white",
			font=ctk.CTkFont(size=12),
			command=lambda p=path: toggle_pin(p)
		)
		pin_btn.pack(side="right")

	# Add pinned files first
	for path in pinned:
		add_file_button(path, is_pinned=True)

	# Divider (optional)
	if pinned and recent:
		ctk.CTkLabel(recent_files_frame, text="—", text_color="gray").pack(pady=(5, 2))

	# Then add recent files
	for path in recent:
		add_file_button(path, is_pinned=False)

	clear_button = ctk.CTkButton(
		master=recent_files_frame,
		text="Clear List",
		width=180,
		height=24,
		fg_color="#222222",
		hover_color="#444444",
		text_color="white",
		font=ctk.CTkFont(size=12),
		command=confirm_clear_recent_files
	).pack(pady=8, padx=5)

def open_recent_file(path):
	global current_file
	with open(path, "r", encoding="utf-8") as f:
		content = f.read()
	notepad.delete("1.0", "end")
	notepad.insert("1.0", content)
	current_file = path
	app.title(f"Novelistr - {os.path.basename(path)}")
	try:
		with open(".recent.txt", "r") as f:
			recent = json.load(f)
			if not isinstance(recent, dict):
				recent = {"pinned": [], "recent": []}
	except:
		recent = {"pinned": [], "recent": []}
	if path in recent["recent"]:
		recent["recent"].remove(path)
		recent["recent"].insert(0, path)
	elif path not in recent["pinned"]:
		recent["recent"].insert(0, path)
	recent["recent"] = recent["recent"][:how_recent]  # Keep only the last 25
	with open(".recent.txt", "w") as f:
		json.dump(recent, f)
	refresh_recent_files()

def confirm_clear_recent_files():
	dialog = ctk.CTkToplevel(app)
	dialog.title("Confirm Clear")
	dialog.geometry("300x120")
	ctk.CTkLabel(dialog, text="Clear all recent files?", font=ctk.CTkFont(size=14)).pack(pady=15)
	btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
	btn_frame.pack(pady=5)

	def confirm():
		with open(".recent.txt", "w") as f:
			json.dump({"recent": [], "pinned": []}, f)
		refresh_recent_files()
		dialog.destroy()

	def cancel():
		dialog.destroy()

	ctk.CTkButton(btn_frame, text="Yes", command=confirm, width=80).pack(side="left", padx=10)
	ctk.CTkButton(btn_frame, text="No", command=cancel, width=80).pack(side="right", padx=10)

def toggle_tag(tag_name):
    try:
        start = text_widget.index("sel.first")
        end = text_widget.index("sel.last")

        # Check if tag is already applied
        if tag_name in text_widget.tag_names("sel.first"):
            text_widget.tag_remove(tag_name, start, end)
        else:
            text_widget.tag_add(tag_name, start, end)
    except:
        pass

# ===== UI ===== #

# ----- Toolbar (Top: row=0, spans both columns) -----
toolbar = ctk.CTkFrame(master=app, height=50)
toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")

toggle_button = ctk.CTkButton(toolbar, text="☰", width=40,command=collapse_sidebar)
toggle_button.pack(side="left", padx=10, pady=10)

new_button = ctk.CTkButton(master=toolbar, text="New", width=60, fg_color=toolbar.cget("fg_color"), command=func_new)
new_button.pack(side="left", padx=5, pady=5)

save_button = ctk.CTkButton(master=toolbar, text="Save", width=60, fg_color=toolbar.cget("fg_color"), command=func_save)
save_button.pack(side="left", padx=5, pady=5)

load_button = ctk.CTkButton(master=toolbar, text="Load", width=60, fg_color=toolbar.cget("fg_color"), command=func_load)
load_button.pack(side="left", padx=5, pady=5)

bold_button = ctk.CTkButton(master=toolbar, width=60, fg_color=toolbar.cget("fg_color"), text="Bold", command=lambda: toggle_tag("bold")).pack(side="left", padx=5)
italic_button = ctk.CTkButton(master=toolbar, width=60, fg_color=toolbar.cget("fg_color"), text="Italic", command=lambda: toggle_tag("italic")).pack(side="left", padx=5)
underline_button = ctk.CTkButton(master=toolbar, width=60, fg_color=toolbar.cget("fg_color"), text="Underline", command=lambda: toggle_tag("underline")).pack(side="left", padx=5)
heading_button = ctk.CTkButton(master=toolbar, width=60, fg_color=toolbar.cget("fg_color"), text="Heading", command=lambda: toggle_tag("heading")).pack(side="left", padx=5)

# ----- Sidebar (Left: column=0) -----
sidebar = ctk.CTkFrame(master=app)
sidebar.grid(row=1, column=0, sticky="ns")
recent_label = ctk.CTkLabel(master=sidebar, text="Recent Files:",anchor="w",font=ctk.CTkFont(size=16, weight="bold")).pack(padx=5, pady=5, anchor="w")
filler = ctk.CTkLabel(sidebar, text="", height=1, width=sidebar_width)
filler.pack(side="bottom")
recent_files_frame = ctk.CTkFrame(master=sidebar, fg_color=sidebar.cget("fg_color"))
recent_files_frame.pack(fill="both", expand=False, pady=(2, 0))

# ----- Example label in sidebar
ctk.CTkLabel(sidebar, text="Sidebar Filler").pack(padx=10, pady=10)

# ----- Text area
notepad = ctk.CTkTextbox(master=app, wrap='word')
notepad.grid(row=1, column=1, sticky="nsew")
notepad.focus_set()

# ----- Defining fonts/tags
text_widget = notepad._textbox

bold_font = tkFont.Font(text_widget, text_widget.cget("font"))
bold_font.configure(weight="bold")

italic_font = tkFont.Font(text_widget, text_widget.cget("font"))
italic_font.configure(slant="italic")

underline_font = tkFont.Font(text_widget, text_widget.cget("font"))
underline_font.configure(underline=True)

heading_font = tkFont.Font(text_widget, text_widget.cget("font"))
heading_font.configure(size=18, weight="bold")

# Configure tags
text_widget.tag_configure("bold", font=bold_font)
text_widget.tag_configure("italic", font=italic_font)
text_widget.tag_configure("underline", font=underline_font)
text_widget.tag_configure("heading", font=heading_font)

# ===== Main ===== #
refresh_recent_files()
app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
