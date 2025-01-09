import requests
from bs4 import BeautifulSoup
import random
import os
from imdb import IMDb

class scrape:        
    def scrape(self):
        goods_list = ["滑鼠", "鍵盤", "喇叭", "耳機", "麥克風", "電競椅", "辦公椅", "繪圖板", "office軟體",
              "電競螢幕", "網路攝影機", "電腦機殼", "固態硬碟", "傳統硬碟", "顯示卡", "CPU", "主機板", "記憶體", "電源供應器",
              "風扇", "外接硬碟", "電腦機殼", "UPS", "記憶卡", "隨身碟", "Nintendo Switch", "PlayStation 5", "Xbox", "手把控制器",
              "羅技", "雷蛇", "HyperX", "路由器", "橋接器", "交換器", "光碟機", "華碩", "ROG", "曜越", "海盜船", "酷媽", "藍芽耳機",
              "Turtle Beach", "鐵三角", "微星", "賽德斯", "威剛", "樹梅派", "Arduino", "ESP32"]
        x = random.randrange(50)
        user_input = goods_list[x]
        headers = {"User-Agent": "Mozilla/5.0"}  # 確保用戶代理正常
        result = requests.get(url=f"https://feebee.com.tw/s/?q={user_input}", headers=headers)
        soup = BeautifulSoup(result.text, 'html.parser')

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

    def movies(movie_name):
        # 創建 IMDb 物件
        ia = IMDb()
        
        # 使用 IMDbPY 查詢電影資訊
        search_results = ia.search_movie(movie_name)

        movie_info = {}
        
        if search_results:
            # 取得第一個搜尋結果的 ID
            movie_id = search_results[0].movieID
            
            # 根據 ID 取得電影詳細資訊
            movie = ia.get_movie(movie_id)
            
            # 整理電影資訊到字典中
            movie_info['title'] = movie['title']
            movie_info['year'] = movie['year']
            movie_info['rating'] = movie['rating']
            movie_info['plot'] = movie['plot'][0]
            
            # 獲取 IMDb 鏈結
            imdb_link = f"https://www.imdb.com/title/{movie_id}/"
            movie_info['link'] = imdb_link

            # 獲取電影海報影像連結
            poster_url = ia.get_imdbURL(movie)
            movie_info['poster'] = poster_url
        else:
            movie_info['error'] = "找不到相關電影資訊。"
        
        return movie_info

    def news(self):
        url = "https://technews.tw/"
        headers = {"User-Agent": "Mozilla/5.0"}  # 確保用戶代理正常
        result = requests.get(url, headers=headers)
        soup = BeautifulSoup(result.text, 'html.parser')

        # 使用更通用的選擇器來匹配文章區塊
        div = soup.find("div", id="content")
        if not div:
            return "找不到新聞內容，請檢查網頁結構或反爬蟲保護"
        
        # 初始化新聞列表
        news_list = []

        # 嘗試抓取文章資訊
        for article in div.find_all("article")[:3]:
            try:
                target = {
                    "title": article.select_one("h1.entry-title").text.strip(),
                    "role": article.select_one("span.body").text.strip(),
                    "news_url": article.select_one("div.img a")["href"],
                    "img_url": article.select_one("div.img img")["src"]
                }
                news_list.append(target)
            except (AttributeError, TypeError):
                continue

        # 偵測是否為空列表
        if not news_list:
            return "未能成功擷取新聞，請檢查網頁結構或反爬蟲保護。"

        return news_list
