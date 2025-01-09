from flask import Flask, request, abort

import openai
import os
from pyChatGPT import ChatGPT
from Scrape import scrape
#from Postgresql import database
from imdb import IMDb

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = str(event.message.text)         
    if msg == "熱銷商品比價GO":       
        myScrape = scrape()
        output = myScrape.scrape()       
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=str(output)))

    elif msg == "movies":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入電影英文名稱")
        )
        return



    elif msg == "news":
        myScrape = scrape()
        news_list = myScrape.news()

        # 確保 news_list 是一個列表，且每個元素都是字典
        if not isinstance(news_list, list) or not all(isinstance(item, dict) for item in news_list):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="抱歉，目前無法取得最新新聞資訊。")
            )
            return

        # 確保至少有三筆資料
        if len(news_list) < 3:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="新聞數量不足，請稍後再試。")
            )
            return

        carousel_template_message = TemplateSendMessage(
            alt_text='最新新聞推薦',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=news_list[0].get("img_url", ""),
                        title=news_list[0].get("title", "無標題"),
                        text=f'作者:{news_list[0].get("role", "未知作者")}',
                        actions=[
                            URIAction(
                                label='馬上查看',
                                uri=news_list[0].get("news_url", "#")
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=news_list[1].get("img_url", ""),
                        title=news_list[1].get("title", "無標題"),
                        text=f'作者:{news_list[1].get("role", "未知作者")}',
                        actions=[
                            URIAction(
                                label='馬上查看',
                                uri=news_list[1].get("news_url", "#")
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=news_list[2].get("img_url", ""),
                        title=news_list[2].get("title", "無標題"),
                        text=f'作者:{news_list[2].get("role", "未知作者")}',
                        actions=[
                            URIAction(
                                label='馬上查看',
                                uri=news_list[2].get("news_url", "#")
                            )
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, carousel_template_message)

    else:
        ia = IMDb()
        
        search_results = ia.search_movie(msg)
    
        if search_results:
            # 取得第一個搜尋結果的 ID
            movie_id = search_results[0].movieID
            
            # 根據 ID 取得電影詳細資訊
            movie = ia.get_movie(movie_id)
            
            # 獲取 IMDb 鏈結
            imdb_link = f"https://www.imdb.com/title/tt{movie_id}/"
            #movie_info['link'] = imdb_link

            print(imdb_link)

            # 獲取電影海報影像連結
            #poster_url = ia.get_imdbURL(movie)
            poster_url = movie.get('full-size cover url', '無海報')
            #movie_info['poster'] = poster_url
            
            title = movie.get('title', '未知標題')
            plot = movie.get('plot', ['無簡介'])[0]
            rating = movie.get('rating', '無評分')
            year = movie.get('year', '未知年份')
            
            messages = [
                TextSendMessage(text=f"電影名稱: {title}\n劇情大綱: {plot}\n上映年份: {year}\nIMDb 鏈結: {imdb_link}"),
                ImageSendMessage(original_content_url=poster_url, preview_image_url=poster_url)
            ]


        line_bot_api.reply_message(event.reply_token, messages)
'''        
    else:          
        openai.api_key = os.getenv('SESSION_TOKEN')
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 或者使用最新的模型，如 gpt-4
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": msg}
            ],
            max_tokens=300,
            temperature=0.5
        )

        completed_text = response['choices'][0]['message']['content']
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = completed_text[2:]))
'''


if __name__ == "__main__":
    app.run()
