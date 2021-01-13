#!/usr/bin/env python3

# format copied content from PDF
# e.g. https://www.city.okazaki.lg.jp/1550/1562/1615/p025980_d/fil/20210109.pdf

import sys
import re

print('症例番号\t年代\t性別\t居住地\t海外渡航歴\t発症日\t陽性確定日\t症状等\t特記事項')

f_all = sys.stdin.read().replace('\r', '\n')

for word in ('患者例', '(市内在住例)', '年代性別職業症状等発症日判明日備考'):
    f_all = f_all.replace(word + '\n', '')

f_all = re.sub('(\d+)\n（\d+）\n', '\\1\t', f_all)
f_all = re.sub('\n歳代\n([男女])', '\t\\1\t岡崎市\t\t', f_all)
f_all = re.sub('(軽症|中等症|重症)', '\t\\1\t', f_all)
f_all = re.sub('無症状', '\tなし\t', f_all)

lines = f_all.split('\n')

for line in lines:
    line = re.sub('(なし|軽症|中等症|重症)\t(\d+/\d+) (\d+/\d+)', '\\2\t\\3\t\\1\t', line)
    line = re.sub('なし\t－ (\d+/\d+)', '－\t\\1\tなし\t', line)
    print(line)

