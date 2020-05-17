DATABASE_URL = "localhost"
DATABASE_USERNAME = "dxr"
DATABASE_PASSWORD = "dxr"
DATABASE_NAME = "network_asset"
RAW_POC_LIST = "https://raw.githubusercontent.com/Moriarty-Hub/airbug/master/API.json"
RAW_POC_LIST_KEYS = ["name", "type", "filepath", "time"]
POC_INFO_TABLE_NAME = "poc_info"
POC_INFO_TABLE_FIELDS = ["id", "name", "type", "file_path", "create_time", "url"]
SCAN_RESULT_TABLE_NAME = "scan_result"
SCAN_RESULT_TABLE_FIELDS = ["id", "target", "target_type", "description", "scan_time"]
TARGET_TABLE_NAME = "target"
TARGET_TABLE_FIELDS = ["id", "target", "type"]
POC_SCRIPT_FOLDER_NAME = "poc_script"
RAW_POC_SCRIPT_ROOT_PATH = "https://raw.githubusercontent.com/Moriarty-Hub/airbug/master"
