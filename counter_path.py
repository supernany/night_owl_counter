#!/usr/bin/env python3
# coding: utf8

# auteur originel : Gabriel Pettier
# fork : nany
# license GPL V3 or later

# bibliothèque des chemins pour le compteur + url du forum
# nécessite python 3 minimum.

import os
import sys
from datetime import date

FORUM_URL = 'https://forum.ubuntu-fr.org/'
TOPIC_URL = 'viewtopic.php'

MYPATH = sys.path[0] + os.sep

LOGPATH = MYPATH + 'log'
if not os.path.exists(LOGPATH):
    if os.access(MYPATH, os.W_OK):
        os.mkdir(LOGPATH)
    else:
        LOGPATH = os.getenv('HOME') + os.sep + 'counter_files/log'
        if not os.path.exists(LOGPATH):
            os.makedirs(LOGPATH)
LOGPATH += os.sep
LOGFILE = LOGPATH + str(date.today())
POSTFILE = LOGFILE + '_post_TdCT'
STATFILE = LOGFILE + '_stat_TdCT'

FILESPATH = MYPATH + 'files'
if not os.path.exists(FILESPATH):
    if os.access(MYPATH, os.W_OK):
        os.mkdir(FILESPATH)
    else:
        LOGPATH = os.getenv('HOME') + os.sep + 'counter_files/files'
        if not os.path.exists(FILESPATH):
            os.makedirs(FILESPATH)
FILESPATH += os.sep

