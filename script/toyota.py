#!/usr/bin/env python3

# format copied content from HTML
# e.g. https://www.city.toyota.aichi.jp/pressrelease/1040515/1040817.html

import sys
import re

print('症例番号\t年代\t性別\t居住地\t海外渡航歴\t発症日\t陽性確定日\t症状等\t特記事項', end='')

lines = sys.stdin.readlines()

for line in lines:
    line = line.replace('\n', '')
    if line.find('職業：') == 0 or line.find('職業 ：') == 0 or line == '' or line.find('職業　　　：') == 0:
        continue

    line = re.sub('患者（(\d*)例目）概要', '\n\\1\t', line)
    line = re.sub('年齢、性別：(\d*)歳代　(.*)', '\\1\t\\2\t豊田市\t\t\t\t', line)
    line = re.sub('年齢、性別：(\d*)歳代 (.*)', '\\1\t\\2\t豊田市\t\t\t\t', line)
    line = re.sub('年代、性別：(\d*)歳代 (.*)', '\\1\t\\2\t豊田市\t\t\t\t', line)
    line = re.sub('年代、性別：(\d*)歳代　(.*)', '\\1\t\\2\t豊田市\t\t\t\t', line)
    line = re.sub('年齢、性別：10歳未満　(.*)', '10歳未満\t\\1\t豊田市\t\t\t\t', line)
    line = re.sub('年齢、性別：10歳未満 (.*)', '10歳未満\t\\1\t豊田市\t\t\t\t', line)
    line = re.sub('年代、性別：10歳未満　(.*)', '10歳未満\t\\1\t豊田市\t\t\t\t', line)

    line = re.sub('現在の症状：(.*)', '\\1\t', line)
    line = re.sub('本市(\d*)例目患者', '豊田市発表\\1例目', line)
    line = re.sub('愛知県発表(\d*)例目患者', '愛知県内\\1例目', line)
    line = re.sub('　*', '', line)
    line = re.sub('\t(軽症|中等症|重症)（(.*)）\t', '\t\\1\t', line)
    line = re.sub('経過等：', '', line)

    print(line, end='')
