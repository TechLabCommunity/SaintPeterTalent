from threading import Thread
import socket
import json
from time import sleep
from Global import *

class SpmSocketJSON(Thread):

    NAMEMODULE = 'Socket'

    def __init__(self):
        print(self.NAMEMODULE)
        Thread.__init__(self)

    def get_binding_socket(self):
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                host = get_value_config('socketconf', 'host')
                port = int(get_value_config('socketconf', 'port'))
                s.bind((host, port))
                s.listen(1)
                return s
            except:
                print("Binding failed socket. Retry...")
                sleep(1)

    @staticmethod
    def clientthread(conn):
        print("Client connection")
        while True:
            try:
                data = conn.recv(1024).decode("utf-8").strip()
                json_rec = json.loads(data)
                print(json_rec)
                #TODO
                conn.close()
                print("Client close")
                break
            except:
                conn.close()
                print("Client close with exception")
                break

    def run(self):
        jsock = self.get_binding_socket()
        while True:
            try:
                conn, addr = jsock.accept()
                conn.settimeout(5)
                print('Connected with ' + addr[0] + ':' + str(addr[1]))
                Thread(target=self.clientthread, args = (conn,)).start()
            except:
                jsock = self.get_binding_socket()
                pass
