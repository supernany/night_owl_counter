#!/usr/bin/env python3
# coding: utf8

# auteur originel : Gabriel Pettier
# fork : nany
# license GPL V3 or later

# bibliothèque des fonctions du compteur
# nécessite python 3 minimum et python3-dateutil.


from counter_path import LOGFILE, POSTFILE, LOGPATH, FILESPATH
from counter_path import FORUM_URL, TOPIC_URL
from datetime import *
from dateutil.tz import *
import re

tzFrance = 'Europe/Paris'


def DateTimePost(dt):

    if ', ' in dt:
        dt = [dt.split(' ')[1].split(',')[0],
              dt.split(' ')[-1].split('\'')[0]]
    else:
        dt = [dt.split(' ')[0],
              dt.split(' ')[-1].split('\'')[0].split('"')[0]]
    if 'hier' in dt[0].lower():
        d = date.today() + timedelta(days=-1)
    elif 'aujourd\'hui' in dt[0].lower():
        d = date.today()
    else:
        d = datetime.strptime(dt[0], '%d/%m/%Y').date()
    t = time(int(dt[-1].split(':')[0]), int(dt[-1].split(':')[1]))
    dyear = int(d.strftime('%Y'))
    dmonth = int(d.strftime('%m'))
    dday = int(d.strftime('%d'))
    thour = int(dt[-1].split(':')[0])
    tmin = int(dt[-1].split(':')[1])

    return datetime(dyear, dmonth, dday, thour, tmin, tzinfo=gettz('UTC'))


def naive(dt):

    return datetime.combine(dt.date(), dt.time())


def renderstats(stats):  # pour faire le graphique

    DayStats = {'00': 0, '01': 0, '02': 0, '03': 0, '04': 0, '05': 0,
                '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0,
                '12': 0, '13': 0, '14': 0, '15': 0, '16': 0, '17': 0,
                '18': 0, '19': 0, '20': 0, '21': 0, '22': 0, '23': 0}
    DayStats.update(stats)
    code = '[code]\n'
    for k in sorted(DayStats.keys())[5:]:
        code += '[' + k + 'h:' + ((int(k) < 9 and '0') or '')
        code += ((int(k) == 23 and '00') or str(int(k)+1)) + 'h[ : '
        code += '#' * DayStats[k]
        code += ((DayStats[k] > 0 and ' ') or '')
        code += str(DayStats[k]) + '\n'
    for k in sorted(DayStats.keys())[:5]:
        code += '[' + k + 'h:' + '0' + str(int(k)+1) + 'h[ : '
        code += '#' * DayStats[k]
        code += ((DayStats[k] > 0 and ' ') or '')
        code += str(DayStats[k]) + '\n'
    code += '[/code]'

    return code


def renderpost(_file):

    title = (((_file == FILESPATH + 'count_TdCT') and
              'Scores totaux de la seconde guerre') or
             'Scores du mois en cours')
    msg = title + ' :\n[code]\n' + b'\xe2\x80\xad'.decode('utf8')
    fs = open(_file, 'r')
    scores = fs.readlines()
    for i in range(len(scores)):  # on veut toutes les lignes restantes
        score = re.split('\s+', scores[i], 3)[1:]
        precnum = re.split('\s+', scores[i-1])[1]
        num = score[0]
        Id = score[1]
        name = score[2]
        line = scores[i].replace(Id.rjust(10), '')
        if i == 0:
            tmpRange = 0
        elif num == precnum:
            pass
        else:
            tmpRange = i
        # et on ajoute la ligne avec le bon rang a l'entrée
        if '\xe2\x80\xae' in scores[i-1]:
            msg += b'\xe2\x80\xac'.decode('utf8')
        if Id == '7666':
            msg += '*** Vétéran des couche-tard, héros de la première'
            msg += ' guerre, invaincu avant retraite ***\n'
        msg += str(tmpRange + 1).rjust(5) + ')' + line
        if Id == '7666':
            msg += '*' * 85 + '\n'
    msg += '[/code]\n'

    fp = open(POSTFILE, 'a')
    fp.write(msg)
    fp.close


def HtmlToText(txt):
    data = (['&lt;', '<'], ['&gt;', '>'], ['&#039;', '\''], ['&#160;', ' '],
            ['&quot;', '\"'], ['&amp;', '&'])
    for rep in data:
        txt = txt.replace(rep[0], rep[1])

    return txt


def log(line):

    time = datetime.now().strftime('[%H:%M:%S]  ')
    f = open(LOGFILE, 'a')
    f.write(time + line + '\n')
    f.close()

