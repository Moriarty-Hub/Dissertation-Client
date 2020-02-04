import Constants


def __replaceDotInFileNameToUnderline(string):
    prefix = string[:string.rfind("/")]
    suffix = string[string.rfind("."):]
    fileName = string[string.rfind("/"):string.rfind(".")]
    fileName = fileName.replace(".", "_")
    finalFileName = prefix + fileName + suffix
    return finalFileName


def __acquireModuleNameOfSpecifiedKeyword(keyword):
    moduleNameList = []
    for pocInfo in [{"name": "php", "type": "system", "file_path": "/system/php/expose_php.py",
                     "create_time": "2018-10-03 00:00:49",
                     "url": "https://raw.githubusercontent.com/Moriarty-Hub/airbug/master/system/php/expose_php.py"}]:
        if pocInfo["name"] == keyword:
            moduleName = (Constants.POC_SCRIPT_FOLDER_NAME + pocInfo["file_path"]).rstrip('.py') \
                .replace("/", ".")
            moduleNameList.append(moduleName)
    return moduleNameList


if __name__ == '__main__':
    """fileName = __replaceDotInFileNameToUnderline("poc_script/system/php/expose_php.py")
    print(fileName)"""
    print(__acquireModuleNameOfSpecifiedKeyword("php"))
    print("/system/php/expose_php.py"[:-3])
