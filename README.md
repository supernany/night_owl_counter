## night_owl_counter
Compteur pour le topic des couche-tard sur https://forum.ubuntu-fr.org


Le compteur fait les statistiques à 5:42 (heure de Paris) par le biais
de la commande counter_stat.py, puis il publie ces statistiques
à 6:42 (heure de Paris) par le biais de la commande counter_post.py stat.

Le compteur fait le compte des points à 19:10 (heure de Paris) alors que la
nuit a fait le tour de la planète par le biais de la commande counter.py,
puis il publie ces comptes à 19:42 (heure de Paris) par le biais de la
commande counter_post.py.

### Le profil du compteur sur le forum doit être réglé sur UTC sans heure d’été.

Un archivages des logs est effectué tous les mois par le biais de la commande
archives.sh.


Voici comment est le crontab :

42  5  * *  * /path/to/counter_directory/counter_stat.py

42  6  * *  * /path/to/counter_directory/counter_post.py stat

10 19  * *  * /path/to/counter_directory/counter.py

42 19  * *  * /path/to/counter_directory/counter_post.py

42  7  2 *  * /path/to/counter_directory/archives.sh
