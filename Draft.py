def __replaceDotInFileNameToUnderline(string):
    prefix = string[:string.rfind("/")]
    suffix = string[string.rfind("."):]
    fileName = string[string.rfind("/"):string.rfind(".")]
    fileName = fileName.replace(".", "_")
    finalFileName = prefix + fileName + suffix
    return finalFileName


if __name__ == '__main__':
    fileName = __replaceDotInFileNameToUnderline("poc_script/system/php/expose_php.py")
    print(fileName)
