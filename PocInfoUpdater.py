import os
import json
import pymysql
import requests
import shutil

import Constants


class PocInfoUpdater(object):
    __WORKSPACE = None
    __DATABASE_CONNECTION = None
    __DATABASE_CURSOR = None
    __POC_SCRIPT_FOLDER_PATH = None
    __pocInfoList = []
    __pocScriptUrlList = []

    def getPocInfoList(self):
        return self.__pocInfoList

    def getPocScriptUrlList(self):
        return self.__pocScriptUrlList

    def execute(self):
        self.__initializeEnvironmentVariables()
        self.__updatePocInfo()
        self.__releaseResources()

    def __initializeEnvironmentVariables(self):
        self.__WORKSPACE = os.getcwd()
        self.__DATABASE_CONNECTION = pymysql.connect(Constants.DATABASE_URL, Constants.DATABASE_USERNAME,
                                                     Constants.DATABASE_PASSWORD, Constants.DATABASE_NAME)
        self.__DATABASE_CURSOR = self.__DATABASE_CONNECTION.cursor()
        self.__POC_SCRIPT_FOLDER_PATH = self.__WORKSPACE + "/" + Constants.POC_SCRIPT_FOLDER_NAME

    def __updatePocInfo(self):
        self.__updatePocInfoInDatabase()
        self.__updateLocalPocFile()

    def __updatePocInfoInDatabase(self):
        self.__clearPocInfoInDatabase()
        self.__collectPocInfoFromWebsite()
        self.__insertPocInfoIntoDatabase()

    def __clearPocInfoInDatabase(self):
        deleteStatement = "DELETE FROM " + Constants.POC_INFO_TABLE_NAME
        self.__DATABASE_CURSOR.execute(deleteStatement)
        self.__DATABASE_CONNECTION.commit()

    def __collectPocInfoFromWebsite(self):
        pageSource = requests.get(Constants.RAW_POC_LIST)
        self.__pocInfoList = json.loads(pageSource.text)

    def __insertPocInfoIntoDatabase(self):
        insertStatementTemplate = "INSERT INTO %s (%s, %s, %s, %s, %s) VALUES (\"%s\", \"%s\", \"%s\", \"%s\", \"%s\")"
        for pocItem in self.__pocInfoList:
            insertStatement = insertStatementTemplate % (
                Constants.POC_INFO_TABLE_NAME,
                Constants.POC_INFO_TABLE_FIELDS[1],
                self.__replaceDotInFileNameToUnderscore(Constants.POC_INFO_TABLE_FIELDS[2]),
                Constants.POC_INFO_TABLE_FIELDS[3], Constants.POC_INFO_TABLE_FIELDS[4],
                Constants.POC_INFO_TABLE_FIELDS[5],
                pocItem[Constants.RAW_POC_LIST_KEYS[0]], pocItem[Constants.RAW_POC_LIST_KEYS[1]],
                self.__replaceDotInFileNameToUnderscore(pocItem[Constants.RAW_POC_LIST_KEYS[2]]),
                pocItem[Constants.RAW_POC_LIST_KEYS[3]],
                Constants.RAW_POC_SCRIPT_ROOT_PATH + pocItem[Constants.RAW_POC_LIST_KEYS[2]])
            self.__DATABASE_CURSOR.execute(insertStatement)
        self.__DATABASE_CONNECTION.commit()

    def __updateLocalPocFile(self):
        self.__removeLocalPocFile()
        self.__constructPocScriptUrlList()
        self.__downloadPocFile()

    def __removeLocalPocFile(self):
        shutil.rmtree(path=self.__POC_SCRIPT_FOLDER_PATH, ignore_errors=True)
        os.mkdir(self.__POC_SCRIPT_FOLDER_PATH)

    def __constructPocScriptUrlList(self):
        for item in self.__pocInfoList:
            self.__pocScriptUrlList.append(Constants.RAW_POC_SCRIPT_ROOT_PATH + item['filepath'])

    def __downloadPocFile(self):
        for pocScriptUrl in self.__pocScriptUrlList:
            pocScriptCode = self.__acquirePocScriptCode(pocScriptUrl)
            pocScriptSavePath = self.__replaceDotInFileNameToUnderscore(
                self.__constructSavePathOfPocScript(pocScriptUrl))
            self.__savePocScriptCodeToSpecifiedPath(pocScriptCode, pocScriptSavePath)

    @staticmethod
    def __acquirePocScriptCode(pocScriptUrl):
        pageSource = requests.get(pocScriptUrl)
        pocScriptCode = pageSource.text
        return pocScriptCode

    def __constructSavePathOfPocScript(self, pocScriptUrl):
        workspacePath = self.__WORKSPACE
        pocScriptFolderPath = workspacePath + "/" + Constants.POC_SCRIPT_FOLDER_NAME + "/"
        savePath = pocScriptUrl.replace(Constants.RAW_POC_SCRIPT_ROOT_PATH, pocScriptFolderPath)
        return savePath

    def __savePocScriptCodeToSpecifiedPath(self, pocScriptCode, pocScriptSavePath):
        directoryPath = self.__acquireDirectoryPath(pocScriptSavePath)
        self.__makeDirectoryIfNotExists(directoryPath)
        pocScript = open(pocScriptSavePath, "w")
        pocScript.write(pocScriptCode)
        pocScript.close()

    @staticmethod
    def __acquireDirectoryPath(pocScriptSavePath):
        splitIndex = pocScriptSavePath.rfind("/") + 1
        directoryPath = pocScriptSavePath[:splitIndex]
        return directoryPath

    @staticmethod
    def __makeDirectoryIfNotExists(directoryPath):
        if not os.path.exists(directoryPath):
            os.makedirs(directoryPath)

    def __releaseResources(self):
        self.__DATABASE_CURSOR.close()
        self.__DATABASE_CONNECTION.close()

    @staticmethod
    def __replaceDotInFileNameToUnderscore(string):
        prefix = string[:string.rfind("/")]
        suffix = string[string.rfind("."):]
        fileName = string[string.rfind("/"):string.rfind(".")]
        fileName = fileName.replace(".", "_")
        finalFileName = prefix + fileName + suffix
        return finalFileName


if __name__ == "__main__":
    updater = PocInfoUpdater()
    updater.execute()
