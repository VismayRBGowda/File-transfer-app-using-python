import os
import socket
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import END


class FileTransferApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set window properties.
        self.title("File Transfer")
        self.geometry("500x300")

        # Create the UI elements.
        self.label = tk.Label(self, text="Select an option:")
        self.label.pack(pady=10)

        self.send_button = tk.Button(self, text="Send File", command=self.send_file)
        self.send_button.pack(pady=10)

        self.receive_button = tk.Button(self, text="Receive File", command=self.receive_file)
        self.receive_button.pack(pady=10)


        self.sender_window = tk.Toplevel(self)
        self.sender_window.title("Sender")
        self.sender_window.geometry("400x250")

        self.host_name = tk.Label(self.sender_window)

        self.file = tk.Label(self.sender_window)

        self.file_size_sender = tk.Label(self.sender_window)
        self.file_size_sender.pack(pady=10)

        self.index_label_sender = tk.Label(self.sender_window)
        self.index_label_sender.pack(pady=10)

        # Create the receiver window.
        self.receiver_window = tk.Toplevel(self)
        self.receiver_window.title("Receiver")
        self.receiver_window.geometry("400x500")

        

        self.connected = tk.Label(self.sender_window,text="Connected")

        # Create the UI elements in the receiver window.
        self.receiver_label = tk.Label(self.receiver_window, text="Enter host name:")
        self.receiver_label.pack(pady=10)

        self.receiver_entry = tk.Entry(self.receiver_window)
        self.receiver_entry.pack(pady=10)



        self.connect_button = tk.Button(self.receiver_window, text="Connect", command=self.connect)
        self.connect_button.pack(pady=10)


        self.sender_connected = tk.Label(self.receiver_window)
        self.sender_connected.pack(pady=10)

        self.file_size = tk.Label(self.receiver_window)
        self.file_size.pack(pady=10)

        self.index_label = tk.Label(self.receiver_window)
        self.index_label.pack(pady=10)

        self.file_list_label = tk.Label(self.receiver_window, text='List of files:')
               

        self.index_send = tk.Button(self.receiver_window, text="Receive File")
        

        

        # create a listbox to display the list of files
        self.file_listbox = tk.Listbox(self.receiver_window)

        self.receiver_window.withdraw()

        self.sender_window.withdraw()

        self.file_name = ""
        self.sock = None
        self.flag_value = -1


    def check_flag_value(self):
        if self.flag_value == 1:
            return True
        else:
            return False


    def send_file(self):
    #file_path = filedialog.askopenfilename()
    #if not file_path:
    #    return
    
        
        # Creating a socket.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        port = 22222
        self.sock.bind((host, port))
        self.sock.listen(5)
        print("Host Name:",self.sock.getsockname())
        self.host_name.configure(text=self.sock.getsockname())
        self.host_name.pack(pady=10)
        self.sender_window.deiconify()
        self.sender_window.update()
        

        # Get the list of files available at the sender's side.
        file_list = os.listdir()

        # Send the list of files to the receiver.
        file_list_str = '\n'.join(file_list)
        client, addr = self.sock.accept()
        client.send(file_list_str.encode())

        file_name_bytes = client.recv(1024)
        self.file_name = file_name_bytes.decode()

        self.file.configure(text=self.file_name)
        self.file.pack(pady=10)

        print("Filename:",self.file_name)

        # Getting file details.
        file_size = os.path.getsize(self.file_name)

        msg_bytes = client.recv(1024)
        msg = msg_bytes.decode()
        #print("Message is :",msg)

        if(msg == "send"):

            # Sending file_name and detail.
            #client.send(file_name.encode())
            client.send(str(file_size).encode())

            # Opening file and sending data.
            with open(self.file_name, "rb") as file:
                c = 0
                # Starting the time capture.
                start_time = time.time()

                # Running loop while c != file_size.
                while c < file_size:
                    data = file.read(1024)
                    if not (data):
                        break
                    client.sendall(data)
                    c += len(data)
                # Ending the time capture.
                end_time = time.time()

            print("File Transfer Complete.Total time: ", end_time - start_time)

            self.file_size_sender.configure(text=f"File size is: {int(file_size)/1024:.2f} KB")


            self.index_label_sender.configure(text=f"File transfer complete. Total time: {end_time - start_time:.4f} seconds.")
            # Closing the socket.
            self.sock.close()



    def receive_file(self):
        self.receiver_window.deiconify()

    # def send_index(self):
    #     self.sock.sendall(self.file_name.encode())


    def connect(self):
        host = self.receiver_entry.get()
        if not host:
            return
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Trying to connect to socket.
        try:
            self.sock.connect((host, 22222))
            print("Connected Successfully")
            self.sender_connected.configure(text="Connected successfully")
        except:
            print("Unable to connect")
            return
        


        file_list_str = self.sock.recv(1024).decode().split("\n")
        
        for file_name in file_list_str:
            self.file_listbox.insert(END, file_name)
        self.file_list_label.pack()
        self.file_listbox.pack()
        self.index_send.pack(pady=10)

         


        
        # print("Files Available:")
        # for i, files in enumerate(file_list_str):
        #     print(f"{i} : {files}")
        # Choose the file to receive.


        def send_index():
            print("File name is sent to the sender")
            #print("flag_value before:", self.flag_value)
            index = self.file_listbox.curselection()
            if index:
                index = index[0]
                self.file_name = file_list_str[index]
                self.sock.sendall(str(self.file_name).encode())
                self.flag_value = 1
                #print("flag_value after:", self.flag_value)



        self.index_send.configure(command=send_index)
        

        #print("Flag value is :",self.flag_value)



        while not self.check_flag_value():
            self.update()

        msg = "send"
        self.sock.sendall(msg.encode())


        
        print("filename is :",self.file_name)
        file_size = self.sock.recv(100).decode()

        print("File size :",file_size)

            # Opening and reading file.
        with open("./" + self.file_name, "wb") as file:
                c = 0
                # Starting the time capture.
                start_time = time.time()

                # Running the loop while file is received.
                while c <= int(file_size):
                    data = self.sock.recv(1024)
                    if not (data):
                        break
                    file.write(data)
                    c += len(data)

                # Ending the time capture.
                end_time = time.time()

        print("File transfer Complete.Total time: ", end_time - start_time)

        self.file_size.configure(text=f"File size is: {int(file_size)/1024:.2f} KB")


        self.index_label.configure(text=f"File transfer complete. Total time: {end_time - start_time:.4f} seconds.")


            # Closing the socket.
        self.sock.close()


if __name__ == "__main__":
    app = FileTransferApp()
    app.mainloop()