import datetime
import os
import sys

# --- Helper Functions (Adapted for GUI) ---

def get_clean_time(user_input):
    """
    Parses a time string into HH:MM format.
    Returns the formatted time string if valid, None otherwise.
    No longer prompts or prints errors.
    """
    user_input = user_input.strip()
    # Handle 4-digit time like "2311" => "23:11"
    if len(user_input) == 4 and user_input.isdigit():
        user_input = user_input[:2] + ":" + user_input[2:]
    # Try multiple formats 
    for fmt in ("%H:%M", "%H", "%H.%M"):
        try:
            parsed = datetime.datetime.strptime(user_input, fmt)
            return parsed.strftime("%H:%M")
        except ValueError:
            continue
    return None # Return None if no valid format is found

def parse_yes_no(answer):
    """
    Parses a yes/no string.
    Returns 1 for 'yes', 0 for 'no', and None for invalid input.
    """
    answer = answer.strip().lower()
    if answer == "yes":
        return 1
    elif answer == "no":
        return 0
    else:
        return None # indicate invalid input
    
def parse_number(user_input):
    """
    Parses a string into an integer.
    Returns the integer if valid, None otherwise.
    """
    user_input = user_input.strip()
    if user_input.isdigit():
        return int(user_input)
    else:
        return None 

class HabitTrackerLogic:
    def __init__(self):
        self.today = datetime.date.today()
        self.total_points = 0
        self.log_entries = [] # Store log entries internally, to be written at the end.
        self.answers = {} # Dictionary to store all collected answers by their key.

        self.log_file_name = "habit_log.txt" # Define the name of your log file

        # Determine the base directory for the log file
        if getattr(sys, 'frozen', False):
            # If running as a PyInstaller bundle, use the directory of the executable
            # sys.executable gives the path to the .exe file itself
            self.log_base_dir = os.path.dirname(sys.executable)
        else:
            # If running as a regular Python script, use the script's directory
            # __file__ points to the current script file
            self.log_base_dir = os.path.dirname(os.path.abspath(__file__))

        # Combine the base directory and file name to get the full path
        self.log_path = os.path.join(self.log_base_dir, self.log_file_name)
        
        # Add the date header to the internal log entries when initialized
        self.log_entries.append(f"\n=== {self.today} ===")

    def add_log_entry(self, entry):
        """Helper to add an entry to the internal log list."""
        self.log_entries.append(entry)

    def write_final_log_to_file(self):
        """
        Writes all accumulated log entries to the habit_log.txt file.
        This will be called ONCE by the GUI at the very end.
        """
        log_file_path = self.log_path
        today_header = f"=== {self.today} ==="
        existing_log_lines = []
        try:
            if os.path.exists(log_file_path):
                with open(log_file_path, "r", encoding="utf-8") as f:
                    existing_log_lines = f.readlines()
        except Exception as e:
            print(f"Error reading existing log file: {e}")
            return False   
        # Prepare new log content (including the header for today)
        new_day_content_lines = [entry + "\n" for entry in self.log_entries] # Add newline for each entry
        # Find where today's previous entries (if any) start and end
        start_index = -1
        end_index = -1
        for i, line in enumerate(existing_log_lines):
            if today_header in line:
                start_index = i
            # Find the next date header after today's header to determine end_index
            # This logic assumes headers always start with "===" and are on their own line
            elif start_index != -1 and line.strip().startswith("===") and i > start_index:
                end_index = i
                break

        # Construct the final log content
        final_log_lines = []
        if start_index != -1:
            # If today's entries were found, add lines before and after them
            final_log_lines.extend(existing_log_lines[:start_index])
            final_log_lines.extend(new_day_content_lines) # Add the new, updated content for today
            if end_index != -1:
                final_log_lines.extend(existing_log_lines[end_index:])
            # If start_index was found but no next header, it means today is the last entry
            # In this case, existing_log_lines[end_index:] would be empty, which is correct.
        else:
            # If today's header was NOT found, append new day's content to the end
            final_log_lines.extend(existing_log_lines) # Keep all previous lines
            final_log_lines.extend(new_day_content_lines) # Add new content for today

        try:
            # Step 5: Write the entire modified content back to the file (overwriting)
            with open(log_file_path, "w", encoding="utf-8") as log: # Notice "w" (write) mode!
                log.writelines(final_log_lines) # writelines expects a list of strings
            return True # Indicate success
        except Exception as e:
            print(f"Error writing final log file: {e}")
            return False

    # ... (your get_final_points_summary and reset_for_new_day methods) ...

     # --- Habit Tracking Methods (Adapted for GUI - Accept data, return results) ---
    def process_sleep_data(self, bedtime, waketime, sleep_quality):
        """
        Processes sleep data, calculates points, and prepares log entry.
        Assumes inputs are already validated by the GUI.
        """
        self.answers["bed_time"] = bedtime
        self.answers["wake_time"] = waketime
        self.answers["sleep_quality"] = sleep_quality
        self.add_log_entry(f"Sleep log: Bedtime -- {bedtime} | Wake Time -- {waketime} | Sleep Quality -- {sleep_quality}")    

    def process_morning_walk(self, walk_answer):
        """
        Processes morning walk data, calculates points, and prepares log entry.
        walk_answer should be 1 for yes, 0 for no.
        """
        self.answers["morning_walk"] = walk_answer
        if walk_answer == 1:
            self.total_points += 1
            self.add_log_entry(f"Morning Walk: Walk done👍 +1")
        else:
            self.add_log_entry(f"Morning Walk: None.")

    def process_breakfast_data(self, breakfast_answer):
        """
        Processes breakfast data, calculates points, and prepares log entry.
        breakfast_answer should be 1 for yes, 0 for no.
        """
        self.answers["healthy_breakfast"] = breakfast_answer
        if breakfast_answer == 1:
            self.total_points += 1
            self.add_log_entry(f"Breakfast: Healthy👍 +1")
        else:
            self.add_log_entry(f"Breakfast: None.")


    def process_pomodoro_data(self, pomodoro_done):
        """
        Processes pomodoro data, calculates points, and prepares log entry.
        """
        self.answers["pomodoro_done"] = pomodoro_done
        if pomodoro_done >= 8:
            self.total_points += 2
        elif pomodoro_done >= 4:
            self.total_points += 1
        total_minutes = pomodoro_done * 30
        hours, minutes = divmod(total_minutes, 60)
        self.add_log_entry(f"Pomodoro/Work Done: {pomodoro_done} sessions = {hours}:{minutes:02d} hours of focused work.")

    def process_junk_food_data(self, junk_answer, what_junk_food=None):
        """
        Processes junk food data, calculates points, and prepares log entry.
        junk_answer_int should be 1 for yes, 0 for no.
        what_junk_food_str is optional if junk_answer_int is 1.
        """
        self.answers["junk_food"] = junk_answer
        self.answers["what_junk_food"] = what_junk_food
        if junk_answer == 1:
            self.add_log_entry(f"Junk Food: Yes: {what_junk_food}")
        else:
            self.add_log_entry("Junk Food: No")
            self.total_points += 1 

    def process_daily_steps_data(self, steps):
        self.answers["daily_steps"] = steps
        message = ""
        if steps >= 7000:
            message = "great!"
            self.total_points += 2
        elif steps >= 5000:
            message = "minimum!"
            self.total_points += 1
        else:
            message = "Below average more steps need!"
        self.add_log_entry(f"Steps Done:{steps} {message}")

    def get_final_points(self):   
        total = self.total_points
        message = ""
        if total == 7:
            message = "Excellent! You hit all your goals today. 💯"
        elif total >= 4:
            message = "Great job! You're doing very well. 👍"
        elif total >= 2:
            message = "Keep building those habits."
        else:
            message = "Start again never give up!"
        self.add_log_entry(f"Today's Points: {total}/7 - {message}")
        return f"You got {total}/7 points today! - {message}"
                
    def get_full_log_content(self):
        """Returns the complete log content as a single string."""
        return "\n".join(self.log_entries)
    
    def reset_for_new_day(self):
        """Resets all internal state for a new day's tracking."""
        self.today = datetime.date.today()
        self.total_points = 0
        self.log_entries = [f"\n=== {self.today} ==="] # Start new log with new date
        self.answers = {} # Clear all stored answers

    def get_log_file_path(self):
    # This logic can be extracted and reused
        return self.log_path