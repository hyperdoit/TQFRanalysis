import requests, os
from bs4 import BeautifulSoup
from TQFRpage import *
from TQFRscraper import *
from TQFRanalyzer import *

print '''This is the main program. '''
'''NOTE TO PROGRAMMER: SQL database (SQL Alchemy is good) would be a good way to store data in a way better than using windows filenames. (path limit)...'''
'''I'm still not sure TQFRpage and TQFRdata should be separate. And it's possible I should also have a "Class" class.'''

# Set the path to the output =============================
print ""

# CHANGE THIS AT END! =========================================================================
'''
tqfrData = raw_input("""Enter path to desired main data location. 
Enter '.' to use the location this program is being run from (suggested, if you copied the full thing):""")
tqfrData = os.path.abspath(tqfrData)
'''

# QUICKUSE: decomment this, set as desired.

tqfrData = os.path.abspath(".")
print "using: " + tqfrData


tqfrDataFolder = os.path.join(tqfrData, "TQFRdata")

if not os.path.exists(tqfrDataFolder):
    print "making folder TQFRdata"
    os.makedirs(tqfrDataFolder)
else:
    print "found existing TQFRdata folder"
    
scrapedPagesPath = os.path.join(tqfrDataFolder, "scrapedPages") 
ensureFolder(scrapedPagesPath)
    





# Main loop =======================================

scraper = TQFRscraper(tqfrDataFolder)
analyzer = TQFRanalyzer(tqfrData)

# REMOVE before submission! ================

# uncommment below line for automatic prompt for login
# scraper.login()

"""
tqfrMatch = blankTQFR()
tqfrMatch.setMatchAny()
tqfrMatch.year = "2015-16"
tqfrMatch.term = "FA"
tqfrMatch.departments = ["GENERAL", "BE"]
tqfrs = scraper.scrapeFromURLtree([tqfrMatch])
"""
# End stuff that needs to be removed.


""" What does debug do? If debug is on, the program may crash with an informative error message. 
 If it is off, it will return you to your most recent menu instead of crashing, and may not supply an informative error message.
 Probably the best reason to have Debug off is if you are going to be analyzing a wide variety of classes. 
 It takes time to load them all into the program, and you a single formatting difference on one class's TQFR 
 could in theory crash the program and force you to reload everything. """
debugOn = True
setDebug = True # TURN DEBUG ON/OFF HERE
if setDebug:
    debugOn = True
    scraper.debugOn = True
    analyzer.debugOn = True
else:
    debugOn = False
    scraper.debugOn = False
    analyzer.debugOn = False
    


# NOte to self: must be 79 characters to not wrap weirdly on SFL computers.
commandInstructs = """login
    Login to Caltech access to enable scraping. Do this once after starting the 
    program if you intend to scrape new data.
scrape
    Interactively scrape class information from TQFRs for analysis. Does not 
    load the scraped pages base info into the system-there's an option for that
    under analyze.
analyze
    Load and analyze scraped data.
instructions | help | info | information
    Repeat these instructions.
commands 
    Prints JUST the names and arguments of the valid commands.
done
    End the program."""

# Add this if I ever get it to work:
"""registrar
    Downloads 'course schedules' registrar page in the correct format. You will
    be prompted to provide the URL for your year and term. Also analyzes it and
    loads the scheduling data into the analyzer."""

commandNames = """login
scrape
analyze
instructions | help | info | information
commands
done"""


def mainInstructs():
    print commandInstructs

def mainLoop():
    """Scrapes and analyses data interactively."""
    choice = ''
    message = ''
    mainInstructs()
    allPages = []
    # The loop
    while not (choice == 'done'):
        print message
        message = ""
        choice = raw_input("[Main] Command: ") 
        args = choice.split(' ')        
        if debugOn:
            allPages += mainLoopChoices(choice)
        else:
            try: 
                allPages += mainLoopChoices(choice)
            except:
                message = "Unexpected Error! Sorry for the bad message, but I thought you'd prefer this to having to log back in again."
        if choice == "done":
            return 0        

def mainLoopChoices(choice):
    # View choices
    allPages = []
    helpWords = ["help", "info", "instructions", "information"]
    if choice.lower() in helpWords:
        mainInstructs()
    elif choice == "commands":
        print commandNames
    elif choice == "login":
        scraper.login()
    elif choice == "scrape":
        allPages += scraper.scrapeDataLoop()
    elif choice == "registrar":
        scraper.getCourseSchedulesPage()
        # analyzer should automatically load it!
    elif choice == "analyze":
        analyzer.analyzerLoop()
    elif not choice == "done" :
        print "Unrecognized command!"
    return allPages
  
    
    
# Fire it up

# Need to turn this back on at some point!
mainLoop()





# DEBUGGING CODE.


# Not ready to be slotted into analyzer yet.

# The way they write this makes me want to bang my head against a table.
# High on my list being the SOCIAL SCIENCE row, which does NOT have a [Go to top] on the same row as it...


# Okay, actually thinking through this now.
tbls=[]
# Will likely want the below back in the future.
#soupy = analyzer.loadRegistrar()
#tbls = soupy.find_all('table')


ptables = []
for table in tbls:
    ptables.append(tableExtract(table))
ptbls = ptables # just for me...

''' The goal is to break on the "goto top" links they include for departments,
 and on the top rows of courses. The latter are identified by their length of 3 real elements, 
 the first one satisfying regExp ".* \d{3}.*", the second one either + or #-#-#
'''
def isDepartmentRow(row):
    for col in row:
        if u"Go\xa0to\xa0top" in col:
            return True
    return False

def isCourseStartRow(row):
    # and re.search(".* \d{3}.*", row[0]) # Didn't work well with unicode.
    if len(row) == 3 and (row[1] == "+" or len(row[1].split("-")) == 3):
        return True
    return False

# The problem is that extra times, and sometimes even just the full location, are on different rows.
def isSectionRow(row):
    if len(row) > 3 and re.search("\w*, \w", row[1]):
        return True



#currentDepartment = ""   
# I don't actually need to keep track of departments. CLassName will do that.
mergedTables = [] # not sure if I need this but using it for now.
classTables = [[]]

# This is a start, though an imperfect one.
for table in ptables:
    for row in table:
        mergedTables.append(row)
        #if isDepartmentRow(row):
        #    currentDepartment = row[0]
        if isCourseStartRow(row):
            classTables.append([row])
        elif not "______________" in row[0] and not row[0] == "." and not isDepartmentRow(row) and not u"Course\xa0Offering" in row[0] and not u"Section" in row[0]:
            classTables[-1].append(row)
        
# Will want this back if I ever get back into it.
"""
for table in classTables:
    print ""
    prettyPrintTable(table)
"""