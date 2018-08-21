from tkinter import Tk, Label, Event
from PIL import ImageTk, Image
from threading import Thread
import socket, json, pickle


class ClientHandler:
    ''' This acts as a gateway for interacting with the client '''

    def __init__(self, address):
        self.event_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.event_socket.connect((address, 5790))
        
        self.image_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.image_socket.connect((address, 5791))

        self.is_running = True
        self.image_thread = Thread(target=self.image_handler)
        self.image_thread.start()

        print("Connected to " + address)
    
    def disconnect(self):
        self.is_running = False
        self.event_socket.close()

    def image_handler(self):
        image_data = []
        delimiter = "\n\n".encode("utf-8")

        while self.is_running:
            data = self.image_socket.recv(4096)
            
            if data.endswith(delimiter):
                data = data[:-2]

                if data != []:
                    image_data.append(data)

                try:
                    pickled_image = b''.join(image_data)
                    screenshot = pickle.loads(pickled_image)

                    tk_image = ImageTk.PhotoImage(screenshot)
                    
                    image_label.configure(image=tk_image)
                    image_label.image = tk_image
                except Exception as exp:
                    print(exp)
                
                image_data = []

            else:
                image_data.append(data)
        
        self.image_socket.close()

    def send_click(self, x, y, mouse_button):
        options = {
            "action": "click",
            "x": x,
            "y": y,
            "mouse_button": mouse_button
            }
        
        data = json.dumps(options).encode("utf-8")
        self.event_socket.sendall(data)
    
    def send_key(self, key):
        options = {
            "action": "key",
            "char": key
            }

        data = json.dumps(options).encode("utf-8")
        self.event_socket.sendall(data)


def left_click(event: Event):
    client.send_click(event.x, event.y, "left")

def right_click(event: Event):
    client.send_click(event.x, event.y, "right")

def middle_click(event: Event):
    client.send_click(event.x, event.y, "middle")

def key_callback(event: Event):
    client.send_key(event.char)


root = Tk()
root.title("PySpy")
root.resizable(False, False)

image_label = Label(root)
image_label.pack()

root.bind("<Key>", key_callback)
image_label.bind("<Button-1>", left_click)
image_label.bind("<Button-2>", middle_click)
image_label.bind("<Button-3>", right_click)

client = ClientHandler("192.168.1.194")
root.mainloop()
client.disconnect()