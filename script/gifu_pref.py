#!/usr/bin/env python3

# format copied content from PDF
# e.g. https://www.city.gifu.lg.jp/secure/44927/2021.01.27%20syousai_s.pdf

import sys
import re

f_all = sys.stdin.read().replace('\r', '\n')
f_all = f_all.replace(' ', '\t')

f_all = re.sub('\t(\d+)\tの', '\t岐阜県内\\1例目の', f_all)
f_all = re.sub('\t(\d+)\t等の', '\t岐阜県内\\1例目等の', f_all)
f_all = re.sub('\t([1-9]{1})([0]{1})\t', '\t\\1\\2代\t', f_all)
f_all = re.sub('\n10\t歳未\n満\n', '\t10歳未満\t', f_all)
f_all = re.sub('\t(男|女)\t', '\t\\1性\t', f_all)
f_all = re.sub('\(', '（', f_all)
f_all = re.sub('\)', '）', f_all)
f_all = re.sub('(\d{4,5})\t', '\\1例目\t', f_all)
f_all = re.sub('\t(\d{1,2}/\d{1,2})\n', '\t\\1\t\n', f_all)
f_all = re.sub('\t調査中\n', '\t調査中\t\n', f_all)
f_all = re.sub('\n10歳未\n満\n(男|女)\t', '10歳未満\t\\1性\t', f_all)
f_all = re.sub('\n10\t歳\n未満\n(男|女)\t', '10歳未満\t\\1性\t', f_all)
f_all = re.sub('\n10歳\n未満\n(男|女)\t', '10歳未満\t\\1性\t', f_all)
f_all = re.sub('\t(\d{4})の濃厚接触者', '\t岐阜県内\\1例目の濃厚接触者', f_all)
f_all = re.sub('\t(\d{4})の接触者', '\t岐阜県内\\1例目の接触者', f_all)
f_all = re.sub('\t(\d{4})等の濃厚接触者', '\t岐阜県内\\1例目等の濃厚接触者', f_all)
f_all = re.sub('\t(\d{4})等の接触者', '\t岐阜県内\\1例目等の接触者', f_all)
f_all = re.sub('市\t', '市\t\t', f_all)
f_all = re.sub('町\t', '町\t\t', f_all)
f_all = re.sub('県\t', '県\t\t', f_all)
f_all = re.sub('症例\n番号\n陽性\n判明\n日\n年代\t性別\t居住地\t発症日\t備考\n', '', f_all)
f_all = re.sub('症例\n番号\n陽性\n判明日\n年代\t性別\t居住地\t発症日\t備考\n', '', f_all)

lines = f_all.split('\n')

for line in lines:
    if line.find('令和') >= 0 or line.find('担当課') >= 0 or line.find('感染症') >= 0 or \
       line.find('第一係') >= 0 or line.find('居波') >= 0 or line.find('058-27') >= 0 or line.find('内線') >= 0:
        continue
    print(line)
