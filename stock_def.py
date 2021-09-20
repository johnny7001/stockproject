import numpy as np
import pandas as pd
import time
from bs4 import BeautifulSoup
import requests
import datetime
import os
import sqlalchemy
import plotly_express as px
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from selenium import webdriver
import mysql.connector.connection
from datetime import timedelta, date
def stockDate_tocsv(code): #產生個股月份資訊
    date = datetime.datetime.today()
    date_str = date.strftime('%Y%m01')  # 產稱最新日期, 日一律=01
    url = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date='+date_str+'&stockNo='+str(code)
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                            '(KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}
    resp = requests.get(url, headers=headers)
    time.sleep(5)
    data = resp.json() #type=dict
    # columns = data['fields']
    date_list = []
    volume_list = [] #成交股數
    value_list = [] #成交金額
    open_list = []
    high_list = []
    low_list = []
    close_list = []
    change_list = [] #漲跌價差
    transaction_list = [] #交易筆數

    for day in range(len(data['data'])):
        date_year = int(data['data'][day][0][:3]) + 1911
        date_month = data['data'][day][0][3:]
        date_list.append((str(date_year) + date_month.replace('/', '-')))
        volume_list.append(int(data['data'][day][1].replace(',', '')))
        value_list.append(int(data['data'][day][2].replace(',', '')))
        open_list.append(float(data['data'][day][3].replace('--', '0')))
        high_list.append(float(data['data'][day][4].replace('--', '0')))
        low_list.append(float(data['data'][day][5].replace('--', '0')))
        close_list.append(float(data['data'][day][6].replace('--', '0')))
        change_list.append(float(data['data'][day][7].replace('+', '').replace('X', '')))
        transaction_list.append(int(data['data'][day][8].replace(',', '')))

    df = pd.DataFrame({'日期':date_list, '成交股數':volume_list, '成交金額':value_list,
                      '開盤價':open_list, '最高價':high_list, '最低價':low_list, '收盤價':close_list,
                      '帳跌價差':change_list, '成交筆數':transaction_list})
    time.sleep(3)
    filepath = "static/{}/{}_{}".format(code, code, date_str)
    df.to_csv(filepath + '.csv')

    # AllDf = AllDf.append(df, ignore_index=True)
    html = df.to_html()
    with open(filepath+'.html', "w", encoding="utf-8") as file: #將編碼寫入html檔案
        file.writelines('<meta charset="UTF-8">\n')
        file.write(html)
    # time.sleep(3)
    # df.columns = ['Date', 'TradeVolume', 'TradeValue', 'Open', 'High', 'Low', 'Close', 'Change', 'Transaction']
    time.sleep(3)

def auto_to_csv(code):#自動抓取全部表格
    datetime.date.today()
    for year in range(2020, 2022): #抓取近三年的資料
        for month in range(1, 13):
            if month < 10:
                date = str(year)+'0'+str(month) + '01' #因為必須輸入日期, 一次顯示一整個月, 所以幾日先都設定01號
            else:
                date = str(year) + str(month) + '01'  # 因為必須輸入日期, 一次顯示一整個月, 所以幾日先都設定01號
            filepath = r"C:\Users\user\PycharmProjects\pythonProject\stockproject\static" + '/' +\
                       str(code) + '/' + str(code) + '_' + str(date) + ".csv"
            folderpath = r"C:\Users\user\PycharmProjects\pythonProject\stockproject\static" + '/' + str(code)

            if os.path.isfile(filepath) == True:
                createDate_tocsv(date, code)
                time.sleep(5)
            else:
                if os.path.isdir(folderpath) == True:
                    i = datetime.date.today()
                    i = int(str(i).replace('-', ''))
                    if int(date) > i:
                        break
                    else:
                        createDate_tocsv(date, code)
                        time.sleep(5)
                else:
                    os.makedirs(folderpath)
                    createDate_tocsv(date, code)
                    time.sleep(5)
            time.sleep(10)

#檔名格式 : 代號 + _ + 年 + 月 + 01 + 檔案類型 ex: 2302_20210501.csv
def df_Merge(code): #將多表格結合成一個表格
    df = pd.DataFrame() #創建空的df
    df_y = pd.DataFrame()
    for year in range(2020, 2022):
        for month in range(1, 13):
            if month < 10:
                filename = 'static/' + str(code) + '/' + str(code) + '_' + str(year) + '0' + str(month) + '01.csv'
            else:
                filename = 'static/' + str(code) + '/' + str(code) + '_' + str(year) + str(month) + '01.csv'
            if os.path.isfile(filename) == False:
                break
            else:
                i = datetime.date.today()
                i = int(str(i).replace('-', ''))
                date = int(filename[17:23])
                if int(date) > i:
                    break
                else:
                    df_m = pd.read_csv(filename, index_col=None)
                # df_y = df_y.append(df_m, ignore_index=True)
                df = df.append(df_m, ignore_index=True)
    df.to_csv('static/{}/{}_2020to2021.csv'.format(code, code), index=False)



def get_stock_group(): #抓取各業界當日成交資訊 (group)
    url = 'https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html'
    driver = webdriver.Chrome('chromedriver')
    driver.implicitly_wait(5)
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    driver.get(url)
    ele_select = driver.find_element_by_xpath('//*[@id="main-form"]/div/div/form/select/option[36]') #分類項目選單
    ele_select.click()
    button = driver.find_element_by_xpath('//*[@id="main-form"]/div/div/form/a') #查詢按鈕
    button.click()
    time.sleep(5)
    new_html = driver.page_source
    page_button = driver.find_element_by_xpath('//*[@id="report-table1_length"]/label/select/option[5]') #每頁幾筆選單
    page_button.click()
    time.sleep(5)
    totalPage_html = driver.page_source
    df = pd.read_html(totalPage_html)
    df = df[0]
    # df.columns = [i[1] for i in df.columns] #整理表格
    df = pd.DataFrame(df)
    df = df.reset_index(drop=True)
    df = df.iloc[:21, :]

    df.to_csv('static/semiconductor_df.csv', encoding='utf-8', index=False) #中文csv檔案
    html = df.to_html()

    with open("static/semiconductor.html", "w", encoding="utf-8") as file: #將編碼寫入html檔案
        file.writelines('<meta charset="UTF-8">\n')
        file.write(html)
    # df.to_html('static/semiconductor.html', encoding='utf-8', index=False) #產生html檔案

    df.columns = ['Security Code', 'name', 'TradeVolume', 'Transaction', 'Trade Value',
                  'Open', 'High', 'Low', 'Close', 'Dir(+/-)', 'Change_l',
                  'Last Best Bid Price', 'Last Best Bid Volume', 'Last Best Ask Price',
                  'Last Best Ask Volume', 'Price-Earning ratio']

    df.to_csv('static/semiconductor_eng.csv', index=False) #英文csv檔案

def all_engData_tocsv(filename):  #計算均線等數據並建立新的欄位
    df = pd.read_csv(filename)
    if len(df.columns) > 9:
        df = df.iloc[:, 1:]
    # df.columns = ['Date', 'TradeVolume', 'TradeValue', 'Open', 'High', 'Law', 'Close', 'Change', 'Transaction',
    #               'MA_5', 'MA_20', 'MA_60', 'MA_120', 'BIAS_5', 'BIAS_20', 'BIAS_60', 'BIAS_120']
    df.columns = ['Date', 'TradeVolume', 'TradeValue', 'Open', 'High', 'Low', 'Close', 'Change', 'Transaction']
    # df.columns = ['Date', 'Open', 'High', 'Low', 'Close']

    df['MA_5'] = df['Close'].rolling(5).mean() #5日均線
    df['MA_20'] = df['Close'].rolling(20).mean() #20日均線
    df['MA_60'] = df['Close'].rolling(60).mean() #60日均線
    df['MA_120'] = df['Close'].rolling(120).mean() #120日均線
    df['EMA_12'] = df['Close'].ewm(span=12).mean()  # 指數移動平均線
    df['EMA_26'] = df['Close'].ewm(span=26).mean()

    df['DIF'] = df['EMA_12'] - df['EMA_26']  # DIF = 差離值 (快線)
    df['DEM'] = df['DIF'].ewm(span=9).mean()  # DEM 又稱 MACD值 (慢線)
    df['OSC'] = df['DIF'] - df['DEM']  # 柱狀圖(直方圖)

    df['BIAS_5'] = (df['Close'] - df['MA_5']) / df['MA_5']
    df['BIAS_20'] = (df['Close'] - df['MA_20']) / df['MA_20']
    df['BIAS_60'] = (df['Close'] - df['MA_60']) / df['MA_60']
    df['BIAS_120'] = (df['Close'] - df['MA_120']) / df['MA_120']
    df = df.fillna(0) #把Nan值補0
    # df = df.iloc[:, 1:]
    df.to_csv(filename[:-4] + '_eng.csv')

def df_sql(filepath): #將資料寫進資料庫
    df = pd.read_csv(filepath)
    mydb = mysql.connector.connect(host='localhost', user='root', passwd='root', database='stockdata')
    mycursor = mydb.cursor()
    sql_delete = ("DROP TABLE IF EXISTS `%s`")
    sql_delete = sql_delete.format('stock_'+filepath[7:11])
    mycursor.execute(sql_delete)
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/stockdata')
    # df.to_sql(filepath[7:-8], con=engine, if_exists='replace', index=False)
    df = df.replace([np.inf, -np.inf], np.nan)
    df.to_sql('stock_' + filepath[7:11], con=engine, if_exists='replace', index=False)
def kBar_MA(filepath): #畫K棒+均線圖
    df = pd.read_csv(filepath)
    code = filepath[7:11]
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    increasing_line_color='red', #更改k棒顏色
                    decreasing_line_color='green')])
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['MA_5'], name='MA_5'))
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['MA_20'], name='MA_20'))
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['MA_60'], name='MA_60'))
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['MA_120'], name='MA_120'))
    # fig.update_layout(yaxis_title='Price', xaxis_title='date', title=filepath[7:11])
    # fig.update_layout(yaxis_title='Price', xaxis_title='date', title=filepath[7:11])
    fig.update_layout(yaxis_title='Price', xaxis_title='date', title=filepath[7:12] + '_K棒均線圖')
    plotly.offline.plot(fig, filename=filepath[:-4] + '_kBar_Ma.html', auto_open=True)
    # plotly.offline.plot(fig, filename='static/{}/{}_2020to2021_kBar_Ma.html'.format(code, code), auto_open=False)

def MACD_OSC(filepath):#MACD BIAS 背離率
    df = pd.read_csv(filepath)
    fig = make_subplots(rows=2, cols=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BIAS_5'], name='BIAS_5'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BIAS_20'], name='BIAS_20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BIAS_60'], name='BIAS_60'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BIAS_120'], name='BIAS_120'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['DIF'], name='DIF快線'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['DEM'], name='MACD慢線'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['OSC'], name='OSC', fill='tozeroy'), row=2, col=1)
    fig.update_layout(title_text=filepath[7:12] + '乖離率_MACD指標')
    # fig.show()
    plotly.offline.plot(fig, filename=filepath[:-4] + '_MACD_OSC.html', auto_open=False)

def TAIEX_merge():
    df = pd.DataFrame()  # 創建空的df
    df_y = pd.DataFrame()
    for year in range(2020, 2022):
        for month in range(1, 13):
            if month < 10:
                filename = 'static/TAIEX' + '/' + str(year) + '-' + '0' + str(month) +'.csv'
            else:
                filename = 'static/TAIEX' + '/' + str(year) + '-' + str(month) + '.csv'
            if os.path.isfile(filename) == False:
                break
            else:
                df_m = pd.read_csv(filename)
                # df_y = df_y.append(df_m, ignore_index=True)
            df = df.append(df_m, ignore_index=True)

    # df = df.iloc[:, 1:]
    df.to_csv('static/TAIEX/2020to2021.csv', index=False)

def TAIEX(date): #產生加權指數
    import urllib.request, csv
    #自動抓取csv檔案

    url = 'https://www.twse.com.tw/indicesReport/MI_5MINS_HIST?response=csv&date=' + str(date)
    webpage = urllib.request.urlopen(url)
    data = csv.reader(webpage.read().decode('cp950').splitlines())
    time.sleep(10)
    columns_list = []
    date_list = []
    open_list = []
    high_list = []
    low_list = []
    close_list = []
    data_list = [i for i in data] #列數
    columns_list = data_list[1][:-1]
    for num in range(2, len(data_list)):
        year = int(data_list[num][0][:3]) + 1911
        month = data_list[num][0][3:]
        date = str(year) + month.replace('/', '-') #2021-01-01
        date_list.append(date)
        open_list.append(float(data_list[num][1].replace(',', '')))
        high_list.append(float(data_list[num][2].replace(',', '')))
        low_list.append(float(data_list[num][3].replace(',', '')))
        close_list.append(float(data_list[num][4].replace(',', '')))
    df = pd.DataFrame({'Date' : date_list, 'Open':open_list, 'High':high_list, 'Low':low_list, 'close':close_list}, index=None)
    time.sleep(10)
    df.to_csv('static/TAIEX/' + str(date)[:-3] + '.csv', index=False)

def auto_TAIEX():
    for year in range(2020, 2022):  # 抓取近三年的資料
        for month in range(1, 13):
            if month < 10:
                date = str(year) + '-' + '0' + str(month) # 因為必須輸入日期, 一次顯示一整個月, 所以幾日先都設定01號
            else:
                date = str(year) + '-' + str(month)  # 因為必須輸入日期, 一次顯示一整個月, 所以幾日先都設定01號
            filepath = r"C:\Users\user\PycharmProjects\pythonProject\static\TAIEX" + str(date) + '.csv'
            folderpath = r"C:\Users\user\PycharmProjects\pythonProject\static\TAIEX"

            if os.path.isfile(filepath) == True:
               break
            else:
                if os.path.isdir(folderpath) == True:
                    TAIEX(date.replace('-', '')+'01')
                    time.sleep(5)
                else:
                    os.makedirs(folderpath)
                    TAIEX(date.replace('-', '')+'01')
                    time.sleep(5)
                time.sleep(5)

def KD_value():
    df = pd.read_csv('static/2302/2302_2020to2021_eng.csv')
    min_close9 = df['Close'].rolling(9).min() #近9日收盤價最小值
    min_close9 = np.nan_to_num(min_close9)
    Min_close = pd.DataFrame(min_close9)
    Min_close.columns = ['MIN9']
    Min_close.index = df['Close'].index
    df['MIN9'] = Min_close['MIN9']

    max_close9 = df['Close'].rolling(9).max() #近9日收盤價最大值
    max_close9 = np.nan_to_num(max_close9)
    Max_close = pd.DataFrame(max_close9)
    Max_close.columns = ['MAX9']
    Max_close.index = df['Close'].index
    df['MAX9'] = Max_close['MAX9']


    rsv = ((df['Close']-df['MIN9'])/(df['MAX9']-df['MIN9'])) * 100  #   (17.55-17.4)/0.5*100
    rsv = np.nan_to_num(rsv)
    RSV = pd.DataFrame(rsv)
    RSV.columns = ['RSV']
    RSV.index = df['Close'].index
    df['RSV'] = RSV['RSV']



    # df.to_csv('static/2302/2302_2019to2021.csv')
    # df['RSV'][8] #第九天的RSV值
    #創建K值
    k1 = []
    for a in range(8):
        b = 50
        k1.append(b)
    k1 = pd.DataFrame(k1)
    k1.columns = ['k']

    k2 = []
    k_temp = 50
    for i in range(len(df)-8): #前8日因為沒有數據, 所以不算
        k_temp = k_temp * (2/3) + df['RSV'][i + 8] * (1/3)
        k2.append(k_temp)
    k2 = pd.DataFrame(k2)
    k2.columns = ['k']

    k = pd.concat([k1, k2], axis=0) #計算出k值
    k.index = df['Close'].index
    df['k'] = k['k'] #將k值欄位加入df
    # print(df)
    #創建D值
    d1 = []
    for a in range(8):
        b = 50 #初始值
        d1.append(b)
    d1 = pd.DataFrame(d1)
    d1.columns = ['d']
    d2 = []
    d_temp = 50
    for j in range(len(df)-8):
        d_temp = d_temp * (2/3) + df['k'][j + 8] * (1/3)
        d2.append(d_temp)
    d2 = pd.DataFrame(d2)
    d2.columns = ['d']
    d = pd.concat([d1, d2])
    d.index = df['Close'].index
    df['d'] = d['d']
    print(df)
    return df

# DIF = 差離值 (快線)
# DEM 又稱 MACD值 (慢線)

def cross_data(): #黃金/死亡交叉線圖
    df = pd.read_csv('static/semiconductor_eng.csv')
    code_list = df['Security Code'].tolist()
    today_gol = []
    today_dea = []
    for l in range(0, 21):
        golden_list = []
        death_list = []
        up_list = []
        down_list = []
        code = code_list[l]
        filename = 'static/{}/{}_2020to2021_eng.csv'.format(code, code)
        df = pd.read_csv(filename)
        macd = df['DEM'].tolist()
        dif = df['DIF'].tolist()
        day = df['Date'].tolist()
        golden = 0
        death = 0
        up = 0
        down = 0
        day_row = len(day) #計算總共有幾個交易日期
        # print(day_row)
        for d in range(1, day_row):
                if macd[d-1] < dif[d-1] and macd[d] > dif[d]: #死亡交叉
                    death += 1
                    death_list.append(day[d]) #將黃金交叉的日期寫入清單
                elif macd[d-1] > dif[d-1] and macd[d] < dif[d]: #黃金交叉
                    golden += 1
                    golden_list.append(day[d])
                elif macd[d-1] >= dif[d-1] and macd[d] > dif[d]: #快線上漲到觸碰到慢線後又下跌
                    down += 1
                    down_list.append(day[d])
                elif macd[d-1] <= dif[d-1] and macd[d] < dif[d]: #快線下跌觸碰到慢線後又上漲
                    up += 1
                    up_list.append(day[d])
                else:
                    pass
        print(code)
        print('黃金交叉:', golden_list[-1])
        print('死亡交叉:', death_list[-1])
        today_gol.append(golden_list[-1])
        today_dea.append(death_list[-1])
        print('-'*100)
        print(today_dea)
        print(today_gol)

def createDate_tocsv(date, code): #產生個股月份資訊

    url = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date='+str(date)+'&stockNo='+str(code)
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                            '(KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}
    resp = requests.get(url, headers=headers)
    time.sleep(5)
    data = resp.json() #type=dict
    # columns = data['fields']
    date_list = []
    volume_list = [] #成交股數
    value_list = [] #成交金額
    open_list = []
    high_list = []
    low_list = []
    close_list = []
    change_list = [] #漲跌價差
    transaction_list = [] #交易筆數

    for day in range(len(data['data'])):
        date_year = int(data['data'][day][0][:3]) + 1911
        date_month = data['data'][day][0][3:]
        date_list.append((str(date_year) + date_month.replace('/', '-')))
        volume_list.append(int(data['data'][day][1].replace(',', '')))
        value_list.append(int(data['data'][day][2].replace(',', '')))
        open_list.append(float(data['data'][day][3].replace('--', '0').replace(',', '')))
        high_list.append(float(data['data'][day][4].replace('--', '0').replace(',', '')))
        low_list.append(float(data['data'][day][5].replace('--', '0').replace(',', '')))
        close_list.append(float(data['data'][day][6].replace('--', '0').replace(',', '')))
        change_list.append(float(data['data'][day][7].replace('+', '').replace('X', '')))
        transaction_list.append(int(data['data'][day][8].replace(',', '')))

    df = pd.DataFrame({'日期':date_list, '成交股數':volume_list, '成交金額':value_list,
                      '開盤價':open_list, '最高價':high_list, '最低價':low_list, '收盤價':close_list,
                      '帳跌價差':change_list, '成交筆數':transaction_list})
    time.sleep(3)
    filepath = "static/{}/{}_{}".format(code, code, date)
    df.to_csv(filepath + '.csv')

    # AllDf = AllDf.append(df, ignore_index=True)
    html = df.to_html()
    with open(filepath+'.html', "w", encoding="utf-8") as file: #將編碼寫入html檔案
        file.writelines('<meta charset="UTF-8">\n')
        file.write(html)
    # time.sleep(3)
    # df.columns = ['Date', 'TradeVolume', 'TradeValue', 'Open', 'High', 'Low', 'Close', 'Change', 'Transaction']
    time.sleep(3)

def line_frame():
    df = pd.read_csv('semiconductor_eng.csv')
    code_list = df['Security Code'].tolist()

    for l in range(21):
        code = code_list[l]
        filepath = 'static/{}/{}_2020to2021_eng.csv'.format(code, code)
        kBar_MA(filepath) #k線均線圖
        MACD_OSC(filepath)
def all_TAIEXengData_tocsv(filename):  #計算均線等數據並建立新的欄位
    df = pd.read_csv(filename)
    # if len(df.columns) > 9:
    #     df = df.iloc[:, 1:]
    # df.columns = ['Date', 'TradeVolume', 'TradeValue', 'Open', 'High', 'Law', 'Close', 'Change', 'Transaction',
    #               'MA_5', 'MA_20', 'MA_60', 'MA_120', 'BIAS_5', 'BIAS_20', 'BIAS_60', 'BIAS_120']
    # df.columns = ['Date', 'TradeVolume', 'TradeValue', 'Open', 'High', 'Low', 'Close', 'Change', 'Transaction']
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close']

    df['MA_5'] = df['Close'].rolling(5).mean() #5日均線
    df['MA_20'] = df['Close'].rolling(20).mean() #20日均線
    df['MA_60'] = df['Close'].rolling(60).mean() #60日均線
    df['MA_120'] = df['Close'].rolling(120).mean() #120日均線
    df['EMA_12'] = df['Close'].ewm(span=12).mean()  # 指數移動平均線
    df['EMA_26'] = df['Close'].ewm(span=26).mean()

    df['DIF'] = df['EMA_12'] - df['EMA_26']  # DIF = 差離值 (快線)
    df['DEM'] = df['DIF'].ewm(span=9).mean()  # DEM 又稱 MACD值 (慢線)
    df['OSC'] = df['DIF'] - df['DEM']  # 柱狀圖(直方圖)

    df['BIAS_5'] = (df['Close'] - df['MA_5']) / df['MA_5']
    df['BIAS_20'] = (df['Close'] - df['MA_20']) / df['MA_20']
    df['BIAS_60'] = (df['Close'] - df['MA_60']) / df['MA_60']
    df['BIAS_120'] = (df['Close'] - df['MA_120']) / df['MA_120']
    df = df.fillna(0) #把Nan值補0
    # df = df.iloc[:, 1:]
    df.to_csv(filename[:-4] + '_eng.csv')


def percent_Analytics():
    df = pd.read_csv('static/semiconductor_eng.csv')
    code_list = df['Security Code'].tolist()
    code_list = code_list[:21]
    today_change = []
    continues_change = []
    hiscon_change = []
    today_gol = []
    today_dea = []

    for l in range(0, 21):
        code = code_list[l]
        golden_list = []
        death_list = []
        filename = 'static/{}/{}_2020to2021_eng.csv'.format(code, code)
        df = pd.read_csv(filename)
        date = df.index
        # len(date)
        up = 0  # 上漲日
        down = 0  # 下跌日
        up_list = []  # 連續上漲日
        down_list = []  # 連續下跌日
        change_list = []  # 漲幅清單
        up_list.insert(0, 0)
        down_list.insert(0, 0)
        change_list.insert(0, '0')
        for i in range(1, len(date)):
            ans = ((df['Close'][i] - df['Close'][i - 1]) / df['Close'][i - 1]) * 100
            if ans > 0:
                down = 0
                change_list.append("{:.2f}".format(ans))
                up += 1
                up_list.append(up)
                down_list.append(0)
            elif ans < 0:
                up = 0
                change_list.append("{:.2f}".format(ans))
                down -= 1
                down_list.append(down)
                up_list.append(0)
            elif ans == 0:
                up = 0
                down = 0
                change_list.append('0.00')
                up_list.append(0)
                down_list.append(0)

        if float(change_list[-1]) > 0:  # 今日漲
            today_change.append(change_list[-1])
            continues_change.append(up_list[-1])
            hiscon_change.append(max(up_list))
            # print('{}--本日漲幅:{}%, 連續漲{}日, 連續最長漲:{}日'.format(code, change_list[-1], up_list[-1], max(up_list)))
        elif float(change_list[-1]) < 0:  # 今日跌
            today_change.append(change_list[-1])
            continues_change.append(down_list[-1])
            hiscon_change.append(min(down_list))
            # print('{}--本日跌幅:{}%, 連續跌{}日, 連續最長跌:{}日'.format(code, change_list[-1], down_list[-1], max(down_list)))
        elif float(change_list[-1]) == 0:
            today_change.append(change_list[-1])
            continues_change.append('0')
            hiscon_change.append(max(up_list))
            # print('{}--本日平盤:{}%, 連續最長漲/跌:{}/{}日'.format(code, change_list[-1], max(up_list), max(down_list)))

        macd = df['DEM'].tolist()
        dif = df['DIF'].tolist()
        day = df['Date'].tolist()
        golden = 0
        death = 0
        up = 0
        down = 0
        day_row = len(day) #計算總共有幾個交易日期
        # print(day_row)
        for d in range(1, day_row):
                if macd[d-1] < dif[d-1] and macd[d] > dif[d]: #死亡交叉
                    death += 1
                    death_list.append(day[d]) #將黃金交叉的日期寫入清單
                elif macd[d-1] > dif[d-1] and macd[d] < dif[d]: #黃金交叉
                    golden += 1
                    golden_list.append(day[d])
                elif macd[d-1] >= dif[d-1] and macd[d] > dif[d]: #快線上漲到觸碰到慢線後又下跌
                    down += 1
                    down_list.append(day[d])
                elif macd[d-1] <= dif[d-1] and macd[d] < dif[d]: #快線下跌觸碰到慢線後又上漲
                    up += 1
                    up_list.append(day[d])
                else:
                    pass
        today_gol.append(golden_list[-1])
        today_dea.append(death_list[-1])
    df1 = pd.DataFrame({'代碼':code_list, '今日漲/跌幅':today_change, '目前連續漲/跌幅':continues_change, '連續最長漲/跌幅':hiscon_change,
                        '最近一次黃金交叉':today_gol, '最近一次死亡交叉':today_dea})
    html = df1.to_html()
    with open('analysis.html', "w", encoding="utf-8") as file: #將編碼寫入html檔案
        file.writelines('<meta charset="UTF-8">\n')
        file.write(html)
#     change_percent(filename)
#     print(code, '更新完成')
# percent_Analytics()

# change_percent('static/2330/2330_2020to2021_eng.csv')
df = pd.read_csv('static/semiconductor_eng.csv')
code_list = df['Security Code'].tolist()
# cross_data()
percent_Analytics()

#自動更新順序
# for l in range(0, 1):
#     code = code_list[l]
#     filename = 'static/{}/{}_2020to2021.csv'.format(code, code)
#     filepath = 'static/{}/{}_2020to2021_eng.csv'.format(code, code)
    # stockDate_tocsv(code) #更新最新月份
    # auto_to_csv(code) #自動抓取多月份資料
    # df_Merge(code) #合併成統一表格 (中文)
    # all_engData_tocsv(filename)  #將表格轉換成英文並加入計算欄位
    # df_sql(filepath) #將資料寫進資料庫
    # kBar_MA(filepath) #k棒+均線圖
    # MACD_OSC(filepath) #背離率
#加權指數
# TAIEX(date) #產生加權指數 (個月份)
# TAIEX_merge() #合併
# all_TAIEXengData_tocsv(filename) #k棒+均線圖
# kBar_MA(filename) #k棒+均線圖
# MACD_OSC(filepath)