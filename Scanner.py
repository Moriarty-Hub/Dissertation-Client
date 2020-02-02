# NOTICE
# You need to install HackRequest and scapy module before running this script

import os
import pymysql

import Constants
import airbug


class Scanner(object):
    __WORKSPACE = None
    __DATABASE_CONNECTION = None
    __DATABASE_CURSOR = None
    __urlTargetsList = None
    __hostTargetsList = None
    __resultOfSingleTarget = []
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

    def execute(self):
        self.__clearDatabaseContent()
        self.__scanTargets("url")
        self.__scanTargets("host")
        self.__commitModificationToDatabase()
        self.__releaseResources()

    def __clearDatabaseContent(self):
        deleteStatement = "DELETE FROM " + Constants.SCAN_RESULT_TABLE_NAME
        self.__DATABASE_CURSOR.execute(deleteStatement)

    def __scanTargets(self, targetType):
        if targetType == "url":
            targetList = self.__urlTargetsList
            keywordList = self.__nameListOfPocScriptForUrlTarget
        else:
            targetList = self.__hostTargetsList
            keywordList = self.__nameListOfPocScriptForHostTarget
        for target in targetList:
            result = airbug.run_airbug(target, keywordList)
            if result:
                print("Issue was detected on target " + target)
                result = self.__DATABASE_CONNECTION.escape(result)
                self.__resultOfSingleTarget = {"name": target, "target_type": targetType, "description": result}
                self.__saveResultOfSingleTargetIntoDatabase()

    def __saveResultOfSingleTargetIntoDatabase(self):
        insertStatementTemplate = "INSERT INTO %s (%s, %s, %s) VALUES (%s, %s, %s)"
        insertStatement = insertStatementTemplate % (Constants.SCAN_RESULT_TABLE_NAME,
                                                     Constants.SCAN_RESULT_TABLE_FIELDS[0],
                                                     Constants.SCAN_RESULT_TABLE_FIELDS[1],
                                                     Constants.SCAN_RESULT_TABLE_FIELDS[2],
                                                     self.__resultOfSingleTarget["name"],
                                                     self.__resultOfSingleTarget["target_type"],
                                                     self.__resultOfSingleTarget["description"])
        self.__DATABASE_CURSOR.execute(insertStatement)

    def __commitModificationToDatabase(self):
        self.__DATABASE_CONNECTION.commit()

    def __releaseResources(self):
        self.__DATABASE_CURSOR.close()
        self.__DATABASE_CONNECTION.close()


if __name__ == "__main__":
    scanner = Scanner(["https://x.hacking8.com", "http://45.32.224.205:8080/"], ["47.98.53.171"])
    scanner.execute()
