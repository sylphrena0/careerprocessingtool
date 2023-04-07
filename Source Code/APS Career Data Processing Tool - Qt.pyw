##   █████  ██████  ███████     ██████  ██   ██ ██    ██ ███████ ██  ██████ ███████ 
##  ██   ██ ██   ██ ██          ██   ██ ██   ██  ██  ██  ██      ██ ██      ██      
##  ███████ ██████  ███████     ██████  ███████   ████   ███████ ██ ██      ███████ 
##  ██   ██ ██           ██     ██      ██   ██    ██         ██ ██ ██           ██ 
##  ██   ██ ██      ███████     ██      ██   ██    ██    ███████ ██  ██████ ███████ 
##  
##  APS Career Data Processing Tool v1.1.pyw -- written by Sylphrena Kleinsasser
##  Note: I highly recommend revising this code using Microsoft Visual Studio Code. Use what you will to package this, but I recommend PyInstaller and a tool like AdvancedInstaller
################################################################################################

import sys

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from pathlib import Path

import pandas as pd #spreadsheet management tool to allow us to import .csv files easily
import re #imports regex for data validation and search function.
import nltk #used to classify word types
import sqlite3 #our sql 'server'
from io import BytesIO #for checkboxes in GUI
from PIL import Image, ImageDraw #for checkboxes in GUI
from os import path #allows us to check if a file exists
from time import sleep #allows us to pause script for a time. Too bad it doesn't let me sleep irl
from collections import Counter #required for any semblance of speed in keyword counting
from datetime import datetime #needed to auto name exported files


if not(path.exists('APSdata.db')): #APSdata will not exist before we run the code the first time
    print("This appears to be the first time this program has run on this computer\nDownloading dependencies.")
    nltk.download('wordnet') #this code downloads wordnet libraries we need to classify word types
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    print("Done!")

################################################
########### PySide Application Setup ###########
################################################
app = QGuiApplication(sys.argv)
app.setWindowIcon(QIcon("logo.png")); #sets titlebar logo

engine = QQmlApplicationEngine()
engine.quit.connect(app.quit)
engine.load('Source Code/QtDesign.qml') #loads the gui config from the file

app.setProperty("home", Path.home()) 

sys.exit(app.exec())