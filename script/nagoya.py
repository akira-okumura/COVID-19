#!/usr/bin/env python3

# format copied content from Acrobat

import sys
import re

print('本市公表\t年代\t性別\t居住地\t海外渡航歴\t発症日\t陽性確定日\t重症度\t特記事項')

lines = sys.stdin.readlines()[0].split('\r')

for line in lines:
    line = line.replace('\r', '').replace('\n', '')
    if line == '本市公表 年代 性別 居住地 海外渡航歴 発症日 陽性確定日 重症度 特記事項':
        continue
    elif line == '10歳':
        print(line, end='')
        continue
    elif line == '未満':
        print(line, end='\t')
        continue
    line = line.replace(' ', '\t')
    line = re.sub('\t(男|女)', '\t\\1\t', line)
    line = re.sub('(なし|軽症|中等症|重症)', '\t\\1\t', line)
    line = re.sub('愛知県公表(\d*)例目', '愛知県内\\1例目', line)
    line = re.sub('岐阜県公表(\d*)例目', '岐阜県内\\1例目', line)
    line = re.sub('本市公表(\d*)例目', '名古屋市発表\\1例目', line)
    line = re.sub('岡崎市公表(\d*)例目', '岡崎市発表\\1例目', line)
    line = re.sub('豊橋市公表(\d*)例目', '豊橋市発表\\1例目', line)
    line = re.sub('豊田市公表(\d*)例目', '豊田市発表\\1例目', line)
    line = re.sub('日(\d*)月', '日\t\\1月', line)
    line = re.sub('10歳未満\t(男|女)', '10歳未満\t\\1\t', line)
    line = re.sub('(男|女)名古屋市', '\\1\t名古屋市', line)

    if line in ('10歳未', '満'):
        print(line, end = '')
    elif line in ('10歳未', '満'):
        print(line, end = '')
    else:
        print(line)
