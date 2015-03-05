from Tkinter import *
import socket
import threading
import datetime

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
        # return message type, IP address, Port and Client ID
        return (n[0], n[1], int(n[2]), n[3]) 
    else:
        return (n[0], n[1], int(n[2]))

def update_log_file(info):
    """
    save the client address information in txt file 
    """
    log_file = open(file_name, 'a')
    log_file.write(info+'\n')
    log_file.close()

def Shutwindow():
    """
    when click the close window button on top of server_gui, shutdown
    all the thread, close the TCP socket and close the server_gui window 
    """
    lis1.stop()
    s.close()
    root.destroy()

def Update(server_Log, loginfo):
    """
    Update the server log window with every Requesting and Offline information
    """
    if loginfo != '':
        server_Log.config(state=NORMAL)
        server_Log.insert(END, loginfo+'\n')
        server_Log.config(state=DISABLED)
        server_Log.yview(END)
        
class Server_listen_thread(threading.Thread):
    """
    A threading for server socket keep listening clients request 
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.flag = True
    def run(self):
        while self.flag:
            conn,addr = s.accept()
            info = conn.recv(1024)
            conn_addr = (addr[0], dpkg(info)[2])
            # if server received type 'K' packet, no response to client and 
            # delete that client information from client_list
            if dpkg(info)[0]=='K':
                if conn_addr in client_list.keys():
                    Update(server_Log, 'receive offline from:'+info[2:])
                    del client_list[conn_addr]
            elif dpkg(info)[0]=='R':
            # if server received type 'R' packet, respone the requesting client
            # with all clients address information saved in its client_list
                Update(server_Log, 'got request from :'+info[2:])
                client_ID = dpkg(info)[3]
                if not client_list:
                    conn.send('Null-')
                else:
                    conn.send(str(len(client_list))) 
                    for ADDR in client_list.keys():
                        conn.send('-'+pkg('R', ADDR[0], ADDR[1]))
                if conn_addr not in client_list.keys():
                    client_list[conn_addr] = client_ID
                    update_log_file(info)
            
            conn.close()
    def stop(self):
        self.flag = False
        self._Thread__stop()
        
        
HOST = socket.gethostbyname(socket.gethostname())
PORT = 2002              

##server gui window configuration and place
root =Tk()
wintitle = 'Server v1.0\t' + HOST + ':'+str(PORT)
root.title(wintitle)
root.geometry("400x400")
server_Log = Text(root, bd=0, bg="white", height="8", width="50", font="Arial")
server_Log.insert(END, "Waiting for clients connection...\n")
server_Log.config(state=DISABLED)
server_scrollbar = Scrollbar(root, command=server_Log.yview, cursor="heart")
server_Log['yscrollcommand']=server_scrollbar.set
server_Log.place(x=4,y=4, height=394, width=384)
server_scrollbar.place(x=388,y=4, height=394, width=10)
root.protocol("WM_DELETE_WINDOW", Shutwindow)

#time format for txt log files name
format = "%H-%M-%d-%b-%Y"
today = datetime.datetime.today()
file_name = today.strftime(format)+'.txt'


    
client_list={}  ## using for store the client address information (IP, Port):ID

#open the TCP socket for serving listening
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(5)

#server listening thread start and server is online
lis1 = Server_listen_thread()
lis1.start()
        

root.mainloop()
