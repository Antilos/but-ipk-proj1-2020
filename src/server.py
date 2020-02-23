import socket
import re
import ipk_exceptions as ipke

class ipkRequest():
    def __init__(self, requestStr):
        parsedRequest = self.parseRequest(requestStr)
        self.method = parsedRequest['method']
        self.version = parsedRequest['version']
        self.name = parsedRequest['name']
        self.nameType = parsedRequest['type']
        self.output = ''

    def parseRequest(self, request):
        print(request)
        '''
        Correct Pattern = r'^
        (?P<method>(?:GET)|(?:POST))\  # Method
        (?P<url>(?:/resolve?name=(?P<name>.*?)&(?P<type>(?:A)|(?:PTR)))|(?:/dns-query))\ 
        (?P<version>HTTP/1.1)
        $'
        '''
        requestPattern = r'''^
        (?P<method>[^ ]*)\  # Method
        (?P<url>[^ ]*)\ 
        (?P<version>.*)
        $'''
        m = re.search(requestPattern, request, re.VERBOSE)
        parsedRequest = dict()

        if(not m):
            raise ipke.RequestDidntMatchAtAllException
        
        #scan method
        if(m.group('method') == 'GET' or m.group('method') == 'POST'):
            parsedRequest['method'] = m.group('method')
        else:
            raise ipke.IllegalHTTPMethodException()

        #scan url
        if(parsedRequest['method'] == 'GET'):
            #EXAMPLE: /resolve?name=apple.com&type=A
            #NOTE: Can't simply use one regex pattern, we need to distinguish between wrong request and missing parameters
            tokens = re.split(r'[?=&]', m.group('url'))
            if(len(tokens) == 5):
                if(tokens[0] == '/resolve'):
                    if(tokens[1] == 'name'):
                        parsedRequest['name'] = tokens[2]
                    if(tokens[3] == 'type'):
                        if(tokens[4] == 'A' or tokens[4] == 'PTR'):
                            parsedRequest['type'] = tokens[4]
                        else:
                            raise ipke.IncorrectURLRequestException
                    else:
                        raise ipke.IncorrectGETFormatException
                else:
                    raise ipke.IncorrectGETFormatException
            else:
                raise ipke.IncorrectGETFormatException
        else: #should only be POST
            #/dns-query
            if(m.group('url') == '/dns-query'):
                parsedRequest['name'] = 'NA'
                parsedRequest['type'] = 'NA'
            else:
                raise ipke.IncorrectURLRequestException

        #scan version
        if(m.group('version') == 'HTTP/1.1'):
            parsedRequest['version'] = m.group('version')
        else:
            raise ipke.IncorrectHTTPVersion()

        return parsedRequest

    def handleRequest(self):
        if self.method == 'GET':
            self.__doGET()
        else:
            self.__doPOST()
    
    def __doGET(self):
        if(self.nameType=='A'):
            self.output = f'{self.name}:{self.nameType}={socket.gethostbyname(self.name)}\n'
        else:
            self.output = f'{self.name}:{self.nameType}={socket.gethostbyaddr(self.name)[0]}\n'


    def __doPOST(self):
        pass

    def getOutput(self):
        if(self.output):
            return self.output
        else:
            raise ipke.EmptyOutputException

def main():
    HOST = '127.0.0.1'  # localhost
    PORT = 5353        # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                #data = conn.recv(1024)
                data = conn.makefile(mode='r', buffering=1).readline()
                #if not data:
                #    break
                #conn.sendall(bytes(data, 'utf-8'))
                request = ipkRequest(data)
                request.handleRequest()
                conn.sendall(bytes(request.getOutput(), 'utf-8'))

main()