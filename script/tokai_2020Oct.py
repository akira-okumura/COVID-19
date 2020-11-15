import graphviz
import datetime
import json
from urllib import request
import re

cases = {}

def readTSV(pref):
    if pref == 'aichi':
        text = open('CTV/Aichi.tsv').readlines()
        lines = open('CTV/Aichi_unofficial.tsv').readlines()[1:]
        lines.reverse()
        modified_text = ''
        for line in lines:
            try:
                n, date, person, notionality, city, note, another_index = line[:-1].split('\t')
            except:
                print(line)
                raise
            n = int(n)
            if n < 1613:
                continue

            # inpefect. needs to be cleaned up.
            if person.find('10歳未満') >= 0:
                sex = person.split('10歳未満')[1]
                age = '10歳未満'
            elif person.find('調査中') == 0:
                sex = '調査中'
                age = person.split('・')[0]
            elif person.find('調査中') > 0:
                sex = person.split('・')[1]
                age = '調査中'
            else:
                age, sex = person.split('代')

            if note.find('No.') >= 0 and note.find('と接触') >= 0:
                tmp = re.findall('No\.[,\d]*と接触', note)[0]
                note = note.replace(tmp, tmp.replace('No.', '愛知県内').replace(',', '例目、').replace('と接触', '例目と接触'))
            elif note == '':
                note = ' '

            if note.find('岐阜県発表') >= 0:
                tmp = re.findall('岐阜県発表[,\d]*', note)[0]
                note = note.replace(tmp, tmp.replace('岐阜県発表', '岐阜県内').replace(',', '例目、') + '例目と接触')

            if age == '10歳未満':
                modified_text += '%d例目\t%s\t%s在住の%s（%s）\t%s\n****' % (n, date, city, sex, age, note)
            elif age == '調査中':
                modified_text += '%d例目\t%s\t%s在住の%s（%s）\t%s\n****' % (n, date, city, sex, age, note)
            else:
                modified_text += '%d例目\t%s\t%s在住の%s（%s代）\t%s\n****' % (n, date, city, sex, age, note)
        text = modified_text.split('****')[:-1] + text

        return text
    elif pref == 'gifu':
        text = open('CTV/Gifu.tsv').readlines()
        lines = open('CTV/Gifu_official.tsv').readlines()[1:]
        lines.reverse()
        modified_text = ''
        for line in lines:
            try:
                pub_date, n, pos_date, age, sex, city, abroad, symp_date, note = line[:-1].split('\t')
            except:
                print(line)
                raise

            if note == '':
                note = ' '

            modified_text += '%s\t%s\t%s在住の%s（%s）\t%s\n****' % (n, pub_date, city, sex, age, note)

        text = modified_text.split('****')[:-1] + text

        return text

def register_cases(pref, label_mode=0):
    lines = readTSV(pref)
    lines.reverse()

    for line in lines:
        idx, date, description, note = line[:-1].split('\t')
        idx = int(idx.replace('例目', '')) # drop '例目’

        m, d = map(int, date.replace('月', '-').replace('日', '').split('-'))
        date = datetime.date.fromisoformat('2020-%02d-%02d' % (m, d))

        try:
            age = description.split('（')[-1].split('）')[0].replace('代', '')
            if age == '10歳未満':
                age = 9
            elif age == '1歳未満':
                age = 0
            elif age == '調査中':
                pass
            else:
                age = int(description.split('（')[-1].split('）')[0].replace('代', ''))
        except:
            age = None

        try:
            city = description.split('在住')[0]
        except:
            city = ''

        #note = note[:-2] # commented out on April 21
        node_name = '%s%d' % (pref, idx)

        source_idx = []
        if note.find('愛知県内') >= 0: # cluster
            for split_txt in note.split('愛知県内')[1:]:
                sources = split_txt.split('県内')[0].split('例目')
                for source in sources:
                    try:
                        n = int(source.replace('・', '、').split('、')[-1].translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})))
                    except:
                        pass
                    else:
                        source_idx.append('aichi%d' % n)

        if note.find('岐阜県内') >= 0: # cluster
            sources = note.split('岐阜県内')[1].split('県内')[0].split('例目')
            for source in sources:
                try:
                    n = int(source.split('、')[-1])
                except:
                    pass
                else:
                    source_idx.append('gifu%d' % n)

        if note == '11月6日岐阜県公表のクラスターの関連から検査':
            source_idx.append('gifu708') 
        elif note.find('11月6日の集団感染が発生した市内事業所の') >= 0:
            source_idx.append('aichi6365') 
        elif note.find('PUB「EDEN」関係の患者の濃厚接触者') >= 0:
            source_idx.append('aichi6111') 

        cases['%s%d' % (pref, idx)] = {'node_name':node_name, 'date':date, 'note':note,
                                       'source_idx':source_idx, 'age':age, 'city':city,
                                       'description':description, 'linked':False}

def register_sources():
    for case in cases.values():
        for source_idx in case['source_idx']:
            cases[source_idx]['linked'] = True


def make_date_ranks():
    date_ranks = {}
    for case in sorted(cases.values(), key=lambda x:x['date']):
        date = case['date']
        if before_2020Oct(case['date']):
            continue
        if date not in date_ranks.keys():
            date_ranks[date] = [case,]
        else:
            date_ranks[date].append(case)

    return date_ranks

def before_2020Oct(date):
    return str(date)[:-3] in ('2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06', '2020-07', '2020-08', '2020-09')

def register_dummy_cases():
    for case in sorted(cases.values(), key=lambda x:x['date']):
        date = case['date']
        if before_2020Oct(date):
            continue
        node_name = 'dummy%s' % str(date)
        cases[node_name] = {'node_name':node_name, 'date':date, 'note':'',
                            'source_idx':[],
                            'description':'', 'linked':False}

def make_date_nodes(date_ranks, label_mode):
    date_nodes = []
    for date in date_ranks.keys():
        if before_2020Oct(date):
            continue
        if str(date) == '2020-10-01':
            with graph.subgraph() as s:
                s.attr('node', fixedsize='1', width='2', fontsize='18')
                s.node('date', label='陽性発表日', shape='plaintext', fontsize='18')
                s.node('NB', label='　' * 47 + '※1 陽性確定日の順に並べているため、各クラスターの先頭が感染源であったことを必ずしも意味しません。\n' \
                       + '　' * 42 + '※2 間違いが混入している可能性がありますので、一次情報は自治体の発表をあたってください。\n' \
                       + '　' * 32 + '※3 愛知県の合計感染者数は延べ人数です。再陽性となった人を含みます。\n' \
                       + '　' * 16 + '※4 印刷・再配布などご自由にどうぞ。', shape='plaintext', fontsize='24', labeljust='l', height='1.4')
                s.node('author', label='　' * 30 + 'データ出典：https://www.ctv.co.jp/covid-19/ および自治体公開データ\n' + '　' * 28 + '作成：@AkiraOkumura（名古屋大学 宇宙地球環境研究所 奥村曉）', shape='plaintext', fontsize='24', height='1.2')
                #response = request.urlopen('https://www.ctv.co.jp/covid-19/person.txt')
                response = request.urlopen('https://www.ctv.co.jp/covid-19/person2.txt') # new file since Apr 21
                json_data = json.loads(response.read())[0]
                update = json_data['update']
                json_data = json_data['pref3']
                for i in range(len(json_data) - 1, -1, -1):
                    deaths = int(json_data[i]['content2'])
                    total = int(json_data[i]['content'])
                    if json_data[i]['class'] == 'aichi':
                        s.node('total_aichi', label='' + '　' * 16 + ('愛知 合計感染者数：%3d　合計死者数：%2d' % (total, deaths)), shape='plaintext', fontsize='30', height='0.5')
                    elif json_data[i]['class'] == 'gifu':
                        s.node('total_gifu', label='' + '　' * 16 + ('岐阜 合計感染者数：%3d　合計死者数：%3d' % (total, deaths)), shape='plaintext', fontsize='30', height='0.5')

                #m, d = map(int, [x for x in cases.keys() if cases[x]['node_name'].find('dummy') == 0][-1].split('-')[1:])
                #today = '%d/%d %s' % (m, d, t)
                m, d, t = update.replace('月', ' ').replace('日', '').split(' ')
                today = '%s/%s %s' % (m, d, t)
                s.node('title', label='　' * 20 + '新型コロナウイルス感染経路図（%s 現在）' % today, shape='plaintext', fontsize='40')

                s.node('border', label='\n愛知県↑\n岐阜県↓', shape='plaintext', height='8', fontsize='40')
                s.node('arrow_exp', label='\n接触経路', shape='plaintext', fontcolor='black', height='2')
                s.node('arrows', label='\n\n←→', shape='plaintext', fontcolor='black')
                s.node('nosex', label='紫：性別不明', shape='plaintext', fontcolor='purple')
                s.node('male', label='青：男性　　', shape='plaintext', fontcolor='blue')
                s.node('female', label='赤：女性　　', shape='plaintext', fontcolor='red')
                s.node('blank10', style='invis')
                s.node('cap2', label='帰国者 or 外国籍', shape='circle')
                s.node('cap3', label='感染経路不明', style='filled', shape='circle', color='#000000AA', fontcolor='white')
                s.node('cap4', label='接触者\n※リンク非表示\nは他県との接触', shape='square')
                s.node('cap5', label='県外滞在者\n感染経路不明', shape='tripleoctagon', height='2', style='filled', color='#000000AA', fontcolor='white')
                s.node('cap6', label='県外陽性者\nとの接触者', shape='tripleoctagon', height='2')
                s.node('cap7', label='図の読み方', shape='plaintext')

        with graph.subgraph() as s:
            s.attr(rank='same')
            # default not to be seen
            s.attr('node', fixedsize='1', width='0.5')
            m, d = map(int, str(date).split('-')[1:])
            if (m, d) == (1, 26) or (m, d) == (2, 14) or d == 1:
                label = '%d/%d' % (m, d)
            elif (m, d) == (1, 29):
                label = '……'
            else:
                label = '%d' % d
            if d == 1:
                s.node('date%s' % date, label=label, shape='plaintext', fontsize='24')
            else:
                s.node('date%s' % date, label=label, shape='plaintext', fontsize='20')
            date_nodes.append('date%s' % date)

            tmp1 = sorted([x for x in date_ranks[date] if x['node_name'].find('aichi') >= 0], key=lambda x:x['linked'], reverse=True)
            tmp2 = [x for x in date_ranks[date] if x['node_name'].find('dummy') >= 0]
            tmp3 = sorted([x for x in date_ranks[date] if x['node_name'].find('gifu') >= 0], key=lambda x:x['linked'], reverse=False)
            date_ranks[date] = tmp1 + tmp2 + tmp3
            #date_ranks[date] = sorted(date_ranks[date], key=lambda x:x['linked'], reverse=True)

            for case in date_ranks[date]:
                s.attr('node', shape='octagon', color='black', style='diagonals', fontcolor='black')
                if case['description'].find('男性') >= 0:
                    color = '#0000ff' # blue
                elif case['description'].find('女性') >= 0:
                    color = '#ff0000' # red
                elif case['description'].find('名古屋市在住の方（性別・年代非公表）') >= 0 or case['description'] == '' or case['description'].find('調査中（') >= 0 :
                    color = '#ff00ff' # purple
                else:
                    color='#000000' # black

                if case['note'].find('帰国') >= 0 or \
                   case['description'].find('中国籍') >= 0 or \
                   case['description'].find('帰国') >= 0 or \
                   case['description'].find('10月17日にイタリアから入国') >= 0 or \
                   (case['note'].find('渡航歴') >= 0 and case['note'].find('家族がパキスタン渡航歴あり') < 0):
                    s.attr('node', shape='circle', style='', color=color, fontcolor='black')
                elif case['note'].find('感染経路不明') >= 0 or case['node_name'] in ('gifu79', 'aichi662', 'aichi661'):
                    s.attr('node', shape='circle', style='filled', color=color+'AA', fontcolor='white')
                elif case['note'].find('新宿区の劇場利用') >= 0 or \
                     case['note'].find('新宿区内の劇場を利用') >= 0 or \
                     case['note'].find('さいたま市発表の陽性患者の家族') >= 0 or \
                     case['note'].find('さいたま市発表の陽性患者との接触を確認') >= 0 or \
                     case['note'].find('東京都発表の陽性患者との接触を確認') >= 0 or \
                     case['note'].find('神奈川県発表の陽性患者の同僚') >= 0 or \
                     case['note'].find('東京都発表の陽性患者の濃厚接触者') >= 0 or \
                     case['note'].find('京都市発表の陽性患者と接触') >= 0 or \
                     case['note'].find('滋賀県発表の陽性患者の濃厚接触者') >= 0 or \
                     case['note'].find('石川県発表の陽性患者の濃厚接触者') >= 0 or \
                     case['note'].find('東京都事例と接触') >= 0 or \
                     case['note'].find('浜松市事例と接触') >= 0 or \
                     case['note'].find('富山県事例と接触') >= 0 or \
                     case['note'].find('三重県事例と接触') >= 0 or \
                     case['note'].find('東京都事例の家族') >= 0 or \
                     case['note'].find('大阪府事例と接触') >= 0 or \
                     case['note'].find('三重県公表231') >= 0 or \
                     case['note'].find('神奈川県9100') >= 0 or \
                     case['note'].find('静岡県熱海市のクラスターが発生したカラオケを伴う飲食店を利用') >= 0 or \
                     case['note'].find('四日市市陽性患者の接触者') >= 0 or \
                     case['note'].find('三重県陽性患者の接触者') >= 0 or \
                     case['note'].find('浜松市患者の濃厚接触者') >= 0 or \
                     case['note'].find('石川県事例と接触') >= 0 or \
                     case['note'].find('大阪府事例の知人') >= 0 or \
                     case['note'].find('東京都事例の知人') >= 0 or \
                     case['note'].find('神奈川県事例の知人') >= 0 or \
                     case['note'].find('高知県発表86') >= 0 or \
                     case['note'].find('沖縄県発表1557') >= 0 or \
                     case['note'].find('東京都の陽性患者と接触') >= 0 or \
                     case['note'].find('東京都陽性患者の接触者') >= 0 or \
                     case['note'].find('東京都陽性患者の濃厚接触者') >= 0 or \
                     case['note'].find('大阪府事例の家族') >= 0 or \
                     case['note'].find('大阪府発表11853') >= 0 or \
                     case['note'].find('大阪府7256') >= 0 or \
                     case['note'].find('大阪府7421') >= 0 or \
                     case['note'].find('兵庫県1927') >= 0 or \
                     case['note'].find('神戸市744') >= 0 or \
                     case['note'].find('滋賀県発表505') >= 0 or \
                     case['note'].find('兵庫県公表2531') >= 0 or \
                     case['note'].find('三重県内443例目の知人') >= 0 or \
                     case['note'].find('神奈川県患者と接触') >= 0 or \
                     case['note'].find('大分市発表79例目の濃厚接触') >= 0 or \
                     case['note'].find('川崎市陽性患者の濃厚接触者（友人）') >= 0 or \
                     case['note'].find('大阪府陽性患者の濃厚接触者（友人）') >= 0 or \
                     case['note'].find('東京都にて埼玉県の陽性患者と接触') >= 0 or \
                     case['note'].find('東京都にて感染が確認された新型コロナウイルス感染症患者の濃厚接触者') >= 0 or \
                     case['note'].find('滋賀県内468例目') >= 0 or \
                     case['note'].find('東京都陽性患者と接触') >= 0 or \
                     case['note'].find('滞在中に大阪府陽性患者と接触') >= 0 or \
                     case['note'].find('大阪府発表11596') >= 0 or\
                     case['note'].find('北海道3424') >= 0 or\
                     case['note'].find('大阪府13123') >= 0 or\
                     case['note'].find('宮城県861') >= 0 or\
                     case['note'].find('鹿児島県533') >= 0 or\
                     case['note'].find('鹿児島県480') >= 0 or\
                     case['note'].find('神奈川県7779') >= 0 or\
                     case['note'].find('京都市公表1323') >= 0 or\
                     case['note'].find('福岡県5230') >= 0 or\
                     case['note'].find('滋賀県陽性患者の濃厚接触者') >= 0 or\
                     case['note'].find('北海道公表3964') >= 0 or\
                     case['node_name'] in ('aichi1220', 'aichi1414'):
                    s.attr('node', shape='tripleoctagon', style='', color=color, fontcolor='black')
                elif case['node_name'] not in ('aichi1402', 'aichi1435', 'aichi1722', 'aichi3768', 'aichi3775') and \
                     (case['note'].find('例目') >= 0 or \
                      case['note'].find('名古屋市陽性者の濃厚接触者（同じ職場）') >= 0 or \
                      case['note'].find('11月6日岐阜県公表のクラスターの関連から検査') >= 0 or \
                      case['note'].find('11月6日岐阜県内のクラスターの関連から検査') >= 0 or \
                      case['note'].find('PUB「EDEN」関係の患者の濃厚接触者') >= 0 or \
                      case['note'].find('11月6日の集団感染が発生した市内事業所の') >= 0 or \
                      case['note'].find('岐阜県で集団感染が発生した合唱団に所属') >= 0 or \
                      case['note'].find('※集団感染が発生した合唱団に参加') >= 0 or \
                      case['note'].find('大阪市内のライブハウスの利用者') >= 0 or \
                      case['note'].find('岐阜市内の肉料理店（潜龍）') >= 0 or \
                      case['note'].find('スポーツジムの利用者') >= 0 or \
                      case['note'].find('※高齢者施設の送迎ドライバーとして勤務') >= 0 or \
                      case['note'].find('※死亡後に感染を確認<br>※名古屋市緑区のデイサービスを利用') >= 0 or \
                      case['note'].find('※3月5日に感染確認。3月24日に検査で陰性だったため退院。4月2日に陽性と再度確認') >= 0 or \
                      case['note'].find('※4月2日に愛知県の陽性患者と接触') >= 0 or \
                      case['note'].find('※愛知県陽性患者の濃厚接触者') >= 0 or \
                      case['note'].find('※愛知県発表の陽性患者の濃厚接触者') >= 0 or \
                      case['note'].find('※名古屋市緑区のデイサービスを利用') >= 0 or \
                      case['note'].find('愛知県内1642例目と同一患者') >= 0 or \
                      case['note'].find('愛知県内1484例目と同一患者') >= 0 or \
                      case['note'].find('再度') >= 0 or \
                      case['note'].find('愛知県陽性患者の接触者') >= 0 or \
                      case['note'].find('愛知県陽性者の濃厚接触者') >= 0 or \
                      case['note'].find('後日感染判明者と接触') >= 0 or \
                      case['note'].find('名古屋市事例と接触') >= 0 or \
                      case['note'].find('愛知県内陽性者と接触') >= 0 or \
                      case['note'].find('愛知県患者の濃厚接触') >= 0 or \
                      case['note'].find('名古屋市陽性患者の濃厚接触者') >= 0 or \
                      case['note'].find('名古屋市陽性患者の接触者') >= 0 or \
                      case['note'].find('愛知県患者の濃厚接触者') >= 0 or \
                      case['note'].find('愛知県陽性患者の濃厚接触者') >= 0 or \
                      case['note'].find('愛知県陽性者の接触者') >= 0 or \
                      case['node_name'] == 'gifu151' or \
                      case['node_name'] == 'aichi521' or \
                      case['node_name'] in ('gifu210', 'gifu211', 'gifu215', 'gifu216')): # 7/24 Gifu cases not reflected in CTV data
                    s.attr('node', shape='square', style='', color=color, fontcolor='black')
                elif case['node_name'] in ('aichi547') or \
                     case['note'].find('滞在') >= 0 or case['note'].find('東京都から名古屋市へ移動') >= 0 or \
                     case['note'].find('8月13日～16日に大阪府に滞在') >= 0 or\
                     case['note'].find('9月25日まで神奈川県居住') >= 0 or\
                     case['note'].find('7月30日～8月10日に青森県、岩手県、宮城県、福島県、秋田県に滞在') >= 0 or\
                     case['note'].find('8月18日まで静岡県に在住') >= 0 or\
                     case['note'].find('9月12日から名古屋市に滞在') >= 0 or\
                     (case['note'].find('6月15~16日神奈川県、6月19~21日東京を訪問') >= 0 or 
                      case['node_name'] in ('aichi918', 'aichi925', 'aichi939') or # 7/24 Nagoya cases not reflected in CTV data
                      case['node_name'] in ('aichi998',)): # 7/25 Nagoya cases not reflected in CTV data '7/9〜7/10に大阪府滞在'
                    s.attr('node', shape='tripleoctagon', style='filled', color=color+'AA', fontcolor='white')
                elif case['node_name'].find('dummy2') == 0:
                    pass
                else:
                    # probably OK to be categorized into '感染経路不明'
                    s.attr('node', shape='circle', style='filled', color=color+'AA', fontcolor='white')
                    print(case['node_name'], case['description'], case['note'])
                    #s.attr('node', shape='square', style='diagonals', color=color)

                if case['node_name'].find('dummy') == 0:
                    s.node(case['node_name'], label='', style='invis', width='0', height='3', shape='box')
                else:
                    if label_mode == 0: # case number
                        s.node(case['node_name'], label=case['node_name'].replace('aichi', 'A').replace('gifu', 'G'), fontname='Myriad Pro')
                    elif label_mode == 1: # age
                        if case['age'] == None:
                            label = ''
                        elif case['age'] == 0:
                            label = '0歳'
                        elif case['age'] == 9:
                            label = '<10歳'
                        elif case['age'] == '調査中':
                            label = '調査中'
                        else:
                            label = '%d代' % case['age']

                        if case['city'][-1] == '市':
                            label += '\n' + case['city'][:-1]
                        else:
                            label += '\n' + case['city']
                        s.node(case['node_name'], label=label, fontname='Myriad Pro')

    graph.edge('date', date_nodes[0], style='invis')
    graph.edge('border', 'dummy2020-10-01', style='invis')

    return date_nodes

def link_date_nodes():
    for i in range(len(date_nodes) - 1):
        graph.edge(date_nodes[i], date_nodes[i + 1], style='invis')

def link_dummy_nodes():
    dummy_cases = [y for y in sorted(cases.values(), key=lambda x:x['node_name']) if y['node_name'].find('dummy') == 0]
    for i in range(len(dummy_cases) - 1):
        graph.edge(dummy_cases[i]['node_name'], dummy_cases[i + 1]['node_name'], style='dashed', color='black', dir='')
    gifu_cases = [y for y in sorted(cases.values(), key=lambda x:x['node_name']) if y['node_name'].find('gifu') == 0]
    for i in range(len(gifu_cases)):
        case = gifu_cases[i]
        if before_2020Oct(case['date']):
            continue
        dummy_case = cases['dummy%s' % str(case['date'])]
        if case['node_name'] not in ('gifu5') or \
           case['node_name'] not in ('gifu9', 'gifu10', 'gifu11') or \
           case['node_name'] not in ('gifu16') or \
           case['node_name'] not in ('gifu23', 'gifu24', 'gifu25', 'gifu26') or \
           case['node_name'] not in ('gifu27', 'gifu28', 'gifu29', 'gifu30', 'gifu31') or \
           case['node_name'] not in ('gifu48', 'gifu52', 'gifu54', 'gifu55', 'gifu56', 'gifu57', 'gifu58'):
            graph.edge(dummy_case['node_name'], case['node_name'], style='invis')

#debug = True
debug = False

for label_mode in range(1 if debug else 2):
    fname = 'PDF/Tokai_mode%d' % label_mode
    graph = graphviz.Graph(engine='dot', filename=fname)
    graph.attr('node', fontname='Hiragino UD Sans F StdN', fontsize='14')
    graph.attr('edge', arrowhead='vee', arrowsize='0.5', dir='both')
    graph.attr(nodesep='0.1', ranksep='0.12')

    register_cases('gifu', label_mode)
    register_cases('aichi', label_mode)
    register_dummy_cases()
    register_sources()

    date_ranks = make_date_ranks()
    date_nodes = make_date_nodes(date_ranks, label_mode=label_mode)

    for case in cases.values():
        if before_2020Oct(case['date']):
            continue
        if len(case['source_idx']) > 0:
            source_idx = case['source_idx']
            node_name = case['node_name']
            for source in source_idx:
                source_name = cases[source]['node_name']
                if before_2020Oct(cases[source]['date']):
                    continue
                if source_name in ('gifu708', 'gifu711') :
                    color='deeppink'
                else:
                    color='black'
                graph.edge(source_name, node_name, color=color)

    link_date_nodes()
    link_dummy_nodes()

    if debug:
        dummy_edge = lambda a, b : graph.edge(a, b, color='red')#, style='invis') # for debugging
    else:
        dummy_edge = lambda a, b : graph.edge(a, b, style='invis')
    dummy_edges = lambda a : [dummy_edge(a[i], a[i + 1]) for i in range(len(a) - 1)]

    dummy_edges(('aichi5376', 'aichi5384', 'aichi5385'))
    dummy_edge('aichi5398', 'aichi5427')
    dummy_edge('aichi5397', 'aichi5415')
    dummy_edge('aichi5433', 'aichi5450')
    dummy_edge('aichi5397', 'aichi5453')
    dummy_edge('aichi5432', 'aichi5455')
    dummy_edge('aichi5440', 'aichi5463')
    dummy_edge('aichi5464', 'aichi5533')
    dummy_edge('aichi5522', 'aichi5548')
    dummy_edge('aichi5549', 'aichi5552')
    dummy_edge('aichi5554', 'aichi5595')
    dummy_edge('aichi5619', 'aichi5638')
    dummy_edge('aichi5618', 'aichi5670')
    dummy_edge('aichi5635', 'aichi5687')
    dummy_edge('aichi5620', 'aichi5695')
    dummy_edge('aichi5653', 'aichi5706')
    dummy_edge('aichi5657', 'aichi5709')
    dummy_edge('aichi5570', 'aichi5667')
    dummy_edge('aichi5655', 'aichi5743')
    dummy_edge('aichi5700', 'aichi5754')
    dummy_edge('aichi5703', 'aichi5758')
    dummy_edge('aichi5574', 'aichi5750')
    dummy_edge('aichi5631', 'aichi5735')
    dummy_edge('aichi5816', 'aichi5825')
    dummy_edge('aichi5796', 'aichi5858')
    dummy_edge('aichi5795', 'aichi5859')
    dummy_edge('aichi5848', 'aichi5874')
    dummy_edge('aichi5870', 'aichi5922')
    dummy_edge('aichi5770', 'aichi5803')
    dummy_edge('aichi5728', 'aichi5806')
    dummy_edge('aichi5739', 'aichi5810')
    dummy_edge('aichi5765', 'aichi5915')
    dummy_edge('aichi5736', 'aichi5880')
    dummy_edge('aichi5609', 'aichi5669')
    dummy_edge('aichi5578', 'aichi5621')
    dummy_edge('aichi5617', 'aichi5642')
    dummy_edge('aichi5590', 'aichi5643')
    dummy_edge('aichi5705', 'aichi5723')
    dummy_edge('aichi5710', 'aichi5717')
    dummy_edge('aichi5565', 'aichi5594')
    dummy_edge('aichi5482', 'aichi5530')
    dummy_edge('aichi5538', 'aichi5582')
    dummy_edge('aichi5542', 'aichi5582')
    dummy_edge('aichi5535', 'aichi5565')
        
    dummy_edges(('aichi6107', 'aichi6136', 'dummy2020-10-30'))
    dummy_edges(('aichi6629', 'aichi6627', 'aichi6591', 'aichi6626'))

    dummy_edge('aichi5439', 'aichi5503')
    dummy_edge('aichi5457', 'aichi5490')
    dummy_edge('aichi6626', 'dummy2020-11-06')

    dummy_edges(('dummy2020-11-03', 'gifu694', 'gifu698', 'gifu696', 'gifu697'))

    dummy_edges(('gifu646', 'gifu645', 'gifu647'))
    dummy_edges(('gifu646', 'gifu645', 'gifu647'))
    dummy_edge('gifu651', 'gifu648')
    dummy_edge('gifu647', 'gifu648')
    dummy_edge('gifu644', 'gifu645')
    dummy_edge('gifu658', 'gifu657')
    dummy_edge('gifu645', 'gifu657')
    dummy_edge('gifu648', 'gifu650')

    dummy_edges(('gifu656', 'gifu654', 'gifu653', 'gifu655'))
    dummy_edge('gifu656', 'gifu665')
    dummy_edge('gifu654', 'gifu662')
    dummy_edge('gifu653', 'gifu666')

    dummy_edge('gifu665', 'gifu674')
    dummy_edge('gifu666', 'gifu677')
    dummy_edge('gifu663', 'aichi5847')
    dummy_edge('gifu680', 'gifu681')

    dummy_edge('gifu680', 'gifu685')
    dummy_edge('gifu681', 'gifu685')

    dummy_edges(('gifu689', 'gifu688', 'gifu691', 'gifu690', 'gifu693'))

    dummy_edges(('gifu685', 'gifu682', 'gifu686'))
    dummy_edge('gifu686', 'gifu700')

    dummy_edge('gifu689', 'gifu694')
    dummy_edge('gifu688', 'gifu698')
    dummy_edge('gifu691', 'gifu696')
    dummy_edge('gifu690', 'gifu697')

    dummy_edges(('gifu751', 'gifu748', 'gifu747', 'gifu746', 'gifu749', 'gifu743', 'gifu752', 'gifu745'))
    dummy_edge('gifu752', 'gifu778')

    dummy_edge('gifu720', 'gifu741')
    dummy_edge('gifu719', 'gifu755')
    dummy_edge('gifu718', 'gifu750')

    dummy_edges(('gifu708', 'gifu704', 'gifu702', 'gifu701', 'gifu706', 'gifu707', 'gifu703'))
    dummy_edge('gifu700', 'gifu709')
    dummy_edges(('gifu717', 'gifu715', 'gifu726', 'gifu725', 'gifu724', 'gifu722', 'gifu721'))

    dummy_edge('gifu729', 'dummy2020-11-07')
    
    dummy_edge('gifu729', 'dummy2020-11-07')

    dummy_edge('gifu726', 'gifu754')

    graph.graph_attr['rankdir'] = 'LR'
    graph.view()

import ROOT

ROOT.gStyle.SetOptStat(0)

can = [ROOT.ExactSizeCanvas('can%d' % i, 'can%d' % i, 800, 600) for i in range(3)]

t0 = ROOT.TDatime(2020, 7, 1, 0, 0, 0)
nweeks = 20
ndays = nweeks * 7
dt = ndays * 3600 * 24

h_aichi_wo_nagoya = ROOT.TH1D('h_aichi_wo_nagoya', ';Date;Number of Cases / Day', ndays, t0.Convert(), t0.Convert() + dt)
h_nagoya = ROOT.TH1D('h_nagoya', ';Date;Number of Cases / Day', ndays, t0.Convert(), t0.Convert() + dt)
h_gifu = ROOT.TH1D('h_gifu', ';Date;Number of Cases / Day', ndays, t0.Convert(), t0.Convert() + dt)

h_traced = ROOT.TH1D('h_traced', ';Date;Number of Cases / Day', ndays, t0.Convert(), t0.Convert() + dt)
h_untraced = ROOT.TH1D('h_untraced', ';Date;Number of Cases / Day', ndays, t0.Convert(), t0.Convert() + dt)

h_age = ROOT.TH2D('h_age', ';Date;Age;Number of Cases / Day / Generation', ndays, t0.Convert(), t0.Convert() + dt, 11, 0, 110)
h_age.GetXaxis().SetTimeDisplay(1)
h_age.GetXaxis().SetTimeFormat('%b %d')
h_age.GetXaxis().SetNdivisions(100 + int(ndays/7/2), 0)

for case in cases.values():
    if case['node_name'].find('dummy') == 0:
        continue

    date = case['date']
    y, m, d = date.year, date.month, date.day
    t = ROOT.TDatime(y, m, d, 0, 0, 0)

    if case['node_name'].find('aichi') == 0:
        if case['city'] == '名古屋市':
            h_nagoya.Fill(t.Convert())
        else:
            h_aichi_wo_nagoya.Fill(t.Convert())
    elif case['node_name'].find('gifu') == 0:
        h_gifu.Fill(t.Convert())

    if len(case['source_idx']) > 0:
        h_traced.Fill(t.Convert())
    else:
        h_untraced.Fill(t.Convert())

    age = case['age']
    try:
        h_age.Fill(t.Convert(), age + 5 if age >= 10 else 5)
    except:
        print('Ignoring age ', age, ' of ', case['node_name'])

can[0].cd()
h_age.Draw('colz')
ROOT.gPad.SetRightMargin(0.15)
ROOT.gPad.Update()
pal = ROOT.gPad.GetPrimitive('palette')
pal.SetX1NDC(0.86)
pal.SetX2NDC(0.91)

px_age = ROOT.h_age.ProfileX('px_age')
px_age.SetLineColor(2)
px_age.SetLineWidth(3)
px_age.Draw('same e')

can[1].cd()
can[1].SetGridx()
can[1].SetGridy()
h_aichi_wo_nagoya.SetFillColorAlpha(2, 0.5)
h_nagoya.SetFillColorAlpha(5, 0.5)
h_gifu.SetFillColorAlpha(4, 0.5)
stack = ROOT.THStack('stack', '')
stack.Add(h_aichi_wo_nagoya)
stack.Add(h_nagoya)
stack.Add(h_gifu)
stack.Draw()
can[1].Modified()
stack.GetXaxis().SetTimeDisplay(1)
stack.GetXaxis().SetTimeFormat('%b %d')
stack.GetXaxis().SetNdivisions(100 + int(ndays/7/2), 0)
stack.GetYaxis().SetNdivisions(110, 1)
stack.SetTitle(';Date;Number of Cases / Day')

leg = ROOT.TLegend(0.6, 0.7, 0.95, 0.85)
leg.AddEntry(h_gifu, 'Gifu', 'f')
leg.AddEntry(h_nagoya, 'Aichi (Nagoya)', 'f')
leg.AddEntry(h_aichi_wo_nagoya, 'Aichi (Other)', 'f')
leg.SetFillStyle(0)
leg.Draw()

can[2].cd()
can[2].SetGridx()
can[2].SetGridy()
h_traced.SetFillColorAlpha(1, 0.2)
h_untraced.SetFillColorAlpha(1, 0.7)
stack2 = ROOT.THStack('stack2', '')
stack2.Add(h_untraced)
stack2.Add(h_traced)
stack2.Draw()
can[2].Modified()
stack2.GetXaxis().SetTimeDisplay(1)
stack2.GetXaxis().SetTimeFormat('%b %d')
stack2.GetXaxis().SetNdivisions(100 + int(ndays/7/2), 0)
stack2.GetYaxis().SetNdivisions(110, 1)
stack2.SetTitle(';Date;Number of Cases / Day')

leg2 = ROOT.TLegend(0.5, 0.65, 1.0, 0.85)
leg2.AddEntry(h_traced, 'Traced Infection Source', 'f')
leg2.AddEntry(h_untraced, 'Unknown Source', 'f')
leg2.SetFillStyle(0)
leg2.Draw()
