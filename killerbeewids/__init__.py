

class ErrorCodes:

    def __init__(self):

    self.ERROR_UNABLETOREACHWIDS  = 'W1'
    self.ERROR_UNABLETOREACHDRONE = 'D1'
    self.ERROR_MISSINGDRONETASKPARAMETER = 'D2'
    self.ERROR_InvalidDroneIndex = 'D3'

    self.__ERRORS = {
                'W1' : 'Unable to reach WIDS',
                'D1' : 'Unable to reach Drone',


             }

    def getError(self, code):
        return self.__ERRORS.get(code, None)
