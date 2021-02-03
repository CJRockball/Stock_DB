# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 20:25:23 2019

@author: CJ ROCKBALL
"""

from flask import Flask, request,render_template,session

import webbrowser
import os
import sqlite3
import numpy as np
import pandas as pd
from pandas_datareader import data
from math import pi

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.palettes import d3


#Connect to db
conn = sqlite3.connect("stock.db")
conn.execute("PRAGMA foreign_keys = 1")
cur = conn.cursor()
#Create a table
cur.execute("""CREATE TABLE IF NOT EXISTS stock_ticker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL UNIQUE,
                name TEXT,
                start_date DATE,
                end_date DATE );""")


cur.execute("""CREATE TABLE IF NOT EXISTS stock_hist (
                stock_id INTEGER,
                date DATE,
                high REAL,
                low REAL,
                open REAL,
                close REAL,
                volume INTEGER);""")

# Write changes
# Write changes
conn.commit()
conn.close()

def plot_candle(df):
    # Graphing, set up up/down candlestick
    mids = (df.Open + df.Close)/2
    spans = abs(df.Close-df.Open)
    
    inc = df.Close > df.Open
    dec = df.Open > df.Close
    w = 18*60*60*1000 # half day in ms
    
    # Graphing set up Bokeh graph    
    p = figure(x_axis_type="datetime", plot_width=1000, 
                y_axis_label = "Price", x_axis_label = "Date")
    
    p.segment(df.Date, df.High, df.Date, df.Low, color="black")
    p.rect(df.Date[inc], mids[inc], w, spans[inc], fill_color='green', line_color="green")
    p.rect(df.Date[dec], mids[dec], w, spans[dec], fill_color='red', line_color="red")

    p.title.text = 'Stock chart'
    p.xaxis.major_label_orientation = pi/4  

    return p

def plot_line(df):
    stocks_ser = df['Stock'].unique()
    
    p = figure(x_axis_type="datetime", plot_width=1000,
                y_axis_label = "Price", x_axis_label = "Date")
    c_num = 0
    for stock in stocks_ser:
        temp_data = df.Close[df['Stock'] == stock]
        temp_date = df.Date[df['Stock'] == stock]
        p.line(temp_date, temp_data, line_width = 2, color = d3['Category20'][20][c_num],\
               legend_label=str(stock))
        c_num = c_num + 1
    
    p.title.text = 'Stock chart'
    p.xaxis.major_label_orientation = pi/4  

    return p

def plot_normalline(df):
    stocks_ser = df['Stock'].unique()
    
    p = figure(x_axis_type="datetime", plot_width=1000,
                y_axis_label = "Price", x_axis_label = "Date")
    c_num = 0
    for stock in stocks_ser:
        temp_data = df.Close[df['Stock'] == stock]
        temp_data = temp_data / temp_data.iloc[0]
        temp_date = df.Date[df['Stock'] == stock]
        p.line(temp_date, temp_data, line_width = 4, color = d3['Category20'][20][c_num],\
               legend_label=str(stock))
        c_num = c_num + 1
    
    p.title.text = 'Stock chart'
    p.xaxis.major_label_orientation = pi/4  

    return p


def check_dates(stock_ticker, start, end):
    #Get dates/data from db and compare with new download
    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()
    cur.execute("SELECT start_date, end_date FROM stock_ticker WHERE ticker = ?;", stock_ticker)   
    db_dates = cur.fetchall()
    db_start = db_dates[0][0]
    db_end = db_dates[0][1]
    conn.commit()
    conn.close()
    
    if   db_start <= start and db_end >= end: return 0, db_start, db_end         
    elif db_start > start and db_end >= end: return 1, start, db_start  
    elif db_start <= start and db_end < end: return 1, db_end, end
    elif db_start > start and db_end < end: return 2, start, end
        
    
def dl_new(stock_name, stock_ticker, start,end):
     #Get data
    print(start,end)
    df = data.DataReader(stock_ticker, 'yahoo', start,end)
    df["date"] = pd.to_datetime(df.index)
    #Make lists
    date_list = df.date.dt.date.astype(str).to_list()
    open_list = df.Open.round(2).to_list()
    high_list = df.High.round(2).to_list()
    low_list = df.Low.round(2).to_list()
    close_list = df.Close.round(2).to_list()
    vol_list = df.Volume.astype(int).to_list()
    
    # Handle stock_name if not present
    if stock_name == '':
        ticker_name = "None"
    else:
        ticker_name = str(stock_name)
    
    stock_ticker_tuple = (stock_ticker, ticker_name, start, end)
    
    #Connect to db
    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()
    
    cur.execute("INSERT OR IGNORE INTO stock_ticker (ticker, name, start_date, end_date) VALUES (?,?,?,?);""",stock_ticker_tuple)
    #insert_id = cur.lastrowid #gives row id of last inserted
    conn.commit()
    param = ((stock_ticker),)
    cur.execute("SELECT id FROM stock_ticker WHERE ticker = ?", param)
    ticker_number = cur.fetchall()
    #Get ticker number for new entry
    ticker_id_list = [ticker_number[0][0]]*len(date_list)
    #Make tuples for db insert
    result_tuple = []
    for i in range(len(date_list)):
        result_tuple.append((ticker_id_list[i], date_list[i], high_list[i], low_list[i], open_list[i], close_list[i], vol_list[i]))
    
    cur.executemany("INSERT INTO stock_hist VALUES (?,?,?,?,?,?,?);""",result_tuple)
    # Write change
    conn.commit()
    conn.close()
    return

def dl_part(name_check, stock_ticker, start2,end2):  
    #Get data
    df = data.DataReader(stock_ticker, 'yahoo', start2,end2) # 'VOLV-B.ST' 'ASSA-B.ST'
    df["date"] = pd.to_datetime(df.index)
    #Make lists
    date_list = df.date.dt.date.astype(str).to_list()
    open_list = df.Open.round(2).to_list()
    high_list = df.High.round(2).to_list()
    low_list = df.Low.round(2).to_list()
    close_list = df.Close.round(2).to_list()
    vol_list = df.Volume.astype(int).to_list()
    ticker_id_list = [name_check[0][1]]*len(date_list)
    #Make tuple for stock_hist
    result_tuple = []
    for i in range(len(date_list)):
        result_tuple.append((ticker_id_list[i], date_list[i], high_list[i], low_list[i], open_list[i], close_list[i], vol_list[i])) 
    
    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()
    cur.executemany("INSERT INTO stock_hist VALUES (?,?,?,?,?,?,?);""",result_tuple)
    conn.commit()
    
    update_stock_id = str(name_check[0][1])
    cur.execute("SELECT MIN(date) FROM stock_hist WHERE stock_id = ?;", update_stock_id)
    start_date = cur.fetchone()
    cur.execute("SELECT MAX(date) FROM stock_hist WHERE stock_id = ?;",  update_stock_id)
    end_date = cur.fetchone()
    #Make stock_ticker tuple
    ticker_result_tuple = (start_date[0], end_date[0], update_stock_id)
    
    cur.execute("""UPDATE stock_ticker 
                    SET start_date = ?, end_date = ? 
                    WHERE id = ?;""",ticker_result_tuple)
    
    # Write change
    conn.commit()
    conn.close()
    return

def dl_full(name_check, stock_ticker, start2,end2):
    #Get data
    df = data.DataReader(stock_ticker, 'yahoo', start2,end2)
    df["date"] = pd.to_datetime(df.index)
    #Make lists
    date_list = df.date.dt.date.astype(str).to_list()
    open_list = df.Open.round(2).to_list()
    high_list = df.High.round(2).to_list()
    low_list = df.Low.round(2).to_list()
    close_list = df.Close.round(2).to_list()
    vol_list = df.Volume.astype(int).to_list()
    ticker_id_list = [name_check[0][1]]*len(date_list)
    #Make tuple for stock_hist
    result_tuple = []
    for i in range(len(date_list)):
        result_tuple.append((ticker_id_list[i], date_list[i], high_list[i], low_list[i], open_list[i], close_list[i], vol_list[i])) 
    #Delete old records
    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()
    update_stock_id = str(name_check[0][1])
    cur.execute("DELETE FROM stock_hist WHERE stock_id = ?;",  update_stock_id)
    conn.commit()
    #Inset new records
    cur.executemany("INSERT INTO stock_hist VALUES (?,?,?,?,?,?,?);""",result_tuple)
    cur.execute("SELECT MIN(date) FROM stock_hist WHERE stock_id = ?;", update_stock_id)
    start_date = cur.fetchone()
    cur.execute("SELECT MAX(date) FROM stock_hist WHERE stock_id = ?;",  update_stock_id)
    end_date = cur.fetchone()
    #Make stock_ticker tuple
    ticker_result_tuple = (start_date[0], end_date[0], update_stock_id)
    
    cur.execute("""UPDATE stock_ticker 
                    SET start_date = ?, end_date = ? 
                    WHERE id = ?;""",ticker_result_tuple)
    
    # Write change
    conn.commit()
    conn.close()
    return

def load_data_func(stock_tick, start, end):
    #Connect to db
    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()
     
    cur.execute("""SELECT stock_hist.rowid,stock_ticker.ticker, stock_ticker.name, stock_hist.date, stock_hist.high,
                stock_hist.low, stock_hist.open, stock_hist.close, stock_hist.volume
                FROM stock_ticker JOIN stock_hist
                ON stock_ticker.id = stock_hist.stock_id AND stock_ticker.ticker = ?
                AND stock_hist.date BETWEEN ? AND ?;""", (stock_tick, start, end))
                
    datas = cur.fetchall() 
    # Write change
    conn.commit()
    conn.close() 
    
    stock_arr = np.array(datas)
    df2 = pd.DataFrame(data=stock_arr[:,1:], index=stock_arr[:,0])
    df2.columns = ("Stock", "Ticker", "Date", "High", "Low", "Open", "Close", "Volume")
    df2[[ "High", "Low", "Open", "Close", "Volume"]] = df2[[ "High", "Low", "Open", "Close", "Volume"]].apply(pd.to_numeric)
    df2["Date"] = pd.to_datetime(df2["Date"])
    dat = session.get("data")
    df = pd.read_json(dat, dtype=False)
    df = pd.concat([df, df2])
    
    session['dl'] = True
    session["data"] = df.to_json()
    
    temp = [(stock_tick, start, end),]
    session["loaded"] = session["loaded"] + temp
    return

def read_all():
    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()
    
    cur.execute("SELECT ticker,name, start_date, end_date FROM stock_ticker;")
    db_tickers = cur.fetchall()
    
    # Write change
    conn.commit()
    conn.close()
    return db_tickers

app = Flask(__name__)
app.secret_key = os.urandom(28)


@app.route('/')
def index():    
    return render_template('dl_stock_index.html')
    

@app.route('/dl_data', methods=['GET', 'POST'])
def dl_data():
    if request.method == 'POST':
        db_tickers = read_all()
       
        if request.form.get('Return') == 'Return':
            return render_template("dl_stock_index.html")
        elif request.form.get("Download") == "Download":
            stock_ticker = request.form['stock_ticker']
            stock_name = request.form['stock_name']
            start = request.form['start']
            end = request.form['end']
            param = ((stock_ticker),)
            #Check if data already in the db
            conn = sqlite3.connect("stock.db")
            cur = conn.cursor()
            cur.execute("Select name,id FROM stock_ticker WHERE ticker = ?;", param)
            name_check = cur.fetchall()
            # Write change
            conn.commit()
            conn.close()
            
            if len(name_check) < 1:
                dl_new(stock_name, stock_ticker, start,end)
                db_tickers = read_all()
                return render_template('dl_data.html', db_stocks = db_tickers)          
            else:
                flag, start2, end2 = check_dates(stock_ticker, start, end)
                if flag == 0:
                    db_tickers = read_all()
                    return render_template('dl_data.html', db_stocks = db_tickers)              
                elif flag == 1:
                    dl_part(name_check, stock_ticker, start2,end2)
                    db_tickers = read_all()
                    return render_template('dl_data.html', db_stocks = db_tickers)
                elif flag == 2:
                    dl_full(name_check, stock_ticker, start2,end2)
                    db_tickers = read_all()
                    return render_template('dl_data.html', db_stocks = db_tickers)
                    
        else:
            return 'Something went wrong'
    elif request.method == 'GET':
        db_tickers = read_all()
        return render_template('dl_data.html', db_stocks = db_tickers)
                
    return render_template('dl_data.html')

@app.route('/display', methods=['GET', 'POST'])
def display():
    if request.method == 'POST':
        if request.form.get('Return') == 'Return':
            return render_template("dl_stock_index.html")
        else:
            return 'Button function'
    elif request.method == 'GET':
        return render_template('display.html')
                
    return render_template('display.html')

@app.route('/load_data', methods=['GET', 'POST'])
def load_data():
    if request.method == 'POST':
        if request.form.get('Return') == 'Return':
            return render_template("dl_stock_index.html")
        
        elif request.form.get('Load') == 'Load':
            stock_tick = request.form['stock_ticker']
            start = request.form['start']
            end = request.form['end']
            
            load_data_func(stock_tick, start, end) 
            db_tickers = read_all()
            return render_template('load_data.html', db_stocks = db_tickers)    
        
        if request.form.get('Clear') == 'Clear':
            session["loaded"] = []
            df = pd.DataFrame(columns=["Stock", "Ticker", "Date", "High", "Low", "Open", "Close", "Volume"])
            session["data"] = df.to_json()
            session["dl"] = False
            db_tickers = read_all()
            return render_template('load_data.html', db_stocks = db_tickers)
        
        if request.form.get('Plot') == 'Plot':
            if request.form.get('graph') == 'candle':
                dat = session.get("data")
                df = pd.read_json(dat, dtype=False)
                df[[ "High", "Low", "Open", "Close", "Volume"]] = df[[ "High", "Low", "Open", "Close", "Volume"]].apply(pd.to_numeric)
                df["Date"] = pd.to_datetime(df["Date"])            
                graph = plot_candle(df)
                script, div = components(graph)  
                db_tickers = read_all()
                return render_template('load_data.html', script = script, div = div, db_stocks = db_tickers)
        
            elif request.form.get('graph') == 'line':
                dat = session.get("data")
                df = pd.read_json(dat, dtype=False)
                df[[ "High", "Low", "Open", "Close", "Volume"]] = df[[ "High", "Low", "Open", "Close", "Volume"]].apply(pd.to_numeric)
                df["Date"] = pd.to_datetime(df["Date"])
                graph = plot_line(df)
                script, div = components(graph)
                db_tickers = read_all()
                return render_template('load_data.html', script = script, div = div, db_stocks = db_tickers)
            
            elif request.form.get('graph') == 'nline':
                dat = session.get("data")
                df = pd.read_json(dat, dtype=False)
                df[[ "High", "Low", "Open", "Close", "Volume"]] = df[[ "High", "Low", "Open", "Close", "Volume"]].apply(pd.to_numeric)
                df["Date"] = pd.to_datetime(df["Date"])
                graph = plot_normalline(df)
                script, div = components(graph)
                db_tickers = read_all()
                return render_template('load_data.html', script = script, div = div, db_stocks = db_tickers)
            
            else: return render_template('load_data.html', db_stocks = db_tickers)                
        else: return 'Plot Error'

         
    elif request.method == 'GET':
        session["dl"] = False
        df = pd.DataFrame(columns=["Stock", "Ticker", "Date", "High", "Low", "Open", "Close", "Volume"])
        session["data"] = df.to_json()
        session["loaded"] = []
        db_tickers = read_all()
        return render_template('load_data.html', db_stocks = db_tickers)
                
    else: return "GET/POST error"

@app.route('/view_db', methods=['GET', 'POST'])
def view_db():
    if request.method == 'POST':
        if request.form.get("Return") == "Return":
            return render_template("dl_stock_index.html")
        else:
            return 'Button function'
    elif request.method == 'GET':
        conn = sqlite3.connect("stock.db")
        cur = conn.cursor()
        
        cur.execute("SELECT ticker,name, start_date, end_date FROM stock_ticker;")
        db_tickers = cur.fetchall()
        
        # Write change
        conn.commit()
        conn.close()
        return render_template('view_db.html', db_stocks = db_tickers)

    return render_template('view_db.html')


if __name__ == "__main__":
    webbrowser.open('http://localhost:5000/')
    app.run()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    