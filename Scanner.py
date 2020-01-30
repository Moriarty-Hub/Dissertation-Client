import os
import pymysql
from abc import ABC
from importlib.abc import Loader

import Constants


class PocLoader(Loader, ABC):
    __pocName = None
    __pocPath = None
    __pocSourceCode = None

    def __init__(self, pocName, pocPath):
        self.__pocName = pocName
        self.__pocPath = pocPath
        self.__acquirePocSourceCode()

    def __acquirePocSourceCode(self):
        pocFile = open(self.__pocPath)
        self.__pocSourceCode = pocFile.read()
        pocFile.close()

    def executePocScript(self, module):
        objectCode = compile(self.__pocSourceCode, self.__pocName, mode='exec', dont_inherit=True)
        exec(objectCode, module.__dict__)


class Scanner(object):
    __WORKSPACE = None
    __DATABASE_CONNECTION = None
    __DATABASE_CURSOR = None
    __urlTargetList = None
    __hostTargetList = None
    __pocScriptPathList = None

    def __init__(self, urlTargetList, hostTargetList):
        self.__WORKSPACE = os.getcwd()
        self.__DATABASE_CONNECTION = pymysql.connect(Constants.DATABASE_URL, Constants.DATABASE_USERNAME,
                                                     Constants.DATABASE_PASSWORD, Constants.DATABASE_NAME)
        self.__DATABASE_CURSOR = self.__DATABASE_CONNECTION.cursor()
        self.__urlTargetList = urlTargetList
        self.__hostTargetList = hostTargetList
        self.__acquirePocScriptPathFromDatabase()

    def __acquirePocScriptPathFromDatabase(self):
        
