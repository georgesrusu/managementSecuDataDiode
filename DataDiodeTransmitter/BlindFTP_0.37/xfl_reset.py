#!/usr/local/bin/python
# -*- coding: latin-1 -*-
"""
----------------------------------------------------------------------------
XFL Reset
----------------------------------------------------------------------------
version 0.02 du 04/04/2008

Auteur:
- Laurent VILLEMIN (LV) - Laurent.villemin(a)laposte.net


Module d'initialisation des caract�ristiques d'�mission au sein du fichier
de reprise XML de BlindFTP.

En production blindftp peut reposer sur une architecture qui utilise un serveur
de publication (les donn�es sont recues sur un poste dit "guichet" et sont
publi�es sur un poste tiers (dit de publication) disposant d'un espace disque
plus cons�quent. Cet espace disque est mont� sur le guichet via les services
r�seaux standards (nfs, montage smb, ...).

L'augmentation du nombre de postes augmente la probabilit� d'indisponibilit�
d'un �l�ment sur la chaine de r�ception/publication empechant la publication des
donn�es �mises et n�cessitant de forcer une nouvelle �mission des donn�es.

La modification du fichier XML de reprise permet de "forcer" de nouvelles
�missions des donn�es depuis le guichet bas.
Le mode op�ratoire n�cessite d'utiliser blindftp en mode synchro (options -s) et
avec fichier de reprise (option -c).
1 - Stopper l'�mission
2 - Utiliser le present code pour modifier le fichier XML de reprise
3 - relancer l'�mission des donn�es

Automatisation prise en charge :
 * Initialisation par date
 * Initialisation par nom de fichier
 * Initialisation par comparaison XML / Dossier de r�ception
 * Initialisation via regexp

Site Web du projet : http://adullact.net/projects/blindftp/

License: CeCILL v2, open-source (GPL compatible)
         see http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
"""
#------------------------------------------------------------------------------
# HISTORIQUE:
# 24/03/08 v0.01 LV : - 1�re version
# 28/03/08 v0.02 LV : Recherche par expression r�guli�re impl�ment�e
# 04/04/08 v0.03 LV : Int�gration du module TraitEncours

try:
    import bftp
except :
    raise ImportError, "Le module blindftp n'est pas accessible: Voir https://adullact.net/projects/blindftp/"
try:
    import TraitEncours
except :
    raise ImportError, "Le module TraitEncours n'est pas accessible: Voir https://adullact.net/projects/blindftp/"
try:
    import xfl
except:
    raise ImportError, "the XFL module is not installed: see http://www.decalage.info/python/xfl"
import datetime, time, re

XFLFile="BFTPsynchro.xml"

def Saisie(Libelle, DefValue):
    """
    Saisie d'une valeur avec proposition par d�faut
    """
    question = Libelle + '? [' + str(DefValue) + '] '
    val=raw_input(question)
    if val == '':
        return(DefValue)
    else:
        return(val)

def InputResetDate():
    """
    Saisie de la date et heure d'incident - pr�initialisation � Now - 1 jour
    """
    print "Initialisation sur date incident. \n  Saisie de la date et heure de rupture du lien diode :"
    Incident=datetime.datetime.now()-datetime.timedelta(days=1)

    aaaa= Saisie('    Annee  ', Incident.year)
    mmm = Saisie('    Mois   ', Incident.month)
    dd  = Saisie('    Jour   ', Incident.day)
    hh  = Saisie('    Heure  ', Incident.hour)
    mm  = Saisie('    Minute ', Incident.minute)

    pattern = '%Y-%m-%d %H:%M:%S'
    MyDate="%d-%02d-%02d %02d:%02d:00" %(int(aaaa), int(mmm) , int(dd), int(hh), int(mm))
    epoch = int(time.mktime(time.strptime(MyDate, pattern)))
    bftp.debug("date_initialisation       = %s" % bftp.mtime2str(epoch))
    return(epoch)

def resetbyDate(ResetDate):
    """
    Initialisation des �missions au sein du fichier XML post�rieur � une date
    Cot� bas penser � automatiser la g�n�ration d'un fichier timestamp au sein de
    l'arborescence synchronis�e afin d'identifier facilement l'heure de non transmission
    """
    DRef = xfl.DirTree()
    DRef.read_file(XFLFile)
    DRef.pathdict()
    NbFile=0
    NbReinitFile=0
    for myfile in DRef.dict:
        if(DRef.dict[myfile].tag == xfl.TAG_FILE):
            NbFile+=1
            if float(DRef.dict[myfile].get(bftp.ATTR_LASTSEND)) > ResetDate:
                NbReinitFile+=1
                print ("        %s \n" % myfile)
                for attr in (bftp.ATTR_LASTSEND, bftp.ATTR_NBSEND):
                    DRef.dict[myfile].set(attr, str(0))
    bftp.debug('Initialisation de %d fichier(s) sur %d.' % (NbReinitFile,  NbFile))
    if NbReinitFile > 0:
        DRef.write_file(XFLFile)

def resetbyRegexp(expr):
    """
    Initialisation des �missions au sein du fichier XML selon un motif regexp
    Consulter le howto regexp python pour maitriser la syntaxe
    Quelques exemples
        .* : tous les fichiers
        .*\.txt$ : tous les fichiers d'extension ".txt"
        monrep\\.* : tous les fichiers contenus dans monrep
    """
    DRef = xfl.DirTree()
    DRef.read_file(XFLFile)
    DRef.pathdict()
    NbFile=0
    NbReinitFile=0
    motif=re.compile(expr)
    for myfile in DRef.dict:
        if(DRef.dict[myfile].tag == xfl.TAG_FILE):
            NbFile+=1
            res=motif.match(str(myfile))
            if res!=None:
                NbFile+=1
                NbReinitFile+=1
                print ("        %s" % myfile)
                for attr in (bftp.ATTR_LASTSEND, bftp.ATTR_NBSEND):
                    DRef.dict[myfile].set(attr, str(0))
    bftp.debug('Initialisation de %d fichier(s) sur %d.' % (NbReinitFile,  NbFile))
    if NbReinitFile > 0:
        DRef.write_file(XFLFile)

def resetbyDiff(path):
    """
    Initialisation des �missions au sein du fichier XML en comparant l'arborescence de r�ception
    Mode op�ratoire :
        Le fichier XML de reprise est transmis cot� haut.
        Ce fichier est compar� � l'arborescence de r�ception
        Tous les fichiers d�clar�s �mis et non recus sont r�initialis�s
        Importer le fichier XML modifi� sur le guichet bas et relancer blindftp
    """
    DRef  = xfl.DirTree()
    DHaut = xfl.DirTree()
    MonAff=TraitEncours.TraitEnCours()
    MonAff.StartIte()
    DRef.read_file(XFLFile)
    DHaut.read_disk(path, None, MonAff.AffCar)
    same, different, only1, only2 = xfl.compare_DT(DRef, DHaut)
    NbReinitFile=0
    for myfile in sorted(different + only1):
        if(DRef.dict[myfile].tag == xfl.TAG_FILE):
            NbReinitFile+=1
            print ("        %s" % myfile)
            for attr in (bftp.ATTR_LASTSEND, bftp.ATTR_NBSEND):
                DRef.dict[myfile].set(attr, str(0))
    bftp.debug('Initialisation de %d fichier(s)' % NbReinitFile)
    if NbReinitFile > 0:
        DRef.write_file(XFLFile)


def resetbyPath(path):
    """
    Initialisation des �missions au sein du fichier XML selon un chemin
    """
    DRef = xfl.DirTree()
    DRef.read_file(XFLFile)
    DRef.pathdict()
    if DRef.dict.has_key(path):
        for attr in (bftp.ATTR_LASTSEND, bftp.ATTR_NBSEND):
            DRef.dict[path].set(attr, str(0))
        DRef.write_file(XFLFile)
    else:
        print 'Erreur : Chemin inexistant'


#--- MAIN ---------------------------------------------------------------------

if __name__ == "__main__":
    methode=Saisie('Methode d initialisation utilisee ? \n1 : par date \n2 : par chemin du fichier \n3 : par analyse arborescence \n4 : par expression reguliere ', '1')
    if methode == '1':
        MyResetDate=InputResetDate()
        resetbyDate(MyResetDate)
    if methode == '2':
        path=Saisie('Chemin fichier ', 'c:\\NotReceivedFile.txt')
        resetbyPath(path)
    if methode == '3':
        path=Saisie('Chemin arborescence de reception ', "c:\\reception")
        resetbyDiff(path)
    if methode == '4':
        print ("HowTo des expressions regulieres disponible � l'URL http://www.python.org/doc/howto/")
        regexp=Saisie('Expression reguliere ', ".*\.txt$")
        resetbyRegexp(regexp)



