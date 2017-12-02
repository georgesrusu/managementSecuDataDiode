#!/usr/local/bin/python
# -*- coding: latin-1 -*-
"""
----------------------------------------------------------------------------
BlindFTP v 0.37 - Unidirectional File Transfer Protocol
----------------------------------------------------------------------------

Pour transferer un fichier ou une arborescence complete a travers une liaison
reseau unidirectionnelle de type "diode", par UDP.

usage: voir bftp.py -h


Copyright Philippe Lagadec 2005-2008
Auteurs:
- Philippe Lagadec (PL) - philippe.lagadec(a)laposte.net
- Laurent Villemin (LV) - laurent.villemin(a)laposte.net
                          laurent.villemin(a)dga.defense.gouv.fr

Ce logiciel est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA
sur le site "http://www.cecill.info".

En contrepartie de l'accessibilité au code source et des droits de copie,
de modification et de redistribution accordés par cette licence, il n'est
offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
seule une responsabilité restreinte pèse sur l'auteur du programme,  le
titulaire des droits patrimoniaux et les concédants successifs.

A cet égard  l'attention de l'utilisateur est attirée sur les risques
associés au chargement,  à l'utilisation,  à la modification et/ou au
développement et à la reproduction du logiciel par l'utilisateur étant
donné sa spécificité de logiciel libre, qui peut le rendre complexe à
manipuler et qui le réserve donc à des développeurs et des professionnels
avertis possédant  des  connaissances  informatiques approfondies.  Les
utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
logiciel à leurs besoins dans des conditions permettant d'assurer la
sécurité de leurs systèmes et ou de leurs données et, plus généralement,
à l'utiliser et l'exploiter dans les mêmes conditions de sécurité.

Le fait que vous puissiez accéder à cet en-tête signifie que vous avez
pris connaissance de la licence CeCILL, et que vous en avez accepté les
termes.
"""

#------------------------------------------------------------------------------
# HISTORIQUE:
# 20/02/2005 v0.01 PL: - 1ère version (UFTP)
# 23/02/2005 v0.02 PL: - réception de fichier fonctionnelle
# 24/02/2005 v0.03 PL: - synchronisation simple d'arborescence
#                      - gestion des options avec optparse
# 06/04/2005 v0.04 PL: - correction temporaire de synchro_arbo, à reprendre
# 21/04/2005 v0.05 PL: - correction d'un bug dans Fichier.annuler_fichier()
#                        (close sur fichier temp non ouvert)
#                      - ajout de chemin_interdit() pour filtrer les chemins
#                        interdits: chemins absolus, contenant "..", ...
#                      - ajout options -b (boucle) et -P (pause)
#                      - classe LimiteurDebit pour contrôler le débit d'envoi
#                      - correction des chemins relatifs dans synchro_arbo
#                      - ajout print_oem, str_oem et str_lat1 pour corriger les
#                        problèmes dûs aux noms de fichiers avec accents
# 06/07/2005 v0.06 PL: - réception simultanée de plusieurs fichiers, avec
#                        gestion de la redondance (multiples fichiers temporaires,
#                        et gestion de paquets arrivant dans le désordre)
#                        --> modification complète du protocole et format des paquets
#                      - correction bug augmenter_priorite sous Unix
#                      - UFTP renommé en BlindFTP
# 11/07/2005 v0.07 PL: - correction d'un bug lié aux accents dans envoyer()
#                      - gestion (très spartiate) des exceptions
#                      - début de journalisation dans un fichier bftp.log
# 18/07/2005 v0.08 PL: - affichage du nom de fichier en cours de réception même si ignoré
# 18/07/2005 v0.09 PL: - affichage de l'heure pour chaque réception de fichier
#                      - correction d'un bug lié aux accents dans les logs
#                      - affichage complet des exceptions Python
# 21/07/2005 v0.10 PL: - format de paquet v3: ajout n°session et compteur de paquet
#                      - classe Stats pour mesurer taux de perte, débit effectif, ...
# 03/08/2005 v0.11 PL: - import Console pour améliorer l'affichage (à poursuivre)
#                      - ajout CRC32 d'un fichier pour détecter d'éventuels fichiers
#                        corrompus
#                      - correction tests sys.platform() == 'win32'
# 04/10/2005 v0.12 LV: - optimisation de l'algorithme de synchro d'arborescence
#                        priorisation aux fichiers les moins souvent transmis
# 22/02/2006 v0.13 LV: - optimisation des synchro (vérification que les fichiers à
#                        émettre sont stables)
# 04/03/2007 v0.14 PL: - verif import pywin32 et path
#                      - correction mot-clé "global"
#                      - correction limiteur_debit dans synchro_arbo
#                      - conversion tabs en espaces et corrections mineures
# 05/03/2007 v0.15 PL: - (re)correction limiteur_debit dans synchro_arbo
#                  LV: - exclusion des fichiers temporaires (extension .tmp)
# 17/03/2007 dev   LV: - simplification des exclusions des fichiers temporaires
#                      - extraction du calcul du CRC32
#                      - optimisation de la synchro ; utilisation d'un delai de
#                        transmission multifichiers pour synchro de grosses arborescences
#                        comme un repository linux
# 03/02/2008 v0.20 LV: - Refonte complete de la synchro (utilisation de ElementTree)
#                      - Sauvegarde de l'état de transmission dans un fichier XML
#                      - Option mode reprise
# 07/02/2008 v0.21 LV: - extraction du code XFL et import du module
# 10/02/2008 v0.22 LV: - correction bug 546 : Modification de l'entete pour supporter les fichiers de 4.5G et plus
#            v0.22a      Correction Bug 554 :
#            v0.22b      Correction bug 557 : Calcul automatique de la taille de l'entete
# 29/03/2008 v0.23  LV:- Mise en thread de la recopie de fichier
#                      - Integration du module TraitEncours
# 05/04/2008 v0.23a LV:- Correction Bug 573 :
#                      - Traitement exception ouverture fichier
#                      - Amelioration de l'affichage
# 15/04/2008 v0.23b PL:- correction partielle pour affichage de l'aide
# 27/10/2008 v0.24  LV:- Vérification pré emission de stabilité
#                      - Correction boucle émission limitée à MinFileRedundancy et non MinFileRedundancy+1
#                      - Correction synchro arbo mode boucle (plus de sortie sur aucun fichier à emetre)
#                      - Correction affichage de l'aide (UnicodeError) - "reprise à/a chaud"
# 03/11/2008 v0.25 PL: - reduction de TAILLE_PAQUET sous MacOSX
#                      - quelques corrections mineures
#                      - remplacement de str_lat1 et print_oem par module plx
# 15/08/2010 v0.30 LV: - Ajout des messages Heart Beat
# xx/09/2010 v0.35 LV: - Mode synchro stricte avec suppression des fichiers
# xx/10/2010 v0.36 LV: - Correction bug 4868 Erreur d'encodage latin 1
#                      - Ajout affichage sur console lors des operations longues
#                      - Correction bug 4901 Non transmission de fichiers timestamp en mode boucle sur gros volume
# 17/11/2010 v0.37 LV: - Sauvegarde en ".bak" du fichier de reprise BFTPsynchro.xml
# xx/xx/xxxx v0.40 LV: - en cours de dev
#                      - Fichier Ini

#------------------------------------------------------------------------------
# A FAIRE:
# - mettre les extensions de fichiers à exclure dans une liste paramétrable
# - fichier de config style .ini
# - reprendre la gestion des numéros de session avec l'ordonnanceur de synchro_arbo
# - corriger bug du a la taille max des paquets UDP sous MacOSX (setsockopt ?)
#   => cf. TAILLE_PAQUET

#=== IMPORTS ==================================================================

import sys, socket, struct, time, os, os.path, tempfile, logging, traceback
import binascii
import threading
import ConfigParser

# Dedicated Windows modules
if sys.platform == 'win32':
    try:
        import win32api, win32process
    except:
        raise ImportError, "the pywin32 module is not installed: "\
            +"see http://sourceforge.net/projects/pywin32"

# path.py module import
try:
    from path import path
except:
    raise ImportError, "the path module is not installed:"\
        +" see http://www.jorendorff.com/articles/python/path/"\
        +" or http://pypi.python.org/pypi/path.py/ (if first URL is down)"

# ElementTree for pythonic XML:
try:
    # ElementTree is included in the standard library since Python 2.5
    import xml.etree.ElementTree as ET
except:
    try:
        # external ElemenTree for Python <=2.4
        import elementtree.ElementTree as ET
    except:
        raise ImportError, "the ElementTree module is not installed:"\
            +" see http://effbot.org/zone/element-index.htm"

# XFL - Python module to create and compare file lists in XML
try:
    import xfl
except:
    raise ImportError, "the XFL module is not installed:"\
        +" see http://www.decalage.info/python/xfl"

# plx - portability layer extension
try:
    from plx import str_lat1, print_console
except:
    raise ImportError, 'the plx module is not installed:'\
        +' see http://www.decalage.info/en/python/plx'

# internal modules
from OptionParser_doc import *
import TabBits, Console
import TraitEncours


#=== CONSTANTES ===============================================================

NOM_SCRIPT = os.path.basename(__file__)    # script filename

ConfigFile = 'bftp.ini'
RunningFile = 'bftp_run.ini'

# Network Packet Max size
if sys.platform == 'darwin':
    # With MacOSX exception 'Message too long' if size is too long
    TAILLE_PAQUET = 1500
else:
    TAILLE_PAQUET = 65500

MODE_DEBUG = True   # check if debug() messages are displayed

RACINE_TEMP = "temp"    # Tempfile root

MAX_NOM_FICHIER = 1024  # Max length for the filename field

HB_DELAY = 10 # Default time between two Heartbeat

# en synchro stricte durée de rétention
# un fichier disparu/effacé sur le guichet bas est effacé coté haut après ce délai
OFFLINEDELAY = 86400*7 # 86400 vaut 1 jour

IgnoreExtensions = ('.part', '.tmp', '.ut', '.dlm') #  Extensions of temp files which are never send (temp files)

# Correction du bug sur taille des fichiers de plus de 4.5 Go
#      Modification de la structure (taille + offset de Int(I) en Long Long (Q))

# Header fields of BFTP data (format v4) :
# check help of module struct for the codes
# - type de paquet: uchar=B
# - longueur du nom de fichier (+chemin): uchar=B
# - longueur des données du fichier dans le paquet: uint16=H
# - offset, position des données dans le fichier: Long Long =Q
# - numéro de session: uint32=I
# - n° de paquet dans la session: uint32=I
# - n° de paquet du fichier: uint32=I
# - nombre de paquets pour le fichier: uint32=I
# - longueur du fichier (en octets): Long Long=Q
# - date du fichier (en secondes depuis epoch): uint32=I
# - CRC32 du fichier: int32=i (signé)
# (suivi du nom du fichier, puis des données)
FORMAT_ENTETE = "BBHQIIIIQIi"
# Correction bug 557 : taille du format diffère selon les OS
TAILLE_ENTETE = struct.calcsize(FORMAT_ENTETE)
# size : Win32 (48) ; Linux (44) ; MacOSX PPC (44)

# Types de paquets:
PAQUET_FICHIER      = 0  # File
PAQUET_REPERTOIRE   = 1  # Directory (not yet use)
PAQUET_HEARTBEAT    = 10 # HeartBeat
PAQUET_DELETEFile   = 16 # File Delete

# Complement d'attributs à XFL
ATTR_CRC = "crc" 			            # File CRC
ATTR_NBSEND = "NbSend"		        	# Number of send
ATTR_LASTVIEW = "LastView"	        	# Last View Date
ATTR_LASTSEND = "LastSend"	        	# Last Send Date

#=== Valeurs à traiter au sein du fichier .ini in fine ========================
MinFileRedundancy = 5

#=== VARIABLES GLOBALES =======================================================

# pour stocker les options (cf. analyse_options)
# options parameters
global options
options = None

# dictionnaire des fichiers en cours de réception
# receiving files dictionnary
global fichiers
fichiers = {}

# pour mesurer les stats de reception:

stats = None

#------------------------------------------------------------------------------
# str_ajuste : Adjust string to a dedicated length adding space or cutting string
#-------------------
def str_ajuste (chaine, longueur=79):
    """ajuste la chaine pour qu'elle fasse exactement la longueur indiquée,
    en coupant ou en remplissant avec des espaces."""
    l = len(chaine)
    if l>longueur:
        return chaine[0:longueur]
    else:
        return chaine + " "*(longueur-l)

#------------------------------------------------------------------------------
# DEBUG : Display debug messages if MODE_DEBUG is True
#-------------------

def debug(texte):
    "pour afficher un texte si MODE_DEBUG = True"

    if MODE_DEBUG:
        print_console ("DEBUG:" + texte)


#------------------------------------------------------------------------------
# EXIT_AIDE : Display Help in case of error
#-------------------

def exit_aide():
    "Affiche un texte d'aide en cas d'erreur."

    # on affiche la docstring (en début de ce fichier) qui contient l'aide.
    print __doc__
    sys.exit(1)


#------------------------------------------------------------------------------
# MTIME2STR : Convert date as a string
#-------------------

def mtime2str(date_fichier):
    "Convertit une date de fichier en chaine pour l'affichage."
    localtime = time.localtime(date_fichier)
    return time.strftime('%d/%m/%Y %H:%M:%S', localtime)


#------------------------------------------------------------------------------
# classe STATS
#-------------------

class Stats:
    """classe permettant de calculer des statistiques sur les transferts."""

    def __init__(self):
        """Constructeur d'objet Stats."""
        self.num_session = -1
        self.num_paquet_attendu = 0
        self.nb_paquets_perdus = 0

    def ajouter_paquet (self, paquet):
        """pour mettre à jour les stats en fonction du paquet."""
        # on vérifie si on est toujours dans la même session, sinon RAZ
        if paquet.num_session != self.num_session:
            self.num_session = paquet.num_session
            self.num_paquet_attendu = 0
            self.nb_paquets_perdus = 0
        # a-t-on perdu des paquets ?
        if paquet.num_paquet_session != self.num_paquet_attendu:
            self.nb_paquets_perdus += paquet.num_paquet_session - self.num_paquet_attendu
        self.num_paquet_attendu = paquet.num_paquet_session + 1

    def taux_perte (self):
        """calcule le taux de paquets perdus, en pourcentage"""
        # num_paquet_attendu correspond au nombre de paquets envoyés de la session
        if self.num_paquet_attendu > 0:
            taux = (100 * self.nb_paquets_perdus) / self.num_paquet_attendu
        else:
            taux = 0
        return taux

    def print_stats (self):
        """affiche les stats"""
        print 'Taux de perte: %d%%, paquets perdus: %d/%d' % (self.taux_perte(),
            self.nb_paquets_perdus, self.num_paquet_attendu)

#------------------------------------------------------------------------------
# CHEMIN_INTERDIT
#-------------------

def chemin_interdit (chemin):
    """Vérifie si le chemin de fichier demandé est interdit, par exemple
    s'il s'agit d'un chemin absolu, s'il contient "..", etc..."""
    # si chemin n'est pas une chaine on le convertit:
#   if not isinstance(chemin, str):
#       chemin = str(chemin)
    # est-ce un chemin absolu pour Windows avec une lettre de lecteur ?
    if len(chemin)>=2 and chemin[0].isalpha() and chemin[1]==":":
        return True
    # est-ce un chemin absolu qui commence par "/" ou "\" ?
    if chemin.startswith("/") or chemin.startswith("\\"):
        return True
    # est-ce qu'il contient ".." ?
    if ".." in chemin:
        return True
    if "*" in chemin:
        return True
    if "?" in chemin:
        return True
    # A AJOUTER: vérifier si codage unicode, ou autre ??
    # Sinon c'est OK, le chemin est valide:
    return False

#------------------------------------------------------------------------------
# classe FICHIER
#-------------------

class Fichier:
    """classe représentant un fichier en cours de réception."""

    def __init__(self, paquet):
        """Constructeur d'objet Fichier.

        paquet: objet paquet contenant les infos du fichier."""

        self.nom_fichier = paquet.nom_fichier
        self.date_fichier = paquet.date_fichier
        self.taille_fichier = paquet.taille_fichier
        self.nb_paquets = paquet.nb_paquets
        # chemin du fichier destination
        self.fichier_dest = CHEMIN_DEST / self.nom_fichier
        debug('fichier_dest = "%s"' % self.fichier_dest)
        # on crée le fichier temporaire (objet file):
        self.fichier_temp = tempfile.NamedTemporaryFile(prefix='BFTP_')
        debug('fichier_temp = "%s"' % self.fichier_temp.name)
        self.paquets_recus = TabBits.TabBits(self.nb_paquets)
        #print 'Reception du fichier "%s"...' % self.nom_fichier
        self.est_termine = False    # flag indiquant une réception complète
        self.crc32 = paquet.crc32 # CRC32 du fichier
        # on ne doit pas traiter le paquet automatiquement, sinon il peut
        # y avoir des problèmes d'ordre des actions
        #self.traiter_paquet(paquet)


    def annuler_reception(self):
        "pour annuler la réception d'un fichier en cours."
        # on ferme et on supprime le fichier temporaire
        # seulement s'il est effectivement ouvert
        # (sinon à l'initialisation c'est un entier)
        if isinstance(self.fichier_temp, file):
            if not self.fichier_temp.closed:
                self.fichier_temp.close()
        # d'après la doc de tempfile, le fichier est automatiquement supprimé
        #os.remove(self.nom_temp)
        debug('Reception de fichier annulee.')

    def recopier_destination(self):
        "pour recopier le fichier à destination une fois qu'il est terminé."
        print 'OK, fichier termine.'
        # créer le chemin destination si besoin avec makedirs
        chemin_dest = self.fichier_dest.dirname()
        if not os.path.exists(chemin_dest):
            chemin_dest.makedirs()
        elif not os.path.isdir(chemin_dest):
            chemin_dest.remove()
            chemin_dest.mkdir()
        # recopier le fichier temporaire au bon endroit
        debug('Recopie de %s vers %s...' % (self.fichier_temp.name, self.fichier_dest))
        # move(self.nom_temp, self.fichier_dest)
        # on revient au début
        self.fichier_temp.seek(0)
        f_dest = file(self.fichier_dest, 'wb')
        buffer = self.fichier_temp.read(16384)
        # on démarre le calcul de CRC32:
        crc32 = binascii.crc32(buffer)
        while len(buffer) != 0:
            f_dest.write(buffer)
            buffer = self.fichier_temp.read(16384)
            # poursuite du calcul de CRC32:
            crc32 = binascii.crc32(buffer, crc32)
        f_dest.close()
        # vérifier si la taille obtenue est correcte
        if self.fichier_dest.getsize() != self.taille_fichier:
            debug ("taille_fichier = %d, taille obtenue = %d" %
                   (self.taille_fichier, self.fichier_dest.getsize()) )
            logging.error('Taille du fichier incorrecte: "%s"'% self.nom_fichier)
            raise IOError, 'taille du fichier incorrecte.'
        # vérifier si le checksum CRC32 est correct
        if self.crc32 != crc32:
            debug ("CRC32 fichier = %X, CRC32 attendu = %X" %
                   (crc32, self.crc32))
            logging.error('Controle d\'integrite incorrect: "%s"'% self.nom_fichier)
            raise IOError, "controle d'integrite incorrect."
        # mettre à jour la date de modif: tuple (atime,mtime)
        self.fichier_dest.utime( (self.date_fichier, self.date_fichier) )
        # fermer le fichier temporaire
        self.fichier_temp.close()
        # d'après la doc de tempfile, le fichier est automatiquement supprimé
        self.fichier_en_cours = False
        # Affichage de fin de traitement
        debug ("Fichier termine.")
        logging.info('Fichier "%s" recu en entier, recopie a destination.'% self.nom_fichier)
        # dans ce cas on retire le fichier du dictionnaire
        self.est_termine = True
        del fichiers[self.nom_fichier]

    def traiter_paquet(self, paquet):
        "pour traiter un paquet contenant un morceau du fichier."
        # on vérifie si le paquet n'a pas déjà été reçu
        if not self.paquets_recus.get (paquet.num_paquet):
            # c'est un nouveau paquet: il faut l'écrire dans le fichier temporaire
            # on calcule l'offset dans le fichier, en considérant que chaque
            # paquet contient la même longueur de données:
            #offset = paquet.num_paquet * paquet.taille_donnees
            #debug("offset = %d" % offset)
            self.fichier_temp.seek(paquet.offset)
            # note: si on déplace le curseur après la fin réelle du fichier,
            # celui-ci est complété d'octets nuls, ce qui nous arrange bien :-).
            self.fichier_temp.write(paquet.donnees)
            debug("offset apres = %d" % self.fichier_temp.tell())
            self.paquets_recus.set(paquet.num_paquet, True)
            pourcent = 100*(self.paquets_recus.nb_true)/self.nb_paquets
            # affichage du pourcentage: la virgule évite un retour chariot
            print "%d%%\r" % pourcent,
            # pour forcer la mise à jour de l'affichage
            sys.stdout.flush()
            # si le fichier est terminé, on le recopie à destination:
            if self.paquets_recus.nb_true == self.nb_paquets:
                # on va à la ligne
                #print ""
                # Mise en thread de la recopie afin de liberer de la ressource pour la réception
                recopie=threading.Thread(None, self.recopier_destination, None,())
                recopie.start()
                # ...et on suppose qu'il n'y a plus d'autres références:
                # le garbage collector devrait le supprimer de la mémoire.

#------------------------------------------------------------------------------
# classe PAQUET
#-------------------

class Paquet:
    """classe représentant un paquet BFTP, permettant la construction et le
    décodage du paquet."""

    def __init__(self):
        "Constructeur d'objet Paquet BFTP."
        # on initialise les infos contenues dans l'entête du paquet
        self.type_paquet = PAQUET_FICHIER
        self.longueur_nom = 0
        self.taille_donnees = 0
        self.offset = 0
        self.num_paquet = 0
        self.nom_fichier = ""
        self.nb_paquets = 0
        self.taille_fichier = 0
        self.date_fichier = 0
        self.donnees = ""
        self.fichier_en_cours = ""
        self.num_session = -1
        self.num_paquet_session = -1

    def decoder(self, paquet):
        "Pour décoder un paquet BFTP."
        # on décode d'abord l'entête (cf. début de ce fichier):
        entete = paquet[0:TAILLE_ENTETE]
        (
            self.type_paquet,
            self.longueur_nom,
            self.taille_donnees,
            self.offset,
            self.num_session,
            self.num_paquet_session,
            self.num_paquet,
            self.nb_paquets,
            self.taille_fichier,
            self.date_fichier,
            self.crc32
        ) = struct.unpack(FORMAT_ENTETE, entete)
        debug("type_paquet        = %d" % self.type_paquet)
        debug("longueur_nom       = %d" % self.longueur_nom)
        debug("taille_donnees     = %d" % self.taille_donnees)
        debug("offset             = %d" % self.offset)
        debug("num_session        = %d" % self.num_session)
        debug("num_paquet_session = %d" % self.num_paquet_session)
        debug("num_paquet         = %d" % self.num_paquet)
        debug("nb_paquets         = %d" % self.nb_paquets)
        debug("taille_fichier     = %d" % self.taille_fichier)
        debug("date_fichier       = %s" % mtime2str(self.date_fichier))
        debug("CRC32              = %08X" % self.crc32)
        if self.type_paquet not in [PAQUET_FICHIER, PAQUET_HEARTBEAT, PAQUET_DELETEFile]:
            raise ValueError, 'type de paquet incorrect'
        if self.type_paquet == PAQUET_FICHIER:
            if self.longueur_nom > MAX_NOM_FICHIER:
                raise ValueError, 'nom de fichier trop long'
            if self.offset + self.taille_donnees > self.taille_fichier:
                raise ValueError, 'offset ou taille des donnees incorrects'
            self.nom_fichier = paquet[TAILLE_ENTETE : TAILLE_ENTETE + self.longueur_nom]
            # conversion en utf-8 pour éviter problèmes dûs aux accents
            # A VOIR: seulement sous Windows ?? (sous Mac ça pose problème...)
            if sys.platform == 'win32':
                self.nom_fichier = self.nom_fichier.decode('utf_8','strict')
            ##debug("nom_fichier    = %s" % self.nom_fichier)
            if chemin_interdit(self.nom_fichier):
                logging.error('nom de fichier ou de chemin incorrect: %s' % self.nom_fichier)
                raise ValueError, 'nom de fichier ou de chemin incorrect'
            taille_entete_complete = TAILLE_ENTETE + self.longueur_nom
            if self.taille_donnees != len(paquet) - taille_entete_complete:
                debug("taille_paquet = %d" % len(paquet))
                debug("taille_entete_complete = %d" % taille_entete_complete)
                raise ValueError, 'taille de donnees incorrecte'
            self.donnees = paquet[taille_entete_complete:len(paquet)]
            # on mesure les stats, et on les affiche tous les 100 paquets
            stats.ajouter_paquet(self)
            #if self.num_paquet_session % 100 == 0:
                #stats.print_stats()
            # est-ce que le fichier est en cours de réception ?
            if self.nom_fichier in fichiers:
                debug("Fichier en cours de reception")
                f = fichiers[self.nom_fichier]
                # on vérifie si le fichier n'a pas changé:
                if f.date_fichier != self.date_fichier \
                or f.taille_fichier != self.taille_fichier \
                or f.crc32 != self.crc32:
                    # on commence par annuler la réception en cours:
                    f.annuler_reception()
                    del fichiers[self.nom_fichier]
                    # puis on recrée un nouvel objet fichier d'après les infos du paquet:
                    self.nouveau_fichier()
                else:
                    if self.fichier_en_cours != self.nom_fichier:
                        # on change de fichier
                        msg = 'Suite de "%s"...' % self.nom_fichier
                        heure = time.strftime('%d/%m %H:%M ')
                        # Vérifier si un NL est nécessaire ou non
                        Console.Print_temp(msg, NL=True)
                        logging.info(msg)
                        self.fichier_en_cours = self.nom_fichier
                    f.traiter_paquet(self)
            else:
                # est-ce que le fichier existe déjà sur le disque ?
                fichier_dest = CHEMIN_DEST / self.nom_fichier
                ##debug('fichier_dest = "%s"' % fichier_dest)
                # si la date et la taille du fichier n'ont pas changé,
                # inutile de recréer le fichier, on l'ignore:
                if  fichier_dest.exists() \
                and fichier_dest.getsize() == self.taille_fichier \
                and fichier_dest.getmtime() == self.date_fichier:
                    #debug("Le fichier n'a pas change, on l'ignore.")
                    msg = 'Fichier deja recu: %s' % self.nom_fichier
                    #msg = str_ajuste(msg)+'\r'
                    #print_oem(msg),
                    Console.Print_temp(msg)
                    sys.stdout.flush()
                else:
                    # sinon on crée un nouvel objet fichier d'après les infos du paquet:
                    self.nouveau_fichier()
        if self.type_paquet == PAQUET_HEARTBEAT:
            debug("Reception HEARTBEAT")
            HeartBeat.check_heartbeat(HB_recus, self.num_session, self.num_paquet_session, self.num_paquet)
        if self.type_paquet == PAQUET_DELETEFile:
            debug("Reception DeleteFile notification")
            self.nom_fichier = paquet[TAILLE_ENTETE : TAILLE_ENTETE + self.longueur_nom]
            if sys.platform == 'win32':
                self.nom_fichier = self.nom_fichier.decode('utf_8', 'strict')
            fichier_dest = CHEMIN_DEST / self.nom_fichier
            # Test pour bloquer en présence de caracteres joker ou autres
            if chemin_interdit(self.nom_fichier):
                msg = 'Notification pour effacement suspecte "%s"...' % self.nom_fichier
                Console.Print_temp(msg, NL=True)
                logging.error(msg)
            else:
                msg = 'Effacement de "%s"...' % self.nom_fichier
                if fichier_dest.isfile():
                    try:
                        os.remove(fichier_dest)
                    except (OSError):
                        msg = 'Echec effacement de "%s"...' % self.nom_fichier
                        logging.warn(msg)
                    Console.Print_temp(msg, NL=True)
                    # log à supprimer après qualif.
                    logging.info(msg)
                if fichier_dest.isdir():
                    # TODO Supression de dossier vide à coder coté bas (émission)
                    logging.info("suppression de dossier")
                    try:
                        os.rmdir(fichier_dest)
                    except(OSError):
                        msg = 'Echec de effacement de "%s"...' % self.nom_fichier
                        Console.Print_temp(msg, NL=True)
                        logging.warn(msg)

    def nouveau_fichier (self):
        "pour débuter la réception d'un nouveau fichier."
        msg = 'Reception de "%s"...' % self.nom_fichier
        heure = time.strftime('%d/%m %H:%M ')
        #msg = str_ajuste(msg)+'\r'
        #print_oem(heure + msg)
        Console.Print_temp(msg, NL=True)
        logging.info(msg)
        self.fichier_en_cours = self.nom_fichier
        debug("Nouveau fichier ou fichier mis a jour")
        # on crée un nouvel objet fichier d'après les infos du paquet:
        nouveau_fichier = Fichier(self)
        fichiers[self.nom_fichier] = nouveau_fichier
        nouveau_fichier.traiter_paquet(self)

    def construire(self):
        "pour construire un paquet BFTP à partir des paramètres. (non implémenté)"
        raise NotImplementedError


#------------------------------------------------------------------------------
# HeartBeat - dépendant de la classe de paquet
#---------------
class HeartBeat:
    """ Generate and check HeartBeat BFTP packet

        A session is a heartbeat sequence.
        A heartbeat is a simple packet with a timestamp (Session Id + sequence
        number) to identify if the link (physical and logical) is up or down

        The session Id will identify a restart
        The sequence number will identify lost paquet

        Because time synchronisation betwen emission/reception computer isn't garantee,
        timestamp can't be check in absolute.
        """

    # TODO :
    # Add HB from reception to emission in broadcast to detect bi-directional link

    def __init__(self):
        #Variables locales
        self.hb_delay=HB_DELAY
        self.hb_numsession=0
        self.hb_numpaquet=0
        self.hb_timeout=time.time()+1.25*(self.hb_delay)

    def newsession(self):
        """ initiate values for a new session """
        self.hb_numsession=int(time.time())
        self.hb_numpaquet=0
        return(self.hb_numsession, self.hb_numpaquet)

    def incsession(self):
        """ increment values in a existing session """
        self.hb_numpaquet+=1
        self.hb_timeout=time.time()+(self.hb_delay)
        return(self.hb_numpaquet, self.hb_timeout)

    def print_heartbeat(self):
        """ Print internal values of heartbeat """
        print ("----- Current HeartBeart -----")
        print ("Session ID      : %d " %self.hb_numsession)
        print ("Seq             : %d " %self.hb_numpaquet)
        print ("Delay           : %d " %self.hb_delay)
        print ("Current Session : %s " %mtime2str(self.hb_numsession))
        print ("Next Timeout    : %s " %mtime2str(self.hb_timeout))
        print ("----- ------------------ -----")

    def check_heartbeat(self, num_session, num_paquet, delay):
        """ Check and diagnostic last received heartbeat paquet """
        msg=None
        #self.print_heartbeat()
        # new session identification (session restart)
        if self.hb_numsession != num_session:
                if num_paquet==0 :
                    msg = 'HeartBeat : emission redemarree'
                    logging.info(msg)
                # lost packet in a new session (reception start was too late)
                else:
                    # TODO : vérifier cas du redemarrage de la reception (valeurs locales à 0)
                    if (self.hb_numpaquet==0 and self.hb_numsession==0):
                        msg = 'HeartBeat : reception redemaree'
                        logging.info(msg)
                    else:
                        msg = 'HeartBeat : emission redemaree, perte de %d paquet(s)' %num_paquet
                        logging.warn(msg)
                # Set correct num_session
                self.hb_numsession=num_session
        # lost packet identification
        else:
            hb_lost=num_paquet-self.hb_numpaquet-1
            if bool(hb_lost) :
                msg = 'HeartBeat : perte de %d paquet(s)' % hb_lost
                logging.warn(msg)
        # Set new values
        self.hb_numpaquet=num_paquet
        self.hb_timeout=time.time()+1.5*(delay)
        if msg != None:
            Console.Print_temp(msg, NL=True)
            sys.stdout.flush()


    def checktimer_heartbeat(self):
        "Timer to send alarm if no heartbeat are received"
        #self.print_heartbeat()
        Nbretard=0
        while True:
            if self.hb_timeout < time.time():
                Nbretard+=1
                delta=time.time()-self.hb_timeout
                msg = 'HeartBeat : Reception en attente ( %d ) ' % self.hb_numpaquet
                Console.Print_temp(msg, NL=False)
                sys.stdout.flush()
                time.sleep(self.hb_delay-1)
                if Nbretard%10==0:
                    msg = 'HeartBeat : Retard de reception ( %d ) - %d ' % (self.hb_numpaquet, Nbretard/10)
                    logging.warn(msg)
                    Console.Print_temp(msg, NL=True)
            else:
                Nbretard=0
            time.sleep(1)

    def Th_checktimeout_heartbeatT(self):
        """ thead to send heartbeat """
        Sendheartbeat=threading.Thread(None, self.checktimer_heartbeat, None)
        Sendheartbeat.start()


    def send_heartbeat(self, message=None, num_session=None, num_paquet=None):
        """ Send a heartbeat packet """
        # un HeartBeat est un paquet court donnant un timestamp qui pourra être vérifié à la réception
        # on donne un numero de session afin de tracer coté haut une relance du guichet bas
        # num paquet permet de tracer les iterations au sein d'une session

        # Affectation statique pour tests et qualification du mod
        if num_session == None:
            num_session=self.hb_numsession
        if num_paquet == None:
            num_paquet=self.hb_numpaquet
        if message == None:
            message="HeartBeat"
        taille_donnees=len(message)
        debug("sending HB...")
        #self.print_heartbeat()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # on commence par packer l'entete:
        entete = struct.pack(FORMAT_ENTETE,
            PAQUET_HEARTBEAT,
            0,
            taille_donnees,
            0,
            num_session,
            num_paquet,
            self.hb_delay,
            1,
            0,
            0,
            0
            )
        paquet = entete + message
        s.sendto(paquet, (HOST, PORT))
        s.close()

    def envoyer_Boucleheartbeat(self):
        """A loop to send heartbeat sequence every X seconds"""
        self.newsession()
        while True:
            self.send_heartbeat()
            self.incsession()
            time.sleep(self.hb_delay)


    def Th_envoyer_BoucleheartbeatT(self):
        """ thead to send heartbeat """
        Sendheartbeat=threading.Thread(None, self.envoyer_Boucleheartbeat, None)
        Sendheartbeat.start()

#------------------------------------------------------------------------------
# LimiteurDebit
#-------------------

class LimiteurDebit:
    "pour controler le débit d'envoi de données."

    def __init__(self, debit):
        """contructeur de classe LimiteurDebit.

        debit : débit maximum autorisé, en Kbps."""
        # débit en Kbps converti en octets/s
        self.debit_max = debit*1000/8
        debug ("LimiteurDebit: debit_max = %d octets/s" % self.debit_max)
        # on stocke le temps de départ
        self.temps_debut = time.time()
        # nombre d'octets déjà transféré
        self.octets_envoyes = 0

    def depart_chrono(self):
        "pour (re)démarrer la mesure du débit."
        self.temps_debut = time.time()
        self.octets_envoyes = 0

    def ajouter_donnees(self, octets):
        "pour ajouter un nombre d'octets envoyés."
        self.octets_envoyes += octets

    def temps_total(self):
        "donne le temps total de mesure."
        return (time.time() - self.temps_debut)

    def debit_moyen(self):
        "donne le débit moyen mesuré, en octets/s."
        temps_total = self.temps_total()
        if temps_total == 0: return 0   # pour éviter division par zéro
        debit_moyen = self.octets_envoyes / temps_total
        return debit_moyen

    def limiter_debit(self):
        "pour faire une pause afin de respecter le débit maximum."
        # on fait des petites pauses (10 ms) tant que le débit est trop élevé:
        while self.debit_moyen() > self.debit_max:
            time.sleep(0.01)
        # méthode alternative qui ne fonctionne pas très bien
        # (donne souvent des temps de pause négatifs !)
#       temps_total = self.temps_total()
#       debit_moyen = self.debit_moyen()
#       # si on dépasse le débit max, on calcule la pause:
#       if debit_moyen > self.debit_max:
#           pause = self.octets_envoyes/self.debit_max - temps_total
#           if pause>0:
#               debug ("LimiteurDebit: pause de %.3f s..." % pause)
#               time.sleep(pause)


#------------------------------------------------------------------------------
# RECEVOIR
#-------------------

def recevoir(repertoire):
    """Pour recevoir les paquets UDP BFTP contenant les fichiers, et stocker
    les fichiers reçus dans le répertoire indiqué en paramètre."""

    # bidouille: on change le contenu de la variable globale
    CHEMIN_DEST = repertoire
    print 'Les fichiers seront recus dans le repertoire "%s".' % str_lat1(CHEMIN_DEST.abspath(),errors='replace')
    print 'En ecoute sur le port UDP %d...' % PORT
    print '(taper Ctrl+Pause pour quitter)'
    p = Paquet()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
    while 1:
        debug("")
        paquet, emetteur = s.recvfrom(TAILLE_PAQUET)
        debug ('emetteur: '+str(emetteur))
        if not paquet: break
        #print 'donnees recues:'
        #print paquet
        try:
            p.decoder (paquet)
        except:
            msg = "Erreur lors du decodage d'un paquet: %s" % traceback.format_exc(1)
            print msg
            traceback.print_exc()
            logging.error(msg)


#------------------------------------------------------------------------------
# CalcCRC
#-------------------
def CalcCRC(fichier):
    """Calcul du CRC32 du fichier."""

    debug('Calcul de CRC32 pour "%s"...' % fichier)
    MonAff=TraitEncours.TraitEnCours()
    MonAff.StartIte()
    chaine=" Calcul CRC32 " + fichier
    MonAff.NewChaine(chaine, truncate=True)
    try:
        f = open(fichier, 'rb')
        buffer = f.read(16384)
        # on démarre le calcul de CRC32:
        crc32 = binascii.crc32(buffer)
        while len(buffer) != 0:
            buffer = f.read(16384)
            # poursuite du calcul de CRC32:
            crc32 = binascii.crc32(buffer, crc32)
            MonAff.AffLigneBlink()
        f.close()
        debug("CRC32 = %08X" % crc32)
    except IOError:
            #print "Erreur : CRC32 Ouverture impossible de %s" %fichier
            crc32=0
    return(crc32)

#------------------------------------------------------------------------------
# SendDeleteFileMessage
#-------------------
def SendDeleteFileMessage(fichier):
    """ Emet un message de suppression du fichier coté haut
    """
    # Doit on ajouter des éléments de Dref (taille/date) pour consolider l'ordre à la reception ?
    debug("Sending DeleteFileMessage...")
    if sys.platform == 'win32':
        # sous Windows on doit corriger les accents
        nom_fichier = fichier.encode('utf_8','strict')
    else:
        # sinon ça a l'air de passer
        nom_fichier = str(fichier)
    taille=len(nom_fichier)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # on commence par packer l'entete:
    entete = struct.pack(
        FORMAT_ENTETE,
        PAQUET_DELETEFile,
        taille,
        taille,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
        0
        )
    paquet = entete + nom_fichier
    s.sendto(paquet, (HOST, PORT))
    s.close()

#------------------------------------------------------------------------------
# ENVOYER
#-------------------

def envoyer(fichier_source, fichier_dest, limiteur_debit=None, num_session=None,
    num_paquet_session=None, crc=None):
    """Pour émettre un fichier en paquets UDP BFTP.

    fichier_source : chemin du fichier source sur le disque local
    fichier_dest   : chemin relatif du fichier dans le répertoire destination
    limiteur_debit : pour limiter le débit d'envoi
    num_session    : numéro de session
    num_paquet_session : compteur de paquets
    """

    msg = "Envoi du fichier %s..." % fichier_source
    Console.Print_temp(msg,NL=True)
    logging.info(msg)
    if num_session == None:
        num_session = int(time.time())
        num_paquet_session = 0
    debug("num_session         = %d" % num_session)
    debug("num_paquet_session  = %d" % num_paquet_session)
    debug("fichier destination = %s" % fichier_dest)
    if sys.platform == 'win32':
        # sous Windows on doit corriger les accents
        nom_fichier_dest = fichier_dest.encode('utf_8','strict')
    else:
        # sinon ça a l'air de passer
        nom_fichier_dest = str(fichier_dest)
    longueur_nom = len(nom_fichier_dest)
    debug("longueur_nom = %d" % longueur_nom)
    if longueur_nom > MAX_NOM_FICHIER:
        raise ValueError
    if fichier_source.isfile():
        taille_fichier = fichier_source.getsize()
        date_fichier = fichier_source.getmtime()
        debug("taille_fichier = %d" % taille_fichier)
        debug("date_fichier = %s" % mtime2str(date_fichier))
        # calcul de CRC32
        if crc==None:
            crc32=CalcCRC(fichier_source)
        else:
            crc32=crc
    # taille restant pour les données dans un paquet normal
    taille_donnees_max = TAILLE_PAQUET - TAILLE_ENTETE - longueur_nom
    debug("taille_donnees_max = %d" % taille_donnees_max)
    nb_paquets = (taille_fichier + taille_donnees_max-1) / taille_donnees_max
    if nb_paquets == 0:
        # si le fichier est vide, il faut quand même envoyer un paquet
        nb_paquets = 1
    debug("nb_paquets = %d" % nb_paquets)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reste_a_envoyer = taille_fichier
    try:
        f = open(fichier_source, 'rb')
        if limiteur_debit == None:
            # si aucun limiteur fourni, on en initialise un:
            limiteur_debit = LimiteurDebit(options.debit)
        limiteur_debit.depart_chrono()
        for num_paquet in range(0, nb_paquets):
            # on fait une pause si besoin pour limiter le débit
            limiteur_debit.limiter_debit()
            if reste_a_envoyer > taille_donnees_max:
                taille_donnees = taille_donnees_max
            else:
                taille_donnees = reste_a_envoyer
            reste_a_envoyer -= taille_donnees
            offset = f.tell()
            donnees = f.read(taille_donnees)
            # on commence par packer l'entete:
            entete = struct.pack(
                FORMAT_ENTETE,
                PAQUET_FICHIER,
                longueur_nom,
                taille_donnees,
                offset,
                num_session,
                num_paquet_session,
                num_paquet,
                nb_paquets,
                taille_fichier,
                date_fichier,
                crc32
                )
            paquet = entete + nom_fichier_dest + donnees
            s.sendto(paquet, (HOST, PORT))
            num_paquet_session += 1
            limiteur_debit.ajouter_donnees(len(paquet))
            #debug("debit moyen = %d" % limiteur_debit.debit_moyen())
            #time.sleep(0.3)
            pourcent = 100*(num_paquet+1)/nb_paquets
            # affichage du pourcentage: la virgule évite un retour chariot
            print "%d%%\r" % pourcent,
            # pour forcer la mise à jour de l'affichage
            sys.stdout.flush()
        print "transfert en %.3f secondes - debit moyen %d Kbps" % (
        limiteur_debit.temps_total(), limiteur_debit.debit_moyen()*8/1000)
    except IOError:
        msg = "Ouverture du fichier %s..." % fichier_source
        print "Erreur : " + msg
        logging.error(msg)
        num_paquet_session=-1
    s.close()
    return num_paquet_session


#------------------------------------------------------------------------------
# SortDictBy
#-----------------
def sortDictBy(nslist, key):
    """
    Tri d'un dictionnaire sur un champ
    """
    nslist = map(lambda x, key=key: (x[key], x), nslist)
    nslist.sort()
    return map(lambda(key,x): x, nslist)

#------------------------------------------------------------------------------
# SYNCHRO_ARBO
#-------------------

def synchro_arbo(repertoire):
    """
    Synchroniser une arborescence en envoyant regulierement tous les
    fichiers.
    """

    logging.info('Synchronisation du repertoire "%s"' % str_lat1(repertoire, errors='replace'))

    # on utilise un objet LimiteurDebit global pour tout le transfert:
    limiteur_debit = LimiteurDebit(options.debit)

    # TODO : Distinguer le traitement d'une arborescence locale / distante
    if (0):
        print("arborescence locale")
        # TODO : Traitement Local des donnnées :
        #            - utiliser wath_directory pour détecter le besoin l'émission
    else:
        #print("arborescence distante")
        # Traitement distant des donnnées :
        #     Boucle 1 : Analyse et priorisation des fichiers
        AllFileSendMax=False
        # test pour affichage d'un motif cyclique
        monaff=TraitEncours.TraitEnCours()
        monaff.StartIte()
        while (not(AllFileSendMax) or options.boucle):
            print ("%s - Scrutation arborescence" %mtime2str(time.time()))
            Dscrutation = xfl.DirTree()
            if MODE_DEBUG:
                Dscrutation.read_disk(repertoire, xfl.callback_dir_print)
                #Dscrutation.read_disk(repertoire, xfl.callback_dir_print, xfl.callback_file_print)
            else:
                Dscrutation.read_disk(repertoire, None, monaff.AffCar)
                #Dscrutation.read_disk(repertoire)
            debug ("%s - Analyse arborescence" %mtime2str(time.time()))
            same, different, only1, only2 = xfl.compare_DT(Dscrutation, DRef)
            Console.Print_temp("%s - Traitement des fichiers supprimes" %mtime2str(time.time()))
            debug ("\n========== Supprimes ========== ")
            for f in sorted(only2, reverse=True):
                debug("S  "+f)
                monaff.AffCar()
                DeletionNeeded=False
                parent, myfile=f.splitpath()
                if(DRef.dict[f].tag == xfl.TAG_DIR):
                    # Vérifier la présence de fils (dir / file)
                    if not(bool(DRef.dict[f].getchildren())): DeletionNeeded=True
                if(DRef.dict[f].tag == xfl.TAG_FILE):
                    LastView=DRef.dict[f].get(ATTR_LASTVIEW)
                    NbSend=DRef.dict[f].get(ATTR_NBSEND)
                    if LastView == None: LastView=0
                    # Si Disparu depuis X jours ; on notifie la suppression
                    if (time.time() - (float(LastView) + OffLineDelay)) > 0:
                        if (NbSend == None): NbSend=-10
                        else:
                            if (NbSend >= 0):
                                NbSend=-1
                        for attr in (ATTR_LASTSEND, ATTR_CRC):
                            DRef.dict[f].set(attr, str(0))
                        if options.synchro_arbo_stricte:
                            SendDeleteFileMessage(f)
                        NbSend-=1
                        if NbSend > -10:
                            DRef.dict[f].set(ATTR_NBSEND, str(NbSend))
                        else:
                            DeletionNeeded=True
                if DeletionNeeded:
                    debug ("****** Suppression")
                    if parent == '':
                        DRef.et.remove(DRef.dict[f])
                    else:
                        DRef.dict[parent].remove(DRef.dict[f])
            Console.Print_temp("%s - Traitement des nouveaux fichiers " %mtime2str(time.time()))
            debug("\n========== Nouveaux  ========== ")
            RefreshDictNeeded=False
            for f in sorted(only1):
                # TODO : Optimiser le traitement
                # en cas de nombreux ajouts ; la reconstruction du dict est trop gourmande
                monaff.AffCar()
                debug("N  "+f)
                parent, myfile=f.splitpath()
                index=0
                if parent == '':
                    newET = ET.SubElement(DRef.et, Dscrutation.dict[f].tag)
                    index=len(DRef.et)-1
                    if (Dscrutation.dict[f].tag == xfl.TAG_FILE):
                        RefreshDictNeeded=True
                        for attr in (xfl.ATTR_NAME, xfl.ATTR_MTIME, xfl.ATTR_SIZE):
                            DRef.et[index].set(attr, Dscrutation.dict[f].get(attr))
                        for attr in (ATTR_LASTSEND, ATTR_CRC, ATTR_NBSEND):
                            DRef.et[index].set(attr, str(0))
                        DRef.et[index].set(ATTR_LASTVIEW, Dscrutation.et.get(xfl.ATTR_TIME))
                    else:
                        DRef.et[index].set(xfl.ATTR_NAME, Dscrutation.dict[f].get(xfl.ATTR_NAME))
                else:
                    newET = ET.SubElement(DRef.dict[parent], Dscrutation.dict[f].tag)
                    index=len(DRef.dict[parent])-1
                    if (Dscrutation.dict[f].tag == xfl.TAG_FILE):
                        RefreshDictNeeded=True
                        for attr in (xfl.ATTR_NAME, xfl.ATTR_MTIME, xfl.ATTR_SIZE):
                            DRef.dict[parent][index].set(attr, Dscrutation.dict[f].get(attr))
                        for attr in (ATTR_LASTSEND, ATTR_CRC, ATTR_NBSEND):
                            DRef.dict[parent][index].set(attr, str(0))
                        DRef.dict[parent][index].set(ATTR_LASTVIEW, (Dscrutation.et.get(xfl.ATTR_TIME)))
                    else:
                        DRef.dict[parent][index].set(xfl.ATTR_NAME, Dscrutation.dict[f].get(xfl.ATTR_NAME))
                # Reconstruction du dictionnaire pour faciliter l'insertion des sous éléments
                if (Dscrutation.dict[f].tag == xfl.TAG_DIR):
                    DRef.pathdict()
                    RefreshDict=False
            # reconstruction du dictionnaire si ajout uniquement de fichiers
            if RefreshDictNeeded:
                DRef.pathdict()
            Console.Print_temp("%s - Traitement des fichiers modifies" %mtime2str(time.time()))
            debug ("\n========== Differents  ========== ")
            for f in (different):
                monaff.AffCar()
                debug("D  "+f)
                if (Dscrutation.dict[f].tag == xfl.TAG_FILE):
                    # Mise à jour des données
                    for attr in (xfl.ATTR_MTIME, xfl.ATTR_SIZE):
                        DRef.dict[f].set(attr, str(Dscrutation.dict[f].get(attr)))
                    for attr in (ATTR_LASTSEND, ATTR_CRC, ATTR_NBSEND):
                        DRef.dict[f].set(attr, str(0))
                    DRef.dict[f].set(ATTR_LASTVIEW, Dscrutation.et.get(xfl.ATTR_TIME))
            Console.Print_temp("%s - Traitement des fichiers identiques" %mtime2str(time.time()))
            debug ("\n========== Identiques  ========== ")
            for f in (same):
                monaff.AffCar()
                debug("I  "+f)
                if (Dscrutation.dict[f].tag == xfl.TAG_FILE):
                    if DRef.dict[f].get(ATTR_LASTVIEW) == None:
                        for attr in (ATTR_LASTSEND, ATTR_CRC, ATTR_NBSEND):
                            DRef.dict[f].set(attr, str(0))
                    DRef.dict[f].set(ATTR_LASTVIEW, Dscrutation.et.get(xfl.ATTR_TIME))
            Console.Print_temp("%s - Sauvegarde du fichier de reprise" %mtime2str(time.time()))
            DRef.et.set(xfl.ATTR_TIME, str(time.time()))
            if XFLFile == "BFTPsynchro.xml":
                if os.path.isfile(XFLFile):
                    try:
                        os.rename(XFLFile,XFLFileBak)
                    except:
                        os.remove(XFLFileBak)
                        os.rename(XFLFile,XFLFileBak)
            DRef.write_file(XFLFile)
            debug ("%s - Selection des fichiers les moins emis " %mtime2str(time.time()))
            FileToSend=[]
            Console.Print_temp("%s - Selection des fichiers a emettre" %mtime2str(time.time()))
            for f in (only1 + different + same):
                monaff.AffCar()
                (shortname, extension) =  os.path.splitext(os.path.basename(f))
                if not(extension in IgnoreExtensions) and (Dscrutation.dict[f].tag == xfl.TAG_FILE):
                    # Ignorer les fichiers trop récents (risque de prendre une image iso en cours de téléchargement)
                    # et les fichiers trop émis
                    #if abs(float(DRef.dict[f].get(xfl.ATTR_MTIME))-float(DRef.dict[f].get(ATTR_LASTVIEW)))>60 \
                    # and int(DRef.dict[f].get(ATTR_NBSEND))<MinFileRedundancy:
                    if int(DRef.dict[f].get(ATTR_NBSEND))<MinFileRedundancy:
                        monfichier={'iteration':int(DRef.dict[f].get(ATTR_NBSEND)), 'file':f}
                        FileToSend.append(monfichier)
                    debug(" +-- "+f)
            Console.Print_temp("%s - Priorisation des fichiers a emettre" %mtime2str(time.time()))
            FileToSend = sortDictBy(FileToSend, "iteration")
            debug ("Nombre de fichiers a synchroniser : %d" %len(FileToSend))
            if len(FileToSend)==0:
                AllFileSendMax=True
            boucleemission = LimiteurDebit(options.debit)
            boucleemission.depart_chrono()
            print ("%s - Emission des donnees " %mtime2str(time.time()))
            # Set TransmitDelay from min 300 to max time needed to identify data to send
            TransmitDelay=time.time()-float(Dscrutation.et.get(xfl.ATTR_TIME))
            if TransmitDelay < 300: TransmitDelay=300
            # Boucle 2 d'émission temporelle
            FileLessRedundancy=0
            LastFileSendMax=False
            while (boucleemission.temps_total() < TransmitDelay*4) and (not(LastFileSendMax)):
                if len(FileToSend)!=0:
                    item=FileToSend.pop(0)
                    f=item['file']
                    i=item['iteration']
                    debug("Iteration:* %d *" %i)
                    if sys.platform == 'win32':
                        separator='\\'
                    else:
                        separator='/'
                    fullpathfichier = repertoire + separator + f
                    # Correction Bug Erreur si le fichier a été supprimé.
                    if fullpathfichier.isfile():
                        # Controle de stabilité du fichier : vérification des paramètres date et taille par rapport à la référence
                        #   éjecter le fichier s'il a changé
                        # bug 4901	Non transmission de fichiers timestamp en mode boucle sur gros volume
                        # modif : pas de vérif de stabilité pour les petits fichiers ou le fichier de synchro
                        stable=(fullpathfichier.getmtime()==float(DRef.dict[f].get(xfl.ATTR_MTIME)) and \
                            fullpathfichier.getsize()==int(DRef.dict[f].get(xfl.ATTR_SIZE)))
                        if not stable:
                            DRef.dict[f].set(ATTR_CRC,'0')
                            DRef.dict[f].set(ATTR_NBSEND,'0')
                        if (stable or fullpathfichier.getsize()<1024 or f=="BFTPsynchro.xml"):
                            if DRef.dict[f].get(ATTR_CRC)=='0':
                                current_CRC=str(CalcCRC(fullpathfichier))
                                DRef.dict[f].set(ATTR_CRC, current_CRC)
                            if (envoyer(fullpathfichier, f, limiteur_debit, crc=int(DRef.dict[f].get(ATTR_CRC))) != -1):
                                DRef.dict[f].set(ATTR_LASTSEND, str(time.time()))
                                DRef.dict[f].set(ATTR_NBSEND, str(int(DRef.dict[f].get(ATTR_NBSEND)) + 1))
                                if int(DRef.dict[f].get(ATTR_NBSEND)) > MinFileRedundancy:
                                    LastFileSendMax=True
                                    if (FileLessRedundancy == 0): AllFileSendMax=True
                                else:
                                    FileLessRedundancy+=1
                        else:
                            debug("Fichier non stable - out")
                            # doit on réinitialiser les données de référence ?
                            # fichier non émis donc à réémettre ultérieurement
                            FileLessRedundancy+=1
                        # fin du controle
                # Liste vide : rien à transmettre
                else:
                    # permet de sortir de la boucle 2
                    LastFileSendMax=True
                    # On temporise si on est en mode boucle
                    if options.boucle:
                        attente=options.pause-boucleemission.temps_total()
                        if attente > 0:
                            print("%s - Attente avant nouvelle scrutation" %mtime2str(time.time()))
                            time.sleep(attente)
            Console.Print_temp("%s - Sauvegarde du fichier de reprise" %mtime2str(time.time()))
            DRef.et.set(xfl.ATTR_TIME, str(time.time()))
            if XFLFile == "BFTPsynchro.xml" :
                if os.path.isfile(XFLFile):
                    try:
                        os.rename(XFLFile,XFLFileBak)
                    except:
                        os.remove(XFLFileBak)
                        os.rename(XFLFile,XFLFileBak)
            DRef.write_file(XFLFile)
        debug("Tous les fichiers ont ete emis")




#------------------------------------------------------------------------------
# AUGMENTER_PRIORITE
#---------------------

def augmenter_priorite():
    """pour augmenter la priorité du processus, afin de garantir une bonne
    réception des paquets UDP."""

    if sys.platform == 'win32':
        # sous Windows:
        process = win32process.GetCurrentProcess()
        win32process.SetPriorityClass (process, win32process.REALTIME_PRIORITY_CLASS)
        #win32process.SetPriorityClass (process, win32process.HIGH_PRIORITY_CLASS)
    else:
        # sous Unix:
        try:
            os.nice(-20)
        except:
            print "Impossible d'augmenter la priorite du processus:"
            print "Il est conseille de le lancer en tant que root pour obtenir les meilleures performances."

#------------------------------------------------------------------------------
# Analyse Config File
#---------------------
def analyse_conf():
    """pour analyser/initialiser le parametrage
    (à l'aide du module ConfigParser)"""
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp("bftp.ini")
    param=config.items("blindftp")
    for val in param:
        if config.has_option("blindftp", param):
            param = config.get("blindftp", param)

#------------------------------------------------------------------------------
# Save Config trace File
#---------------------
def Save_ConfTrace():
    """pour sauvegarder le parametrage courant"""


#------------------------------------------------------------------------------
# analyse_options
#---------------------

def analyse_options():
    """pour analyser les options de ligne de commande.
    (à l'aide du module optparse)"""

    # on crée un objet optparse.OptionParser, en lui donnant comme chaîne
    # "usage" la docstring en début de ce fichier:
    parseur = OptionParser_doc(usage="%prog [options] <fichier ou repertoire>")
    parseur.doc = __doc__

    # on ajoute les options possibles:
    parseur.add_option("-e", "--envoi", action="store_true", dest="envoi_fichier",\
        default=False, help="Envoyer le fichier")
    parseur.add_option("-s", "--synchro", action="store_true", dest="synchro_arbo",\
        default=False, help="Synchroniser l'arborescence")
    parseur.add_option("-S", "--Synchro", action="store_true", dest="synchro_arbo_stricte",\
        default=False, help="Synchroniser l'arborescence avec suppression")
    parseur.add_option("-r", "--reception", action="store_true", dest="recevoir",\
        default=False, help="Recevoir des fichiers dans le repertoire indique")
    parseur.add_option("-a", dest="adresse", default="localhost", \
        help="Adresse destination: Adresse IP ou nom de machine")
    parseur.add_option("-p", dest="port_UDP",\
        help="Port UDP", type="int", default=36016)
    parseur.add_option("-l", dest="debit",\
        help="Limite du debit (Kbps)", type="int", default=8000)
    parseur.add_option("-d", "--debug", action="store_true", dest="debug",\
        default=False, help="Mode Debug")
    parseur.add_option("-b", "--boucle", action="store_true", dest="boucle",\
        default=False, help="Envoi des fichiers en boucle")
    parseur.add_option("-P", dest="pause",\
        help="Pause entre 2 boucles (en secondes)", type="int", default=300)
    parseur.add_option("-c", "--continue", action="store_true", dest="reprise",\
        default=False, help="Fichier de reprise a chaud")


    # on parse les options de ligne de commande:
    (options, args) = parseur.parse_args(sys.argv[1:])
    # vérif qu'il y a 1 et 1 seule action:
    nb_actions = 0
    if options.envoi_fichier: nb_actions+=1
    if options.synchro_arbo: nb_actions+=1
    if options.synchro_arbo_stricte: nb_actions+=1
    if options.recevoir: nb_actions+=1
    if nb_actions != 1:
        parseur.error("Vous devez indiquer une et une seule action. (%s -h pour l'aide complete)" % NOM_SCRIPT)
    if len(args) != 1:
        parseur.error("Vous devez indiquer un et un seul fichier/repertoire. (%s -h pour l'aide complete)" % NOM_SCRIPT)
    return (options, args)



#==============================================================================
# PROGRAMME PRINCIPAL
#=====================
if __name__ == '__main__':
    # pour que la date des fichiers soit gérée en nombre entier de secondes
    # (cela dépend des OS: cf. aide Python)
    # => utile uniquement pour générer un numéro de session
    os.stat_float_times(False)

    (options, args) = analyse_options()
    cible = path(args[0])
    HOST = options.adresse
    PORT = options.port_UDP
    MODE_DEBUG = options.debug

    # Utilisation de Psyco pour améliorer les performances:
    # Perturbe l'affichage sous Windows: A CORRIGER.
    #try:
    #   import psyco
    #   psyco.full()
    #   debug("Psyco charge.")
    #except ImportError:
    #   print "ATTENTION: le module Psyco n'est pas installe, les performances ne seront pas optimales !"
    #   pass

    # pour mesurer les stats de reception:
    stats = Stats()

    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(levelname)-8s %(message)s',
                datefmt='%d/%m/%Y %H:%M:%S',
                filename='bftp.log',
                filemode='a')
    logging.info("Demarrage de BlindFTP")

    # Emission de messages heartbeat
    HB_emis=HeartBeat()
    HB_recus=HeartBeat()
    if not(options.recevoir):
        HB_emis.Th_envoyer_BoucleheartbeatT()

    if options.envoi_fichier:
        envoyer(cible, cible.name)
    elif (options.synchro_arbo or options.synchro_arbo_stricte):
        # Délais pour considérer un fichier "hors ligne" comme définitivement effacé
        OffLineDelay=OFFLINEDELAY
        # Fichier référence de l'arborescence synchronisée
        # TODO : Nom du fichier transmis en paramètre
        print "Lecture/contruction du fichier de reprise"
        XFLFile_id=False
        working=TraitEncours.TraitEnCours()
        working.StartIte()
        if options.reprise:
            XFLFile="BFTPsynchro.xml"
            XFLFileBak="BFTPsynchro.bak"
        else:
            XFLFile_id,XFLFile=tempfile.mkstemp(prefix='BFTP_',suffix='.xml')
        DRef = xfl.DirTree()
        if (XFLFile_id):
            debug("Fichier de reprise de la session : %s" %XFLFile)
            DRef.read_disk(cible, working.AffCar)
        else:
            debug("Lecture du fichier de reprise : %s" %XFLFile)
            try:
                DRef.read_file(XFLFile)
            except:
                DRef.read_disk(cible, working.AffCar)
        if options.boucle:
            while True:
                try:
                    synchro_arbo(cible)
                except:
                    print "Erreur lors de l'envoi d'arborescence."
                    traceback.print_exc()
                print "Attente de %d secondes avant prochain envoi... (Ctrl+Pause ou Ctrl+C pour quitter)\n" % options.pause
                time.sleep(options.pause)
        else:
            synchro_arbo(cible)
        if (XFLFile_id):
            debug("Suppression du fichier de reprise temporaire : %s" %XFLFile)
            os.close(XFLFile_id)
            #os.close(XFLFileBak_id)
            os.remove(XFLFile)
            #os.remove(XFLFileBak)
    elif options.recevoir:
        CHEMIN_DEST = path(args[0])
        # on commence par augmenter la priorité du processus de réception:
        augmenter_priorite()
        # thread de timeout des heartbeat
        HB_recus.Th_checktimeout_heartbeatT()
        # puis on se met en réception:
        recevoir(CHEMIN_DEST)
    logging.info("Arret de BlindFTP")