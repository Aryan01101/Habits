import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates


class HabitTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Habit Tracker")
        self.master.geometry("800x600")

        self.habits = self.load_habits()
        self.reminders = self.load_reminders()

        self.create_widgets()
        self.check_reminders()

    def create_widgets(self):
        # Notebook for different views
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=1, fill="both")

        # Habits tab
        self.habits_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.habits_frame, text="Habits")

        # Habit input
        self.habit_entry = ttk.Entry(self.habits_frame, width=30)
        self.habit_entry.grid(row=0, column=0, padx=5, pady=5)

        self.difficulty_var = tk.StringVar()
        self.difficulty_var.set("Medium")
        self.difficulty_menu = ttk.OptionMenu(self.habits_frame, self.difficulty_var, "Medium", "Easy", "Medium", "Hard")
        self.difficulty_menu.grid(row=0, column=1, padx=5, pady=5)

        self.add_button = ttk.Button(self.habits_frame, text="Add Habit", command=self.add_habit)
        self.add_button.grid(row=0, column=2, padx=5, pady=5)

        # Habit list
        self.habit_list = ttk.Treeview(self.habits_frame, columns=("Habit", "Streak", "Difficulty"), show="headings")
        self.habit_list.heading("Habit", text="Habit")
        self.habit_list.heading("Streak", text="Streak")
        self.habit_list.heading("Difficulty", text="Difficulty")
        self.habit_list.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        # Complete button
        self.complete_button = ttk.Button(self.habits_frame, text="Mark Complete", command=self.mark_complete)
        self.complete_button.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        # Statistics tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")

        self.stats_text = tk.Text(self.stats_frame, height=20, width=80)
        self.stats_text.pack(padx=10, pady=10)

        # Visualization tab
        self.viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.viz_frame, text="Visualization")

        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Reminders tab
        self.reminders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reminders_frame, text="Reminders")

        self.reminder_habit_var = tk.StringVar()
        self.reminder_habit_menu = ttk.OptionMenu(self.reminders_frame, self.reminder_habit_var, "")
        self.reminder_habit_menu.grid(row=0, column=0, padx=5, pady=5)

        self.reminder_time_entry = ttk.Entry(self.reminders_frame, width=10)
        self.reminder_time_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.reminders_frame, text="Time (HH:MM)").grid(row=0, column=2, padx=5, pady=5)

        self.add_reminder_button = ttk.Button(self.reminders_frame, text="Add Reminder", command=self.add_reminder)
        self.add_reminder_button.grid(row=0, column=3, padx=5, pady=5)

        self.reminders_list = ttk.Treeview(self.reminders_frame, columns=("Habit", "Time"), show="headings")
        self.reminders_list.heading("Habit", text="Habit")
        self.reminders_list.heading("Time", text="Time")
        self.reminders_list.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        self.update_habit_list()
        self.update_reminder_list()
        self.update_stats()
        self.update_visualization()

    def add_habit(self):
        habit = self.habit_entry.get()
        difficulty = self.difficulty_var.get()
        if habit:
            if habit not in self.habits:
                self.habits[habit] = {
                    "streak": 0,
                    "last_completed": None,
                    "history": {},
                    "difficulty": difficulty
                }
                self.save_habits()
                self.update_habit_list()
                self.update_reminder_menu()
                self.habit_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Warning", "This habit already exists.")
        else:
            messagebox.showwarning("Warning", "Please enter a habit.")

    def mark_complete(self):
        selected_item = self.habit_list.selection()
        if selected_item:
            habit = self.habit_list.item(selected_item)["values"][0]
            today = date.today().isoformat()
            if self.habits[habit]["last_completed"] != today:
                self.habits[habit]["streak"] += 1
                self.habits[habit]["last_completed"] = today
                self.habits[habit]["history"][today] = True
                self.save_habits()
                self.update_habit_list()
                self.update_stats()
                self.update_visualization()
            else:
                messagebox.showinfo("Info", "You've already completed this habit today.")
        else:
            messagebox.showwarning("Warning", "Please select a habit to mark as complete.")

    def update_habit_list(self):
        self.habit_list.delete(*self.habit_list.get_children())
        for habit, data in self.habits.items():
            self.habit_list.insert("", "end", values=(habit, data["streak"], data["difficulty"]))

    def load_habits(self):
        try:
            with open("habits.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_habits(self):
        with open("habits.json", "w") as f:
            json.dump(self.habits, f)

    def update_stats(self):
        self.stats_text.delete('1.0', tk.END)
        for habit, data in self.habits.items():
            completion_rate = self.calculate_completion_rate(data['history'])
            longest_streak = self.calculate_longest_streak(data['history'])
            self.stats_text.insert(tk.END, f"Habit: {habit}\n")
            self.stats_text.insert(tk.END, f"Current Streak: {data['streak']}\n")
            self.stats_text.insert(tk.END, f"Longest Streak: {longest_streak}\n")
            self.stats_text.insert(tk.END, f"Completion Rate: {completion_rate:.2f}%\n")
            self.stats_text.insert(tk.END, f"Difficulty: {data['difficulty']}\n\n")

    def calculate_completion_rate(self, history):
        if not history:
            return 0
        total_days = (date.today() - date.fromisoformat(min(history.keys()))).days + 1
        completed_days = sum(history.values())
        return (completed_days / total_days) * 100

    def calculate_longest_streak(self, history):
        streak = 0
        longest_streak = 0
        dates = sorted(history.keys())
        for i, d in enumerate(dates):
            if history[d]:
                streak += 1
                if i == len(dates) - 1 or date.fromisoformat(dates[i+1]) != date.fromisoformat(d) + timedelta(days=1):
                    longest_streak = max(longest_streak, streak)
                    streak = 0
        return longest_streak

    def update_visualization(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        for habit, data in self.habits.items():
            dates = [date.fromisoformat(d) for d in sorted(data['history'].keys())]
            streaks = self.calculate_streaks(data['history'])
            ax.plot(dates, streaks, label=habit, marker='o')

        ax.set_xlabel('Date')
        ax.set_ylabel('Streak')
        ax.set_title('Habit Streaks Over Time')
        ax.legend()

        # Format the date on the x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))  # Show every 5th day
        plt.xticks(rotation=45, ha='right')

        self.fig.tight_layout()
        self.canvas.draw()

    def calculate_streaks(self, history):
        dates = sorted(history.keys())
        streaks = []
        current_streak = 0

        for i, d in enumerate(dates):
            if history[d]:
                current_streak += 1
            else:
                current_streak = 0
            
            streaks.append(current_streak)

            # If it's not the last date, check if the next date is consecutive
            if i < len(dates) - 1:
                next_date = date.fromisoformat(dates[i+1])
                current_date = date.fromisoformat(d)
                if (next_date - current_date).days > 1:
                    # Fill in zeros for missing dates
                    streaks.extend([0] * ((next_date - current_date).days - 1))

        return streaks


    def add_reminder(self):
        habit = self.reminder_habit_var.get()
        time = self.reminder_time_entry.get()
        if habit and time:
            try:
                datetime.strptime(time, "%H:%M")
                self.reminders.append({"habit": habit, "time": time})
                self.save_reminders()
                self.update_reminder_list()
                self.reminder_time_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showwarning("Warning", "Invalid time format. Please use HH:MM.")
        else:
            messagebox.showwarning("Warning", "Please select a habit and enter a time.")

    def update_reminder_list(self):
        self.reminders_list.delete(*self.reminders_list.get_children())
        for reminder in self.reminders:
            self.reminders_list.insert("", "end", values=(reminder["habit"], reminder["time"]))

    def update_reminder_menu(self):
        menu = self.reminder_habit_menu["menu"]
        menu.delete(0, "end")
        for habit in self.habits:
            menu.add_command(label=habit, command=lambda value=habit: self.reminder_habit_var.set(value))

    def load_reminders(self):
        try:
            with open("reminders.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_reminders(self):
        with open("reminders.json", "w") as f:
            json.dump(self.reminders, f)

    def check_reminders(self):
        current_time = datetime.now().strftime("%H:%M")
        for reminder in self.reminders:
            if reminder["time"] == current_time:
                messagebox.showinfo("Reminder", f"Don't forget to complete your habit: {reminder['habit']}")
        self.master.after(60000, self.check_reminders)  # Check every minute

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTracker(root)
    root.mainloop()