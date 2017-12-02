@echo off

REM ce script BAT permet de generer facilement les documentations HTML des 
REM modules Python a l'aide de pydoc.

if not exist pydoc.py goto erreur
python pydoc.py -w .\
if errorlevel 1 pause
goto fin

:erreur
echo Pour generer la documentation HTML, copiez ici pydoc.py depuis votre repertoire
echo ou se trouve Python, puis relancez ce fichier BAT.
pause

:fin
