from flask import Flask, request, abort

import openai
import os
from pyChatGPT import ChatGPT
from Scrape import scrape
#from Postgresql import database


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
        myScrape = scrape()
        movie_list = myScrape.movies(msg)

        carousel_template_message = TemplateSendMessage(
            alt_text='最新新聞推薦',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=movie_list[0].get("poster", ""),
                        title=movie_list[0].get("title", "無標題"),
                        text=f'大網:{movie_list[0].get("plot", "未知作者")}',
                        actions=[
                            URIAction(
                                label='詳細資料',
                                uri=movie_list[0].get("link", "#")
                            )
                        ]
                    )
                ]
            )
        )


        line_bot_api.reply_message(event.reply_token, carousel_template_message)
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
