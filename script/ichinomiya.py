#!/usr/bin/env python3

# format copied content from HTML
# https://www.city.ichinomiya.aichi.jp/covid19/1033846/1040165.html

import sys
import re

print('患者例\t年代\t性別\t居住地\t海外渡航歴\t発症日\t採取日\t現在の症状\t備考')

lines = sys.stdin.readlines()

for line in lines:
    line = re.sub('(\d+?)例目\t', '\\1\t', line)
    line = re.sub('(\d+?)歳代', '\\1', line)
    line = re.sub('(男|女)性\t\n', '\\1\t一宮市\t\t', line)
    line = re.sub('(男|女)性\t', '\\1\t一宮市\t\t', line)
    line = re.sub('(抗原|PCR)\n', '', line)
    line = re.sub('(\d+?)月(\d+?)日\t\n', '\\1月\\2日\t', line)
    line = re.sub('(\d+?)月(\d+?)日\n', '\\1月\\2日\t', line)
    line = re.sub('\t(\d+?)例目', '\t一宮市発表\\1例目', line)
    line = re.sub('\t市(\d+?)例目', '\t一宮市発表\\1例目', line)
    line = re.sub('^市(\d+?)例目', '\t一宮市発表\\1例目', line)
    line = re.sub('^(\d+?)例目', '\t一宮市発表\\1例目', line)
    line = re.sub('\t県(\d+?)例目（.+）', '\t愛知県内\\1例目', line)
    line = re.sub('日\n(\d+)月', '日\t\\1月', line)
    line = line.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
    line = re.sub('例目\n', '\t', line)
    line = re.sub('\t ', '\t', line)
    line = line.replace('軽症\n', '軽症\t')

    if line != ' \n':
        print(line, end='')

