#!/usr/bin/env python3

# format copied content from PDF
# https://www.pref.gifu.lg.jp/uploaded/attachment/246391.pdf

import sys
import re

lines = sys.stdin.readlines()

for line in lines:
    line = line.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
    line = re.sub('海外渡航歴なし\n', '\t\t・海外渡航歴なし', line)
    line = re.sub('不特定多数との接触なし\n', '・不特定多数との接触なし', line)
    line = re.sub('(\d+?\/\d+?) 公表No.(\d+?) の関係者', '・No.\\2の関係者', line)
    line = re.sub('No.(\d+?) の関係者', 'No.\\1の関係者', line)
    line = re.sub(' ', '\t', line)

    print(line, end='')

