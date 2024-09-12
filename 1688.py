from datetime import datetime, timedelta
from dateutil.relativedelta import *


def _to_class(dic:dict):
    field_names = dic.keys()
    
    class _Class:
        pass
    instance = _Class()
    for name in field_names:
        setattr(instance, name, dic.get(name,""))
    return instance

def test_relativedelta():
    
    todo = _to_class({"_id":"","提醒时间":""})
    todo._id = "178"
    results = []
    now = datetime.now()
    p = _to_class({"时间值":"","星期值":"","时间方式":""})

    p.时间值 = '10:00'
    p.星期值 = '5'
    p.时间方式 = '下'
    date_pattern = "%Y-%m-%d %H:%M:%S"


    results.append(f"待办任务总表.{todo._id}")
    # 根据具体时间或者相对时间计算提醒时间
    now = datetime(now.year, now.month,6)
    hours = 0
    minutes = 0
    weeks = 0
    if p.时间值 is not None and p.时间值 != "":
        try:
            hours, minutes = p.时间值.split(":",1)
            hours = int(hours)
            minutes = int(minutes)
        except:
            raise Exception("意图识别匹配的时间值格式不正确：[" + p.时间值 + "]." )
    if p.时间方式 == "后":
        todo.提醒时间 = (now + timedelta(days=int(p.星期值)*7,hours=hours, minutes=minutes)).strftime(date_pattern)
    elif p.时间方式  ==  "本":
        todo.提醒时间 = (now + relativedelta(weekday=int(p.星期值)-1, weeks=0, hours=hours, minutes=minutes)).strftime(date_pattern)
    elif p.时间方式  ==  "下":
        todo.提醒时间 = (now + relativedelta(weekday=int(p.星期值)-1, weeks=1, hours=hours, minutes=minutes)).strftime(date_pattern)
    elif p.时间方式  ==  "下下":
        todo.提醒时间 = (now + relativedelta(weekday=int(p.星期值)-1, weeks=2, hours=hours, minutes=minutes)).strftime(date_pattern)
    else:
        raise Exception(f"待办任务提醒[{todo.任务描述}]处理异常.")

    print (todo.提醒时间)

test_relativedelta()

now = datetime.now()
monday = now - timedelta(days=now.weekday())
monday = datetime(monday.year, monday.month,monday.day,10)
print(monday)