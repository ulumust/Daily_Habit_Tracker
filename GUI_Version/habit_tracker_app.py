# Habit_Tracker_app.py
import customtkinter
import os
import sys
import subprocess
import datetime # Added for time comparisons if needed in future, but not strictly for current logic
from habit_tracker_logic import HabitTrackerLogic, get_clean_time, parse_yes_no, parse_number

class HabitTrackerApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. Basic Window Configuration ---
        self.title("Daily Habit Tracker")
        self.geometry("750x650")
        self.resizable(False, False)
        #icon add
        # Check if running as a PyInstaller bundled executable
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # The _MEIPASS attribute holds the path to the temporary folder
            # where PyInstaller extracts bundled files.
            base_path = sys._MEIPASS
        else:
            # If running as a normal Python script, get the current script's directory.
            base_path = os.path.dirname(os.path.abspath(__file__))

        icon_file_name = "log_icon.ico" # Make sure this matches your icon's exact name
        full_icon_path = os.path.join(base_path, icon_file_name)

        # Set the window icon if the file exists
        if os.path.exists(full_icon_path):
            self.iconbitmap(full_icon_path)
        else:
            print(f"Warning: Icon file not found at {full_icon_path}. Using default icon.")
    
        # --- 2. Initialize Backend Logic ---
        self.tracker_logic = HabitTrackerLogic()

        # --- 3. Main Frame Setup ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        for i in range(15): # More rows for a flexible layout
            self.main_frame.grid_rowconfigure(i, weight=1)

        # --- 4. Fixed Header Widgets ---
        self.title_label = customtkinter.CTkLabel(
            self.main_frame,
            text="Welcome to your Daily Habit Tracker!",
            font=customtkinter.CTkFont(size=24, weight="bold"),
            text_color="#F0F0F0"
        )
        self.title_label.grid(row=0, column=0, pady=(20, 10), sticky="n")

        self.description_label = customtkinter.CTkLabel(
            self.main_frame,
            text="Let's log your habits for today.",
            font=customtkinter.CTkFont(size=16),
            text_color="#B0B0B0"
        )
        self.description_label.grid(row=1, column=0, pady=(0, 20), sticky="n")

         # --- 5. Navigation & Feedback Widgets (Dynamically Placed) ---
        # These widgets are created here, but their visibility and position 
        # are managed programmatically later based on the app's current state.
        self.next_button = customtkinter.CTkButton(
            self.main_frame,
            text="Next Step",
            command=self.handle_next_step,
            font=customtkinter.CTkFont(size=16, weight="bold"),
            height=40, corner_radius=10, fg_color="#2E86C1", hover_color="#3498DB"
        )
        self.message_label = customtkinter.CTkLabel(
            self.main_frame,
            text="", font=customtkinter.CTkFont(size=14), text_color="#2ECC71"
        )
        self.start_new_day_button = customtkinter.CTkButton(
            self.main_frame,
            text="Start New Day",
            command=self.start_new_day,
            font=customtkinter.CTkFont(size=14), height=30, corner_radius=8
        )
        self.exit_button = customtkinter.CTkButton(
            self.main_frame,
            text="Exit App",
            command=self.destroy,
            font=customtkinter.CTkFont(size=14), height=30, corner_radius=8,
            fg_color="#C0392B", hover_color="#E74C3C"
        )
        self.show_log_button = customtkinter.CTkButton(
            self.main_frame,
            text="Show Log File",
            command=self.show_log_file,
            font=customtkinter.CTkFont(size=14), height=30, corner_radius=8
        )
        
        # --- 6. Habit-Specific Widgets (ALL HABITS DEFINED HERE) ---

        # 6.1 Sleep Tracking Widgets
        self.bedtime_label = customtkinter.CTkLabel(self.main_frame, text="What time did you go to bed? (e.g., 23:30 or 23):", font=customtkinter.CTkFont(size=14))
        self.bedtime_entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="HH:MM or HH", width=300, corner_radius=8)
        self.waketime_label = customtkinter.CTkLabel(self.main_frame, text="What time did you wake up? (e.g., 7:30 or 7):", font=customtkinter.CTkFont(size=14))
        self.waketime_entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="HH:MM or HH", width=300, corner_radius=8)
        self.sleep_quality_label = customtkinter.CTkLabel(self.main_frame, text="How was the quality of your sleep? (e.g., Good, Restless):", font=customtkinter.CTkFont(size=14))
        self.sleep_quality_entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="Comment on sleep quality", width=300, corner_radius=8)
        self.bedtime_entry.bind("<Return>", lambda event: self.waketime_entry.focus_set())
        self.waketime_entry.bind("<Return>", lambda event: self.sleep_quality_entry.focus_set())
        self.sleep_quality_entry.bind("<Return>", lambda event: self.handle_next_step())

        # 6.2 Morning Walk Widgets
        self.morning_walk_label = customtkinter.CTkLabel(self.main_frame, text="Did you go for a morning walk today?", font=customtkinter.CTkFont(size=14))
        self.morning_walk_var = customtkinter.IntVar(value=-1) # Use IntVar for 0/1 matching logic
        self.morning_walk_yes_radio = customtkinter.CTkRadioButton(self.main_frame, text="Yes", variable=self.morning_walk_var, value=1, command=self.handle_next_step)
        self.morning_walk_no_radio = customtkinter.CTkRadioButton(self.main_frame, text="No", variable=self.morning_walk_var, value=0, command=self.handle_next_step)
        
        # 6.3 Breakfast Widgets
        self.breakfast_label = customtkinter.CTkLabel(self.main_frame, text="Did you have a healthy breakfast?", font=customtkinter.CTkFont(size=14))
        self.breakfast_var = customtkinter.IntVar(value=-1)
        self.breakfast_yes_radio = customtkinter.CTkRadioButton(self.main_frame, text="Yes", variable=self.breakfast_var, value=1, command=self.handle_next_step)
        self.breakfast_no_radio = customtkinter.CTkRadioButton(self.main_frame, text="No", variable=self.breakfast_var, value=0, command=self.handle_next_step)

        # 6.4 Pomodoro / Work Widgets
        self.pomodoro_label = customtkinter.CTkLabel(self.main_frame, text="How many 30-minute Pomodoro sessions did you complete?", font=customtkinter.CTkFont(size=14))
        self.pomodoro_entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="Enter number of sessions", width=300, corner_radius=8)
        self.pomodoro_entry.bind("<Return>", lambda event: self.handle_next_step())

        # 6.5 Junk Food Widgets
        self.junk_food_label = customtkinter.CTkLabel(self.main_frame, text="Did you eat any junk food today?", font=customtkinter.CTkFont(size=14))
        self.junk_food_var = customtkinter.IntVar(value=-1)
        self.junk_food_yes_radio = customtkinter.CTkRadioButton(self.main_frame, text="Yes", variable=self.junk_food_var, value=1, command=self.toggle_junk_food_details)
        self.junk_food_no_radio = customtkinter.CTkRadioButton(self.main_frame, text="No", variable=self.junk_food_var, value=0, command=self.handle_next_step)
        self.what_junk_food_label = customtkinter.CTkLabel(self.main_frame, text="What did you eat?", font=customtkinter.CTkFont(size=12))
        self.what_junk_food_entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="e.g., chips, chocolate", width=300, corner_radius=8)
        self.what_junk_food_entry.bind("<Return>", lambda event: self.handle_next_step())

        #6.6 Daily Steps Widgets
        self.daily_steps_label = customtkinter.CTkLabel(self.main_frame, text="How many steps did you walk today?", font=customtkinter.CTkFont(size=14))
        self.daily_steps_entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="Enter total steps", width=300, corner_radius=8)
        self.daily_steps_entry.bind("<Return>", lambda event: self.handle_next_step())

        # --- 7. Survey/Habit Flow Management Data Structure ---
        # This list defines the sequence of questions, their widgets, validation, and processing logic.
        self.questions_data = [
            # Step 0: Sleep Tracking
            {
                "widgets": [self.bedtime_label, self.bedtime_entry, self.waketime_label, self.waketime_entry, self.sleep_quality_label, self.sleep_quality_entry],
                "grid_configs": [
                    {"widget": self.bedtime_label, "row": 2, "column": 0, "padx": 20, "pady": (10, 5)},
                    {"widget": self.bedtime_entry, "row": 3, "column": 0, "padx": 20, "pady": (0, 10)},
                    {"widget": self.waketime_label, "row": 4, "column": 0, "padx": 20, "pady": (10, 5)},
                    {"widget": self.waketime_entry, "row": 5, "column": 0, "padx": 20, "pady": (0, 10)},
                    {"widget": self.sleep_quality_label, "row": 6, "column": 0, "padx": 20, "pady": (10, 5)},
                    {"widget": self.sleep_quality_entry, "row": 7, "column": 0, "padx": 20, "pady": (0, 20)},
                ],
                "validation_func": self.validate_sleep_inputs,
                "process_func": self.tracker_logic.process_sleep_data,
                "get_values": lambda: (self.bedtime_entry.get(), self.waketime_entry.get(), self.sleep_quality_entry.get()),
                "set_values": lambda b, w, s: (self.bedtime_entry.delete(0, customtkinter.END) or self.bedtime_entry.insert(0, b), # Use 'or' to ensure execution
                                               self.waketime_entry.delete(0, customtkinter.END) or self.waketime_entry.insert(0, w),
                                               self.sleep_quality_entry.delete(0, customtkinter.END) or self.sleep_quality_entry.insert(0, s)),
                "clear_defaults": lambda: (self.bedtime_entry.delete(0, customtkinter.END), self.waketime_entry.delete(0, customtkinter.END), self.sleep_quality_entry.delete(0, customtkinter.END)),
                "auto_advance_on_select": False # For entry fields, user presses enter or next
            },
            # Step 1: Morning Walk
            {
                "widgets": [self.morning_walk_label, self.morning_walk_yes_radio, self.morning_walk_no_radio],
                "grid_configs": [
                    {"widget": self.morning_walk_label, "row": 2, "column": 0, "padx": 20, "pady": (10, 5), "sticky": "ew"},
                    {"widget": self.morning_walk_yes_radio, "row": 3, "column": 0, "padx": 20, "pady": 5, "sticky": "ew"},
                    {"widget": self.morning_walk_no_radio, "row": 4, "column": 0, "padx": 20, "pady": (5, 20), "sticky": "ew"},
                ],
                "validation_func": self.validate_radio_button_selection,
                "process_func": self.tracker_logic.process_morning_walk,
                "get_values": lambda: self.morning_walk_var.get(),
                "set_values": lambda val: self.morning_walk_var.set(val),
                "clear_defaults": lambda: self.morning_walk_var.set(-1), # -1 indicates no selection
                "auto_advance_on_select": True # Radio buttons auto-advance
            },
            # Step 2: Breakfast
            {
                "widgets": [self.breakfast_label, self.breakfast_yes_radio, self.breakfast_no_radio],
                "grid_configs": [
                    {"widget": self.breakfast_label, "row": 2, "column": 0, "padx": 20, "pady": (10, 5), "sticky": "ew"},
                    {"widget": self.breakfast_yes_radio, "row": 3, "column": 0, "padx": 20, "pady": 5, "sticky": "ew"},
                    {"widget": self.breakfast_no_radio, "row": 4, "column": 0, "padx": 20, "pady": (5, 20), "sticky": "ew"},
                ],
                "validation_func": self.validate_radio_button_selection,
                "process_func": self.tracker_logic.process_breakfast_data,
                "get_values": lambda: self.breakfast_var.get(),
                "set_values": lambda val: self.breakfast_var.set(val),
                "clear_defaults": lambda: self.breakfast_var.set(-1),
                "auto_advance_on_select": True
            },
            # Step 3: Pomodoro
            {
                "widgets": [self.pomodoro_label, self.pomodoro_entry],
                "grid_configs": [
                    {"widget": self.pomodoro_label, "row": 2, "column": 0, "padx": 20, "pady": (10, 5), "sticky": "ew"},
                    {"widget": self.pomodoro_entry, "row": 3, "column": 0, "padx": 20, "pady": (0, 20), "sticky": "ew"},
                ],
                "validation_func": self.validate_number_input,
                "process_func": self.tracker_logic.process_pomodoro_data,
                "get_values": lambda: self.pomodoro_entry.get(),
                "set_values": lambda val: (self.pomodoro_entry.delete(0, customtkinter.END) or self.pomodoro_entry.insert(0, str(val))),
                "clear_defaults": lambda: self.pomodoro_entry.delete(0, customtkinter.END),
                "auto_advance_on_select": False
            },
            # Step 4: Junk Food
            {
                "widgets": [self.junk_food_label, self.junk_food_yes_radio, self.junk_food_no_radio, self.what_junk_food_label, self.what_junk_food_entry],
                "grid_configs": [
                    {"widget": self.junk_food_label, "row": 2, "column": 0, "padx": 20, "pady": (10, 5), "sticky": "ew"},
                    {"widget": self.junk_food_yes_radio, "row": 3, "column": 0, "padx": 20, "pady": 5, "sticky": "ew"},
                    {"widget": self.junk_food_no_radio, "row": 4, "column": 0, "padx": 20, "pady": 5, "sticky": "ew"},
                    {"widget": self.what_junk_food_label, "row": 5, "column": 0, "padx": 20, "pady": (10, 5), "sticky": "ew"},
                    {"widget": self.what_junk_food_entry, "row": 6, "column": 0, "padx": 20, "pady": (0, 20), "sticky": "ew"},
                ],
                "validation_func": self.validate_junk_food_input,
                "process_func": self.tracker_logic.process_junk_food_data,
                "get_values": lambda: (self.junk_food_var.get(), self.what_junk_food_entry.get()),
                "set_values": lambda junk_ans, food_desc: (self.junk_food_var.set(junk_ans),
                                                           self.what_junk_food_entry.delete(0, customtkinter.END) or self.what_junk_food_entry.insert(0, food_desc),
                                                           self.toggle_junk_food_details(update_ui_only=True, is_yes=True if junk_ans == 1 else False)), # Ensure visibility
                "clear_defaults": lambda: (self.junk_food_var.set(-1), self.what_junk_food_entry.delete(0, customtkinter.END), self.toggle_junk_food_details(update_ui_only=True, is_yes=False)),
                "auto_advance_on_select": False # Due to conditional entry field
            },
            # Step 5: Daily Steps
            {
                "widgets": [self.daily_steps_label, self.daily_steps_entry],
                "grid_configs": [
                    {"widget": self.daily_steps_label, "row": 2, "column": 0, "padx": 20, "pady": (10, 5), "sticky": "ew"},
                    {"widget": self.daily_steps_entry, "row": 3, "column": 0, "padx": 20, "pady": (0, 20), "sticky": "ew"},
                ],
                "validation_func": self.validate_number_input,
                "process_func": self.tracker_logic.process_daily_steps_data,
                "get_values": lambda: self.daily_steps_entry.get(),
                "set_values": lambda val: (self.daily_steps_entry.delete(0, customtkinter.END) or self.daily_steps_entry.insert(0, str(val))),
                "clear_defaults": lambda: self.daily_steps_entry.delete(0, customtkinter.END),
                "auto_advance_on_select": False
            }
        ]
        self.current_step_index = 0
        
        # --- 8. Initialize GUI Flow ---
        self.hide_all_step_widgets()
        self.display_current_step()

    # --- GUI Flow Management Methods ---

    def hide_all_step_widgets(self):
        """Hides all habit-specific labels and input widgets, and navigation buttons."""
        for step_data in self.questions_data:
            for widget_config in step_data["grid_configs"]:
                widget_config["widget"].grid_forget()
        # Hide conditionally displayed junk food widgets
        self.what_junk_food_label.grid_forget()
        self.what_junk_food_entry.grid_forget()

        self.next_button.grid_forget()
        self.message_label.grid_forget()
        self.start_new_day_button.grid_forget()
        self.exit_button.grid_forget()
        self.show_log_button.grid_forget()
        if hasattr(self, 'summary_label'):
            self.summary_label.grid_forget()

    def display_current_step(self):
        """Displays the habit tracking step corresponding to self.current_step_index."""
        self.hide_all_step_widgets() # Clear previous step from view

        self.title_label.grid(row=0, column=0, pady=(20, 10), sticky="n")
        self.description_label.grid(row=1, column=0, pady=(0, 20), sticky="n")

        if self.current_step_index < len(self.questions_data):
            step_data = self.questions_data[self.current_step_index]

            # Re-grid the specific step's widgets
            for widget_config in step_data["grid_configs"]:
                widget_config["widget"].grid(row=widget_config["row"], column=widget_config["column"],
                                             padx=widget_config["padx"], pady=widget_config["pady"],)
            
            # Restore previously entered answers if available, otherwise clear to default
            # This complex 'if/elif/else' structure is necessary due to varying 'get_values'
            # and 'set_values' lambdas that handle different numbers/types of inputs.
            # We fetch values from tracker_logic.answers dictionary which stores processed data.
            if self.current_step_index == 0: # Sleep data
                b = self.tracker_logic.answers.get('bed_time', '')
                w = self.tracker_logic.answers.get('wake_time', '')
                s = self.tracker_logic.answers.get('sleep_quality', '')
                step_data["set_values"](b, w, s)
            elif self.current_step_index == 1: # Morning walk (integer 0 or 1)
                walk_val_int = self.tracker_logic.answers.get('morning_walk', -1)
                step_data["set_values"](walk_val_int) # IntVar uses 0/1 directly
            elif self.current_step_index == 2: # Breakfast (integer 0 or 1)
                breakfast_val_int = self.tracker_logic.answers.get('healthy_breakfast', -1)
                step_data["set_values"](breakfast_val_int)
            elif self.current_step_index == 3: # Pomodoro (integer)
                pomodoro_val_int = self.tracker_logic.answers.get('pomodoro_done', '')
                step_data["set_values"](pomodoro_val_int) # Set as string into CTkEntry
            elif self.current_step_index == 4: # Junk Food (integer 0 or 1, and string)
                junk_ans_int = self.tracker_logic.answers.get('junk_food', -1)
                food_desc_str = self.tracker_logic.answers.get('what_junk_food', '')
                step_data["set_values"](junk_ans_int, food_desc_str)
            elif self.current_step_index == 5: # Daily Steps (integer)
                steps_val_int = self.tracker_logic.answers.get('daily_steps', '')
                step_data["set_values"](steps_val_int)
            else:
                # Fallback for future steps if they fit a simple single-value restoration
                step_data["clear_defaults"]() 

            # Update button text based on whether it's the last step
            if self.current_step_index == len(self.questions_data) - 1:
                self.next_button.configure(text="Complete Day Log")
            else:
                self.next_button.configure(text="Next Step")

            # Show/hide next button based on auto_advance_on_select flag
            if step_data["auto_advance_on_select"]:
                self.next_button.grid_forget()
            else:
                self.next_button.grid(row=9, column=0, pady=(0, 10))
            self.message_label.grid(row=10, column=0, pady=(5, 10))
            self.show_message("", "green")

        else:
            # All steps completed, proceed to final summary/logging
            self.finalize_day_log_and_display_summary()
   
    def handle_next_step(self):
        """
        Handles validation, data collection, and habit tracking progression.
        Acts as "Next Step" or "Complete Day Log" based on current stage.
        """
        current_step_data = self.questions_data[self.current_step_index]
        
        raw_values = current_step_data["get_values"]()
        validation_result = current_step_data["validation_func"](raw_values)
        
        if not validation_result["is_valid"]:
            self.show_message(validation_result["message"], "red")
            return

        # Process function from logic.py expects individual arguments, so unpack cleaned_data
        current_step_data["process_func"](*validation_result["cleaned_data"])

        self.current_step_index += 1
        self.display_current_step()

    # --- Validation Methods (Return {"is_valid": bool, "message": str, "cleaned_data": tuple}) ---

    def validate_sleep_inputs(self, raw_values):
        """Validates bedtime, waketime, and sleep quality."""
        bedtime_str, waketime_str, sleep_quality_str = raw_values

        cleaned_bedtime = get_clean_time(bedtime_str)
        if cleaned_bedtime is None:
            return {"is_valid": False, "message": "Invalid bedtime. Use HH:MM or HH.", "cleaned_data": None}

        cleaned_waketime = get_clean_time(waketime_str)
        if cleaned_waketime is None:
            return {"is_valid": False, "message": "Invalid wake time. Use HH:MM or HH.", "cleaned_data": None}
        
        if not sleep_quality_str.strip():
            return {"is_valid": False, "message": "Please comment on your sleep quality.", "cleaned_data": None}
        
        return {"is_valid": True, "message": "", "cleaned_data": (cleaned_bedtime, cleaned_waketime, sleep_quality_str.strip())}
   
    def validate_radio_button_selection(self, raw_value):
        """Validates if a radio button (IntVar 0 or 1) has been selected."""
        if raw_value not in [0, 1]:
            return {"is_valid": False, "message": "Please select 'Yes' or 'No'.", "cleaned_data": None}
        return {"is_valid": True, "message": "", "cleaned_data": (raw_value,)} # Pass the int directly

    def validate_number_input(self, raw_value):
        """Validates if input is a non-negative integer."""
        cleaned_num = parse_number(raw_value)
        if cleaned_num is None or cleaned_num < 0:
            return {"is_valid": False, "message": "Please enter a valid positive number.", "cleaned_data": None}
        return {"is_valid": True, "message": "", "cleaned_data": (cleaned_num,)}

    def validate_junk_food_input(self, raw_values):
        """Validates junk food input including the optional description."""
        junk_ans_int, food_desc_str = raw_values
        if junk_ans_int not in [0, 1]:
            return {"is_valid": False, "message": "Please select 'Yes' or 'No' for junk food.", "cleaned_data": None}
        
        if junk_ans_int == 1 and not food_desc_str.strip():
            return {"is_valid": False, "message": "Please specify what junk food you ate.", "cleaned_data": None}
        
        # If no junk food, ensure description is effectively empty for the logic.
        if junk_ans_int == 0:
            food_desc_str = None # Or "" based on what process_junk_food_data handles best for 'None' case

        return {"is_valid": True, "message": "", "cleaned_data": (junk_ans_int, food_desc_str.strip() if food_desc_str else None)}
    
     # --- Helper Method for Junk Food conditional visibility ---
    def toggle_junk_food_details(self, *args, update_ui_only=False, is_yes=None):
        """
        Shows/hides the 'What junk food?' input based on Yes/No radio button selection.
        This is called by the radio button command.
        """
        if not update_ui_only: # If called by user interaction (radio button click)
            selected_value = self.junk_food_var.get()
            if selected_value == 1: # Yes selected
                self.what_junk_food_label.grid(row=5, column=0, padx=20, pady=(10, 5), sticky="w")
                self.what_junk_food_entry.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="w")
            else: # No selected or unselected
                self.what_junk_food_label.grid_forget()
                self.what_junk_food_entry.grid_forget()
                self.what_junk_food_entry.delete(0, customtkinter.END) # Clear content
                if selected_value == 0: # Only auto-advance if 'No' is definitively selected
                    self.handle_next_step()
        else: # If called programmatically (e.g., during display_current_step)
            if is_yes:
                self.what_junk_food_label.grid(row=5, column=0, padx=20, pady=(10, 5), sticky="w")
                self.what_junk_food_entry.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="w")
            else:
                self.what_junk_food_label.grid_forget()
                self.what_junk_food_entry.grid_forget()

     # --- Finalization and App Control Methods ---

    def finalize_day_log_and_display_summary(self):
        """
        Handles final calculations, saving all collected answers to a file,
        and displays the 'Daily Log Completed!' summary screen.
        """
        self.hide_all_step_widgets()

        final_summary_text = self.tracker_logic.get_final_points()
        save_success = self.tracker_logic.write_final_log_to_file()

        self.title_label.configure(text="Daily Log Completed!")
        self.description_label.configure(text="Review your progress below:")
        
        if not hasattr(self, 'summary_label'): # Create only if it doesn't exist
            self.summary_label = customtkinter.CTkLabel(
                self.main_frame,
                text="",
                font=customtkinter.CTkFont(size=18, weight="bold"),
                text_color="#F0F0F0",
                wraplength=600 # Ensure text wraps within the frame
            )
        self.summary_label.configure(text=final_summary_text)
        self.summary_label.grid(row=2, column=0, pady=(10, 20))

        if save_success:
            self.show_message(f"Daily log updated successfully!", "#2ECC71")
        else:
            self.show_message(f"Error saving daily log. Check console for details.", "red")

        self.start_new_day_button.grid(row=9, column=0, pady=(20, 5), padx=5, sticky="e")
        self.show_log_button.grid(row=9, column=0, pady=(20, 5), padx=5, sticky="w")
        self.exit_button.grid(row=10, column=0, pady=(5, 10))
        self.message_label.grid(row=11, column=0, pady=(5, 10))

    def start_new_day(self):
        """Resets the habit tracker state and restarts from the first step."""
        self.tracker_logic.reset_for_new_day()

        self.current_step_index = 0
        self.title_label.configure(text="Welcome to your Daily Habit Tracker!")
        self.description_label.configure(text="Let's log your habits for today.")
        
        if hasattr(self, 'summary_label'):
            self.summary_label.grid_forget()
        
        # Clear all input fields for the new day
        for step_data in self.questions_data:
            step_data["clear_defaults"]()

        self.hide_all_step_widgets()
        self.show_message("", "green")
        self.display_current_step()

    def show_message(self, message, color):
        """Displays a message to the user and clears it after a few seconds."""
        self.message_label.configure(text=message, text_color=color)
        if message:
            self.after(5000, lambda: self.message_label.configure(text=""))

    def show_log_file(self):
        """Opens the habit_log.txt file using the default system application."""
        log_file_path = self.tracker_logic.get_log_file_path()
        try:
            if os.path.exists(log_file_path):
                if os.name == 'nt': # Windows
                    os.startfile(log_file_path)
                elif os.uname().sysname == 'Darwin': # macOS
                    subprocess.run(['open', log_file_path])
                else: # Linux
                    subprocess.run(['xdg-open', log_file_path])
            else:
                self.show_message("Log file not found. Complete a log first!", "orange")
        except Exception as e:
            self.show_message(f"Error opening log file: {e}", "red")
            print(f"Error opening log file: {e}") # Log error to console for debugging

if __name__ == "__main__":
    customtkinter.set_appearance_mode("Dark")
    customtkinter.set_default_color_theme("dark-blue")

    app = HabitTrackerApp()
    app.mainloop()