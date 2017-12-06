#!/usr/local/bin/python
# -*- coding: latin-1 -*-
"""
--------------------------------------------------------------------------------
BlindFTP_simple v0.11 - Unidirectional File Transfer Protocol - Philippe Lagadec
--------------------------------------------------------------------------------

Pour transferer un fichier ou une arborescence complete a travers une liaison
reseau unidirectionnelle de type "diode", par UDP.

usage: voir bftp.py -h


Copyright Philippe Lagadec 2005-2007
Auteur:
- Philippe Lagadec (PL) - philippe.lagadec(a)laposte.net

Ce logiciel est r�gi par la licence CeCILL soumise au droit fran�ais et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL telle que diffus�e par le CEA, le CNRS et l'INRIA
sur le site "http://www.cecill.info".

En contrepartie de l'accessibilit� au code source et des droits de copie,
de modification et de redistribution accord�s par cette licence, il n'est
offert aux utilisateurs qu'une garantie limit�e.  Pour les m�mes raisons,
seule une responsabilit� restreinte p�se sur l'auteur du programme,  le
titulaire des droits patrimoniaux et les conc�dants successifs.

A cet �gard  l'attention de l'utilisateur est attir�e sur les risques
associ�s au chargement,  � l'utilisation,  � la modification et/ou au
d�veloppement et � la reproduction du logiciel par l'utilisateur �tant
donn� sa sp�cificit� de logiciel libre, qui peut le rendre complexe �
manipuler et qui le r�serve donc � des d�veloppeurs et des professionnels
avertis poss�dant  des  connaissances  informatiques approfondies.  Les
utilisateurs sont donc invit�s � charger  et  tester  l'ad�quation  du
logiciel � leurs besoins dans des conditions permettant d'assurer la
s�curit� de leurs syst�mes et ou de leurs donn�es et, plus g�n�ralement,
� l'utiliser et l'exploiter dans les m�mes conditions de s�curit�.

Le fait que vous puissiez acc�der � cet en-t�te signifie que vous avez
pris connaissance de la licence CeCILL, et que vous en avez accept� les
termes.
"""

#------------------------------------------------------------------------------
# HISTORIQUE:
# 20/02/2005 v0.01 PL: - 1�re version (UFTP)
# 23/02/2005 v0.02 PL: - r�ception de fichier fonctionnelle
# 24/02/2005 v0.03 PL: - synchronisation simple d'arborescence
#                      - gestion des options avec optparse
# 06/04/2005 v0.04 PL: - correction temporaire de synchro_arbo, � reprendre
# 21/04/2005 v0.05 PL: - correction d'un bug dans Fichier.annuler_fichier()
#                        (close sur fichier temp non ouvert)
#                      - ajout de chemin_interdit() pour filtrer les chemins
#                        interdits: chemins absolus, contenant "..", ...
#                      - ajout options -b (boucle) et -P (pause)
#                      - classe LimiteurDebit pour contr�ler le d�bit d'envoi
#                      - correction des chemins relatifs dans synchro_arbo
#                      - ajout print_oem, str_oem et str_lat1 pour corriger les
#                        probl�mes d�s aux noms de fichiers avec accents
# 06/07/2005 v0.06 PL: - r�ception simultan�e de plusieurs fichiers, avec
#                        gestion de la redondance (multiples fichiers temporaires,
#                        et gestion de paquets arrivant dans le d�sordre)
#                        --> modification compl�te du protocole et format des paquets
#                      - correction bug augmenter_priorite sous Unix
#                      - UFTP renomm� en BlindFTP
# 11/07/2005 v0.07 PL: - correction d'un bug li� aux accents dans envoyer()
#                      - gestion (tr�s spartiate) des exceptions 
#                      - d�but de journalisation dans un fichier bftp.log
# 18/07/2005 v0.08 PL: - affichage du nom de fichier en cours de r�ception m�me si ignor�
# 18/07/2005 v0.09 PL: - affichage de l'heure pour chaque r�ception de fichier
#                      - correction d'un bug li� aux accents dans les logs
#                      - affichage complet des exceptions Python
# 21/07/2005 v0.10 PL: - format de paquet v3: ajout n�session et compteur de paquet
#                      - classe Stats pour mesurer taux de perte, d�bit effectif, ...
# 03/08/2005 v0.11 PL: - import Console pour am�liorer l'affichage (� poursuivre)
#                      - ajout CRC32 d'un fichier pour d�tecter d'�ventuels fichiers
#                        corrompus
#                      - correction tests sys.platform() == 'win32'
# 04/03/2007 v0.12 PL: - verif import pywin32 et path
#                      - correction mot-cl� "global"
#                      - conversion tabs en espaces et corrections mineures

#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

import sys, socket, struct, time, os, os.path, tempfile, logging, traceback
import binascii

# modules sp�cifiques � Windows:
if sys.platform == 'win32': 
    try:
        import win32api, win32process
    except:
        raise ImportError, "the pywin32 module is not installed: see http://sourceforge.net/projects/pywin32"

# import du module path.py
try:
    from path import path
except:
    raise ImportError, "the path module is not installed: see http://www.jorendorff.com/articles/python/path/"

# modules perso
from OptionParser_doc import *
import TabBits, Console

#=== CONSTANTES ===============================================================

TAILLE_PAQUET = 1400    # taille max d'un paquet r�seau

MODE_DEBUG = True   # contr�le si les messages de debug() s'affichent

RACINE_TEMP = "temp"    # racine pour cr�er les r�pertoires temporaires

MAX_NOM_FICHIER = 1024  # taille max pour le nom d'un fichier (en octets)

# Ent�te d'un paquet BFTP (format v3):
# (cf. aide du module struct pour les codes)
# - type de paquet: uchar=B
# - longueur du nom de fichier (+chemin): uchar=B
# - longueur des donn�es du fichier dans le paquet: uint16=H
# - offset, position des donn�es dans le fichier: uint32=I
# - num�ro de session: uint32=I
# - n� de paquet dans la session: uint32=I
# - n� de paquet du fichier: uint32=I
# - nombre de paquets pour le fichier: uint32=I
# - longueur du fichier (en octets): uint32=I
# - date du fichier (en secondes depuis epoch): uint32=I
# - CRC32 du fichier: int32=i (sign�)
# (suivi du nom du fichier, puis des donn�es)
FORMAT_ENTETE = "BBHIIIIIIIi"
TAILLE_ENTETE = 36

# Types de paquets:
PAQUET_FICHIER      = 0
PAQUET_REPERTOIRE   = 1
PAQUET_KEEPALIVE    = 10

#=== VARIABLES GLOBALES =======================================================

# pour stocker les options (cf. analyse_options)
global options
options = None

# dictionnaire des fichiers en cours de r�ception
global fichiers
fichiers = {}

# pour mesurer les stats de reception:
stats = None

#------------------------------------------------------------------------------
# str_lat1
#-------------------
def str_lat1 (chaine, errors='strict'):
    """
    pour convertir une cha�ne unicode en cha�ne de type str au format "Latin-1"
    --> Bidouille inf�me n�cessaire pour �viter une UnicodeDecodeError quand
        une cha�ne contient des accents et qu'on utilise fichier.write(chaine)
    """
    return str(chaine.encode('latin_1', errors))

#------------------------------------------------------------------------------
# str_oem
#-------------------
def str_oem (chaine, errors='strict'):
    """
    pour convertir une cha�ne unicode en cha�ne de type str au format "CP850" (MS-DOS OEM)
    --> Bidouille inf�me n�cessaire pour �viter une UnicodeDecodeError quand
        une cha�ne contient des accents et qu'on utilise fichier.write(chaine)
    """
    return str(chaine.encode('cp850', errors))

#------------------------------------------------------------------------------
# print_oem
#-------------------
def print_oem (chaine, errors='strict'):
    """
    Pour afficher correctement une cha�ne contenant des accents sur un
    terminal cmd de Windows. (conversion en page de code "cp850")
    Affichage simple sans conversion si on n'est pas sous Windows.
    """
    if sys.platform == 'win32': 
        print str(chaine.encode('cp850', errors))
    else:
        print chaine

#------------------------------------------------------------------------------
# str_ajuste
#-------------------
def str_ajuste (chaine, longueur=79):
    """ajuste la chaine pour qu'elle fasse exactement la longueur indiqu�e,
    en coupant ou en remplissant avec des espaces."""
    l = len(chaine)
    if l>longueur:
        return chaine[0:longueur]
    else:
        return chaine + " "*(longueur-l)

#------------------------------------------------------------------------------
# DEBUG
#-------------------

def debug(texte):
    "pour afficher un texte si MODE_DEBUG = True"

    if MODE_DEBUG:
        print_oem ("DEBUG:" + texte)


#------------------------------------------------------------------------------
# EXIT_AIDE
#-------------------

def exit_aide():
    "Affiche un texte d'aide en cas d'erreur."

    # on affiche la docstring (en d�but de ce fichier) qui contient l'aide.
    print __doc__
    sys.exit(1)


#------------------------------------------------------------------------------
# MTIME2STR
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
        """pour mettre � jour les stats en fonction du paquet."""
        # on v�rifie si on est toujours dans la m�me session, sinon RAZ
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
        # num_paquet_attendu correspond au nombre de paquets envoy�s de la session
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
    """V�rifie si le chemin de fichier demand� est interdit, par exemple
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
    # A AJOUTER: v�rifier si codage unicode, ou autre ??
    # Sinon c'est OK, le chemin est valide:
    return False

#------------------------------------------------------------------------------
# classe FICHIER
#-------------------

class Fichier:
    """classe repr�sentant un fichier en cours de r�ception."""
    
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
        # on cr�e le fichier temporaire (objet file):
        self.fichier_temp = tempfile.NamedTemporaryFile(prefix='BFTP_')
        debug('fichier_temp = "%s"' % self.fichier_temp.name)
        self.paquets_recus = TabBits.TabBits(self.nb_paquets)
        #print 'Reception du fichier "%s"...' % self.nom_fichier
        self.est_termine = False    # flag indiquant une r�ception compl�te
        self.crc32 = paquet.crc32 # CRC32 du fichier
        # on ne doit pas traiter le paquet automatiquement, sinon il peut
        # y avoir des probl�mes d'ordre des actions
        #self.traiter_paquet(paquet)
        
        
    def annuler_reception(self):
        "pour annuler la r�ception d'un fichier en cours."
        # on ferme et on supprime le fichier temporaire
        # seulement s'il est effectivement ouvert
        # (sinon � l'initialisation c'est un entier)
        if isinstance(self.fichier_temp, file):
            if not self.fichier_temp.closed:
                self.fichier_temp.close()
        # d'apr�s la doc de tempfile, le fichier est automatiquement supprim�
        #os.remove(self.nom_temp)
        debug('Reception de fichier annulee.')
        
    def recopier_destination(self):
        "pour recopier le fichier � destination une fois qu'il est termin�."
        print 'OK, fichier termine.'
        # cr�er le chemin destination si besoin avec makedirs
        chemin_dest = self.fichier_dest.dirname()
        if not os.path.exists(chemin_dest):
            chemin_dest.makedirs()
        elif not os.path.isdir(chemin_dest):
            chemin_dest.remove()
            chemin_dest.mkdir()
        # recopier le fichier temporaire au bon endroit
        debug('Recopie de %s vers %s...' % (self.fichier_temp.name, self.fichier_dest))
        # move(self.nom_temp, self.fichier_dest)
        # on revient au d�but
        self.fichier_temp.seek(0)
        f_dest = file(self.fichier_dest, 'wb')
        buffer = self.fichier_temp.read(16384)
        # on d�marre le calcul de CRC32:
        crc32 = binascii.crc32(buffer)
        while len(buffer) != 0:
            f_dest.write(buffer)
            buffer = self.fichier_temp.read(16384)
            # poursuite du calcul de CRC32:
            crc32 = binascii.crc32(buffer, crc32)
        f_dest.close()
        # v�rifier si la taille obtenue est correcte
        if self.fichier_dest.getsize() != self.taille_fichier:
            debug ("taille_fichier = %d, taille obtenue = %d" % 
                   (self.taille_fichier, self.fichier_dest.getsize()) )
            logging.error('Taille du fichier incorrecte: "%s"'% self.nom_fichier)
            raise IOError, 'taille du fichier incorrecte.'
        # v�rifier si le checksum CRC32 est correct
        if self.crc32 != crc32:
            debug ("CRC32 fichier = %X, CRC32 attendu = %X" % 
                   (crc32, self.crc32))
            logging.error('Controle d\'integrite incorrect: "%s"'% self.nom_fichier)
            raise IOError, "controle d'integrite incorrect."
        # mettre � jour la date de modif: tuple (atime,mtime)
        self.fichier_dest.utime( (self.date_fichier, self.date_fichier) )
        # fermer le fichier temporaire
        self.fichier_temp.close()
        # d'apr�s la doc de tempfile, le fichier est automatiquement supprim�
        self.fichier_en_cours = False

    def traiter_paquet(self, paquet):
        "pour traiter un paquet contenant un morceau du fichier."
        # on v�rifie si le paquet n'a pas d�j� �t� re�u
        if not self.paquets_recus.get (paquet.num_paquet):
            # c'est un nouveau paquet: il faut l'�crire dans le fichier temporaire
            # on calcule l'offset dans le fichier, en consid�rant que chaque
            # paquet contient la m�me longueur de donn�es:
            #offset = paquet.num_paquet * paquet.taille_donnees
            #debug("offset = %d" % offset)
            self.fichier_temp.seek(paquet.offset)
            # note: si on d�place le curseur apr�s la fin r�elle du fichier,
            # celui-ci est compl�t� d'octets nuls, ce qui nous arrange bien :-).
            self.fichier_temp.write(paquet.donnees)
            debug("offset apres = %d" % self.fichier_temp.tell())
            self.paquets_recus.set(paquet.num_paquet, True)
            pourcent = 100*(self.paquets_recus.nb_true)/self.nb_paquets
            # affichage du pourcentage: la virgule �vite un retour chariot
            print "%d%%\r" % pourcent,
            # pour forcer la mise � jour de l'affichage
            sys.stdout.flush()
            # si le fichier est termin�, on le recopie � destination:
            if self.paquets_recus.nb_true == self.nb_paquets:
                # on va � la ligne
                #print ""
                self.recopier_destination()
                debug ("Fichier termin�.")
                logging.info('Fichier "%s" recu en entier, recopie a destination.'% self.nom_fichier)
                # dans ce cas on retire le fichier du dictionnaire
                self.est_termine = True
                del fichiers[self.nom_fichier]
                # ...et on suppose qu'il n'y a plus d'autres r�f�rences:
                # le garbage collector devrait le supprimer de la m�moire.
                        
                    

        
        
#------------------------------------------------------------------------------
# classe PAQUET
#-------------------

class Paquet:
    """classe repr�sentant un paquet BFTP, permettant la construction et le
    d�codage du paquet."""
    
    def __init__(self):
        "Constructeur d'objet Paquet BFTP."
        # on initialise les infos contenues dans l'ent�te du paquet
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
        "Pour d�coder un paquet BFTP."
        # on d�code d'abord l'ent�te (cf. d�but de ce fichier):
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
        if self.type_paquet not in [PAQUET_FICHIER]:
            raise ValueError, 'type de paquet incorrect'
        if self.longueur_nom > MAX_NOM_FICHIER:
            raise ValueError, 'nom de fichier trop long'
        if self.offset + self.taille_donnees > self.taille_fichier:
            raise ValueError, 'offset ou taille des donn�es incorrects'
        self.nom_fichier = paquet[TAILLE_ENTETE : TAILLE_ENTETE + self.longueur_nom]
        # conversion en Latin1 pour �viter probl�mes d�s aux accents
        # A VOIR: seulement sous Windows ?? (sous Mac �a pose probl�me...
        if sys.platform == 'win32':
            self.nom_fichier = self.nom_fichier.decode('latin_1')
        debug("nom_fichier    = %s" % self.nom_fichier)
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
        # est-ce que le fichier est en cours de r�ception ?
        if self.nom_fichier in fichiers:
            debug("Fichier en cours de r�ception")
            f = fichiers[self.nom_fichier]
            # on v�rifie si le fichier n'a pas chang�:
            if f.date_fichier != self.date_fichier \
            or f.taille_fichier != self.taille_fichier \
            or f.crc32 != self.crc32:
                # on commence par annuler la r�ception en cours:
                f.annuler_reception()
                del fichiers[self.nom_fichier]
                # puis on recr�e un nouvel objet fichier d'apr�s les infos du paquet:
                self.nouveau_fichier()
            else:
                if self.fichier_en_cours != self.nom_fichier:
                    # on change de fichier
                    msg = 'Suite de "%s"...' % self.nom_fichier
                    heure = time.strftime('%d/%m %H:%M ')
                    print_oem(heure + msg)
                    logging.info(msg)
                    self.fichier_en_cours = self.nom_fichier
                f.traiter_paquet(self)
        else:
            # est-ce que le fichier existe d�j� sur le disque ?
            fichier_dest = CHEMIN_DEST / self.nom_fichier
            debug('fichier_dest = "%s"' % fichier_dest)
            # si la date et la taille du fichier n'ont pas chang�,
            # inutile de recr�er le fichier, on l'ignore:
            if  fichier_dest.exists() \
            and fichier_dest.getsize() == self.taille_fichier \
            and fichier_dest.getmtime() == self.date_fichier:
                #debug("Le fichier n'a pas change, on l'ignore.")
                msg = 'Fichier deja recu: %s' % self.nom_fichier
                msg = str_ajuste(msg)+'\r'
                print msg,
                sys.stdout.flush()
            else:
                # sinon on cr�e un nouvel objet fichier d'apr�s les infos du paquet:
                self.nouveau_fichier()
                
    def nouveau_fichier (self):
        "pour d�buter la r�ception d'un nouveau fichier."
        msg = 'Reception de "%s"...' % self.nom_fichier
        heure = time.strftime('%d/%m %H:%M ')
        print_oem(heure + msg)
        logging.info(msg)
        self.fichier_en_cours = self.nom_fichier
        debug("Nouveau fichier ou fichier mis � jour")
        # on cr�e un nouvel objet fichier d'apr�s les infos du paquet:
        nouveau_fichier = Fichier(self)
        fichiers[self.nom_fichier] = nouveau_fichier
        nouveau_fichier.traiter_paquet(self)

    def construire(self):
        "pour construire un paquet BFTP � partir des param�tres. (non impl�ment�)"
        raise NotImplementedError
    

#------------------------------------------------------------------------------
# LimiteurDebit
#-------------------

class LimiteurDebit:
    "pour controler le d�bit d'envoi de donn�es."
    
    def __init__(self, debit):
        """contructeur de classe LimiteurDebit.
        
        debit : d�bit maximum autoris�, en Kbps."""
        # d�bit en Kbps converti en octets/s
        self.debit_max = debit*1000/8
        debug ("LimiteurDebit: debit_max = %d octets/s" % self.debit_max)
        # on stocke le temps de d�part
        self.temps_debut = time.time()
        # nombre d'octets d�j� transf�r�
        self.octets_envoyes = 0
        
    def depart_chrono(self):
        "pour (re)d�marrer la mesure du d�bit."
        self.temps_debut = time.time()
        self.octets_envoyes = 0
        
    def ajouter_donnees(self, octets):
        "pour ajouter un nombre d'octets envoy�s."
        self.octets_envoyes += octets
        
    def temps_total(self):
        "donne le temps total de mesure."
        return (time.time() - self.temps_debut)
        
    def debit_moyen(self):
        "donne le d�bit moyen mesur�, en octets/s."
        temps_total = self.temps_total()
        if temps_total == 0: return 0   # pour �viter division par z�ro
        debit_moyen = self.octets_envoyes / temps_total
        return debit_moyen
        
    def limiter_debit(self):
        "pour faire une pause afin de respecter le d�bit maximum."
        # on fait des petites pauses (10 ms) tant que le d�bit est trop �lev�:
        while self.debit_moyen() > self.debit_max:
            time.sleep(0.01)
        # m�thode alternative qui ne fonctionne pas tr�s bien
        # (donne souvent des temps de pause n�gatifs !)
#       temps_total = self.temps_total()
#       debit_moyen = self.debit_moyen()
#       # si on d�passe le d�bit max, on calcule la pause:
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
    les fichiers re�us dans le r�pertoire indiqu� en param�tre."""

    # bidouille: on change le contenu de la variable globale
    CHEMIN_DEST = repertoire
    print 'Les fichiers seront recus dans le repertoire "%s".' % str_lat1(CHEMIN_DEST.abspath())
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
# ENVOYER
#-------------------

def envoyer(fichier_source, fichier_dest, limiteur_debit=None, num_session=None,
    num_paquet_session=None):
    """Pour �mettre un fichier en paquets UDP BFTP.
    
    fichier_source : chemin du fichier source sur le disque local
    fichier_dest   : chemin relatif du fichier dans le r�pertoire destination
    limiteur_debit : pour limiter le d�bit d'envoi
    num_session    : num�ro de session
    num_paquet_session : compteur de paquets
    """

    msg = "Envoi du fichier %s..." % fichier_source
    print_oem(msg)
    logging.info(msg)
    if num_session == None:
        num_session = int(time.time())
        num_paquet_session = 0
    debug("num_session         = %d" % num_session)
    debug("num_paquet_session  = %d" % num_paquet_session)
    debug("fichier destination = %s" % fichier_dest)
    longueur_nom = len(fichier_dest)
    debug("longueur_nom = %d" % longueur_nom)
    if longueur_nom > MAX_NOM_FICHIER:
        raise ValueError
    taille_fichier = fichier_source.getsize()
    date_fichier = fichier_source.getmtime()
    debug("taille_fichier = %d" % taille_fichier)
    debug("date_fichier = %s" % mtime2str(date_fichier))
    # calcul de CRC32: on est oblig� de lire une 1�re fois le fichier:
    debug('Calcul de CRC32 pour "%s"...' % fichier_source)
    f = file(fichier_source, 'rb')
    buffer = f.read(16384)
    # on d�marre le calcul de CRC32:
    crc32 = binascii.crc32(buffer)
    while len(buffer) != 0:
        buffer = f.read(16384)
        # poursuite du calcul de CRC32:
        crc32 = binascii.crc32(buffer, crc32)
    f.close()
    debug("CRC32 = %08X" % crc32)
    # taille restant pour les donn�es dans un paquet normal
    taille_donnees_max = TAILLE_PAQUET - TAILLE_ENTETE - longueur_nom
    debug("taille_donnees_max = %d" % taille_donnees_max)
    nb_paquets = (taille_fichier + taille_donnees_max-1) / taille_donnees_max
    if nb_paquets == 0:
        # si le fichier est vide, il faut quand m�me envoyer un paquet
        nb_paquets = 1
    debug("nb_paquets = %d" % nb_paquets)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reste_a_envoyer = taille_fichier
    f = file(fichier_source, 'rb')
    if limiteur_debit == None:
        # si aucun limiteur fourni, on en initialise un:
        limiteur_debit = LimiteurDebit(options.debit)
    for num_paquet in range(0, nb_paquets):
        # on fait une pause si besoin pour limiter le d�bit
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
        if sys.platform == 'win32':
            # sous Windows on doit corriger les accents
            nom_fichier_dest = str_lat1(fichier_dest)
        else:
            # sinon �a a l'air de passer
            nom_fichier_dest = str(fichier_dest)
        paquet = entete + nom_fichier_dest + donnees
        s.sendto(paquet, (HOST, PORT))
        num_paquet_session += 1
        limiteur_debit.ajouter_donnees(len(paquet))
        #debug("debit moyen = %d" % limiteur_debit.debit_moyen())
        #time.sleep(0.3)
        pourcent = 100*(num_paquet+1)/nb_paquets
        # affichage du pourcentage: la virgule �vite un retour chariot
        print "%d%%\r" % pourcent,
        # pour forcer la mise � jour de l'affichage
        sys.stdout.flush()
    print "transfert en %.3f secondes - debit moyen %d Kbps" % (
    limiteur_debit.temps_total(), limiteur_debit.debit_moyen()*8/1000)
    return num_paquet_session



#------------------------------------------------------------------------------
# SYNCHRO_ARBO
#-------------------

def synchro_arbo(repertoire):
    """pour synchroniser une arborescence en envoyant r�guli�rement tous les
    fichiers."""
    
    logging.info('Synchronisation du repertoire "%s"' % str_lat1(repertoire))
    # on utilise un objet LimiteurDebit global pour tout le transfert:
    limiteur_debit = LimiteurDebit(options.debit)
    num_session = int(time.time())
    num_paquet_session = 0
    for fichier in repertoire.walkfiles():
        try:
            num_paquet_session = envoyer(fichier, repertoire.relpathto(fichier), limiteur_debit,
                num_session, num_paquet_session)
        except:
            msg = 'Erreur lors de l\'envoi du fichier "%s": %s' % (str(fichier),
                traceback.format_exc(1))
            print msg
            traceback.print_exc()
            logging.error(msg)

#------------------------------------------------------------------------------
# AUGMENTER_PRIORITE
#---------------------

def augmenter_priorite():
    """pour augmenter la priorit� du processus, afin de garantir une bonne
    r�ception des paquets UDP."""
    
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
# analyse_options
#---------------------

def analyse_options():
    """pour analyser les options de ligne de commande.
    (� l'aide du module optparse)"""
    
    # on cr�e un objet optparse.OptionParser, en lui donnant comme cha�ne
    # "usage" la docstring en d�but de ce fichier:
    parseur = OptionParser_doc(usage="%prog [options] <fichier ou repertoire>")
    parseur.doc = __doc__
    
    # on ajoute les options possibles:
    parseur.add_option("-e", "--envoi", action="store_true", dest="envoi_fichier",\
        default=False, help="Envoyer le fichier")
    parseur.add_option("-s", "--synchro", action="store_true", dest="synchro_arbo",\
        default=False, help="Synchroniser l'arborescence")
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
        help="Pause entre 2 boucles (en secondes)", type="int", default=5)
    # on parse les options de ligne de commande:
    (options, args) = parseur.parse_args(sys.argv[1:])
    # v�rif qu'il y a 1 et 1 seule action:
    nb_actions = 0
    if options.envoi_fichier: nb_actions+=1
    if options.synchro_arbo: nb_actions+=1
    if options.recevoir: nb_actions+=1
    if nb_actions != 1:
        parseur.error("Vous devez indiquer une et une seule action. (BFTP -h pour l'aide complete)")
    if len(args) != 1:
        parseur.error("Vous devez indiquer un et un seul fichier/repertoire. (BFTP -h pour l'aide complete)")
    return (options, args)



#==============================================================================
# PROGRAMME PRINCIPAL
#=====================
if __name__ == '__main__':
    # pour que la date des fichiers soit g�r�e en nombre entier de secondes
    # (cela d�pend des OS: cf. aide Python)
    # => utile uniquement pour g�n�rer un num�ro de session
    os.stat_float_times(False)
        
    (options, args) = analyse_options()
    cible = path(args[0])
    HOST = options.adresse
    PORT = options.port_UDP
    MODE_DEBUG = options.debug
    
    # Utilisation de Psyco pour am�liorer les performances:
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
    logging.info("D�marrage de BlindFTP")       
    
    if options.envoi_fichier:
        envoyer(cible, cible.name)
    elif options.synchro_arbo:
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
    elif options.recevoir:
        CHEMIN_DEST = path(args[0])
        # on commence par augmenter la priorit� du processus de r�ception:
        augmenter_priorite()
        # puis on se met en r�ception:
        recevoir(CHEMIN_DEST)
    logging.info("Arret de BlindFTP")       
        

