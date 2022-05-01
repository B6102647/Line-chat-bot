from flask import Flask, request
from linebot.models import *
from linebot import *
from datetime import datetime


from scaping_stock import scaping
from predict_price import predict_price


app = Flask(__name__)


line_bot_api = LineBotApi('6OgL1ZGu+VIeFcKabIt73JaN2cRzyvYeyV3/eqi5vZJIUxTYvFA4BWBdvPUE9GAd4bnvv/cU2EQ8lZrCcS5o7f2upYLUNsgV+qvM4w8fQWlRtvuc26+yF1ji7RCdE05KkZkOx92z2vLIZby/Sq5ScAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('26f0a32f38d1a9a9e0d08651b988ad50')

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    # print(body)
    req = request.get_json(silent=True, force=True)
    
    # print("req = ",req)

    intent = req["queryResult"]["intent"]["displayName"]
    queryText = req["queryResult"]["queryText"]
    
    text = req['originalDetectIntentRequest']['payload']['data']['message']['text']
    reply_token = req['originalDetectIntentRequest']['payload']['data']['replyToken']
    id = req['originalDetectIntentRequest']['payload']['data']['source']['userId']

    disname = line_bot_api.get_profile(id).display_name

    print('id = ' + id)
    print('name = ' + disname)
    print('queryText = ' + queryText)
    print('text = '+text)
    print('intent = ' + intent)
    print('reply_token = ' + reply_token)

    reply(intent,queryText,reply_token,id)

    

    print("---------------------------------------------")

    return 'OK'


def reply(intent,text,reply_token,id):
    if intent == "stock price - name":
        table = scaping(text)
        # waiting_message = TextSendMessage(text='กำลังประมวลผล กรุณารอสักครู่')
        # line_bot_api.reply_message(reply_token,waiting_message)
        date_time_str = table['Datetime']
        date_time_str = date_time_str[:19]
        date_time_split = date_time_str.split(" ")
        date = date_time_split[0]
        time = date_time_split[1]
        text_message = TextSendMessage(text='หุ้น : {}\nราคา : {}\nวันที่ : {}\nเวลา : {}\nสถานะ : {}'.format(text,table['Price'],date,time,table['Status']))
        line_bot_api.reply_message(reply_token,text_message)
        # line_bot_api.push_message(id, TextSendMessage(text='Hello World!'))
        # line_bot_api.push_message(user_id, text_message)
    if intent == "predict price - name":
        table = scaping(text)
        line_bot_api.reply_message(reply_token,TextSendMessage(text='กำลังประมวลผล กรุณารอสักครู่'))
        pred_price = predict_price(text,table['Status'])
        pred_price = float(pred_price)
        if table['Status'] == 'open':
            text_message = TextSendMessage(text='ทำนายราคาหุ้น {} ในอีก 5 นาที\nราคาจะอยู่ที่ {:.2f}'.format(text,pred_price))
        else:
            text_message = TextSendMessage(text='ทำนายราคาหุ้น {} ในตอนที่ตลาดเปิด\nราคาจะอยู่ที่ {:.2f}'.format(text,pred_price))
        line_bot_api.push_message(id, text_message)

if __name__ == "__main__":
    app.run(debug=True) 