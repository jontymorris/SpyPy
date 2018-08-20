from tkinter import Tk, Label, Event
from PIL import ImageTk, Image
from threading import Thread
import socket, json, pickle


class ClientHandler:
    ''' This acts as a gateway for interacting with the client '''

    def __init__(self, address):
        self.event_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.event_socket.connect((address, 25565))

        self.image_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.image_socket.connect((address, 5791))

        self.image_thread = Thread(target=self.image_handler)
        self.image_thread.start()

        print("Connected to " + address)
    
    def image_handler(self):
        image_data = []

        while True:
            data = self.image_socket.recv(4096)

            # TODO: check for new line character
            image_data.append(data)

            #image = pickle.loads(data)
            #image_label.image = ImageTk.PhotoImage(image)

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

#screenshot = ImageTk.PhotoImage(get_screenshot())

image_label = Label(root)
image_label.pack()

root.bind("<Key>", key_callback)
image_label.bind("<Button-1>", left_click)
image_label.bind("<Button-2>", middle_click)
image_label.bind("<Button-3>", right_click)

client = ClientHandler("192.168.1.194")

root.mainloop()