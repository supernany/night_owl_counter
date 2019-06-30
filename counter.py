#!/usr/bin/env python3
# coding: utf8

# auteur originel : Gabriel Pettier
# license GPL V3 or later

# sert uniquement a compter les points sur ce topic :
# https://forum.ubuntu-fr.org/viewtopic.php?pid=22045004#p22045004
# et donc probablement inutile a quiquonque vu que le serveur
# se charge de le lancer tous les matins et tous les soirs
# publié a seul but de vérification par les interressés. ;),
# peut aussi servir si le serveur n'est plus là
# pour assurer le service un jour.

# nécessite python 3.6 minimum et python3-dateutil.

# le fichier './files/.counter_logins' doit contenir
# le login du posteur sur la première ligne,
# et son mot de passe sur la deuxième (cela et seulement cela).

# fork : nany


from counter_path import LOGFILE, POSTFILE, LOGPATH, FILESPATH
from counter_path import FORUM_URL, TOPIC_URL
from counter_classlib import IgnoreList, Day, Score, User, Post
from counter_funclib import DateTimePost, naive, renderpost
from counter_funclib import HtmlToText, tzFrance, log
import counter_forum as forum
import datetime
from time import sleep
from dateutil.tz import *
import re
import os

DEBUG = True
TZPATH = '/usr/share/zoneinfo/'


def main(urlfile, files, blackfile):

    PUB_BLACK = False
    TODAY = datetime.date.today()
    # TODAY = datetime.date(2015, 8, 13)
    YESTERDAY = TODAY + datetime.timedelta(days=-1)
    log('POINTS DE LA NUIT DU ' + YESTERDAY.strftime('%d/%m/%Y') + ' AU ' +
        TODAY.strftime('%d/%m/%Y') + '\n')
    log('début\n                  ‾‾‾‾‾')
    MIN = datetime.datetime.combine(YESTERDAY, datetime.time(21, 0))
    MINSTAT = datetime.datetime.combine(YESTERDAY, datetime.time(5, 0))
    MAX = MAXSTAT = datetime.datetime.combine(TODAY, datetime.time(5, 0))
    logurl = LOGPATH + str(TODAY) + '_' + urlfile
    urlfile = FILESPATH + urlfile
    users = {}
    f = open(urlfile, 'r')
    url = f.readline().strip('\n')
    t_url = url.split('/')[-1]
    f.close()
    save_url = ''
    entries = Day()
    black = IgnoreList(blackfile)
    log('blacklist chargée')

    browser = forum.getBrowser()
    forum.log_in(browser, FORUM_URL)
    # vérification des pseudos de la blacklist
    for stridname in black.list:
        oname = stridname.split(';')[1]
        if stridname.split(';')[0] != '1714901':
            purl = FORUM_URL + 'profile.php?id=' + stridname.split(';')[0]
            page = forum.getPage(browser, purl)
            nname = str(page.find('dd').renderContents().decode('utf8'))
            nname = nname.split('\'')[-1]
            if nname != oname:
                black.Del(stridname)
                black.Add(stridname.split(';')[0] + ';' + nname)

    log('parcours des pages')
    while True:
        log(url)
        if not forum.check_url(browser, url, FORUM_URL, t_url):
            url = forum.search_TdCT(browser, FORUM_URL)
        page = forum.getPage(browser, url)
        # parcourt les posts de la page
        for p in page.findAll('div', id=re.compile('p+[0-9]')):
            post = Post(p)
            user = User(post.left)
            post.localize(tzFrance)
            if str(user.id) in users.keys():
                user = users[str(user.id)]
            user.posts.append(post)
            users[str(user.id)] = user
            # recherche de « timezone[ » dans le message
            # (sans citation ni code) et dans la signature
            tpost = post.msg + post.sign
            stpost = tpost.replace(' ', '')
            stpost = stpost.replace(' ', '')
            stpost = stpost.replace(' ', '')
            stpost = stpost.replace('&#160;', '')
            if 'timezone[' in stpost:
                tzpost = stpost.split('timezone[')[1].split(']')[0]
                # ne sera pas pris en compte s’il y a plus d’une occurence
                if stpost.count('timezone[') > 1:
                    log('{0} {1} → trop de « timezone » !'.format(
                        user.name, post.url))
                # ni si la désignation du fuseau horaire est incorrect
                elif not os.path.exists(TZPATH + tzpost):
                    log('{0} {1} → mauvaise « timezone » : {2}'.format(
                        user.name, post.url, tzpost))
                else:
                    user.tz = tzpost
            # recherche de « [blacklistme] » dans le message
            stridname = str(user.id) + ';' + user.name
            if '[blacklistme]' in post.msg.lower():
                log('ajout éventuel de {0} à la blacklist'.format(user.name))
                if stridname not in black.list:
                    log('demande de publication de la blacklist')
                    PUB_BLACK = True
                black.Add(stridname)
            # recherche de « [unblacklistme] » dans le message
            if '[unblacklistme]' in post.msg.lower():
                log('retrait éventuel de {0} de la blacklist'.format(
                    user.name, user.id))
                if stridname in black.list:
                    log('demande de publication de la blacklist')
                    PUB_BLACK = True
                black.Del(stridname)
            # recherche de « [razme] » dans le message
            if '[razme]' in post.msg.lower():
                log('retrait éventuel du score de {0}'.format(
                    user.name, user.id))
                content = ''
                for scorefile in files:
                    fscore = open(FILESPATH + scorefile, 'r')
                    lines = fscore.readlines()
                    fscore.close()
                    new_lines = ''
                    for line in lines:
                        if str(user.id) not in line:
                            new_lines += line
                        else:
                            log(user.name + ' effacé')
                    fscore = open(FILESPATH + scorefile, 'w')
                    fscore.write(new_lines)
                    fscore.close()
                    log(scorefile + ' sauvegardé')

        # ne sert qu’en cas de récup depuis une date antérieure
        # TOMOROW = TODAY + datetime.timedelta(days=1)
        # LIMIT = datetime.datetime.combine(TOMOROW, datetime.time(15, 0))
        # if naive(post.dt) > LIMIT:
        #     break
        # les 4 lignes précédentes peuvent être commentées
        # s’il n’y a pas de récup depuis une date antérieure

        new_url = forum.next(page, url)
        if new_url == url:
            break
        else:
            url = new_url

    forum.log_out(browser, FORUM_URL)

    save_dt = naive(datetime.datetime.now())
    for u in users:
        user = users[u]
        for post in user.posts:
            # récupère l’url d’où repartir le lendemain
            if save_dt > naive(post.dt) >= MAXSTAT:
                save_dt = naive(post.dt)
                save_url = FORUM_URL + post.url

            # traitement du décalage horaire
            post.localize(user.tz)

            # comptage si post entre 21:00 la veille et 04:59 ce jour
            if MIN < naive(post.dt) < MAX:
                if post.edit and MIN < naive(post.edit) < MAX:
                    user.Points(naive(post.edit).hour)
                else:
                    user.Points(naive(post.dt).hour)
                # on ajoute l’entrée si le membre n’est pas blacklisté
                if (str(user.id) + ';' + user.name) not in black.list:
                    entries.addEntry(user)

    if not DEBUG:
        log('sauvegarde de l\'url')
        log(save_url)
        f = open(urlfile, 'w')
        f.write(save_url)
        f.close()
        flog = open(logurl, 'w')
        flog.write(save_url)
        flog.close()

    log('analyse des scores')
    for scorefile in files:
        if files.index(scorefile) == 0:
            period = 'du mois en cours'
        else:
            period = 'de la seconde guerre'
        log(period + '\n')
        f = open(FILESPATH + scorefile, 'r')
        lines = f.readlines()
        f.close()
        scores = []

        for line in lines:
            if line not in [' ', '']:
                line_tuple = re.split('\s+', line)[1:]
                line_num = line_tuple[0]
                line_id = line_tuple[1]
                line_name = ' '.join(line_tuple[2:])
                scores.append(Score([line_num, line_id, line_name]))

        new_scores = []
        night_scores = []
        for entry, data in entries.entries.items():
            name = data[0]
            num = data[1]
            night_scores.append(Score([num, entry, name]))
            if files.index(scorefile) == 0 and TODAY.day == 2:
                scores = []
                log(' '.join(['nouvelle période', name, '→',
                    str(num), 'points']))
                new_scores.append(Score([num, entry, name]))
            elif scores == []:
                log(' '.join(['nouveau membre :', name, '→', str(num),
                    'points']))
                new_scores.append(Score([num, entry, name]))
            else:
                for score in scores:
                    if entry == score.id:
                        score.num += num
                        score.name = name
                        log(' '.join(['ajout :', score.name, '+', str(num),
                            '⇒', str(score.num)]))
                        break
                    if score is scores[-1]:
                        log(' '.join(['nouveau membre :', name, '→',
                            str(num), 'points']))
                        new_scores.append(Score([num, entry, name]))
                        break

        scores += new_scores

        # vérification des doublons
        for nScore in range(len(scores) - 2):
            mScore = nScore + 1
            for score in scores[mScore:]:
                if scores[nScore].id == score.id:
                    log(' '.join(['doublon :', scores[nScore].name, '⇐⇒',
                        score.name]))
                    score.num += scores[nScore].num
                    del(scores[nScore])

        scores.sort(reverse=True)
        if not DEBUG:
            log('sauvegarde des scores ' + period + '\n')
            f = open(FILESPATH + scorefile, 'w')
            flog = open(LOGPATH + str(TODAY) + '_' + scorefile, 'w')
            for score in scores:
                f.write('%s\n' % score)
                flog.write('%s\n' % score)
            f.close()
            flog.close()
        renderpost(FILESPATH + scorefile)
    if TODAY.day == 2:
        PUB_BLACK = True
    fp = open(POSTFILE, 'r')
    msg = fp.read()
    fp.close()
    fp = open(POSTFILE, 'w')
    fp.write('Points marqués la nuit passée :\n[code]\n')
    night_scores.sort(reverse=True)
    for score in night_scores:
        fp.write(str(score.num).rjust(3) + '    ' + score.name + '\n')
    fp.write('[/code]\n')
    fp.write(msg)
    if PUB_BLACK:
        fp.write('\nLes membres suivants sont ignorés :\n')
        fp.write('[code]\n')
        for stridname in black.list:
            fp.write(stridname.split(';')[1] + '\n')
        fp.write('[/code]')
    fp.close()

    log('fin\n                  ‾‾‾\n')


main('url_TdCT', ['count_month_TdCT', 'count_TdCT'], 'blacklist')

