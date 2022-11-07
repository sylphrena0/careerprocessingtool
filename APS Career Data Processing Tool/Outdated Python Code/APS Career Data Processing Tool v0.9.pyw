################################################
## 
################################################
import mysql.connector as mysql #imports SQL bridge module
import pandas as pd #spreadsheet managment tool to allow us to import .csv files easily
import numpy as np #used to replace nan syntax, used by pandas
import PySimpleGUI as sg #used to build the GUI
import plotly.graph_objects as go #used to display tables
import re #imports regex for data validation and search function.
import nltk
from mysql.connector import Error #imports error funtionality from SQL bridge
from sqlalchemy import create_engine #used for bulk SQL inserts. Much faster than line-by-line options
from io import BytesIO #for checkboxes in GUI
from PIL import Image, ImageDraw #for checkboxes in GUI
from os import path #allows us to check if a file exists
from time import sleep #allows us to pause script for a time. Too bad it doesn't let me sleep irl
from collections import Counter #required for any semblance of speed in keyword counting

#to-do: add first-run module:
#nltk.download('wordnet') #downloads wordnet library if this is the first run
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#setup sql locally

#sg.theme_add_new('APS', {'BACKGROUND': '#252525',\
#'TEXT': 'white', 'INPUT': '#111111', 'TEXT_INPUT': '#b2aca2',\
#'SCROLL': '#af0404', 'BUTTON': ('#FFFFFF', '#252525'),\
#'PROGRESS': ('#000000', '#000000'), 'BORDER': 1, 'SLIDER_DEPTH': 0,\
#'PROGRESS_DEPTH': 0, 'COLOR_LIST': ['#252525', '#414141', '#111111']})

################################################
## Menu Window Module:
################################################
def menuModule():
    sg.theme('DarkBrown4')
    sg.theme_text_color(('white'))
    sg.SetOptions(element_padding=(15, 30))
    layout = [
                [sg.Image('logo.png')],
                [sg.Text("Welcome to the APS Career Data Processing Tool!")],
                [sg.Button("Import Data"),sg.Button("Analyze Data"),sg.Button("Cancel")]
              ]

    # Create the window
    window = sg.Window("APS Career Data Processing Tool", layout, element_justification='c', finalize=True, resizable=True, icon='logo.ico', size=(500,420))
    window.set_min_size((350,390)) #sets minimum window size. Prevents cutoff of important elements

    # Create an event loop
    while True: #end program if user closes window or presses the Cancel button
        event, values = window.read()
        if event == "Cancel" or event == sg.WIN_CLOSED:
            window.close()
            break
        elif event == "Import Data":
            window.close()
            importModule()
            break
        elif event == "Analyze Data":
            window.close()
            analyzeWindowModule()
            break
    
################################################
## Import Data Window Module: [status error to fix, change error popups?]
################################################
def importModule():
    fileName = "empty" #defines fileName variable as empty so program can check if it is populated before import
    sg.theme('DarkBrown4')
    sg.theme_text_color(('white'))
    sg.theme_input_text_color(('white'))
    sg.theme_input_background_color(('black'))
    sg.SetOptions(element_padding=(15, 30))
    layout = [
                [sg.Image('logo.png')],
                [sg.Text("Import data, using filename.csv",key='text',size=(0, 1), pad=(15, 0))],
                [sg.Button("File Input", pad=(15, 30)),sg.Button("Use Default", pad=(15, 30))],
                [sg.Button("Start Import", pad=(15, 0)),sg.Button("Main Menu", pad=(15, 0)),sg.Button("Cancel", pad=(15, 0))]
              ]

    # Create the window
    window = sg.Window("APS Career Data Processing Tool", layout, element_justification='c', finalize=True, resizable=True, icon='logo.ico', size=(500,420))
    window.set_min_size((350,410)) #sets minimum window size. Prevents cutoff of important elements

    # Create an event loop
    while True: #end program if user closes window or presses the Cancel button
        event, values = window.read()
        if event == "Cancel" or event == sg.WIN_CLOSED:
            window.close()
            break
        elif event == "Use Default":
            fileName = "exported-job-data.csv"
            window['text'].update("Import data, using " + fileName) 
            window.refresh()
        elif event == "File Input":
            fileName = filePopup()
            if fileName == "CLOSED":
                pass
            elif not(path.exists(fileName)):
                notify("Error: File not found! Ensure the file is in this directory.")  #uses our custom notify function to send error to both terminal and popup
            elif not(iscsv(fileName)):
                notify("Error: File must be a csv file!")
            else: 
                print(fileName,"exists and is in directory")
                window['text'].update("Import data, using " + fileName) 
            window.refresh()
        elif event == "Main Menu":
            window.close()
            menuModule()
            break
        elif event == "Start Import":
            try:
                if fileName == "empty":
                    notify("Error: Please select a file first!")
                else:
                    importFunction(fileName)
            except:
                notify("Critical error in import function!")
    
################################################
## Analyze Data Menu Module:
################################################
def analyzeWindowModule():
    sg.theme('DarkBrown4')
    sg.theme_text_color(('white'))
    sg.SetOptions(element_padding=(15, 15))
    layout = [
                [sg.Image('logo.png')],
                [sg.Text("You may import search terms directly, via a comma seperated .txt file,\nor use the search module",justification='center',size=(60,None))],
                [sg.Text("Select search field:",pad=(0,15)),sg.Radio('Description', "query", default=True,key="desc",enable_events=True),sg.Radio('Job Title', "query",key="title",enable_events=True,pad=(0,15)),sg.Radio('Requirements', "query",key="req",enable_events=True)],                
                [sg.Button("Direct Input"),sg.Button("File Input"),sg.Button("Search Module")],
                [sg.Button("Main Menu"),sg.Button("Cancel")]
              ]

    # Create the window
    window = sg.Window("APS Career Data Processing Tool", layout, element_justification='c', finalize=True, resizable=True, icon='logo.ico', size=(500,500))
    window.set_min_size((460,470)) #sets minimum window size. Prevents cutoff of important elements

    queryType = "fDescription" #inilizies query type variable

    # Create an event loop
    while True: #end program if user closes window or presses the Cancel button
        event, values = window.read()
        if event == "Cancel" or event == sg.WIN_CLOSED:
            break
        elif event == "Main Menu":
            window.close()
            menuModule()
            break
        elif event == "Direct Input":
            keywords = keywordsPopup()
            if re.match('.*Enter keywords.*',keywords):
                notify("No keywords provided. Please try again.")
            elif re.match('.*Null.*',keywords):
                pass
            else:
                keywords = keywords.replace('\n','') #remove those pesky newline chars
                keywords = keywords.replace('\t','') #same with \t
                listTerms = list(keywords.split(",")) #turns provided string into list
                result = searchAll(listTerms,search=queryType)
                export = results(result) #displays results. Will return true if user wishes to export data.
                if export:
                    name = filePopup(msg="Please name the exported file, including file extension. This will overwrite any conflicts!",file="example_export.csv")
                    if name == "CLOSED":
                        pass
                    elif not(iscsv(name)):
                        notify("Error: File must be a csv file!")
                    else:
                        try:
                            result.to_csv(name, index=False)
                            notify("Data is exported!",title="Success")
                        except:
                            notify("Fatal Error: Check if file exists and is in use!")

        elif event == "File Input":
            fileName = filePopup(file="example_import.txt")
            if fileName == "CLOSED":
                pass
            elif not(path.exists(fileName)):
                notify("Error: File not found! Ensure the file is in this directory.")
            elif not(istxt(fileName)):
                notify("Error: File must be a csv file!")
            else: 
                print(fileName,"exists and is in directory")
                file = open(fileName,'r') #opens specified text file
                keywords = file.read() #assigns contents to keywords variable
                file.close() #closes text file
                keywords = keywords.replace('\n','') #remove those pesky newline chars
                keywords = keywords.replace('\t','') #same with \t
                listTerms = list(keywords.split(",")) #turns provided string into list
                result = searchAll(listTerms,search=queryType)
                export = results(result) #displays results. Will return true if user wishes to export data.
                if export:
                    name = filePopup(msg="Please name the exported file, including file extension. This will overwrite any conflicts!",file="example_export.csv")
                    if name == "CLOSED":
                        pass
                    elif not(iscsv(name)):
                        notify("Error: File must be a csv file!")
                    else:
                        try:
                            result.to_csv(name, index=False)
                            notify("Data is exported!",title="Success")
                        except:
                            notify("Fatal Error: Check if file exists and is in use!")
            
        elif event == "Search Module":
            listTerms = searchModule()
            print(listTerms)
            result = searchAll(listTerms)
            export = results(result) #displays results. Will return true if user wishes to export data.
            if export:
                name = filePopup(msg="Please name the exported file, including file extension. This will overwrite any conflicts!",file="example_export.csv")
                if name == "CLOSED":
                    pass
                elif not(iscsv(name)):
                    notify("Error: File must be a csv file!")
                else:
                    try:
                        result.to_csv(name, index=False)
                        notify("Data is exported!",title="Success")  
                    except:
                        notify("Fatal Error: Check if file exists and is in use!")
                

        ################################################
        ## Radio Element Event Handling (defines "queryType" when button is clicked)
        ################################################
        elif event == "desc":
            queryType = "fDescription"
        elif event == "title":
            queryType = "Title"
        elif event == "req":
            queryType = "Requirements"
        ################################################

################################################
## Data Validation Functions:
################################################
def iscsv(file): #checks if given file name ends in .csv
    if re.match('^.*\.csv',file):
        return True
    else:
        return False

def istxt(file): #checks if given file name ends in .txt
    if re.match('^.*\.txt',file):
        return True
    else:
        return False

################################################
## Popup Functions:
################################################
def filePopup(msg="Please include file extension. The file must be in this directory.",file='Enter Filename:'):
    sg.theme('DarkBrown4')
    sg.theme_text_color(('white'))
    sg.theme_input_text_color(('#b2aca2'))
    sg.theme_input_background_color(('black'))
    sg.SetOptions(element_padding=(15, 10))
    layout = [
                [sg.Text(msg,justification='center',size=(40,None))],
                [sg.Input(file, key='file')],
                [sg.Button("OK"),sg.Button("Cancel")]
              ]

    # Create the window
    window = sg.Window("Filename Input", layout, element_justification='c', finalize=True, resizable=False, icon='logo.ico',size=(420, 150))

    # Create an event loop
    while True: #end program if user closes window or presses the Cancel button
        event, values = window.read()
        if event == "Cancel" or event == sg.WIN_CLOSED:
            window.close()
            return "CLOSED" #break would cause errors here, since we need the module to return a value
        elif event == "OK":
            fileName = str(values['file'])
            window.close()
            break
    return fileName #sends the filename back to the module that called this function

def keywordsPopup():
    sg.theme('DarkBrown4')
    sg.theme_text_color(('white'))
    sg.theme_input_text_color(('#b2aca2'))
    sg.theme_input_background_color(('black'))
    sg.SetOptions(element_padding=(15, 10))
    layout = [
                [sg.Text("Enter your keywords below, seperated by commas.\nYou may use \"|\" for OR and \"+\" for AND.\nRegex is supported.",justification='center',size=(40,None))],
                [sg.Multiline(default_text="Enter keywords",size=(30, 5), autoscroll=True, key='keywords',no_scrollbar=True)],
                [sg.Button("OK"),sg.Button("Cancel")]
              ]

    # Create the window
    window = sg.Window("Keywords Input", layout, element_justification='c', resizable=False, icon='logo.ico')

    # Create an event loop
    while True: #end program if user closes window or presses the Cancel button
        event, values = window.read()
        if event == "Cancel" or event == sg.WIN_CLOSED:
            window.close()
            return "Null" #break would cause errors here, since we need the module to return a value
        elif event == "OK":
            keywords = str(values['keywords'])
            window.close()
            break
    return keywords #sends the filename back to the module that called this function

def notify(msg,title="Error!",bttn='OK',timeout=3): #this will log an msg to terminal and have a popup declare the msg. Defaults to "Error!" title Allows multiple centered lines with \n. 
    print(msg)
    sg.theme('DarkBrown4')
    sg.theme_text_color(('white'))
    sg.theme_input_text_color(('white'))
    sg.theme_input_background_color(('black'))
    sg.SetOptions(element_padding=(15, 10))
    layout = [
                [sg.Text(msg, key='msg',justification='center',size=(40,None))],
                [sg.Button(bttn)]
            ]

    # Create the window
    window = sg.Window(title, layout, element_justification='c', resizable=False, icon='logo.ico',auto_close_duration=timeout)

    # Create an event loop
    while True: #end program if user closes window or presses the Cancel button
        event, values = window.read()
        if event == bttn or event == sg.WIN_CLOSED:
            window.close()
            break

def results(df,timeout=3): #this shows search results and allow the user to export data. Allows multiple centered lines with \n. 
    sg.theme('DarkBrown4')
    sg.theme_text_color(('white'))
    sg.SetOptions(element_padding=(15, 10))
    
    ## Process dataframe to print in gui
    ################################################
    df.insert(0,"Term",df.index,True) #pysimplegui can't display row index, so this adds row labels as a column.
    data = df.values.tolist() #read everything else into a list of rows
    header_list = list(df.columns) #uses the first row (which should be column names) as columns names
    ################################################

    layout = [
                [sg.Table(values=data,
                        headings=header_list,
                        #def_col_width=10,
                        text_color="white",
                        #alternating_row_color="",
                        selected_row_colors="#EDEDED on #151515",
                        header_background_color="#101010",
                        hide_vertical_scroll=True,
                        display_row_numbers=False,
                        auto_size_columns=False,
                        num_rows=min(25, len(data)))],
                [sg.Button("OK"),sg.Button("Export Results")]
            ]

    #layout = [
    #            #[sg.Text(results, key='msg',justification='center',size=(40,None))],
    #            [sg.Multiline(default_text=results,size=(30, 5), autoscroll=True, key='results',no_scrollbar=True)],
    #            [sg.Button("OK"),sg.Button("Export Data")]
    #        ]

    # Create the window
    window = sg.Window("Search Results", layout, element_justification='c', resizable=True, icon='logo.ico',auto_close_duration=timeout)

    # Create an event loop
    while True: #end program if user closes window or presses the Cancel button
        event, values = window.read()
        if event == "OK" or event == sg.WIN_CLOSED:
            window.close()
            return False
        if event == "Export Results":
            window.close()
            return True

################################################
## Job Import Function:
################################################
def importFunction(file): #imports job data from specifed .csv file
    jobData = pd.read_csv(file,index_col=False)
    jobData.head()

    ################################################
    ## Status Window Definition:
    ################################################
    msg = "Importing " + file
    sg.theme('DarkBrown4')
    sg.theme_text_color(('white'))
    sg.theme_input_text_color(('white'))
    sg.theme_input_background_color(('black'))
    sg.SetOptions(element_padding=(15, 10))
    layout = [
                [sg.Text(msg, key='status')]
              ]
    window = sg.Window("Importing Data", layout, finalize=True, element_justification='c', resizable=True, icon='logo.ico',size=(225,50)) #finalize allows us to continue without closing window
    ################################################

    try: #try-except handles errors
        conn = mysql.connect( #connects to mySQL database. Use host=localhost if sql is running on the same machine
          host="10.42.102.235",
          user="apsdata",
          password="4m3E5yM^"
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("use aps") #selects database
            cursor.execute("select database();")
            cursor.fetchone()
            window['status'].update("You're connected to the APS database") #these status updates require window.refresh(). 
            window.refresh()
            sleep(0.5)
            cursor.execute('DROP TABLE IF EXISTS aps.Jobs;')
            window['status'].update("Creating table....")
            window.refresh()
            sleep(0.5)
            cursor.execute("create table Jobs\
                (jid int AUTO_INCREMENT,\
                Temporary varchar(5),\
                tFlagged varchar(5),\
                Sector text,\
                sFlagged varchar(5),\
                sComments text,\
                BillingName text,\
                EmployerName text,\
                fDescription text,\
                NetworkName text,\
                AdditionalSalaryInfo text,\
                CategoryList text,\
                CountryName varchar(52),\
                City varchar(85),\
                Title varchar(150),\
                Requirements text,\
                DateTimePosted text,\
                SectorList text,\
                DisciplineName varchar(52),\
                EducationLevel varchar(30),\
                IndustryName varchar(30),\
                JobLevel varchar(30),\
                JobType varchar(25),\
                Salary varchar(35),\
                JobApplicationQty int,\
                ViewQty int,\
                CandidatesDeliveredQty int,\
                Department varchar(15),\
                StateName text,\
                primary key (jid))\
                engine = innodb")
            window['status'].update("Jobs table created...")
            window.refresh()
            sleep(0.5)
            window['status'].update("Inserting data...")
            window.refresh()
            sleep(0.5)

        ################################################
        ## SQL Insert (via dataframe)
        ################################################     
        engine = create_engine("mysql+pymysql://{user}:{pw}@10.42.102.235/{db}" #creates sqlalchemy engine 
                              .format(user="apsdata", pw="4m3E5yM^", 
                              db="aps"), pool_pre_ping=True)
        #insert whole DataFrame into MySQL
        jobData.to_sql('Jobs', con = engine, if_exists = 'append', chunksize = 1000,index=False)
        
        #close the connection
        if (conn.is_connected()):
            cursor.close()
            conn.close()
            window['status'].update("MySQL connection is closed")
            window.refresh()
            sleep(0.5)

        window['status'].update("Data successfully imported!")
        window.refresh()
        sleep(3)
        window.close()

        ################################################
        ## Alternate SQL Insert (line-by-line) -- slow
        ################################################
        #for i,row in jobData.iterrows():
        #    row = row.fillna("")
        #    sql = "Replace INTO aps.Jobs (jid,Temporary,tFlagged,Sector,sFlagged,sComments,\
        #                        BillingName,EmployerName,fDescription,NetworkName,AdditionalSalaryInfo,\
        #                        CategoryList,CountryName,City,Title,Requirements,DateTimePosted,\
        #                        SectorList,DisciplineName,EducationLevel,IndustryName,\
        #                        JobLevel,JobType,Salary,JobApplicationQty,ViewQty,\
        #                        CandidatesDeliveredQty,Department,StateName\
        #                        )VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        #    ins = (i,) + tuple(row)
        #    cursor.execute(sql, ins)
        #    print("Record",i,"inserted. ", end = "\r") #will look OK in terminal, but not in idle
        #    conn.commit() #the connection is not autocommitted by default, so we  must commit to save our changes
        ################################################
    
    except Error as e:
        notify("Critical error while connecting to MySQL for data insertion/n" + e)

################################################
## Keyword Counter Module:
################################################
def getdesc(): #gets all job descriptions as a string. A little slow on large datasets.
    try:
        notify("This may take some time.",title="Warning")
        conn = mysql.connect( #connects to mySQL database. Use host=localhost if sql is running on the same machine
            host="10.42.102.235",
            user="apsdata",
            password="4m3E5yM^"
        )
        cursor = conn.cursor()
        sql = "SELECT fDescription FROM Jobs" #the query sent to mySQL
        cursor.execute("use aps") #selects database
        cursor.execute(sql) #executes the query

        #query returns a list of tuples:
        strResult = str(cursor.fetchall()).strip('[]') 

        #close the connection
        if (conn.is_connected()):
            cursor.close()
            conn.close()
        return strResult
    except:
        notify("Critical error while connecting to MySQL\nto get job descriptions.")
        
def topTerms(searchText, minhits=1000, wordtype="J"): #module that counts words in provided searchText, prompts users to select words to keep, and returns list of selected words. Parts of code cookbooked from: https://stackoverflow.com/questions/65773214/is-it-possible-to-insert-a-checkbox-in-a-pysimplegui-table
    #Minhits allows you to specify how many times a word has to be repeated in the data to be returned.
    #Type allows you to specify what type of word you want. N=noun,V=verb,J=descriptor.
    def count(text): #nested function that actually counts words
        #N=noun,V=verb,J=descriptor
        stopwords = ['a', 'about', 'above', 'across', 'after', 'afterwards', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'amoungst', 'amount', 'an', 'and', 'another', 'any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere', 'are', 'around', 'as', 'at', 'back', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'below', 'beside', 'besides', 'between', 'beyond', 'bill', 'both', 'bottom', 'but', 'by', 'call', 'can', 'cannot', 'cant', 'co', 'computer', 'con', 'could', 'couldnt', 'cry', 'de', 'describe', 'detail', 'did', 'do', 'done', 'down', 'due', 'during', 'each', 'eg', 'eight', 'either', 'eleven', 'else', 'elsewhere', 'empty', 'enough', 'etc', 'even', 'ever', 'every', 'everyone', 'everything', 'everywhere', 'except', 'few', 'fifteen', 'fifty', 'fill', 'find', 'fire', 'first', 'five', 'for', 'former', 'formerly', 'forty', 'found', 'four', 'from', 'front', 'full', 'further', 'get', 'give', 'go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'however', 'hundred', 'i', 'ie', 'if', 'in', 'inc', 'indeed', 'interest', 'into', 'is', 'it', 'its', 'itself', 'keep', 'last', 'latter', 'latterly', 'least', 'less', 'ltd', 'made', 'many', 'may', 'me', 'meanwhile', 'might', 'mill', 'mine', 'more', 'moreover', 'most', 'mostly', 'move', 'much', 'must', 'my', 'myself', 'name', 'namely', 'neither', 'never', 'nevertheless', 'next', 'nine', 'no', 'nobody', 'none', 'noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'part', 'per', 'perhaps', 'please', 'put', 'rather', 're', 's', 'same', 'see', 'seem', 'seemed', 'seeming', 'seems', 'serious', 'several', 'she', 'should', 'show', 'side', 'since', 'sincere', 'six', 'sixty', 'so', 'some', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhere', 'still', 'such', 'system', 'take', 'ten', 'than', 'that', 'the', 'their', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein', 'thereupon', 'these', 'they', 'thick', 'thin', 'third', 'this', 'those', 'though', 'three', 'three', 'through', 'throughout', 'thru', 'thus', 'to', 'together', 'too', 'top', 'toward', 'towards', 'twelve', 'twenty', 'two', 'un', 'under', 'until', 'up', 'upon', 'us', 'very', 'via', 'was', 'we', 'well', 'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'with', 'within', 'without', 'would', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves']
        stopwords.extend(['the', 'it']) #adds more stopwords (words to remove from text)
        
        if wordtype != None: 
            print("Selecting desired types of words")
            wordlist = [word.lower() for (word, pos) in nltk.pos_tag(nltk.word_tokenize(text)) if pos[0] == 'J']  #selects specfied type of word using nltk language processing, then removes case
        else:
            print("Removing punction from job descriptions")
            text = re.sub('[^\w\s]','',text) #removes punctuation with regex
            print("Removing case from job descriptions")
            text = text.lower() #turn string to lowercase
            print("Splitting text into a list of words")
            wordlist = text.split() #splits string into list of words

        print("Removing stopwords")
        wordlist = [w for w in wordlist if (w not in stopwords)] #removes stopwords, defined above
        print("Counting",len(wordlist),"words")
        counts = Counter()
        counts.update(wordlist) #counts words. Much much faster than the fastest manual code for this
        wordlist = [[key,val] for key, val in counts.items()if not (isinstance(val, int) and (val < minhits))] #turns data into set of sets, limits results to specified amount of hits
        print("Sorting results")
        wordlist = sorted(wordlist,key=lambda x: x[1]) #sorts list by frequency. Faster alterntives exist, but this is simpler
        wordlist.reverse() #sets list to desc order

        return wordlist

    def icon(check): #nested function to make and update checkmarks 
        box = (50, 32) #container for check
        background = (255, 255, 255, 0)
        line = ((9, 17), (15, 23), (23, 9))
        im = Image.new('RGBA', box, background)
        draw = ImageDraw.Draw(im, 'RGBA')
        #rectangle = (3, 3, 29, 29) #defines size for border around check
        #draw.rectangle(rectangle, outline='white', width=3) #adds border around check
        if check == 1:
            draw.line(line, fill='white', width=3, joint='curve')
        with BytesIO() as output:
            im.save(output, format="PNG")
            png = output.getvalue()
        return png

    check = [icon(0), icon(1), icon(2)] #adds allias to icon()

    headings = ['Search Term', 'Hits'] #defines table (technically tree) headers
    data = count(searchText) #calls nested function to count words

    treedata = sg.TreeData() #adds allias for sg.TreeData
    treemeta = [] #initialise treemeta list 

    for term, hits in data:
        treedata.Insert('', term, term, values=[hits], icon=check[1]) #gets data from counter and inserts data to table
        treemeta.append(term) #fills intial metadata list

    sg.theme('DarkBrown4')
    sg.theme_text_color(('white'))
    sg.theme_input_text_color(('white'))
    sg.theme_input_background_color(('black'))
    sg.SetOptions(element_padding=(15, 8))
    sg.set_options(font=('Helvetica', 12))
    layout = [
        [sg.Text('Deselect undesired search terms', key='msg',justification='center')],
        [sg.Tree(data=treedata, headings=headings[1:], auto_size_columns=True,
            num_rows=10, col0_width=20, key='-TREE-', row_height=48, metadata=treemeta,
            show_expanded=False, enable_events=True,justification='center',
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,text_color='white',selected_row_colors=('black','grey'),header_text_color='black', header_background_color='#808080')],
        [sg.Button('Submit')]
    ]
    window = sg.Window('Search Results', layout, element_justification='c', finalize=True, size=(350,615))
    tree = window['-TREE-']
    tree.Widget.heading("#0", text=headings[0]) # Set heading for column #0

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Submit'):
            break
        elif event == '-TREE-':
            term = values['-TREE-'][0]
            if term in tree.metadata:
                tree.metadata.remove(term)
                tree.update(key=term, icon=check[0])
            else:
                tree.metadata.append(term)
                tree.update(key=term, icon=check[1])
    window.close()
    return tree.metadata #returns list of selected data

def searchModule(): #asks for options. inerfaces with topTerms() and main menu 
    sg.theme('DarkBrown4')
    sg.theme_text_color(('white'))
    sg.theme_input_text_color(('white'))
    sg.theme_input_background_color(('black'))
    sg.SetOptions(element_padding=(5, 10))
    layout = [
                [sg.Text("Please select which words you would like to count, and the minimum hits each word must reach to be selected.", key='msg',justification='center',size=(40,None))],
                [sg.Radio('All', "WORDTYPE", default=True,key="All",enable_events=True),sg.Radio('Verbs', "WORDTYPE",key="Verbs",enable_events=True),sg.Radio('Nouns', "WORDTYPE",key="Nouns",enable_events=True),sg.Radio('Adjectives', "WORDTYPE",key="Adjectives",enable_events=True)],
                [sg.Text("Minimum Hits:",justification='center'),sg.Input("1000", key='hits',justification='center',size=(10,1))],
                [sg.Button("OK",pad=(15, 10)),sg.Button("Cancel",pad=(15, 10))]
            ]

    # Create the window
    window = sg.Window("Select Options", layout, element_justification='c', resizable=False, icon='logo.ico')

    type = None #intilizes backend word type as "any" 

    # Create an event loop
    while True: #end program if user closes window or presses the Cancel button
        event, values = window.read()
        if event == "Cancel" or event == sg.WIN_CLOSED:
            window.close()
            break
        ################################################
        ## Radio Element Event Handling (defines "Type" when button is clicked)
        ################################################
        elif event == "All":
            type = None
        elif event == "Verbs":
            type = "V"
        elif event == "Nouns":
            type = "N"
        elif event == "Adjectives":
            type = "J"
        ################################################
        elif event == 'OK':
            try: #checks that min hits is an int, returns error if false
                hits = int(values['hits'])
            except:
                notify("Error: Minimum hits must be an integer!") 
                window.close()
                break
            window.close()
            return topTerms(searchText=getdesc(),minhits=hits,wordtype=type)
               
################################################
## Query Module:
################################################
def allJobs(searchTerms, search="fDescription"): #counts all jobs which contain terms.
    try:
        conn = mysql.connect( #connects to mySQL database. Use host=localhost if sql is running on the same machine
            host="10.42.102.235",
            user="apsdata",
            password="4m3E5yM^"
        )
        results = {}
        for term in searchTerms:
            cursor = conn.cursor()
            sql = "SELECT count(*) FROM Jobs where {} REGEXP %s".format(search) #the query sent to mySQL, where %s is a placeholder, defined in the next few lines
            regex = ("(?i).*{}.*".format(term),) #the string that replaces %s. Here .format(term) replaces {} with the search term variable
            cursor.execute("use aps") #selects database
            cursor.execute(sql, regex) #executes the query

            #query returns a list of tuples, but there is only one element. Best to extract the number now:
            listResult = cursor.fetchall() 
            tupleResult = listResult[0]
            results[term] = tupleResult[0] #adds results to dictionary

        #close the connection
        if (conn.is_connected()):
            cursor.close()
            conn.close()
        return results
    except:
        notify("Critical error while connecting to MySQL\nwhile searching all jobs.")

def temporaryJobs(searchTerms, search="fDescription"): #counts temp jobs which contain terms. Note that the import makes false = 0 and true = 1 in the database for some reason.
    try:
        conn = mysql.connect( #connects to mySQL database. Use host=localhost if sql is running on the same machine
            host="10.42.102.235",
            user="apsdata",
            password="4m3E5yM^"
        )
        results = {}
        for term in searchTerms:
            cursor = conn.cursor()
            sql = "SELECT count(*) FROM Jobs where {} REGEXP %s and Temporary = 1".format(search) #the query sent to mySQL, where %s is a placeholder, defined in the next few lines
            regex = ("(?i).*{}.*".format(term),) #the string that replaces %s. Here .format(term) replaces {} with the search term variable
            cursor.execute("use aps") #selects database
            cursor.execute(sql, regex) #executes the query

            #query returns a list of tuples, but there is only one element. Best to extract the number now:
            listResult = cursor.fetchall() 
            tupleResult = listResult[0]
            results[term] = tupleResult[0] #adds results to dictionary

        #close the connection
        if (conn.is_connected()):
            cursor.close()
            conn.close()
        return results
    except:
        notify("Critical error while connecting to MySQL\nwhile searching temporary jobs.")

def searchAll(keylist,search='fDescription'):
    keylist = [(''.join(['(?=.*',term.replace('+',')(?=.*'),')']) if '+' in term else term) for term in keylist] #this does all the work enabling the "+" operator in an efficent, one-line manner.
    alls = allJobs(keylist,search)
    temp = temporaryJobs(keylist,search)
    data = {'all': alls,'temp': temp} #formats dictionary terms (the results from above) for parsing by pandas
    tabledData = pd.DataFrame.from_dict(data, orient='index') #organizies data into a table, easily exportable into GUIs and .csv
    return tabledData
    
################################################

menuModule() #runs program