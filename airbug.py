#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/6/15 9:15 PM
# @Author  : w8ay
# @File    : airbug.py
import hashlib
import sys
from abc import ABC
from concurrent import futures
from importlib import util
from importlib.abc import Loader
import HackRequests
import pymysql

import Constants

WEB_REPOSITORY = "https://github.com/boy-hack/airbug"
HACK = HackRequests.hackRequests()


def get_md5(value):
    if isinstance(value, str):
        value = value.encode(encoding='UTF-8')
    return hashlib.md5(value).hexdigest()


def load_string_to_module(code_string, fullname=None):
    try:
        module_name = 'pocs_{0}'.format(get_md5(code_string)) if fullname is None else fullname
        file_path = 'w12scan://{0}'.format(module_name)
        poc_loader = PocLoader(module_name, file_path)
        poc_loader.set_data(code_string)
        spec = util.spec_from_file_location(module_name, file_path, loader=poc_loader)
        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    except ImportError:
        error_msg = "load module '{0}' failed!".format(fullname)
        print(error_msg)
        raise


class PocLoader(Loader, ABC):
    def __init__(self, fullname, path):
        self.fullname = fullname
        self.path = path
        self.data = None

    def set_data(self, data):
        self.data = data

    def get_filename(self, fullname):
        return self.path

    def get_data(self, filename):
        if filename.startswith('w12scan://') and self.data:
            data = self.data
        else:
            with open(filename, encoding='utf-8') as f:
                data = f.read()
        return data

    def exec_module(self, module):
        filename = self.get_filename(self.fullname)
        poc_code = self.get_data(filename)
        obj = compile(poc_code, filename, 'exec', dont_inherit=True, optimize=-1)
        exec(obj, module.__dict__)


def load_poc_info_from_database():
    databaseConnection = pymysql.connect(Constants.DATABASE_URL, Constants.DATABASE_USERNAME,
                                         Constants.DATABASE_PASSWORD, Constants.DATABASE_NAME)
    databaseCursor = databaseConnection.cursor()
    selectStatementTemplate = "SELECT %s, %s, %s, %s, %s FROM %s"
    selectStatement = selectStatementTemplate % (Constants.POC_INFO_TABLE_FIELDS[0],
                                                 Constants.POC_INFO_TABLE_FIELDS[1],
                                                 Constants.POC_INFO_TABLE_FIELDS[2],
                                                 Constants.POC_INFO_TABLE_FIELDS[3],
                                                 Constants.POC_INFO_TABLE_FIELDS[4],
                                                 Constants.POC_INFO_TABLE_NAME)
    databaseCursor.execute(selectStatement)
    results = databaseCursor.fetchall()
    pocInfoList = []
    for row in results:
        name = row[0]
        type1 = row[1]
        filepath = row[2]
        time = row[3]
        webFile = row[4]
        data = {"name": name, "type": type1, "filepath": filepath, "time": time, "webfile": webFile}
        pocInfoList.append(data)
    return pocInfoList


def run_airbug(target: str, keywords: list):
    PocQueue = []
    print("load poc from airbug repository")
    pocs = load_poc_info_from_database()
    for poc in pocs:
        for keyword in keywords:
            if keyword.lower() in poc["name"].lower():
                webfile = poc["webfile"]
                msg = "load {0} poc:{1} poc_time:{2}".format(poc["type"], webfile, poc["time"])
                print(msg)
                code = HACK.http(webfile).text()
                obj = load_string_to_module(code, webfile)
                PocQueue.append((target, obj))
    print("Start to run poc")
    collector = []
    if not PocQueue:
        msg = "Not found poc {}".format(repr(keywords))
        print(msg)
        return collector

    executor = futures.ThreadPoolExecutor(len(PocQueue))
    fs = []
    for target, obj in PocQueue:
        fs.append(executor.submit(obj.poc, target))
    for f in futures.as_completed(fs):
        try:
            ret = f.result()
        except Exception as e:
            ret = None
            print("load poc error:{} error:{}".format(target, str(e)))
        if ret:
            collector.append(ret)
    print("Finished")
    return collector


def main():
    target = ''
    keywords = []
    argv = sys.argv
    index = 0
    msg_help = "help:-u http://xxx.com -r emlog,wordpress"
    for arg in argv:
        try:
            if arg == "-u":
                target = argv[index + 1]
            if arg == "-r":
                keywords = argv[index + 1].split(",")
        except IndexError:
            print(msg_help)
            return
        index += 1
    if target and keywords:
        ret = run_airbug(target, keywords)
        if not ret:
            print("nothing.")
        for i in ret:
            print(i)
    else:
        print(msg_help)


main()
