#!/usr/bin/env python3

from tkinter import PhotoImage
import customtkinter as ctk
import tkinter.font as tkFont
from tkinter import filedialog
from pathlib import Path
import os, json, re, sys, platform

def main():
	# ===== Functions and Logic ===== #
	#Application-wide behaviors & additional set up
	def bind_and_block(action): #Disables non-standard keybind behaviors
		return lambda e: (action(), "break")[1] 
		#Surprisingly, a bunch of the 'normal' keybinds have non-standard default behavior
		#inside the text box element. This function disables the non-standard behaviors

	def on_closing(): #autosave on close
		save_file()
		app.destroy()

	def select_all():
		notepad.tag_add("sel", "1.0", "end-1c")

	def setup_keybinds(notepad):
		os_name = platform.system()
		if os_name == "Darwin": # Mac needs command based keybinds
			notepad.bind("<Command-n>", bind_and_block(lambda: func_new()))
			notepad.bind("<Command-s>", bind_and_block(lambda:save_file()))
			notepad.bind("<Command-o>", bind_and_block(lambda:load_file()))
			notepad.bind("<Command-a>", bind_and_block(lambda:select_all()))
			notepad.bind("<Command-m>", bind_and_block(lambda:key_toggle_format()))
			notepad.bind("<Command-z>", lambda event: notepad.edit_undo())
			notepad.bind("<Command-y>", lambda event: notepad.edit_redo())
			notepad.bind("<Command-b>", bind_and_block(lambda:toggle_tag("bold")))
			notepad.bind("<Command-i>", bind_and_block(lambda:toggle_tag("italic")))
			notepad.bind("<Command-u>", bind_and_block(lambda:toggle_tag("underline")))
			notepad.bind("<Command-h>", bind_and_block(lambda:toggle_tag("heading")))
		else: #Linux and windows want ctrl; and bind_all is bad for windows
			notepad.bind("<Control-n>", bind_and_block(lambda: func_new()))
			notepad.bind("<Control-s>", bind_and_block(lambda:save_file()))
			notepad.bind("<Control-o>", bind_and_block(lambda:load_file()))
			notepad.bind("<Control-a>", bind_and_block(lambda:select_all()))
			notepad.bind("<Control-m>", bind_and_block(lambda:key_toggle_format()))
			notepad.bind("<Control-z>", lambda event: notepad.edit_undo())
			notepad.bind("<Control-y>", lambda event: notepad.edit_redo())
			notepad.bind("<Control-b>", bind_and_block(lambda:toggle_tag("bold")))
			notepad.bind("<Control-i>", bind_and_block(lambda:toggle_tag("italic")))
			notepad.bind("<Control-u>", bind_and_block(lambda:toggle_tag("underline")))
			notepad.bind("<Control-h>", bind_and_block(lambda:toggle_tag("heading")))

	#Top toolbar and its related functions

	def func_new(): #New File button
		dialog = ctk.CTkToplevel(app)
		dialog.title("Confirm New File")
		dialog.geometry("300x120")
		ctk.CTkLabel(dialog, text="Really Start a New File?", font=ctk.CTkFont(size=14)).pack(pady=15)
		btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
		btn_frame.pack(pady=5)

		def confirm():
			notepad.delete("1.0", "end")
			app.title(app_title)
			current_file = None
			update_status_label()
			dialog.destroy()

		def cancel():
			dialog.destroy()

		ctk.CTkButton(btn_frame, text="Yes", command=confirm, width=80).pack(side="left", padx=10)
		ctk.CTkButton(btn_frame, text="No", command=cancel, width=80).pack(side="right", padx=10)

	def save_file(): #Save File Button
		nonlocal current_file, last_saved_content, current_app_title
		mode = format_mode.get()
		content = notepad.get("1.0", "end-1c")
		if content != "":
			if mode == "Plaintext":
				content = notepad.get("1.0", "end-1c")
				extension = ".txt"
				file_types = [("Text Files", "*.txt"), ("All Files", "*.*")]
			elif mode == "Formatted":
				content = convert_to_md()
				extension = ".md"
				file_types = [("Markdown Files", "*.md"), ("All Files", "*.*")]
			if not current_file:
				file_path = filedialog.asksaveasfilename(
					defaultextension=extension,
					filetypes=file_types,
					title="Save As"
				)
				if file_path:
					with open(file_path, "w", encoding="utf-8") as f:
						f.write(content)
					print(f"Saved to {file_path}")
					current_file = file_path
					current_app_title = f"Novelistr - {os.path.basename(file_path)}"
					app.title(current_app_title)
					save_recent_file(file_path)
				else:
					print("Save cancelled.")
			else:
				file_path = current_file
				with open(file_path, "w", encoding="utf-8") as f:
					f.write(content)
				current_file = file_path
				current_app_title = f"Novelistr - {os.path.basename(file_path)}"
				app.title(current_app_title)
			last_saved_content = content
			saved_label.configure(text="Saved")

	def autosave(): #Autosave feature
		nonlocal last_saved_content, current_file
		if current_file:
			content = notepad.get("1.0", "end-1c")
			if content != last_saved_content:
				save_file()
			app.after(autosave_interval, autosave)

	def load_file(): #Load File Button
		nonlocal current_file, last_saved_content, current_app_title
		mode = format_mode.get()
		if mode == "Plaintext":
			extension = ".txt"
			file_types = [("Text Files", "*.txt"), ("All Files", "*.*")]
		elif mode == "Formatted":
			extension = ".md"
			file_types = [("Markdown Files", "*.md"), ("All Files", "*.*")]
		file_path = filedialog.askopenfilename(
			defaultextension=extension,
			filetypes=file_types,
			title="Open File"
		)
		if file_path:
			with open(file_path, "r", encoding="utf-8") as f:
				content = f.read()
			notepad.delete("1.0", "end")
			notepad.insert("1.0", content)
			if mode == "Formatted":
				format_from_md()
			last_saved_content = notepad.get("1.0", "end-1c")
			print(f"Loaded from {file_path}")
			current_file = file_path
			current_app_title = f"Novelistr - {os.path.basename(file_path)}"
			app.title(current_app_title)
			save_recent_file(file_path)
			ext = os.path.splitext(file_path)[1].lower()
			if ext == ".md":
				format_mode.set("Formatted")
			else:
				format_mode.set("Plaintext")
		else:
			print("Load cancelled.")
		update_status_label()
		notepad.edit_reset()

	def convert_to_md(): #plaintext-formatted >> MD, used in saving & mode-toggling
		content = notepad.get("1.0", "end-1c")
		output = list(content)
		tag_priority = ["heading", "bold", "italic", "underline"]

		def index_to_offset(widget, index):
			lines = widget.get("1.0", index).splitlines(True)
			return sum(len(line) for line in lines)

		insertions = []  # Collect tuples of (offset, string)

		for tag in tag_priority:
			ranges = notepad.tag_ranges(tag)
			for i in range(0, len(ranges), 2):
				start = ranges[i]
				end = ranges[i + 1]

				start_idx = notepad.index(start)
				end_idx = notepad.index(end)

				start_offset = index_to_offset(notepad, start_idx)
				end_offset = index_to_offset(notepad, end_idx)

				# Tag-to-markdown syntax
				if tag == "bold":
					insertions.append((start_offset, "**"))
					insertions.append((end_offset, "**"))
				elif tag == "italic":
					insertions.append((start_offset, "*"))
					insertions.append((end_offset, "*"))
				elif tag == "underline":
					insertions.append((start_offset, "_"))
					insertions.append((end_offset, "_"))
				elif tag == "heading":
					line_start = notepad.index(f"{start_idx} linestart")
					if line_start == start_idx:
						insertions.append((start_offset, "# "))

		# Sort insertions in reverse so they don't affect each other's offsets
		for offset, string in sorted(insertions, key=lambda x: -x[0]):
			output.insert(offset, string)

		return "".join(output)

	def format_from_md(): #MD >> plaintext-formatted, used in loading & mode-toggling
		notepad.edit_separator()
		content = notepad.get("1.0", "end-1c")

		# Patterns and tag names
		patterns = {
			"bold": r"\*\*(.*?)\*\*",
			"italic": r"\*(.*?)\*",
			"underline": r"_(.*?)_",
			"heading": r"^# (.*?)$"
		}

		for tag, pattern in patterns.items():
			for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
				start_char = match.start(1)
				end_char = match.end(1)

				start_index = f"1.0 + {start_char} chars"
				end_index = f"1.0 + {end_char} chars"

				notepad.tag_add(tag, start_index, end_index)

		formatting_marks = ["**", "# ", "*", "_"]

		for marks in formatting_marks:
			start = "1.0" # start from the bottem
			while True:
				pos = notepad.search(marks, start, stopindex="end", regexp=False)
				if not pos:
					break #gtfo
				end = f"{pos} + {len(marks)}c"
				notepad.delete(pos, end)
				start = pos  # now we're here
		notepad.edit_separator()

	def toggle_tag(tag_name): #The formatting buttons: Bold, Italic, Underline, Heading and applying them to the text
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

	def update_font_size(choice): #Font size; unused
		new_font = ctk.CTkFont(family="Roboto", size=int(choice))
		notepad.configure(font=new_font)

	def scratch_formatting(): #Unused
		content = notepad.get("1.0", "end-1c")

		formatting_marks = ["**", "# ", "*", "_"]

		for marks in formatting_marks:
			start = "1.0" # start from the bottem
			while True:
				pos = notepad.search(marks, start, stopindex="end", regexp=False)
				if not pos:
					break #gtfo
				end = f"{pos} + {len(marks)}c"
				notepad.delete(pos, end)
				start = pos  # now we're here

	def key_toggle_format(): #keybind for mode-toggling
		mode = format_mode.get()
		if mode == "Formatted":
			format_mode.set("Plaintext")
		else:
			format_mode.set("Formatted")
		toggle_format_button()

	def toggle_format_button(): #The plaintext/formatted mode toggle switch
		mode = format_mode.get()
		if mode == "Formatted":
			format_from_md()
		else:
			notepad.edit_separator()
			content = convert_to_md()
			notepad.delete("1.0", "end")
			notepad.insert("1.0", content)
			notepad.edit_separator()
		update_status_label()

	#Left sidebar and its related functions

	def collapse_sidebar(): #Hamburger button
		nonlocal sidebar_expanded, sidebar_width
		if sidebar_expanded:
			sidebar.grid_remove()
		else:
			sidebar.grid(row=1, column=0, sticky="ns")
		sidebar_expanded = not sidebar_expanded

	def save_recent_file(path): #Save the recent files list, then calls refresh_recent_files()
		nonlocal recent_file
		try:
			with open(recent_file, "r") as f:
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
		
		with open(recent_file, "w") as f:
			json.dump(recent, f)
		refresh_recent_files()

	def refresh_recent_files(): #Refreshes the display of the recent files list
		nonlocal recent_file
		for widget in recent_files_frame.winfo_children():
			widget.destroy()
		try:
			with open(recent_file, "r") as f:
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
			with open(recent_file, "w") as f:
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

	def open_recent_file(path): #When selecting a recent file, load the file, update the list
		nonlocal current_file, last_saved_content, current_app_title, recent_file
		save_file()
		ext = os.path.splitext(path)[1].lower()
		if ext == ".md":
			format_mode.set("Formatted")
		else:
			format_mode.set("Plaintext")
		with open(path, "r", encoding="utf-8") as f:
			content = f.read()
		notepad.delete("1.0", "end")
		notepad.insert("1.0", content)
		last_saved_content = content
		mode = format_mode.get()
		if mode == "Formatted":
			format_from_md()
		current_file = path
		current_app_title = f"Novelistr - {os.path.basename(path)}"
		app.title(current_app_title)
		try:
			with open(recent_file, "r") as f:
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
		with open(recent_file, "w") as f:
			json.dump(recent, f)
		refresh_recent_files()
		update_status_label()
		notepad.edit_reset()

	def confirm_clear_recent_files(): #Confirms and clears the recent file list
		dialog = ctk.CTkToplevel(app)
		dialog.title("Confirm Clear")
		dialog.geometry("300x120")
		ctk.CTkLabel(dialog, text="Clear all recent files?", font=ctk.CTkFont(size=14)).pack(pady=15)
		btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
		btn_frame.pack(pady=5)

		def confirm():
			with open(recent_file, "w") as f:
				json.dump({"recent": [], "pinned": []}, f)
			refresh_recent_files()
			dialog.destroy()

		def cancel():
			dialog.destroy()

		ctk.CTkButton(btn_frame, text="Yes", command=confirm, width=80).pack(side="left", padx=10)
		ctk.CTkButton(btn_frame, text="No", command=cancel, width=80).pack(side="right", padx=10)

	def update_reports(): #Update status indicators
		update_status_label()
		update_saved_label()

	def update_status_label(): #Line or Word count, depending on formatted/plaintext mode
		content = notepad.get("1.0", "end-1c")
		mode = format_mode.get()
		if mode == "Formatted":
			# Word count for markdown/visual
			word_count = len(content.split())
			status_label.configure(text=f"Word count: {word_count}")
		else:
			# Line count for plaintext
			line_count = int(notepad.index("end-1c").split(".")[0])
			status_label.configure(text=f"Line count: {line_count}")

	def update_saved_label(): #Saved/Unsaved/Autosaved label
		nonlocal last_saved_content, current_app_title
		content = notepad.get("1.0", "end-1c")
		if content != last_saved_content:
			saved_label.configure(text="Unsaved")
			if " *" not in current_app_title:
				current_app_title += " *"
				app.title(current_app_title)
		else:
			saved_label.configure(text="Saved")

	# ===== INIT ===== #
	app_data_dir = Path.home() / ".novelistr"
	app_data_dir.mkdir(exist_ok=True)
	recent_file = app_data_dir / "recent.json"
	#Build/PyInstaller Help
	if getattr(sys, 'frozen', False):
		BASE_DIR = Path(sys._MEIPASS)
	else:
		BASE_DIR = Path(__file__).parent
	icon_path = BASE_DIR / "assets" / "icon_32x32.png"
	#Configure App
	app = ctk.CTk() # create CTk window like you do with the Tk window
	app.title("Novelistr")
	app.geometry("1280x800")
	app.minsize(800, 600)
	app.iconphoto(True, PhotoImage(file=icon_path))  # cross-platform
	#Application Theming
	ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
	ctk.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green
	#Configure grid layout: 2 rows, 2 columns
	app.grid_rowconfigure(1,weight=1)
	app.grid_columnconfigure(1, weight=1)
	#nonlocal variables
	sidebar_expanded = True
	sidebar_width = 250
	how_recent = 25
	current_file = None
	recent_label = None
	last_saved_content = None
	app_title = "Novelistr"
	current_app_title = app_title
	autosave_minutes = 1
	autosave_interval = autosave_minutes * 60 * 1000
	font_size_var = ctk.StringVar(value="14")

	# ===== UI ===== #

	#Toolbar (Top: row=0, spans both columns), and related buttons
	toolbar = ctk.CTkFrame(master=app, height=50)
	toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")
	#Hamburger button
	toggle_button = ctk.CTkButton(toolbar, text="☰", width=40,command=collapse_sidebar)
	toggle_button.pack(side="left", padx=10, pady=10)
	#File management buttons
	new_button = ctk.CTkButton(master=toolbar, text="New", width=60, fg_color=toolbar.cget("fg_color"), command=func_new)
	new_button.pack(side="left", padx=5, pady=5)
	save_button = ctk.CTkButton(master=toolbar, text="Save", width=60, fg_color=toolbar.cget("fg_color"), command=save_file)
	save_button.pack(side="left", padx=5, pady=5)
	load_button = ctk.CTkButton(master=toolbar, text="Load", width=60, fg_color=toolbar.cget("fg_color"), command=load_file)
	load_button.pack(side="left", padx=5, pady=5)
	#Formatting buttons
	bold_button = ctk.CTkButton(master=toolbar, width=60, fg_color=toolbar.cget("fg_color"), text="Bold", command=lambda: toggle_tag("bold")).pack(side="left", padx=5)
	italic_button = ctk.CTkButton(master=toolbar, width=60, fg_color=toolbar.cget("fg_color"), text="Italic", command=lambda: toggle_tag("italic")).pack(side="left", padx=5)
	underline_button = ctk.CTkButton(master=toolbar, width=60, fg_color=toolbar.cget("fg_color"), text="Underline", command=lambda: toggle_tag("underline")).pack(side="left", padx=5)
	heading_button = ctk.CTkButton(master=toolbar, width=60, fg_color=toolbar.cget("fg_color"), text="Heading", command=lambda: toggle_tag("heading")).pack(side="left", padx=5)
	#font_menu = ctk.CTkOptionMenu(master=toolbar,variable=font_size_var,values=["12", "14", "16", "18", "20", "24", "28"],command=update_font_size).pack(side="left", padx=5)
	#Plaintext/Formatted toggle switch, all the way on the right
	format_mode = ctk.StringVar(value="Plaintext")
	format_toggle = ctk.CTkSegmentedButton(master=toolbar, values=["Plaintext", "Formatted"], variable=format_mode)
	format_toggle.pack(side="right", padx=5, pady=5)
	format_mode.trace_add("write", lambda *args: toggle_format_button())

	#Sidebar (Left: column=0), related buttons/data
	sidebar = ctk.CTkFrame(master=app)
	sidebar.grid(row=1, column=0, sticky="ns")
	#Recent Files List
	recent_label = ctk.CTkLabel(master=sidebar, text="Recent Files:",anchor="w",font=ctk.CTkFont(size=16, weight="bold")).pack(padx=5, pady=5, anchor="w")
	filler = ctk.CTkLabel(sidebar, text="", height=1, width=sidebar_width)
	filler.pack(side="bottom")
	recent_files_frame = ctk.CTkFrame(master=sidebar, fg_color=sidebar.cget("fg_color"))
	recent_files_frame.pack(fill="both", expand=False, pady=(2, 0))
	#Sidebar labels
	status_label = ctk.CTkLabel(master=sidebar, text="Line count: 0")
	status_label.pack(side="bottom", padx=10, pady=5)
	saved_label = ctk.CTkLabel(master=sidebar, text="Saved")
	saved_label.pack(side="bottom", padx=10, pady=5)

	#Text area
	notepad = ctk.CTkTextbox(master=app, undo=True, wrap='word')
	notepad.grid(row=1, column=1, sticky="nsew")
	notepad.focus_set()
	default_font = ctk.CTkFont(family="Roboto", size=int(font_size_var.get()))
	notepad.configure(font=default_font)
	notepad.bind("<KeyRelease>", lambda event: app.after_idle(update_reports))
	setup_keybinds(notepad)

	# ===== Text Area Fromatting ===== #
	text_widget = notepad._textbox
	#bold
	bold_font = tkFont.Font(text_widget, text_widget.cget("font"))
	bold_font.configure(weight="bold")
	#italic
	italic_font = tkFont.Font(text_widget, text_widget.cget("font"))
	italic_font.configure(slant="italic")
	#underline
	underline_font = tkFont.Font(text_widget, text_widget.cget("font"))
	underline_font.configure(underline=True)
	#heading
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
	app.after(autosave_interval, autosave)
	app.mainloop()

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		import traceback
		with open("error.log", "w") as f:
			f.write(traceback.format_exc())
		raise