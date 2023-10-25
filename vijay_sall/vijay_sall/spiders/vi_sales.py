import scrapy
import json
import math
from bs4 import BeautifulSoup
from lxml import etree

class ViSalesSpider(scrapy.Spider):
    name = 'vi_sales'
    url = "https://www.vijaysales.com/index.aspx/LoadMM"

    payload = "{'Device':'Desktop','abspath':'/','HideHeader':'1','Section':'All'}"
    headers = {
    'content-type': 'application/json;charset=UTF-8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'Cookie': 'ASP.NET_SessionId=3iwvm3xvubxmvahjruvryddy; AWSALB=hKfHaw0BJ6FGtVywM8eus7ddJyQpbk3dGEjKSAA06qGuhC5+AP4lArF1qOMyx3uAvmrrdYWYL905gXLbNRyQ/BhVt+qf/CqcCTU9rdTp8gmL3LOs7k6FZ1pmawDF; AWSALBCORS=hKfHaw0BJ6FGtVywM8eus7ddJyQpbk3dGEjKSAA06qGuhC5+AP4lArF1qOMyx3uAvmrrdYWYL905gXLbNRyQ/BhVt+qf/CqcCTU9rdTp8gmL3LOs7k6FZ1pmawDF; __AntiXsrfToken=96099b8d8aa647f28902758fd93fa0e0'
    }
        
    def start_requests(self):
        
        yield scrapy.Request(
                                url=self.url,
                                headers=self.headers,
                                body=self.payload,
                                method="POSt",
                                meta={"currnt_page":1,"count":0},
                                callback=self.parse
                            )

    def parse(self, response):
        pagi_data = json.loads(response.text)

        cat = pagi_data["d"]["cateMenu"]  
        soup = BeautifulSoup(cat,"html.parser")
        cate = soup.find_all('a')

        for link in cate:
            cat_name = link.get('id')
            cat_id = link.get('name')

            if int(cat_id) !=0:
                url2 = f"https://www.vijaysales.com/Handlers/getProductData.ashx?catid={cat_id}&cityid=1&maxPrice=575995&Index=1&q=SearchPageProducts_isDefault_true_1{cat_name}"
                categ = cat_name.split("CatMenuDesktopli")[1]
                yield scrapy.Request(
                                    url=url2,
                                    headers=self.headers,
                                    body=self.payload,
                                    method="GET",
                                    meta={"url": url2, "currnt_page": 1, "count": 0, "currnt_page": response.meta['currnt_page'], "categ": categ,"cat_id":cat_id},
                                    callback=self.parse2
                                    )

    def parse2(self, response):
        data2 = json.loads(response.text)
        total_result = math.ceil(int(data2["TotalProducts"]) /12 )
   
        for j in data2["SearchData"]:
            
            URLName = j["URLName"]

            mrprice = j["MRPrice"]

            fvids = j["FVIDs"]

            lowest_price = j["LowestDisc"]

            diff = math.ceil(mrprice-lowest_price)

            NewPrice = j["NewPrice"]

            OfferPrice = j["OfferPrice"]

            diff_new_price = math.ceil(NewPrice-OfferPrice)

            item = {
                    "dName":URLName,
                        "fvids_id":[{
                            "fvids":fvids
                                }
                                ],
                    "price":{
                            "mrprice":mrprice,
                            "lowest_price":lowest_price,
                            "diff_price":diff
                    },
                    "offer_price":{
                        "NewPrice":NewPrice,
                        "OfferPrice":OfferPrice,
                        "diff_new_price":diff_new_price
                        },            
                    "categ":response.meta["categ"],                   
                    }
            yield item

        if response.meta['currnt_page'] < total_result:
            response.meta['currnt_page'] += 1     
            url2 = f"https://www.vijaysales.com/Handlers/getProductData.ashx?catid={response.meta['cat_id']}&cityid=1&maxPrice=575995&Index={response.meta['currnt_page']}&q=SearchPageProducts_isDefault_true_1{response.meta['categ']}"
            
            yield scrapy.Request(
                                    url=url2,
                                    headers=self.headers,
                                    meta={
                                        "url": url2,
                                        "currnt_page": response.meta['currnt_page'],
                                        "count": 0,
                                        "cat_id":response.meta["cat_id"],
                                        "categ": response.meta["categ"],
                                        },
                                    callback=self.parse2
                                )
