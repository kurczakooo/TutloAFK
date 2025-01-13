import customtkinter
import threading
import mouse
import time
from checking_and_clicking_bot import CheckingAndClickingBot

#remember to disable antivirus before pyinstaller
#pyinstaller --noconsole main.py

#TO DO
#make a timer to run the program for a certain period of time

class SetCoordinatesFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, id):
        super().__init__(master)
        
        self.id = id
        self.is_updating = False
        self.grid_columnconfigure((0, 1), weight=1)

        self.title_label = customtkinter.CTkLabel(self, text=title)
        self.title_label.grid(row=0, column=0, sticky='ew', columnspan=2, pady=(10, 0), padx=5)
        
        self.entry_x = customtkinter.CTkEntry(self, placeholder_text=" X ")
        self.entry_x.grid(row=1, column=0, sticky='ew', columnspan=1, padx=(5, 5))
        self.entry_y = customtkinter.CTkEntry(self, placeholder_text=" Y ")
        self.entry_y.grid(row=1, column=1, sticky='ew', columnspan=1, padx=(5, 5))

        self.confirm_button = customtkinter.CTkButton(self, text="Set", command=self.track_coords)
        self.confirm_button.grid(row=2, column=0, sticky='ew', columnspan=2, padx=5, pady=(7, 5))
    
    def track_coords(self):
        
        self.entry_x.delete(0, "end")
        self.entry_y.delete(0, "end")
        self.entry_x.insert(0, 'Click anywhere')
        self.entry_y.insert(0, 'to set coords')
        
        if not self.is_updating:
            self.is_updating = True
            
            self.listener_thread = threading.Thread(target=self.monitor_mouse_clicks)
            self.listener_thread.daemon = True
            self.listener_thread.start()

    def monitor_mouse_clicks(self):
        time.sleep(0.5)
        mouse.on_click(lambda: self.save_mouse_position())

    def save_mouse_position(self):
        
        x, y = mouse.get_position()
        self.entry_x.delete(0, "end")
        self.entry_y.delete(0, "end")
        self.entry_x.insert(0, str(x))
        self.entry_y.insert(0, str(y))
        self.is_updating = False
        mouse.unhook_all()
        
        if self.id == 1:
            self.master.bot.set_answer_call_coords((x, y))
        elif self.id == 2:  
            self.master.bot.set_close_new_tab_coords((x, y))




class StartStopFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.elapsed_time = 0
        self.running = False
        self.timer = 99999

        self.grid_columnconfigure((0, 1), weight=1)

        self.title_label = customtkinter.CTkLabel(self, text=f'Elapsed worktime {self.elapsed_time}')
        self.title_label.grid(row=0, column=0, sticky='ew', columnspan=2, pady=(10, 0), padx=5)
        
        self.stop_button = customtkinter.CTkButton(self, text="Stop", command=self.confirm_stop)
        self.stop_button.grid(row=1, column=0, sticky='ew', columnspan=1, padx=(5, 5), pady=(7, 5))
        self.start_button = customtkinter.CTkButton(self, text="Start", command=self.confirm_start)
        self.start_button.grid(row=1, column=1, sticky='ew', columnspan=1, padx=(5, 5), pady=(7, 5))
        
    def confirm_stop(self):
        if self.running:
            self.running = False
            self.master.bot.stop()
        
    def confirm_start(self):
        self.start_time = time.time() - self.elapsed_time
        if not self.running:
            self.running = True
            self.master.bot.start()
            self.listener_thread = threading.Thread(target=self.count_time)
            self.listener_thread.daemon = True
            self.listener_thread.start()
        
    def count_time(self):
        while self.running:
            time.sleep(1)
            elapsed = int(time.time() - self.start_time)
            self.update_time(elapsed)
            
    def update_time(self, new_time):
        new_formatted_time = time.strftime("%H:%M:%S", time.gmtime(new_time))
        self.elapsed_time = new_time
        self.after(0, self.title_label.configure(text=f'Elapsed worktime {new_formatted_time}'), new_formatted_time)
        if(self.elapsed_time >= self.timer):
            self.master.bot.logs.append("Timer reached.")
            self.confirm_stop()





class LogsFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, values, bot):
        super().__init__(master)
        self.values = values
        self.grid_columnconfigure(0, weight=1)
        self.labels = []
        self.create_labels()
        self.bot = bot

    def create_labels(self):
        for label in self.labels:
            label.destroy()

        self.labels = []
        for i, value in enumerate(self.values):
            label = customtkinter.CTkLabel(self, text=value, anchor='w', justify='left')
            label.grid(row=i, column=0, padx=(5, 0), pady=5, sticky='w')
            self.labels.append(label)

    def update_logs(self, new_values):
        self.values = new_values
        self.create_labels()

    def start_log_monitoring(self):
        self.stop_thread = False
        self.monitor_thread = threading.Thread(target=self.monitor_logs)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def monitor_logs(self):
        last_log_length = len(self.bot.logs)
        while not self.stop_thread:
            time.sleep(1)
            current_log_length = len(self.bot.logs)
            if current_log_length > last_log_length:
                self.update_logs(self.bot.logs)
                last_log_length = current_log_length

    def stop_log_monitoring(self):
        self.stop_thread = True
        if self.monitor_thread:
            self.monitor_thread.join()




class TimerFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Timer")
        self.label.grid(row=0, column=0, sticky='ew', columnspan=1, padx=5, pady=(10, 0))

        self.entry_time = customtkinter.CTkEntry(self, placeholder_text="Set timer (minutes) (optional) ")
        self.entry_time.grid(row=1, column=0, sticky='ew', columnspan=1, padx=5)
        
        self.stop_button = customtkinter.CTkButton(self, text="Save", command=self.set_timer)
        self.stop_button.grid(row=2, column=0, sticky='ew', columnspan=1, padx=5, pady=(7,5))
        
    def set_timer(self):
        
        time = self.entry_time.get()
        
        if not time: 
            self.master.bot.logs.append("Timer set : no timer")
        elif not time.isdigit():
            self.master.bot.logs.append("Timer value should be an integer")
        else:
            self.master.bot.logs.append(f"Timer set: {time} min")
            self.time = int(time) * 60
            self.master.start_stop.timer = self.time




class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tutlo afk")
        self.geometry("640x420")
        self.resizable(width=False, height=True)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.bot = CheckingAndClickingBot()

        self.frame1 = SetCoordinatesFrame(self, 'Answer call button coordinates', id=1)
        self.frame1.grid(row=0, column=0, sticky='nsew', columnspan=1, pady=(10, 5), padx=10)
        self.frame2 = SetCoordinatesFrame(self, 'Close new tab button coordinates', id=2)
        self.frame2.grid(row=1, column=0, sticky='nsew', columnspan=1, pady=(10, 5), padx=10)
        self.start_stop = StartStopFrame(self)
        self.start_stop.grid(row=2, column=0, sticky='nsew', columnspan=1, pady=(50, 10), padx=10)
        
        
        self.timer = TimerFrame(self)
        self.timer.grid(row=0, column=1, sticky='nsew', columnspan=1, padx=(5, 10), pady=(10, 5))
        
        self.logs_frame=LogsFrame(self, values=self.bot.logs, bot=self.bot)
        self.logs_frame.grid(row=1, column=1, sticky='nsew', rowspan=2, columnspan=1, pady=10, padx=(5, 10))
        
        self.logs_frame.start_log_monitoring()

if __name__ == "__main__":
    app = App()
    app.mainloop()
