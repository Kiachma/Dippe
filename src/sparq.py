import socket
from pyparsing import nestedExpr


class Sparq:
    class __Sparq:

        def __init__(self):
            self.CRLF = "\r\n"  # Definelineendings
            # createasocketandconnect
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.connect(('127.0.0.1', 4443))
            self.sockfile = self.sock.makefile('rw')

        def __str__(self):
            return repr(self) + self.val

    instance = None

    def __init__(self):
        if not Sparq.instance:
            Sparq.instance = Sparq.__Sparq()
        else:
            Sparq.instance.CRLF = "\r\n"

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def readline(self):
        input = self.sockfile.readline()
        if not input:
            raise EOFError
        if input[-2:] == self.CRLF:  # striplineendings
            input = input[:-2]
        elif input[-1:] in self.CRLF:
            input = input[:-1]
        if len(input) == 0:
            return self.readline()
        if input[0] == ";":  # ignorecomments
            return self.readline()
        else:
            return input

    def sendline(self, line):  # sendalinetoSparq
        self.sock.send(line + self.CRLF)

    def removePrompt(self, line):  # remove"Sparq>"prompt
        return line[line.find('>') + 1:]

    def close_sparq(self):
        # self.sendline("quit")
        self.sock.close()

    def read_line_and_remove_prompt(self):
        return self.removePrompt(self.readline())

    def parse_scene_to_tuples(self, reponse):
        return nestedExpr('(', ')').parseString(reponse).asList()[0]

    def parse_relation_tuples(self, tuples):

        relations = []
        for tuple in tuples:
            opras = tuple[1][0].split('_')
            relations = relations + [
                {
                    'from': tuple[0],
                    'OPRA1': int(opras[0]),
                    'OPRA2': int(opras[1]),
                    'to': tuple[2]
                }
            ]
        return relations
