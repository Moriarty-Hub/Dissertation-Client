def __replaceDotInFileNameToUnderline(string):
    prefix = string[:string.rfind("/")]
    suffix = string[string.rfind("."):]
    fileName = string[string.rfind("/"):string.rfind(".")]
    fileName = fileName.replace(".", "_")
    finalFileName = prefix + fileName + suffix
    return finalFileName


if __name__ == '__main__':
    fileName = __replaceDotInFileNameToUnderline("/cms/thinkphp/thinkphp_3.1_code_exec.py")
    print(fileName)
