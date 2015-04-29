##import cn_Fn
from Tkinter import *
from socket import *
import time, threading, Queue
# Might need the antigravity module incase of space travel
# import antigravity

Info1 = 'Input the user name and port you want to use in chat room.'
Info2 = 'Name length should at least one letter and no more than 16 letters.'
Info3 = 'Port number should be integar and over 2000'
Info3_1 = 'Port number should be integar'
Info4 = 'Not valid IPv4 address format. Example 192.168.2.1'


UNKNOWN_NAME = "Unknown"

SPECIAL_MESSAGE = {
    "GET_NAME_MSG": "X_GET_NAME",   # format X_GET_NAME|Port
    "GET_NAME_RESP": "X_NAME"       # format X_NAME|Nickname|Port
}


def pkg(Type, IPaddr, port, ID=""):
    """
    Package the clients (IP, Port):ID information in string for 
    transmit. 'Type' indicates the purpose of the package: 
    'R'(Requesting Information Package)
    'K'(Offline Information Package)
    """
    if not ID:
        info = Type+':'+IPaddr + ':' + str(port)
    else:
        info = Type+':'+IPaddr + ':' + str(port) + ':' + ID
    return info
    
def dpkg(info):
    """
    depackage the packed received string to (IP, Port):ID format. 
    """
    n = info.split(':')
    if len(n)==4:
        return (n[0], n[1], int(n[2]), n[3])
    else:
        return (n[0], n[1], int(n[2]))



#---------------------------------------------------#
#----------------Quest GUI Window ------------------#
#---------------------------------------------------#

class Quest_GUI_Win(Tk):
    """ 
    Creating the Quest GUi window where asking client to input username
    and port number they want to use for communicate. It also request client
    to input the server IP address for accessing the latest client list
    """
    def __init__(self):
        
        Tk.__init__(self)
        self.title('Quest')
        questWindow = Frame(self)
        questWindow.grid()
        info1_lbl = Label(questWindow, text=Info1)
        info2_lbl = Label(questWindow, text=Info2)
        info3_lbl = Label(questWindow, text=Info3)
        user_lbl = Label(questWindow, text='user name')
        self.user_ent = Entry(questWindow)
        port_lbl = Label(questWindow, text='UDP port')
        self.port_ent = Entry(questWindow)
        server_add_lbl = Label(questWindow, text='server IP address')
        self.server_add_ent = Entry(questWindow)
        confirm_bttn = Button(questWindow, text='Confirm', command=self.reveal)
        quit_bttn = Button(questWindow, text='Cancel', command=self.destroy)
        
    ##  place wedges
        info1_lbl.grid(row=0, column=0, columnspan=3, sticky=W,padx=10)
        info2_lbl.grid(row=1, column=0,columnspan=3, sticky=W,padx=10)
        info3_lbl.grid(row=2, column=0,columnspan=3, sticky=W,padx=10)
        user_lbl.grid(row=3, column=0,sticky=W,padx=10)
        self.user_ent.grid(row=4, column=0,sticky=W,padx=10)
        port_lbl.grid(row=3, column=1,sticky=W)
        self.port_ent.grid(row=4, column=1, sticky=W)
        server_add_lbl.grid(row=5, column=0,sticky=W,padx=10)
        self.server_add_ent.grid(row=6, column=0,sticky=W,padx=10)
        confirm_bttn.grid(row=7, column=0, pady=10)
        quit_bttn.grid(row=7, column=1)

    def reveal(self):
        """ 
        Check the input information follows the instruction and create the
        first connection with server. Then start server_refresh thread and 
        open the user defined UDP socket listening thread
        """
        global myID
        global myIP
        global serverIP
        global myPort
        global sock
        global server_refresh
        global re
        myID = self.user_ent.get()
        myPort = self.port_ent.get()
        serverIP = self.server_add_ent.get()
        if (len(myID)<1) or (len(myID)>18):
            showerror("Name Length Error", Info2)
        else:
            try:
                val = int(myPort)
                if val<2000: #2048 check it later?
                    showerror("Port Number Error", Info3)
                else:
                    self.destroy()
                    NewTitle = 'Chat_dic v1.0:' +' '+myID+' (' + myIP + ':' + myPort+' )'
                    chat_win = Chat_GUI_Win(NewTitle)  
                    myAddress = (myIP, int(myPort))
                    sock = socket(AF_INET, SOCK_DGRAM)
                    sock.bind(myAddress)
                    connect_server(myID, myPort, serverIP, 2002, 'R','[ Succesfully connected with server]\n')
                    server_refresh=Server_Alive()
                    re =  Receiving(sock)

                    server_refresh.start()
                    re.start()

##                    host_socket.bind((myIPaddr, val))
##                    host_socket.listen(5)
##                    waitconnect.start()
            except ValueError:
                showerror("Port Number Error", Info3)
                

#---------------------------------------------------#
#------------------ Chat Window  -------------------#
#---------------------------------------------------#            
class Chat_GUI_Win(Tk):
    """ 
    GUI for client communicate with each other. There are three main block 
    in layout: Chatlog, where show the communicate information including 
    chating content and connection information; EntryBox, where for user to
    input the message for sending to other clients; FriList, where show the 
    online friends.
    """
    def __init__(self,newtitle):
        global chat_Chatlog
        global chat_EntryBox
        global chat_FriList
        Tk.__init__(self)
        self.title(newtitle)
        self.protocol("WM_DELETE_WINDOW", self.cls_chat_win)
        self.geometry("410x500")
        #-----Chat Window---------------- 
        chat_Chatlog = Text(self, bd=0, bg="white", height="8", width="50", font="Arial")
##        chat_Chatlog.insert(END, "Waiting for your friend to connect..\n")
        chat_Chatlog.config(state=DISABLED)

        #Bind a scrollbar to the Chat window
        chat_scrollbar = Scrollbar(self, command=chat_Chatlog.yview, cursor="heart")
        chat_Chatlog['yscrollcommand']=chat_scrollbar.set

        #Create the box to enter message
        chat_EntryBox = Text(self,bd=0, bg="white", width="29", height="5", font="Arial")
        chat_EntryBox.bind("<Return>", DisableEntry)
        chat_EntryBox.bind("<KeyRelease-Return>", PressAction)
                        
        # Create Online Friend List
        chat_FriLIst_lbl = Label(self, font=22, text='Friend List')
        chat_FriList = Listbox(self)

        # Create the Button to send message
        chat_Sendbttn = Button(self, font=30, text="Send", width="12", height="5", command=ClickAction)
        
        chat_Chatlog.place(x=6,y=6, height=386, width=265)
        chat_scrollbar.place(x=6,y=6, height=386, width=266)
        chat_EntryBox.place(x=6, y=401, height=90, width=265)
        chat_FriLIst_lbl.place(x=280, y=8, height=12, width=120)
        chat_FriList.place(x=280, y=22, height=200, width=120)
        chat_Sendbttn.place(x=280, y=401, height=90)

    def cls_chat_win(self):
        """
        close the Chat_GUI_Win trigger function to stop the rest threads
        """
        self.destroy()
        cls_connect()

#---------------------------------------------------#
#----------------- KEYBOARD EVENTS -----------------#
#---------------------------------------------------#
def PressAction(event):
    global chat_EntryBox
    chat_EntryBox.config(state=NORMAL)
    ClickAction()
def DisableEntry(event):
    global chat_EntryBox
    chat_EntryBox.config(state=DISABLED)

#---------------------------------------------------#
#------------------ MOUSE EVENTS -------------------#
#---------------------------------------------------#
def ClickAction():
    global chat_EntryBox
    global chat_FriList

    #Write message to chat window
    EntryText = FilteredMessage(chat_EntryBox.get("0.0",END))
    LoadMyEntry(EntryText)

    #Scroll to the bottom of chat windows
    #chat_Chatlog.yview(END)

    #Erace previous message in Entry Box
    chat_EntryBox.delete("0.0",END)
            
    #Send my mesage to all others

    import socket

    data = FilteredMessage(chat_EntryBox.get("0.0",END))
    SendMessage(EntryText, neighbor_list[chat_FriList.curselection()[0]])
    """
    student need to create the function for sending the message themselves
    here
    """

# Wrap all message sending with a function to prepend source port
def SendMessage(message, neighbor):
    s = socket(AF_INET,SOCK_DGRAM)
    s.sendto(myPort + "!" + message,(neighbor.host, neighbor.port))

#---------------------------------------------------#
#------------------ Load Entris  -------------------#
#---------------------------------------------------#
def FilteredMessage(EntryText):
    """
    Filter out all useless white lines at the end of a string,
    returns a new, beautifully filtered string.
    """
    EndFiltered = ''
    for i in range(len(EntryText)-1,-1,-1):
        if EntryText[i]!='\n':
            EndFiltered = EntryText[0:i+1]
            break
    for i in range(0,len(EndFiltered), 1):
            if EndFiltered[i] != "\n":
                    return EndFiltered[i:]+'\n'
    return ''

def LoadconnectInfo(EntryText):
    """ 
    Load the connection information and put them on Chatlog
    """
    global chat_Chatlog
    if EntryText != '':
        chat_Chatlog.config(state=NORMAL)
        if chat_Chatlog.index('end') != None:
            chat_Chatlog.insert(END, EntryText+'\n')
            chat_Chatlog.config(state=DISABLED)
            chat_Chatlog.yview(END)

def LoadMyEntry(EntryText):
    """ 
    Load user input information and put them on Chatlog
    """
    global chat_Chatlog
    if EntryText != '':
        chat_Chatlog.config(state=NORMAL)
        if chat_Chatlog.index('end') != None:
            LineNumber = float(chat_Chatlog.index('end'))-1.0
            chat_Chatlog.insert(END, "You: " + EntryText)
            chat_Chatlog.tag_add("You", LineNumber, LineNumber+0.4)
            chat_Chatlog.tag_config("You", foreground="#FF8000", font=("Arial", 12, "bold"))
            chat_Chatlog.config(state=DISABLED)
            chat_Chatlog.yview(END)

# Load an entry into the chat from someone other than yourself
def LoadOtherEntry(otherID, EntryText):
    """ 
    Manage the received information from others and put them on Chatlog
    """
    global chat_Chatlog
    if EntryText != '':
        chat_Chatlog.config(state=NORMAL)
        if chat_Chatlog.index('end') != None:
            try:
                LineNumber = float(chat_Chatlog.index('end'))-1.0
            except:
                pass
            chat_Chatlog.insert(END, otherID + ": " + EntryText)
            chat_Chatlog.tag_add(otherID, LineNumber, LineNumber+0.6)
            chat_Chatlog.tag_config(otherID, foreground="#04B404", font=("Arial", 12, "bold"))
            chat_Chatlog.config(state=DISABLED)
            chat_Chatlog.yview(END)


# UpdateFriendsList now takes a neighbour object
def UpdateFriendsList(neighbour):
    """ 
    Updates the friends list
    """
    global chat_FriList

    # Insert the name into the sidebar list instead
    # of the port like we originally did
    chat_FriList.insert(END, neighbour.name)


def DeleteFriendsList():
    """ 
    Clears the friends List
    """
    global chat_FriList
    chat_FriList.delete(0, END)


            
#---------------------------------------------------#
#------------------ Connections  -------------------#
#---------------------------------------------------#
class Server_Alive(threading.Thread):
    """ 
    Thread keep connect with server every 30s, and receive the client_list 
    information saved on server.
    """
    def __init__(self): #, myID, myPort, serverIP):
        threading.Thread.__init__(self)
        self.flag= True
        self.Type= 'R'
    def run(self):
        global myID
        global myPort
        global serverIP
        global serverPort
        while self.flag:
            time.sleep(30)
            connect_server(myID, myPort, serverIP, serverPort, self.Type)          
    def stop(self):
        self.flag = False
        self.Type = 'K'
        self._Thread__stop()

class Receiving(threading.Thread):
    """ 
    Thread keep wacthing the user defined UDP socket and receving the messages
    from other clients. 
    """
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
        self.flag = True
    def run(self):
        while self.flag:
            msg, addr = self.sock.recvfrom(1024) 

            # Special messages begin with X_ so we don't want to print these
            # to the message log
            if 'X_' in msg:
                # All messages are prepended PORT! so we strip it out
                msg = msg[msg.find('!') + 1:]
                # Special messages are delimited with | so we can 
                # split by the character
                msg_unpacked = msg.split('|')
                
                # Check the type of special message,
                # if it's a request for the name of this client
                if msg_unpacked[0] == SPECIAL_MESSAGE["GET_NAME_MSG"]:
                    # extract the destination port from the message
                    dest_port = int(msg_unpacked[1])
                    # We need to respond to the GET_NAME request
                    SendMessage("{}|{}|{}".format(
                            SPECIAL_MESSAGE["GET_NAME_RESP"],
                            myID, 
                            myPort
                        ), 
                        # Need to create a temporary neighbour object
                        # to pass through to SendMessage
                        Neighbour(addr[0], dest_port)
                    )
                    continue
                # If we got a response to the name request then we need to
                # update our list of neighbours with the name based on the port
                elif msg_unpacked[0] == SPECIAL_MESSAGE["GET_NAME_RESP"]:
                    # Pass the new name and the port of the neighbour
                    UpdateNeighborName(msg_unpacked[1], msg_unpacked[2])
                    continue
            else:
                fromName = UNKNOWN_NAME
                hasPort = False
                if '!' in msg:
                    hasPort = True
                    dest_port = int(msg[0:msg.find('!')])
                    msg = msg[msg.find('!') + 1:]
                    fromName = GetUserNameFromPort(addr[0], dest_port)
                
                #Loads message into the chat.
                LoadOtherEntry(fromName, msg)

    def stop(self):
        self.flag = False
        self._Thread__stop()

# Makes sense to make a real class for neighbours instead
# of passing a tuple around and having to remember the indices
class Neighbour(object):
    """
        Holds information about other neighbours connected to the 
        same server and their names       
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.name = "Unknown"

    def setName(self, name):
        self.name = name


def connect_server(myID, myPort, SERVER_ADD, SERVER_PORT,  Type, Info=''):
    """ 
    connect the server. If Type is Requesting('R'), then receive the 
    client_list transmitted from server. If Type is Offline('K'), then
    close down without expecting receive anything from server
    """
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((SERVER_ADD, SERVER_PORT))
    LoadconnectInfo(Info)
    s.send(pkg(Type, myIP, myPort, myID))
    if Type == 'R':
        data = None
        IP_addr = None
        data = s.recv(1024)
        server_recv=data

        if data:
            if data.split('-')[0] == 'Null':
                print 'no neighbors right now'
            else:
                count = 0
                while (count < int(data.split('-')[0])):
                    info = s.recv(1024)
                    server_recv += info
                    count += 1
                    
                neighbor = server_recv.split('-')
                count = 0
                while (count < int(neighbor[0])):
                    IP_addr = neighbor[count+1].split(':')
                    
                    AddUserToList(myID, int(myPort), IP_addr[1], int(IP_addr[2]))

                    count += 1
    s.close()

def client_offline():
    """ 
    send the offline informationm to server
    """
    global myID
    global myPort
    global serverIP
    global serverPort
    connect_server(myID, myPort, serverIP, serverPort,  'K')

def cls_connect():
    """
    close all the threads and socket 
    """
    server_refresh.stop()
    client_offline()
    re.stop()
    sock.close()
def AddUserToList(myID, myPort, newip, newport):
    """
    Adds a new user to the list if it doesn't already exsist
    """
    
    if (myID, myPort) == (newip, newport):
        return

    found = False
    for neighbour in neighbor_list:
        if neighbour.host == newip and neighbour.port == newport:
            found = True

    if not found:
        new_neighbor = Neighbour(newip, newport)
        neighbor_list.append(new_neighbor)
        GetUserNameFromClient(new_neighbor)

def GetUserNameFromClient(neighbor):
    SendMessage("X_GET_NAME|" + myPort, neighbor)

def UpdateNeighborName(name, port):
    port = int(port)
    print "Updating name for [" + str(port) + "]" + name

    [n.setName(name) for n in neighbor_list if n.port == port]

    # This is the for equivalent of the above
    # for neighbor in neighbor_list:
    #     if neighbor.port == port:
    #         print "Found, updating!!"
    #         neighbor.setName(name)
    #         break



    DeleteFriendsList()

    [UpdateFriendsList(n) for n in neighbor_list]

    # This for loop is the same as the above loop
    # for neighbour in neighbor_list:
    #     UpdateFriendsList(neighbour)

# We only get the port of the user when we get a message
# so we need to find the neighbour that belongs to the port
# so we can get the name of the user. It will default to "Unknown"
def GetUserNameFromPort(ip, port):
    for neighbor in neighbor_list:
        if neighbor.host == ip and neighbor.port == port:
            return neighbor.name

    return UNKNOWN_NAME

myID=''
myIP = gethostbyname(gethostname())
myPort=''
chat_Chatlog=''
chat_EntryBox=''
serverIP=''
serverPort=2002
neighbor_list = [] #[(IP,Port),(IP,Port)]
sock=''
server_refresh=''
re=''

app = Quest_GUI_Win()
app.mainloop()
