import socket

FORMAT=('utf-8')
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, 80)

def login(data):
    if(data=='Username=admin&Password=admin'):
        return True
    else:
        return False

def download(data):
    if(data=='files=Files'):
        return True
    else:
        return False
    
def info(conn):
    header = 'HTTP/1.1 301 Moved Permanently\nLocation:/info.html'
    conn.send(header.encode())
    conn.close()

def files(conn):
    header = 'HTTP/1.1 301 Moved Permanently\nLocation:/files.html'
    conn.send(header.encode())
    conn.close()

def _404(conn):
    header = 'HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n'
    myfile="404.html"
    myfile=open(myfile,"rb")
    response=myfile.read()
    header=header.encode(FORMAT)
    final=header+response
    conn.send(final)
    conn.close()

def chunked(myfile,conn):
    file=open(myfile,'rb')
    max_chunk=1024*16
    while True:
        chunk=file.read(max_chunk)
        indi=bytes("%s \r\n" % hex(len(chunk))[2:],FORMAT)
        conn.sendall(indi)
        chunk=chunk+bytes("\r\n",FORMAT)
        conn.sendall(chunk)
        if(indi==bytes("%s \r\n" % hex(0)[2:],FORMAT)):
            break
    final=bytes("\r\n",FORMAT)
    conn.send(final)

authority='0'
server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(ADDR)
server.listen(5)
print('Server is running')
print('Access at:',SERVER)
while True:
    conn,addr=server.accept()
    user_request=conn.recv(100000).decode(FORMAT)
    print(user_request)
    list_request=user_request.split(' ')
    method=list_request[0]
    if(method == "GET"):
        requesting=list_request[1]
        print (requesting)
        myfile=requesting.split('?')[0]
        myfile=myfile.lstrip('/')
        if(myfile==''):
            myfile='index.html'
        if((myfile=='info.html' or myfile=="files.html") and authority=='0'):
            myfile='index.html'
        response="HTTP/1.1 200 OK\n"
    elif(method == 'POST'):
        auth = list_request[-1].splitlines()
        msg=auth[2]  
        if(login(msg)):
            authority='1'
            info(conn)
            continue
        elif(download(msg)):
            files(conn)
            continue
        else:
            _404(conn)
            continue
    if (myfile.endswith(".html")):
        response+="Content-Type: text/html \n"
    response+="Transfer-Encoding: chunked\n\n"  
    try:
        f=open(myfile,"rb")
        f.close()
    except Exception as e:
        _404(conn)
        continue
    response=response.encode(FORMAT)
    conn.send(response)
    chunked(myfile,conn)
    conn.close()
