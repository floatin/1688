from dotenv import load_dotenv
load_dotenv()
from apitable import Apitable
from apitable.datasheet.record_manager import RecordManager
import re
import os

def _load():
    _api_base = os.getenv("DROPCELL_API_BASE")
    _token = os.getenv("DROPCELL_API_TOKEN")
    _resource_wb_id = os.getenv("DROPCELL_RESOURCE_WB_ID")
    _dropcell = Apitable(api_base=_api_base, token=_token) 
    if _dropcell is None:
        raise Exception(f"ERROR - Dropcell[{os.getenv('DROPCELL_API_BASE')}]加载失败.")
    _resource_sheet = _dropcell.datasheet(_resource_wb_id)
    return _dropcell,_resource_sheet

_dropcell,_resource_sheet = _load()

def wb(workbench_name:str) -> RecordManager:
    """
    通过工作表名称或者工作表id获得当前工作表的记录集
    """
    try:
        pattern = r'^[a-zA-Z0-9_]*$'
        if re.match(pattern, workbench_name):
            return _dropcell.datasheet(workbench_name).records
        wb_rid = _resource_sheet.records.get(资源名称=workbench_name).资源ID
        return _dropcell.datasheet(wb_rid).records
    except Exception as e:
        raise Exception(f"ERROR - 无法获得工作表[{workbench_name}].")

    