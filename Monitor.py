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

class Monitor(object):
    __ENV_WORKSPACE = None
    __DATABASE_CONNECTION = None
    __DATABASE_CURSOR = None
    __POC_SCRIPT_FOLDER_PATH = None
    __pocInfoList = []
    __pocScriptUrlList = []

    def initializeConstantVariables(self):
        self.__ENV_WORKSPACE = os.getcwd()
        self.__DATABASE_CONNECTION = pymysql.connect(Constants.DATABASE_URL, Constants.DATABASE_USERNAME,
                                                     Constants.DATABASE_PASSWORD, Constants.DATABASE_NAME)
        self.__DATABASE_CURSOR = self.__DATABASE_CONNECTION.cursor()
        self.__POC_SCRIPT_FOLDER_PATH = self.__ENV_WORKSPACE + "/" + Constants.POC_SCRIPT_FOLDER_NAME

    def updatePocInfo(self):
        self.updatePocInfoInDatabase()
        self.updateLocalPocFile()

    def updatePocInfoInDatabase(self):
        self.clearPocInfoInDatabase()
        self.collectPocInfoFromWebsite()
        self.insertPocInfoIntoDatabase()

    def clearPocInfoInDatabase(self):
        deleteStatement = "DELETE FROM " + Constants.POC_INFO_TABLE_NAME
        self.__DATABASE_CONNECTION.execute(deleteStatement)
        self.__DATABASE_CONNECTION.commit()

    def collectPocInfoFromWebsite(self):
        pageSource = requests.get(Constants.RAW_POC_LIST)
        self.__pocInfoList = json.loads(pageSource.text)

    def insertPocInfoIntoDatabase(self):
        insertStatementTemplate = "INSERT INTO %s (%s, %s, %s, %s, %s)"
        for pocItem in self.__pocInfoList:
            insertStatement = insertStatementTemplate % (
                Constants.POC_INFO_TABLE_NAME, pocItem[Constants.POC_INFO_TABLE_FIELDS[1]],
                pocItem[Constants.POC_INFO_TABLE_FIELDS[2]], pocItem[Constants.POC_INFO_TABLE_FIELDS[3]],
                pocItem[Constants.POC_INFO_TABLE_FIELDS[4]], pocItem[Constants.POC_INFO_TABLE_FIELDS[5]])
            self.__DATABASE_CURSOR.execute(insertStatement)
            # The performance may be better if this statement was put out of the for-loop, but not sure if there is any
            # error occurs.
            self.__DATABASE_CONNECTION.commit()

    def updateLocalPocFile(self):
        self.removeLocalPocFile()
        self.constructPocScriptUrlList()
        self.downloadPocFile()

    def removeLocalPocFile(self):
        shutil.rmtree(self.__POC_SCRIPT_FOLDER_PATH)
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
        workspacePath = self.__ENV_WORKSPACE
        savePath = pocScriptUrl.replace(Constants.RAW_POC_SCRIPT_ROOT_PATH, workspacePath)
        return savePath

    @staticmethod
    def savePocScriptCodeToSpecifiedPath(pocScriptCode, pocScriptSavePath):
        pass

    def getPocInfoList(self):
        return self.__pocInfoList

    def getPocScriptUrlList(self):
        return self.__pocScriptUrlList

    def releaseResources(self):
        self.__DATABASE_CONNECTION.close()


if __name__ == '__main__':
    monitor = Monitor()
    Monitor.initializeConstantVariables(monitor)
    Monitor.collectPocInfoFromWebsite(monitor)
    Monitor.constructPocScriptUrlList(monitor)
    urlList = Monitor.getPocScriptUrlList(monitor)
    # print(urlList)
    # print(monitor.acquirePocScriptCode("https://raw.githubusercontent.com/boy-hack/airbug/master/cms/typecho/typoecho_install_rce/poc.py"))
    pocScriptSavePath1 = monitor.constructSavePathOfPocScript("https://raw.githubusercontent.com/boy-hack/airbug/master/cms/typecho/typoecho_install_rce/poc.py")
    print(pocScriptSavePath1)
