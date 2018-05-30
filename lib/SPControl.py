from lib.SPDbCall import SPDbCall
from lib.SPDbCall import TypeAlarmAction
from lib.SPDbCall import TypeEnter
from Global import *

class SPControl:

    @staticmethod
    def get_code_empty_jail():
        return get_value_config('emptyjail', 'code')

    def enter_code(self, access_code):
        #retrieve user's data
        if access_code == SPControl.get_code_empty_jail():
            SPDbCall.empty_jail()
            #TODO: set empty jail like member.
            return 'EMPTY', 'JAIL', 'EMPTYJAIL', 4, '-1', True, TypeEnter.EXIT,  TypeAlarmAction.ACTIVATE, 0
        name, surname, talent_code, member_type, depending_on = SPDbCall.get_info_user(access_code)
        alarm_action = TypeAlarmAction.NOTHING
        type_enter = TypeEnter.NOTHING
        result = False
        #Talent Code is needed...
        if talent_code is not None and talent_code:
            #if user is online, access code will be interpreted in exit mode.
            type_enter = TypeEnter.ENTER
            if SPDbCall.is_online(talent_code):
                type_enter = TypeEnter.EXIT
                if self.check_dependence(depending_on, member_type, TypeEnter.EXIT):
                    result = SPDbCall.exit_user(talent_code)
                # if this user is the last one, activate alarm.
                if SPDbCall.n_user_online() == 0:
                    alarm_action = TypeAlarmAction.ACTIVATE
            #otherwise, enter mode...
            elif self.check_dependence(depending_on, member_type, TypeEnter.ENTER):
                result = SPDbCall.enter_user(talent_code, member_type)
            #if this user is the first one, deactivate alarm.
            if SPDbCall.n_user_online() == 1 and type_enter == TypeEnter.ENTER:
                alarm_action = TypeAlarmAction.DEACTIVATE
            SPDbCall.save_log(talent_code, member_type, type_enter, alarm_action)
        return name, surname, talent_code, member_type, depending_on, result, type_enter, alarm_action, SPDbCall.n_user_online()

    @staticmethod
    def check_dependence(depending_on, member_type, type_enter):
        if len(depending_on) == 1 and depending_on[0] == -1:
            return True
        if type_enter == TypeEnter.ENTER:
            return SPDbCall.n_type_user(depending_on) > 0
        else:
            return SPDbCall.n_type_user(SPDbCall.all_dependent_by(member_type)) == 0 or SPDbCall.n_type_user((member_type,)) > 1