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

# fork : nany


from counter_path import LOGFILE, POSTFILE, LOGPATH, FILESPATH , TZPATH
from counter_path import FORUM_URL, TOPIC_URL
from counter_classlib import IgnoreList, Day, Score, User, Post
from counter_funclib import DateTimePost, naive, renderpost
from counter_funclib import HtmlToText, tzFrance, log
import counter_forum as forum
import datetime
from dateutil.tz import *
import re
import os

DEBUG = False
TODAY = datetime.date.today()
# TODAY = datetime.date(2022, 12, 27)
YESTERDAY = TODAY + datetime.timedelta(days=-1)
MIN = datetime.datetime.combine(YESTERDAY, datetime.time(21, 0))
MAX = datetime.datetime.combine(TODAY, datetime.time(5, 0))


def main(urlfile, files, blockfile):

    pub_block = False
    log('POINTS DE LA NUIT DU ' + YESTERDAY.strftime('%d/%m/%Y') + ' AU ' +
        TODAY.strftime('%d/%m/%Y') + '\n')
    log('début\n                  ‾‾‾‾‾')
    logurl = LOGPATH + str(TODAY) + '_' + urlfile
    urlfile = FILESPATH + urlfile
    users = {}
    f = open(urlfile, 'r')
    url = save_url = f.readline().strip('\n')
    t_url = url.split('/')[-1]
    f.close()
    entries = Day()
    block = IgnoreList(blockfile)

    browser = forum.getBrowser()
    forum.log_in(browser, FORUM_URL)
    # vérification des pseudos de la blocklist
    for stridname in block.list:
        if stridname.split(';')[0] == '40383':
            oname = stridname.split(';')[1] + ';'
        else:
            oname = stridname.split(';')[1]
        purl = FORUM_URL + 'profile.php?id=' + stridname.split(';')[0]
        page = forum.getPage(browser, purl)
        
        try:
            nname = str(page.find('dd').renderContents().decode('utf8'))
        except AttributeError:
            nname = page.find('div' , 'infldset').find('p')
            nname = nname.renderContents().decode('utf8')
            nname = str(nname).replace('Nom d\'utilisateur: ' , '')
        if nname != oname:
            block.Del(stridname)
            block.Add(stridname.split(';')[0] + ';' + nname)

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
            if 'timezone[' in stpost.lower():
                tzi = stpost.lower().find("timezone[")
                tzt = stpost[tzi:tzi+9]
                tzpost = stpost.split(tzt)[1].split(']')[0]
                # ne sera pas pris en compte s’il y a plus d’une occurence
                if stpost.count(tzt) > 1:
                    log('{0} {1} → trop de « timezone » !'.format(
                        user.name, post.url))
                # ni si la désignation du fuseau horaire est incorrect
                elif not os.path.exists(TZPATH + tzpost):
                    log('{0} {1} → mauvaise « timezone » : {2}'.format(
                        user.name, post.url, tzpost))
                else:
                    user.tz = tzpost
            # recherche de « [blockme] » dans le message
            stridname = str(user.id) + ';' + user.name
            if '[blockme]' in post.msg.lower():
                log('ajout éventuel de {0} à la blocklist'.format(user.name))
                if stridname not in block.list:
                    log('demande de publication de la blocklist')
                    pub_block = True
                block.Add(stridname)
            # recherche de « [letmepass] » dans le message
            if '[letmepass]' in post.msg.lower():
                log('retrait éventuel de {0} de la blocklist'.format(
                    user.name, user.id))
                if stridname in block.list:
                    log('demande de publication de la blocklist')
                    pub_block = True
                block.Del(stridname)
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

        new_url = forum.next(browser, page, url)
        if new_url == url:
            break
        else:
            url = new_url

    forum.log_out(browser, FORUM_URL)

    save_dt = naive(datetime.datetime.now())
    pcrime = []
    moinsune = []
    for u in users:
        toupil = []
        user = users[u]
        for post in user.posts:
            # récupère l’url d’où repartir le lendemain
            if save_dt > naive(post.dt) >= MAX:
                save_dt = naive(post.dt)
                save_url = FORUM_URL + post.url

            # traitement du décalage horaire
            post.localize(user.tz)

            # si le membre n’est pas blocklisté
            # comptage si post entre 21:00 la veille et 04:59 ce jour
            # ou si l’edit est entre 21:00 la veille et 04:59 ce jour
            if (str(user.id) + ';' + user.name) not in block.list:
                if MIN <= naive(post.dt) < MAX:
                    user.Points(naive(post.dt).hour)
                if post.stredit and MIN <= naive(post.edit) < MAX and \
                   user.name in post.stredit:
                    user.Points(naive(post.edit).hour)
                # tout pile
                if "00:00" in naive(post.dt).strftime('%M:%S') and \
                   MIN <= naive(post.dt) < MAX:
                    toupil.append([user.name, '/' + post.url])
            # crime parfait
            if "00:00:00" in naive(post.dt).strftime('%H:%M:%S') and \
               (str(user.id) + ';' + user.name) not in block.list and \
               MIN <= naive(post.dt) < MAX:
                user.cr = True
                pcrime.append([user.name, '/' + post.url])
            # moins une
            if "04:59:59" in naive(post.dt).strftime('%H:%M:%S') and \
               (str(user.id) + ';' + user.name) not in block.list and \
               MIN <= naive(post.dt) < MAX:
                user.mu = True
                moinsune.append([user.name, '/' + post.url])
        # comptage des points des tout pile
        if toupil != []:
            user.tp = 1
            s = sorted(toupil, key=lambda x: x[0]+x[1])
            prec = ['', '']
            while s:
                i = s.pop()
                if i[0] == prec[0]:
                    user.tp += 1
                prec = i
            user.points += int(user.tp/2)
        # points du crime parfait
        if user.cr:
            user.points += 2
        # points du moins une
        if user.mu:
            user.points += 5
        if user.points > 0:
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
        log('demande de publication de la blocklist')
        pub_block = True
    fp = open(POSTFILE, 'r')
    msg = fp.read()
    fp.close()
    fp = open(POSTFILE, 'w')
    fp.write('PLOUF !\n\n')
    fp.write('[url=/viewtopic.php?pid=22511619#p22511619]')
    fp.write('Rappel des règles.[/url]\n\n')
    for u in users:
        user = users[u]
        if user.tp == 1 and not user.cr:
            fp.write('Bravo ' + user.name + ' pour ton tout pile ')
            fp.write('(message à l’heure juste) ! Avec un autre tout pile, ')
            fp.write('tu aurais pu avoir 1 point bonus supplémentaire.\n')
        elif user.tp > 1:
            tpp = int(user.tp/2)
            fp.write('Bravo ' + user.name + ' pour tes ' + str(user.tp) + ' ')
            fp.write('tout pile (messages à l’heure juste) ! Tu gagnes ')
            fp.write(str(tpp) + ' ')
            if tpp == 1:
                fp.write('point bonus supplémentaire.\n')
            else:
                fp.write('points bonus supplémentaires.\n')
    if pcrime != []:
        for c in pcrime:
            fp.write('Bravo ' + c[0] + ' pour [url=' + c[1])
            fp.write(']ton crime parfait (message à minuit pile)[/url] ! ')
            fp.write('Tu gagnes 2 points bonus supplémentaires.\n')
            for u in users:
                user = users[u]
                if c[0] == user.name and user.tp == 1:
                    fp.write('Avec un autre tout pile, tu aurais pu ')
                    fp.write('accumuler les points correspondants plus ')
                    fp.write('1 point bonus supplémentaire.\n')
    if moinsune != []:
        for u in moinsune:
            fp.write('Bravo ' + u[0] + ' pour [url=' + u[1])
            fp.write(']ton message à 5h moins une seconde[/url] ! ')
            fp.write('Tu gagnes 5 points bonus supplémentaires.\n')
    if night_scores != []
        fp.write('\nPoints marqués la nuit passée :\n[code]\n')
        night_scores.sort(reverse=True)
        for score in night_scores:
            fp.write(str(score.num).rjust(3) + '    ' + score.name + '\n')
        fp.write('[/code]\n')
    fp.write(msg)
    if pub_block:
        fp.write('\nLes membres suivants sont ignorés :\n')
        fp.write('[code]\n')
        for stridname in block.list:
            if stridname.split(';')[0] == "40383":
                fp.write(stridname.split(';')[1] + ';\n')
            else:
                fp.write(stridname.split(';')[1] + '\n')
        fp.write('[/code]\n')
    fp.close()

    log('fin\n                  ‾‾‾\n')


main('url_TdCT', ['count_month_TdCT', 'count_TdCT'], 'blocklist')

