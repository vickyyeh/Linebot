from transitions.extensions import GraphMachine

import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage

from utils import send_text_message

load_dotenv()

import requests as rs
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyimgur
import message_template

def get_value_now():
    # get html
    res = rs.get('https://rate.bot.com.tw/xrt/quote/ltm/JPY')
    res.encoding = 'utf-8'
    # get data table
    soup = BeautifulSoup(res.text, 'lxml')
    table = soup.find('table', {'class': 'table table-striped table-bordered table-condensed table-hover'})
    table = table.find_all('tr')
    # remove table title
    table = table[2:]
    # add to dataframe
    col = ['掛牌日期', '幣別', '現金買入', '現金賣出', '匯率買入', '匯率賣出']
    data = []
    for row in table:
        row_data = []
        date = row.find('td',{'class':'text-center'}).text
        currency = row.find('td',{'class':'text-center tablet_hide'}).text
        cash = row.find_all('td',{'class':'rate-content-cash text-right print_table-cell'})
        sight = row.find_all('td',{'class':'rate-content-sight text-right print_table-cell'})
        row_data.append(date)
        row_data.append(currency)
        row_data.append(cash[0].text)
        row_data.append(cash[1].text)
        row_data.append(sight[0].text)
        row_data.append(sight[1].text)
        data.append(row_data)
    df = pd.DataFrame(data)
    df.columns = col
    df['掛牌日期'] = pd.to_datetime(df['掛牌日期'])
    df.set_index('掛牌日期', inplace=True)
    # value query
    output=df.iloc[0]
    return output

def get_url_3month():
    # get html
    res = rs.get('https://rate.bot.com.tw/xrt/quote/ltm/JPY')
    res.encoding = 'utf-8'
    # get data table
    soup = BeautifulSoup(res.text, 'lxml')
    table = soup.find('table', {'class': 'table table-striped table-bordered table-condensed table-hover'})
    table = table.find_all('tr')
    # remove table title
    table = table[2:]
    # add to dataframe
    col = ['掛牌日期', '幣別', '現金買入', '現金賣出', '匯率買入', '匯率賣出']
    data = []
    for row in table:
        row_data = []
        date = row.find('td',{'class':'text-center'}).text
        currency = row.find('td',{'class':'text-center tablet_hide'}).text
        cash = row.find_all('td',{'class':'rate-content-cash text-right print_table-cell'})
        sight = row.find_all('td',{'class':'rate-content-sight text-right print_table-cell'})
        row_data.append(date)
        row_data.append(currency)
        row_data.append(cash[0].text)
        row_data.append(cash[1].text)
        row_data.append(sight[0].text)
        row_data.append(sight[1].text)
        data.append(row_data)
    df = pd.DataFrame(data)
    df.columns = col
    df['掛牌日期'] = pd.to_datetime(df['掛牌日期'])
    df.set_index('掛牌日期', inplace=True)
    # draw the graph
    plt.figure(figsize=(20,15))
    plt.rcParams['font.sans-serif']=['Microsoft YaHei']
    df_pic=df[['現金買入', '現金賣出', '匯率買入', '匯率賣出']]
    df_pic=df_pic.astype(float)
    df_pic=df_pic.plot()
    plt.grid()
    plt.title('日圓匯率近三月走勢圖',fontsize=16)
    plt.xlabel('掛牌日期',fontsize=14)
    plt.ylabel('匯率',fontsize=14)
    plt.savefig('JPY_df.png', dpi=300)
    plt.show()
    # upload to imgur and get url
    CLIENT_ID = "b4d6470eeacb77a"
    PATH = "JPY_df.png"
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title="upload")
    return uploaded_image.link

def get_url_2week():
    # get html
    res = rs.get('https://rate.bot.com.tw/xrt/quote/ltm/JPY')
    res.encoding = 'utf-8'
    # get data table
    soup = BeautifulSoup(res.text, 'lxml')
    table = soup.find('table', {'class': 'table table-striped table-bordered table-condensed table-hover'})
    table = table.find_all('tr')
    # remove table title
    table = table[2:]
    # add to dataframe
    col = ['掛牌日期', '幣別', '現金買入', '現金賣出', '匯率買入', '匯率賣出']
    data = []
    for row in table:
        row_data = []
        date = row.find('td',{'class':'text-center'}).text
        currency = row.find('td',{'class':'text-center tablet_hide'}).text
        cash = row.find_all('td',{'class':'rate-content-cash text-right print_table-cell'})
        sight = row.find_all('td',{'class':'rate-content-sight text-right print_table-cell'})
        row_data.append(date)
        row_data.append(currency)
        row_data.append(cash[0].text)
        row_data.append(cash[1].text)
        row_data.append(sight[0].text)
        row_data.append(sight[1].text)
        data.append(row_data)
    df = pd.DataFrame(data)
    df.columns = col
    df['掛牌日期'] = pd.to_datetime(df['掛牌日期'])
    df.set_index('掛牌日期', inplace=True)
    # draw the graph
    df_pic_week=df[['現金買入', '現金賣出', '匯率買入', '匯率賣出']].iloc[0:14]
    plt.figure(figsize=(20,15))
    plt.rcParams['font.sans-serif']=['Microsoft YaHei']
    df_pic_week=df_pic_week.astype(float)
    df_pic_week=df_pic_week.plot(marker='o')
    plt.grid()
    plt.title('日圓匯率近兩周走勢圖',fontsize=16)
    plt.xlabel('掛牌日期',fontsize=14)
    plt.ylabel('匯率',fontsize=14)
    plt.savefig('JPY_df2.png', dpi=300)
    plt.show()
    # upload to imgur and get url
    CLIENT_ID = "b4d6470eeacb77a"
    PATH = "JPY_df2.png"
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title="upload")
    return uploaded_image.link

def get_recommend():
    # get html
    res = rs.get('https://rate.bot.com.tw/xrt/quote/ltm/JPY')
    res.encoding = 'utf-8'
    # get data table
    soup = BeautifulSoup(res.text, 'lxml')
    table = soup.find('table', {'class': 'table table-striped table-bordered table-condensed table-hover'})
    table = table.find_all('tr')
    # remove table title
    table = table[2:]
    # add to dataframe
    col = ['掛牌日期', '幣別', '現金買入', '現金賣出', '匯率買入', '匯率賣出']
    data = []
    for row in table:
        row_data = []
        date = row.find('td',{'class':'text-center'}).text
        currency = row.find('td',{'class':'text-center tablet_hide'}).text
        cash = row.find_all('td',{'class':'rate-content-cash text-right print_table-cell'})
        sight = row.find_all('td',{'class':'rate-content-sight text-right print_table-cell'})
        row_data.append(date)
        row_data.append(currency)
        row_data.append(cash[0].text)
        row_data.append(cash[1].text)
        row_data.append(sight[0].text)
        row_data.append(sight[1].text)
        data.append(row_data)
    df = pd.DataFrame(data)
    df.columns = col
    df['掛牌日期'] = pd.to_datetime(df['掛牌日期'])
    df.set_index('掛牌日期', inplace=True)
    # recommend sort for 3 month & 2 week
    recommend_3month = False
    recommend_2week = False
    date_today = df.index[0]
    df2 = df.copy()
    df2 = df2[0:14]
    df.sort_values('匯率賣出',inplace=True)
    date_5min_3month = df.index[0:5]
    df2.sort_values('匯率賣出',inplace=True)
    date_5min_2week = df.index[0:3]
    if (date_today in date_5min_3month):
        recommend_3month = True
    if (date_today in date_5min_2week):
        recommend_2week = True
    output=[]
    output.append(recommend_3month)
    output.append(recommend_2week)
    return output


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_menu(self, event):
        text = event.message.text
        return text == "主選單"

    def is_going_to_show_fsm_pic(self, event):
        text = event.message.text
        return text == "查看fsm結構圖"

    def is_going_to_cancel(self, event):
        text = event.message.text
        return text == "結束本次操作"

    def is_going_to_value_now(self, event):
        text = event.message.text
        return text == "查詢即時匯率"

    def is_going_to_value_recently(self, event):
        text = event.message.text
        return text == "查詢趨勢走向"
    
    def is_going_to_value_recently_3month(self, event):
        text = event.message.text
        return text == "最近三個月趨勢"

    def is_going_to_value_recently_2week(self, event):
        text = event.message.text
        return text == "最近兩週趨勢"

    def is_going_to_recommend(self, event):
        text = event.message.text
        return text == "是否推薦兌幣"

    def is_going_to_introduction(self, event):
        text = event.message.text
        return text == "功能介紹與說明"

    def on_enter_menu(self, event):
        reply_token = event.reply_token
        message = message_template.main_menu
        message_to_reply = FlexSendMessage("開啟主選單", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
    
    def on_enter_show_fsm_pic(self, event):
        reply_token = event.reply_token
        message = message_template.show_pic
        message_to_reply = FlexSendMessage("查看fsm結構圖", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        self.go_back()

    def on_enter_cancel(self, event):
        reply_token = event.reply_token
        message = message_template.cancel_menu
        message_to_reply = FlexSendMessage("結束並返回主選單", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        self.go_back()

    def on_enter_value_now(self, event):
        reply_token = event.reply_token
        value_now = get_value_now()
        message = message_template.now_table
        message["body"]["contents"][2]["contents"][0]["contents"][1]["text"] = value_now[1]
        message["body"]["contents"][2]["contents"][1]["contents"][1]["text"] = value_now[2]
        message["body"]["contents"][2]["contents"][3]["contents"][1]["text"] = value_now[3]
        message["body"]["contents"][2]["contents"][4]["contents"][1]["text"] = value_now[4]
        message_to_reply = FlexSendMessage("查詢即時值", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        self.go_back()

    def on_enter_value_recently(self, event):
        reply_token = event.reply_token
        message = message_template.plot_menu
        message_to_reply = FlexSendMessage("查詢趨勢走向選單", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        
    def on_enter_value_recently_3month(self, event):
        reply_token = event.reply_token
        pic_url = get_url_3month()
        message = message_template.plot
        message['contents'][0]['hero']['url'] = pic_url
        message_to_reply = FlexSendMessage("趨勢圖-近三個月", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)

    def on_enter_value_recently_2week(self, event):
        reply_token = event.reply_token
        pic_url = get_url_2week()
        message = message_template.plot
        message['contents'][0]['hero']['url'] = pic_url
        message_to_reply = FlexSendMessage("趨勢圖-近兩週", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)

    def on_enter_recommend(self, event):
        reply_token = event.reply_token
        message = message_template.recommend_message
        rec_output = get_recommend()
        rec_level = 0
        if rec_output[0]:
            message["body"]["contents"][3]["contents"][0]["contents"][1]["text"] = "是"
            rec_level = rec_level + 1
        if rec_output[1]:
            message["body"]["contents"][3]["contents"][1]["contents"][1]["text"] = "是"
            rec_level = rec_level + 1
        if (rec_level == 0):
            message["body"]["contents"][3]["contents"][3]["contents"][1]["text"] = "低"
        elif (rec_level == 1):
            message["body"]["contents"][3]["contents"][3]["contents"][1]["text"] = "中"
        else:
            message["body"]["contents"][3]["contents"][3]["contents"][1]["text"] = "高"
        message_to_reply = FlexSendMessage("是否推薦兌幣", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        self.go_back()

    def on_enter_introduction(self, event):
        reply_token = event.reply_token
        message = message_template.introduction_message
        message_to_reply = FlexSendMessage("功能介紹與說明", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        self.go_back()

