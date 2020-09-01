#!/usr/bin/env python3

# cd CTV
# mmdd=0807; ../script/merge.py Aichi_official_$mmdd.tsv Toyota_official_$mmdd.tsv Okazaki_official_$mmdd.tsv Toyohashi_official_$mmdd.tsv Nagoya_official_$mmdd.tsv > merged_$mmdd.tsv

import re

num_Aichi = -1

def tsv(fname):
    global num_Aichi
    try:
        f = open(fname)
    except:
        return ''

    text = ''

    for line in f.readlines():
        if line.find('症例番号') == 0 or line.find('本市公表') == 0:
            continue # skip header           

        try:
            num, age, sex, city, abroad, symp_date, pos_date, level, note = line[:-1].split('\t')
        except:
            import sys
            print(line, file=sys.stderr)
            raise

        if fname.find('Aichi') == 0 and num_Aichi == -1:
            num_Aichi = int(num)
        else:
            num_Aichi += 1
        
        pub_date = fname.split('_')[-1].split('.')[0]
        m, d = int(pub_date[:2]), int(pub_date[2:])
        
        text += '%d\t' % num_Aichi # No
        text += '%d月%d日\t' % (m, d) # 発表日

        sex = sex.replace('性', '')
        if age in ('10未満', '10歳未満'):
            text += '10歳未満%s性\t' % sex # 年代・性別
        else:
            age = int(age)
            text += '%d代%s性\t' % (age, sex) # 年代・性別

        text += '\t' # 国籍
        text += city + '\t' # 住居地
        note = re.sub('（.*?）', '', note) # drop e.g. '（20歳代男性・8月4日）'
        note = note.replace('例目及び', '例目、')
        note = note.replace('例目、', ',')
        note = re.sub('(例目の知人|例目の同僚|例目の家族|例目の濃厚接触者|例目の患者の濃厚接触者|例目患者の同居家族|例目の友人|例目と接触|例目患者の濃厚接触者|例目患者の同居者|例目が利用していた施設の利用者|例目の関連から検査|例目との関連から検査|例目の同居家族|例目が勤務していた医療機関の職員|例目が勤務していた施設の利用者|例目が勤務していた施設の職員|例目等の関連から検査|例目と同居|例目が勤務していた飲食店の利用者|例目が利用していた施設の職員|例目の接触者)', '', note)
        note = re.sub('名古屋市発表([,\d]*)。名古屋市発表(\d*)。?', '名古屋市発表\\1,\\2', note)
        text += note + '\t' # 接触状況
        if fname.find('Aichi') == 0:
            text += '本県発表%d\n' % int(num)
        elif fname.find('Toyota') == 0:
            text += '豊田市発表%d\n' % int(num)
        elif fname.find('Okazaki') == 0:
            text += '岡崎市発表%d\n' % int(num)
        elif fname.find('Toyohashi') == 0:
            text += '豊橋市発表%d\n' % int(num)
        elif fname.find('Nagoya') == 0:
            text += '名古屋市発表%d\n' % int(num)
        
    return text

def main(fnames):
    print('No\t発表日\t年代・性別\t国籍\t住居地\t接触状況\t備考\n', end='')
    for fname in fnames:
        print(tsv(fname), end='')

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
