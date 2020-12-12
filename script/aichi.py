#!/usr/bin/env python3

# format copied content from Acrobat

import sys
import re

print('本市公表\t年代\t性別\t居住地\t海外渡航歴\t発症日\t陽性確定日\t重症度\t特記事項')

lines = sys.stdin.readlines()[0].split('\r')

for line in lines:
    if line == '症例番号年代性別居住地海外渡航歴発症日陽性確定日症状等特記事項':
        continue
    line = line.replace(' ', '\t')
    line = re.sub('\t(男|女)', '\t\\1\t', line)
    line = re.sub('(なし|軽症|中等症|重症)', '\t\\1\t', line)
    line = re.sub('県内(\d*)例目', '愛知県内\\1例目', line)
    line = re.sub('岐阜県(\d*)例目', '岐阜県内\\1例目', line)
    line = re.sub('日(\d*)月', '日\t\\1月', line)
    line = re.sub('10未満(男|女)', '10未満\t\\1\t', line)

    print(line)
