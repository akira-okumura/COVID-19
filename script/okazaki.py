#!/usr/bin/env python3

# format copied content from HTML
# e.g. https://www.city.okazaki.lg.jp/1550/1562/1615/p027826.html

import sys
import re

print('症例番号\t年代\t性別\t居住地\t海外渡航歴\t発症日\t陽性確定日\t症状等\t特記事項', end='')

lines = sys.stdin.readlines()

for line in lines:
    line = line.replace('\n', '').replace('≪在住', '≪市内在住') # fix mistakes
    if line in ('⑴ 概要', '⑵ 経緯', '　　※ 感染症指定医療機関等への入院を調整中です。', '※ 感染症指定医療機関等への入院を調整中です。', '※ 患者に対し積極的疫学調査を実施し、濃厚接触者についてはPCR検査を実施するとともに、自宅待機を要請し健康観察を実施しています。', '※ 患者の行動歴および濃厚接触者について調査中です。', ''):
        continue
    elif line.find('職業：') >= 0:
        continue

    line = re.sub('患者（岡崎市(\d*)例目≪市内在住\d*例目≫）について', '\n\\1\t', line)
    line = re.sub('[　*]年代：(\d*)歳代', '\\1\t', line)
    line = re.sub('[　*]年代：10歳未満', '10歳未満\t', line)
    line = re.sub('[　*]性別：(.*)', '\\1\t岡崎市\t\t', line)
    line = re.sub('[　*]現在の主な症状：(.*)', '\\1\t', line)
    line = re.sub('本市発表の新型コロナウイルス感染症患者（(\d*)例目≪市内在住\d*例目≫）', '岡崎市発表\\1例目', line)

    print(line, end='')