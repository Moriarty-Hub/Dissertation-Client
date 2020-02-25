import pymysql

import Constants


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


if __name__ == '__main__':
    urlTarget = []
    hostTarget = []
    fillTargetList(urlTarget, hostTarget)
    print("---URL---")
    for item in urlTarget:
        print(item)
    print("---HOST---")
    for item in hostTarget:
        print(item)
