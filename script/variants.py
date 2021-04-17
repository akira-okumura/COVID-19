import graphviz
import datetime
import re
import networkx as nx

debug = False
#debug = True

from enum import Enum

class ContactCategory(Enum):
    FOREIGN_ROUTE = 0
    AICHI_GIFU = 1
    UNKNOWN = 2
    NON_AICHI_GIFU = 3
    NON_AICHI_GIFU_UNKNOWN = 4

class Case:
    def __init__(self, node_name, age, sex, city, note, date, variant_type, connected_nodes):
        self.age = age
        self.sex = sex
        self.date = date
        self.city = city
        self.node_name = node_name
        self.note = note
        self.variant_type = variant_type
        self.is_connected = False
        self.connected_nodes = connected_nodes
        self.make_gv_label()
        self.set_contact_category()

    def set_contact_category(self):
        if self.has_foreign_route():
            self.contact_category = ContactCategory.FOREIGN_ROUTE
        elif self.note.find('岐阜県事例との接触あり') >= 0:
            self.contact_category = ContactCategory.AICHI_GIFU
        elif self.note.find('との接触あり') >= 0 or self.note.find('の関係者') >= 0:
            self.contact_category = ContactCategory.AICHI_GIFU
        else:
            self.contact_category = ContactCategory.UNKNOWN

    def make_gv_label(self):
        if self.age == None:
            self.gv_label = ''
        elif self.age == '10未満' or self.age == '10歳未満':
            self.gv_label = '<10歳'
        elif self.age in ('10', '20', '30', '40', '50', '60', '70', '80', '90'):
            self.gv_label = self.age + '代'
        else:
            self.gv_label = '%d代' % self.age

        self.gv_label += '\n' + self.variant_type.replace('南アフリカ', '南ア').replace('英国型', '英国')

    def is_male(self):
        return True if self.sex == '男' else False

    def is_fmale(self):
        return True if self.sex == '女' else False

    def is_unknown_sex(self):
        return True if (not self.is_male()) and (not self.is_female()) else False

    def has_foreign_route(self):
        if self.note.find('海外滞在歴あり') >= 0 or self.note.find('海外渡航歴あり') >= 0:
            return True
        else:
            return False

class CaseGraph:
    def __init__(self, fname):
        self.gv_graph = graphviz.Graph(engine='dot', filename=fname)
        self.gv_graph.attr('node', fontname='Hiragino UD Sans F StdN', fontsize='12')
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
        notes = (('gifuX', ''),
                 ('gifuX', ''),
                 ('gifuX', ''),
                 ('gifuX', ''))
        notes += (('aichiX', ''),)

        for note in notes:
            if source.find(note[0]) >= 0:
                self.gv_graph.node('%s_caption' % note[0], label=note[1], shape='plaintext', fixedsize='1', width='0.5', height='0.5', fontsize='12')
                self.gv_graph.edge(note[0], '%s_caption' % note[0], style='dashed', color='gray', arrowhead='odot')

    def make_gv_edges(self, cases):
        for case in cases.values():
            if before_2021(case.date):
                continue
            if len(case.connected_nodes) > 0:
                node_name = case.node_name
                for node in case.connected_nodes:
                    source_node_name = cases[node].node_name
                    if before_2021(cases[node].date):
                        continue
                    self.gv_graph.edge(source_node_name, node_name)

    def make_gv_date_rank_ditc(self, cases, pref=None):
        '''
        Makes a date rank dictionary for later graphvis use.
        Each date rank holds all the cases reported on that day.
        '''
        self.date_ranks = {} # stores all cases date by date
        for case in sorted(cases.values(), key=lambda x:x.date):
            date = case.date
            if before_2021(case.date):
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
                if d == 1:
                    label = '%d月\n上旬' % m
                elif d == 11:
                    label = '%d月\n中旬' % m
                elif d == 21:
                    label = '%d月\n下旬' % m
                if d == 1:
                    sub.node('date%s' % date, label=label, shape='plaintext', fontsize='16')
                else:
                    sub.node('date%s' % date, label=label, shape='plaintext', fontsize='16')
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
                        sub.node(case.node_name, label=case.gv_label + '\n' + case.node_name.replace('aichi', 'A').replace('gifu', 'G'), fontname='Myriad Pro')
                    else: # age & city
                        sub.node(case.node_name, label=case.gv_label, fontname='Myriad Pro')

        for i in range(len(self.date_nodes) - 1):
            self.gv_graph.edge(self.date_nodes[i], self.date_nodes[i + 1], style='invis')

class TSVReader():
    def __init__(self):
        pass

    def make_cases(self, pref):
        cases = {}
        if pref == 'aichi':
            lines = open('CTV/Aichi_variants.tsv').readlines()[1:]
            for line in lines:
                try:
                    idx, age, sex, city, pos_date, status, variant_type, note = line[:-1].split('\t')
                except:
                    print(line)
                    raise
                idx = int(idx)
                node_name = '%s%d' % (pref, idx)

                if note.find('との接触あり') >= 0:
                    print(note)
                    if note.find('岐阜県事例との接触あり') >= 0:
                        pass
                    else:
                        connected_nodes = ['aichi%d' % int(re.sub('・No.(\d*)との接触あり', '***\\1***', note).split('***')[1])]
                else:
                    connected_nodes = []

                m = int(pos_date.split('月')[0])
                if pos_date.find('上旬') >= 0:
                    d = 1
                elif pos_date.find('中旬') >= 0:
                    d = 11
                else:
                    d = 21
                date = datetime.date.fromisoformat('2021-%02d-%02d' % (m, d))

                cases[node_name] = Case(node_name, age, sex, city, note, date, variant_type, connected_nodes)

        elif pref == 'gifu':
            lines = open('CTV/Gifu_variants.tsv').readlines()[1:]
            for line in lines:
                try:
                    idx, age, sex, city, symp_date, variant_type, note = line[:-1].split('\t')
                except:
                    print(line)
                    raise
                idx = int(idx)
                node_name = '%s%d' % (pref, idx)
                sex = sex.replace('性', '')
                age = age.replace('代', '')
                
                if note.find('の関係者') >= 0:
                    connected_nodes = ['gifu%d' % int(re.sub('・No.(\d*)の関係者', '***\\1***', note).split('***')[1])]
                else:
                    connected_nodes = []

                if symp_date == '無症状':
                    if idx in (42, 43):
                        date = datetime.date.fromisoformat('2021-03-21')
                    elif idx in (74, 75, 76):
                        date = datetime.date.fromisoformat('2021-04-01')
                    else:
                        try:
                            date = cases[connected_nodes[0]].date
                        except:
                            print('skipping', idx, '...')
                            date = datetime.date.fromisoformat('2021-05-01')
                else:
                    m = int(symp_date.split('月')[0])
                    if symp_date.find('上旬') >= 0:
                        d = 1
                    elif symp_date.find('中旬') >= 0:
                        d = 11
                    else:
                        d = 21

                    date = datetime.date.fromisoformat('2021-%02d-%02d' % (m, d))

                cases[node_name] = Case(node_name, age, sex, city, note, date, variant_type, connected_nodes)

        return cases

    def make_aichi_cases(self):
        return self.make_cases('aichi')

    def make_gifu_cases(self):
        return self.make_cases('gifu')

def main():
    global plotter

    reader = TSVReader()
    cases = reader.make_aichi_cases()
    case_graph_aichi = CaseGraph('Aichi_Variants')
    case_graph_aichi.add_only_aichi_cases(cases, 1)
    case_graph_aichi.gv_graph.view()

    reader = TSVReader()
    cases = reader.make_gifu_cases()
    case_graph_gifu = CaseGraph('Gifu_Variants')
    case_graph_gifu.add_only_gifu_cases(cases, 1)
    case_graph_gifu.gv_graph.view()

def before_2021(date):
    return str(date)[:-5] in ('2020-',)

if __name__ == '__main__':
    main()
