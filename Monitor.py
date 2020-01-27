"""
Task list:
1. Listening on server's commands
2. Update poc_info in database and download poc script
3. Start Scanner.py
4. Kill the thread of Scanner.py if server require or time was used up
5. Export environment variables
"""

import os

import Constants


# The monitor is consist of two threads, one for listening server's command, the other one for executing

def exportEnvironmentVariable():
    Constants.ENV_WORKSPACE = os.getcwd()


def updatePocInfo():
    pass


exportEnvironmentVariable()
