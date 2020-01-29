"""
Task list:
1. Listening on server's commands
2. Update poc_info in database and download poc script
3. Start Scanner.py
4. Kill the thread of Scanner.py if server require or time was used up
5. Export environment variables
"""

import os
import json
import pymysql
import requests
import shutil

import Constants


# The monitor is consist of two threads, one for listening server's command, the other one for executing

class PocInfoUpdater(object):
    __WORKSPACE = None
    __DATABASE_CONNECTION = None
    __DATABASE_CURSOR = None
    __POC_SCRIPT_FOLDER_PATH = None
    __pocInfoList = []
    __pocScriptUrlList = []

    def execute(self):
        self.initializeEnvironmentVariables()
        self.updatePocInfo()

    def initializeEnvironmentVariables(self):
        self.__WORKSPACE = os.getcwd()
        self.__DATABASE_CONNECTION = pymysql.connect(Constants.DATABASE_URL, Constants.DATABASE_USERNAME,
                                                     Constants.DATABASE_PASSWORD, Constants.DATABASE_NAME)
        self.__DATABASE_CURSOR = self.__DATABASE_CONNECTION.cursor()
        self.__POC_SCRIPT_FOLDER_PATH = self.__WORKSPACE + "/" + Constants.POC_SCRIPT_FOLDER_NAME

    def updatePocInfo(self):
        self.updatePocInfoInDatabase()
        self.updateLocalPocFile()

    def updatePocInfoInDatabase(self):
        self.clearPocInfoInDatabase()
        self.collectPocInfoFromWebsite()
        self.insertPocInfoIntoDatabase()

    def clearPocInfoInDatabase(self):
        deleteStatement = "DELETE FROM " + Constants.POC_INFO_TABLE_NAME
        self.__DATABASE_CURSOR.execute(deleteStatement)
        self.__DATABASE_CONNECTION.commit()

    def collectPocInfoFromWebsite(self):
        pageSource = requests.get(Constants.RAW_POC_LIST)
        self.__pocInfoList = json.loads(pageSource.text)

    def insertPocInfoIntoDatabase(self):
        insertStatementTemplate = "INSERT INTO %s (%s, %s, %s, %s, %s) VALUES (\"%s\", \"%s\", \"%s\", \"%s\", \"%s\")"
        for pocItem in self.__pocInfoList:
            insertStatement = insertStatementTemplate % (
                Constants.POC_INFO_TABLE_NAME, Constants.POC_INFO_TABLE_FIELDS[1], Constants.POC_INFO_TABLE_FIELDS[2],
                Constants.POC_INFO_TABLE_FIELDS[3], Constants.POC_INFO_TABLE_FIELDS[4],
                Constants.POC_INFO_TABLE_FIELDS[5], pocItem[Constants.RAW_POC_LIST_KEYS[0]],
                pocItem[Constants.RAW_POC_LIST_KEYS[1]], pocItem[Constants.RAW_POC_LIST_KEYS[2]],
                pocItem[Constants.RAW_POC_LIST_KEYS[3]],
                Constants.RAW_POC_SCRIPT_ROOT_PATH + pocItem[Constants.RAW_POC_LIST_KEYS[2]])
            self.__DATABASE_CURSOR.execute(insertStatement)
            # The performance may be better if this statement was put out of the for-loop, but not sure if there is any
            # error occurs.
            self.__DATABASE_CONNECTION.commit()

    def updateLocalPocFile(self):
        self.removeLocalPocFile()
        self.constructPocScriptUrlList()
        self.downloadPocFile()

    def removeLocalPocFile(self):
        shutil.rmtree(path=self.__POC_SCRIPT_FOLDER_PATH, ignore_errors=True)
        os.mkdir(self.__POC_SCRIPT_FOLDER_PATH)

    def constructPocScriptUrlList(self):
        for item in self.__pocInfoList:
            self.__pocScriptUrlList.append(Constants.RAW_POC_SCRIPT_ROOT_PATH + item['filepath'])

    def downloadPocFile(self):
        for pocScriptUrl in self.__pocScriptUrlList:
            pocScriptCode = self.acquirePocScriptCode(pocScriptUrl)
            pocScriptSavePath = self.constructSavePathOfPocScript(pocScriptUrl)
            self.savePocScriptCodeToSpecifiedPath(pocScriptCode, pocScriptSavePath)

    @staticmethod
    def acquirePocScriptCode(pocScriptUrl):
        pageSource = requests.get(pocScriptUrl)
        pocScriptCode = pageSource.text
        return pocScriptCode

    def constructSavePathOfPocScript(self, pocScriptUrl):
        workspacePath = self.__WORKSPACE
        pocScriptFolderPath = workspacePath + "/" + Constants.POC_SCRIPT_FOLDER_NAME + "/"
        savePath = pocScriptUrl.replace(Constants.RAW_POC_SCRIPT_ROOT_PATH, workspacePath)
        return savePath

    def savePocScriptCodeToSpecifiedPath(self, pocScriptCode, pocScriptSavePath):
        directoryPath = self.acquireDirectoryPath(pocScriptSavePath)
        self.makeDirectoryIfNotExists(directoryPath)
        pocScript = open(pocScriptSavePath, "w")
        pocScript.write(pocScriptCode)
        pocScript.close()

    @staticmethod
    def acquireDirectoryPath(pocScriptSavePath):
        splitIndex = pocScriptSavePath.rfind("/") + 1
        directoryPath = pocScriptSavePath[:splitIndex]
        return directoryPath

    @staticmethod
    def makeDirectoryIfNotExists(directoryPath):
        if not os.path.exists(directoryPath):
            os.makedirs(directoryPath)

    def getPocInfoList(self):
        return self.__pocInfoList

    def getPocScriptUrlList(self):
        return self.__pocScriptUrlList

    def releaseResources(self):
        self.__DATABASE_CONNECTION.close()


if __name__ == '__main__':
    pocInfoUpdater = PocInfoUpdater()
    PocInfoUpdater.execute(pocInfoUpdater)
