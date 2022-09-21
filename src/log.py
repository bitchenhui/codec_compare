# public log module
# log will be stored in bin folder and named as x_warn_x_error.txt
# import log
# log.info('aaa')
# log.warn('aaa')
# log.error('aaa')
import codecs
import os


class Log(object):
    __instance = None

    def __init__(self):
        self._lines = ['']
        self._warnCount = 0
        self._errorCount = 0

    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = Log()
        return cls.__instance

    def info(self, text):
        print(text)
        self._lines.append('\n' + text)

    def warn(self, text):
        self._warnCount = self._warnCount + 1
        text = 'warn {} : {}'.format(self._warnCount, text)
        print(text)
        self._lines.append('\n' + text)

    def error(self, text):
        self._errorCount = self._errorCount + 1
        text = 'error {} : {}'.format(self._errorCount, text)
        print(text)
        self._lines.append('\n' + text)

    def save_to(self, file_path):
        if os.path.isfile(file_path):
            os.remove(file_path)

        file = codecs.open(file_path, 'w', 'utf-8-sig')
        file.writelines(self._lines)
        file.close()

    def clear(self):
        self._lines = ['']
        self._warnCount = 0
        self._errorCount = 0

def info(text):
    Log.instance().info(text)


def warn(text):
    Log.instance().warn(text)


def error(text):
    Log.instance().error(text)
