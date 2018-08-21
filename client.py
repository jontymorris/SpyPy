from PIL import ImageGrab, Image
from threading import Thread
from time import sleep
from io import StringIO
import pyautogui, socket, json, pickle


class ControllerHandler:
    ''' This acts as a gateway for interacting with the controller '''

    def __init__(self, address):
        self.event_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.event_socket.bind((address, 5790))

        self.image_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.image_socket.bind((address, 5791))

        self.event_thread = Thread(target=self.event_handler)
        self.event_thread.start()

        self.image_handler()
    
    def image_handler(self):
        self.image_socket.listen(1)
        delimiter = "\n\n".encode("utf-8")

        while True:
            conn, address = self.image_socket.accept()
            
            try:
                while True:
                    screenshot = get_screenshot()
                    data = pickle.dumps(screenshot)
                    
                    conn.send(data)
                    conn.send(delimiter)
                    
                    sleep(0.01)
            except Exception as exp:
                print(exp)
            
            conn.close()

    def event_handler(self):
        self.event_socket.listen(1)

        while True:
            print("Now listening...")
            conn, address = self.event_socket.accept()
            print("Connection from " + address[0] + "\n")

            try:
                while True:
                    data = conn.recv(100)

                    if data:
                        options = json.loads(data.decode("utf-8"))

                        if options["action"] == "click":
                            click(options["x"], options["y"], options["mouse_button"])
                        
                        elif options["action"] == "key":
                            press_key(options["char"])
            except Exception as exp:
                print(exp)
            
            conn.close()


def get_screenshot():
    ''' Returns a screenshot of the window that is scaled down by 1.5. '''
    image_data = ImageGrab.grab()
    image_data = image_data.resize((int(image_data.width/1.5), int(image_data.height/1.5)), Image.ANTIALIAS)

    return image_data

def click(x, y, mouse_button):
    ''' Scales up the cordinates and clicks a mouse button at the new location ''' 
    pyautogui.moveTo(x*1.5, y*1.5)

    if mouse_button == "left":
        pyautogui.click()
    
    elif mouse_button == "middle":
        pyautogui.middleClick()

    elif mouse_button == "right":
        pyautogui.rightClick()

def press_key(char):
    ''' Presses a key on the client computer '''
    pyautogui.press(char)

# Creates a new handler
ControllerHandler("192.168.1.194")