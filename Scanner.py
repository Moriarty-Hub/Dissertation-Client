# NOTICE
# You need to install HackRequest and scapy module before running this script

import os
import pymysql

import airbug
import Constants


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
                                                     Constants.POC_INFO_TABLE_NAME)
        self.__DATABASE_CURSOR.execute(selectStatement)
        results = self.__DATABASE_CURSOR.fetchall()
        for row in results:
            self.__pocScriptRecordList.append([row[0], row[1], self.__WORKSPACE + "/" +
                                               Constants.POC_SCRIPT_FOLDER_NAME + row[2]])

    def execute(self):
        self.__scanTargets("url")
        self.__scanTargets("host")

    def __scanTargets(self, targetType):
        if targetType == "url":
            targetList = self.__urlTargetsList
            keywordList = self.__nameListOfPocScriptForUrlTarget
        else:
            targetList = self.__hostTargetsList
            keywordList = self.__nameListOfPocScriptForHostTarget
        for target in targetList:
            resultList = []
            result = airbug.run_airbug(target, keywordList)
            if result:
                resultList.append(result)
            else:
                print("No issue was detected.")
            print("Report for " + target)
            for result in resultList:
                print(result)
            print("======================================")


if __name__ == "__main__":
    scanner = Scanner(["https://x.hacking8.com", "http://45.32.224.205:8080/"], ["47.98.53.171"])
    scanner.execute()
