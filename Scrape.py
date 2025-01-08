import requests
from bs4 import BeautifulSoup
import random
import os

class scrape:
    def __init__(self):
        self.headers = {
            "User-Agent": os.getenv('User_Agent')
          }
        
    def scrape(self):
        goods_list = ["滑鼠", "鍵盤", "喇叭", "耳機", "麥克風", "電競椅", "辦公椅", "繪圖板", "office軟體",
              "電競螢幕", "網路攝影機", "電腦機殼", "固態硬碟", "傳統硬碟", "顯示卡", "CPU", "主機板", "記憶體", "電源供應器",
              "風扇", "外接硬碟", "電腦機殼", "UPS", "記憶卡", "隨身碟", "Nintendo Switch", "PlayStation 5", "Xbox", "手把控制器",
              "羅技", "雷蛇", "HyperX", "路由器", "橋接器", "交換器", "光碟機", "華碩", "ROG", "曜越", "海盜船", "酷媽", "藍芽耳機",
              "Turtle Beach", "鐵三角", "微星", "賽德斯", "威剛", "樹梅派", "Arduino", "ESP32"]
        x = random.randrange(50)
        user_input = goods_list[x]
        result = requests.get(url=f"https://feebee.com.tw/s/?q={user_input}", headers=self.headers)
        soup = BeautifulSoup(result.text)
        
        options = soup.findAll("h3", class_="large")
        price = soup.findAll("span", class_="price ellipsis xlarge")
        link = soup.findAll("a", class_="campaign_link campaign_link_buy")

        # 確保至少有一筆資料可用
        if not options or not price or not link:
            return "抱歉，目前找不到足夠的商品資訊。"

        # 使用最小的長度以避免索引錯誤
        lst = ""
        max_items = min(3, len(options), len(price), len(link))

        for i in range(max_items):
            lst += f"商品名稱: {options[i].getText().strip()}\n"
            lst += f"價格: {price[i].getText().strip()}\n"
            lst += f"購買連結: {link[i].get('href')}\n"

        # 若資料不足3筆，提示用戶
        if max_items < 3:
            lst += f"\n注意：僅找到 {max_items} 筆商品資訊。\n"

        return lst

    
    def news(self):
        url = "https://technews.tw/"
        result = requests.get(url=url, headers=self.headers)
        soup = BeautifulSoup(result.text, 'html.parser')  # 加入解析器指定
        div = soup.find(id="content") 


        # 加入None檢查
        if not div:
            return "找不到新聞內容，請檢查網頁結構或反爬蟲保護"

        news_list=[]
        for article in div.find_all("article")[:3]:
            try:
                target = { 
                    "title": "",
                    "img_url": "",
                    "role": "",
                    "news_url": ""
                    }
                target["title"] = article.find("h1", class_="entry-title").text
                target["role"] = article.find_all("span", class_="body")[0].text
                target["news_url"] = article.find("div", class_="img").find("a").get('href')
                target["img_url"] = article.find("div", class_="img").find("img").get('src')
                news_list.append(target)
            except AttributeError:  # 防止部分元素缺失報錯
                continue
        return news_list
