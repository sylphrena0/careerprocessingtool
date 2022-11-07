@echo off


:start
cls

set python_ver=36

python ./get-pip.py

cd \
cd \python%python_ver%\Scripts\
pip install pandas
pip install PySimpleGUI
pip install regex
pip install nltk
pip install pysqlite3
pip install pillow
pip install pysinstaller

pause
exit