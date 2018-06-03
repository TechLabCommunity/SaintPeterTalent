from threading import Thread
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from lib.SPDbCall import SPDbCall
from Global import *
from lib.AccessLogger import AccessLogger

class S(BaseHTTPRequestHandler):


    PATH_LOG = './log/httplog.txt'
    logger = AccessLogger(PATH_LOG)

    def setup(self):
        BaseHTTPRequestHandler.setup(self)
        self.request.settimeout(2)


    def _set_headers(self, error=False):
        self.send_response(500 if error else 200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'https://gestionale.talentlabpadova.org')
        self.end_headers()

    def do_POST(self):

        try:
            data_string = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8').strip().replace('\r', '').replace('\n','').replace('\t', '')
            self.logger.log("Rec : "+data_string)
            json_rec = json.loads(data_string)
            if not self.execute_json(json_rec):
                raise ValueError('JSON is not valid.')
            ok_resp = {'response' : True}
            self._set_headers()
            self.wfile.write(str(json.dumps(ok_resp, ensure_ascii=False)).encode("utf-8"))
            self.logger.log("Response : OK")
        except:
            self.logger.log("Response : FAIL")
            self._set_headers(True)
        return

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

class SpmSocketJSON(Thread):

    NAMEMODULE = "HttpServer"

    def __init__(self):
        print(self.NAMEMODULE)
        Thread.__init__(self)

    def run(self):
        port = int(get_value_config("socketconf", "port"))
        server_address = ('', port)
        httpd = HTTPServer(server_address, S)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()

