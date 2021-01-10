#!/usr/bin/env python3

# format the difference (wdiff result) between Aichi_unofficial.tsv and the official PDF

import sys
import re

lines = sys.stdin.readlines()

for line in lines:
    line = line.replace('名古屋市\t[-あり-]\t\t名古屋市発表', '名古屋市\t\t名古屋市発表')
    line = re.sub('名古屋市\t\[-あり-\]\t\{\+No.(\d+?)と接触\+\}\t名古屋市発表', '名古屋市\tNo.\\1と接触\t名古屋市発表', line)
    line = re.sub('\t\[-あり\t本県発表(\d+?)-\]\t\{\+No.(\d+?)と接触\t本県発表(\d+?)\+\}', '\tNo.\\2と接触\t本県発表\\1', line)
    line = re.sub('\t\t\[-本県発表(\d+?)-\]\t\t\{\+本県発表(\d+?)\+\}', '\t\t本県発表\\1', line)
    line = re.sub('\t\[-あり\t本県発表(\d+?)-\]\t\{\+(.+?)(都|道|府|県)事例と接触\t本県発表(\d+?)\+\}', '\t\\2\\3事例と接触\t本県発表\\1', line)
    line = re.sub('\t\[-あり-\]\t\{\+(.+?)(都|道|府|県)事例と接触\+\}\t名古屋市発表', '\t\\1\\2事例と接触\t名古屋市発表', line)

    print(line, end='')
