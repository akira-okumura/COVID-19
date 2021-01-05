import graphviz
import datetime
import json
from urllib import request
import re
import networkx as nx
import ROOT

debug = False
#debug = True

aichi_gifu_contact_tuple = (
    '例目', '外国人学校クラスター関連', '名古屋市陽性者の濃厚接触者（同じ職場）',
    '11月6日岐阜県公表のクラスターの関連から検査',
    '11月6日岐阜県内のクラスターの関連から検査', '11月6日の岐阜県クラスターの関連から検査',
    '岐阜のクラスターの関連から検査', 'PUB「EDEN」関係の患者の濃厚接触者',
    '11月6日の集団感染が発生した市内事業所の',
    '11月6日岡崎市発表の集団感染が発生した市内事業所の',
    '岐阜県で集団感染が発生した合唱団に所属',
    '※集団感染が発生した合唱団に参加', '大阪市内のライブハウスの利用者',
    '岐阜市内の肉料理店（潜龍）', 'スポーツジムの利用者',
    '※高齢者施設の送迎ドライバーとして勤務',
    '※死亡後に感染を確認<br>※名古屋市緑区のデイサービスを利用',
    '※3月5日に感染確認。3月24日に検査で陰性だったため退院。4月2日に陽性と再度確認',
    '※4月2日に愛知県の陽性患者と接触', '※愛知県陽性患者の濃厚接触者',
    '※愛知県発表の陽性患者の濃厚接触者', '※名古屋市緑区のデイサービスを利用',
    '愛知県内1642例目と同一患者', '愛知県内1484例目と同一患者', '再度',
    '愛知県陽性患者の接触者', '愛知県陽性者の濃厚接触者', '後日感染判明者と接触',
    '名古屋市事例と接触', '愛知県内陽性者と接触', '愛知県患者の濃厚接触',
    '名古屋市陽性患者の濃厚接触者', '名古屋市陽性患者の接触者', '愛知県患者の濃厚接触者',
    '愛知県陽性患者の濃厚接触者', '愛知県陽性者の接触者', '名古屋市陽性者の濃厚接触者',
    '名古屋市陽性者の接触者', '豊田市陽性者の接触者', '知人が陽性者',
    '新型コロナウイルス接触確認アプリの通知により検査', '岐阜県事例の別居親族',
    '市外の陽性者の濃厚接触者', '陽性者が発生した市内医療機関の関係者', '愛知県患者の接触者',
    '岐阜市事例の濃厚接触者', '陽性者が発生した市内高齢者施設の関係者', '岐阜県事例の濃厚接触者',
    '岐阜県事例と接触')

non_aichi_gifu_contact_tuple = (
    '新宿区の劇場利用', '新宿区内の劇場を利用', 'さいたま市発表の陽性患者の家族',
    'さいたま市発表の陽性患者との接触を確認', '東京都発表の陽性患者との接触を確認',
    '神奈川県発表の陽性患者の同僚', '東京都発表の陽性患者の濃厚接触者',
    '京都市発表の陽性患者と接触', '滋賀県発表の陽性患者の濃厚接触者',
    '石川県発表の陽性患者の濃厚接触者', '東京都事例と接触', '浜松市事例と接触',
    '富山県事例と接触', '三重県事例と接触', '東京都事例の家族', '東京都事例の同居家族',
    '大阪府事例と接触', '大阪府陽性者と接触', '三重県公表231', '神奈川県9100',
    '静岡県熱海市のクラスターが発生したカラオケを伴う飲食店を利用', '四日市市陽性患者の接触者',
    '三重県陽性患者の接触者', '浜松市患者の濃厚接触者', '石川県事例と接触',
    '大阪府事例の知人', '東京都事例の知人', '神奈川県事例の知人', '高知県発表86',
    '沖縄県発表1557', '東京都の陽性患者と接触', '東京都陽性患者の接触者',
    '東京都陽性患者の濃厚接触者', '大阪府事例の家族', '大阪府発表11853', '大阪府7256',
    '大阪府7421', '兵庫県1927', '神戸市744', '滋賀県発表505', '兵庫県公表2531',
    '三重県内443例目の知人', '神奈川県患者と接触', '大分市発表79例目の濃厚接触',
    '川崎市陽性患者の濃厚接触者（友人）', '大阪府陽性患者の濃厚接触者（友人）',
    '東京都にて埼玉県の陽性患者と接触',
    '東京都にて感染が確認された新型コロナウイルス感染症患者の濃厚接触者', '滋賀県内468例目',
    '東京都陽性患者と接触', '滞在中に大阪府陽性患者と接触', '大阪府発表11596',
    '北海道3424', '大阪府13123', '宮城県861', '鹿児島県533', '鹿児島県480',
    '神奈川県7779', '京都市公表1323', '福岡県5230', '滋賀県陽性患者の濃厚接触者',
    '北海道公表3964', '三重県611', '静岡市公表の陽性患者と接触', '東京都陽性者の濃厚接触者',
    '東京都の陽性者と接触', '静岡県発表988', 'さいたま市発表1125', '広島県の陽性者と接触',
    '県外⑫の濃厚接触者（家族）', '三重県発表643,666', '静岡県1105', '三重県発表643,666',
    '三重県665', '姫路市公表340', '四日市市公表の関連から検査', '札幌市陽性者と接触',
    '三重県667', '神奈川県陽性者の濃厚接触者', '県外⑰の接触者', '大阪府陽性患者と接触',
    '静岡県の陽性患者と接触', '東京都事例の同僚', '沖縄県事例の同僚', '長野県陽性者の接触者',
    '大阪府陽性者の濃厚接触者', '東京都の陽性患者及び名古屋市発表58', '滋賀県陽性者の接触者',
    '四日市市公表160', '三重県921', '静岡県陽性者の濃厚接触者', '石川県916',
    '浜松市発表569', '山形県公表226', '沖縄県陽性患者の濃厚接触者', '京都府陽性患者と接触',
    '福岡県6692', '浜松市発表569', '浜松市発表582', '東京都事例の濃厚接触者',
    '浜松市発表580', '広島県陽性患者と接触', '長野県公表1011', '静岡県事例の濃厚接触者',
    '福岡県6736', '滋賀県公表883', '神奈川県陽性患者と接触',
    '長野県陽性者の濃厚接触者（親族）', '三重県公表1161', '静岡県2276',
    '埼玉県陽性者の接触者', '大阪府陽性者の接触者', '県外43の濃厚接触者（家族）',
    '岩手県事例の濃厚接触者', '三重県発表1210', '横浜市発表8621',
    '長崎県事例と接触', '長野県事例と接触', '岡山県事例と接触')

class Case:
    def __init__(self, age, city, node_name, note, date, description, connected_nodes):
        self.age = age
        self.city = city
        self.date = date
        self.node_name = node_name
        self.note = note
        self.description = description
        self.connected_nodes = connected_nodes
        self.is_connected = False
        self.cluster_duration = 1
        self.make_gv_label()

    def make_gv_label(self):
        if self.age == None:
            self.gv_label = ''
        elif self.age == 0:
            self.gv_label = '0歳'
        elif self.age == 9:
            self.gv_label = '<10歳'
        elif self.age == '調査中':
            self.gv_label = '調査中'
        else:
            self.gv_label = '%d代' % self.age

        if self.city[-1] == '市':
            self.gv_label += '\n' + self.city[:-1]
        else:
            self.gv_label += '\n' + self.city

    def is_male(self):
        if self.description.find('男性') >= 0:
            return True
        else:
            return False

    def is_fmale(self):
        if self.description.find('女性') >= 0:
            return True
        else:
            return False

    def is_unknown_sex(self):
        if self.description.find('名古屋市在住の方（性別・年代非公表）') >= 0 or self.description == '' or self.description.find('調査中（') >= 0 :
            return True
        else:
            return False

    def has_foreign_route(self):
        if self.note.find('帰国') >= 0 or \
           self.description.find('中国籍') >= 0 or \
           self.description.find('帰国') >= 0 or \
           self.description.find('10月17日にイタリアから入国') >= 0 or \
           self.note.find('11月10日に南アフリカ共和国から入国') >= 0 or \
           self.note.find('11月21日にパキスタンから帰国') >= 0 or \
           self.note.find('11月27日アメリカから帰国') >= 0 or \
           self.note.find('12月3日ポルトガルから帰国') >= 0 or \
           self.note.find('12月6日にロシアより入国') >= 0 or \
           self.note.find('12月1日海外から入国') >= 0 or \
           self.note.find('航空機近席に感染者あり') >= 0 or \
           self.note.find('フィリピン') >= 0 or \
           (self.note.find('渡航歴') >= 0 and self.note.find('家族がパキスタン渡航歴あり') < 0):
            return True
        else:
            return False

    def has_non_aichi_gifu_route(self):
        return False

    def has_aichi_gifu_route(self):
        return False

class CaseGraph:
    def __init__(self, fname):
        self.gv_graph = graphviz.Graph(engine='dot', filename=fname)
        self.gv_graph.attr('node', fontname='Hiragino UD Sans F StdN', fontsize='14')
        self.gv_graph.attr('edge', arrowhead='normal', arrowsize='0.5', dir='both')
        self.gv_graph.attr(nodesep='0.1', ranksep='0.12')
        self.gv_graph.graph_attr['rankdir'] = 'LR'

        self.nx_graph = nx.path_graph(0)

    def add_cases(self, cases, pref=None):
        for case in cases.values():
            for node in case.connected_nodes:
                cases[node].is_connected = True

        self.make_nx_nodes(cases)

        self.make_pref_selection(cases, pref)

        self.make_gv_date_rank_ditc(cases, pref)
        self.make_gv_caption()
        self.make_gv_date_nodes()
        self.make_gv_edges(cases)
        self.make_gv_notes()

    def add_only_aichi_cases(self, cases):
        self.add_cases(cases, 'aichi')

    def add_only_gifu_cases(self, cases):
        self.add_cases(cases, 'gifu')

    def make_nx_nodes(self, cases):
        for case in sorted(cases.values(), key=lambda x:x.date):
            self.nx_graph.add_node(case.node_name)
            for node in case.connected_nodes:
                self.nx_graph.add_edge(case.node_name, node)

    def make_pref_selection(self, cases, pref=None):
        if pref == None:
            return

        # make clusters from the NetworkX graph
        for comp in nx.connected_components(self.nx_graph):
            subgraph = self.nx_graph.subgraph(comp).copy()
            node_names = subgraph.nodes

            # calculate the claster duration for later sort
            first_day = datetime.date.fromisoformat('3000-01-01')
            last_day = datetime.date.fromisoformat('1000-01-01')
            for node_name in node_names:
                day = cases[node_name].date
                if first_day > day:
                    first_day = day
                if last_day < day:
                    last_day = day

            # duration of the cluster (e.g., = 1 for isolated cases)
            days = (last_day - first_day).days + 1

            for node_name in node_names:
                cases[node_name].cluster_duration = days
            
            # check if the cluster has 'aichiXXX' or 'gifuYYY'
            if len([x for x in node_names if x.find(pref) >= 0]) == 0:
                for node_name in node_names:
                    cases.pop(node_name) # remove the node if it is not relevant to 'pref'

    def make_gv_notes(self):
        source = self.gv_graph.source
        notes = (('gifu708', '岐阜市\n芸能事務所'), ('gifu741', '美濃加茂市\n外国人学校'), ('gifu1078', '美濃加茂市\nデイサービス'),
                 ('gifu1041', '岐阜市\n河村病院'), ('gifu1270', '大垣日大高校'), ('gifu1378', '多治見市\nケアハウスビアンカ\n（老人ホーム）'),
                 ('gifu1491', '中京学院大学\n硬式野球部'), ('gifu1603', '中津川市\nサンシャインプレミアム中津川\nグループホーム'), ('gifu1463', '複数大学の会食'),
                 ('gifu1086', '岐阜協立大学\n男子バレーボール部'), ('gifu1559', '岐南町\n障害者福祉施設'), ('gifu1673', '本巣市\n職場'),
                 ('gifu2106', '本巣郡北方町\nGAS PANIC（接待）'), ('gifu1924', '岐阜市折立\nオイコットクラブ（接待）'), ('gifu1950', '朝日大\n運動部'),
                 ('gifu1783', '可児市\nスターダストフィリピンクラブ'), ('gifu1930', '羽島市\n入所型高齢者福祉施設'), ('gifu2193', '複数大学の飲食'),
                 ('gifu1377', '羽島市\n職場関連'), ('gifu2250', '岐阜市\n高齢者福祉施設'), ('gifu2079', '会食'),
                 ('gifu2108', '親族の会食'), ('gifu1857', '可児郵便局'), ('gifu1254', '帝京大可児高校'),
                 ('gifu1134', 'さわやかナーシング\n可児デイサービスセンター'), ('gifu1206', '複数の飲食店'), ('gifu1887', '各務原市\n職場'),
                 ('gifu1256', '岐阜協立大\nサッカー部（飲食）'), ('gifu1243', '不破郡垂井町\n不破高校'), ('gifu1257', '飲食店会食\nから親族へ'),
                 ('gifu956', '揖斐郡池田町\nイビデン樹脂'), ('gifu1662', '海津市\n学童保育'), ('gifu1253', '高山市\n久美愛厚生病院'),
                 ('gifu1152', '親族'), ('gifuX', ''), ('gifuX', ''))
        for note in notes:
            if source.find(note[0]) >= 0:
                self.gv_graph.node('%s_caption' % note[0], label=note[1], shape='plaintext', fixedsize='1', width='0.5', height='0.5', fontsize='12')
                self.gv_graph.edge(note[0], '%s_caption' % note[0], style='dashed', color='gray', arrowhead='odot')

    def make_gv_edges(self, cases):
        for case in cases.values():
            if before_2020Nov(case.date):
                continue
            if len(case.connected_nodes) > 0:
                node_name = case.node_name
                for node in case.connected_nodes:
                    source_node_name = cases[node].node_name
                    if before_2020Nov(cases[node].date):
                        continue
                    self.gv_graph.edge(source_node_name, node_name)


    def make_gv_caption(self):
        with self.gv_graph.subgraph() as s:
            s.attr('node', fixedsize='1', width='2', fontsize='18')
            s.node('date', label='陽性発表日', shape='plaintext', fontsize='18')
            s.node('empty', style='invis', height='20')

            s.node('arrows', label='←→\n接触経路', shape='plaintext', fontcolor='black', fontsize='24', height='3')
            s.node('nosex', label='紫：性別不明', shape='plaintext', fontcolor='purple', fontsize='24')
            s.node('male', label='青：男性　　', shape='plaintext', fontcolor='blue', fontsize='24')
            s.node('female', label='赤：女性　　', shape='plaintext', fontcolor='red', fontsize='24')
            s.node('blank10', style='invis')
            s.node('cap2', label='帰国者 or 外国籍', shape='circle')
            s.node('cap3', label='感染経路不明', style='filled', shape='circle', color='#000000AA', fontcolor='white')
            s.node('cap4', label='接触者\n※リンク非表示\nは他県との接触', shape='square')
            s.node('cap5', label='県外滞在者\n感染経路不明', shape='tripleoctagon', height='2', style='filled', color='#000000AA', fontcolor='white')
            s.node('cap6', label='県外陽性者\nとの接触者', shape='tripleoctagon', height='2')
            s.node('cap7', label='\n図の読み方', shape='plaintext', fontsize='24', height='2')

            s.node('NB', label='　' * 47 + '※1 陽性確定日の順に並べているため、各クラスターの先頭が感染源であったことを必ずしも意味しません。\n' \
                   + '　' * 42 + '※2 間違いが混入している可能性がありますので、一次情報は自治体の発表をあたってください。\n' \
                   + '　' * 32 + '※3 愛知県の合計感染者数は延べ人数です。再陽性となった人を含みます。\n' \
                   + '　' * 15 + '※4 印刷・再配布などご自由にどうぞ', shape='plaintext', fontsize='24', labeljust='l', height='1.4')
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
                    s.node('total_aichi', label='' + '　' * 20 + ('愛知 合計感染者数：%5d　合計死者数：%3d' % (total, deaths)), shape='plaintext', fontsize='30', height='0.5')
                elif json_data[i]['class'] == 'gifu':
                    s.node('total_gifu', label='' + '　' * 20 + ('岐阜 合計感染者数：%6d　合計死者数：%4d' % (total, deaths)), shape='plaintext', fontsize='30', height='0.5')

            m, d, t = update.replace('月', ' ').replace('日', '').split(' ')
            today = '%s/%s %s' % (m, d, t)
            s.node('title', label='　' * 20 + '新型コロナウイルス感染経路図（%s 現在）' % today, shape='plaintext', fontsize='40')

    def make_gv_date_rank_ditc(self, cases, pref=None):
        '''
        Makes a date rank dictionary for later graphvis use.
        Each date rank holds all the cases reported on that day.
        '''
        self.date_ranks = {} # stores all cases date by date
        for case in sorted(cases.values(), key=lambda x:x.date):
            date = case.date
            if before_2020Nov(case.date):
                continue
            if date not in self.date_ranks.keys():
                self.date_ranks[date] = [case,]
            else:
                self.date_ranks[date].append(case)        

    def make_gv_date_nodes(self):
        '''
        Makes graphvis "ranked" subgraphs for individual dates
        '''
        self.date_nodes = []

        for date in sorted(self.date_ranks.keys()):
            with self.gv_graph.subgraph() as sub:
                sub.attr(rank='same')
                # default not to be seen
                sub.attr('node', fixedsize='1', width='0.5')
                m, d = map(int, str(date).split('-')[1:])
                if (m, d) == (1, 26) or (m, d) == (2, 14) or d == 1:
                    label = '%d/%d' % (m, d)
                elif (m, d) == (1, 29):
                    label = '……'
                else:
                    label = '%d' % d
                if d == 1:
                    sub.node('date%s' % date, label=label, shape='plaintext', fontsize='24')
                else:
                    sub.node('date%s' % date, label=label, shape='plaintext', fontsize='20')
                self.date_nodes.append('date%s' % date)

                #self.date_ranks[date] = sorted(self.date_ranks[date], key=lambda x:x.is_connected, reverse=True)
                self.date_ranks[date] = sorted(self.date_ranks[date], key=lambda x:x.cluster_duration, reverse=True)

                for case in self.date_ranks[date]:
                    # Default values. To be changed according to the case specs later.
                    sub.attr('node', shape='octagon', color='black', style='diagonals', fontcolor='black')
                    if case.is_male():
                        color = '#0000ff' # blue
                    elif case.is_fmale():
                        color = '#ff0000' # red
                    elif case.is_unknown_sex():
                        color = '#ff00ff' # purple
                    else:
                        color='#000000' # black

                    if case.has_foreign_route():
                        sub.attr('node', shape='circle', style='', color=color, fontcolor='black')
                    elif case.note.find('感染経路不明') >= 0 or case.node_name in ('gifu79', 'aichi662', 'aichi661'):
                        sub.attr('node', shape='circle', style='filled', color=color+'AA', fontcolor='white')
                    elif len([x for x in non_aichi_gifu_contact_tuple if case.note.find(x) >= 0]) > 0 or \
                         case.node_name in ('aichi10002', 'aichi10003') or \
                         case.node_name in ('aichi1220', 'aichi1414'):
                        sub.attr('node', shape='tripleoctagon', style='', color=color, fontcolor='black')
                    elif case.node_name not in ('aichi1402', 'aichi1435', 'aichi1722', 'aichi3768', 'aichi3775') and \
                         (len([x for x in aichi_gifu_contact_tuple if case.note.find(x) >= 0]) > 0 or \
                          case.note == 'あり' or \
                          case.node_name == 'gifu151' or \
                          case.node_name == 'aichi521' or \
                          case.node_name in ('gifu210', 'gifu211', 'gifu215', 'gifu216')): # 7/24 Gifu cases not reflected in CTV data
                        sub.attr('node', shape='square', style='', color=color, fontcolor='black')
                    elif case.node_name in ('aichi547') or \
                         len([x for x in ('滞在', '東京都から名古屋市へ移動', '8月13日～16日に大阪府に滞在', '9月25日まで神奈川県居住', '7月30日～8月10日に青森県、岩手県、宮城県、福島県、秋田県に滞在', '8月18日まで静岡県に在住', '9月12日から名古屋市に滞在', '6月15~16日神奈川県、6月19~21日東京を訪問') if case.note.find(x) >= 0]) > 0 or \
                         (case.node_name in ('aichi918', 'aichi925', 'aichi939') or # 7/24 Nagoya cases not reflected in CTV data
                          case.node_name in ('aichi998',)): # 7/25 Nagoya cases not reflected in CTV data '7/9〜7/10に大阪府滞在'
                        sub.attr('node', shape='tripleoctagon', style='filled', color=color+'AA', fontcolor='white')
                    elif case.node_name.find('dummy2') == 0:
                        pass
                    else:
                        # probably OK to be categorized into '感染経路不明'
                        sub.attr('node', shape='circle', style='filled', color=color+'AA', fontcolor='white')
                        print(case.node_name, case.description, case.note)

                    if debug: # case number
                        sub.node(case.node_name, label=case.node_name.replace('aichi', 'A').replace('gifu', 'G'), fontname='Myriad Pro')
                    else: # age & city
                        sub.node(case.node_name, label=case.gv_label, fontname='Myriad Pro')

        self.gv_graph.edge('date', self.date_nodes[0], style='invis')

        for i in range(len(self.date_nodes) - 1):
            self.gv_graph.edge(self.date_nodes[i], self.date_nodes[i + 1], style='invis')

class TSVReader():
    def __init__(self):
        pass

    def make_cases(self, lines, pref):
        lines.reverse()

        cases = {}

        for line in lines:
            idx, date, description, note = line[:-1].split('\t')
            idx = int(idx.replace('例目', '')) # drop '例目’

            m, d = map(int, date.replace('月', '-').replace('日', '').split('-'))
            if (pref == 'gifu' and idx < 2293) or (pref == 'aichi' and idx < 16577):
                date = datetime.date.fromisoformat('2020-%02d-%02d' % (m, d))
            else:
                date = datetime.date.fromisoformat('2021-%02d-%02d' % (m, d))

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

            node_name = '%s%d' % (pref, idx)

            connected_nodes = []
            if note.find('愛知県内') >= 0: # has a traced route
                for split_txt in note.split('愛知県内')[1:]:
                    sources = split_txt.split('県内')[0].split('例目')
                    for source in sources:
                        try:
                            n = int(source.replace('・', '、').split('、')[-1].translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})))
                        except:
                            pass
                        else:
                            connected_nodes.append('aichi%d' % n)

            if note.find('岐阜県内') >= 0: # has a traced route
                sources = note.split('岐阜県内')[1].split('県内')[0].split('例目')
                for source in sources:
                    try:
                        n = int(source.split('、')[-1])
                    except:
                        pass
                    else:
                        connected_nodes.append('gifu%d' % n)

            if note in ('11月6日岐阜県公表のクラスターの関連から検査', '11月6日岐阜県内のクラスターの関連から検', '岐阜のクラスターの関連から検査', '11月6日の岐阜県クラスターの関連から検査'):
                connected_nodes.append('gifu708')
            elif note.find('11月6日の集団感染が発生した市内事業所の') >= 0 or note.find('11月6日岡崎市発表の集団感染が発生した市内事業所の') >= 0:
                connected_nodes.append('aichi6365')
            elif note.find('PUB「EDEN」関係の患者の濃厚接触者') >= 0:
                connected_nodes.append('aichi6111')
            elif note.find('外国人学校クラスター関連') >= 0:
                connected_nodes.append('gifu753')
            elif note.find('陽性者が発生した市内医療機関の関係者') >= 0:
                # Toyohashi
                connected_nodes.append('aichi13174')
            elif note.find('陽性者が発生した市内高齢者施設の関係者') >= 0:
                # Toyohashi
                connected_nodes.append('aichi13890')

            cases['%s%d' % (pref, idx)] = Case(age, city, node_name, note, date, description, connected_nodes)

        return cases

    def make_aichi_gifu_cases(self):
        cases = self.make_aichi_cases()
        cases.update(self.make_gifu_cases())
        return cases

    def make_aichi_cases(self):
        return self.make_cases(self.read_aichi_tsv(), 'aichi')

    def make_gifu_cases(self):
        return self.make_cases(self.read_gifu_tsv(), 'gifu')

    def read_aichi_tsv(self):
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

    def read_gifu_tsv(self):
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

class ROOTPlotter:
    def __init__(self, cases):
        ROOT.gStyle.SetOptStat(0)

        self.can = [ROOT.ExactSizeCanvas('can%d' % i, 'can%d' % i, 800, 600) for i in range(3)]

        t0 = ROOT.TDatime(2020, 7, 1, 0, 0, 0)
        nweeks = 28
        ndays = nweeks * 7
        dt = ndays * 3600 * 24

        self.h_aichi_wo_nagoya = ROOT.TH1D('h_aichi_wo_nagoya', ';Date;Number of Cases / Day', ndays, t0.Convert(), t0.Convert() + dt)
        self.h_nagoya = ROOT.TH1D('h_nagoya', ';Date;Number of Cases / Day', ndays, t0.Convert(), t0.Convert() + dt)
        self.h_gifu = ROOT.TH1D('h_gifu', ';Date;Number of Cases / Day', ndays, t0.Convert(), t0.Convert() + dt)

        self.h_traced = ROOT.TH1D('h_traced', ';Date;Number of Cases / Day', ndays, t0.Convert(), t0.Convert() + dt)
        self.h_untraced = ROOT.TH1D('h_untraced', ';Date;Number of Cases / Day', ndays, t0.Convert(), t0.Convert() + dt)

        self.h_age = ROOT.TH2D('h_age', ';Date;Age;Number of Cases / Day / Generation', ndays, t0.Convert(), t0.Convert() + dt, 11, 0, 110)
        self.h_age.GetXaxis().SetTimeDisplay(1)
        self.h_age.GetXaxis().SetTimeFormat('%b %d')
        self.h_age.GetXaxis().SetNdivisions(300 + int(ndays/7/3), 0)

        for case in cases.values():
            if case.node_name.find('dummy') == 0:
                continue

            date = case.date
            y, m, d = date.year, date.month, date.day
            t = ROOT.TDatime(y, m, d, 0, 0, 0)

            if case.node_name.find('aichi') == 0:
                if case.city == '名古屋市':
                    self.h_nagoya.Fill(t.Convert())
                else:
                    self.h_aichi_wo_nagoya.Fill(t.Convert())
            elif case.node_name.find('gifu') == 0:
                self.h_gifu.Fill(t.Convert())

            if len(case.connected_nodes) > 0 or case.note == 'あり':
                self.h_traced.Fill(t.Convert())
            else:
                self.h_untraced.Fill(t.Convert())

            age = case.age
            try:
                self.h_age.Fill(t.Convert(), age + 5 if age >= 10 else 5)
            except:
                print('Ignoring age ', age, ' of ', case.node_name)

        self.can[0].cd()
        self.h_age.Draw('colz')
        ROOT.gPad.SetRightMargin(0.15)
        ROOT.gPad.Update()
        pal = ROOT.gPad.GetPrimitive('palette')
        pal.SetX1NDC(0.86)
        pal.SetX2NDC(0.91)

        self.px_age = self.h_age.ProfileX('px_age')
        self.px_age.SetLineColor(2)
        self.px_age.SetLineWidth(3)
        self.px_age.Draw('same e')

        self.can[1].cd()
        self.can[1].SetGridx()
        self.can[1].SetGridy()
        self.h_aichi_wo_nagoya.SetFillColorAlpha(2, 0.5)
        self.h_nagoya.SetFillColorAlpha(5, 0.5)
        self.h_gifu.SetFillColorAlpha(4, 0.5)
        self.stack = ROOT.THStack('stack', '')
        self.stack.Add(self.h_aichi_wo_nagoya)
        self.stack.Add(self.h_nagoya)
        self.stack.Add(self.h_gifu)
        self.stack.Draw()
        self.can[1].Modified()
        self.stack.GetXaxis().SetTimeDisplay(1)
        self.stack.GetXaxis().SetTimeFormat('%b %d')
        self.stack.GetXaxis().SetNdivisions(300 + int(ndays/7/3), 0)
        self.stack.GetYaxis().SetNdivisions(110, 1)
        self.stack.SetTitle(';Date;Number of Cases / Day')

        self.leg = ROOT.TLegend(0.4, 0.7, 0.75, 0.85)
        self.leg.AddEntry(self.h_gifu, 'Gifu', 'f')
        self.leg.AddEntry(self.h_nagoya, 'Aichi (Nagoya)', 'f')
        self.leg.AddEntry(self.h_aichi_wo_nagoya, 'Aichi (Other)', 'f')
        self.leg.SetFillStyle(0)
        self.leg.Draw()

        self.can[2].cd()
        self.can[2].SetGridx()
        self.can[2].SetGridy()
        self.h_traced.SetFillColorAlpha(1, 0.2)
        self.h_untraced.SetFillColorAlpha(1, 0.7)
        self.stack2 = ROOT.THStack('stack2', '')
        self.stack2.Add(self.h_untraced)
        self.stack2.Add(self.h_traced)
        self.stack2.Draw()
        self.can[2].Modified()
        self.stack2.GetXaxis().SetTimeDisplay(1)
        self.stack2.GetXaxis().SetTimeFormat('%b %d')
        self.stack2.GetXaxis().SetNdivisions(300 + int(ndays/7/3), 0)
        self.stack2.GetYaxis().SetNdivisions(110, 1)
        self.stack2.SetTitle(';Date;Number of Cases / Day')

        self.leg2 = ROOT.TLegend(0.3, 0.65, 0.8, 0.85)
        self.leg2.AddEntry(self.h_traced, 'Traced Infection Source', 'f')
        self.leg2.AddEntry(self.h_untraced, 'Unknown Source', 'f')
        self.leg2.SetFillStyle(0)
        self.leg2.Draw()

def main():
    global plotter
    '''
    reader = TSVReader()
    cases = reader.make_aichi_gifu_cases()
    plotter = ROOTPlotter(cases)

    reader = TSVReader()
    cases = reader.make_aichi_cases()
    cases.update(reader.make_gifu_cases())
    case_graph_aichi = CaseGraph('Aichi')
    case_graph_aichi.add_only_aichi_cases(cases)
    case_graph_aichi.gv_graph.view()
    '''
    reader = TSVReader()
    cases = reader.make_aichi_gifu_cases()
    case_graph_gifu = CaseGraph('Gifu')
    case_graph_gifu.add_only_gifu_cases(cases)
    case_graph_gifu.gv_graph.view()


def before_2020Nov(date):
    return str(date)[:-3] in ('2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06', '2020-07', '2020-08', '2020-09', '2020-10')

if __name__ == '__main__':
    main()
