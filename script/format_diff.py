#!/usr/bin/env python3

# format the difference (wdiff result) between Aichi_unofficial.tsv and the official PDF

import sys
import re

lines = sys.stdin.readlines()

for line in lines:
    line = line.replace('[-あり-]	{+陽性者と接触+}', '陽性者と接触')
    line = line.replace('名古屋市\t[-あり-]\t\t名古屋市発表', '名古屋市\t\t名古屋市発表')
    line = line.replace('[-知人が陽性者-]\t{+陽性者と接触+}', '知人が陽性者')
    line = line.replace('[-名古屋市事例の濃厚接触者-]	{+名古屋市事例と接触+}', '名古屋市事例の濃厚接触者')
    line = re.sub('名古屋市\t\[-あり-\]\t\{\+No.(\d+?)と接触\+\}\t名古屋市発表', '名古屋市\tNo.\\1と接触\t名古屋市発表', line)
    line = re.sub('\t\[-あり\t本県発表(\d+?)-\]\t\{\+No.(\d+?)と接触\t本県発表(\d+?)\+\}', '\tNo.\\2と接触\t本県発表\\1', line)
    line = re.sub('\t\t\[-本県発表(\d+?)-\]\t\{\+陽性者と接触\t本県発表(\d+?)\+\}', '\t陽性者と接触\t本県発表\\1', line)
    line = re.sub('\t\t\[-本県発表(\d+?)-\]\t\{\+No.(\d+?)と接触\t本県発表(\d+?)\+\}', '\tNo.\\2と接触\t本県発表\\1', line)
    line = re.sub('\t\t\[-本県発表(\d+?)-\]\t\t\{\+本県発表(\d+?)\+\}', '\t\t本県発表\\1', line)
    line = re.sub('\t\[-あり\t本県発表(\d+?)-\]\t\{\+(.+?)(都|道|府|県)事例と接触\t本県発表(\d+?)\+\}', '\t\\2\\3事例と接触\t本県発表\\1', line)
    line = re.sub('\t\[-あり-\]\t\{\+(.+?)(都|道|府|県)事例と接触\+\}\t名古屋市発表', '\t\\1\\2事例と接触\t名古屋市発表', line)
    line = re.sub('\t\[-一宮市発表(\d+?)-\]\t\{\+一宮市発表(\d+?)\+\}', '\t一宮市発表\\1', line)
    line = re.sub('\t\[-一宮市発表(\d+?)-\]\t\t\{\+一宮市発表(\d+?)\+\}', '\t一宮市発表\\1', line)
    line = re.sub('\t\[-No.(\d+?)と接触\t一宮市発表(\d+?)-\]\t\{\+No.\\1と接触一宮市発表(\d+?)\+\}', '\tNo.\\1と接触\t一宮市発表\\2', line)

    print(line, end='')
