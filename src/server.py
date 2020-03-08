import socket
import re
import ipk_exceptions as ipke
import datetime
import argparse

class ipkRequest():
    def __init__(self, request):
        parsedRequest = self.parseRequest(request)
        self.method = parsedRequest['method']
        self.version = parsedRequest['version']
        self.name = parsedRequest['name']
        self.nameType = parsedRequest['type']
        self.header = parsedRequest['header']
        self.body = parsedRequest['body']
        self.output = list()

    def __str__(self):
        if(self.method == 'GET'):
            print(f'{self.method} /resolve?name={self.name}&type={self.nameType} {self.version}\n{self.header}\n\n')
        else:
            print(f'{self.method} /dns-query {self.version}\n{self.header}\n\n{self.body}')

    def parseRequest(self, request):
        '''
        Correct Pattern = r'^
        (?P<method>(?:GET)|(?:POST))\  # Method
        (?P<url>(?:/resolve?name=(?P<name>.*?)&(?P<type>(?:A)|(?:PTR)))|(?:/dns-query))\ 
        (?P<version>HTTP/1.1)
        $'
        '''
        requestLine = request[0]

        requestPattern = r'''^
        (?P<method>[^ ]*)\  # Method
        (?P<url>[^ ]*)\ 
        (?P<version>.*)
        $'''
        m = re.search(requestPattern, requestLine, re.VERBOSE)
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

            parsedRequest['header'] = request[1:]
            parsedRequest['body'] = ''

            tokens = re.split(r'[?=&]', m.group('url'))
            if(len(tokens) == 5):
                if(tokens[0] == '/resolve'):
                    if(tokens[1] == 'name'):
                        parsedRequest['name'] = tokens[2]
                    if(tokens[3] == 'type'):
                        if(tokens[4] == 'A' or tokens[4] == 'PTR'):
                            parsedRequest['type'] = tokens[4]
                        else:
                            raise ipke.IncorrectGETFormatException
                    else:
                        raise ipke.IncorrectGETFormatException
                else:
                    raise ipke.IncorrectGETFormatException
            else:
                raise ipke.IncorrectGETFormatException
        else: #should only be POST
            #/dns-query
            if(m.group('url') == '/dns-query'):
                parsedRequest['name'] = ''
                parsedRequest['type'] = ''
            else:
                raise ipke.IncorrectURLRequestException
            
            #split header and body
            tmpHeader = list()
            tmpBody = list()
            for i, ln in enumerate(request[1:], 1):
                if(ln != ''):
                    tmpHeader.append(ln)
                else:
                    tmpBody = request[i+1:]
                    break
            
            parsedRequest['header'] = tmpHeader
            parsedRequest['body'] = tmpBody



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
            self.output.append(f'{self.name}:{self.nameType}={socket.gethostbyname(self.name)}\n')
        else:
            self.output.append(f'{self.name}:{self.nameType}={socket.gethostbyaddr(self.name)[0]}\n')


    def __doPOST(self):
        for ln in self.body:
            ln = ln.strip()

            if not ln:
                break

            parsed = ln.split(':')
            if(not parsed):
                raise ipke.IncorrectPOSTFormatException
            else:
                if(parsed[1] == 'A'):
                    self.output.append(f'{ln}={socket.gethostbyname(parsed[0])}\n')
                elif(parsed[1] == 'PTR'):
                    self.output.append(f'{ln}={socket.gethostbyaddr(parsed[0])[0]}\n')
                else:
                    raise ipke.IncorrectPOSTFormatException
            

    def getOutputBody(self):
        if(self.output):
            return self.output
        else:
            raise ipke.EmptyOutputException

    def getVersion(self):
        return self.version

class ipkResponse():
    def __init__(self, httpVersion, status, phrase, dateTime, body):
        self.httpVersion = httpVersion
        self.status = status
        self.phrase = phrase
        self.dateTime = dateTime
        self.body = body

    def outputResponse(self):
        output = f'{self.httpVersion} {self.status} {self.phrase}\n'
        output += 'Connection: close\n'
        output += f'Date: {self.dateTime}\n' #fix
        output += '\n'
        output += ''.join(self.body)

        return bytes(''.join(output), 'utf-8')

def handleArguments():
    argParser = argparse.ArgumentParser()
    argParser.add_argument('ip', type=str)
    argParser.add_argument('port', type=int)

    return argParser.parse_args()

def main():

    args = handleArguments()

    HOST = args.ip #'127.0.0.1'  # localhost
    PORT = args.port #5353        # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            try:
                conn, addr = s.accept()
                receivedInput = conn.recv(1024)
                #if not receivedInput:
                #    break
                data = re.split(r'\r\n', receivedInput.decode('utf-8'))

                try:
                    request = ipkRequest(data)
                    request.handleRequest()
                except (ipke.IllegalHTTPMethodException, ipke.IncorrectGETFormatException, ipke.IncorrectPOSTFormatException):
                    response = ipkResponse("HTTP/1.1", 400, "Bad Request", datetime.datetime.now(), "")
                except ipke.IllegalHTTPMethodException:
                    response = ipkResponse("HTTP/1.1", 405, "Method Not Allowed", datetime.datetime.now(), "")
                else:
                    response = ipkResponse(request.getVersion(), 200, "OK", datetime.datetime.now(), request.getOutputBody())

                conn.sendall(response.outputResponse())
                conn.close()
            except KeyboardInterrupt:
                break


main()