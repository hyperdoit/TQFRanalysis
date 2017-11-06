import os, copy
from bs4 import BeautifulSoup
import TQFRpage

"""
tqfrData = os.path.abspath(".")
tqfrDataFolder = os.path.join(tqfrData, "TQFRdata")
scrapedPagesPath = os.path.join(tqfrDataFolder, "scrapedPages")
"""

class TQFRanalyzer:
    """ The class that handles all the analysis. This is the one that ties everything together!" 
    
    Variables:
    static: ====
    analyzerCommandInstructs
    
    behavior definers: ====
    debugOn
    THIS IS SET IN runThisOne.
    
    file locations: ====
    self.scrapedPagesPath
    
    lists: ====
    loadedNames: a list of all the filenames in scrapedPagesPath when last loaded. 
    loaded: a list containing a TQFRpage instance for every file in scrapedPages, once it has been loaded into- NOT automatically initialized!
    classAggs: a list of ClassAggregates. Once constructed, one for each class in the loaded.
    """

    def __init__(self, tqfrDataPath):
        self.tqfrDataFolder = os.path.join(tqfrDataPath, "TQFRdata")
        self.scrapedPagesPath = os.path.join(os.path.join(tqfrDataPath, "TQFRdata"), "scrapedPages")
        self.loaded = [] # a list of TQFRpage classes. Not automatically initialized!
        self.loadedNames = [] # nothing loaded yet
        self.classAggs = []
        self.classAggsClassNames = [] # Note this is not kept ordered the same as classAggs by sortClaggs, currently.
        self.debugOn = True
        # self.load() # Nah, not now that it runs load on entering its loop.
        
    # LOADING FUNCTIONS =================================================
    # schedules !
    def loadRegistrar(self):
        # THIS SHOULD DO MORE THAN IT CURRENTLY DOES.
        pageText = ''
        with open(os.path.join(self.tqfrDataFolder, "registrarCourseSchedules"), "r") as f:
            pageText = f.read()
        courseSoup = BeautifulSoup(pageText, 'html.parser')
        return courseSoup 
        
    def reloadAll(self): # reload everything.
        tempFiles = os.listdir(self.scrapedPagesPath)
        self.loaded = []
        self.loadedNames = []
        print "LOADED: "
        for f in tempFiles:
            if not f in self.loadedNames:
                self.loadedNames.append(f)
                self.loaded.append(TQFRpage.tqfrFromFilenameAndPath(f, os.path.join(self.scrapedPagesPath, f)))
                print f
    
    def load(self):
        tempFiles = os.listdir(self.scrapedPagesPath)
        print "LOADED: "
        if not self.debugOn:
            warnings = []
            for f in tempFiles:
                try:
                    self.loadOne(f)
                except:
                    warnings.append(f)
                    print "Initial Warning: could not load: " + f
            for fileName in warnings:
                print "WARNING: COULD NOT LOAD: " + fileName # Suggestion to self: to find what's wrong with these, define a single-load function, and use that to explore these issues.
        else:
            for f in tempFiles:
                self.loadOne(f)
    
    def loadOne(self, f): # this function should not catch exceptions. Change that.
        # f is a filename.
        if not f in self.loadedNames:
            self.loaded.append(TQFRpage.tqfrFromFilenameAndPath(f, os.path.join(self.scrapedPagesPath, f)))
            self.loadedNames.append(f)
            print f 
            return True
        return False
                
    def loadFromTemplate(self, template):
        ''' Loads things that match a TQFRpage template. ONLY looks at what can be learned from the filename, 
        because loading in from data would defeat the point of having this speed up; so TQFRpage, but not TQFRdata.'''
        tempFiles = os.listdir(self.scrapedPagesPath)
        warnings = []        
        print "LOADED: "
        if not self.debugOn:
            warnings = []
            for f in tempFiles:
                try:
                    self.loadOneWithTemplateCheck(f, template)
                except:
                    warnings.append(f)
                    print "Initial Warning: could not load: " + f
            for fileName in warnings:
                print "WARNING: COULD NOT LOAD: " + fileName # Suggestion to self: to find what's wrong with these, define a single-load function, and use that to explore these issues.
        else:
            for f in tempFiles:
                self.loadOneWithTemplateCheck(f, template)
                
    def loadOneWithTemplateCheck(self, filename, template):
        # returns the preloaded file if the preload matches the template.
        if not filename in self.loadedNames:
            preload = TQFRpage.tqfrFromFilename(filename)
            if preload.matches(template):
                preload.mD = TQFRpage.TQFRdata(os.path.join(self.scrapedPagesPath, filename))
                self.loaded.append(preload)
                self.loadedNames.append(filename)
                print filename
                return True
        return False
    
    # ============Analyzer's aggregate-manipulation functions ================
    
    # ===========This is an important funtion! It should first check if the aggregate is already loaded, really...well...maybe not. 
    def compileAgg(self, template, aggType):
        # compiles an aggregate from the loaded files. Returns it.
        aggy = Aggregate([], template, aggType)
        for page in self.loaded:
            aggy.tryAddPage(page)
                #print "Added: " + page.toFilename()
        return aggy
    
    def compileAllClassAggs(self):
        for page in self.loaded:
            if not page.className in self.classAggsClassNames:
                print "Compiling: " + page.className
                self.classAggsClassNames.append(page.className)
                classTemp = TQFRpage.blankTQFR()
                classTemp.setMatchAny()
                classTemp.className = page.className
                aggy = self.compileAgg(classTemp, "class")
                aggy.calculate()
                self.classAggs.append(aggy)
                
    def getStatNames(self, agg, aggType):
        if aggType == "class":
            mine = agg.aggPage.mD
            attrs = mine.__dict__
            statNames = filter(lambda x: isinstance(getattr(mine, x), TQFRpage.statObj), attrs.keys())
        if aggType == "professor":
            mine = agg.aggPage.mD.professorsData[0]
            attrs = mine.__dict__   
            statNames = filter(lambda x: isinstance(getattr(mine, x), TQFRpage.statObj), attrs.keys())
        return statNames
        
    def sortAggListByStat(self, aggList, aggType, statName):
        # aggType = class or professor right now. statName should be a name of a class object.
        if len(aggList) < 1:
            print "No aggregates to sort!"
            return aggList
        if aggType not in ["class", "professor"]:
            print "Unrecognized aggType"
            return aggList
        attrs = self.getStatNames(aggList[0], aggType)
        print attrs
        if not statName in attrs:
            print "invalid statName"
            return aggList
        if aggType == "class":
            aggList.sort(key=lambda x: getattr(x.aggPage.mD, statName).average) #, reverse=True
        return aggList
    
    def sortClaggsBy(self, statName):
        self.classAggs = self.sortAggListByStat(self.classAggs, "class", statName)
        
    # Maybe add an option to display std and quartiles?
    def displayClassAggsStats(self, statNameList):
        if len(self.classAggs) < 1:
            return "No class aggregates loaded..."
        attrs = self.getStatNames(self.classAggs[0], "class")
        for stat in statNameList:
            if not stat in attrs:
                return "stat " + stat + " is not a legit stat"
        display = [["className"] + statNameList]
        for clagg in self.classAggs:
            row = []
            row.append(clagg.aggPage.className)
            for stat in statNameList:
                row.append(getattr(clagg.aggPage.mD, stat).average)
            display.append(row)
        TQFRpage.prettyPrintTable(display)
        return ""
            
                
    def importantNumbers(self):
        numTable = [["Class Name", "under/over uniting", "Hours Outside Class", "Expected Grade", "Pass/fail"]]
        for claAgg in self.classAggs:
            #claAgg.calculate()
            classAgg = claAgg.aggPage
            className = classAgg.className
            workAmountPerception = round(classAgg.mD.workAmountPerception.average, 3)
            hoursOutsideClass = round(classAgg.mD.hoursOutsideClass.average, 3)
            expectedGrade = round(classAgg.mD.expectedGrade.average, 3)
            passFail = round(classAgg.mD.passFail.average, 3)
            numTable.append([className, workAmountPerception, hoursOutsideClass, expectedGrade, passFail])
        TQFRpage.prettyPrintTable(numTable)
    
    
    # ================ User interaction =================
        
    def analyzerCommands(self):
        # Note: Includes stuff I haven't coded up yet!
        # Remember to add new commands to analyzerInstructs, too!
        analyzerCommands = """    Things not yet stable have # in front.
fullLoad
templateLoad
analyzeClass <department1> <number> [termChar] ['prac', 'anal', or nothing]
analyzeProfessor <ProfessorFirstname> <ProfessorLastname>
#analyzeTA <TAfirstName> <TAlastname>
constructClassAggregates | constructClaggs
displayClassAggsStats | claggStats
sortClaggs
analyzeClagg <className, exactly as listed on one of the clagg displays>
importantNumbers
#constructProfessorAggregates
instructions | help | info | information
commands
done"""
        print analyzerCommands
    
    def analyzerInstructs(self):
            print "COMMANDS:"
            # NOT DONE-- And possibly should add TA recommendation.
            # Remember to add new names to "commands" printing too!
            analyzerCommandInstructs = """fullLoad
    Loads basic data on every file you have in your scrapedPages directory that 
    has not already been loaded into the program for analysis. This generally 
    took me about 1 minute/year of classes being loaded.    
templateLoad
    Loads basic data on every file you have in your scrapedPages directory that 
    has not already been loaded, IF it matches a template you will be prompted 
    to construct. Way faster than fullLoad if you're only interested in a 
    subsection of the classes, and not having to go through everything can speed
    up some other things analysis can do as well.           
analyzeClass <department1> <number> [termChar] ['prac', 'anal', or nothing]
    Usage example: analyzeClass Ma 1 A
    Do not include [] things if class does not have them.
    If the class is cross-listed, <department1> can be any of its departments.
    Searches every loaded file for ones that are from that class, consolidates 
    them into an aggregate class, displays data, prompts for further pruning of 
    data if desired.   
analyzeProfessor <ProfessorFirstname> <ProfessorLastname>
    Names should be capitalized and spelled correctly.
    Searches every loaded file for ones that are taught by that professor, 
    consolidates them into an aggregate object, displays data, prompts for 
    further pruning of data if desired.
analyzeTA <TAfirstName> <TAlastname>
    Names should be capitalized and spelled correctly.
    # TODO! -some work done, Ctrl-F taMatches in TQFRpage
    Searches every loaded file for ones that person TA's, consolidates them into
    an aggregate object, displays data, prompts for further pruning of data.    
constructClassAggregates | constructClaggs
    Assigns every loaded page to a ClassAggregate, if it is not already 
    assigned. Very quick. Necessary if you want to search for a class by its 
    aggregate data qualities (e.g., 'quality of content' score).                      
displayClassAggsStats | claggStats
    Prompts you to choose stats, displays them for all constructed class aggs.  
sortClaggs
    Prompts you to choose one stat of interest, sorts all loaded class 
    aggregates and displays sorted list with that agg. List will stay sorted, 
    so later calls to display it will show same thing.
analyzeClagg <className, exactly as listed on one of the clagg displays>
    Does what analyzeClass does, except by picking an already constructed clagg
    from the list. Unlike analyzeClass, analyzeClagg will affect which pages are
    included in the stats displayed for the clagg in 
    claggStats/sortClaggs/importantNumbers etc. Try looking at/excluding the 
    individual pages with this option if you see weird things in the claggStats,
    or just to look at a class in more detail.                                                                         
importantNumbers
    Prints the numbers I look at first for hums for all classAggs constructed.    
constructProfessorAggregates
    # TODO!!!!: 
    Assigns every loaded page to a ProfessorAggregate, if it is not already 
    assigned. Necessary if you want to search for a professor by their aggregate
    data qualities (e.g., 'overall teaching' score).        
instructions | help | info | information
    Prints these instructions again.
commands
    Prints JUST the names and arguments of the valid commands.
done
    Indicates you have finished analyzing and return to main menu.

Typical usage: 
fullLoad -> constructClaggs -> claggStats or sortClaggs or analyzeClagg"""              
            print analyzerCommandInstructs        

    def analyzerChoices(self, choice):
        # View choices
        args = choice.split(" ")
        sT = TQFRpage.blankTQFR() # search template
        sT.setMatchAny()
        message = ""
        helpWords = ["help", "info", "instructions", "information"]
        if choice.lower() in helpWords:
            self.analyzerInstructs()
        elif choice == "commands":
            self.analyzerCommands()        
        elif choice == "fullLoad":
            self.load()
        elif choice == "templateLoad":
            sT.interactiveTemplate()
            self.loadFromTemplate(sT)
        elif len(args) >= 3 and args[0] == "analyzeClass":
            sT.departments = ["GENERAL", args[1]]
            sT.classNum = [int(args[2]), int(args[2])]
            if len(args) > 3:
                if "prac" in args[3] or "anal" in args[3]:
                    sT.pracOrAnal = args[3]
                else:
                    sT.termChar = args[3]
                if len(args) > 4:
                    sT.pracOrAnal = args[4]
                    sT.compileClassNameForFilename() 
            #print sT.toFilename()
            aggy = self.compileAgg(sT, "class")
            aggy.aggLoop()
        elif len(args) == 3 and args[0] == "analyzeProfessor":
            sT.professors = ["GENERAL",  args[1] + " " + args[2]]
            aggy = self.compileAgg(sT, "professor")
            aggy.aggLoop()
        elif len(args) == 3 and args[0] == "analyzeTA":
            print "TODO!"
        elif choice == "constructClassAggregates" or choice == "constructClaggs":
            self.compileAllClassAggs()
        elif choice == "displayClassAggsStats" or choice == "claggStats":
            if len(self.classAggs) > 0:
                print "Legit statNames: "
                print str(self.getStatNames(self.classAggs[0], "class"))
                statDone = False
                statsList = []
                print "Now prompting for stats. Enter statNames EXACTLY as above, or enter 'all' to include all of them."
                print "Otherwise, enter 'done' when finished, 'undo' to remove last statName entered."
                while not statDone:
                    response = raw_input("StatName, all, done, or undo: ")
                    if response == 'all':
                        statDone = True
                        statsList = self.getStatNames(self.classAggs[0], "class")
                    elif response == "done":
                        statDone = True
                    elif response == "undo":
                        if len(statsList) > 0:
                            del statsList[-1]
                        else:
                            "No statnames entered yet."
                    else:
                        statsList.append(response)
                    print "My stats: " + str(statsList)
                print self.displayClassAggsStats(statsList) 
            else:
                print "You have no loaded classAggs. Load some TQFRpages if you haven't already, then constructClaggs."
        elif choice == "sortClaggs":
            if len(self.classAggs) > 0:
                print "Legit statNames: "
                print str(self.getStatNames(self.classAggs[0], "class"))
                stat = raw_input("Enter statname to sort by exactly as above: ")
                self.sortClaggsBy(stat)
                print self.displayClassAggsStats([stat])
            else:
                print "You have no loaded classAggs. Load some TQFRpages if you haven't already, then constructClaggs."
        elif choice[:13] == "analyzeClagg " :
            if choice[13:] in self.classAggsClassNames:
                foundAgg = False
                for clagg in self.classAggs:
                    if clagg.aggPage.className == choice[13:]:
                        foundAgg = True
                        clagg.aggLoop()
                        break
                if not foundAgg:
                    print "Could not find clagg."
            else:
                print "Clagg name not recognized. Here are currently loaded clagg names:"
                print self.classAggsClassNames
        elif choice == "importantNumbers":
            self.importantNumbers()               
        elif choice == "debug":
            sT.departments = ['Ma', 'CS']
            sT.term = 'FA'
            self.loadFromTemplate(sT)
        else :
            message = "Unrecognized command! Note: | means 'or'. Enter 'help' for command names and usage."
        return message
            
    def analyzerLoop(self):
        """Scrapes and analyses data interactively."""
        choice = ''
        message = ''
        #self.load() # just go ahead and load anything new. ...not anymore, this got huge.
        self.analyzerInstructs()
        # The loop
        while not (choice == 'done'):
            print message
            message = ""
            choice = raw_input("[Analyzer] Command: ") 
            args = choice.split(' ')        
            if self.debugOn:
                self.analyzerChoices(choice)
            else:
                try: 
                    self.analyzerChoices(choice)
                except:
                    message = "Unexpected Error! Sorry for the bad message, but I thought you'd prefer this to having to log back in again."
            if choice == "done":
                return 0        


class Aggregate:
    """ Aggregates all data on all pages that fit a certain template. 
    
    Variables:
    debugOn (what kind of errors do I use?)
    aggType: class, professor, or TA. Mostly an identifier. Relevant for class agg construction due to changing full class names :/
    myTemplate: the template the Aggregate is built around. Relevant for the .match.
    myPages: a list of TQFRpage instances, all of the same class/professor/TA.
    included: a list of TQFRpage instances that are CURRENTLY included in the analysis.
    aggPage: a TQFRpage instance that is the aggregate of all pages currently included.
    
    """
    def __init__(self, pagesList, template, aggType):
        # Initialization includes everything, but does not calculate.
        self.debugOn = True
        self.myPages = pagesList
        self.included = [] # Start with everything included
        for page in self.myPages:
            self.included.append(page)
        self.template = template
        self.aggType = aggType
        self.aggPage = template.copy()
        self.aggPage.mD.aggPageInit(pagesList, template.toFilename(), aggType) 
        # the mD gets class name--the FULL class name--from page now.
        # But this version is prettier and more consistent, so give access to it in classNameA:
        for page in self.myPages:
            page.mD.classNameA = page.toFilename()
            
    def tryAddPage(self, page):
        # Adds the page if it matches the template. Returns True if it does, False otherwise.
        # Automatically adds the page to .included. Does not automatically recalculate.
        if page.matches(self.template):
            self.myPages.append(page)
            # the mD gets class name--the FULL class name--from page now.
            # But this version is prettier and more consistent, so give access to it in classNameA:
            page.mD.classNameA = page.toFilename() 
            self.included.append(page)
            return True
        return False
        
    def promptToInclude(self):
        TQFRpage.prettyPrintTable(self.isIncludedTable())
        toInclude = raw_input("Enter which numbers to include, separated by spaces: ").split(' ')
        self.included = []
        for i in toInclude:
            if i.isdigit() and int(i) < len(self.myPages) and int(i) > -1:
                self.included.append(self.myPages[int(i)])
        print ""
        print "New included: "
        TQFRpage.prettyPrintTable(self.isIncludedTable())
    
    def isIncludedTable(self):
        iT = [["#", "In?" , "Identifier"],
              ['--', '-', '---------']]
        for i in range(len(self.myPages)):
            if self.myPages[i] in self.included: 
                incl = "Y"
            else:
                incl = ""
            iT.append([str(i), incl, self.myPages[i].toFilename()])
        return iT
            
    def calculate(self):
        #self.aggPage = template.copy()
        self.aggPage.mD.aggPageInit(self.included, self.template.toFilename(), self.aggType)
        self.aggPage.mD.readAll()
    
    def reportAllData(self, includeComments):
        self.aggPage.mD.reportAllData(includeComments)
    
    aggCommandInstructs = [
        """selectIncluded
            Select which of the aggregate's files should be included in the analysis.""", 
        """calculate
            Calculates and displays data, as calculated from all files in current included list.""",
        """displayComments <Y or N>
            Sets whether to display comments or not.""",        
        """instructions
            Prints these instructions again.""",        
        """done
            Return to main analyzer menu."""] 
        
        
    def aggLoop(self):
        choice = ""
        dc = ''
        message = ''
        displayComments = True
        self.calculate()
        self.reportAllData(displayComments)  
        self.aggInstructs()
        while not (choice == "done"):
            print message
            message = ""
            choice = raw_input("[Aggregate] Command: ") 
            args = choice.split(' ')        
            if self.debugOn:
                if args[0] == "selectIncluded":
                    self.promptToInclude()
                elif args[0] == "calculate":
                    self.calculate()
                    self.reportAllData(displayComments)
                elif args[0] == "displayComments" and len(args) == 2:
                    if args[1] == 'Y':
                        displayComments = True
                    elif args[1] == 'N':
                        displayComments = False
                    else:
                        message = "Unrecognized command! Enter 'instructions' for instructions."
                elif args[0] == "instructions":
                    self.aggInstructs()
                elif args[0] == "debug":
                    print self.myPages
                else:
                    message = "Unrecognized command! Enter 'instructions' for instructions."
            else:
                try: 
                    if args[0] == "selectIncluded":
                        self.promptToInclude()
                    elif args[0] == "calculate":
                        self.calculate()
                        self.reportAllData(displayComments)
                    elif args[0] == "displayComments" and len(args) == 2:
                        if args[1] == 'Y':
                            displayComments = True
                        elif args[1] == 'N':
                            displayComments = False
                        else:
                            message = "Unrecognized command! Enter 'instructions' for instructions."
                    elif args[0] == "instructions":
                        self.aggInstructs()
                    else:
                        message = "Unrecognized command! Enter 'instructions' for instructions."
                except:
                    message = "Unexpected Error! Sorry for the bad message, but I thought you'd prefer this to having to log back in again."
            if choice == "done":
                return 0   
            
    def aggInstructs(self):
        print "COMMANDS: ========"
        for com in self.aggCommandInstructs:
            print com    
            
class Section:
    """ Represents a section of a class. Primarily used through ScheduledClass.
    PROBLEM RIGHT NOW: professor given differently in course schedules.
    Variables:
    sectionNum
    professor
    timeBlocks    Note: also include location.
    gradeScheme"""
    
    def __init__(self, table):
        self.sectionNum = int(table[0][0])
        self.professor = table[0][1]
        # TODO
        
# Not even CLOSE to done!
class ScheduledClass:
    """ Represents schedule data on the class as it WILL be taught/taken this year, 
    as opposed to how it has been taught in the past. 
    Variables:
    
    strings:
    className           e.g. "Ae 100"
    classNum
    termChar
    pracOrAnal
    title               e.g. "Research in Aerospace"  
    
    lists:
    units               Note: not necessarily length 3!
    departments
    sections
    
    The very important list sections is a list of just that. See the class above for its exact contents.
    contains:
    
    
    """
    def __init__(self, table):
        # Class name is 'Ae 100'. title is 'Research in Aerospace'
        self.setClassName(table[0][0])
        self.units = table[0][1].split('-')
        # TODO
        
    # This method was lifted STRAIGHT out of TQFRpage. 
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
    



# The below is debugging and testing that I might want again if I add on to this.

def tableExtract(table):
    # Takes a table tag from BeautifulSoup. Right now does not include empty rows.
    data = []
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        toAppend = [ele for ele in cols if ele] # Get rid of empty values 
        if len(toAppend) > 0:
            data.append(toAppend)
    return data

# THis didn't work out.
def tableExtract2(table):
    # Takes a table tag from BeautifulSoup. Right now does not include empty rows.
    data = []
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        toAppend = [ele.text.strip() for ele in cols]
        # DON'T Get rid of empty values in the hope that it will make registrar  more sensible...
        if len(toAppend) > 0:
            data.append(toAppend)
    return data


"""
print "TEST OOP ====================================="
# tqfr = TQFRpage.tqfrFromFilenameAndPath("BE--167__Michael Elowitz__2015-16__FA__BBE", os.path.join(scrapedPagesPath, "BE--167__Michael Elowitz__2015-16__FA__BBE"))
tqfr = TQFRpage.tqfrFromFilenameAndPath("Ph--127A__Jason Alicea__2015-16__FA__PMA__", os.path.join(scrapedPagesPath, "Ph--127A__Jason Alicea__2015-16__FA__PMA__"))
# tqfr = TQFRpage.tqfrFromFilenameAndPath("BE-Bi-NB--203__Justin Bois_Mitchell Guttman__2015-16__FA__BBE__", os.path.join(scrapedPagesPath, "BE-Bi-NB--203__Justin Bois_Mitchell Guttman__2015-16__FA__BBE__"))

tqfr.mD.printPage(tqfr.mD.sCont)
print "====================================="
tqfr.mD.getTable(tqfr.mD.pCont, "Comments > .+").append(["EXPERIMENT"])
# Experiment worked!
tqfr.mD.printPage(tqfr.mD.pCont)
print "====================================="
tqfr.mD.printPage(tqfr.mD.nCont)


print "====================================="
#print tqfr.mD.hoursOutsideClass.data
#print tqfr.mD.hoursOutsideClass.toString()

tqfr.mD.reportAllData(False)


tqfr.mD.hoursOutsideClass.data = [2, 4, 5]
tqfr.mD.hoursOutsideClass.calculate()

tqfr.mD.reportAllData()
"""

# YESSSSSSSSS it works.
"""
print "TEST AGGREGATE ==========================="
tqfr1 = TQFRpage.tqfrFromFilenameAndPath("Ph--127A__Jason Alicea__2015-16__FA__PMA__", os.path.join(scrapedPagesPath, "Ph--127A__Jason Alicea__2015-16__FA__PMA__"))
tqfr2 = TQFRpage.tqfrFromFilenameAndPath("Ph--127A__Jason Alicea__2014-15__FA__PMA__", os.path.join(scrapedPagesPath, "Ph--127A__Jason Alicea__2014-15__FA__PMA__"))
tqfr3 = TQFRpage.tqfrFromFilenameAndPath("Ph--127A__Olexei Motrunich__2011-12__FA__PMA__", os.path.join(scrapedPagesPath, "Ph--127A__Olexei Motrunich__2011-12__FA__PMA__"))

aggregatePages = [tqfr1, tqfr2]
template42 = TQFRpage.blankTQFR()
template42.setMatchAny() # Not the correct template for this, but only matters for matching...

for page in aggregatePages:
    print "=============================== " + page.toFilename() + " printPage: ==============================="
    page.mD.printPage(page.mD.nCont)
    print "=============================== " + page.toFilename() + " reportAllData: ==============================="
    page.mD.reportAllData(True)
                  
aggy = Aggregate(aggregatePages, template42, template42.toString())
aggy.calculate()

print "=============================== aggy printPage: ==============================="
aggy.aggPage.mD.printPage(aggy.aggPage.mD.nCont)
print "=============================== aggy reportAlllData: ==============================="
aggy.reportAllData(True)


analyzer = TQFRanalyzer(tqfrData)
analyzer.analyzerLoop()
"""