from threading import Thread
import json
from time import sleep
from lib.SPDbCall import SPDbCall
from Global import *
import requests
from lib.AccessLogger import AccessLogger

class SpmUpdateAccessCode(Thread):

    NAMEMODULE = "HttpServer"
    PATH_LOG = './log/updateaccesscode.txt'

    def __init__(self):
        print(self.NAMEMODULE)
        Thread.__init__(self)

    def run(self):
        logger = AccessLogger(self.PATH_LOG)
        delta = 1
        while True:
            try:
                logger.log("Starting update...")
                json_send = {
                    "token": get_value_config("socketconf", "token"),
                    "entity": "TalentMembers",
                    "type_request": "query",
                    "range": [0+delta-1, 9+delta]
                }
                request = requests.post(get_value_config("socketconf", "urlrequest"), json=json_send)
                logger.log('from %s to %s' % (0+delta-1, 9+delta))
                json_resp = json.loads(request.text)
                SpmUpdateAccessCode.execute_json(json_resp)
                if not json_resp['response']:
                    logger.log('End. Ready to restart! Waiting : '+str(get_value_config("socketconf", "timeout")))
                    delta = 0
                    sleep(int(get_value_config("socketconf", "timeout")))
                    continue
                delta = delta + 10
            except:
                logger.log("Error in update.")


    @staticmethod
    def execute_json(json_req):
        try:
            if "token" in json_req and json_req['token'] == get_value_config('socketconf', 'token'):
                if "type_request" not in json_req or json_req["type_request"] not in ['query']:
                    return False
                # TODO backup, log.
                controller = json_req['entity']
                table_name = None
                if controller == 'TalentMembers':
                    table_name = 'talent_members'
                elif controller == 'OldMembersAccesses':
                    table_name = 'old_members_accesses'
                if not table_name:
                    return False
                for member in json_req['response']:
                    talent_code = SPDbCall.exists_talent_code(member['TalentCode'])
                    if talent_code is None:
                        SPDbCall.insert_member(table_name, member)
                        print("insert " + str(member['Name']) + "," + str(member['Surname'])+ ","+ str(member['TalentCode']))
                    else:
                        SPDbCall.update_accesscode(table_name, member['AccessCode'], member['TalentCode'])
                        print("update " + str(member['Name']) + "," + str(member['Surname'])+ ","+ str(member['TalentCode']))
                return True
        except:
            return False

