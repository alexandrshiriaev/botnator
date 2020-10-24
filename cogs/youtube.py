import io
import json
import os
path = 'cogs\coinsbot.json'
import datetime
import psycopg2

con = psycopg2.connect(
    host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
    database = 'dfe269uifoco1o',
    user = 'ncdnwynzrmqjnc',
    password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
    port = 5432
)
cur = con.cursor()

arr = ['stone', 'iron', 'diamond']

selected = []

for resource in arr:
    cur.execute(f"SELECT {resource} FROM mine WHERE user_id='373848782602895360'")
    selected.append(cur.fetchone()[0])
print(selected)

cur.close()
con.close()
    