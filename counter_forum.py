#!/usr/bin/env python
# encoding: utf-8

# auteur originel : Gabriel Pettier
# fork : nany
# license GPL V3 or later

# bibliothèque de fonctions pour naviguer dans le forum
# nécessite python 2.4 minimum et python-mechanicalsoup.


from counter_path import LOGFILE, POSTFILE, FILESPATH, FORUM_URL, TOPIC_URL
from counter_funclib import log
from time import sleep
from sys import exit
from os import access, F_OK
from mechanicalsoup import *


def getBrowser():

    return StatefulBrowser(raise_on_404=True,
                           user_agent='Mozilla/5.0 (compatible)')


def getPage(browser, url):

    # essaye de récupérer la page tant qu’il y a des erreurs
    while True:
        try:
            browser.open(url)
            page = browser.get_current_page()
            if 'Error / FluxBB' in page.title.renderContents():
                log('Erreur FluxBB')
                sleep(10)
                continue
            break
        except Exception as error:
            log(str(error))
            sleep(10)
    return page


def log_in(browser, forum_url):

    lf = open(FILESPATH + '.counter_logins', 'r')
    login = lf.readline().strip('\n')
    password = lf.readline().strip('\n')
    lf.close()
    url_log = forum_url + 'login.php'
    url_index = forum_url + 'index.php'

    browser.open(url_log)
    browser.select_form('form[id="login"]')
    browser['req_username'] = login
    browser['req_password'] = password
    browser.submit_selected()

    page = getPage(browser, url_index)
    welcome = page.find('div', id='brdwelcome')
    if welcome.findAll('a')[-1].renderContents() == 'Déconnexion':
        log('connexion effectuée')
    else:
        log('erreur lors de la connexion')


def log_out(browser, forum_url):

    pindex = forum_url + 'index.php'
    browser.open(pindex)
    disconnect = browser.find_link(title="Déconnexion")
    try:
        browser.follow_link(disconnect)
        browser.open(pindex)
        welcome = browser.get_current_page().findAll('fieldset')[-1]
        if welcome.findAll('a')[-1].renderContents() == 'inscription':
            log('déconnexion effectuée')
        else:
            log('erreur lors de la déconnexion')
    except:
        log('le compteur ne semble pas être connecté')
    browser.close()


def numpage(page):

    return page.find('p', 'pagelink conl').strong.renderContents()


def pagelinks(page):

    return page.find('p', 'pagelink conl').findAll('a')


def isfirstpage(page):

    num = numpage(page)
    return (int(num) == 1)


def islastpage(page):

    num = numpage(page)
    links = pagelinks(page)
    if len(links) > 0:
        if int(links[-1]['href'].split('p=')[-1]) > int(num):
            return False
        else:
            return True
    else:
        return True


def search_TdCT(browser, f_url):

    log('recherche du TdCT')
    url = ''
    eonpe = getPage(browser, f_url + 'viewforum.php?id=181')
    st = eonpe.tbody
    for td in st.findAll('td', 'tcl'):
        if td.find('span', 'stickytext'):
            t_url = td.findAll('a')[-1]['href']
            str_p = td.findAll('a')[-1].renderContents()
            int_p = int(str_p) - 10
            if int_p < 1:
                int_p = 1
            t_url = t_url.replace(str_p, str(int_p))
            log(t_url)
            url = f_url + t_url
            if check_url(browser, url, f_url, t_url):
                break
    if url == '':
        log('échec : arrêt du script')
        print 'le script s’est arrêté suite à une erreur'
        print 'détail des opérations dans', LOGFILE
        exit()

    return url


def check_url(browser, url, f_url, t_url):

    if not url.split('?')[0] == f_url + TOPIC_URL:
        log('mauvaise url')
        return False
    else:
        page = getPage(browser, url)
        if isfirstpage(page):
            firstpage = page
        else:
            urlfirst = f_url + pagelinks(page)[1]['href']
            firstpage = getPage(browser, urlfirst)
        firstpost = firstpage.find('div',
                                   'blockpost rowodd firstpost blockpost1')
        firstpost = firstpost.find('div', 'postmsg')
        firstlinks = firstpost.findAll('a')
        if len(firstlinks) > 0:
            for link in firstlinks:
                if 'topic des couche-tard' in link.renderContents():
                    return True
        else:
            log('mauvaise url')
            return False


def next(page, url):

    # si la page n’est pas la dernière,
    # le dernier lien pointe vers la page suivante
    if not islastpage(page):
        t_url = pagelinks(page)[-1]['href']
        url = FORUM_URL + t_url
        log('page suivante :')
    else:   # sinon, on est à la dernière page :
            # on vérifie alors si le sujet est fermé,
            # auquel cas on renvoie le dernier lien fourni sur la page
        resp = page.find('p', 'postlink conr').renderContents()
        if resp == 'Discussion fermée':
            for postmsg in page.findAll('div', 'postmsg'):
                if postmsg.find('a'):
                    nextpage = postmsg.findAll('a')[-1]['href']
                    t_url = nextpage.split('/')[-1]
                    print t_url
                    url = FORUM_URL + t_url
            log('nouveau topic :')
        else:
            log('dernière page')

    return url


def post(browser, postfile, urlfile):

    if access(postfile, F_OK):
        fp = open(postfile, 'r')
        msg = fp.read()
        log('message chargé')
        fp.close
    else:
        msg = 'Oups !'
        log('message = Oups !')

    fu = open(urlfile, 'r')
    url = fu.readline().strip('\n')
    fu.close()
    log(url)
    page = getPage(browser, url)
    resp = page.find('p', 'postlink conr').renderContents()
    if resp == 'Discussion fermée':
        url = search_TdCT(browser, FORUM_URL)
    browser.open(url)
    browser.select_form('form[id="quickpostform"]')
    browser['req_message'] = msg
    browser.get_current_form().choose_submit('submit')
    browser.submit_selected()
    log('message posté')

