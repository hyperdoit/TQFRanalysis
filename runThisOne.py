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


def getMyPhysElecOptions(term):
    # Get all physics electives I haven't already taken in fall 2017
    #templateTQFR(year, term, division, className, professors, departments, numRange, termChar, pracOrAnal)
    #  Ph, Ay, APh 100+
    sT = TQFRpage.templateTQFR('ANY', term, 'ANY', 'ANY', 'ANY', ['Ph', 'Ay', 'APh', 'GENERAL'], [100, 1000],  'ANY', '')
    analyzer.loadFromTemplate(sT)
    #  Ph and Ay 20-22 (Ay  22 not actually an option, may not exist; can only take up to 10 units of Ay 20-21)
    sT = TQFRpage.templateTQFR('ANY', term, 'PMA', 'ANY', 'ANY', ['Ph', 'Ay', 'GENERAL'], [20, 22],  'ANY', '')
    analyzer.loadFromTemplate(sT)
    #  Ma 5
    #templateTQFR(year, term, division, className, professors, departments, numRange, termChar, pracOrAnal):
    sT = TQFRpage.templateTQFR('ANY', term, 'PMA', 'ANY', 'ANY', ['Ma', 'GENERAL'], [5, 5],  'ANY', '')
    analyzer.loadFromTemplate(sT)
    # Ma 108
    sT = TQFRpage.templateTQFR('ANY', term, 'PMA', 'ANY', 'ANY', ['Ma', 'GENERAL'], [108, 108],  'ANY', '')
    analyzer.loadFromTemplate(sT)
    # ACM 101
    sT = TQFRpage.templateTQFR('ANY', term, 'EAS', 'ANY', 'ANY', ['ACM', 'GENERAL'], [101, 101],  'ANY', '')
    analyzer.loadFromTemplate(sT)    
    
    # This below doesn't check if a class in another department is primary cross-lister.
    """
    #  Ph and Ay 100+
    sT = TQFRpage.templateTQFR('ANY', 'ANY', 'PMA', 'ANY', 'ANY', ['Ph', 'Ay', 'GENERAL'], [100, 1000],  'ANY', '')
    analyzer.loadFromTemplate(sT)
    # APh 100+
    sT = TQFRpage.templateTQFR('ANY', 'ANY', 'EAS', 'ANY', 'ANY', ['APh', 'GENERAL'], [100, 1000],  'ANY', '')
    analyzer.loadFromTemplate(sT)
    #  Ph and Ay 20-22 (Ay  22 not actually an option, may not exist; can only take up to 10 units of Ay 20-21)
    sT = TQFRpage.templateTQFR('ANY', 'ANY', 'PMA', 'ANY', 'ANY', ['Ph', 'Ay', 'GENERAL'], [20, 22],  'ANY', '')
    analyzer.loadFromTemplate(sT)
    #  Ma 5
    #templateTQFR(year, term, division, className, professors, departments, numRange, termChar, pracOrAnal):
    sT = TQFRpage.templateTQFR('ANY', 'ANY', 'PMA', 'ANY', 'ANY', ['Ma', 'GENERAL'], [5, 5],  'ANY', '')
    analyzer.loadFromTemplate(sT)
    # Ma 108
    sT = TQFRpage.templateTQFR('ANY', 'ANY', 'PMA', 'ANY', 'ANY', ['Ma', 'GENERAL'], [108, 108],  'ANY', '')
    analyzer.loadFromTemplate(sT)
    # ACM 101
    sT = TQFRpage.templateTQFR('ANY', 'ANY', 'EAS', 'ANY', 'ANY', ['ACM', 'GENERAL'], [101, 101],  'ANY', '')
    analyzer.loadFromTemplate(sT)
    """

def getCSelecOptions():
    #  CS 114+
    sT = TQFRpage.templateTQFR('ANY', 'ANY', 'ANY', 'ANY', 'ANY', ['CS', 'GENERAL'], [114, 1000],  'ANY', '')
    analyzer.loadFromTemplate(sT)    
    
    
def getCStermElecOptions(term):
    #templateTQFR(year, term, division, className, professors, departments, numRange, termChar, pracOrAnal)
    #  CS 114+, in 
    sT = TQFRpage.templateTQFR('ANY', term, 'ANY', 'ANY', 'ANY', ['CS', 'GENERAL'], [114, 1000],  'ANY', '')
    analyzer.loadFromTemplate(sT)    
    
#getMyPhysElecOptions('SP')
#getCSelecOptions()

#analyzer.compileAllClassAggs()

# DEBUGGING CODE.


# You know, it would probably be worth it if I could just get a list of classes currently being offered for analyzer to cross-reference.

# Not ready to be slotted into analyzer yet.

# The way they write this makes me want to bang my head against a table.
# High on my list being the SOCIAL SCIENCE row, which does NOT have a [Go to top] on the same row as it...


# Okay, actually thinking through this now.
tbls=[]
# Will likely want the below back in the future.
soupy = analyzer.loadRegistrar()
tbls = soupy.find_all('table')


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

classesOffered = []
for table in classTables:
    #print table[0][0]
    className = table[0][0].replace(u'\xa0', ' ').replace('  ', ' ')
    className = className.replace(' 0', ' ').replace(' 0', ' ')
    firstDigit = -1
    lastDigit = len(className)-1
    for i in range(0, len(className)):
        if className[i] in "0123456789" and firstDigit == -1:
            firstDigit = i
        if className[i] in "0123456789" and i > 0 and  not className[i-1] in "0123456789":
            lastDigit = i
    # Might want lastDigit someday if there's a spacing mistake with termChars
    if firstDigit > 0 and not className[firstDigit-1] == ' ':
        className = className[:firstDigit] + ' ' + className[firstDigit:]
    print className
    classesOffered.append(className)

"""
lists: ====
    loadedNames: a list of all the filenames in scrapedPagesPath when last loaded. 
    loaded: a list containing a TQFRpage instance for every file in scrapedPages, once it has been loaded into- NOT automatically initialized!
    classAggs: a list of ClassAggregates. Once constructed, one for each class in the loaded.
    classAggsClassNames : a list of the human-readable names of the classes in the classAggs list."""


def isClassNameOffered(className):
    #print className
    if className in classesOffered:
        return True
    else:
        return False

def isClaggOffered(clagg):
    #print 
    if clagg.aggPage.className in classesOffered:
        return True
    else:
        return False


# These important lines!
def removeNonOfferedClaggs():
    # Not offered in whatever term you loaded the catalog for.
    analyzer.classAggs = filter(isClaggOffered, analyzer.classAggs)
    analyzer.classAggsClassNames = filter(isClassNameOffered, analyzer.classAggsClassNames)
    


