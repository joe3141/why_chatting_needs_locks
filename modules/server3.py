import socket
import sys
import time
from thread import *
import threading

port = 6002
clients = []
here = {}
guest_cnt = -1
shutdown = False
help_mess = "type /p for getting all the people connected to the server\n" \
       "type /m [NAME] for sending a message to a certain user\n" \
       "type anything without a forward slash (/) to send a message to every user!\n" \
       "type /q to quit and leave us :("

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))
except socket.error, msg:
    print("Bind failed. Error Code: " + str(msg[0]) + " Message: " + msg[1])
    sys.exit()
try:
    s4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

except socket.error, msg:
    print("Connection failed. Error Code: " + str(msg[0]) + " Message: " + msg[1])
    sys.exit()
# while 1:
#     try:
#         s4.connect(('127.0.0.1', 6003))
#         break
#     except:
#         continue
#     finally:
#         break
s4.connect(('127.0.0.1', 6003))
s.listen(10)
print "Listening"
s2, ip = s.accept()
print "connected to the other server!!!"


def receive_server2():
    while 1:
        try:
            data = s2.recv(2048)
            if data == "":
                print "I'm there!"
                break
            else:
                recv_not(data, s2)  # TODO 404 CASE
                # s3.sendall(data)
        except:
            break


def receive_server4():
    while 1:
        try:
            data = s4.recv(2048)
            if data == "":
                print "I'm there!"
                break
            else:
                recv_not(data, s4)  # TODO 404 CASE
                # s1.sendall(data)
        except:
            break


def client_thread(c):
    global s2
    global s4
    c.sendall("Welcome!\nType y to enter your name or n to have an auto generated name.")
    try:
        data = c.recv(1024)
		data = data.strip(' \t\n\r')
        serv_name(data, c)
    except:
        print "something"
        c.close()
        return
    for client in here.values():
            if not client == c:
                client.sendall("2")
    serv_people(c)
    temp_name = get_name(c)
    for client in here.values():
        client.sendall("0 " + time.ctime(time.time()) + " : " + "SERVER" + "-> " + temp_name + " has joined")
    while True:
        try:
            mess = c.recv(2048)
            if mess == "/q":
                parse(mess, c)
                notify("quit", temp_name, "", "", 0, s2)
                notify("quit", temp_name, "", "", 0, s4)
                for client in here.values():
                    client.sendall("2")
                serv_shout(temp_name + " has disconnected.", None, 1)
                break
            parse(mess, c)
        except:
            try:
                del clients[clients.index(temp_name)]
                here.pop(temp_name)  # notify
                notify("quit", temp_name, "", "", 0, s2)
                notify("quit", temp_name, "", "", 0, s4)
                print temp_name + " Disconnected"
                serv_shout(temp_name + " has disconnected.", None, 1)
                for client in here.values():
                    client.sendall("2")
            except:
                notify("quit", temp_name, "", "", 0, s2)
                notify("quit", temp_name, "", "", 0, s4)
                for client in here.values():
                    client.sendall("2")
                print temp_name + " Disconnected"
                serv_shout(temp_name + " has disconnected.", None, 1)
                break
#    c.close()


def Main():
    t = threading.Thread(target=receive_server2, args=())
    t.start()
    t1 = threading.Thread(target=receive_server4, args=())
    t1.start()
    while 1:
        # start_new_thread(server_thread(), )
        c, addr = s.accept()
        # print "I'm here!"
        print "Connected to: " + str(addr)
        start_new_thread(client_thread, (c,))


def serv_name(data, c):
    global guest_cnt
    global s2
    global s4
    if data == "y" or data == "Y":
                while True:
                    c.sendall("Enter your name: ")
                    name = c.recv(2048)
                    flag = 0
                    for i in clients:
                        if name == i:
                            flag = 1
                            break
                    if flag:
                        c.sendall("This name is already used!\n")
                    else:
                        clients.append(name)
                        here[name] = c
                        notify("join", name, "", "", 0, s2)
                        notify("join", name, "", "", 0, s4)
                        break
    else:
        guest_cnt += 1
        name = "guest" + str(guest_cnt)
        clients.append(name)
        here[name] = c
        notify("join", name, "", "", 0, s2)
        notify("join", name, "", "", 0, s4)
        notify("guest", str(guest_cnt), "", "", 0, s2)
        notify("guest", str(guest_cnt), "", "", 0, s4)


def recv_not(mess, y):  # spaghetti
    global guest_cnt
    global here
    global clients
    mess_list = mess.split(" ", 4)
    if mess_list[0] == "join":
        clients.append(mess_list[4])
        for client in here.values():
            client.sendall("2")
            client.sendall("0 " + time.ctime(time.time()) + " : " + "SERVER" + "-> " + mess_list[4] + " has joined")
        if y == s2:
            s4.sendall(mess)
        else:
            s2.sendall(mess)
    elif mess_list[0] == "guest":
        guest_cnt = int(mess_list[4])
        if y == s2:
            s4.sendall(mess)
        else:
            s2.sendall(mess)
    elif mess_list[0] == "quit":
        try:
            del clients[clients.index(mess_list[4])]
        except:
            print ""
        for client in here.values():
                    client.sendall("2")
        if y == s2:
            s4.sendall(mess)
        else:
            s2.sendall(mess)
    elif mess_list[0] == "shout":
        for client in here.values():
            client.sendall(mess_list[4])
        if y == s2:
            s4.sendall(mess)
        else:
            s2.sendall(mess)
    elif mess_list[0] == "whisper":
        if mess_list[2] in here.keys():
            here[mess_list[2]].sendall(mess_list[4])
            notify("sent", mess_list[4], "", mess_list[1], 0, y)
        else:
            # notify("404", "", "", mess_list[1], y)  # TODO ROUTING
            if y == s2:
                s4.sendall(mess)
            else:
                s2.sendall(mess)
    elif mess_list[0] == "sent":
        if mess_list[1] in here.keys():
            here[mess_list[1]].sendall(mess_list[4])
        elif y == s4:
            s2.sendall(mess)
        else:
            s4.sendall(mess)
    elif mess_list[0] == "404":
        m = int(mess_list[3])
        if y == s4 and m == 1:
            notify("whisper", mess_list[4], mess_list[2], mess_list[1], 1, s2)
        elif y == s4 and m == 0:
            notify("404", "", "", mess_list[1], 0, s2)
        elif y == s2 and m == 1:
            if mess_list[1] in here.keys():
                here[mess_list[1]].sendall("0 " + time.ctime(time.time()) + " : " + "SERVER" + "-> " +
                                                                            "This name does not exist.")
            else:
                notify("404", "", "", mess_list[1], 1, s4)


def notify(comm, mess, name, sender, d,  y):
        try:
            y.sendall(comm + " " + sender + " " + name + " " + str(d) + " " + mess)
        except:
            sys.exit(0)


def parse(mess, c):

    command = mess[0:2]
    if command == "/p":
        serv_people(c)
    elif command == "/m":
        serv_private(mess, c)
    elif command == "/q":
        serv_quit(c)
    elif command == "/h":
        serv_help(c)
    else:
        serv_shout(mess, c, 0)


def serv_shout(mess, c, f):
    if f == 0:
        mod = "0 " + time.ctime(time.time()) + " : " + get_name(c) + " -> " + mess
        for client in here.values():
            client.sendall(mod)
        notify("shout", mod, "", "", 0, s2)
        notify("shout", mod, "", "", 0, s4)
    else:
        mod = "0 " + time.ctime(time.time()) + " : " + "SERVER" + " -> " + mess
        for client in here.values():
            client.sendall(mod)
        notify("shout", mod, "", "", 0, s2)
        notify("shout", mod, "", "", 0, s4)


def serv_people(c):
    peeps = ""
    for name in clients:
        peeps += name
        peeps += "\n"
    c.sendall(peeps)


def serv_help(c):
    c.sendall(help_mess)


def serv_private(mess, c):
    name = get_name(c)
    mess_list = mess.split(" ", 2)
    mod = "1 " + time.ctime(time.time()) + " : " + name + "-> " + mess_list[2]
    if mess_list[1] in here.keys():
        here[mess_list[1]].sendall(mod)
        c.sendall(mod)
    else:
        notify("whisper", mod, mess_list[1], name, 1, s4)  # TODO 4


def serv_quit(c):
    temp_name = get_name(c)
    print str(temp_name) + " has disconnected."
    del clients[clients.index(temp_name)]
    here.pop(temp_name)
    c.close()


def get_name(c):
    for key in here.keys():
        if here[key] == c:
            return key

if __name__ == '__main__':
    Main()
