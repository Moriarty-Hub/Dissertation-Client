## Summary

This is the client of my graduation project, network asset management system, it runs on Linux system with some other pre-installed applications such as, python interpreter, pip package manager, database, to name just a few.

The client includes three components, they are PocInfoUpdater.py, Scanner.py, Constants.py.

The first component is responsible for collecting the latest POC information from specified website, and update which stored in database and local storage.

The second component is the most critical one, it scans the given targets according to the data the updater provide, the results of scanning were stored in database.

Constant variables are defined in Constants.py, like the IP address, user name, password of database, the name of each table, the field list of that, and so on. It is very convenient to define all constant variables in one place, we just need to modify several lines of a file rather than a sea of lines of countless files when they were changed.

The first two component can be run through command line, for booting them, some necessary applications and program package are needed.



## PocInfoUpdater.py

The pymysql and requests packages are required to be pre-installed through the pip3 package manager before running this script by executing this command.

```
$python3 PocInfoUpdater.py
```

This script is used for automatically updating POC information in database and POC script on the disk of the server.

In the stage of updating database, the script deletes all POC information in the database and captures the latest POC information from the given URL, which was defined in Constants.py. Those data items include the name, type, path on local disk, created time and URL of each POC item. After that, the collected data will be insert into database.

In another stage, local POC scripts will be update. As we did in the last stage, those local out-of-date POC scripts were deleted at the very beginning. Then it reads the URL of every POC item and download the source code from that to specified path, which was constructed by the given prefix(in Constants.py) and part of URL, on the local disk.



## Scanner.py

For running this script by executing the command, HackRequest and scapy packages are required.

```
$python3 Scanner.py
```

Here are many types of POC script, some of them apply to laptops or servers, and the other for websites. Therefore, at the beginning of Scanner.py, we divide them to two groups and pre-define them in two list.

After that, the script initialize some dynamic parameters, such as the path of the script itself, the connection and cursor object of database. They are called dynamic since their value varies in different machine. Also, the POC information will be get from database and be saved into list.

After the preparation, scan procedure is about to start. First, it tries to ping every host target for filtering some inactive target for reducing some unnecessary operation afterward. Then the previous scanning results in database will be deleted, and it continue to iterates every target and import suitable script one by one and execute them. If there is any vulnerable point was found, the target and information that POC script provide will be record, which will be save into database at the end of scanning. So far, the workload of this script has been finished.