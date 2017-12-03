@echo off
echo --------------------------------------------------------------------------
echo                         DEMO RAPIDE BlindFTP
echo --------------------------------------------------------------------------
echo.
REM 2008-11-03 v0.01 PL: - first version

echo Attention: ce script va effacer puis recreer 2 repertoires emission et
echo reception. Pressez maintenant Ctrl+C pour annuler.
pause
echo Creation repertoire emission...
if exist emission\. rmdir /q /s emission
mkdir emission
copy *.pdf emission
copy *.html emission
echo Creation repertoire reception...
if exist reception\. rmdir /q /s reception
mkdir reception

echo Demarrage BlindFTP en mode reception dans une autre fenetre...
start bftp.py -r reception -a localhost 
pause

echo --------------------------------------------------------------------------
echo Demarrage BlindFTP en mode emission, avec pauses de 5 secondes...
echo (ensuite vous pourrez ajouter/supprimer des fichiers dans ce repertoire
echo pendant que BlindFTP fonctionne)
bftp.py -b -S emission -a localhost -P 5
 
