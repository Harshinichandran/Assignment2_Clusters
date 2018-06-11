# # import uuid
# # from numpy import vstack,array
# from scipy.cluster.vq import *
import pandas
import pandas as pd
import math
from math import sin, cos, sqrt, atan2, radians
from datetime import datetime, timedelta
import pytest
from sklearn.cluster import KMeans
from sklearn import metrics
import numpy as np
from numpy.core.umath import deg2rad
from sqlalchemy import create_engine
from flask import Flask, render_template, request, send_file
import sqlite3 as sqll


app = Flask(__name__)

# conn = sqll.connect('Assig2.db')
# conn.set_limit(sqll.SQLITE_LIMIT_VARIABLE_NUMBER, 1337)
########################################################################################################################
# db = create_engine('sqlite:///Assig2.db')
# with db.connect() as con, con.begin():
#
#     chunks = pandas.read_csv('all_day.csv',chunksize=1000)
#     for chunk in chunks:
#         chunk[['date', 'time']] = chunk['time'].str.split('T', expand=True)
#         chunk['time'] = chunk['time'].str.split('.').str[0]
#         chunk.to_sql("EarthQuake1", con, if_exists='replace')
conn = sqll.connect('Assign2.db')
df = pd.read_csv("edata.csv")
df['lat_rad'] = deg2rad(df['latitude'])
df['long_rad'] = deg2rad(df['longitude'])
df[['date', 'time']] = df['time'].str.split('T', expand=True)
df['time'] = df['time'].str.split('.').str[0]
df.to_sql('EarthQuake1', conn, if_exists='replace', index=False)

print(df)

########################################################################################################################

@app.route('/')
def home():
    return render_template('home.html')
#######################################################################################################################
@app.route('/Radius', methods=['POST'])
def Radius():
    LatCoord = request.form['LatCoord']
    LongCoord = request.form['LongCoord']
    # LatCoord_rad=deg2rad(LatCoord)
    # LongCoord_rad=deg2rad(LongCoord)
    Dist = request.form['Dist']
    con = sqll.connect("Assign2.db")
    con.row_factory = sqll.Row
    cur = con.cursor()
    # cur.execute("SELECT mag FROM EarthQuake1 WHERE math.acos(sin(?) * sin(latitude) + cos(?) * cos(latitude) * cos("
    #             "longitude - (?))) * 6371 <= ?",(LatCoord,LatCoord,LongCoord,Distance))
    # Query='SELECT mag FROM EarthQuake1 WHERE math.acos(sin('+LatCoord+') * sin(latitude) + cos('+LatCoord+') * cos(latitude) * cos(longitude - ('+LongCoord+'))) * 6371 <= '+Distance+';'
    # Query = 'SELECT mag FROM EarthQuake1 WHERE (math.acos(sin(' + LatCoord + ') * sin(lat_rad) + cos(' + LatCoord + ') * cos(lat_rad) * cos(long_rad - (' + LongCoord + '))))* 6371 <= '+Distance+';'

    # cur.execute('SELECT mag FROM EarthQuake1 WHERE math.sin(lat_rad) >'+Distance+';')
    # cur.execute('SELECT mag FROM EarthQuake1 where latitude =' + LatCoord + ';')
    # cur.execute('SELECT mag FROM EarthQuake1 where latitude like \'%' + LatCoord + '%\';')
    cur.execute('SELECT * FROM EarthQuake1')
    rows = cur.fetchall()
    ct=0
    for row in rows:
        pair = []
        x = float(row["latitude"])
        y = float(row["longitude"])
        R = 6373.0

        lat1 = radians(float(LatCoord))
        lon1 = radians(float(LongCoord))
        lat2 = radians(x)
        lon2 = radians(y)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        if distance <= float(Dist):
            ct+=1

    # rows = cur.fetchall()
    return render_template('Home.html',count=ct)

#######################################################################################################################
@app.route('/PrevDays', methods=['POST'])
def PrevDays():
    PrevDays = request.form['PrevDays']
    d = datetime.today() - timedelta(days=4)
    con = sqll.connect("Assign2.db")
    con.row_factory = sqll.Row
    cur = con.cursor()
    cur.execute('SELECT mag FROM EarthQuake1 where mag > ? and date between ? and ?', (PrevDays,d,datetime.today()))

    rows = cur.fetchall()

    return render_template('Home.html',rows=rows)

########################################################################################################################
@app.route('/GreatMag', methods=['POST'])
def GreatMag():
    GreatMag = request.form['GreatMag']
    con = sqll.connect("Assign2.db")
    con.row_factory = sqll.Row
    cur = con.cursor()
    cur.execute('SELECT mag FROM EarthQuake1 where mag > ?', (GreatMag,))
    # cur.execute('SELECT * FROM EarthQuake')

    rows = cur.fetchall()
    count = 0
    for row in rows:
        count = count + 1
        # magnitude.append("mag:" + row[0])
    # return vehicleName
    return render_template('Home.html', counter=count, rows=rows)
#########################################################################################################################

@app.route('/BetMag', methods=['POST'])
def BetMag():
    StartMag = request.form['StartMag']
    EndMag = request.form['EndMag']
    StartDate = request.form['StartDate']
    EndDate = request.form['EndDate']
    con = sqll.connect("Assign2.db")
    con.row_factory = sqll.Row
    cur = con.cursor()
    cur.execute('SELECT date,mag FROM EarthQuake1 where mag between ? and ? AND date between date(?)and date(?)',
                (StartMag, EndMag, StartDate, EndDate))
    # cur.execute('SELECT time FROM EarthQuake where mag ? AND time LIKE \''+StartDate+'%\'',(StartMag,))
    rows = cur.fetchall()
    return render_template('Home.html', rows=rows)

########################################################################################################################
@app.route('/DayMag', methods=['POST'])
def DayMag():
    DayMag = request.form['DayMag']
    con = sqll.connect("Assign2.db")
    con.row_factory = sqll.Row
    cur1 = con.cursor()
    cur2= con.cursor()
    cur1.execute('SELECT mag FROM EarthQuake1 where mag > ? and time between time(?)and time(?)',
                (DayMag, '23:00:00', '23:59:59'))
    rows1 = cur1.fetchall()
    cur2.execute('SELECT mag FROM EarthQuake1 where mag > ? and time between time(?)and time(?)',
                [DayMag, '00:00:00', '00:59:59'])
    rows2 = cur2.fetchall()
    count1 = 0
    count2 = 0

    for row in rows1:
        count1 = count1 + 1
    for row in rows2:
        count2 = count2 + 1


    if count1 > count2:
        msg = str(count1)+"Earthquake occurs mostly at night"
        # msg= "count1"+str(count1)
    else:
        msg = str(count2)+" Earthquakes occurs mostly during day"
        # msg = "count2"+str(count2)

    return render_template('Home.html', msg=msg)
########################################################################################################################



if __name__ == '__main__':
    app.run(debug=True)
