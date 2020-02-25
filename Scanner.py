# NOTICE
# You need to install HackRequest and scapy module before running this script

import os
import pymysql
import importlib

import Constants


class Scanner(object):
    __WORKSPACE = None
    __DATABASE_CONNECTION = None
    __DATABASE_CURSOR = None
    __POC_INFO_LIST = None
    __urlTargetsList = None
    __hostTargetsList = None
    __nameListOfPocScriptForUrlTarget = ["typecho", "zzcms", "phpcms", "metinfo", "pbootcms", "ecshop", "emlog",
                                         "siteserver", "beescms", "discuz", "empirecms", "weblogic", "grafana",
                                         "phpstudy", "phpcms", "thinkphp", "hfs", "axis", "confluence", "iis",
                                         "coremail", "rails", "www_common", "tomcat"]
    __nameListOfPocScriptForHostTarget = ["wordpress", "thinkphp", "dedecms", "ftp", "weblogic", "tomcat",
                                          "phpstudy", "php", "smtp", "hfs", "windows", "zabbix"]

    def __init__(self, urlTargetsList, hostTargetsList):
        self.__WORKSPACE = os.getcwd()
        self.__DATABASE_CONNECTION = pymysql.connect(Constants.DATABASE_URL, Constants.DATABASE_USERNAME,
                                                     Constants.DATABASE_PASSWORD, Constants.DATABASE_NAME)
        self.__DATABASE_CURSOR = self.__DATABASE_CONNECTION.cursor()
        self.__POC_INFO_LIST = self.__acquirePocInfoFromDatabase()
        self.__urlTargetsList = urlTargetsList
        self.__hostTargetsList = hostTargetsList

    def __acquirePocInfoFromDatabase(self):
        selectStatementTemplate = "SELECT %s, %s, %s, %s, %s FROM %s"
        selectStatement = selectStatementTemplate % (Constants.POC_INFO_TABLE_FIELDS[1],
                                                     Constants.POC_INFO_TABLE_FIELDS[2],
                                                     Constants.POC_INFO_TABLE_FIELDS[3],
                                                     Constants.POC_INFO_TABLE_FIELDS[4],
                                                     Constants.POC_INFO_TABLE_FIELDS[5],
                                                     Constants.POC_INFO_TABLE_NAME)
        self.__DATABASE_CURSOR.execute(selectStatement)
        result = self.__DATABASE_CURSOR.fetchall()
        pocInfoList = []
        for row in result:
            pocInfo = {"name": row[0], "type": row[1], "file_path": row[2], "create_time": row[3], "url": row[4]}
            pocInfoList.append(pocInfo)
        return pocInfoList

    def execute(self):
        self.__deleteInactiveHostFromHostList()
        self.__clearDatabaseContent()
        self.__scanTargetsOfSpecifiedType("url")
        self.__scanTargetsOfSpecifiedType("host")
        self.__commitModificationToDatabase()
        self.__releaseResources()

    def __deleteInactiveHostFromHostList(self):
        targetListCopy = list(self.__hostTargetsList)
        for target in targetListCopy:
            os.system("ping -w 4 %s | tail -n 2 | head -n 1 > pingResult.txt" % target)
            file = open("pingResult.txt")
            result = file.read()
            file.close()
            if "0 received, 100% packet loss" in result:
                self.__hostTargetsList.remove(target)

    def __clearDatabaseContent(self):
        deleteStatement = "DELETE FROM " + Constants.SCAN_RESULT_TABLE_NAME
        self.__DATABASE_CURSOR.execute(deleteStatement)

    def __scanTargetsOfSpecifiedType(self, targetType):
        if targetType == "url":
            for target in self.__urlTargetsList:
                resultList = self.__scan(target, self.__nameListOfPocScriptForUrlTarget)
                self.__saveResultListOfSingleTargetIntoDatabase(target, "url", resultList)
        else:
            for target in self.__hostTargetsList:
                resultList = self.__scan(target, self.__nameListOfPocScriptForHostTarget)
                self.__saveResultListOfSingleTargetIntoDatabase(target, "host", resultList)

    def __scan(self, target, keywordList):
        resultList = []
        for keyword in keywordList:
            moduleNameList = self.__acquireModuleNameOfSpecifiedKeyword(keyword)
            for moduleName in moduleNameList:
                module = importlib.import_module(moduleName)
                try:
                    result = module.poc(target)
                    if result:
                        resultList.append(result)
                except:
                    pass
        return resultList

    def __acquireModuleNameOfSpecifiedKeyword(self, keyword):
        moduleNameList = []
        for pocInfo in self.__POC_INFO_LIST:
            if pocInfo["name"] == keyword:
                moduleName = self.__stripTheSuffixOfPythonFile(Constants.POC_SCRIPT_FOLDER_NAME + pocInfo["file_path"]) \
                    .replace("/", ".")
                moduleNameList.append(moduleName)
        return moduleNameList

    @staticmethod
    def __stripTheSuffixOfPythonFile(fileName):
        return fileName[:-3]

    def __saveResultListOfSingleTargetIntoDatabase(self, target, targetType, resultList):
        for result in resultList:
            insertStatementTemplate = "INSERT INTO %s (%s, %s, %s) VALUES (\"%s\", \"%s\", \"%s\")"
            insertStatement = insertStatementTemplate % (Constants.SCAN_RESULT_TABLE_NAME,
                                                         Constants.SCAN_RESULT_TABLE_FIELDS[0],
                                                         Constants.SCAN_RESULT_TABLE_FIELDS[1],
                                                         Constants.SCAN_RESULT_TABLE_FIELDS[2],
                                                         target, targetType, pymysql.escape_string(str(result)))
            self.__DATABASE_CURSOR.execute(insertStatement)

    def __commitModificationToDatabase(self):
        self.__DATABASE_CONNECTION.commit()

    def __releaseResources(self):
        self.__DATABASE_CURSOR.close()
        self.__DATABASE_CONNECTION.close()


def fillTargetList(urlTargetList, hostTargetList):
    connection = pymysql.connect(Constants.DATABASE_URL, Constants.DATABASE_USERNAME, Constants.DATABASE_PASSWORD,
                                 Constants.DATABASE_NAME)
    cursor = connection.cursor()
    selectStatementTemplate = "SELECT %s, %s FROM %s"
    selectStatement = selectStatementTemplate % (Constants.TARGET_TABLE_FIELDS[1], Constants.TARGET_TABLE_FIELDS[2],
                                                 Constants.TARGET_TABLE_NAME)
    cursor.execute(selectStatement)
    result = cursor.fetchall()
    for row in result:
        if row[1] == "url":
            urlTargetList.append(row[0])
        else:
            hostTargetList.append(row[0])


if __name__ == "__main__":
    urlList = []
    hostList = []
    fillTargetList(urlList, hostList)
    scanner = Scanner(urlList, hostList)
    scanner.execute()
