##   █████  ██████  ███████     ██████  ██   ██ ██    ██ ███████ ██  ██████ ███████ 
##  ██   ██ ██   ██ ██          ██   ██ ██   ██  ██  ██  ██      ██ ██      ██      
##  ███████ ██████  ███████     ██████  ███████   ████   ███████ ██ ██      ███████ 
##  ██   ██ ██           ██     ██      ██   ██    ██         ██ ██ ██           ██ 
##  ██   ██ ██      ███████     ██      ██   ██    ██    ███████ ██  ██████ ███████ 
##  
##  APS Career Data Processing Tool v1.1.pyw -- written by Sylphrena Kleinsasser
##  Note: For your sanity, I highly recommend revising this code using Microsoft Visual Studio Code, not idle or N++. Use what you will to package this, but I recommend PyInstaller and a tool like AdvancedInstaller
################################################################################################
import pandas as pd #spreadsheet management tool to allow us to import .csv files easily
import PySimpleGUI as sg #used to build the GUI
import re #imports regex for data validation and search function.
import nltk #used to classify word types
import sqlite3 #our sql 'server'
from io import BytesIO #for checkboxes in GUI
from PIL import Image, ImageDraw #for checkboxes in GUI
from os import path #allows us to check if a file exists
from time import sleep #allows us to pause script for a time. Too bad it doesn't let me sleep irl
from collections import Counter #required for any semblance of speed in keyword counting
from datetime import datetime #needed to auto name exported files

################################################
## Theme Settings:
################################################
#these lines set global themes for our windows with PySimpleGUI. See all options here: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#themes
sg.theme('DarkBrown4') #this is one of the best themes, but we need some adjustments to make it... not tacky:
sg.theme_text_color(('white'))
sg.theme_input_text_color(('white'))
sg.theme_input_background_color(('#111111'))

################################################
## Menu Window Module:
################################################
def menuModule(): #this is the function that creates the first window (main menu). Anytime menuModule() is called, this function will run and return to this window. I'll only document basic window elements here as I use them many many times. 
    #for documentation on GUI options, dig in here: https://pysimplegui.readthedocs.io/en/latest/call%20reference/

    sg.SetOptions(element_padding=(15, 30)) #sets default element padding. Must be defined for each window, or results will be unpredictable
    layout = [ #this defines the layout as a list of lists
                [sg.Image('logo.png')], #adds the APS logo
                [sg.Text("Welcome to the APS Career Data Processing Tool!")], #adds text
                [sg.Button("Import Data"),sg.Button("Analyze Data"),sg.Button("Cancel")] #adds buttons
              ]

    #defines and opens window using defined layout. First element is window title. Finalize is used pretty much everywhere as it allows us to edit the window after definition (we use this for max size, changing text, and a bunch of other things). Size is W x H:
    window = sg.Window("APS Career Data Processing Tool", layout, element_justification='c', finalize=True, resizable=True, icon='logo.ico', size=(500,420)) 
    window.set_min_size((350,390)) #sets minimum window size. Prevents cutoff of important elements

    #create an event loop to control window events like button clicks or an exit:
    while True: #end program if user closes window or presses the Cancel button
        event, values = window.read()
        if event == "Cancel" or event == sg.WIN_CLOSED: #handles window close and activates our cancel button
            window.close()
            break
        elif event == "Import Data": #activates our import button, which calls the function which will open the import module, then closes the main menu
            window.close()
            importModule()
            break
        elif event == "Analyze Data": #activates our analyze button, which calls the function which will open the analyze module, then closes the main menu
            window.close()
            analyzeWindowModule()
            break
    
################################################
## Import Data Window Module:
################################################
def importModule(): #function that creates import window and calls job import functions
    fileName = "empty" #defines fileName variable as empty so program can check if it is populated before import

    sg.SetOptions(element_padding=(15, 30))
    layout = [
                [sg.Image('logo.png')],
                [sg.Text("Import data, using filename.csv",key='text',size=(0, 1), pad=(15, 0))], #we'll update this text with window['text'].update() and window.refresh()
                [sg.Button("File Input"),sg.Button("Use Default")],
                [sg.Button("Start Import", pad=(15, 0)),sg.Button("Main Menu", pad=(15, 0)),sg.Button("Cancel", pad=(15, 0))]
              ]

    #create the window:
    window = sg.Window("APS Career Data Processing Tool", layout, element_justification='c', finalize=True, resizable=True, icon='logo.ico', size=(500,420))
    window.set_min_size((350,410)) #sets minimum window size. Prevents cutoff of important elements

    #create an event loop:
    while True: 
        event, values = window.read()
        if event == "Cancel" or event == sg.WIN_CLOSED:
            window.close()
            break
        elif event == "Use Default": #updates file to default value if user clicks our default button
            fileName = "import-job-data_example.csv"
            window['text'].update("Import data, using " + fileName)  #updates text
            window.refresh() #this is super important. Text will not update without a refresh
        elif event == "File Input": #calls our file input popup to ask user for custom filename
            fileName = sg.popup_get_file('', no_window=True,file_types=(("Comma Separated Files", "*.csv"),)) #simplified way to get file, using native file popup. Much better for installations
            if not(path.exists(fileName)): #checks that file exists. Prevents bugs that might pass the dialog
                notify("Error: File not found! Ensure the file is in this directory.")
            else:  #runs code if validation passes
                nameOnly = path.basename(fileName)
                window['text'].update("Import data, using " + nameOnly) #updates text
                window.refresh() #really, don't forget this!
        elif event == "Main Menu": #takes us back to the main menu if button is clicked, by simply closing this window and calling menuModule()
            window.close()
            menuModule()
            break
        elif event == "Start Import": #starts import after defining the filename
            try: #try-except are super handy ways to handle errors. If an error is called, we'll move on to except without erroring out in the python fashion
                if fileName == "empty": #validates that user has selected a file
                    notify("Error: Please select a file first!")
                else: #calls import function if all izz well :)
                    importFunction(fileName)
            except:
                notify("Critical error in import function!")
    
################################################
## Analyze Data Menu Module:
################################################
def analyzeWindowModule(): #function that creates analyze window that calls analyze functions

    def showResults(resultList): #defines nested function that will results and exporting
        result = resultList[0] #grabs actual results from the list we make in searchAll() 
        searchfield = resultList[1] #grabs the search term we used, returned from searchAll()
        exportFilename = path.expanduser('~\\Documents\\') + datetime.now().strftime("APS Export - %m.%d.%Y (using ") + searchfield + ").csv" #generates the filename. Feel free to change format, but don't remove ".csv". path.expanduser('~\\Documents\\') will get the location of my documents
        export = results(result) #displays results window. This will return true if user wishes to export data.
        if export: #opens export window if selected in results window
            name = filePopup(msg="Please name the exported file, including file extension. This will overwrite any conflicts!",file=exportFilename) #grabs a custom filename
            if name == "CLOSED": #moves past if statement gracefully if user exited filePopup dialog
                pass
            elif not(isCsv(name)): #validates the file extension
                notify("Error: File must be a csv file!")
            else:
                try:
                    result.to_csv(name, index=False) #uses a pandas method to export data to csv file
                    notify("Data is exported!",title="Success")
                except: #handles errors
                    notify("Fatal Error: Invalid export location. Check your path and ensure that you are not attempting to overwrite a file that is in use.")

    sg.SetOptions(element_padding=(15, 15))

    #I use size=(60,None) to allow me to force text to rollover if it is longer than the first value specified. Best if used with justification='center' (for the element settings) AND element_justification='c' (window settings):
    layout = [
                [sg.Image('logo.png')],
                [sg.Text("You may import search terms directly, via a comma separated .txt file,\nor use the search module",justification='center',size=(60,None))], #\n in a string makes a new line
                [sg.Button("Direct Input"),sg.Button("File Input"),sg.Button("Search Module")],
                [sg.Button("Main Menu"),sg.Button("Cancel")]
              ]

    #create the window
    window = sg.Window("APS Career Data Processing Tool", layout, element_justification='c', finalize=True, resizable=True, icon='logo.ico', size=(500,400))
    window.set_min_size((460,400)) #sets minimum window size. Prevents cutoff of important elements

    #create the event loop
    while True: #end program if user closes window or presses the Cancel button
        event, values = window.read()
        if event == "Cancel" or event == sg.WIN_CLOSED:
            break
        elif event == "Main Menu":
            window.close()
            menuModule()
            break
        elif event == "Direct Input": #handles direct text input
            keywords = keywordsPopup() #prompts user with custom popup
            if re.match('Enter keywords',keywords): #ensures that user entered something
                notify("No keywords provided. Please try again.")
            else:
                keywords = keywords.replace('\n','') #remove those pesky newline chars
                keywords = keywords.replace('\t','') #same with \t
                listTerms = list(keywords.split(",")) #turns provided string into list
                returnedResults = searchAll(listTerms) #searches with provided terms
                if returnedResults != "CLOSED": showResults(returnedResults) #calls our nested function to handle results if it wasn't ended prematurely

        elif event == "File Input": #handles text file input
            fileName = sg.popup_get_file('', no_window=True,file_types=(("Text Files", "*.txt"),))
            if not(path.exists(fileName)): #checks that file exists. Prevents bugs that might pass the dialog
                notify("Error: File not found! Ensure the file is in this directory.")
            else:  #runs code if validation passes
                file = open(fileName,'r') #opens specified text file
                keywords = file.read() #assigns contents to keywords variable
                file.close() #closes text file
                keywords = keywords.replace('\n','') #remove those pesky newline chars
                keywords = keywords.replace('\t','') #same with \t
                listTerms = list(keywords.split(",")) #turns provided string into list
                returnedResults = searchAll(listTerms) #searches with provided terms
                if returnedResults != "CLOSED": showResults(returnedResults) #calls our nested function to handle results if it wasn't ended prematurely

            
        elif event == "Search Module": #handles search module input
            listTerms = searchModule() #opens search module. Will return  
            if listTerms == "CLOSED": #gracefully moves on if user exited out of search module
                pass
            else:
                returnedResults = searchAll(listTerms) #searches with search module terms
                if returnedResults != "CLOSED": showResults(returnedResults) #calls our nested function to handle results if it wasn't ended prematurely

################################################
## Data Validation Functions:
################################################
def isCsv(file): #checks if given file name ends in .csv using regex
    if re.match('^.*\.csv',file):
        return True
    else:
        return False

def isTxt(file): #checks if given file name ends in .txt using regex
    if re.match('^.*\.txt',file):
        return True
    else:
        return False

################################################
## Popup Functions:
################################################
def filePopup(msg="Please include file extension. The file must be in this directory.",file='Enter Filename:'): #prompts user for a filename
    sg.SetOptions(element_padding=(15, 10))
    layout = [
                [sg.Text(msg,justification='center',size=(40,None))],
                [sg.Input(file, key='file',size=(75,1))],
                [sg.Button("OK"),sg.Button("Cancel")]
              ]

    # Create the window
    window = sg.Window("Filename Input", layout, element_justification='c', finalize=True, resizable=False, icon='logo.ico',size=(510, 160))
    window['file'].Widget.config(insertbackground='#b2aca2') #fixes the cursor color!

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

def keywordsPopup(): #prompts user for keywords
    sg.SetOptions(element_padding=(15, 10))
    layout = [
                [sg.Text("Enter your keywords below, separated by commas.\n\nYou may use \"|\" for OR and \"+\" for AND. You may use \"_\" wildcards for single characters, \"%\" for zero or more characters.",justification='center',size=(40,None))],
                [sg.Multiline(default_text="Enter keywords",size=(30, 5), autoscroll=True, key='keywords',no_scrollbar=True)],
                [sg.Button("OK"),sg.Button("Cancel")]
              ]

    # Create the window
    window = sg.Window("Keywords Input", layout, element_justification='c', resizable=False, finalize=True, icon='logo.ico')
    window['keywords'].Widget.config(insertbackground='#b2aca2') #fixes the cursor color!

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

def notify(msg,title="Error!",button='OK',timeout=3): #this will log an msg to terminal and have a popup declare the msg. Defaults to "Error!" title. Allows multiple centered lines with \n. 
    print(msg)
    sg.SetOptions(element_padding=(15, 10))
    layout = [
                [sg.Text(msg, key='msg',justification='center',size=(40,None))],
                [sg.Button(button)]
            ]

    # Create the window
    window = sg.Window(title, layout, element_justification='c', resizable=False, icon='logo.ico',auto_close_duration=timeout)

    # Create an event loop
    while True: #end program if user closes window or presses the Cancel button
        event, values = window.read()
        if event == button or event == sg.WIN_CLOSED:
            window.close()
            break

def results(df): #this shows search results and returns True if user wishes to export data
    sg.SetOptions(element_padding=(15, 10))
    
    ## Process DataFrame to print in gui
    ################################################
    df.insert(0,"Term",df.index,True) #PySimpleGUI can't display row index, so this adds row labels as a column.
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

    # Create the window
    window = sg.Window("Search Results", layout, element_justification='c', resizable=True, finalize=True, icon='logo.ico')
    window.set_min_size((250,120)) #sets minimum window size. Prevents cutoff of important elements

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
def importFunction(file): #imports job data from specified .csv file
    jobData = pd.read_csv(file,index_col=False) #imports data to variable for later use using pandas

    ################################################
    ## Status Window Definition:
    ################################################
    msg = "Importing " + file
    sg.SetOptions(element_padding=(15, 10))
    layout = [
                [sg.Text(msg, key='status')]
              ]
    window = sg.Window("Importing Data", layout, finalize=True, element_justification='c', resizable=True, icon='logo.ico',size=(225,50)) #finalize allows us to continue without closing window
    ################################################

    try: #try-except handles errors
        conn = sqlite3.connect('APSdata.db') #connects to database. Creates database if it does not exist
        cursor = conn.cursor() #defines the cursor used to execute commands
        window['status'].update("Creating Table") #updates status window
        window.refresh() #status updates require window.refresh(). 
        sleep(0.5) #allows user to read before continuing
        cursor.execute('DROP TABLE IF EXISTS Jobs;') #drops existing data if it exists
        window['status'].update("Creating table....")
        window.refresh()
        sleep(0.5)

        #creates table. This is what you need to change to change the structure of imported data. Order is important. Ensure you are using correct datatypes (https://www.w3schools.com/sql/sql_datatypes.asp, though they are a little funky for sqlite)
        cursor.execute('''create table Jobs\
            ([generated_id] int PRIMARY KEY,\
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
            DateTimePosted date,\
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
            StateName text)''') #creates table with type constraints

        window['status'].update("Jobs table created...")
        window.refresh()
        sleep(0.5)
        window['status'].update("Inserting data...")
        window.refresh()
        sleep(0.5)        
        jobData.to_sql('Jobs', conn, if_exists = 'append', chunksize = 1000,index=False) #inserts whole DataFrame into sqllite3 using pandas. Wow, that was easy compared to other solutions!
        window['status'].update("Data successfully imported!")
        window.refresh()
        sleep(3)
        window.close()
    
    except:
        notify("Critical error while connecting to SQL for data insertion")

################################################
## Keyword Counter Module:
################################################
def getDesc(sector,perm,level,degree,state,startDate="",endDate=""): #gets all job descriptions as a string
    #convert from text temporary/permanent to boolean 1s and 0s:
    if perm == "Temporary": 
        perm = 1
    elif perm == "Permanent":
        perm = 0
    else: #we use permanence as a base to build the sql query. For simplicity, we always have this condition and just put an sql wildcard so it will not filter if a permanence filter is not selected
        perm = "%"
    
    try:
        conn = sqlite3.connect('APSdata.db') #connects to database. Creates database if it does not exist
        cursor = conn.cursor() #defines the cursor used to execute commands
        sql = "SELECT fDescription FROM Jobs WHERE (Temporary LIKE '%{}%')".format(perm) #we need a starting condition to build the query or we have a chance of building a nonsense query, so this condition will always exist

        if sector != "Sector Filter": #adds sector condition, if a condition is selected ("Sector Filter" is the default value, the var "sector" will contain the sector when the filter was selected)
            sql += " AND (Sector LIKE '%{}%')".format(sector) #the .format() method is way faster and easier pathway to insert our sector variable than python concatenation. The += operand appends this condition on our already defined sql query
        if degree != "Degree Requirement Filter": #adds degree condition if selected
            sql += " AND (EducationLevel LIKE '%{}%')".format(degree)
        if level != "Job Level Filter": #adds job condition if selected
            sql += " AND (JobLevel LIKE '%{}%')".format(level)
        if state != "State Filter": #adds state condition if selected
            sql += " AND (StateName LIKE '%{}%')".format(state)
        #if startDate != "": #this enables adding date conditions. Disabled due to issues with formatting of inputted data. You need to enable in other places as well
        #    sql += " AND (DateTimePosted >= datetime('{}'))".format(startDate)
        #if endDate != "":
        #    sql += " AND (DateTimePosted <= datetime('{}'))".format(endDate)

        cursor.execute(sql) #executes the query
        strResult = str(cursor.fetchall()).strip('[]') #query returns a list of tuples. Strip extracts our results and str() turn it into a string
        return strResult #returns our result
    except:
        notify("Critical error while connecting to MySQL\nto get job descriptions.")
        
def topTerms(searchText, minHits=1000, wordType="J"): #module that counts words in provided searchText, prompts users to select words to keep, and returns list of selected words. 
    #parts of code cookbooked from: https://stackoverflow.com/questions/65773214/is-it-possible-to-insert-a-checkbox-in-a-pysimplegui-table
    #minHits allows you to specify how many times a word has to be repeated in the data to be returned.
    #wordType allows you to specify what type of word you want. N=noun,V=verb,J=descriptor.

    def count(text): #nested function that actually counts words
        #N=noun,V=verb,J=descriptor
        stopwords = ['a', 'about', 'above', 'across', 'after', 'afterwards', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'amoungst', 'amount', 'an', 'and', 'another', 'any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere', 'are', 'around', 'as', 'at', 'back', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'below', 'beside', 'besides', 'between', 'beyond', 'bill', 'both', 'bottom', 'but', 'by', 'call', 'can', 'cannot', 'cant', 'co', 'computer', 'con', 'could', 'couldnt', 'cry', 'de', 'describe', 'detail', 'did', 'do', 'done', 'down', 'due', 'during', 'each', 'eg', 'eight', 'either', 'eleven', 'else', 'elsewhere', 'empty', 'enough', 'etc', 'even', 'ever', 'every', 'everyone', 'everything', 'everywhere', 'except', 'few', 'fifteen', 'fifty', 'fill', 'find', 'fire', 'first', 'five', 'for', 'former', 'formerly', 'forty', 'found', 'four', 'from', 'front', 'full', 'further', 'get', 'give', 'go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'however', 'hundred', 'i', 'ie', 'if', 'in', 'inc', 'indeed', 'interest', 'into', 'is', 'it', 'its', 'itself', 'keep', 'last', 'latter', 'latterly', 'least', 'less', 'ltd', 'made', 'many', 'may', 'me', 'meanwhile', 'might', 'mill', 'mine', 'more', 'moreover', 'most', 'mostly', 'move', 'much', 'must', 'my', 'myself', 'name', 'namely', 'neither', 'never', 'nevertheless', 'next', 'nine', 'no', 'nobody', 'none', 'noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'part', 'per', 'perhaps', 'please', 'put', 'rather', 're', 's', 'same', 'see', 'seem', 'seemed', 'seeming', 'seems', 'serious', 'several', 'she', 'should', 'show', 'side', 'since', 'sincere', 'six', 'sixty', 'so', 'some', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhere', 'still', 'such', 'system', 'take', 'ten', 'than', 'that', 'the', 'their', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein', 'thereupon', 'these', 'they', 'thick', 'thin', 'third', 'this', 'those', 'though', 'three', 'three', 'through', 'throughout', 'thru', 'thus', 'to', 'together', 'too', 'top', 'toward', 'towards', 'twelve', 'twenty', 'two', 'un', 'under', 'until', 'up', 'upon', 'us', 'very', 'via', 'was', 'we', 'well', 'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'with', 'within', 'without', 'would', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves']
        stopwords.extend(['the', 'it']) #adds more stopwords (words to remove from text)
        
        if wordType != None: 
            print("Selecting desired types of words") #keep in mind that print commands will only appear in visual code consoles, not when run as a .pyw or .exe file. This is mostly for our sake and debugging
            wordList = [word.lower() for (word, pos) in nltk.pos_tag(nltk.word_tokenize(text)) if pos[0] == 'J']  #selects specified type of word using nltk language processing, then removes case
        else:
            print("Removing punctuation from job descriptions")
            text = re.sub('[^\w\s]','',text) #removes punctuation with regex
            print("Removing case from job descriptions")
            text = text.lower() #turn string to lowercase
            print("Splitting text into a list of words")
            wordList = text.split() #splits string into list of words

        print("Removing stopwords")
        wordList = [w for w in wordList if (w not in stopwords)] #removes stopwords, defined above
        print("Counting",len(wordList),"words")
        counts = Counter()
        counts.update(wordList) #counts words. Much much faster than the fastest manual code for this
        wordList = [[key, val] for key, val in counts.items() if not (isinstance(val, int) and (val < minHits))] #turns data into set of sets, limits results to specified amount of hits
        print("Sorting results")
        wordList = sorted(wordList,key=lambda x: x[1]) #sorts list by frequency. Faster alternatives exist, but this is simpler
        wordList.reverse() #sets list to desc order

        return wordList

    def icon(check): #nested function to make and update check marks 
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

    check = [icon(0), icon(1), icon(2)] #adds alias to icon()

    headings = ['Search Term', 'Hits'] #defines table (technically tree) headers
    data = count(searchText) #calls nested function to count words

    treeData = sg.TreeData() #adds alias for sg.TreeData
    treeMeta = [] #initialise treeMeta list 

    for term, hits in data:
        treeData.Insert('', term, term, values=[hits], icon=check[1]) #gets data from counter and inserts data to table
        treeMeta.append(term) #fills initial metadata list

    sg.SetOptions(element_padding=(15, 8))
    sg.set_options(font=('Helvetica', 12))
    #this table is actually a PySimpleGUI "tree." Normal tables are not interactive like this.
    layout = [
        [sg.Text('Deselect undesired search terms', key='msg',justification='center')],
        [sg.Tree(data=treeData, headings=headings[1:], auto_size_columns=True,
            num_rows=10, col0_width=20, key='-TREE-', row_height=48, metadata=treeMeta,
            show_expanded=False, enable_events=True,justification='center',
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,text_color='white',selected_row_colors=('black','grey'),header_text_color='black', header_background_color='#808080')],
        [sg.Button("Cancel"),sg.Button('Submit')]
    ]

    window = sg.Window('Search Results', layout, element_justification='c', finalize=True, size=(350,615))
    tree = window['-TREE-'] #this assignment makes things easier in while loop
    tree.Widget.heading("#0", text=headings[0]) # Set heading for column #0

    while True:
        event, values = window.read()
        if event == "Cancel" or event == sg.WIN_CLOSED:
            window.close()
            return "CLOSED"
        elif event == '-TREE-': #event that allows us to select and deselect tree elements
            term = values['-TREE-'][0]
            if term in tree.metadata:
                tree.metadata.remove(term)
                tree.update(key=term, icon=check[0])
            else:
                tree.metadata.append(term)
                tree.update(key=term, icon=check[1])
        elif event == "Submit":
            window.close()
            return tree.metadata #returns list of selected data

def searchModule(): #asks for options. interfaces with topTerms() and main menu 
    sg.SetOptions(element_padding=(5, 10))
    #combos are list boxes. We have them set to readonly (users cannot type custom content) and to use default value to describe the field to the user. Radios are more complicated, but I use one anyway for word type for visual appeal:
    layout = [
                [sg.Text("Please select search module options. Note that degree requirements and job permanence may require you to preprocess data, or you may be excluding date you wish to select.", key='msg',justification='center',size=(48,None))],
                [sg.Radio('All', "WORDTYPE", default=True,key="All",enable_events=True),sg.Radio('Verbs', "WORDTYPE",key="Verbs",enable_events=True),sg.Radio('Nouns', "WORDTYPE",key="Nouns",enable_events=True),sg.Radio('Adjectives', "WORDTYPE",key="Adjectives",enable_events=True)],
                [sg.Combo(values=["Academic","Government and National Lab","Non-Profit","Private","Other"],default_value="Sector Filter", size=(25,30), key='sector',readonly=True,pad=(5, 10)),
                sg.Combo(values=["Permanent","Temporary"],default_value="Permanence Filter", size=(25,30), key='perm',readonly=True,pad=(5, 10))],
                [sg.Combo(values=["4 Year Degree","Masters","Doctorate"],default_value="Degree Requirement Filter", size=(25,30), key='degree',readonly=True,pad=(5, 10)),
                sg.Combo(values=["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", "District of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"],default_value="State Filter", size=(25,30), key='state',readonly=True,pad=(5, 10))],
                [sg.Combo(values=["Summer Research/Internship", "Entry Level", "Experienced"],default_value="Job Level Filter", size=(25,30), key='level',readonly=True,pad=(5, 10))],

                #this enables inputting date conditions. Disabled due to issues with formatting of inputted data. You'll need to enable some code in the while loop below and in getDesc() too!
                #[sg.Input(key='startDate', default_text="", size=(20,1), readonly=True, disabled_readonly_background_color="#111111", disabled_readonly_text_color="white"), sg.Input(key='endDate', default_text="", size=(20,1), readonly=True, disabled_readonly_background_color="#111111", disabled_readonly_text_color="white")],
                #[sg.CalendarButton("Set Start Date", close_when_date_chosen=True,  target='startDate', no_titlebar=False, format='%Y-%m-%d 00:00:00'), sg.CalendarButton("Set End Date", close_when_date_chosen=True,  target='endDate', no_titlebar=False, format='%Y-%m-%d 23:59:59')],
                
                [sg.Text("Minimum Hits:",justification='center'),sg.Input("500", key='hits',justification='center',size=(10,1))],
                [sg.Button("OK",pad=(15, 10)),sg.Button("Cancel",pad=(15, 10))]
            ]

    #create the window
    window = sg.Window("Select Options", layout, element_justification='c', finalize=True, resizable=False, icon='logo.ico')
    window['hits'].Widget.config(insertbackground='#b2aca2') #fixes the cursor color!

    type = None #initializes backend word type as None

    #create the event loop
    while True: #end program if user closes window or presses the Cancel button
        event, values = window.read()
        if event == "Cancel" or event == sg.WIN_CLOSED:
            window.close()
            return "CLOSED"
        ################################################
        ## Radio Element Event Handling (defines "Type" when button is clicked, requires enable_events=True)
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
            #grab values from combos
            sector = values["sector"]
            perm = values["perm"]
            level = values["level"]
            degree = values["degree"]
            state = values["state"]
            #startDate = values["startDate"]
            #endDate = values["endDate"]
            
            try: #grabs and checks that min hits is an int, returns error if false
                hits = int(values['hits'])
            except:
                notify("Error: Minimum hits must be an integer!") 
                window.close()
                break
            window.close()
            return topTerms(searchText=getDesc(sector,perm,level,degree,state),minHits=hits,wordType=type) #this calls our counter and our function to get desc, with conditions passed from this function. Add ,startDate, endDate to getDesc() call to send dates conditions down on
               
################################################
## Query Module:
################################################
def query(searchTerms, search="fDescription", condition=""): #counts occurrences of terms in specified list of terms (searchTerms) with specified sql condition, in specified search field ("search") using SQLite.
    try:
        conn = sqlite3.connect('APSdata.db') #connects to database. Creates database if it does not exist
        results = {} #initializes results dictionary 

        for term in searchTerms: #iterates through the list of search terms
            cursor = conn.cursor() #defines the cursor used to execute commands

            orgTerm = term #stores term before processing operation syntax
            term = term.replace("|","%' OR {} LIKE '%".format(search)) #turn application OR syntax to SQLite syntax
            term = term.replace("+","%' AND {} LIKE '%".format(search)) #turn application AND syntax to SQLite syntax
            term = "'%{}%'".format(term) #adds general syntax for all terms

            sql = "SELECT count(*) FROM Jobs WHERE ({} LIKE {}){} COLLATE NOCASE".format(search,term,condition) #the query sent to SQL, where {} are placeholders, filled with .format(). "COLATE NOCASE" makes the query case insensitive
            cursor.execute(sql) #executes the query
            #print(sql) #this line is super duper helpful for debugging SQL errors

            term = orgTerm #reverts our term back to the original syntax for exporting results
            listResult = cursor.fetchall() #gets results from sql in a list of tuple (but there is only one element)
            tupleResult = listResult[0] #gets tuple from list
            results[term] = tupleResult[0] #gets string from tuple and adds results to dictionary

        return results #returns results

    except:
        notify("Critical error while connecting to SQL.")

def searchAll(keyList, search='fDescription'): #opens window to ask what which conditions to search with, then queries with query()
    #to add more search groups, define the search group at the bottom in the format exhibited and add a checkbox button + a call to grab results with the others
    sg.SetOptions(element_padding=(5, 10))
    layout = [
                [sg.Text("Please select your search parameters. Note that degree requirements and job permanence may require you to preprocess data, or you may be excluding date you wish to select.", key='msg',justification='center',size=(48,None))],
                [sg.Text("Select search field:",pad=(0,15)),sg.Radio('Description', "query", default=True,key="desc",enable_events=True),sg.Radio('Job Title', "query",key="title",enable_events=True,pad=(0,15)),sg.Radio('Requirements', "query",key="req",enable_events=True)],                
                [sg.Checkbox('Sector', default=True, key="sector"),sg.Checkbox('Permanence', default=False, key="perm"),sg.Checkbox('Degree Requirements', default=False, key="degree"),sg.Checkbox('Job Level', default=False, key="level")],
                [sg.Button("OK",pad=(15, 10)),sg.Button("Cancel",pad=(15, 10))]
            ]

    # Create the window
    window = sg.Window("Select Options", layout, element_justification='c', resizable=False, icon='logo.ico')

    # Create an event loop
    while True: #end program if user closes window or presses the Cancel button
        event, values = window.read()
        if event == "Cancel" or event == sg.WIN_CLOSED:
            window.close()
            return "CLOSED"
        ################################################
        elif event == 'OK':
            #grabs values from checkboxes
            sector = values["sector"]
            perm = values["perm"]
            level = values["level"]
            degree = values["degree"]
            window.close()
            break
                    
        ################################################
        ## Radio Element Event Handling (defines "queryType" when button is clicked)
        ################################################
        elif event == "desc":
            search = "fDescription"
        elif event == "title":
            search = "Title"
        elif event == "req":
            search = "Requirements"
        ################################################

    allJobs = query(keyList,search) #our permanent query, of all jobs
    data = {'All Jobs': allJobs} #adds results to results dictionary

    ################################################
    ## Grouping Results:
    ################################################
    if sector:
        #these are the calls to our query function for this grouping, and will be columns in our results:
        academicJobs = query(keyList,search, condition=" AND ((Sector LIKE '%academic%') OR (Sector LIKE '%acedemic%'))")
        govJobs = query(keyList,search, condition=" AND Sector LIKE '%government and national lab%'")
        nonprofitJobs = query(keyList,search, condition=" AND Sector LIKE '%non-profit%'")
        privateJobs = query(keyList,search, condition=" AND ((Sector LIKE '%private%') OR (Sector LIKE '%industry%'))")
        otherJobs = query(keyList,search, condition=" AND Sector LIKE '%other%'")

        #make a temp sector result dictionary and add to all results:
        tempDict = {'Academic': academicJobs, 'Government/National Lab': govJobs, 'Non-Profit': nonprofitJobs, 'Private': privateJobs, 'Other': otherJobs}
        data.update(tempDict) #merges the temp result dictionary results with results dictionary
    if perm:
        #these are the calls to our query function, and will be columns in our results:
        tempJobs = query(keyList,search, condition=" AND Temporary = 1")
        permJobs = query(keyList,search, condition=" AND Temporary = 0")

        #make a temp sector result dictionary and add to all results:
        tempDict = {'Temporary': tempJobs,'Permanent': permJobs}
        data.update(tempDict) #merges the temp result dictionary results with results dictionary
    if level:
        #these are the calls to our query function, and will be columns in our results:
        summerJobs = query(keyList,search, condition=" AND JobLevel LIKE '%Summer Research/Internship%'")
        entryJobs = query(keyList,search, condition=" AND JobLevel LIKE '%Entry Level%'")
        expJobs = query(keyList,search, condition=" AND JobLevel LIKE '%Experienced%'")

        #make a temp sector result dictionary and add to all results:
        tempDict = {'Summer Research/Internship': summerJobs,'Entry Level': entryJobs,'Experienced Level': expJobs}
        data.update(tempDict) #merges the temp result dictionary results with results dictionary
    if degree:
        #these are the calls to our query function, and will be columns in our results:
        nullDegreeJobs = query(keyList,search, condition=" AND EducationLevel IS NULL")
        BAJobs = query(keyList,search, condition=" AND EducationLevel LIKE '%4 Year Degree%'")
        MAJobs = query(keyList,search, condition=" AND EducationLevel LIKE '%Masters%'")
        docJobs = query(keyList,search, condition=" AND EducationLevel LIKE '%Doctorate%'")

        #make a temp sector result dictionary and add to all results:
        tempDict = {'Degree Requirement Unspecified': nullDegreeJobs,'4 Year Degree Required': BAJobs,'Masters Required': MAJobs,'Doctorate Required': docJobs}
        data.update(tempDict) #merges the temp result dictionary results with results dictionary

    tabledData = pd.DataFrame.from_dict(data) #organizes data into a table (but it's really a DataFrame) using pandas. This is easily exportable into GUIs and .csv
    return [tabledData,search] #returns results in a list

################################################
## First Run Code:
################################################
if not(path.exists('APSdata.db')): #APSdata will not exist before we run the code the first time
    notify("This appears to be the first time this program has run on this computer\nDownloading dependencies.",title="Downloading Dependencies")
    nltk.download('wordnet') #this code downloads wordnet libraries we need to classify word types
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    print("Done!")

################################################

menuModule() #this function call runs our program. It needs to be at the end, after all our code is defined.