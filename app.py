from flask import Flask, request, abort
from linebot import (
 LineBotApi, WebhookHandler
)
from linebot.exceptions import (
 InvalidSignatureError
)
from linebot.models import (
 MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

# 設定 LINE Bot 的認證資訊
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
  abort(400)

 return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
 line_bot_api.reply_message(
  event.reply_token,
  TextSendMessage(text=event.message.text))


@app.route('/message', methods=['POST'])  
def message():  
    user_id = request.form.get('user_id')  
    message = request.form.get('message')  
  
    if user_id not in user_messages:  
        user_messages[user_id] = []  
    user_messages[user_id].append(message)  
  
    return 'Hello, your message has been received.'

@handler.add(MessageEvent, message=TextMessage)  
def handle_message(event):  
    user_id = event.source.user_id  
    message = event.message.text  
  
    message_url = url_for('message', _external=True)  
    response_message = requests.post(message_url, data={  
        'user_id': user_id,  
        'message': message  
    })  
  
    line_bot_api.reply_message(  
        event.reply_token,  
        TextSendMessage(text=response_message)  
    )

if __name__ == "__main__":
 app.run()