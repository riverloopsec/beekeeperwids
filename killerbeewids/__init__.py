

class ErrorCodes:

    ERROR_GENERAL_UnknownException          = 'G1'
    ERROR_GENERAL_UnknownUrllib2Error       = 'G2'
    ERROR_WIDS_ConnectionRefused            = 'W1'
    ERROR_DRONE_MissingTaskingParameter     = 'D2'
    ERROR_DRONE_UnavailableInterface        = 'D3'
    ERROR_DRONE_UnavailablePlugin           = 'D4'
    ERROR_DRONE_TaskDoesNotExist            = 'D5'
    ERROR_DRONE_UnknownTaskingFailure       = 'D6'
    ERROR_DRONE_UnknownDetaskingFailure     = 'D7'
    ERROR_DRONE_ConnectionRefused           = 'D8'


    @staticmethod
    def getError(code):
        ERRORS = {
            'G1' : 'Unknown Exception Encountered',
            'G2' : 'Unknown urllib2 exception encountered',
            'W1' : 'Unable to reach WIDS: connection refused',
            'D1' : 'Unable to reach Drone',
            'D2' : 'Missing Tasking Parameter',
            'D3' : 'Unavailable Interface',
            'D4' : 'Unavilable Plugin',
            'D5' : 'Task Does Not Exist',
            'D6' : 'Unknown Tasking Failure',
            'D7' : 'Unknown Detasking Failure',
            'D8' : 'Unable to connect to Drone: Connection Refused',
        }
        return ERRORS.get(code, 'ErrorCode ({0}) does not exist'.format(code))
