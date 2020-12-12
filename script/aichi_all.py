#!/usr/bin/env python3

# format copied content from Acrobat
# applicable to "愛知県内の発生事例12月" or similar

import sys
import re

print('No\t発表日\t年代・性別\t国籍\t住居地\t接触状況\t備考')

lines = sys.stdin.readlines()[0].split('\r')

for line in lines:
    if line == 'No 発表日年代・性別国籍住居地接触状況備考':
        continue
    line = line.replace(' ', '\t')
    line = re.sub('(\d*)月(\d*)日', '\\1月\\2日\t', line)
    line = re.sub('(男|女)性(.+?)(村|町|市)', '\\1性\t\t\\2\\3\t', line) # ignore 国籍
    line = re.sub('本県発表', '\t本県発表', line)
    line = re.sub('名古屋市発表', '\t名古屋市発表', line)
    line = re.sub('岡崎市発表', '\t岡崎市発表', line)
    line = re.sub('豊田市発表', '\t豊田市発表', line)
    line = re.sub('豊橋市発表', '\t豊橋市発表', line)
    line = line.replace('瀬⼾', '瀬戸').replace('⻑久⼿', '長久手').replace('⻄尾', '西尾').replace('愛⻄', '愛西')

    print(line)
