import _rpa as r

def login(base_url,user,password):
    r.url(base_url + "/login")
    r.wait(1)
    if r.present("//span[text()='登录']") == False: # 已经登录过了
        return
    r.type("//input[@placeholder='请输入邮箱']",user)
    r.type("//input[@placeholder='请输入密码']",password)
    r.click("//span[text()='登录']")


def open_dev_mode():
    # 鼠标点在公司名称上点击10下击切换开发者模式的方式
    for i in range(10):
        r.click("//div[contains(@class,'style_organization')]")

def navigate(wb_name:str):
    try:
        # 先选一下系统配置
        r.click("//div[@data-test-id='treeNodeItem']//p[text()='系统配置']")
        # 点击导航查询
        r.click("//div[@data-test-id='workspace-sidebar']//div[contains(@class,'style_searchBtn')]")
        # 输入要查询的工作表名称
        r.type("//input[@placeholder='搜索文件 (⌘ K)']","[clear]"+wb_name)
        # 选择搜工作表
        r.click("//div[text()='工作表']")
        # 选择第一条匹配的结果
        r.click("//div[contains(@class,'style_nodeList')]/div[1]")
    except:
        raise Exception("未定位到工作表[{}].".format(wb_name))

def input_text(label:str,value:str):
    r.type("//div[text()='{}']/ancestor::div[contains(@class,'fieldTitleWrap')]/following-sibling::div[1]//input".format(label),value)
    r.click("//div[text()='{}']".format(label))

def select_one(label:str,value:str):
    r.click("//div[text()='{}']/ancestor::div[contains(@class,'fieldTitleWrap')]/following-sibling::div[1]//button".format(label))
    r.type("//input[contains(@placeholder,'搜索')]",value)
    r.click("//div[@role='option']")

def select_multiple(label:str,values:list[str]):
    r.click("//div[text()='{}']/ancestor::div[contains(@class,'fieldTitleWrap')]/following-sibling::div[1]//button".format(label))
    for v in values:
        r.type("//input[contains(@placeholder,'搜索')]",v)
        r.click("//div[@role='option']")
        r.click("//span[contains(@class,'style_suffixIcon')]")
    r.click("//div[text()='{}']/ancestor::div[contains(@class,'fieldTitleWrap')]/following-sibling::div[1]//button".format(label))
    

def select_one_link(label:str,value:str):
    r.click("//div[text()='{}']/ancestor::div[contains(@class,'fieldTitleWrap')]/following-sibling::div[1]//button".format(label))
    r.type("//input[contains(@placeholder,'搜索')]",value)
    r.click("//div[contains(@class,'style_selectWrapper')]")
    r.click("//div[contains(@class,'style_linkCard')]/child::node()[1]")
    

def close_popup():
    r.click("//div[contains(@class,'style_operateAreaWrapper')]/button[2]")

def add_record():
    r.click("//button[@id='toolInsertRecord']")

def add_view(type:str,name:str):
    r.click("//div[@id='DATASHEET_ADD_VIEW_BTN']")
    r.click("//p[text()='创建视图']/..//span[text()='{}']".format(type))
    r.type("//input[contains(@value,'{}')]".format(type),name)
    r.click("//input[1]//preceding-sibling::*")

def select_view(name:str):
    r.click("//div[contains(@class,'style_sheetName')]/span[text()='{}']".format(name))


def add_filter(column:str,conditoin:str,value:str):
    r.click("//button[@id='toolFilter']")
    r.click("//div[text()='添加筛选条件']")
    # 选择列
    r.click("//div[text()='当']/following-sibling::div[1]")
    r.click("//span[text()='{}']".format(column))
    # 选择匹配条件
    r.click("//div[text()='当']/following-sibling::div[2]")
    r.click("//div[@role='option' and @label='{}']".format(conditoin))
    # 输入筛选的值
    r.type("//div[text()='当']/following-sibling::div[3]//input",value)
    # 切换焦点
    r.click("//button[@id='toolFilter']")


def get_resource_id():
    url = str(r.url())
    offset = url.index("/workbench/") + 11
    return url[offset:]    