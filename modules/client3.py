import thread
import socket
from GUI_FNS import *

# packs

win_title = "Chat"
host = "127.0.0.1"
port = 6002


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()


def ClickAction():
    # Write message to chat window
    EntryText = EntryBox.get("0.0", END)
    LoadMyEntry(ChatLog, EntryText)

    # Scroll to the bottom of chat windows
    ChatLog.yview(END)

    # Erace previous message in Entry Box
    EntryBox.delete("0.0", END)

    # Send my mesage to all others
    if EntryText.strip(' \t\n\r') == "/q":
        s.sendall(EntryText)
        sys.exit()
    s.sendall(EntryText)

def PressAction(event):
	EntryBox.config(state=NORMAL)
	ClickAction()


def DisableEntry(event):
	EntryBox.config(state=DISABLED)

#Create a window
base = Tk()
base.title(win_title)
base.geometry("980x500")
base.resizable(width=FALSE, height=FALSE)

#Create a Chat window
ChatLog = Text(base, bd=0, bg="white", height="1000", width="1000", font="Arial",)
ChatLog.insert(END, "Connecting to the server..\n")
ChatLog.config(state=DISABLED)
ChatLog.pack()

#Bind a scrollbar to the Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")

# scrollbar.grid(sticky = E)
# scrollbar.pack(side=RIGHT)
ChatLog['yscrollcommand'] = scrollbar.set

#Create the Button to send message
SendButton = Button(base,  text="Send",

                    command=ClickAction)

#Create the box to enter message
EntryBox = Text(base, bd=0, bg="grey", width="29", height="5", font="Arial")
EntryBox.bind("<Return>", DisableEntry)
EntryBox.bind("<KeyRelease-Return>", PressAction)

#Peoplepanel


#DropDown for clients


#Place all components on the screen
scrollbar.place(x=800,y=5, height=395)
ChatLog.place(x=6 ,y=6, height=400, width=800)
EntryBox.place(x=128, y=401, height=100, width=690)
SendButton.place(x=6, y=401, height=95)

s.connect((host, port))
LoadConnectionInfo(ChatLog, 'Connected to the server! \n')


def receiving():
    global s
    while 1:
        try:
            data = s.recv(1024)
        except:
            LoadConnectionInfo(ChatLog, '\n [ Server disconnected ] \n')
            break
        if data != '':
            LoadOtherEntry(ChatLog, data)
        else:
            LoadConnectionInfo(ChatLog, '\n [ Server disconnected ] \n')
            break


thread.start_new_thread(receiving, ())

base.mainloop()

