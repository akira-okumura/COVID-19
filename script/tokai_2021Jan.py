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
    '岐阜県事例と接触', '豊田市事例と接触', '名古屋市事例の濃厚接触者', '岡崎市事例と接触',
    '陽性者が発生した市内事業所の関係者',
    '陽性者が発生した市内寮の関係者',
    '本日発表のクラスター発生施設の職員', '本日発表のクラスター発生施設の利用者')

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
    '長崎県事例と接触', '長野県事例と接触', '岡山県事例と接触', '北海道事例と接触',
    '静岡県発表2613', '京都府事例と接触', '神奈川県事例と接触', '埼玉県事例と接触',
    '千葉県事例と接触', '三重県陽性者の濃厚接触者（友人）', '神奈川県の患者の濃厚接触者',
    '和歌山県事例と接触', '群馬県事例と接触', '福岡県事例と接触', '静岡県発表2900', '和歌山県事例と接触',
    '静岡県発表2979', '横浜市陽性者の接触者', '福岡県陽性者の接触者（親族）', '兵庫県陽性者の濃厚接触者',
    '静岡県事例と接触', '兵庫県事例と接触', '栃木県事例と接触', '静岡県事例の濃厚接触者',
    '福岡市発表6116', '佐世保市157,158', '福井県陽性者の濃厚接触者', '広島県事例と接触', '長野県事例と接触',
    '沖縄県事例と接触', '三重県陽性者の接触者', '茨城県事例と接触', '石川県事例の濃厚接触者',
    '宮崎県事例と接触', '鹿児島県事例の濃厚接触者', '大阪府事例の濃厚接触者', '福岡市事例と接触',
    '沖縄県陽性者の接触者（友人）', '和歌山県陽性者の濃厚接触者（友人）', '静岡県陽性者の接触者',
    '三重県陽性者の濃厚接触者（親族）', '沖縄県陽性者の濃厚接触者（友人）', '県外77の濃厚接触者（家族）',
    '県外78の濃厚接触者（家族）', '県外73の濃厚接触者（家族）', '県外74の濃厚接触者（友人）',
    '県外69の濃厚接触者（家族）', '東京都陽性者の接触者')

# 再感染
repos_dict = {'aichi19770': 'aichi15172',
              'aichi20403': 'aichi15384',
              'aichi21078': 'aichi13970',
              'aichi21939': 'aichi18198'}

from enum import Enum

class ContactCategory(Enum):
    FOREIGN_ROUTE = 0
    AICHI_GIFU = 1
    UNKNOWN = 2
    NON_AICHI_GIFU = 3
    NON_AICHI_GIFU_UNKNOWN = 4

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
        self.set_contact_category()

    def set_contact_category(self):
        if self.has_foreign_route():
            self.contact_category = ContactCategory.FOREIGN_ROUTE
        elif self.note.find('感染経路不明') >= 0 or self.node_name in ('gifu79', 'aichi662', 'aichi661'):
            self.contact_category = ContactCategory.UNKNOWN
        elif len([x for x in non_aichi_gifu_contact_tuple if self.note.find(x) >= 0]) > 0 or \
             self.node_name in ('aichi10002', 'aichi10003') or \
             self.node_name in ('aichi1220', 'aichi1414') or \
             self.node_name in repos_dict.keys():
            self.contact_category = ContactCategory.NON_AICHI_GIFU
        elif self.node_name not in ('aichi1402', 'aichi1435', 'aichi1722', 'aichi3768', 'aichi3775') and \
             (len([x for x in aichi_gifu_contact_tuple if self.note.find(x) >= 0]) > 0 or \
              self.note == 'あり' or \
              self.node_name == 'gifu151' or \
              self.node_name == 'aichi521' or \
              self.node_name in ('gifu210', 'gifu211', 'gifu215', 'gifu216')): # 7/24 Gifu cases not reflected in CTV data
            self.contact_category = ContactCategory.AICHI_GIFU
        elif self.node_name in ('aichi547') or \
             len([x for x in ('滞在', '東京都から名古屋市へ移動', '8月13日～16日に大阪府に滞在', '9月25日まで神奈川県居住', '7月30日～8月10日に青森県、岩手県、宮城県、福島県、秋田県に滞在', '8月18日まで静岡県に在住', '9月12日から名古屋市に滞在', '6月15~16日神奈川県、6月19~21日東京を訪問') if self.note.find(x) >= 0]) > 0 or \
             (self.node_name in ('aichi918', 'aichi925', 'aichi939') or # 7/24 Nagoya cases not reflected in CTV data
              self.node_name in ('aichi998',)): # 7/25 Nagoya cases not reflected in CTV data '7/9〜7/10に大阪府滞在'
            self.contact_category = ContactCategory.NON_AICHI_GIFU_UNKNOWN
        else:
            # probably OK to be categorized into '感染経路不明'
            self.contact_category = ContactCategory.UNKNOWN
            if self.note != ' ':
                print(self.node_name, self.description, self.note)

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
        foreign_tuple = ('11月10日に南アフリカ共和国から入国', '11月21日にパキスタンから帰国',
                         '11月27日アメリカから帰国', '12月3日ポルトガルから帰国',
                         '12月6日にロシアより入国', '12月1日海外から入国',
                         '航空機近席に感染者あり', 'フィリピン', 'インドネシア', 'バーレーン',
                         'メキシコ', 'タイ', 'ハンガリー')

        if self.note.find('帰国') >= 0 or \
           self.description.find('中国籍') >= 0 or \
           self.description.find('帰国') >= 0 or \
           self.description.find('10月17日にイタリアから入国') >= 0 or \
           len([x for x in foreign_tuple if self.note.find(x) >= 0]) > 0 or \
           (self.note.find('渡航歴') >= 0 and self.note.find('家族がパキスタン渡航歴あり') < 0):
            return True
        else:
            return False

class CaseGraph:
    def __init__(self, fname):
        self.gv_graph = graphviz.Graph(engine='dot', filename=fname)
        self.gv_graph.attr('node', fontname='Hiragino UD Sans F StdN', fontsize='14')
        self.gv_graph.attr('edge', arrowhead='normal', arrowsize='0.5', dir='both')
        self.gv_graph.attr(nodesep='0.1', ranksep='0.12')
        self.gv_graph.graph_attr['rankdir'] = 'LR'

        self.nx_graph = nx.path_graph(0)

    def add_cases(self, cases, pref=None, cluster_thd=1):
        for case in cases.values():
            for node in case.connected_nodes:
                cases[node].is_connected = True

        self.make_nx_nodes(cases)

        self.make_pref_selection(cases, pref, cluster_thd)

        self.make_gv_date_rank_ditc(cases, pref)
        self.make_gv_caption()
        self.make_gv_date_nodes()
        self.make_gv_edges(cases)
        self.make_gv_notes()

    def add_only_aichi_returning_cases(self, cases):
        for case in cases.values():
            for node in case.connected_nodes:
                cases[node].is_connected = True

        self.make_nx_nodes(cases)

        # make clusters from the NetworkX graph
        for comp in nx.connected_components(self.nx_graph):
            subgraph = self.nx_graph.subgraph(comp).copy()
            node_names = subgraph.nodes
            
            # check if the cluster has any non Aichi, Gifu, Mie cases
            '''
            if len([x for x in node_names if (cases[x].city not in ('愛知県', '岐阜県', '三重県') and cases[x].city[-1] in ('都', '道', '府', '県'))]) == 0 and \
               len([x for x in node_names if cases[x].contact_category in (ContactCategory.NON_AICHI_GIFU, ContactCategory.NON_AICHI_GIFU_UNKNOWN)]) == 0:
            '''
            if len([x for x in node_names if (cases[x].city not in ('愛知県', '岐阜県', '三重県') and cases[x].city[-1] in ('都', '道', '府', '県'))]) == 0:
                for node_name in node_names:
                    cases.pop(node_name)

            # Remove remaining large clusters
            if len([x for x in node_names if x in ('gifu1603', 'aichi13326', 'aichi13504', 'aichi12324')]) > 0:
                for node_name in node_names:
                    cases.pop(node_name)

        self.make_gv_date_rank_ditc(cases, 'aichi')
        self.make_gv_caption()
        self.make_gv_date_nodes()
        self.make_gv_edges(cases)
        self.make_gv_notes()

    def add_only_aichi_20s_cases(self, cases):
        for case in cases.values():
            for node in case.connected_nodes:
                cases[node].is_connected = True

        self.make_nx_nodes(cases)

        # make clusters from the NetworkX graph
        for comp in nx.connected_components(self.nx_graph):
            subgraph = self.nx_graph.subgraph(comp).copy()
            node_names = subgraph.nodes
            
            # check if the cluster has any non Aichi, Gifu, Mie cases
            if len([x for x in node_names if cases[x].age == 20]) == 0:
                for node_name in node_names:
                    cases.pop(node_name)

            # Remove remaining large clusters
            if len([x for x in node_names if x in ('gifu1603', 'aichi13326', 'aichi13504', 'aichi12324')]) > 0:
                for node_name in node_names:
                    cases.pop(node_name)

        self.make_gv_date_rank_ditc(cases, 'aichi')
        self.make_gv_caption()
        self.make_gv_date_nodes()
        self.make_gv_edges(cases)
        self.make_gv_notes()

    def add_only_aichi_kids_cases(self, cases):
        for case in cases.values():
            for node in case.connected_nodes:
                cases[node].is_connected = True

        self.make_nx_nodes(cases)

        # make clusters from the NetworkX graph
        for comp in nx.connected_components(self.nx_graph):
            subgraph = self.nx_graph.subgraph(comp).copy()
            node_names = subgraph.nodes
            
            # Remove clusters not containing < 10 year cases
            if len([x for x in node_names if cases[x].age != None and cases[x].age < 10]) == 0:
                for node_name in node_names:
                    cases.pop(node_name)

            # Remove remaining large clusters
            #if len([x for x in node_names if x in ('gifu1603', 'aichi13326', 'aichi13504', 'aichi12324')]) > 0:
            #    for node_name in node_names:
            #        cases.pop(node_name)

        self.make_gv_date_rank_ditc(cases, 'aichi')
        self.make_gv_caption()
        self.make_gv_date_nodes()
        self.make_gv_edges(cases)
        self.make_gv_notes()

    def add_only_aichi_cases(self, cases, cluster_thd=1):
        self.add_cases(cases, 'aichi', cluster_thd)

    def add_only_gifu_cases(self, cases, cluster_thd=1):
        self.add_cases(cases, 'gifu', cluster_thd)

    def make_nx_nodes(self, cases):
        for case in sorted(cases.values(), key=lambda x:x.date):
            self.nx_graph.add_node(case.node_name)
            for node in case.connected_nodes:
                self.nx_graph.add_edge(case.node_name, node)

    def make_pref_selection(self, cases, pref=None, cluster_thd=1):
        if pref == None:
            return

        # make clusters from the NetworkX graph
        for comp in nx.connected_components(self.nx_graph):
            subgraph = self.nx_graph.subgraph(comp).copy()
            node_names = subgraph.nodes

            # remove small clusters or single cases
            if len(subgraph) < cluster_thd:
                for node_name in node_names:
                    cases.pop(node_name)
                continue

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
                 ('gifu1086', '岐阜協立大学\n男子バレーボール部'), ('gifu1559', '岐南町\n障碍者福祉施設'), ('gifu1673', '本巣市\n職場'),
                 ('gifu2106', '本巣郡北方町\nGAS PANIC（接待）'), ('gifu1924', '岐阜市折立\nオイコットクラブ（接待）'), ('gifu1950', '朝日大学\n運動部'),
                 ('gifu1783', '可児市\nスターダストフィリピンクラブ'), ('gifu1930', '羽島市\n入所型高齢者福祉施設'), ('gifu2193', '複数大学の飲食'),
                 ('gifu1377', '羽島市\n職場関連'), ('gifu2250', '岐阜市\n高齢者福祉施設'), ('gifu2079', '会食'),
                 ('gifu2108', '親族の会食'), ('gifu1857', '可児郵便局'), ('gifu1254', '帝京大可児高校'),
                 ('gifu1134', 'さわやかナーシング\n可児デイサービスセンター'), ('gifu1206', '複数の飲食店'), ('gifu1887', '各務原市\n職場'),
                 ('gifu1256', '岐阜協立大\nサッカー部（飲食）'), ('gifu1243', '不破郡垂井町\n不破高校'), ('gifu1257', '飲食店会食\nから親族へ'),
                 ('gifu956', '揖斐郡池田町\nイビデン樹脂'), ('gifu1662', '海津市\n学童保育'), ('gifu1253', '高山市\n久美愛厚生病院'),
                 ('gifu1152', '親族'), ('gifu2440', '居酒屋・カラオケ'),
                 ('gifu2491', '各務原市\nデイサービスセンター\n岐阜市\n県総合医療センター'), ('gifu2447', '会食'),
                 ('gifu2250', '岐阜市\n高齢者福祉施設'), ('gifu2593', '関市\n事業所'),
                 ('gifu2356', '会食'), ('gifu2604', '会食'), ('gifu2595', '親族会食'), ('gifu2655', '海津市\n事業所'),
                 ('gifu2739', '家族'),
                 ('gifu2740', '職場'), # 3 つの飲食店クラスター? 人数足りない
                 ('gifu2882', '職場\n年始パーティー'),
                 ('gifu3197', '高山西高校運動部'), ('gifu3095', '職場'),
                 ('gifu3125', '山県市\nショートステイ\nデイサービスセンター'),
                 ('gifu3622', '岐阜市\n介護老人保健施設'),
                 ('gifu3676', '職場・家族'),
                 ('gifu3704', '会食'),
                 ('gifu3442', '岐阜市\nデイサービスセンター'),
                 ('gifu3135', '関市\n中濃厚生病院'),
                 ('gifu3558', '親族飲食・職場'),
                 ('gifu3305', '岐阜市\n清流病院'),
                 ('gifu3297', '美濃市\nデイサービス'),
                 ('gifu3502', '家族'),
                 ('gifuX', ''))
        notes += (('aichi6365', '岡崎市\n高齢者施設'),
                  ('aichi7301', '名古屋市\n高齢者施設'),
                  ('aichi8406', '名古屋市\n地域活動グループなど'),
                  ('aichi9161', '医療・高齢者施設\n（3A）'), # confirmed
                  ('aichi10826', '幸田町\n京ヶ峰岡田病院\n（3B）'), # confirmed
                  ('aichi11540', '豊川市民病院\n（3C）'), # confirmed
                  ('aichi10681', '名古屋市\n繁華街の飲食店\n（3D）'), # confirmed
                  ('aichi11028', '名古屋市\n保育施設\n（3E）'), # confirmed
                  ('aichi11043', '豊川市\n病院\n（3F）'), # confirmed
                  ('aichi12093', '保育施設・学校\n（3G）'), # confirmed
                  ('aichi11818', '医療・高齢者施設\n（3H）'), # confirmed
                  ('aichi12583', '職場（3I）'), # confirmed (30 = 32 - 2 Gifu)
                  ('aichi12324', '医療・高齢者施設\n（3J）'), # confirmed (1 common case in 3R?)
                  ('aichi11946', '医療・高齢者施設\n（3K）'), # confirmed (all 12 cases as of Jan 5)
                  ('aichi12868', '藤田医科大学\n学生\n（3L）'), # confirmed
                  ('aichi13326', '春日井市民病院\n（3M）'), # confirmed
                  ('aichi13541', 'クラブチーム\n（3N）'), # confirmed
                  ('aichi12495', '医療・高齢者施設\n（3O?）'), # ? 44 cases as of Jan 5, but official says 33 (Jan 5 and 8)
                  ('aichiX', '医療・高齢者施設\n（3P?）'),  # 23 as of Jan 5 and 8
                  ('aichi12615', '医療・高齢者施設\n（3Q）'), # 23 as of Jan 5 (碧南?)
                  ('aichi13504', '名古屋市\n障碍者施設\n（3R）'), # confirmed
                  ('aichi13623', '碧南市\n看護ステーション（3Q?）'), # 17 cases as of Jan 5
                  ('aichi12834', '船舶\n（3S）'),  # confirmed
                  ('aichi14892', '高齢者施設\n（3T）'), # confirmed
                  ('aichi13191', '医療・高齢者施設\n（3U）'), # confirmed
                  ('aichi14725', '弥富市\n海南病院\n（3V）'), # confirmed
                  ('aichi14370', '職場（3W）'), # confirmed (count 18 direct cases only as of Jan 5)
                  ('aichi13174', '豊橋市\n医療施設'), # 23 as of Jan 5
                  ('aichiX', '医療・高齢者施設等\n（3X）'), # 20 as of Jan 5
                  ('aichi14408', '名古屋市\n名古屋記念病院\n（3Y）'), # confirmed
                  ('aichi14683', '瀬戸市\nあさい病院\n（3Z）'), # confirmed
                  ('aichi13890', '豊橋市\n高齢者施設\n（4A）'), # confirmed
                  ('aichi14219', '医療・高齢者施設等\n（4B）'), # confirmed
                  ('aichi15147', '医療・高齢者施設等\n（4C）'), # confirmed
                  ('aichi16036', '職場（4D）'), ('aichi16039', '職場（4D）'),
                  ('aichi15111', '福祉施設\n（4E）'), # confirmed
                  ('aichi16822', '名古屋市\n東部医療センター\n（4F）'), # confirmed
                  ('aichi14284', '医療・高齢者施設等\n（4G）'), # confirmed
                  ('aichi14219', '高齢者施設\n（4H）'), # confirmed
                  ('aichi15955', '医療・高齢者施設\n（4I）'), # 25 as of Jan 8, 26 as of Jan 12
                  ('aichi18323', '会食\n（4J）'), # confirmed
                  ('aichi18776', 'トヨタ自動車ヴェルブリッツ\nラグビーチーム\n（4K）'), # 13 as of Jan 11
                  ('aichi19047', '医療・高齢者施設等（4L）'), # confirmed
                  ('aichi18942', '年末年始親族'),
                  ('aichi19003', '愛知県警警察学校（4M）'),
                  ('aichiX', '医療・高齢者施設\n（4N）'), # 12 as of Jan 17
                  ('aichiX', 'クラブチーム（4O）'), # 10 as of Jan 17
                  ('aichi18959', '豊橋市\n東部環境センター\n（4P）'), # confirmed
                  ('aichi20230', '豊田市\n医療機関（4Q）'), # confirmed
                  ('aichiX', '飲食店（4R）'), # 9 as of Jan 23
                  ('aichi21152', '大府市\n保育施設'),
                  ('aichi21557', '医療・高齢者施設等（4S）'), # confirmed
                  ('aichi21342', '大府市\n成人式二次会（4T）'), # confirmed
                  ('aichi21601', '名古屋市\n職場（4U）'), # confirmed
                  ('aichi21837', '岡崎市\n高齢者施設（4V）'), # confirmed
                  ('aichiX', '医療・高齢者施設等（4W）'), # 11 as of Jan 23
                  ('aichi22861', '医療・高齢者施設等（4X）'), # confirmed
                  ('aichi21591', '豊橋市\n寮（4Y）'), # confirmed
                  ('aichi21617', '名古屋市\n保育園（4Z）'), # confirmed
                  ('aichi18725', '医療・高齢者施設等（5A?）'), # 18 as of Jan 23, 0 Jan 22
                  ('aichi21620', '医療・高齢者施設等（5B?）'), # 11 as of Jan 23, 0 Jan 22
                  ('aichiX', ''),
                  ('aichiX', ''))
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

                    if case.contact_category == ContactCategory.FOREIGN_ROUTE:
                        sub.attr('node', shape='circle', style='', color=color, fontcolor='black')
                    elif case.contact_category == ContactCategory.UNKNOWN:
                        sub.attr('node', shape='circle', style='filled', color=color+'AA', fontcolor='white')
                    elif case.contact_category == ContactCategory.NON_AICHI_GIFU:
                        sub.attr('node', shape='tripleoctagon', style='', color=color, fontcolor='black')
                    elif case.contact_category == ContactCategory.AICHI_GIFU:
                        sub.attr('node', shape='square', style='', color=color, fontcolor='black')
                    elif case.contact_category == ContactCategory.NON_AICHI_GIFU_UNKNOWN:
                        sub.attr('node', shape='tripleoctagon', style='filled', color=color+'AA', fontcolor='white')

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
            elif note.find('陽性者が発生した市内事業所の関係者') >= 0:
                # Toyohashi
                connected_nodes.append('aichi18959')
            elif note.find('陽性者が発生した市内寮の関係者') >= 0:
                connected_nodes.append('aichi21591') # Toyohashi 705
            elif note.find('本日発表のクラスター発生施設の') >= 0:
                connected_nodes.append('aichi21837') # Okazaki
                # where is Okazaki 1/20 cluster
            elif node_name in repos_dict.keys():
                # 再感染
                connected_nodes.append(repos_dict[node_name])

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

        t0 = ROOT.TDatime(2020, 7, 1, 0, 0, 0).Convert()
        nweeks = 32
        ndays = nweeks * 7
        dt = ndays * 3600 * 24
        t1 = t0 + dt

        self.h_aichi_wo_nagoya = ROOT.TH1D('h_aichi_wo_nagoya', ';Date;Number of Cases / Day', ndays, t0, t1)
        self.h_nagoya = ROOT.TH1D('h_nagoya', ';Date;Number of Cases / Day', ndays, t0, t1)
        self.h_gifu = ROOT.TH1D('h_gifu', ';Date;Number of Cases / Day', ndays, t0, t1)

        self.h_traced = ROOT.TH1D('h_traced', ';Date;Number of Cases / Day', ndays, t0, t1)
        self.h_untraced = ROOT.TH1D('h_untraced', ';Date;Number of Cases / Day', ndays, t0, t1)

        self.h_age = ROOT.TH2D('h_age', ';Date;Age;Number of Cases / Day / Generation', ndays, t0, t1, 11, 0, 110)
        self.h_age.GetXaxis().SetTimeDisplay(1)
        self.h_age.GetXaxis().SetTimeFormat('%b %d')
        self.h_age.GetXaxis().SetNdivisions(300 + int(ndays/7/4), 0)

        max_bin = 0
        for case in cases.values():
            if case.node_name.find('dummy') == 0:
                continue

            date = case.date
            y, m, d = date.year, date.month, date.day
            t = ROOT.TDatime(y, m, d, 0, 0, 0).Convert()

            b = self.h_nagoya.FindBin(t)
            if b > max_bin:
                max_bin = b

            if case.node_name.find('aichi') == 0:
                if case.city == '名古屋市':
                    self.h_nagoya.Fill(t)
                else:
                    self.h_aichi_wo_nagoya.Fill(t)
            elif case.node_name.find('gifu') == 0:
                self.h_gifu.Fill(t)

            if len(case.connected_nodes) > 0 or case.note == 'あり':
                self.h_traced.Fill(t)
            else:
                self.h_untraced.Fill(t)

            age = case.age
            try:
                self.h_age.Fill(t, age + 5 if age >= 10 else 5)
            except:
                print('Ignoring age ', age, ' of ', case.node_name)

        # make 7-day average
        self.stack_ave7 = ROOT.THStack('stack_ave7', '')
        self.h_ave7 = []
        self.g_ave7 = []
        for hi, h in enumerate((self.h_aichi_wo_nagoya, self.h_nagoya, self.h_gifu)):
            self.h_ave7.append(h.Clone('%s_ave7' % h.GetName()))
            self.h_ave7[-1].Reset()
            self.h_ave7[-1].SetFillStyle(0)
            self.h_ave7[-1].SetFillColor(0)
            self.h_ave7[-1].SetLineColor(h.GetFillColor())
            for i in range(1, max_bin + 1):
                for j in range(7):
                    b = i + j
                    if b <= max_bin:
                        t = h.GetBinCenter(b)
                        self.h_ave7[-1].Fill(t, h.GetBinContent(i))

            self.h_ave7[-1].Scale(1/7.)
            self.stack_ave7.Add(self.h_ave7[-1])

            self.g_ave7.append(ROOT.TGraph())
            for i in range(1, max_bin + 1):
                counts = 0
                for h in self.h_ave7:
                    counts += h.GetBinContent(i)

                self.g_ave7[-1].SetPoint(i - 1, self.h_nagoya.GetBinCenter(i), counts)

            self.g_ave7[-1].SetLineColor((2, 5, 4)[hi])
            self.g_ave7[-1].SetLineWidth(2)

        n1 = int(ROOT.h_aichi_wo_nagoya.GetBinContent(max_bin) + ROOT.h_nagoya.GetBinContent(max_bin))
        n2 = int(ROOT.h_nagoya.GetBinContent(max_bin))
        n3 = int(ROOT.h_gifu.GetBinContent(max_bin))
        print(f'愛知県 {n1} 名（うち名古屋市 {n2}）、岐阜県 {n3} 名')

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
        for h in (self.h_aichi_wo_nagoya, self.h_nagoya, self.h_gifu):
            self.stack.Add(h)
        self.stack.Draw()

        #self.stack_ave7.Draw('hist c same')
        for g in self.g_ave7:
            g.Draw('c same')
        self.can[1].Modified()
        self.stack.GetXaxis().SetTimeDisplay(1)
        self.stack.GetXaxis().SetTimeFormat('%b %d')
        self.stack.GetXaxis().SetNdivisions(300 + int(ndays/7/4), 0)
        self.stack.GetYaxis().SetNdivisions(110, 1)
        self.stack.SetTitle(';Date;Number of Cases / Day')

        self.leg = ROOT.TLegend(0.25, 0.7, 0.75, 0.85)
        self.leg.AddEntry(self.h_gifu, 'Gifu', 'f')
        self.leg.AddEntry(self.g_ave7[2], 'Seven-day Average', 'l')
        self.leg.AddEntry(self.h_nagoya, 'Aichi (Nagoya)', 'f')
        self.leg.AddEntry(self.g_ave7[1], '', 'l')
        self.leg.AddEntry(self.h_aichi_wo_nagoya, 'Aichi (Other)', 'f')
        self.leg.AddEntry(self.g_ave7[0], '', 'l')
        self.leg.SetNColumns(2)
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
        self.stack2.GetXaxis().SetNdivisions(300 + int(ndays/7/4), 0)
        self.stack2.GetYaxis().SetNdivisions(110, 1)
        self.stack2.SetTitle(';Date;Number of Cases / Day')

        self.leg2 = ROOT.TLegend(0.3, 0.65, 0.8, 0.85)
        self.leg2.AddEntry(self.h_traced, 'Traced Infection Source', 'f')
        self.leg2.AddEntry(self.h_untraced, 'Unknown Source', 'f')
        self.leg2.SetFillStyle(0)
        self.leg2.Draw()

def link_nodes(case_graph):
    link_cases = lambda a, b : case_graph.gv_graph.edge(a, b, style='invis')
    link_cases('aichi13623', 'aichi12615') # cluster 3Q?
    for i in range(16036, 16039):
        link_cases(f'aichi{i}', f'aichi{i + 1}') # cluster 4D?

def main():
    global plotter

    reader = TSVReader()
    cases = reader.make_aichi_gifu_cases()
    plotter = ROOTPlotter(cases)
    '''
    reader = TSVReader()
    cases = reader.make_aichi_gifu_cases()
    case_graph_aichi = CaseGraph('Aichi_kids')
    case_graph_aichi.add_only_aichi_kids_cases(cases)
    case_graph_aichi.gv_graph.view()

    reader = TSVReader()
    cases = reader.make_aichi_gifu_cases()
    case_graph_aichi = CaseGraph('Aichi_returning')
    case_graph_aichi.add_only_aichi_returning_cases(cases)
    case_graph_aichi.gv_graph.view()

    reader = TSVReader()
    cases = reader.make_aichi_gifu_cases()
    case_graph_aichi = CaseGraph('Aichi_20s')
    case_graph_aichi.add_only_aichi_20s_cases(cases)
    case_graph_aichi.gv_graph.view()

    reader = TSVReader()
    cases = reader.make_aichi_cases()
    cases.update(reader.make_gifu_cases())
    case_graph_aichi = CaseGraph('Aichi_cluster')
    case_graph_aichi.add_only_aichi_cases(cases, 10)
    link_nodes(case_graph_aichi)
    case_graph_aichi.gv_graph.view()
    '''
    reader = TSVReader()
    cases = reader.make_aichi_cases()
    cases.update(reader.make_gifu_cases())
    case_graph_aichi = CaseGraph('Aichi')
    case_graph_aichi.add_only_aichi_cases(cases, 1)
    link_nodes(case_graph_aichi)
    case_graph_aichi.gv_graph.view()
    '''
    reader = TSVReader()
    cases = reader.make_aichi_gifu_cases()
    case_graph_gifu = CaseGraph('Gifu')
    case_graph_gifu.add_only_gifu_cases(cases, 1)
    case_graph_gifu.gv_graph.view()
    '''
def before_2020Nov(date):
    return str(date)[:-3] in ('2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06', '2020-07', '2020-08', '2020-09', '2020-10')

if __name__ == '__main__':
    main()
