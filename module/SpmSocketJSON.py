from threading import Thread
import socket
import json
from time import sleep
from lib.SPDbCall import SPDbCall
from Global import *
from lib.AccessLogger import AccessLogger

class SpmSocketJSON(Thread):

    NAMEMODULE = 'Socket'
    PATH_LOG = './log/socket.txt'

    def __init__(self):
        print(self.NAMEMODULE)
        Thread.__init__(self)

    def get_binding_socket(self):
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                host = ''
                port = int(get_value_config('socketconf', 'port'))
                s.bind((host, port))
                s.listen(1)
                return s
            except:
                print("Binding failed socket. Retry...")
                sleep(1)

    def clientthread(self, conn):
        print("Client connection")
        logger = AccessLogger(self.PATH_LOG)
        while True:
            try:
                data = conn.recv(2048).decode("utf-8").strip()
                logger.log(data)
                json_rec = json.loads(data)
                if not SpmSocketJSON.execute_json(json_rec):
                    logger.log("Error : "+str(json_rec))
                    raise ValueError
            except:
                conn.close()
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

    @staticmethod
    def execute_json(json_req):
        try:
            if "token" in json_req and json_req['token'] == get_value_config('socketconf', 'token'):
                if "type_request" not in json_req or json_req["type_request"] not in ['save']:
                    return False
                if json_req['type_request'] == 'save':
                    #TODO backup, log.
                    table_name = json_req['table_name']
                    member = json_req['member']
                    talent_code = SPDbCall.exists_talent_code(member['TalentCode'])
                    if talent_code is None:
                        SPDbCall.insert_member(table_name, member)
                    else:
                        SPDbCall.update_accesscode(table_name, member['AccessCode'], member['TalentCode'])
                    print("update "+str(member['Name'])+","+str(member['Surname']))
                    return True
        except Exception:
            return False
