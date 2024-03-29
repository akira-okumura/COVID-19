#!/usr/bin/env python3

# format copied content from PDF
# e.g. https://www.city.okazaki.lg.jp/1550/1562/1615/p025980_d/fil/20210109.pdf

import sys
import re

print('症例番号\t年代\t性別\t居住地\t海外渡航歴\t発症日\t陽性確定日\t症状等\t特記事項')

lines = sys.stdin.readlines()

for line in lines:
    if line.find('患者例		年代	性	発症日	採取日		現在の症状等	療養	備考') >= 0:
        continue

    line = re.sub(' ', '', line)
    line = line.replace('知人が陽性者と知り検査を実施	', '知人が陽性者')
    line = re.sub('\t\t', '\t', line)
    line = re.sub('\tー', '\t', line)
    line = re.sub('(\d+?)歳代', '\\1', line)
    line = line.replace('―	', '')
    line = line.replace('者	', '者')
    line = re.sub('(男|女)\t', '\\1\t豊橋市\t\t', line)
    line = re.sub('日\t(抗原|PCR)', '日', line)
    line = re.sub('(自宅|宿泊予定)\t', '', line)
    line = re.sub('\t(\d+?)例目', '\t豊橋市発表\\1例目', line)
    line = re.sub('\t愛知県発表(\d+?)例目', '\t愛知県内\\1例目', line)
    line = re.sub('\t愛知県(\d+?)例目', '\t愛知県内\\1例目', line)
    line = re.sub('知人が陽性と知り検査を実施', '知人が陽性者', line)
    line = line.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
    line = re.sub('なし\t－ (\d+?/\d+?)', '－\t\\1\tなし\t', line)

    print(line, end='')

