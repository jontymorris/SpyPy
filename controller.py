from tkinter import Tk, Label, Event
from PIL import ImageTk, Image
from threading import Thread
import socket, json, pickle


class ClientHandler:
    ''' This acts as a gateway for interacting with the client '''

    def __init__(self, address):
        self.delimiter = "\n\n".encode("utf-8")

        self.event_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.event_socket.connect((address, 5790))

        self.is_connected = True

        self.image_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.image_socket.connect((address, 5791))

        self.image_thread = Thread(target=self.image_handler)
        self.image_thread.start()

        print("Connected to " + address)
    
    def disconnect(self):
        ''' Disconnects from the client '''
        self.is_connected = False

        options = {"action": "disconnect"}
        self.event_socket.sendall(json.dumps(options).encode("utf-8"))
        self.event_socket.sendall(self.delimiter)

        self.event_socket.close()
        self.image_socket.close()
        
        print("Disconnected from client")

    def image_handler(self):
        ''' Receives images through a socket from the client. It then unpickles the images and displays them on to the window '''
        image_data = []
        while self.is_connected:
            try:
                data = self.image_socket.recv(4096)
                
                if data.endswith(self.delimiter):
                    data = data[:-2]

                    if data != []:
                        image_data.append(data)

                    try:
                        pickled_image = b''.join(image_data)
                        screenshot = pickle.loads(pickled_image)

                        tk_image = ImageTk.PhotoImage(screenshot)
                        
                        image_label.configure(image=tk_image)
                        image_label.image = tk_image
                    except:
                        pass
                    
                    image_data = []

                else:
                    image_data.append(data)
            except Exception as exp:
                print(exp)

    def send_click(self, x, y, mouse_button):
        ''' Sends a mouse event to the client '''
        if not self.is_connected:
            return

        options = {
            "action": "click",
            "x": x,
            "y": y,
            "mouse_button": mouse_button
            }
        
        data = json.dumps(options).encode("utf-8")

        self.event_socket.sendall(data)
        self.event_socket.sendall(self.delimiter)
    
    def send_key(self, key):
        ''' Sends key press event to the client'''
        if not self.is_connected:
            return

        options = {
            "action": "key",
            "char": key
            }

        data = json.dumps(options).encode("utf-8")

        self.event_socket.sendall(data)
        self.event_socket.sendall(self.delimiter)


def left_click(event: Event):
    ''' Sends a left click event to the client '''
    client.send_click(event.x, event.y, "left")

def right_click(event: Event):
    ''' Sends a right click event to the client '''
    client.send_click(event.x, event.y, "right")

def middle_click(event: Event):
    ''' Sends a midle click event to the client '''
    client.send_click(event.x, event.y, "middle")

def key_callback(event: Event):
    ''' Sends the pressed key to the client '''
    client.send_key(event.char)


# Creates the window
root = Tk()
root.title("PySpy")
root.resizable(False, False)

# Displays the clients screenshots
image_label = Label(root)
image_label.pack()

# Hooks for the tkinter window
root.bind("<Key>", key_callback)
image_label.bind("<Button-1>", left_click)
image_label.bind("<Button-2>", middle_click)
image_label.bind("<Button-3>", right_click)

# Connect to the client
client = ClientHandler("192.168.1.194")

# Start displaying the window
root.mainloop()

# Disconnect when the window has been closed
client.disconnect()