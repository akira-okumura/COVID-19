#!/usr/bin/env python3

# format copied content from PDF
# e.g. https://www.city.gifu.lg.jp/secure/44927/2021.01.27%20syousai_s.pdf

import sys
import re

f_all = sys.stdin.read().replace('\r', '\n')

f_all = re.sub('(\d+)\n\((\d+)\)\n', '\\2例目\t', f_all)
f_all = f_all.replace(' ', '\t')
f_all = re.sub('\t([1-9]0)\t', '\t\\1代\t', f_all)
f_all = re.sub('市(\d+)\(県(\d+)\)', '岐阜県内\\2例目', f_all)
f_all = f_all.replace('岐阜市\n', '岐阜市\t')
f_all = re.sub('県(\d+)\tの', '岐阜県内\\1例目の', f_all)
f_all = re.sub('県(\d+)\t等の', '岐阜県内\\1例目等の', f_all)

lines = f_all.split('\n')

print(f_all)
