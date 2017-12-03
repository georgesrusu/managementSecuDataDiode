#!/bin/bash
echo "--------------------------------------------------------------------------"
echo "                        DEMO RAPIDE BlindFTP"
echo "--------------------------------------------------------------------------"
echo "Attention: ce script va effacer puis recreer 2 repertoires emission et"
echo "reception. Pressez maintenant Ctrl+C pour annuler."
echo " "
read -p "Appuyer sur Entree pour continuer..."
echo "Creation repertoire emission..."

if [[ -d emission ]] 
	then rm -vrf emission
fi
mkdir -v emission
cp -pv *.pdf emission
cp -pv *.html emission
echo "Creation repertoire reception..."
if [[ -d reception ]]
	then rm -rvf reception
fi
mkdir -v reception
echo "Demarrage BlindFTP en mode reception "
python bftp.py -r reception -a localhost & 
PID=`ps auxw | grep bftp.py | grep -v grep | awk '{ print $2 }'`
echo "--------------------------------------------------------------------------"
echo "Demarrage BlindFTP en mode emission, avec pauses de 5 secondes..."
echo "ensuite vous pourrez ajouter/supprimer des fichiers dans ce repertoire"
echo "pendant que BlindFTP fonctionne"
sleep 5 
python bftp.py -b -S emission -a localhost -P 5 
echo "kill du process de reception"
kill -15 $PID
 
