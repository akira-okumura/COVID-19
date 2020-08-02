import graphviz
import datetime
import json
from urllib import request

cases = {}

def readTSV(pref):
    if pref == 'aichi':
        text = open('CTV/Aichi.tsv').readlines()
        lines = open('CTV/Aichi_official.tsv').readlines()[1:]
        lines.reverse()
        modified_text = ''
        for line in lines:
            n, date, person, notionality, city, note, another_index = line[:-1].split('\t')
            n = int(n)
            if n < 1613:
                continue

            if person.find('10歳未満') >= 0:
                sex = person.split('10歳未満')[1]
                age = '10歳未満'
            else:
                age, sex = person.split('代')

            note = note.replace('No.', '愛知県内').replace(',', '例目、').replace('と接触', '例目と接触')
            if note == '':
                note = ' '
            if age == '10歳未満':
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
            pub_date, n, pos_date, age, sex, city, abroad, symp_date, note = line[:-1].split('\t')
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

        if note == '※岐阜県内31例目女性と同じ職場':
            charme = True
        elif note == '※岐阜大学医学部付属病院の精神科医':
            # see https://www.hosp.gifu-u.ac.jp/oshirase/2020/04/04/post_176.html
            # 「当該医師は、30代2名、20代1名であり、接触があった人については、概ね特定されております。」
            charme = True
            source_idx.append('gifu44') 
        elif note in ('※岐阜市内の飲食店（シャルム）の従業員​', '※岐阜市内の飲食店（シャルム）の従業員 ', '※岐阜市内の飲食店（シャルム）の従業員'):
            charme = True
            #source_idx.append('gifu31')
            #source_idx.append('gifu35')
            #source_idx.append('gifu36')
        elif note in ('※岐阜市内の飲食店（シャルム）を利用', '※岐阜市内の飲食店（シャルム）を利用​', '※岐阜市内の飲食店（シャルム）の従業員 ',
                      '※岐阜市内の飲食店（シャルム）の従業員 の濃厚接触者 ', '※岐阜市内の飲食店（シャルム）の従業員​の濃厚接触者​',
                      '※岐阜市内の飲食店（シャルム）の従業員 の濃厚接触者', '※岐阜市内の飲食店（シャルム）利用者の濃厚接触者',
                      '※岐阜市内の飲食店（シャルム）利用者の濃厚接触者'):
            charme = True
            #for i in range(51, 59):
            #    source_idx.append('gifu%d' % i)
        elif node_name in ('gifu113', 'gifu29', 'gifu25', 'gifu31'):
            charme = True
        elif note in ('※集団感染が発生した合唱団に参加', '※岐阜県で集団感染が発生した合唱団に所属'):
            charme = False
            source_idx.append('gifu5')
        elif note in ('※岐阜市内の肉料理店（潜龍）の従業員',):
            source_idx.append('gifu79')
        elif note in ('※岐阜市内の肉料理店（潜龍）の従業員の家族（濃厚接触者）',
                      '※岐阜市内の肉料理店（潜龍）の利用者'):
            source_idx.append('gifu81')
        else:
            charme = False

        cases['%s%d' % (pref, idx)] = {'node_name':node_name, 'date':date, 'note':note,
                                       'source_idx':source_idx, 'age':age, 'city':city,
                                       'description':description, 'linked':False, 'charme':charme}

def register_sources():
    for case in cases.values():
        for source_idx in case['source_idx']:
            cases[source_idx]['linked'] = True

def make_date_ranks():
    date_ranks = {}
    for case in sorted(cases.values(), key=lambda x:x['date']):
        date = case['date']
        if date not in date_ranks.keys():
            date_ranks[date] = [case,]
        else:
            date_ranks[date].append(case)

        # add an empty date
        if str(date) == '2020-07-11':
            date_ranks[datetime.date.fromisoformat('2020-07-12')] = []
        elif str(date) == '2020-07-09':
            date_ranks[datetime.date.fromisoformat('2020-07-10')] = []
        elif str(date) == '2020-07-06':
            date_ranks[datetime.date.fromisoformat('2020-07-07')] = []
        elif str(date) == '2020-07-02':                
            for d in range(3, 6):
                date_ranks[datetime.date.fromisoformat('2020-07-%02d' % d)] = []
        elif str(date) == '2020-06-20':
            for d in range(21, 29):
                date_ranks[datetime.date.fromisoformat('2020-06-%02d' % d)] = []
        elif str(date) == '2020-06-17':
            date_ranks[datetime.date.fromisoformat('2020-06-18')] = []
        elif str(date) == '2020-06-13':
            date_ranks[datetime.date.fromisoformat('2020-06-14')] = []
        elif str(date) == '2020-06-10':
            date_ranks[datetime.date.fromisoformat('2020-06-11')] = []
        elif str(date) == '2020-06-05':
            date_ranks[datetime.date.fromisoformat('2020-06-06')] = []
        elif str(date) == '2020-06-02':
            for d in range(3, 5):
                date_ranks[datetime.date.fromisoformat('2020-06-%02d' % d)] = []
        if str(date) == '2020-05-30':
            date_ranks[datetime.date.fromisoformat('2020-05-31')] = []
        if str(date) == '2020-05-23':
            for d in range(24, 30):
                date_ranks[datetime.date.fromisoformat('2020-05-%02d' % d)] = []
        elif str(date) == '2020-05-16':
            for d in range(17, 23):
                date_ranks[datetime.date.fromisoformat('2020-05-%02d' % d)] = []
        elif str(date) == '2020-05-09':
            date_ranks[datetime.date.fromisoformat('2020-05-10')] = []
        elif str(date) == '2020-05-05':
            date_ranks[datetime.date.fromisoformat('2020-05-06')] = []
            date_ranks[datetime.date.fromisoformat('2020-05-07')] = []
            date_ranks[datetime.date.fromisoformat('2020-05-08')] = []
        elif str(date) == '2020-04-26':
            date_ranks[datetime.date.fromisoformat('2020-04-27')] = []
        elif str(date) == '2020-03-14':
            date_ranks[datetime.date.fromisoformat('2020-03-15')] = []

        elif str(date) == '2020-03-01':
            date_ranks[datetime.date.fromisoformat('2020-03-02')] = []
        elif str(date) == '2020-02-23':
            date_ranks[datetime.date.fromisoformat('2020-02-24')] = []
        elif str(date) == '2020-01-26':
            date_ranks[datetime.date.fromisoformat('2020-01-27')] = []
        elif str(date) == '2020-01-28':
            date_ranks[datetime.date.fromisoformat('2020-01-29')] = []

    return date_ranks

def register_dummy_cases():
    for case in sorted(cases.values(), key=lambda x:x['date']):
        date = case['date']
        node_name = 'dummy%s' % str(date)
        cases[node_name] = {'node_name':node_name, 'date':date, 'note':'',
                            'source_idx':[],
                            'description':'', 'linked':False, 'charme':False}

def make_date_nodes(date_ranks, label_mode):
    date_nodes = []
    for date in date_ranks.keys():
        if str(date) == '2020-01-26':
            with graph.subgraph() as s:
                s.attr('node', fixedsize='1', width='4', fontsize='36')
                s.node('date', label='陽性発表日', shape='plaintext', fontsize='36')
                s.node('NB', label='　' * 47 + '※1 陽性確定日の順に並べているため、各クラスターの先頭が感染源であったことを必ずしも意味しません。\n' \
                       + '　' * 42 + '※2 間違いが混入している可能性がありますので、一次情報は自治体の発表をあたってください。\n' \
                       + '　' * 45 + '※3 岐阜県飲食店シャルムと潜龍での集団感染は、作図が困難なため線の繋がりを一部省略しています。\n' \
                       + '　' * 33 + '※4 愛知県の合計感染者数は延べ人数です。再陽性となった 6 人を含みます。\n' \
                       + '　' * 16 + '※5 印刷・再配布などご自由にどうぞ。', shape='plaintext', fontsize='48', labeljust='l', height='4')
                s.node('author', label='　' * 30 + 'データ出典：https://www.ctv.co.jp/covid-19/ および自治体公開データ\n' + '　' * 28 + '作成：@AkiraOkumura（名古屋大学 宇宙地球環境研究所 奥村曉）', shape='plaintext', fontsize='48', height='2.5')

                #response = request.urlopen('https://www.ctv.co.jp/covid-19/person.txt')
                response = request.urlopen('https://www.ctv.co.jp/covid-19/person2.txt') # new file since Apr 21
                json_data = json.loads(response.read())[0]
                update = json_data['update']
                json_data = json_data['pref3']
                for i in range(len(json_data) - 1, -1, -1):
                    deaths = int(json_data[i]['content2'])
                    total = int(json_data[i]['content'])
                    if json_data[i]['class'] == 'aichi':
                        s.node('total_aichi', label='' + '　' * 16 + ('愛知 合計感染者数：%3d　合計死者数：%2d' % (total, deaths)), shape='plaintext', fontsize='60', height='1.5')
                    elif json_data[i]['class'] == 'gifu':
                        s.node('total_gifu', label='' + '　' * 16 + ('岐阜 合計感染者数：%3d　合計死者数：%3d' % (total, deaths)), shape='plaintext', fontsize='60', height='0.7')

                #m, d = map(int, [x for x in cases.keys() if cases[x]['node_name'].find('dummy') == 0][-1].split('-')[1:])
                #today = '%d/%d %s' % (m, d, t)
                m, d, t = update.replace('月', ' ').replace('日', '').split(' ')
                today = '%s/%s %s' % (m, d, t)
                s.node('title', label='　' * 20 + '新型コロナウイルス感染経路図（%s 現在）' % today, shape='plaintext', fontsize='80')

                s.node('border', label='\n愛知県↑\n岐阜県↓', shape='plaintext', height='8', fontsize='40')
                s.node('arrow_exp', label='\n濃厚接触もしくは\n健康観察対象者', shape='plaintext', fontcolor='black', height='2')
                s.node('arrows', label='\n\n←→', shape='plaintext', fontcolor='black')
                s.node('nosex', label='紫：性別不明', shape='plaintext', fontcolor='purple')
                s.node('male', label='青：男性　　', shape='plaintext', fontcolor='blue')
                s.node('female', label='赤：女性　　', shape='plaintext', fontcolor='red')
                s.node('blank10', style='invis')
                s.node('cap1', label='岐阜県飲食店\nシャルム関連', shape='doublecircle')
                s.node('cap2', label='帰国者 or 外国籍', shape='circle')
                s.node('cap3', label='感染経路不明\nor 未確定\nor 他地域流入?', style='filled', shape='circle', color='#000000AA', fontcolor='white')
                s.node('cap4', label='接触者\n※リンク非表示\nは他県との接触', shape='square')
                s.node('cap5', label='県外滞在者\n感染経路不明', shape='tripleoctagon', height='4', style='filled', color='#000000AA', fontcolor='white')
                s.node('cap6', label='県外陽性者\nとの接触者', shape='tripleoctagon', height='4')
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
                elif case['description'].find('名古屋市在住の方（性別・年代非公表）') >= 0 or case['description'] == '':
                    color = '#ff00ff' # purple
                else:
                    color='#000000' # black

                if case['note'].find('帰国') >= 0 or \
                   case['description'].find('中国籍') >= 0 or \
                   case['description'].find('帰国') >= 0 or \
                   (case['note'].find('渡航歴') >= 0 and case['note'].find('家族がパキスタン渡航歴あり') < 0):
                    s.attr('node', shape='circle', style='', color=color, fontcolor='black')
                elif case['note'].find('感染経路不明') >= 0 or case['node_name'] in ('gifu79', 'aichi662', 'aichi661'):
                    s.attr('node', shape='circle', style='filled', color=color+'AA', fontcolor='white')
                elif case['charme']:
                    s.attr('node', shape='doublecircle', style='', color=color, fontcolor='black')
                elif case['node_name'] not in ('aichi1402', 'aichi1435', 'aichi1722') and \
                     (case['note'].find('例目') >= 0 or \
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
                      case['note'].find('再度') >= 0 or \
                      case['note'].find('愛知県陽性患者の接触者') >= 0 or \
                      case['note'].find('後日感染判明者と接触') >= 0 or \
                      case['node_name'] == 'gifu151' or \
                      case['node_name'] == 'aichi521' or \
                      case['node_name'] in ('gifu210', 'gifu211', 'gifu215', 'gifu216')): # 7/24 Gifu cases not reflected in CTV data
                    s.attr('node', shape='square', style='', color=color, fontcolor='black')
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
                     case['note'].find('静岡県熱海市のクラスターが発生したカラオケを伴う飲食店を利用') >= 0 or \
                     case['note'].find('四日市市陽性患者の接触者') >= 0 or \
                     case['note'].find('三重県陽性患者の接触者') >= 0 or \
                     case['note'].find('浜松市患者の濃厚接触者') >= 0 or \
                     case['node_name'] in ('aichi1220', 'aichi1414'):
                    s.attr('node', shape='tripleoctagon', style='', color=color, fontcolor='black')
                elif case['node_name'] in ('aichi547') or \
                     case['note'].find('滞在') >= 0 or case['note'].find('東京都から名古屋市へ移動') >= 0 or \
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
                        else:
                            label = '%d代' % case['age']

                        s.node(case['node_name'], label=label, fontname='Myriad Pro')
                    elif label_mode == 2: # city
                        s.node(case['node_name'], label=case['city'].replace('市', ''), fontname='Myriad Pro')

    graph.edge('date', date_nodes[0], style='invis')
    graph.edge('border', 'dummy2020-01-26', style='invis')

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
        dummy_case = cases['dummy%s' % str(case['date'])]
        if case['node_name'] not in ('gifu5') or \
           case['node_name'] not in ('gifu9', 'gifu10', 'gifu11') or \
           case['node_name'] not in ('gifu16') or \
           case['node_name'] not in ('gifu23', 'gifu24', 'gifu25', 'gifu26') or \
           case['node_name'] not in ('gifu27', 'gifu28', 'gifu29', 'gifu30', 'gifu31') or \
           case['node_name'] not in ('gifu48', 'gifu52', 'gifu54', 'gifu55', 'gifu56', 'gifu57', 'gifu58'):
            graph.edge(dummy_case['node_name'], case['node_name'], style='invis')

for label_mode in range(3):
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
        if len(case['source_idx']) > 0:
            source_idx = case['source_idx']
            node_name = case['node_name']
            for source in source_idx:
                source_name = cases[source]['node_name']
                graph.edge(source_name, node_name)

    link_date_nodes()
    link_dummy_nodes()

    #dummy_edge = lambda a, b : graph.edge(a, b, color='red')#, style='invis') # for debugging
    dummy_edge = lambda a, b : graph.edge(a, b, style='invis')

    dummy_edge('aichi166', 'aichi165')
    dummy_edge('aichi64', 'aichi69')
    dummy_edge('aichi132', 'aichi131')
    dummy_edge('aichi131', 'aichi134')

    dummy_edge('aichi160', 'aichi158')
    dummy_edge('aichi163', 'aichi162')

    dummy_edge('aichi98', 'aichi90')

    dummy_edge('aichi188', 'aichi189')

    # Police cluster
    dummy_edge('aichi181', 'aichi182')

    dummy_edge('aichi193', 'aichi192')

    dummy_edge('aichi214', 'aichi217')

    dummy_edge('aichi21', 'aichi23')
    #dummy_edge('aichi22', 'aichi23')    

    # place Aichi nodes in Aichi
    dummy_edge('aichi134', 'dummy2020-03-19')
    dummy_edge('aichi145', 'dummy2020-03-23')
    dummy_edge('aichi151', 'aichi152')
    dummy_edge('aichi155', 'aichi152')
    dummy_edge('aichi155', 'aichi151')
    dummy_edge('aichi155', 'dummy2020-03-26')
    dummy_edge('aichi158', 'aichi159')
    dummy_edge('aichi159', 'dummy2020-03-27')
    dummy_edge('aichi162', 'dummy2020-03-28')
    dummy_edge('aichi165', 'dummy2020-03-29')
    dummy_edge('aichi172', 'dummy2020-03-31')
    dummy_edge('aichi179', 'dummy2020-04-01')
    dummy_edge('aichi181', 'dummy2020-04-01')
    dummy_edge('aichi182', 'dummy2020-04-01')
    dummy_edge('aichi187', 'aichi186')
    dummy_edge('aichi186', 'dummy2020-04-02')
    dummy_edge('aichi221', 'aichi217')
    dummy_edge('aichi217', 'aichi207')
    dummy_edge('aichi207', 'dummy2020-04-04')
    dummy_edge('aichi227', 'dummy2020-04-05')
    dummy_edge('aichi208', 'aichi209')
    dummy_edge('aichi209', 'aichi210')
    dummy_edge('aichi210', 'aichi220')

    dummy_edge('aichi247', 'aichi259')
    dummy_edge('aichi259', 'aichi253')

    dummy_edge('aichi261', 'aichi279')
    dummy_edge('aichi279', 'aichi276')

    dummy_edge('aichi233', 'aichi231')
    dummy_edge('aichi262', 'aichi263')
    dummy_edge('aichi263', 'aichi264')
    dummy_edge('aichi264', 'aichi274')

    dummy_edge('aichi270', 'aichi280')
    dummy_edge('aichi280', 'aichi277')
    dummy_edge('aichi267', 'aichi275')
    dummy_edge('aichi266', 'aichi282')
    dummy_edge('aichi275', 'dummy2020-04-08')
    dummy_edge('aichi282', 'aichi285')
    dummy_edge('aichi267', 'aichi275')


    dummy_edge('aichi272', 'aichi330')

    dummy_edge('aichi341', 'aichi346')

    dummy_edge('aichi378', 'aichi391')
    dummy_edge('aichi377', 'aichi392')
    dummy_edge('aichi399', 'aichi398')
    dummy_edge('aichi398', 'aichi392')
    dummy_edge('aichi391', 'aichi400')
    dummy_edge('aichi392', 'aichi404')
    dummy_edge('aichi409', 'aichi404')

    dummy_edge('aichi439', 'aichi449')
    dummy_edge('aichi449', 'aichi448')
    dummy_edge('aichi448', 'aichi434')

    dummy_edge('aichi471', 'aichi475')
    dummy_edge('aichi475', 'aichi474')
    dummy_edge('aichi474', 'aichi463')
    dummy_edge('aichi463', 'aichi462')


    dummy_edge('aichi403', 'aichi410')

    dummy_edge('aichi348', 'aichi372')

    dummy_edge('aichi394', 'aichi395')
    dummy_edge('aichi395', 'aichi396')

    dummy_edge('aichi421', 'aichi430')
    dummy_edge('aichi406', 'aichi402')

    dummy_edge('aichi428', 'aichi422')

    dummy_edge('aichi440', 'aichi468')

    dummy_edge('aichi450', 'aichi451')
    dummy_edge('aichi472', 'aichi465')
    dummy_edge('aichi489', 'aichi490')

    dummy_edge('aichi501', 'aichi499')
    dummy_edge('aichi499', 'dummy2020-05-09')

    dummy_edge('aichi503', 'dummy2020-05-12')

    dummy_edge('aichi505', 'dummy2020-05-14')

    dummy_edge('aichi506', 'aichi507')
    dummy_edge('aichi507', 'dummy2020-05-15')

    dummy_edge('aichi512', 'dummy2020-06-02')
    dummy_edge('aichi513', 'dummy2020-06-05')

    dummy_edge('aichi516', 'aichi515')
    dummy_edge('aichi515', 'dummy2020-06-10')

    dummy_edge('aichi518', 'dummy2020-06-12')

    dummy_edge('aichi543', 'aichi577')
    #dummy_edge('aichi545', 'aichi536')

    dummy_edge('dummy2020-03-21', 'gifu5')
    dummy_edge('gifu5', 'gifu4')
    dummy_edge('gifu8', 'gifu7')
    dummy_edge('gifu7', 'gifu6')
    dummy_edge('dummy2020-03-24', 'gifu10')
    dummy_edge('gifu9', 'gifu10')
    dummy_edge('gifu10', 'gifu11')
    dummy_edge('gifu8', 'gifu10')
    dummy_edge('gifu7', 'gifu11')
    dummy_edge('dummy2020-03-27', 'gifu16')
    dummy_edge('gifu16', 'gifu17')
    dummy_edge('aichi161', 'aichi163')
    dummy_edge('dummy2020-03-31', 'gifu26')
    dummy_edge('gifu26', 'gifu25')
    dummy_edge('gifu25', 'gifu23')
    dummy_edge('gifu23', 'gifu24')
    dummy_edge('dummy2020-04-01', 'gifu27')
    dummy_edge('gifu27', 'gifu29')
    dummy_edge('gifu29', 'gifu28')
    dummy_edge('gifu30', 'gifu31')
    dummy_edge('gifu28', 'gifu30')
    dummy_edge('gifu24', 'gifu31')
    dummy_edge('gifu28', 'gifu31')
    dummy_edge('gifu32', 'gifu36')
    dummy_edge('gifu36', 'gifu35')
    dummy_edge('gifu35', 'gifu34')
    dummy_edge('gifu34', 'gifu33')
    dummy_edge('gifu40', 'gifu38')
    dummy_edge('gifu38', 'gifu39')
    dummy_edge('dummy2020-04-04', 'gifu45')
    dummy_edge('gifu45', 'gifu46')
    dummy_edge('gifu46', 'gifu47')
    dummy_edge('gifu47', 'gifu41')
    dummy_edge('gifu41', 'gifu42')
    dummy_edge('gifu42', 'gifu43')
    dummy_edge('dummy2020-04-05', 'gifu48')
    dummy_edge('gifu48', 'gifu52')
    dummy_edge('gifu52', 'gifu54')
    dummy_edge('gifu54', 'gifu55')
    dummy_edge('gifu55', 'gifu56')
    dummy_edge('gifu56', 'gifu57')
    dummy_edge('gifu57', 'gifu58')
    dummy_edge('gifu59', 'gifu50')

    dummy_edge('gifu87', 'gifu97')
    '''
    dummy_edge('dummy2020-04-21', 'gifu140')
    dummy_edge('gifu140', 'gifu144')
    dummy_edge('gifu144', 'gifu143')
    '''
    dummy_edge('gifu141', 'gifu140')
    dummy_edge('gifu140', 'gifu148')

    #dummy_edge('aichi535', 'aichi536')
    dummy_edge('aichi536', 'dummy2020-07-13')
    dummy_edge('gifu164', 'gifu163')
    dummy_edge('gifu163', 'gifu165')

    dummy_edge('aichi565', 'aichi594')

    dummy_edge('aichi599', 'aichi638')

    dummy_edge('aichi600', 'aichi580')

    dummy_edge('aichi622', 'aichi597')

    dummy_edge('aichi623', 'aichi671')

    dummy_edge('aichi646', 'aichi608')

    dummy_edge('aichi674', 'aichi635')

    dummy_edge('aichi673', 'aichi732')
    dummy_edge('aichi728', 'aichi732')

    dummy_edge('aichi768', 'aichi703')

    dummy_edge('aichi726', 'aichi725')
    dummy_edge('aichi725', 'aichi665')

    dummy_edge('aichi719', 'aichi783')
    dummy_edge('aichi717', 'aichi805')
    dummy_edge('aichi774', 'aichi789')

    dummy_edge('dummy2020-07-26', 'gifu228')
    dummy_edge('aichi844', 'dummy2020-07-23')
    dummy_edge('aichi916', 'dummy2020-07-24')
    #dummy_edge('aichi917', 'aichi916')
    dummy_edge('gifu183', 'gifu200')
    #dummy_edge('gifu184', 'gifu187')
    #dummy_edge('gifu194', 'gifu188')
    #for i in range(181, 186):
    #    dummy_edge('gifu%d' % (i + 1), 'gifu%d' % i)
    dummy_edge('dummy2020-07-21', 'gifu184')
    dummy_edge('gifu228', 'gifu221')
    dummy_edge('gifu214', 'gifu207')
    dummy_edge('gifu216', 'gifu206')
    dummy_edge('gifu207', 'gifu206')
    dummy_edge('gifu203', 'gifu217')

    dummy_edge('aichi700', 'aichi871')
    dummy_edge('aichi756', 'aichi612')
    dummy_edge('aichi822', 'aichi882')
    dummy_edge('aichi815', 'aichi924')
    dummy_edge('aichi928', 'aichi823')
    dummy_edge('aichi956', 'aichi914')

    dummy_edge('gifu227', 'gifu236')
    dummy_edge('gifu226', 'gifu237')
    dummy_edge('gifu225', 'gifu240')
    dummy_edge('gifu224', 'gifu234')
            
    dummy_edge('gifu217', 'gifu239')

    dummy_edge('aichi1024', 'aichi963')
    dummy_edge('aichi778', 'aichi694')
    dummy_edge('aichi994', 'aichi798')
    dummy_edge('aichi992', 'aichi739')
    dummy_edge('aichi922', 'aichi738')
    dummy_edge('aichi980', 'aichi754')
    dummy_edge('aichi859', 'aichi742')
    dummy_edge('aichi1015', 'aichi748')
    dummy_edge('aichi1026', 'aichi947')
    dummy_edge('aichi1047', 'aichi892')
    dummy_edge('aichi1031', 'aichi986')
    dummy_edge('aichi1067', 'aichi904')
    dummy_edge('aichi959', 'aichi818')
    dummy_edge('aichi1182', 'aichi1069')
    dummy_edge('aichi1178', 'aichi1025')
    dummy_edge('aichi1192', 'aichi1021')
    dummy_edge('aichi1270', 'aichi637')
    dummy_edge('aichi1098', 'aichi973')

    #dummy_edge('aichi997', 'aichi1104')

    graph.graph_attr['rankdir'] = 'LR'
    graph.view()
    import os
    os.system('open -a Preview %s.pdf' % fname)
