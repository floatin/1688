# https://drissionpage.cn/get_start/installation

from dropcell_dsl import wb 
import logging
from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._elements.none_element import NoneElement
from urllib.parse import quote
import json

logging.basicConfig(level=logging.DEBUG)

co = ChromiumOptions()
co.incognito(on_off=True)#无痕模式

# 大区划分
biz_blocks = {
    "华东":"江苏、浙江、上海、安徽、福建、江西、山东",
    "华南":"广东、广西、香港、澳门",
    "华北":"北京、天津、河北、山西、内蒙",
    "华中":"湖北、湖南、河南",
    "东北":"辽宁、黑龙江、吉林",
    "西南":"四川、云南、贵州、重庆、西藏",
    "东北":"辽宁、黑龙江、吉林",
    "西北":"陕西、甘肃、宁夏、新疆"
}

def _get_biz_block(province:str) -> str:
    for k,v in biz_blocks.items():
        if v.find(province) >= 0:
            return k
    return ""
        
# 从首页进入，防止被反爬机制命中
search_page = "https://www.1688.com/"

# 一个品牌下供应商最大数量
max_company_count = 3

# 等待时长
wait_duration = [1,3]

class CompanyInfo:
    # 供应商名称
    name:str
    # 商品品牌
    brand:str
    # 商品品类
    type:str
    # 手机
    mobile:str
    # 电话
    phone:str
    # 联系人
    contact_person:str
    # 大区
    biz_block:str
    # 省
    province:str
    # 市
    city:str
    # 商家地址
    address:str
    # 上架SKU数量
    sku_count:int
    # 店铺地址
    shop_url:str

    
    def __str__(self):
        return f"CompanyInfo[{json.dumps(self.__dict__,ensure_ascii=False)}]"


# 抓取一个公司的信息
def _crawl_company_info(brand:str,type:str,company:ChromiumElement):
    try:
        c_info = CompanyInfo()
        c_info.brand = brand
        c_info.name = company.ele('x://a[@class="company-name"]').text
        c_info.shop_url = company.ele('x://a[@class="company-name"]').property('href')
        
        # 如果该品牌下已经有该供应商的数据，则什么也不做
        r = wb("太保康养商品品牌1688信息").filter(商品品牌=brand,供应商名称=c_info.name)
        if r is not None and r.count() > 0:
            return

        # 点击公司名称，打开公司店铺首页
        tab_shop_homepage = company.ele('x://a[@class="company-name"]').click.for_new_tab(by_js=True)

        # 尝试拖动滑块
        #flow = tab_shop_homepage.ele('x://span[@class="nc-lang-cnt"]')
        #if flow != NoneElement:
        #    flow.drag(50,50,1)

        # 快速打开联系方式和所有商品页面，无视登录弹框
        tab_contract = tab_shop_homepage.ele('x://li[@class="contactinfo"]//a').click.for_new_tab(by_js=True)
        tab_offerlist = tab_shop_homepage.ele('x://li[@class="offerlist"]//a').click.for_new_tab(by_js=True)
        
        # 可以尝试一下直接打开打开联系方式和所有商品页面的方式
        #tab = p.new_tab(f"{c_info.shop_url}page/contactinfo.htm")
        #tab = p.new_tab(f"{c_info.shop_url}page/offerlist.htm")
        
        c_info.phone = tab_contract.ele('x://div[text()="电话："]').next().text        
        c_info.mobile = tab_contract.ele('x://div[text()="手机："]').next().text        
        c_info.address = tab_contract.ele('x://div[text()="地址："]').next().text        
        c_info.contact_person = tab_contract.ele('x://div[contains(text(),"有任何问题欢迎电话或在线沟通咨询")]').prev().text
        
        # 从foot中抽取省市信息
        address_in_foot = tab_contract.ele('x://div[@id="ft_0_container_0"]//span[contains(text(),"地址")]').text
        country,c_info.province,c_info.city,other = address_in_foot.split(" ")
        c_info.biz_block = _get_biz_block(c_info.province)

        tab_contract.close()

        c_info.sku_count = int(tab_offerlist.ele('x://div[text()="所有类目 >"]').next().ele('x://label').text)
        tab_offerlist.close()

        tab_shop_homepage.close()

        wb("太保康养商品品牌1688信息").create({
            "商品品牌":c_info.brand,
            "供应商名称":c_info.name,
            "手机":c_info.mobile,
            "电话":c_info.phone,
            "联系人":c_info.contact_person,
            "商家地址":c_info.address,
            "店铺地址":c_info.shop_url,
            "上架SKU数量":c_info.sku_count,
            "大区":c_info.biz_block,
            "省份":c_info.province,
            "城市":c_info.city,
        })
    except Exception as e:
        message = f"在采集品牌[{brand}]时发生异常[{e}]."
        logging.error(message)
        raise(message)


def crawl():
    # 可以考虑每次重新开一个chrome浏览器，防止没有关掉的tab把chrome的内存占满
    p = ChromiumPage()
    for rd in wb("商品品牌").all():
        
        try:
            brand = rd.商品品牌
            type = rd.商品品类

            # 测试
            if brand != "仙万里":
                continue
            
            # 如果这个品牌已经采集完成，就跳过
            count_in_wb = wb("太保康养商品品牌1688信息").filter(商品品牌=brand).count()
            if count_in_wb >= max_company_count:
                logging.info(f"品牌[{brand}]已经采集到[{count_in_wb}]个供应商.")
                continue
            
            #brand_encoding = quote(brand.encode("GBK"))
            # 从首页进入
            p.get(f"{search_page}")
            p.wait(wait_duration[0],wait_duration[1])
            # 点击页面上的【工业品】选项页
            tab = p.ele('x://a[text()="工业品"]').click.for_new_tab()
            
            # 在页面上输入品类+品牌信息，并搜索
            tab.ele('x://input[@id="industry-home-searchbox"]').input(f"{brand} {type}")
            tab = tab.ele('x://button[text()="搜 索"]').click().for_new_tab()
            
            # 这个页面是feedflow模式，等待页面一段时间，加载完成商品图片
            tab.wait(wait_duration[0],wait_duration[1])

            # 在查到的页面中依次匹配商品信息。主要匹配商品名称、
            for e in tab.eles('x://div[@data-spm="offerlist"]/a[@data-index]'):
                title_text = e.ele('x:..//div[@class="title-text"]').text
                desc_row_text = e.ele('x:..//div[@class="offer-desc-row"]').text
                desc_text = e.ele('x:..//div[@class="desc-text"]').text
                print (title_text,desc_row_text,desc_text)

        except Exception as e:
            message = f"在采集品牌[{brand}]时发生异常[{e}]."
            logging.error(message)
            wb("太保康养商品品牌1688信息").create({
                "商品品牌":brand,
                "备注":message,
            })
            raise e
        finally:
            pass
    p.close()

crawl()


