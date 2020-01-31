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
    __urlTargetsList = None
    __hostTargetsList = None
    __pocScriptRecordList = []
    __nameListOfPocScriptForUrlTarget = ["typecho", "zzcms", "phpcms", "metinfo", "pbootcms", "ecshop", "emlog",
                                         "siteserver", "beescms", "discuz", "empirecms", "weblogic", "grafana",
                                         "phpstudy", "phpcms", "thinkphp", "hfs", "axis", "confluence", "iis",
                                         "coremail", "rails", "www_common"]
    __nameListOfPocScriptForHostTarget = ["wordpress", "thinkphp", "dedecms", "hardware", "ftp", "weblogic", "tomcat",
                                          "phpstudy", "php", "smtp", "hfs", "windows", "zabbix", ""]
    __summaryListOfUrlTargets = []
    __summaryListOfHostTargets = []

    def __init__(self, urlTargetsList, hostTargetsList):
        self.__WORKSPACE = os.getcwd()
        self.__DATABASE_CONNECTION = pymysql.connect(Constants.DATABASE_URL, Constants.DATABASE_USERNAME,
                                                     Constants.DATABASE_PASSWORD, Constants.DATABASE_NAME)
        self.__DATABASE_CURSOR = self.__DATABASE_CONNECTION.cursor()
        self.__urlTargetsList = urlTargetsList
        self.__hostTargetsList = hostTargetsList
        self.__acquireAllPocScriptPathFromDatabase()

    def __acquireAllPocScriptPathFromDatabase(self):
        selectStatementTemplate = "SELECT %s, %s, %s FROM %s"
        selectStatement = selectStatementTemplate % (Constants.POC_INFO_TABLE_FIELDS[1],
                                                     Constants.POC_INFO_TABLE_FIELDS[2],
                                                     Constants.POC_INFO_TABLE_FIELDS[3],
                                                     Constants.POC_SCRIPT_FOLDER_NAME)
        self.__DATABASE_CURSOR.execute(selectStatement)
        results = self.__DATABASE_CURSOR.fetchall()
        for row in results:
            self.__pocScriptRecordList.append([row[0], row[1], self.__WORKSPACE + "/" +
                                               Constants.POC_SCRIPT_FOLDER_NAME + row[2]])

    def execute(self):
        self.__scanUrlTargets()
        self.__scanHostTargets()
        self.__generateSummary()

    def __scanUrlTargets(self):
        pocScriptRecordListForUrlTarget = self.__filterOutPocScriptRecordForSpecifiedTarget("url")
        for record in pocScriptRecordListForUrlTarget:
            pocLoader = PocLoader(record[0])

    def __scanHostTargets(self):
        pocScriptRecordListForHostTarget = self.__filterOutPocScriptRecordForSpecifiedTarget("host")

    def __filterOutPocScriptRecordForSpecifiedTarget(self, targetType):
        if targetType == "url":
            pocScriptRecordListForUrlTarget = []
            for pocRecord in self.__pocScriptRecordList:
                if pocRecord[0] in self.__nameListOfPocScriptForUrlTarget:
                    pocScriptRecordListForUrlTarget.append(pocRecord)
            return pocScriptRecordListForUrlTarget
        else:
            pocScriptRecordListForHostTarget = []
            for pocRecord in self.__pocScriptRecordList:
                if pocRecord[0] in self.__nameListOfPocScriptForHostTarget:
                    pocScriptRecordListForHostTarget.append(pocRecord)
            return pocScriptRecordListForHostTarget

    def __generateSummary(self):
        pass
