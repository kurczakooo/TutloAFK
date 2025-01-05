import time
from PIL import ImageGrab
import threading
import pyautogui

class CheckingAndClickingBot():
    def __init__(self):
        self.green_color = (61, 140, 64)
        self.working = False
        self.logs = []
        
    def check_if_calling(self):
        screenshot = ImageGrab.grab(bbox=(self.answer_call_cords[0], self.answer_call_cords[1], self.answer_call_cords[0] + 2, self.answer_call_cords[1] + 100))
        checked_color1 = screenshot.getpixel((0, 0))
        checked_color2 = screenshot.getpixel((0, 30))
        if checked_color1 == self.green_color:
            return 1
        elif checked_color2 == self.green_color:
            return 2
        return 0
    
    def set_answer_call_coords(self, answer_call_cords):
        try:
            self.answer_call_cords = answer_call_cords
        except Exception:
            self.logs.append("Error\nsetting answer call button\nCoords shouldn't be empty\nCoords should both be integers")
        
    def set_close_new_tab_coords(self, close_new_tab_coords):
        try:
            self.close_new_tab_coords = close_new_tab_coords
        except Exception:
            self.logs.append("Error\nsetting close tab button\nCoords shouldn't be empty\nCoords should both be integers")
    
    def start(self):
        if not self.working:
            self.working = True
            self.worker_thread = threading.Thread(target=self.run)
            self.worker_thread.daemon = True
            self.worker_thread.start()
            
    def stop(self):
        if self.working:
            self.working = False
            self.worker_thread.join()
            current_time = time.localtime()
            format_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
            self.logs.append(f'Bot stopped working.\nEnd time: {format_time}\n')
            
    
    def run(self):
        current_time = time.localtime()
        format_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
        self.logs.append(f"Monitoring calls...\nStart time: {format_time}\n")
        try:
            while self.working:
                is_calling = self.check_if_calling()
                if  is_calling > 0:
                    self.logs.append("Answering the call...")
                    
                    time.sleep(0.05)
                    if is_calling == 1:
                        pyautogui.moveTo(x=self.answer_call_cords[0], y=self.answer_call_cords[1])
                    if is_calling == 2:
                        pyautogui.moveTo(x=self.answer_call_cords[0], y=(self.answer_call_cords[1]+30))
                        self.logs.append('--demo lesson--\n')
                    pyautogui.click()

                    time.sleep(0.8)

                    pyautogui.moveTo(x=self.close_new_tab_coords[0], y=self.close_new_tab_coords[1])
                    pyautogui.click(button='middle')
                    time.sleep(0.05)
                    pyautogui.click(button='middle')
                    
                    current_time = time.localtime()
                    format_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                    self.logs.append(f"New tab closed at {format_time}\n")
                    
                time.sleep(1)
                
        except AttributeError:
            self.logs.append("Error\nsetting coords\nCoords shouldn't be empty\nCoords should both be integers")
        except  Exception as e :
            self.logs.append("Running bot error.\nRestart the program")