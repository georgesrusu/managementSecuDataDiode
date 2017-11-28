#!/usr/bin/python
# -*- coding: latin-1 -*-
"""
----------------------------------------------------------------------------
TabBits: Classe pour manipuler un tableau de bits de grande taille.
----------------------------------------------------------------------------

version 0.03 du 08/07/2005


Copyright Philippe Lagadec 2005-2007
Auteur:
- Philippe Lagadec (PL) - philippe.lagadec(a)laposte.net

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

# HISTORIQUE:
# 03/07/2005 v0.01: - 1ère version
# 06/07/2005 v0.02: - remplacement du buffer chaine par un objet array
# 08/07/2005 v0.03: - ajout du comptage des bits à 1

# A FAIRE:
# + vérifier si index hors tableau (<0 ou >N-1)
# - import de chaîne ou fichier ou liste de booléens
# - export vers chaîne ou fichier
# - interface tableau Python
# - taille dynamique

import array

#------------------------------------------------------------------------------
# classe TabBits
#--------------------------

class TabBits:
	"""Classe pour manipuler un tableau de bits de grande taille."""
	
	def __init__ (self, taille, buffer=None, readFile=None):
		"""constructeur de TabBits.
		
		taille: nombre de bits du tableau.
		buffer: chaine utilisée pour remplir le tableau (optionnel).
		readFile: fichier utilisé pour remplir le tableau (optionnel).
		"""
		self._taille = taille
		self.nb_true = 0    # nombre de bits à 1, 0 par défaut
		if buffer == None and readFile == None:
			# on calcule le nombre d'octets nécessaires pour le buffer
			taille_buffer = (taille+7)/8
			# on crée alors un buffer de cette taille, initialisé à zéro:
			# self._buffer = chr(0)*taille_buffer
			# on crée un objet array de Bytes
			self._buffer = array.array('B')
			# on ajoute N éléments nuls
			# (à optimiser: boucle pour éviter de créer une liste ?)
			self._buffer.fromlist([0]*taille_buffer)
		else:
			# pas encore écrit...
			raise NotImplementedError

	def get (self, indexBit):
		"""Pour lire un bit dans le tableau. Retourne un booléen."""
		# index de l'octet correspondant dans le buffer et décalage du bit dans l'octet
		indexOctet, decalage =  divmod (indexBit, 8)
		octet = self._buffer[indexOctet]
		masque = 1 << decalage
		bit = octet & masque
		# on retourne un booléen
		return bool(bit)

	def set (self, indexBit, valeur):
		"""Pour écrire un bit dans le tableau."""
		# on s'assure que valeur est un booléen
		valeur = bool(valeur)
		# index de l'octet correspondant dans le buffer et décalage du bit dans l'octet
		indexOctet, decalage =  divmod (indexBit, 8)
		octet = self._buffer[indexOctet]
		masque = 1 << decalage
		ancienne_valeur = bool(octet & masque)
		if valeur == True and ancienne_valeur == False:
			# on doit positionner le bit à 1
			octet = octet | masque
			self._buffer[indexOctet] = octet
			self.nb_true += 1
		elif valeur == False and ancienne_valeur == True:
			# on doit positionner le bit à 0
			masque = 0xFF ^ masque
			octet = octet & masque
			self._buffer[indexOctet] = octet
			self.nb_true -= 1

	def __str__ (self):
		"""pour convertir le TabBits en chaîne contenant des 0 et des 1."""
		chaine = ""
		for i in range(0, self._taille):
			bit = self.get(i)
			if bit:
				chaine += "1"
			else:
				chaine += "0"
		return chaine
		
if __name__ == "__main__":
	# quelques tests si le module est lancé directement
	N=100
	tb = TabBits(N)
	print str(tb)
	tb.set(2, True)
	tb.set(7, True)
	tb.set(N-1, True)
	print str(tb)
	print "tb[0] = %d" % tb.get(0)
	print "tb[2] = %d" % tb.get(2)
	print "tb[%d] = %d" % (N-1, tb.get(N-1))
	print "taille bits = %d" % tb._taille
	print "taille buffer = %d" % len(tb._buffer)
			
		
