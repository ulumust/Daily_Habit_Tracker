 # # daily habit tracker terminal app project
#maybe can i make somethuink like it: i am gonna couple more questions like that in end
#  i give a point for users day if it was good day example he get healty breakfast 
# then he did exersice then he work enught pomodoro i will commen on the end it was very productivt day
#  you are in the right track keep going or other vise you need improve this and this then you feel good etc what do you think





import datetime

def get_clean_time(prompt):
    while True:
        user_input = input(prompt).strip()

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
        print("Invalid time format. Please enter like 23:00, 23, 23.30")

def ask_yes_no(prompt):
    while True:
        answer = input(prompt + " Yes or No: ").strip().lower()
        if answer == "yes":
            return 1
        elif answer == "no":
            return 0
        else:
            print("Please type 'yes or 'no")

def get_number(prompt):
        while True:
            user_input = input(prompt)
            if user_input.isdigit():
               return int(user_input)
            else:
                print("Please enter a number.")


class HabitTracker:
    def __init__(self):
        self.today = datetime.date.today()
        print("Welcome to the Daily Habit Tracker!")
        self.write_log(f"\n=== {self.today} ===") #date header
        self.total_points = 0 # Initialize total points counter
        self.track_sleep()
        self.morning_walk()
        self.track_breakfast()
        self.pomodoro_log()
        self.junk_food_check()
        self.track_daily_steps()
        self.check_points()
        self.goodbye()

    def write_log(self, entry):
        with open("habit_log.txt", "a", encoding="utf-8") as log:
            log.write(entry + "\n")
            

    def track_sleep(self):
        sleep_time = get_clean_time("What time did you go to bed? (enter example, 23:30 or 23): ")
        wake_time = get_clean_time("What time did you wake up? (enter example 7:30 or 7): ")
        sleep_quality = input("How was quality of your sleep comment!: ")
        self.write_log(f"Sleep log: Bedtime -- {sleep_time} | Wake Time -- {wake_time} | Sleep Quality -- {sleep_quality}")

    def morning_walk(self):
        walk = ask_yes_no("Did you go for a morning walk after waking up?")
        self.total_points += walk
        if walk:
            self.write_log(f"Morning Walk: Walk done👍 +{walk}")
        else:
            self.write_log(f"Morning Walk: None.")

    def track_breakfast(self):
        healthy = ask_yes_no("Did you have a healty breakfast?") 
        self.total_points += healthy
        if healthy:
            self.write_log(f"Breakfast: Healthy👍 +{healthy}")
        else:
            self.write_log(f"Breakfast: None.")

    def pomodoro_log(self):
        pomodoro_done = get_number("How many Pomodoros did you complate today? ")
        if pomodoro_done >= 8:
            self.total_points += 2
        elif pomodoro_done >=4:
            self.total_points += 1
        total_minutes = pomodoro_done * 30
        hours, minutes = divmod(total_minutes, 60)
        self.write_log(f"Pomodoro/Work Done: {pomodoro_done} sessions = {hours}:{minutes:02d} hours of focused work.")

    def check_points(self):
        total = self.total_points
        if total == 7:
            message = "Excellent! You hit all your goals today. 💯"
        elif total >= 4:
            message = "Great job! You're doing very well. 👍"
        elif total >= 2:
            message = "Keep building those habits."
        else:
            message = "Start again never give up!"
        print(f"You got {total}/7 points today! - {message}")
        self.write_log(f"Today's Points: {total}/5 - {message}")

    
    def goodbye(self):
        print("Today's Log saved to habit_log.txt.")


    def junk_food_check(self):
        junk = ask_yes_no("Did you eat junk food today? ")
        if junk:
            what = input("What was it? ")
            self.write_log(f"Junk Food: Yes: {what}")         

        else:
            self.write_log("Junk Food: No")
            self.total_points += 1  
            
    def track_daily_steps(self):
        steps = get_number("How many steps did you do today? ")
        if steps >= 7000:
            self.write_log(f"Steps Done:{steps} great!")
            self.total_points += 2
        elif steps >= 5000:
            self.write_log(f"Steps Done: {steps} minimum!") 
            self.total_points += 1
        else:
            self.write_log(f"Steps Done: {steps} Below average more steps need!")    

        



tracker = HabitTracker()
