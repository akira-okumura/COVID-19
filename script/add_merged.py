#!/usr/bin/env python3

import re

def main(fin1, fin2):
    # fin1: Aichi_official.tsv or similar
    # fin2: merged_0807.tsv or similar
    data1 = []
    lines = open(fin1).readlines()

    for line in lines:
        n, date, person, nationality, city, note, another_index = line[:-1].split('\t')
        data1.append((n, date, person, nationality, city, note, another_index))

    data2= []
    lines = open(fin2).readlines()[1:]
    for line in lines:
        n, date, person, nationality, city, note, another_index = line[:-1].split('\t')
        data2.append((n, date, person, nationality, city, note, another_index))
    
    data12 = data1 + data2

    for line in lines:
        n, date, person, nationality, city, note, another_index = line[:-1].split('\t')
        results = re.findall('(愛知県内[,\d]*|豊田市発表[,\d]*|岡崎市発表[,\d]*|豊橋市発表[,\d]*|名古屋市発表[,\d]*|岐阜県内[,\d]*)', note)
        
        indices = ''
        results2 = ''

        for result in results:
            if result.find('岐阜県内') != 0:
                note = note.replace(result, '')

            if result.find('愛知県内') == 0:
                result = result.replace(',', ',愛知県内')
            elif result.find('豊田市発表') == 0:
                result = result.replace(',', ',豊田市発表')
            elif result.find('岡崎市発表') == 0:
                result = result.replace(',', ',岡崎市発表')
            elif result.find('豊橋市発表') == 0:
                result = result.replace(',', ',豊橋市発表')
            elif result.find('名古屋市発表') == 0:
                result = result.replace(',', ',名古屋市発表')
            elif result.find('岐阜県内') == 0:
                result = result.replace(',', ',岐阜県内')

            results2 += result + ','
        
        if len(results2) > 0 and results2[-1] == ',':
            results2 = results2[:-1]
            
        results = results2.split(',')

        for i in range(len(data12) - 1, -1, -1):
            if data12[i][-1] in results or ('愛知県内' + data12[i][0]) in results:
                indices += data12[i][0] + ','

        if len(indices) > 0 and indices[-1] == ',':
            indices = indices[:-1]

        note.replace(' ', '')
        note2 = ''
        if note != '':
            import sys
            print('WARNING', line, file=sys.stderr, end='')
            print('*****', note, '*****', file=sys.stderr)
            note2 = re.sub('(岐阜県内\d*)', '\\1例目と接触', note).replace('例目,岐阜県内', '例目、')
            note3 = re.sub('(三重県内\d*)', '\\1例目と接触', note2).replace('例目,三重県内', '例目、')
            note4 = re.sub('(滋賀県内\d*)', '\\1例目と接触', note3).replace('例目,滋賀県内', '例目、')
            note2 = note4
        elif results == ['']:
            note2 = ''


        if indices != '':
            if note2 == '':
                note2 = 'No.' + indices + 'と接触'
            else:
                note2 += '/No.' + indices + 'と接触'

        data1.append((n, date, person, nationality, city, note2, another_index))

    for i in range(len(data1)):
        n, date, person, nationality, city, note, another_index = data1[i]
        print(n + '\t' + date + '\t' + person + '\t' + nationality + '\t' + city + '\t' + note + '\t' + another_index + '\n', end='')

if __name__ == '__main__':
    import sys
    main(sys.argv[1], sys.argv[2])
