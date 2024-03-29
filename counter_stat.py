#!/usr/bin/env python3
# coding: utf8

# auteur originel : Gabriel Pettier
# fork : nany
# license GPL V3 or later

# pour faire les statistiques des posts de la journée passée sur le topic
# nécessite python 3 minimum.


from counter_path import LOGFILE, STATFILE, LOGPATH, FILESPATH
from counter_path import FORUM_URL, TOPIC_URL
from counter_classlib import Post
from counter_funclib import DateTimePost, naive, renderstats, tzFrance, log
import counter_forum as forum
import datetime
import re


def main(urlfile, statfile):

    DEBUG = False
    TODAY = datetime.date.today()
    # TODAY = datetime.date(2015, 4, 30)
    YESTERDAY = TODAY + datetime.timedelta(days=-1)
    log('STATISTIQUES DE LA NUIT DU ' + YESTERDAY.strftime('%d/%m/%Y') +
        ' AU ' + TODAY.strftime('%d/%m/%Y') + '\n')
    log('début\n                  ‾‾‾‾‾')
    MINSTAT = datetime.datetime.combine(YESTERDAY, datetime.time(5, 0))
    MAXSTAT = datetime.datetime.combine(TODAY, datetime.time(5, 0))
    urlfile = FILESPATH + urlfile
    urlpost = FILESPATH + 'url_poststat'
    logurl = LOGPATH + str(TODAY) + '_' + 'url_poststat'
    stats = {}
    f = open(urlfile, 'r')
    url = f.readline().strip('\n')
    t_url = url.split('/')[-1]
    f.close()

    browser = forum.getBrowser()
    forum.log_in(browser, FORUM_URL)

    log('parcours des pages')
    while True:
        log(url)
        if not forum.check_url(browser, url, FORUM_URL, t_url):
            url = forum.search_TdCT(browser, FORUM_URL)
        page = forum.getPage(browser, url)
        # parcourt les posts de la page
        for p in page.findAll('div', id=re.compile('p+[0-9]')):
            post = Post(p)
            post.localize(tzFrance)

            # statistiques si post entre 05:00 la veille et 04:59 ce jour
            if MINSTAT < naive(post.dt) < MAXSTAT:
                # compte les posts par plage horaire
                if post.dt.strftime('%H') not in stats:
                    stats[post.dt.strftime('%H')] = 1
                else:
                    stats[post.dt.strftime('%H')] += 1

        new_url = forum.next(browser, page, url)
        if new_url == url:
            break
        else:
            url = new_url

    if not DEBUG:
        log('sauvegarde de l\'url')
        log(url)
        f = open(urlpost, 'w')
        f.write(url)
        f.close()
        flog = open(logurl, 'w')
        flog.write(url)
        flog.close()

    fn = open(FILESPATH + 'nannif', 'r')
    f_a = fn.readlines()
    fn.close()
    for d in f_a:
        if datetime.date.today().strftime('%d/%m') in d:
            data = d.strip('\n').split(' ')
            break
    fas = data[1].replace('_',' ')
    if 'Joyeux' in fas:
        tfas = fas + '\n'
    else:
        tfas = 'Selon [url=https://www.keskeces.fr/fete-a-souhaiter.html]'
        tfas += 'Keskeces[/url], bonne fête aux ' + fas + '.\n'
    aas = data[2:]
    taas = ''
    for i in range(len(aas)):
        purl = FORUM_URL + 'profile.php?id=' + aas[i]
        page = forum.getPage(browser, purl)
        naas = str(page.find('dd').renderContents().decode('utf8'))
        naas = naas.replace('_', ' ')
        naas = naas.replace(' ', '_')
        taas += ' ' + naas
    sr = re.findall(r'[^ ]+', taas)
    for i in range(len(sr)):
        if i == len(sr) - 1:
            taas += ' !'
        elif i == len(sr) - 2:
            taas = taas.replace(sr[i], sr[i] + ' et')
        else:
            taas = taas.replace(sr[i], sr[i] + ',')
    if taas != '':
        taas = 'Joyeux aniversaire' + taas +'\n\n'
        taas = taas.replace('_', ' ')
        taas = taas.replace(' ', '_')
    else:
        taas = '\n'

    msg = renderstats(tfas, taas, stats)
    fs = open(statfile, 'w')
    fs.write(msg)
    fs.close()

    forum.log_out(browser, FORUM_URL)

    log('fin\n                  ‾‾‾\n')

main('url_TdCT', STATFILE)

