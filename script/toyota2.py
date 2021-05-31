#!/usr/bin/env python3

# format copied content from HTML
# e.g. https://www.city.toyota.aichi.jp/pressrelease/1043093/1043562.html

import sys
import re
import pandas

print('症例番号\t年代\t性別\t居住地\t海外渡航歴\t発症日\t陽性確定日\t症状等\t特記事項')

url = sys.argv[1]
df = pandas.read_html(url)[0]

for i in range(len(df)):
    if i == 0:
        if df[0][i] == '発生番号':
            continue
        else:
            raise BaseException(df[0][i])

    try:
        n, age, sex, symp, day1 = df[0][i], df[1][i].replace(' 歳代', ''), df[2][i],\
            df[4][i], re.sub('(.*)（.*曜日）', '\\1', df[5][i])
    except:
        print(df[0][i])
        raise

    if df[6][i].find('発症') >= 0:
        day2 = re.sub('(.*)（.*曜日）発症', '\\1', df[6][i])
        note = ''
    else:
        day2 = ''
        note = re.sub('本市(\d*)例目の(同居家族|濃厚接触者)', '豊田市発表\\1例目の\\2', df[6][i])

    note = re.sub('岡崎市(\d*)例目', '岡崎市発表\\1例目', note)
    note = re.sub('豊橋市(\d*)例目', '豊橋市発表\\1例目', note)
    note = re.sub('名古屋市(\d*)例目', '名古屋市発表\\1例目', note)
    note = re.sub('一宮市(\d*)例目', '一宮市発表\\1例目', note)
    note = re.sub('愛知県(\d*)例目', '愛知県内\\1例目', note)

    print(f'{n}\t{age}\t{sex}\t豊田市\t\t{day2}\t{day1}\t{symp}\t{note}')
