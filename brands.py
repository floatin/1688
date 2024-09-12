from dropcell_dsl import wb 
import logging
from DrissionPage import ChromiumPage
from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._elements.none_element import NoneElement
from urllib.parse import quote
import json

logging.basicConfig(level=logging.DEBUG)

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
        
# 查找供应商
search_page = "https://s.1688.com/company/company_search.htm"

# 一个品牌下供应商最大数量
max_company_count = 30

# 等待时长
wait_duration = [1,3]

class CompanyInfo:
    # 供应商名称
    name:str
    # 商品品牌
    brand:str
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
def _crawl_company_info(brand:str,company:ChromiumElement):
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
        split = address_in_foot.split(" ")
        if len(split) == 3 : # 直辖市
            c_info.province = c_info.city = split[1]
        else:
            c_info.province = split[1]
            c_info.city = split[2]
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
    # 每次重新开一个chrome浏览器，防止没有关掉的tab把chrome的内存占满
    p = ChromiumPage()
    
    for rd in wb("商品品牌").all():
        try:
            brand = rd.商品品牌

            # 测试
            if brand != "迪士尼":
                continue
            
            # 如果这个品牌已经采集完成，就跳过
            count_in_wb = wb("太保康养商品品牌1688信息").filter(商品品牌=brand).count()
            if count_in_wb >= max_company_count:
                logging.info(f"品牌[{brand}]已经采集到[{count_in_wb}]个供应商.")
                continue
            
            brand_encoding = quote(brand.encode("GBK"))
            p.get(f"{search_page}")
            
            p.ele('x://input[@id="alisearch-input"]').input(brand)
            p.ele('x://button[text()="搜 索"]').click()
            p.wait(wait_duration[0],wait_duration[1])

            # 没找到相关的品牌
            if p.ele('x://div[@class="sm-noresult"]'):
                message = f"没有找到该品牌[{brand}]的供应商。"
                logging.warning(message)
                raise Exception(message)

            # 该品牌下的商家一共展示了多少页
            page_count = int(p.ele('x://span[@class="fui-paging-total"]//em').text)

            # 一页一页抓取数据
            page = 1
            count = count_in_wb
            for page in range(page_count+1):
                try:
                    logging.info(f"开始抓取品牌[{brand}]第[{page}]页的商家信息...")
                    # 页面跳转按钮
                    goto_page_button = p.ele('x://span[@class="fui-paging-list"]//a[@class="fui-next"]')
                    goto_page_button.click()
                    print("翻页...")
                    p.wait(wait_duration[0],wait_duration[1])
                except Exception as e:
                    raise e
                
                # 定位所有商家
                companies = p.eles('x://div[@class="company-left-card"]')

                # 测试翻页，只保留每一页第一个商家
                #company = companies[0]
                #companies.clear()
                #companies.append(company)

                for company in companies:
                    # 是否到上限
                    if count >= max_company_count:
                        break
                    
                    _crawl_company_info(brand=brand,company=company)
                    count += 1
                
                # 如果已经爬到足够多的商家，不再翻页
                if count >= max_company_count:
                    break

                page += 1    

        except Exception as e:
            message = f"在采集品牌[{brand}]时发生异常[{e}]."
            logging.error(message)
            wb("太保康养商品品牌1688信息").create({
                "商品品牌":brand,
                "备注":message,
            })
            raise e
        finally:
            p.close()

# p = ChromiumPage()
crawl()
# p.close()

