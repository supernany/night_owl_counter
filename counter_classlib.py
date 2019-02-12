#!/usr/bin/env python
# encoding: utf-8

# auteur originel : Gabriel Pettier
# fork : nany
# license GPL V3 or later

# bibliothèque des classes du compteur
# nécessite python 2.4 minimum.


from counter_path import LOGFILE, LOGPATH, FILESPATH, FORUM_URL, TOPIC_URL
from counter_funclib import DateTimePost, HtmlToText, tzFrance, log
from dateutil.tz import *


class IgnoreList:

    def __init__(self, blackfile):
        self.black = FILESPATH + blackfile
        f = open(self.black, 'r')
        self.list = f.read().split('\n')[:-1]
        f.close()

    def Add(self, stridname):
        if stridname not in self.list:
            self.list.append(stridname)
            log(stridname + ' ajouté')
            self.Save()

    def Del(self, stridname):
        if stridname in self.list:
            self.list.remove(stridname)
            log(stridname + ' retiré')
            self.Save()

    def Save(self):
        log('sauvegarde de la blacklist')
        f = open(self.black, 'w')
        for stridname in self.list:
            f.write('%s\n' % stridname)
        f.close()


class Day:
    """
    un jour dure de 21h à 5h du matin exclu ([21h:5h[)
    il contient la derniere entrée (points) de ce jour pour chaque joueur
    """

    def __init__(self):
        self.entries = {}

    # plus simple de faire try/except que de verifier si l'entrée existe. :/
    def addEntry(self, entry):
        try:
            self.entries[str(entry.id)] = (
                entry.name,
                max(self.entries[str(entry.id)][1], entry.points))
        except KeyError:
            self.entries[str(entry.id)] = (entry.name, entry.points)

    def __str__(self):
        for entry in self.entries.items():
            print entry, '+', entries[entry][1]


class Score:

    def __init__(self, tuple):
        self.name = tuple[2]
        self.id = tuple[1]
        self.num = int(tuple[0])

    def __gt__(self, other):
        return self.num > other.num

    def __str__(self):
        rnum = str(self.num).rjust(10)
        rid = str(self.id).rjust(10)
        return rnum + rid + '    ' + self.name


class User:

    def __init__(self, postleft):
        if postleft.find('a'):
            self.id = int(postleft.find('a')['href'].split('=')[1])
            if self.id == 1205711:
                self.name = '<2028><2029>'
            elif self.id == 1205721:
                self.name = '<2029><2028>'
            else:
                self.name = HtmlToText(str(postleft.find('a').renderContents())
                                       )
        else:
            self.id = 0
            self.name = HtmlToText(str(postleft.strong.renderContents()))
        self.posts = []
        self.tz = tzFrance
        self.points = 0
        if postleft.find('img'):
            self.avatar = postleft.find('img')['src'].split('?')[0]
        else:
            self.avatar = ''

    def Points(self, hour):
        if hour in range(21, 24):
            self.points = hour - 20
        if hour in range(3):
            self.points = hour + 4
        if hour in [3, 4]:
            self.points = 10

    def __str__(self):
        return str(self.id) + ' ' + self.name + ' ' + str(self.points)


class Post:

    def __init__(self, post):
        self.url = post.find('h2').a['href']
        self.left = post.find('div', 'postleft')
        self.dt = DateTimePost(str(post.find('h2').a.renderContents()))
        self.edit = post.find('p', 'postedit')
        if self.edit:
            self.edit = DateTimePost(
                            str(self.edit).split('(')[-1].split(')')[0])

        # suppression des balises « quote »
        if post.find('div', 'quotebox'):
            for quote in post.findAll('div', 'quotebox'):
                quote.extract()
        # suppression des balises « code »
        if post.find('div', 'codebox'):
            for code in post.findAll('div', 'codebox'):
                code.extract()

        self.msg = post.find('div', 'postmsg').renderContents()
        if post.find('div', 'postsignature postmsg'):
            self.sign = post.find('div', 'postsignature postmsg'
                                  ).renderContents()
        else:
            self.sign = ''

    def localize(self, tz):
        self.dt = self.dt.astimezone(gettz(tz))
        if self.edit:
            self.edit = self.edit.astimezone(gettz(tz))

