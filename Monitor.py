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

import Constants


# The monitor is consist of two threads, one for listening server's command, the other one for executing

def initializeConstantVariables():
    Constants.ENV_WORKSPACE = os.getcwd()
    Constants.DATABASE_CONNECTION = pymysql.connect(Constants.DATABASE_URL, Constants.DATABASE_USERNAME,
                                                    Constants.DATABASE_PASSWORD, Constants.DATABASE_NAME)
    Constants.DATABASE_CURSOR = Constants.DATABASE_CONNECTION.cursor()


def updatePocInfo():
    updateDatabase()
    updateLocalPocFile()


def updateDatabase():
    clearPocInfo()
    pocList = collectPocInfoFromWebsite()
    insertPocInfoIntoDatabase(pocList)


def clearPocInfo():
    deleteStatement = "DELETE FROM " + Constants.POC_INFO_TABLE_NAME
    Constants.DATABASE_CONNECTION.execute(deleteStatement)
    Constants.DATABASE_CONNECTION.commit()


def collectPocInfoFromWebsite():
    serverResponse = requests.get(Constants.RAW_POC_LIST)
    pocList = json.loads(serverResponse.text)
    return pocList


def insertPocInfoIntoDatabase(pocInfo):
    insertStatementTemplate = "INSERT INTO %s (%s, %s, %s, %s, %s)"
    for pocItem in pocInfo:
        insertStatement = insertStatementTemplate % (
            Constants.POC_INFO_TABLE_NAME, pocItem[Constants.POC_INFO_TABLE_FIELDS[1]],
            pocItem[Constants.POC_INFO_TABLE_FIELDS[2]], pocItem[Constants.POC_INFO_TABLE_FIELDS[3]],
            pocItem[Constants.POC_INFO_TABLE_FIELDS[4]], pocItem[Constants.POC_INFO_TABLE_FIELDS[5]])
        Constants.DATABASE_CURSOR.execute(insertStatement)
        # The performance may be better if this statement was put out of the for-loop, but not sure if there is any
        # error occurs.
        Constants.DATABASE_CONNECTION.commit()


def updateLocalPocFile():
    removeLocalPocFile()
    pocFileUrlList = collectPocFileUrlFromWebsite()
    downloadPocFile(pocFileUrlList)


def removeLocalPocFile():
    pass


def collectPocFileUrlFromWebsite():
    return []
    pass


def downloadPocFile(pocFileUrlList):
    pass


def releaseResources():
    Constants.DATABASE_CONNECTION.close()
