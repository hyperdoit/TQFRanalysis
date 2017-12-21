"""
Rita Sonka, 09/15/2016
This file contains the class TQFRpage, used to store identifying data about
a PAGE of TQFR data, and to work with the scraping program.
It also contains the function blanckTQFR() which returns a TQFRpage instance
with junk data (not a template).
It also contains a number of utility functions.

Finally, it contains the class TQFRdata, used to store data extracted from 
scraped pages.
"""
# used to import copy before realizing sadly that it did not deepcopy nested lists.
import re, os, numpy, textwrap, sys
from bs4 import BeautifulSoup


# Utility functions ============================================
def ensureFolder(pathString):
    # returns true and constructs the folder if the folder doesn't exist
    # returns false if it does
    if not os.path.exists(pathString):
        os.makedirs(pathString)
        return True
    return False

def dMessage(msg):
    print "[DEBUG] " + msg
    
def iMessage(msg):
    print "[INFO] " + msg

def blankTQFR():
    return TQFRpage("20XX-XY", "XX", "DIV", "DEP 000", ["FIRSTNAME LASTNAME"], "URL")


# I should make a version of this using optional arguments and set anything not mentioned to ANY.
# setAllDirect(self, template, year, term, division, className, classNameForFileName, professors, url, departments, classNum, termChar, pracOrAnal, mD)
def templateTQFR(year, term, division, className, professors, departments, numRange, termChar, pracOrAnal): # add pracOrAnal?
    # Input 'ANY' for anything to accept any.
    toReturn = blankTQFR()
    toReturn.setMatchAny() # Not sure this is strictly necessary, but it couldn't hurt.
    toReturn.setAllDirect(True, year, term, division, className, "ANY", professors, "ANY", departments, numRange, termChar, pracOrAnal, toReturn.mD)
    return toReturn

def tqfrFromFilenameAndPath(filename, path):
    tqfr = blankTQFR()
    tqfr.initFromFilenameAndPath(filename, path)
    return tqfr

def tqfrFromFilename(filename):
    tqfr = blankTQFR()
    tqfr.initFromFilename(filename)
    return tqfr

# Utillity printing functions.
def uPrint(string):
    # Expects a utf8 encoded string. Can fail with some characters, but doesn't crash the program when it does so.
    print str(string).encode('utf8', errors='replace') # I should fix this better at some point.

def wrapToNum(text, num):
    # Warning: Ignores newlines!
    return textwrap.fill(' '.join(text.split()), num)   

def wrapTo80(text):
    # Warning: Ignores newlines!
    return textwrap.fill(' '.join(text.split()), 80)    

# For use with the below makePrettyTable string, for if I want to do this after having decided on a pretty print::
def convertTableToTabDelimited(tableString):
    class1 = re.sub("[ ]+\|", "\t", tableString) 
    class2 = class1.replace("\n|", "\n")
    class3 = class2[1:].replace("|", "\t")    
    return class3

def printTabDelimitedTable(table):
    print convertTableToTabDelimited(makePrettyTableString(table))



def makePrettyTableString(table):
    # assumes a rectangular table in the form of a list of rows that are themselves lists of columns
    # e.g. [[row1col1, row1col2], [row2col1, row2col2]]
    # also assumes no \n or \r in elements. I SHOULD FIX THIS, 
    # IT LOOKS TERRIBLE ON MONITOR BECAUSE it has extra whitespace. 
    # I think because it's counting the full string for length and setting columns
    # accordingly.
    if len(table) < 1:
        print "Bad table: " + str(table)
        return -1
    """elif len(table[0]) < 1:
        print "Bad table: " + str(table)
        return -1"""
    # Figuring out how to space the table. =======
    # Find number of columns in longest row.
    colSizes = [] # How many characters in each column?
    rowHeights = [] # How many lines in each row of the table? 
    numCols = len(table[0])
    for row in table:
        if numCols < len(row):
            numCols = len(row)
        rowHeights.append(0)
    for col in range(numCols):
        colSizes.append(0)
    # Find maximum size of each column. Now supporting newlines.
    maxCellSize = 100 # This should probably be a global setting. It's really only necessary for comments right now.
    #, up to maxCellSize (which possibly should be a setting?) Have decided to trust input for now.
    for rowNum in range(len(table)):
        row = table[rowNum]
        for colNum in range(len(row)):
            #text = str(row[colNum]) # Why was this commented out?
            text = wrapToNum(str(row[colNum]), maxCellSize)
            lines = text.splitlines() # splitlines recognizes \r\n
            row[colNum] = lines[:] # Note that I save this back! It saves a lot of splitlining.
            if len(lines) > rowHeights[rowNum]:
                rowHeights[rowNum] = len(lines)
            for line in lines:
                if len(line) > colSizes[colNum]:
                    colSizes[colNum] = len(str(row[colNum]))     
            
            #if isinstance(row[colNum], basestring):
            #    if len(row[colNum]) > colSizes[colNum]:
            #        colSizes[colNum] = len(row[colNum])
            #elif len(str(row[colNum])) > colSizes[colNum]:
            #    colSizes[colNum] = len(str(row[colNum]))
            
            
            #if colSizes[colNum] > maxCellSize:
            #    colSizes[colNum] = maxCellSize
    # Make the table!
    tblString = ""
    for rowNum in range(len(table)):
        row = table[rowNum]
        #rowString = "|"
        if rowHeights[rowNum] > 1 or (rowNum > 0 and rowHeights[rowNum-1] > 1):
            # It's possible that I should leave this to the input, and not force it in.  Also possible that 
            tblString += "|" + (sum(colSizes) + len(colSizes)-1)*"-" + "|\n" # Note len(colSizes) and sum(colSizes) can't be zero if rowHeights[rowNum]>1.
        for lineNum in range(rowHeights[rowNum]):
            lineString = "|"   
            for colNum in range(len(row)):
                lines = row[colNum]# Remember the splitlined result was saved
                if len(lines) > lineNum: 
                    item = lines[lineNum]
                else:
                    item = ""
                lineString += item
                lineString += ' ' * (colSizes[colNum] - len(item))
                lineString += '|'
                
                """
                if isinstance(row[colNum], basestring):
                    if len(table[0]) > 0 and not re.match('-----BELOW.*', table[0][0]): # A WAY OF IDENTIFYING COMMENTS  # .encode('ascii','replace')
                        item = row[colNum].replace('\n', '\\n').replace('\r', '\\r')
                    else:
                        item = row[colNum]
                else:
                    item = str(row[colNum])#.replace('\n', '\\n').replace('\r', '\\r')
                rowString += item
                rowString += ' ' * (colSizes[colNum] - len(item))
                rowString += '|'
                """
            tblString += lineString + "\n"
    return tblString    
    
def prettyPrintTable(table):
    # assumes a rectangular table in the form of a list of rows that are themselves lists of columns
    # e.g. [[row1col1, row1col2], [row2col1, row2col2]]
    # also assumes no \n in elements
    uPrint(makePrettyTableString(table))



    

class TQFRpage:
    """EITHER: A reference to a TQFR page, containing identifying information,
    OR: a "template" TQFR page that can be used to generally match specific ones.
    
    Variables:
    strings: ==========
    year, term, division, className, termChar (ONLY meant to store A/B/C or similar right now), classNameForFileName, url, pracOrAnal
    pracOrAnal is "prac" if practical, "anal" if analytical, "" if neither.
    integer: ==========
    classNum (normally! in templates it is a list of two numbers to match between, INCLUSIVE)
    lists: ==========
    departments (e.g. ["PH", "BE"] )
    professor (there can be more than one).
    Boolean: ==========
    template (notes if this is a matching template or not.)
    classes: ==========
    mD (myData, a TQFRdata instance)
    
    Static variable:
    iS
    Item Separation, for constructing toString() and toFilename().
    Must be filename-friendly! (I may changed it a few times before settling on '__')
    """
    
    iS = "__"
    
    def __init__(self, year, term, division, className, professors, url):
        self.year = year
        self.term = term
        self.division = division
        self.setClassName(className) # sets departments, classNum, and termChar!!
        # also sets className and classNameForFileName, AND pracOrAnal
        self.professors = professors
        self.url = url
        self.template = False
        self.mD = TQFRdata("BLANK")
    
    def initFromFilenameAndPath(self, filename, path):
        # path should be a FULL PATH, to enable mD to open the file! Filename should JUST be the filename.
        preDeps = filename[:filename.index('--')]
        numAndTermChar = filename[filename.index('--')+2:filename.index('__')]
        m = re.search('(\d*)(.*)', numAndTermChar)
        stuff = filename.split('__')
        self.year = stuff[2]
        self.term = stuff[3]
        self.division = stuff[4]
        self.pracOrAnal = stuff[5]
        # class name stuff
        self.departments = preDeps.split('-')
        self.classNum = int(m.group(1))
        self.termChar = m.group(2)
        self.classNameForFileName = stuff[0]
        self.className = ''
        for dep in self.departments:
            self.className += '/' + dep
        self.className = self.className[1:] + ' ' + str(self.classNum) + self.termChar
        # back to normal!
        self.professors = stuff[1].split('_')
        self.url = "I'm not going to try and get this..."
        self.template = False
        self.mD = TQFRdata(path) 
        self.compileClassNameForFilename()    
    
    def initFromFilename(self, filename):
        # DOES NOT initialize self.mD. This is primarily used in analyzer's load method to check if it needs to read in mD.
        preDeps = filename[:filename.index('--')]
        numAndTermChar = filename[filename.index('--')+2:filename.index('__')]
        m = re.search('(\d*)(.*)', numAndTermChar)
        stuff = filename.split('__')
        self.year = stuff[2]
        self.term = stuff[3]
        self.division = stuff[4]
        self.pracOrAnal = stuff[5]
        # class name stuff
        self.departments = preDeps.split('-')
        self.classNum = int(m.group(1))
        self.termChar = m.group(2)
        self.classNameForFileName = stuff[0]
        self.className = ''
        for dep in self.departments:
            self.className += '/' + dep
        self.className = self.className[1:] + ' ' + str(self.classNum) + self.termChar
        # back to normal!
        self.professors = stuff[1].split('_')
        self.url = "ANY" # Okay, not a template, but better this than anything else. I'm not going to try to get this.
        self.template = False
        self.compileClassNameForFilename()           
        
        
    def compileClassNameForFilename(self):
        # The version that can be written as a filename.
        self.classNameForFileName = ''
        for department in self.departments:
            self.classNameForFileName += department + '-'
        self.classNameForFileName += '-' + str(self.classNum) + self.termChar  
        
    def setClassName(self, className):
        # PROPERLY reads in the class name if not a template. If you call this function, it CANNOT be a template any more (because classNum is in wrong format).
        self.template = False
        nameArgs = className.split(' ')
        if not len(nameArgs) == 2: # Ch   062
            print "WARNING! ODD CLASS NAME: \"" + className + "\". Probably fine if program does not immediately crash."
        m = re.search('(\D*)(\d+)(.*)', className)
        m.group(0)  
        self.departments = (m.group(1).replace(' ', '')).split('/')
        self.classNum = int(m.group(2))
        specialChar = m.group(3)
        # Set class name
        self.className = ''
        for dep in self.departments:
            self.className += dep + "/"
        self.className = self.className[:-1]
        self.className += " " + str(self.classNum) + specialChar
        if " " in specialChar:
            self.termChar = specialChar[:specialChar.index(" ")]
        else:
            self.termChar = specialChar
        if "Prac" in specialChar:
            self.pracOrAnal = "prac"
        elif "Anal" in specialChar:
            self.pracOrAnal = "anal"
        else:
            self.pracOrAnal = ""
        self.compileClassNameForFilename() 
        
    def setMatchAny(self):
        self.template = True
        self.year = "ANY"
        self.term = "ANY"
        self.division = "ANY"
        self.className = "ANY"
        self.professors = ["ANY"]
        self.url = "ANY"
        self.departments = ["ANY"]
        self.termChar = "ANY"
        self.classNum = [0, 9001]
        self.compileClassNameForFilename() 
        self.pracOrAnal = "ANY"
        # self.mD = TQFRdata("BLANK")
        # self.mD.tasData.append(TAdata(ta)
    
    def setAllDirect(self, template, year, term, division, className, classNameForFileName, professors, url, departments, classNum, termChar, pracOrAnal, mD):
        # DOES NOT COPY ANYTHING! DIRECT REFERENCES SET!
        self.template = template
        self.year = year
        self.term = term
        self.division = division
        self.className = className
        self.classNameForFileName = classNameForFileName
        self.professors = professors
        self.url = url
        self.departments = departments
        self.classNum = classNum    
        self.termChar = termChar
        self.pracOrAnal = pracOrAnal
        self.mD = mD.copy()
    
    def interactiveTemplate(self):
        print "NOTE: For any of the following, input 'ANY' to match anything. DON'T INCLUDE THE QUOTES ('') FOR ANY OF THIS."
        self.year = raw_input("Year, e.g. '2015-16': ") 
        self.term = raw_input("Term, e.g. 'FA', 'WI', 'SP': ")
        self.division = raw_input("Division, e.g. BBE, CHCHE, EAS, GPS, HSS, Institute, PMA, Performing and Visual Arts, or Physical Education: ")
        self.professors = raw_input("Enter Professor(s), separated by '_' e.g. 'Firstname McLastname' or'Firstname McLastname_Othername Lastname': ").split('_')
        if not "ANY" in self.professors:
            gen = raw_input("If you want to match any class that SHARES a professor with one of the ones you input, enter Y. Otherwise, press Enter, and it will ONLY match those that are listed under all those professors (and not a single one more). E.g. 'Y' if you want to include co-taught classes.")
            if gen == "Y":
                self.professors.append("GENERAL")        
        lowNum = raw_input("The lowest classnumber you want to match: ")
        if lowNum == "ANY":
            self.classNum = [0, 9001]
        else:
            self.classNum = [int(lowNum), int(raw_input("The highest classnumber you want to match: "))]
        deps = raw_input("Enter departments, separated by spaces (e.g. CS Ph): ")
        self.departments = deps.split(" ")
        if not "ANY" in deps:
            gen = raw_input("If you want to match any class that SHARES a department with one of the ones you input, enter Y. Otherwise, enter anything, and it will ONLY match those that are listed under all those departments (and not a single one more). E.g.: Y if you want to include cross-listings.")
            if gen == "Y" or "ANY":
                self.departments.append("GENERAL")
        self.termChar = raw_input("Enter termChar ('A', 'B', 'C', or '') ['ANY' is also an option, as always]: ")
        self.pracOrAnal = raw_input("Enter 'prac' for practical, 'anal' for analytical, '' for a class that isn't split like that: ")
        self.className = raw_input("Enter classname. You should put 'ANY' here unless you're dealing with one of the RARE cases where the previous stuff doesn't fully identify the class; I'm not aware of any. If using this, will need the exact classname used in TQFRS; this is mostly here for if they do something stupid in the future, or if I missed something in the present. ")
    
    def copy(self):
        """NOTE : this is not a perfect copy, in that mD's copy function relies on you not making any changes that would not have been made by the normal read functions."""
        copy = blankTQFR()
        copy.setAllDirect(self.template, self.year, self.term, self.division, self.className, self.classNameForFileName, self.professors, self.url, self.departments, self.classNum, self.termChar, self.pracOrAnal, self.mD)
        copy.departments = [] # This reassigns, does not destroy original...
        for dep in self.departments:
            copy.departments.append(dep)        
        copy.professors = []
        for prof in self.professors:
            copy.professors.append(prof) 
        copy.mD = self.mD.copy()
        return copy
            
    def paddedNum(self, num):
        numStr = str(num)
        return "0" * (5 - len(numStr)) + numStr
    
    def toFilename(self):
        return self.classNameForFileName + self.iS + '_'.join(self.professors) + self.iS + self.year + self.iS + self.term + self.iS + self.division + self.iS + self.pracOrAnal
    
    def toString(self):
        return self.classNameForFileName + self.iS + '_'.join(self.professors) + self.iS + self.year + self.iS + self.term + self.iS + self.division + self.iS + self.pracOrAnal + self.iS + self.url
    
    def sameName(self, otherPage):
        if self.className == otherPage.className:
            return true
        else:
            return false
    
    def matches(self, other):
        # Call regardless of whether it is a template.
        myIdentifiers = [self.year, self.term, self.division, self.className, self.termChar, self.pracOrAnal]
        otherIdentifiers = [other.year, other.term, other.division, other.className, other.termChar, other.pracOrAnal]
        for i in range(len(myIdentifiers)):
            if not myIdentifiers[i] == "ANY" and not otherIdentifiers[i] == "ANY" :
                if not myIdentifiers[i] == otherIdentifiers[i]:
                    return False
        # if "GENERAL" is not in one, matches departments/professor EXACTLY.
        # if it is, then if there is ANY OVERLAP it will match.
        myLists = [self.professors, self.departments]
        otherLists = [other.professors, other.departments]
        for i in range(len(myLists)):
            if not "ANY" in myLists[i] and not "ANY" in otherLists[i]:
                if "GENERAL" in myLists[i] or "GENERAL" in otherLists[i]:
                    noMatch = True
                    for department in myLists[i]:
                        if not department == "GENERAL" and department in otherLists[i]:
                            noMatch = False
                    if noMatch:
                        return False
                else:
                    for department in myLists[i]:
                        if not department in otherLists[i]:
                            return False
                    for department in otherLists[i]:
                        if not department in myLists[i]:
                            return False
        # NUMBER. Here's the annoying one.
        if not self.template and not other.template:
            if not self.classNum == other.classNum:
                return False
        elif not self.template and other.template:
            if self.classNum < other.classNum[0] or self.classNum > other.classNum[1]:
                return False
        elif self.template and not other.template:
            if other.classNum < self.classNum[0] or other.classNum > self.classNum[1]:
                return False
        else: # both are templates
            # Any overlap in the ranges?
            if self.classNum[1] < other.classNum[0]:
                return False
            elif other.classNum[1] < self.classNum[0]:
                return False  
            """
        if not self.mD.taMatches(other.mD):
            return False
            """
        return True        
    
    def matchesAnyOf(self, tqfrTemplateList):
        for tqfrTemplate in tqfrTemplateList:
            if self.matches(tqfrTemplate):
                return True
        return False        



class TQFRdata:
    """Stores data taken from a scraped page. 
    
    ALWAYS included:
    
    Variables:
    Raw data variables:
    (Note that the below are not guaranteed to make any sense).
    sCont: stringContent. A list of (divider-header) and (header, table), in the order found on the scraped page. All in strings. Currently no(divider-headers).
    pCont: percentContent. The above, but with all numbers in its tables actually stored as numbers. "4.00 +/- .82" -> [4.0, 0.82], "60%"-> .6
    nCont: numberContent. The above, but with percents replaced by the actual number or people who voted for each option. Possibly should junk this....No, the translation is useful.
    
    int responders: The number of people who submitted a survey to this page.
    int enrolled: The number of people who took this class
    string classNameA : also used for comment labeling in aggregates. Given to it by the Aggregate class's manipulations. A is for "Above" or "from Aggregate"
    string className : used to label comments on aggregate pages.  Gotten from very top of file. Does NOT have classNameHeader at the end.  (NOT actually used by some TQFRanalyzer functions.)
    string classNameHeader : the part of the classname that will show up in the names for all the tables in the class section. Need to know it so that classAggs can tell when a class has had its name changed to detect false negatives on consolidation. 
    string path: The path to the file it is from, if a single file. "AGG" if it is an aggregate. "BLANK" if whole thing is blank.
        
    ANALYTICS: =================================
    All objects below are NOT automatically defined by init as anything but blank. 
    This is largely because some aggregates will not want them to be anything but blank.
    
    class Analytics: init with initClassAnalytics(), set with setClassAnalytics() 
    classDefined: list of which class analytics are non-blank, and thus will be displayed in fullReport. FORMAT: [["name to display for readout", variable]]
    cList: A list of everything below, regardless of which are non-blank.
    statObj workAmountPerception
    statObj lectureAttendance
    statObj expectedGrade
    statObj passFail
    statObj hoursOutsideClass
    statObj homeworkCompletion
    statObj contentQuality 
    comments : a list of the comments, in string form. This is NOT included in classDefined, and only printed through reportAllData(True). Is included in cList.
    
    professorsData: a list of ProfessorPage objects, one for each professor described on the page.
    
    tasData: a list of TaPage objects, one for each TA described on the page.
    
    # MAYBE IN THE FUTURE (remember to update __init__ and aggPageInit!)
    DepartmentData depData: initDepartment()
    DivisionData divData: initDiv()
    
    """
    
    def __init__(self, path):
        # filename
        if path == "BLANK":
            self.sCont = []
            self.pCont = []
            self.nCont = []
            self.responders = 0
            self.enrolled = 0
            self.classNameA = ''
            self.className = ''
            self.classNameHeader = ''
            self.path = path
            # Data
            self.initAnalytics(False)
        else:
            pageText = ''
            with open(path, 'r') as f:
                pageText = f.read()
            pSoup = BeautifulSoup(pageText, 'html.parser')
            self.classNameA = '' # The reigning Aggregate class will adjust this if it wants to.
            self.readContsAndResponders(pageText, pSoup) # also reads className and classNameHeader
            self.path = path
            self.initAnalytics(True)
                
    def initAnalytics(self, canRead):
        self.initClassData() # gets comments.
        self.professorsData = []
        self.tasData = [] 
        if canRead and self.responders > 0: # numpy can't average a completely empty list....Though actually statObj will catch this itself now.
            self.readAll()
     
    def readAll(self):
        self.readClassData()
        self.readProfessorData()
        self.readTaData()        
    
    def aggPageInit(self, pages, aggName, aggType):
        """ sets this to be an aggregate TQFRdata instance from all the TQFRdata instances in pages.
        it only defines those tables that are present with the same name in ALL of its pages. 
        IMPORTANT: BEFORE CALLING THIS METHOD, you should have made this instance a copy of the aggregate template.
        If you do it afterward, this will all be overwritten.
        This DOES initialize the analytics, but does NOT calculate them.
        aggType is only used for getting around the "class Name changed" issue with classAggs."""
        baseNum = 0   # Using the latest one produced way more weirdness...
        #len(pages)-1 # Use the latest one, chronologically, as the base reference. This actually DOESN'T guarantee latest chronologically due to teacher names. 
        # However, I could implement a search to make it do that... it shouldn't matter though, right now.
        if len(pages) == 0: # SHOULD DEFINE THIS BEHAVIOR BETTER-right now produces we
            #print "CALLED AGGREGATE INIT WITH NO PAGES!"
            #self.setEmptyClassData()
            return 0
        # Figure out which tables to bother with.
        # NOTE: if you call aggPageInit with just 1 page, it will obviously copy everything. 
        # If you later add pages to it, it will delete any tables it does not share with them.
        tableNames = []
        # nCont will always be defined...even if it is an aggregate of aggregate pages!
        # also, my new changes make it so that everything in the nCont is a table; no "just headers"
        # NOTE: this is NOT relying on them not changing the full name of the class to work (it used to). 
        for cont in pages[baseNum].mD.nCont: 
            include = True
            tableRegExp = cont[0] 
            """ Sometimes The full name of a class changes slightly over the years, 
             and thus the tables that include would be inaccurately excluded from a classAgg. if we didn't do this next if clause. """            
            if aggType == "class" and pages[baseNum].mD.classNameHeader in tableRegExp: 
                tableRegExp = ".*" + tableRegExp[len(pages[baseNum].mD.classNameHeader):]
            for page in pages:
                if not page.mD.getTable(page.mD.nCont, tableRegExp):                    
                    # Number 2: Comment string includes a ?, which breaks the regExp, causing this to inaccurately return false. Thus, handle it separately,
                    # And then, if it isn't the comments table, tell the program this table should not be included.
                    m = re.match("Comments > .*", tableRegExp)
                    if not (m and page.mD.getTable(page.mD.nCont, "Comments > .*")): # one last check that it's really not there:
                        include = False
                        break
            if include:
                tableNames.append(tableRegExp)
        # construct total enrolled, responders, in order to construct sCont, pCont, and nCont: (man, do I even USE pCont?)
        self.className = aggName
        self.path = "AGG"
        self.responders = 0
        self.enrolled = 0
        for page in pages:
            self.responders += page.mD.responders
            self.enrolled += page.mD.enrolled
        # Now we just have to construct the sCont, pCont, and nCont. nCont is easiest to start with, most likely. 
        self.sCont = []
        self.pCont = []
        self.nCont = []
        # initialize by copying the relevant tables from the last page
        for tableName in tableNames:
            tableName2 = tableName.replace('?', '\\?')
            conts = [self.copyContentList([(tableName, pages[baseNum].mD.getTable(pages[baseNum].mD.sCont, tableName2))]), 
                      self.copyContentList([(tableName, pages[baseNum].mD.getTable(pages[baseNum].mD.pCont, tableName2))]), 
                      self.copyContentList([(tableName, pages[baseNum].mD.getTable(pages[baseNum].mD.nCont, tableName2))])]
            for i in range(len(conts)):
                conts[i] = [(tableName, self.noteAgg(conts[i][0][1]))]
            self.sCont += conts[0]
            self.pCont += conts[1]
            self.nCont += conts[2]
            # Deal with the special comment table.
            comRe = "Comments > Do you .+"
            m = re.match(comRe, tableName)
            if m:
                if pages[baseNum].mD.classNameA:
                    commentClassName = "-----BELOW FROM CLASS: " + pages[baseNum].mD.classNameA + " " + pages[baseNum].mD.classNameHeader + " -----"
                else:
                    commentClassName = "-----BELOW FROM CLASS: " + pages[baseNum].mD.className + " " + pages[baseNum].mD.classNameHeader + " -----"                
                self.getTable(self.sCont, comRe).insert(0, [commentClassName])
                self.getTable(self.pCont, comRe).insert(0, [commentClassName])
                self.getTable(self.nCont, comRe).insert(0, [commentClassName])
        # Now if there is more than one, add 
        if len(pages) > 1:
            pages2 = pages[1:]
        else:
            pages2 = []
        for page in pages2:
            self.addPageToAgg(page)
        self.initAnalytics(False)
    
    
    # ====================== CLASS analytics ==================================
    
    def initClassData(self):
        self.classDefined = []
        self.workAmountPerception = statObj([-42], [1]) # Makes it clear when there just IS no data.
        self.lectureAttendance = statObj([-42], [1])
        self.expectedGrade = statObj([-42], [1])
        self.passFail = statObj([-42], [1])
        self.hoursOutsideClass = statObj([-42], [1])
        self.homeworkCompletion = statObj([-42], [1])
        self.contentQuality = statObj([-42], [1])   
        self.comments = []
        self.cList = [self.workAmountPerception, self.lectureAttendance, self.expectedGrade, self.passFail, self.hoursOutsideClass, self.homeworkCompletion, self.contentQuality, self.comments]
        
    def setEmptyClassData(self):
        for item in self.cList:
            item.data = []        
    
    #self.classDefined = {'Perceived Under/Overuniting [5 (under) to -5 (over)]: ': self.workAmountPerception, '% Lecture Attendance: ': self.lectureAttendance, 'Expected Grade [A=4,B=3,C=2,D=1,F=0]: ': self.expectedGrade, 'Pass percent if on pass/fail (1 pass, 0 fail): ': self.passFail, 'Hours Spent Outside Class: ': self.hoursOutsideClass, '% Homework Completed: ': self.homeworkCompletion, 'Course Content Quality [0 (bad) to 5 (good)]: ': self.contentQuality}  
    
    def readClassData(self):
        if self.getTable(self.nCont, ".*Was The Amount Of Work Required Higher Or Lower Than The Units Listed In The Catalog?"):
            self.workAmountPerception = statObj([5, 2.5, 0, -2.5, -5], self.getTable(self.nCont, ".*Was The Amount Of Work Required Higher Or Lower Than The Units Listed In The Catalog?")[1][1:-1])
            self.classDefined.append(['Perceived Under/Overuniting [5 (under) to -5 (over)]: ', self.workAmountPerception])
        if self.getTable(self.nCont, ".*% Of Lectures Attended"):
            self.lectureAttendance = statObj(self.getTable(self.nCont, ".*% Of Lectures Attended")[0][1:-1], self.getTable(self.nCont, ".*% Of Lectures Attended")[1][1:-1])
            self.classDefined.append(['% Lecture Attendance: ', self.lectureAttendance])
        if self.getTable(self.nCont, ".*Expected Grade"):
            grades = self.getTable(self.nCont, ".*Expected Grade")[1][1:5] + [self.getTable(self.nCont, ".*Expected Grade")[1][6]]
            self.expectedGrade = statObj([4, 3, 2, 1, 0], grades)
            self.classDefined.append(['Expected Grade [A=4,B=3,C=2,D=1,F=0]: ', self.expectedGrade])
            self.passFail = statObj([1, 0], self.getTable(self.nCont, ".*Expected Grade")[1][7:9])
            self.classDefined.append(['Pass percent if on pass/fail (1 pass, 0 fail): ', self.passFail])
        if self.getTable(self.nCont, ".*Hours/Week Spent On Coursework Outside Of Class"):
            self.hoursOutsideClass = statObj([2, 5, 8, 11, 14, 17.5, 21.5, 25], self.getTable(self.nCont, ".*Hours/Week Spent On Coursework Outside Of Class")[1][1:-1])
            self.classDefined.append(['Hours Spent Outside Class: ', self.hoursOutsideClass])
        if self.getTable(self.nCont, ".*% Of Homework Completed"):
            self.homeworkCompletion = statObj(self.getTable(self.nCont, ".*% Of Homework Completed")[0][1:-1], self.getTable(self.nCont, ".*% Of Homework Completed")[1][1:-1])
            self.classDefined.append(['% Homework Completed: ', self.homeworkCompletion])
        if self.getTable(self.nCont, ".*Course Section: .* > Overall Ratings"):
            self.contentQuality = statObj([5, 4, 3, 2, 1, 0], self.getTable(self.nCont, ".*Course Section: .* > Overall Ratings")[1][1])
            self.classDefined.append(['Course Content Quality [0 (bad) to 5 (good)]: ', self.contentQuality])
        self.readComments()
    
    def readComments(self):
        """Right now there should ALWAYS be a 'comments table,' because if there wasn't one to begin with,
        one should have been added in readContsAndResponders, so that aggPages of old classes wouldn't fail to display all their 
        comments because one of the old classes didn't have comments, and so that they can report which ones did not. 
        However, please leave the check for existence in just in case this someday changes."""
        table = self.getTable(self.nCont, "Comments > .+")
        if table:
            self.comments = table 
        
    
    def reportClassData(self):
        if self.enrolled > 0:
            perResp = str(round( ((float(self.responders) / float(self.enrolled))) * 100, 3)) + "%"
        else:
            perResp = "N/A"
        print "CLASS DATA ================================"
        print "Note: if responders for individual item < responders for whole (under Percent Response), remainder selected Not Answered."
        reportTable = [["Statistical Quantity: ", "Average +/- stdev", "Quartiles", "Responders"],
                       ["------", "------", "------", "------"],
                       ["Percent Response: ", perResp, "enrolled: " + str(self.enrolled), str(self.responders)]]
        for item in self.classDefined:
            newRow = [item[0]] + item[1].toRow()
            reportTable.append(newRow)
        prettyPrintTable(reportTable)
    
    def reportComments(self):
        print "Comments: =================================="
        prettyPrintTable(self.comments) # NOte: my attempt to get this to print nicely goes in the formalizing of comments that occurs where nCont and pCont are set.
        
    # ===================== PROFESSOR data ===================================
    
    def readProfessorData(self):
        # sets up the professorsData list.
        self.professorsData = [] # Just in case....
        tempCont = self.copyContentList(self.nCont)
        while self.getTable(tempCont, "Instructor Section: .*"):
            prof = '.*'
            myData = []
            toDelete = []
            for i in range(len(tempCont)):
                if len(tempCont[i]) == 2 and tempCont[i][0]:
                    m = re.match("Instructor Section: (" + prof + ") > (.*)", tempCont[i][0])
                    if m:
                        prof = m.group(1)
                        myData.append(tempCont[i])
                        toDelete.append(i)
            self.professorsData.append(ProfessorPage(myData, prof, self.responders, self.enrolled))
            toDelete.reverse()
            for index in toDelete:
                del tempCont[index]
        for prof in self.professorsData:
            prof.readProfessorData()
        
        
    # ======================== TA data ===================================
    
    def readTaData(self):
        self.tasData = [] # Just in case....
        tempCont = self.copyContentList(self.nCont)
        while self.getTable(tempCont, "Teaching Assistant Section: .*"):
            ta = '.*'
            myData = []
            toDelete = []
            for i in range(len(tempCont)):
                if len(tempCont[i]) == 2 and tempCont[i][0]:
                    m = re.match("Teaching Assistant Section: (" + ta + ") > (.*)", tempCont[i][0])
                    if m:
                        ta = m.group(1)
                        myData.append(tempCont[i])
                        toDelete.append(i)
            self.tasData.append(TaPage(myData, ta, self.responders))
            toDelete.reverse()
            for index in toDelete:
                del tempCont[index]
        for ta in self.tasData:
            ta.readTaData()
    
    # ================ useful functions after the Conts data containers have been set up.
    
    def reportAllData(self, comments):
        if self.classDefined:
            self.reportClassData()
        for prof in self.professorsData:
            prof.reportProfessorData()
        for ta in self.tasData:
            ta.reportTaData()
        if comments:
            self.reportComments()
        
    def printPage(self, contentList):
        # Content list = nCont, pCont, or sCont.
        for item in contentList:
            if len(item) == 1:
                print item.contents
            elif item[0]:
                print "[--" + item[0] + "--]"
                prettyPrintTable(item[1])
            else:
                print ''
                prettyPrintTable(item[1])        
        
    def getTable(self, contentList, tableName):
        for item in contentList:
            if len(item) == 2 and item[0] and re.match(tableName, item[0]):
                return item[1]
        return False 
    
    def copy(self):
        # NOTE : this is not a perfect copy, in that it relies on you not making any changes that 
        # would not have been made by the normal read functions.
        if self.path == "AGG":
            toReturn = TQFRdata("BLANK")
            toReturn.initAgg([self], self.className)
        else:
            toReturn = TQFRdata(self.path)
        # For the non-blank ones, need to check if subsections are blank.
        if self.classDefined:
            toReturn.readClassData()
        for prof in self.professorsData :
            for defList in allDef:
                if defList:
                    prof.readProfessorData()
                    break
        for ta in self.tasData:
            if taDef:
                ta.readTaData()
        return toReturn
    
    def taMatches(self, other):
        # right now only used to check for TA's! Possibly adjust into a full match function later...
        myTAs = []
        otherTAs = []
        for ta in self.tasData:
            myTAs.append(ta.taName)
        for ta in other.tasData:
            otherTAs.append(ta.taName)
        if "ANY" in myTAs or "ANY" in otherTAs:
            return True
        else:
            for ta in myTAs:
                if ta in otherTAs:
                    return True
        return match
    
    # ====== Helper functions for an aggragate page initialization. =========
    
    def addPageToAgg(self, page):
        # NOTE: DOES NOT recalculate and initialize the data analysis objects (other than self.responders and self.enrolled.).
        # must delete any non-shared tables. Thus, the current tables we have will serve as a guide as to which to translate in.
        # Run from the aggregate, page is the page to add. 
        self.responders += page.mD.responders
        self.enrolled += page.mD.enrolled
        tableNames = []
        toDelete = []
        for i in range(len(self.nCont)):
            cont = self.nCont[i]
            comRe = "Comments > .*"
            if not re.match(comRe, cont[0]) and not page.mD.getTable(page.mD.nCont, cont[0]):
                toDelete.append(i)
        toDelete.reverse()
        for index in toDelete:
            del self.sCont[index]
            del self.pCont[index]
            del self.nCont[index]
        # we do the merging after the deleting in order to make things faster with the searches.
        for cont in self.nCont:
            self.mergePagesTable(page, cont[0])

    def mergePagesTable(self, page, tableName):
        # This assumes that you have already updated the total responders and enrolled.
        myTableS = self.getTable(self.sCont, tableName.replace("?", "\\?"))
        newTableS = page.mD.getTable(page.mD.sCont, tableName.replace("?", "\\?"))
        myTableP = self.getTable(self.pCont, tableName.replace("?", "\\?"))
        newTableP = page.mD.getTable(page.mD.pCont, tableName.replace("?", "\\?"))        
        myTableN = self.getTable(self.nCont, tableName.replace("?", "\\?"))
        newTableN = page.mD.getTable(page.mD.nCont, tableName.replace("?", "\\?"))
        # For convenience, put 'em in a list
        myTables = [myTableS, myTableP, myTableN]
        newTables = [newTableS, newTableP, newTableN]
        # The comments table is special.
        m = re.match("Comments > Do you .*", tableName)
        if m:
            try:
                for i in range(len(myTables)):
                    table = myTables[i]
                    if page.mD.classNameA:
                        commentClassName = "-----BELOW FROM CLASS: " + page.mD.classNameA + " " + page.mD.classNameHeader + " -----"
                    else:
                        commentClassName = "-----BELOW FROM CLASS: " + page.mD.className + " " + page.mD.classNameHeader + " -----"
                    table.append([commentClassName])
                    table += newTables[i]
                return True 
            except TypeError:
                print "Issue with comments table!! Table " +str(i)+ " had a TypeError. newTables:" + str(newTables)
        # For all other tables...Remember that at least nCont HAS to be in the right format to be read correctly!
        try:
            for r in range(1, len(myTableN)): # Note that we skip the column titles!
                for c in range(1, len(myTableN[0])): # ...and also the row titles.
                    cell = myTableN[r][c]
                    if isinstance(cell, int):
                        myTableN[r][c] += newTableN[r][c]
                        if self.enrolled > 0:
                            myTableP[r][c] = round(float(cell) / float(self.enrolled), 2)
                        else:
                            myTableP[r][c] = 0 # Yes, this only matters for ones that allowed responses from unenrolled people. THose are rare, just zero it.                  
                        myTableS[r][c] = str(myTableP[r][c] * 100) + "%"
                    elif isinstance(cell, list):
                        string = ''
                        for i in range(len(cell)):
                            myTableN[r][c][i] += newTableN[r][c][i]
                            string += str(myTableN[r][c][i]) + ","
                        myTableP[r][c] = myTableN[r][c]
                        string = string[:-1] # chop off excess comma
                        myTableS[r][c] = string           
                    elif not cell == "agg":
                        print "WARNING! Weird cell/problem: " + tableName + " row: " + str(r) + " column: " + str(c) + " value: " + str(cell)
        except IndexError:
            print "weird table! " +"r:" + str(r) + " c:" + str(c) + " i:" + str(i) + " " +str(myTableN)
        
    def noteAgg(self, table):
        # ALTERS AND RETURNS THE PASSED TABLE! Helper function for aggInit
        for r in range(len(table)):
            if table[r][0] == "Department Average" or table[r][0] == "Division Average" or table[r][0] == "Survey Average":
                for c in range(1, len(table[r])): # skip the leftmost column
                    table[r][c] = "agg"
        for c in range(len(table[0])):
            if table[0][c] == "Score" or table[0][c] == "Dept." or table[0][c] == "Div." or table[0][c] == "Caltech":
                for r in range(1, len(table)): # skip the topmost row
                    table[r][c] = "agg"
        return table
    
    # ===== Helper functions for ordinary initialization, except those involved in data read in ====
    
    def readContsAndResponders(self, pageText, pSoup):
        # also reads enrolled and className
        self.sCont = self.extractTablesWithHeaders(pageText, pSoup)
        self.pCont = self.copyContentList(self.sCont) # will be  more changes!
        self.nCont = self.copyContentList(self.sCont)
        self.readRespAndEnrolled()
        hasComments = False
        for i in range(len(self.sCont)):
            item = self.sCont[i]
            table = item[1]
            if len(item) == 2 and not re.match("Comments > .*", item[0]):
                for r in range(len(table)):
                    for c in range(len(table[0])):
                        num = self.toNumber(table[r][c])
                        self.pCont[i][1][r][c] = num
                        if "%" in table[r][c] and not r == 0:
                            self.nCont[i][1][r][c] = self.toPersons(table[r][c])
                        else:
                            self.nCont[i][1][r][c] = num 
            elif len(item) == 2:
                hasComments = True
                prettyComments = []
                for row in table:
                    #print row
                    prettyComments.append([textwrap.fill(row[0], 80)]) # wrap length set for my convenience.... Also adjust for not hasComments below if you change it.
                comCont = (item[0], prettyComments)
                del self.sCont[i]
                del self.pCont[i]
                del self.nCont[i]
                self.sCont.append(comCont)
                self.pCont.append(comCont)
                self.nCont.append(comCont)
        # We don't want the fact that TQFR didn't use to have comments (2010-2011, it seems) to keep ALL comments from not displaying in an aggregate.
        if not hasComments:
            noCommentTableNote = textwrap.fill(u"This TQFRpage did not have a standard comments table. It may have an odd comments table with a different name. If it is old (say 2010-2011 or previous) it probably just didn't have comments.", 80)
            noCommentTableCont = (u'Comments > Do you have any constructive comments for other students considering taking this course? In particular, comments about workload/distribution of the workload of the course, the necessity of the textbook, unexpected time requirements or flexibility, or unspecified prerequisites could be particularly helpful.', [[noCommentTableNote]])
            #self.comments = [[noCommentTableNote]] # This will be done later if necessary. 
            self.sCont.append(noCommentTableCont)
            self.pCont.append(noCommentTableCont)
            self.nCont.append(noCommentTableCont)        
                
                            
    def readRespAndEnrolled(self):
        # prerequisite: sCont set correctly.
        self.responders = int(self.getTable(self.sCont, ".*Response Rate")[1][1])
        self.enrolled = int(self.getTable(self.sCont, ".*Response Rate")[1][2])    
        #if self.enrolled < 1: # EE 99 has 8 TQFR responses over two years of surveys even though 0 people actually enrolled in the class. Huh?
        #    seld.enrolled = 1 # This prevents divide by zero errors.  ...Decided to just fix 'em as it's used, sadly.
            
    
    
    # ===== Helper functions used for reading in data. =======================
    def toNumber(self, ele):
        if re.match("\d*\.*\d*%", ele) and not re.match("\d*\.*\d*%.+", ele):
            return float(ele[:-1]) / float(100)
        else:
            return self.nonPercentToNum(ele)
    
    def toPersons(self, ele):
        if re.match("\d*\.*\d*%", ele) and not re.match("\d*\.*\d*%.+", ele):
            return int(round( (float(ele[:-1]) / float(100)) * self.responders ))
        else:
            return self.nonPercentToNum(ele)
    
    def nonPercentToNum(self, ele):
        if ele.isdigit():
            return int(ele)
        sDev = re.match("(\d*\.\d*)\D*(\d*\.\d*)", ele)
        if sDev:
            return [float(sDev.group(1)), float(sDev.group(2))] 
        # This one has to go after sDev, because match matches from the start of the string.
        flt = re.match("\d*\.\d*", ele)
        if flt:
            return float(ele)  
        sLst = re.match("(\d*),(\d*),(\d*),(\d*),(\d*),(\d*)", ele)
        if sLst:
            return [int(sLst.group(1)), int(sLst.group(2)), int(sLst.group(3)), int(sLst.group(4)), int(sLst.group(5)), int(sLst.group(6))]
        return ele
    
    def extractTablesWithHeaders(self, pageText, pSoup):
        # helper function for init
        lines = pageText.split('\n')
        lineNums = []
        lineNums.append('header') # a hack to get the course name attached to things...
        lineNums.append('header')
        for i in range(len(lines)):
            if '<h2' in lines[i] or '<h3' in lines[i]:
                lineNums.append('header')
            if '<table' in lines[i]:
                lineNums.append('table')
        (headers, tables) = self.extractAllHeadersAndTables(pSoup)
        hNum = 0
        tNum = 0
        items = []
        for i in range(len(lineNums)):
            if lineNums[i] == 'table':
                tHead = ''
                if i > 0 and lineNums[i-1] == 'header':
                    tHead = items[-1].contents[0]
                    del items[-1]
                items.append((tHead, tables[tNum]))
                tNum += 1
            elif lineNums[i] == 'header':
                items.append((headers[hNum]))
                hNum += 1
        headerNums = []
        for i in range(len(items)):
            if len(items[i]) == 1:
                headerNums.append(i)
        for num in headerNums:
            index = num + 1
            while index < len(items) and len(items[index]) == 2:
                items[index] = (items[num].contents[0] + " > " + items[index][0], items[index][1])
                index += 1
        headerNums.reverse()
        for num in headerNums:
            del items[num]
        del items[-1] # Removes the one bad table at the end of everything.
        return items
    
    def extractAllHeadersAndTables(self, pSoup):
        # helper function for extractTablesWithHeaders
        pTables = pSoup.find_all('table')
        tables = []
        for table in pTables:
            tables.append(self.convertTable(table))
            '''
            if u'class' in table.attrs and table[class] == u"tablediv comment-table":
                tables.append(self.convertCommentTable(table))
            else:
                tables.append(self.convertTable(table))'''
        headers1 = pSoup.find_all(['h2', 'h3']) #+ pSoup.find_all('h3')
        headers = [pSoup.find('h1',"offering_title")] + [pSoup.find('h1',"offering_title")] + headers1
        self.className = pSoup.find('h1', 'survey_title clearfix').contents[0].encode('utf-8')
        self.classNameHeader = pSoup.find('h1', 'offering_title').contents[0].encode('utf-8')
        #print self.className 
        return (headers, tables)
        
    def convertTable(self, table):
        # helper function for extractAllHeadersAndTables
        data = []
        rows = table.find_all('tr')
        for row in rows:
            cols1 = row.find_all('td')     
            cols = []
            for col in cols1:
                if len(col.contents) < 3 or not col.find('div'):
                    cols.append(col.text.strip())
                else:
                    cols.append(col.find('div')['data-values'])   
            #cols = [ele.text.strip() for ele in cols1]
            headerCols = row.find_all('th')
            headerCols = [ele.text.strip() for ele in headerCols]
            data.append(headerCols + cols)
            #data.append([ele for ele in cols if ele]) # Get rid of empty values
        return data     
    
    def copyContentList(self, cL): 
        # cL is a contentList like the sCont, pCont or nCont.
        nC = [] # newContent
        for item in cL:
            if len(item) == 1:
                nC.append((item))
            else:
                newTable = [] 
                for r in item[1]:
                    newRow = []
                    for c in r:
                        newRow.append(c)
                    newTable.append(newRow)
                nC.append((item[0], newTable))
        return nC
    
class TaPage:
    """  class for use with TQFRdata.
    Because a given class page can have more than one TA.
    
    passed from above
    self.taResponders = num people who gave data on TA
    self.classResponders = num people who gave data on class this TaPage came from.
    self.nCont
    string taName
    
    list taDef : list of items that are non-blank, for display. FORMAT: [["name1 to display for readout", variable1], ["name2 to display for readout", variable2]]
    statObj helpfulComments
    statObj answeredQuestions
    statObj wasPrepared
    statObj presentedClearly
    statObj overall
    """
    
    def __init__(self, nCont, taName, classResponders):
        self.taResponders = 0
        self.classResponders = classResponders
        self.nCont = nCont # YOU MUST pass it a nCont that contains no data on any other TA.
        self.taName = taName
        # actual data below
        self.taDef = []
        self.helpfulComments = statObj([1], [1])
        self.answeredQuestions = statObj([1], [1])
        self.wasPrepared = statObj([1], [1])
        self.presentedClearly = statObj([1], [1])
        self.overall = statObj([1], [1])
    
    def readTaData(self):
        table = self.getTable(self.nCont, "Teaching Assistant Section: .* > Teaching Assistant Ratings")
        if table:
            self.taResponders = len(statObj([1, 1, 1, 1, 1, 1], table[1][1]).data)
            self.overall = statObj([5, 4, 3, 2, 1], table[5][1][:-1])
            self.helpfulComments = statObj([5, 4, 3, 2, 1], table[1][1][:-1])
            self.answeredQuestions = statObj([5, 4, 3, 2, 1], table[2][1][:-1])
            self.wasPrepared = statObj([5, 4, 3, 2, 1], table[3][1][:-1])
            self.presentedClearly = statObj([5, 4, 3, 2, 1], table[4][1][:-1])
            self.taDef = [["Overall teaching effectiveness", self.overall],
                       ["Provided helpful comments on assignments, papers, exams", self.helpfulComments],
                       ["Answered questions clearly and concisely", self.answeredQuestions],
                       ["Was well prepared for section, office hours or lab", self.wasPrepared],
                       ["Presented material clearly in section or lab", self.presentedClearly]]        
            
    def reportTaData(self):
        if self.classResponders > 0:
            perResp = str(round( ((float(self.taResponders) / float(self.classResponders)) * 100 ), 0)) + "%"
        else:
            perResp = "N/A"        
        print "TA DATA: " + self.taName + " ================================"
        print "NOTE: if responders for individual item < responders for whole (under Percent Response), remainder selected N/A."
        reportTable = [["Statistical Quantity: ", "Average +/- stdev", "Quartiles", "Responders"],
                       ["------", "------", "------", "------"],
                       ["Percent of responders to CLASS that gave info on TA: ", perResp, "", str(self.taResponders)]]
        for item in self.taDef:
            newRow = [item[0]] + item[1].toRow()
            reportTable.append(newRow)         
        prettyPrintTable(reportTable)
    
    # Functions that make me wonder if I should be using some manner of inheritance....
    
    def getTable(self, contentList, tableName):
            for item in contentList:
                if len(item) == 2 and item[0] and re.match(tableName, item[0]):
                    return item[1]
            return False     
    
class ProfessorPage:
    """ A class for use with TQFRdata.
    Because a given class page can have more than one professor.
    
    professor Data: init with initProfessorData(), set with setProfessorData()
    passed from above
    self.responders = responders
    self.enrolled = enrolled
    self.nCont
    string professorName
    list allDefs = [self.pOverallDef, self.pOrgDef, self.pEngageDef, self.pInteractionDef, self.pContEvalDef]
    
    list pOverallDef : list of items that are non-blank, for display. FORMAT: [["name1 to display for readout", variable1], ["name2 to display for readout", variable2]]
    statObj overallTeaching 
    ---Organization/Clarity---
    list pOrgDef : as pOverallDef, except for this section of variables.
    statObj clearObjectives
    statObj understoodMaterial
    statObj explainedWell
    statObj distinguishedImportances ('Distinguished between more important and less important topics').
    statObj goodPacing
    ---Ability to Engage and Challenge Students Intellectually---
    list pEngageDef : as pOverallDef, except for this section of variables.
    statObj taughtConceptualThinking ('Emphasized conceptual understanding and/or critical thinking')
    statObj relatedCourseTopics
    ---Interaction with Students---
    list pInteractionDef : as pOverallDef, except for this section of variables.
    statObj concernAboutStudents
    statObj inspirational
    statObj outsideConsultation
    ---Course Organization, Content, and Evaluation---
    list pContEvalDef : as pOverallDef, except for this section of variables.
    statObj courseContentChoices
    statObj organizedCoherently
    statObj usefulHomework
    statObj explainedEvaluation
    statObj fairGrading
    statObj reflectiveTests"""
    
    def __init__(self, nCont, professorName, responders, enrolled):
        # DOES NOT Automatically read in professor data!
        self.responders = responders
        self.enrolled = enrolled
        self.nCont = nCont # YOU MUST pass it a nCont that contains no data on any other professor.
        self.professorName = professorName
        # actual data below
        self.pOverallDef = []
        self.overallTeaching = statObj([1], [1])
        #---Organization/Clarity#---
        self.pOrgDef = []
        self.clearObjectives = statObj([1], [1])
        self.understoodMaterial = statObj([1], [1])
        self.explainedWell = statObj([1], [1])
        self.distinguishedImportances = statObj([1], [1])
        self.goodPacing = statObj([1], [1])
        #---Ability to Engage and Challenge Students Intellectually#---
        self.pEngageDef = []
        self.taughtConceptualThinking = statObj([1], [1])
        self.relatedCourseTopics = statObj([1], [1])
        #---Interaction with Students#---
        self.pInteractionDef = []
        self.concernAboutStudents = statObj([1], [1])
        self.inspirational = statObj([1], [1])
        self.outsideConsultation = statObj([1], [1])
        #---Course Organization, Content, and Evaluation#---
        self.pContEvalDef = []
        self.courseContentChoices = statObj([1], [1])
        self.organizedCoherently = statObj([1], [1])
        self.usefulHomework = statObj([1], [1])
        self.explainedEvaluation = statObj([1], [1])
        self.fairGrading = statObj([1], [1])
        self.reflectiveTests = statObj([1], [1])  
        # Finally...
        self.allDefs = [self.pOverallDef, self.pOrgDef, self.pEngageDef, self.pInteractionDef, self.pContEvalDef]
    
    def readProfessorData(self):
        table = self.getTable(self.nCont, "Instructor Section: .* > Overall Ratings")
        if table:
            self.overallTeaching = statObj([5, 4, 3, 2, 1], table[1][1][:-1])
            self.pOverallDef.append(["The instructor's overall teaching", self.overallTeaching])
        table = self.getTable(self.nCont, "Instructor Section: .* > Organization/Clarity")
        if table:
            self.clearObjectives = statObj([5, 4, 3, 2, 1], table[1][1][:-1])
            self.understoodMaterial = statObj([5, 4, 3, 2, 1], table[2][1][:-1])
            self.explainedWell = statObj([5, 4, 3, 2, 1], table[3][1][:-1])
            self.distinguishedImportances = statObj([5, 4, 3, 2, 1], table[4][1][:-1])
            self.goodPacing = statObj([5, 4, 3, 2, 1], table[5][1][:-1])
            self.pOrgDef = [["Set out and met clear objectives announced for the course", self.clearObjectives],
                       ["Displayed thorough knowledge of course material", self.understoodMaterial],
                       ["Explained concepts clearly", self.explainedWell],
                       ["Distinguished between more important and less important topics", self.distinguishedImportances],
                       ["Presented material at an appropriate pace", self.goodPacing]]        
        table = self.getTable(self.nCont, "Instructor Section: .* > Ability to Engage and Challenge Students Intellectually")
        if table:
            self.taughtConceptualThinking = statObj([5, 4, 3, 2, 1], table[1][1][:-1])
            self.relatedCourseTopics = statObj([5, 4, 3, 2, 1], table[2][1][:-1])      
            self.pEngageDef = [["Emphasized conceptual understanding and/or critical thinking", self.taughtConceptualThinking],
                               ["Related course topics to one another", self.relatedCourseTopics]]
        table = self.getTable(self.nCont, "Instructor Section: .* > Interaction with Students")
        if table:
            self.concernAboutStudents = statObj([5, 4, 3, 2, 1], table[1][1][:-1])
            self.inspirational = statObj([5, 4, 3, 2, 1], table[2][1][:-1])
            self.outsideConsultation = statObj([5, 4, 3, 2, 1], table[3][1][:-1])
            self.pInteractionDef = [["Demonstrated concern about whether students were learning", self.concernAboutStudents],
                                    ["Inspired and motivated student interest in the course content", self.inspirational],
                                    ["Was available for consultation outside of class", self.outsideConsultation]]
        table = self.getTable(self.nCont, "Instructor Section: .* > Course Organization, Content, and Evaluation")
        if table:
            self.pContEvalDef = [] # I do not want to think about what else may need to be set up like this.
            for row in table:
                if row[0] == "Selected course content that was valuable and worth learning":
                    self.courseContentChoices = statObj([5, 4, 3, 2, 1], row[1][:-1])
                    self.pContEvalDef.append(["Selected course content that was valuable and worth learning", self.courseContentChoices])
                elif row[0] == "Organized course topics in a coherent fashion":
                    self.organizedCoherently = statObj([5, 4, 3, 2, 1], row[1][:-1])
                    self.pContEvalDef.append(["Organized course topics in a coherent fashion", self.organizedCoherently])
                elif row[0] == "Chose assignments that solidified understanding":
                    self.usefulHomework = statObj([5, 4, 3, 2, 1], row[1][:-1])
                    self.pContEvalDef.append(["Chose assignments that solidified understanding", self.usefulHomework])  
                elif row[0] == "Explained clearly how students would be evaluated":
                    self.explainedEvaluation = statObj([5, 4, 3, 2, 1], row[1][:-1])
                    self.pContEvalDef.append(["Explained clearly how students would be evaluated", self.explainedEvaluation])  
                elif row[0] == "Designed and used fair grading procedures":
                    self.fairGrading = statObj([5, 4, 3, 2, 1], row[1][:-1])
                    self.pContEvalDef.append(["Designed and used fair grading procedures", self.fairGrading])  
                elif row[0] == "Gave tests and quizzes that accurately reflected material taught":
                    self.reflectiveTests = statObj([5, 4, 3, 2, 1], row[1][:-1])
                    self.pContEvalDef.append(["Gave tests and quizzes that accurately reflected material taught", self.reflectiveTests])  
            """
            self.courseContentChoices = statObj([5, 4, 3, 2, 1], table[1][1][:-1])
            self.organizedCoherently = statObj([5, 4, 3, 2, 1], table[2][1][:-1])
            self.usefulHomework = statObj([5, 4, 3, 2, 1], table[3][1][:-1])
            self.explainedEvaluation = statObj([5, 4, 3, 2, 1], table[4][1][:-1])
            self.fairGrading = statObj([5, 4, 3, 2, 1], table[5][1][:-1])
            self.reflectiveTests = statObj([5, 4, 3, 2, 1], table[6][1][:-1])  
            self.pContEvalDef = [["Selected course content that was valuable and worth learning", self.courseContentChoices],
                                 ["Organized course topics in a coherent fashion", self.organizedCoherently],
                                 ["Chose assignments that solidified understanding", self.usefulHomework],
                                 ["Explained clearly how students would be evaluated", self.explainedEvaluation],
                                 ["Designed and used fair grading procedures", self.fairGrading],
                                 ["Gave tests and quizzes that accurately reflected material taught", self.reflectiveTests]]
            """
            
    def reportProfessorData(self):
        if self.enrolled > 0:
            perResp = str(round( ((float(self.responders) / float(self.enrolled))) * 100, 0))
        else:
            perResp = "N/A"        
        print "PROFESSOR DATA: " + self.professorName + "  ==================================="
        print "NOTE: if responders for individual item < responders for whole (under Percent Response), remainder selected N/A."
        reportTable = [["Statistical Quantity: ", "Average +/- stdev", "Quartiles", "Responders"],
                       ["------", "------", "------", "------"],
                       ["Percent Response: ", perResp, "", str(self.responders)]]
        reportTable.append(self.subHeaderRow("Overall Ratings"))
        for item in self.pOverallDef:
            newRow = [item[0]] + item[1].toRow()
            reportTable.append(newRow)  
        reportTable.append(self.subHeaderRow("Organization/Clarity"))
        for item in self.pOrgDef:
            newRow = [item[0]] + item[1].toRow()
            reportTable.append(newRow)        
        reportTable.append(self.subHeaderRow("Ability to Engage and Challenge Students Intellectually"))
        for item in self.pEngageDef:
            newRow = [item[0]] + item[1].toRow()
            reportTable.append(newRow)        
        reportTable.append(self.subHeaderRow("Interaction with Students"))  
        for item in self.pInteractionDef:
            newRow = [item[0]] + item[1].toRow()
            reportTable.append(newRow)        
        reportTable.append(self.subHeaderRow("Course Organization, Content, and Evaluation"))
        for item in self.pContEvalDef:
            newRow = [item[0]] + item[1].toRow()
            reportTable.append(newRow)        
        prettyPrintTable(reportTable)
    
    # Functions that make me wonder if I should be using some manner of inheritance....
    def subHeaderRow(self, name):
        return ["---" + name + "---", "------", "------", "------"]
    
    def getTable(self, contentList, tableName):
            for item in contentList:
                if len(item) == 2 and item[0] and re.match(tableName, item[0]):
                    return item[1]
            return False     


class statObj:
    """ A class for use with TQFRdata. 
    Vars:
    data: a list of the numberical data. NOT weighted. 
    average: duh. 
    std: standard deviation
    qs = [q25, q50,  q75]: the 25th, 50th, and 75th percentiles."""
    
    def __init__(self, vals, frequencyOfVals):
        # frequencyOfVals should be a list of INTEGERS.
        self.data = []
        for i in range(len(vals)):
            for j in range(frequencyOfVals[i]):
                self.data.append(vals[i])
        if len(self.data) > 0:
            self.calculate()
        else:
            self.average = -42
            self.std = -42
            self.qs = [-42, -42, -42]
    
    def myRound(self, num):
        return numpy.around(num, decimals=2)
    
    def calculate(self):
        self.average = self.myRound(numpy.average(self.data))
        self.std = self.myRound(numpy.std(self.data))
        self.qs =[self.myRound(numpy.percentile(self.data, 25)), self.myRound(numpy.percentile(self.data, 50)), self.myRound(numpy.percentile(self.data, 75))]      
    
    def getAverage(self):
        if not self.average == -42:
            return str(round(self.average, 3))
        else:
            return "NoData"
        
    def getStd(self):
        if not self.std == -42:
            return str(round(self.std, 3))
        else:
            return "NoData"        
    def getQuartiles(self):
        if not (self.qs[0] == -42 and self.qs[1] == -42 and self.qs[2] == -42):
            return str([round(self.qs[0], 3), round(self.qs[1], 3), round(self.qs[02], 3)])
        else:
            return "NoData"
    def getResponders(self):
        return str(len(self.data))
    
    def toLabeledString(self):
        return "Average +/- stdDev: " + self.getAverage() + " +/- " + self.getStd() + " | " + "Quartiles: " + self.getQuartiles() + "Responders: " + self.getResponders()
    
    def toString(self):
        return self.getAverage() + " +/- " + self.getStd() + " | " + self.getQuartiles() + " | " + self.getResponders()
    
    def toRow(self):
        return [self.getAverage() + " +/- " + self.getStd(), self.getQuartiles(), self.getResponders()]