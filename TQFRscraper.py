import requests, os, time
from bs4 import BeautifulSoup
from TQFRpage import *



'''This program scrapes the TQFR database for data. It saves this data
into a folder "TQFRdata" that it will construct in the location of your choice,
if that location does not already have a location with that name.
Data is saved as html files so that any future analysizer can use beautifulSoup.
The accompanying program analyzeTQFRdata.py analyses data you have already 
scraped. '''

class TQFRscraper:
    """ Does the TQFR scraping: communicating with server, etc.
    
    The divisions list is not currently used for anything, because I stopped filling it out halfway through.
    
    vars:
    Static:
    divisions
    baseURL
    scrapeCommandInstructs
    non-static (maybe):
    debugOn
    infoOn
    
    METHODS: ============================================
    __init__(self, dataFolderPath)
    login(self)
    scrapeFromURLtree(self, toScrape, allPages)
    scrapeDataLoop(self)
    
    scrapeInstructs(self)
    searchTQFRpage(self, urlString, myTQFR, toScrape)
    searchDepartmentPage(self, urlString, baseTQFR, toScrape)
    searchDivisionPage(self, urlString, baseTQFR, toScrape)
    searchTermPage(self, urlString, baseTQFR, toScrape)
    """
    
    divisions = ['BBE', 'CHCHE', 'EAS', 'Freshman Seminars', 'GPS', 'HSS', 'PMA', 'Performing Arts', 'Physical Education']
    
    baseURL = "https://access.caltech.edu"
    
    # I don't remember why this is a function.
    def scrapeCommandInstructions(self):
        return """scrapeAll
    Copy every single html file you have not yet scraped
    in the TQFR report system into TQFRdata.
scrapeYear <yearTitle, e.g. "2015-16">
    Copies every html file you do not yet have from that year of TQFRs. 
scrapeClass <department1> <number> [termChar] ['prac', 'anal', or nothing]
    Usage example: scrapeClass Ma 1 A
    Copies every html file you do not yet have that have that number and that 
    department. If the class is cross-listed, <department1> should be the 
    PRIMARY department-the one the class is listed under on the registrar.  
scrapeProfessor <ProfessorFirstname> <ProfessorLastname>
    Copies every html file you do not yet have taught by that professor. Names 
    should be capitalized and spelled correctly.
scrapeAdvanced
    Construct a specific template to match classes to for scraping. 
    Interactively set any of year, term, division, professor, a range of 
    numbers, department, termChar, whether it's practical or analytical, 
    actual classname. Can be SIGNIFICANTLY faster than scrapeClass or 
    scrapeProfessor depending on how much information you specify. Just giving 
    a division can speed things up dramatically, though make sure you're 
    actually writing the division the way it is listed on TQFRs!                      
instructions
    Prints these instructions again.
done
    Indicates you have finished scraping and return to main menu.""" 
    
    debugOn = True
    infoOn = True
    
    def __init__(self, dataFolderPath):
        self.s = requests.Session()
        self.homepageSoup = "Not set until login."
        self.tqfrDataFolder = dataFolderPath
        self.scrapedPagesPath = os.path.join(self.tqfrDataFolder, "scrapedPages") 
        ensureFolder(self.scrapedPagesPath)
        
    
    def login(self):
        # !!!!!!!!!!!!!!!!!!!!!!!!!Change to prompt user for password/username/directory!!!!!!!!!!!!!!!!!
        print ""
        
        username = raw_input("Enter access.caltech.edu username: ")
        password = raw_input("Enter access.caltech.edu password: ")
        
        '''
        username = "YOUR_USERNAME"
        password = "YOUR_PASSWORD"        
        '''
        
        self.s = requests.Session()
        print('Getting login page')
        login_page =  self.s.get('https://access.caltech.edu/auth/login?service=https://access.caltech.edu/tqfr/reports/list_surveys')
        login_page_soup = BeautifulSoup(login_page.text, 'html.parser')
        lt = login_page_soup.form.find(id='lt')['value']
        action = 'https://access.caltech.edu' + login_page_soup.form['action']
        print('Logging in')
        signin_resp = self.s.post(action, data = {'login': username, 'password': password, 'lt': lt})
        
        # If you want you could verify that the login succeded
        
        # But assuming it does, s should now be a signed in session, and
        # signin_resp.text is the tqfr_homepage_html
        baseURL = "https://access.caltech.edu"
        print "Login response will be written to 'login_response', under the TQFRdata folder. If you have weird problems, possibly check this file-you may not have logged in correctly."
        with open(os.path.join(self.tqfrDataFolder, "login_response"), "w") as f:
            f.write(signin_resp.text.encode('utf-8'))
            
        # Make my Soup!
        self.homepageSoup = BeautifulSoup(signin_resp.text, 'html.parser')        

    def getCourseSchedulesPage(self):
        # Gets the course schedules page.
        url = raw_input("Enter the URL for the registrar's course schedules for this term: ")
        regPage =  self.s.get(url)
        with open(os.path.join(self.tqfrDataFolder, "registrarCourseSchedules"), "w") as f:
            f.write(regPage.text.encode('utf-8'))
        courseSoup = BeautifulSoup(regPage.text.encode('utf-8'), 'html.parser')
        print "Success! Probably. Check the file 'registrarCourseSchedules' under the TQFRdata folder if you have reasons to believe this messed up somehow. "
        return (regPage.text, courseSoup) # Note that this is for debugging purposes and should not be used by anything in-program.
        
                  
    
    def searchTQFRpage(self, urlString, myTQFR, toScrape):
        time.sleep(0.3) # wait this long to keep admins from getting mad at us. Hopefully.
        page = self.s.get(urlString)
        #pageSoup = BeautifulSoup(page.text, 'html.parser')
        text = page.text
        texty = text
        professors = []
        while "Instructor Section" in texty:
            index = texty.index("Instructor Section: ")
            area = texty[index:]
            area = area[:area.index("</")]
            professors.append(area[area.index(": ")+2:])
            texty = texty[index + 20:]
        myTQFR.professors = professors
        if myTQFR.matchesAnyOf(toScrape):
            if self.infoOn:
                iMessage("Matched class: " + myTQFR.className)           
            myFilename = os.path.join(self.scrapedPagesPath, myTQFR.toFilename())
            if not os.path.exists(myFilename):
                if len(myFilename) >= 260: # I'm really not sure what to do about this. I didn't know there was a path size limit. I could get around it by having analyzer reset the TQFRpage professors based on the TQFRdata instance's read-in, and having the toFilename method limit itself to so many characters by cutting teachers [except without knowing the path, it wouldn't...no, if I'm going to cut professors from the filename, it should happen right here. And have it add a marker like 'CUTSHORT' to indicate the initFromFileNameAndPath() method that it needs to pull the professors from its TQFRdata instance. Okay, that's how I'll deal with that, but not right now.
                    print "WARNING: PATH TOO LONG FOR WINDOWS: " + myFilename
                    print "CLASS NOT SCRAPED, BECAUSE IT WOULD CRASH THE PROGRAM TO DO SO." # Learned this the hard way...CMS-300 lists all SIXTEEN of its teachers...
                else:
                    with open(os.path.join(self.scrapedPagesPath, myTQFR.toFilename()), "w") as f:
                        f.write(text.encode('utf-8'))    
                return [myTQFR]
            iMessage("Class already in file system-not scraped: " + myTQFR.toString()) # prevents duplicates!
        return [] # ...and also returns if the file isn't scraped.
    
    def searchDepartmentPage(self, urlString, baseTQFR, toScrape):
        pagesToReturn = []
        departmentPage = self.s.get(urlString)  
        departmentPageSoup = BeautifulSoup(departmentPage.text, 'html.parser') 
        tdTags = departmentPageSoup.findAll(attrs={'class' : 'questiondiv'})
        for tdTag in tdTags:
            if len(tdTag.contents) == 3:
                classLinkTag = tdTag.contents[1]
                myTQFR = baseTQFR.copy()
                myTQFR.url = self.baseURL + classLinkTag["href"]
                myTQFR.setClassName(classLinkTag.contents[0]) # myTQFR is no longer a template!
                if self.debugOn:
                    dMessage(myTQFR.toFilename())
                if myTQFR.matchesAnyOf(toScrape):               
                    pagesToReturn += self.searchTQFRpage(self.baseURL + classLinkTag["href"], 
                                                    myTQFR, toScrape)            
        return pagesToReturn     
    
    def searchDivisionPage(self, urlString, baseTQFR, toScrape):
        # Returns a list of TQFRpage objects corresponding to the pages in a division for a given term and year, as given through the url string.
        # Note that I CANNOT in general check for department matches here, because cross-listed items are NOT listed under every department they are cross-listed in,
        # only one of them.
        # I also cannot check here because they write the full name here and only the abbreviation with the class page. 
        pagesToReturn = []
        divisionPage = self.s.get(urlString)  
        divisionPageSoup = BeautifulSoup(divisionPage.text, 'html.parser') 
        tdTags = divisionPageSoup.findAll(attrs={'class' : 'questiondiv'}) 
        for tdTag in tdTags:
            if len(tdTag.contents) == 3:
                departmentLinkTag = tdTag.contents[1]
                pagesToReturn += \
                    self.searchDepartmentPage(self.baseURL + departmentLinkTag["href"], 
                                         baseTQFR, toScrape)            
        return pagesToReturn   
    
    
    def searchTermPage(self, urlString, baseTQFR, toScrape):
        # Returns a list of all tqfr pages found in a term for a given year, as given through the url string.
        pagesToReturn = []
        termPage = self.s.get(urlString)
        termPageSoup = BeautifulSoup(termPage.text, 'html.parser') 
        tdTags = termPageSoup.findAll(attrs={'class' : 'questiondiv'})
        for tdTag in tdTags:
            if len(tdTag.contents) == 3:
                divisionLinkTag = tdTag.contents[1]
                baseTQFR.division = divisionLinkTag.contents[0]
                if baseTQFR.matchesAnyOf(toScrape):
                    pagesToReturn += self.searchDivisionPage(self.baseURL + divisionLinkTag["href"], 
                                                             baseTQFR, toScrape)            
        return pagesToReturn
    
    def scrapeFromURLtree(self, toScrape):
        """
        ONLY LOOKS at TQFR pages that match something in the list of TQFRpages toScrape.
        Matches determined by 
        documents EVERY tqfr url in TQFRurls.txt in the following form:
        Year\tTerm\tDepartment\tClass\tProfessor\tURL
        Also returns a list of TQFRpage items, and scrapes any that match anything 
        in the list of TQFRpages "toScrape".
        """
        pagesToReturn = []
        yearTags = self.homepageSoup.find_all('h1')
        linkTags = self.homepageSoup.find_all('a')
        print "finding years"
        baseTQFR = blankTQFR()
        for yearTag in yearTags:
            baseTQFR = blankTQFR()
            baseTQFR.setMatchAny()
            yearName = yearTag.contents[0]
            baseTQFR.year = yearName
            if baseTQFR.matchesAnyOf(toScrape):
                if self.infoOn:
                    iMessage("matched year: " + yearName)
                (fallLink, winterLink, springLink) = ("FA " + yearName, "WI " + yearName, "SP " + yearName)
                terms = {fallLink : "FA", winterLink: "WI", springLink: "SP"}           
                #print baseTQFR.toString()
                for linkTag in linkTags:
                    if linkTag.contents[0] in terms:
                        baseTQFR.term = terms[linkTag.contents[0]]
                        if baseTQFR.matchesAnyOf(toScrape):
                            if self.infoOn:
                                iMessage("Matched term: " + baseTQFR.term)
                            base = baseTQFR.copy() # searchTermPage alters the baseTQFR passed to it.
                            pagesToReturn += self.searchTermPage(self.baseURL + linkTag["href"], base, toScrape)
        return pagesToReturn
        
    # Scrape data interactively ===============================
    def scrapeInstructs(self):
        print """Note: if you have a bad data file, you should delete it so the scrapers will re-scrape it."""
        print """WARNING: scraping can take some time, as access.caltech will kick us out if we request pages too quickly. Also note that scraping by professor is only very slightly faster than scraping everything, since the professor's name can only be obtained by requesting the actual page (we can't cut the search tree short). So the only reason to use scrapeProfessor is if you don't want to take too much space. """
        # SHOULD NOTE HOW BIG AVERAGE TQFR PAGE IS in kilobytes. Also note how big average YEAR is!
        print "COMMANDS:"
        print self.scrapeCommandInstructs()          
    
    def scraperChoices(self, choice, sT):
        args = choice.split(' ')
        message = ''
        helpWords = ["help", "info", "instructions", "information"]
        if choice.lower() in helpWords:
            self.scrapeInstructs()
        elif choice == "scrapeAll":
            self.scrapeFromURLtree([sT])
        elif choice == "scrapeAdvanced":
            sT.interactiveTemplate()
            self.scrapeFromURLtree([sT])
        elif len(args) == 2 and args[0] == "scrapeYear":
            sT.year = args[1]  
            self.scrapeFromURLtree([sT])
        elif len(args) >= 3 and args[0] == "scrapeClass":
            sT.departments = ["GENERAL", args[1]]
            sT.classNum = [int(args[2]), int(args[2])]
            if len(args) > 3:
                if "prac" in args[3] or "anal" in args[3]:
                    sT.pracOrAnal = args[3]
                else:
                    sT.termChar = args[3]
                if len(args) > 4:
                    sT.pracOrAnal = args[4]
            self.scrapeFromURLtree([sT])
        elif len(args) == 3 and args[0] == "scrapeProfessor":
            sT.professors = ["GENERAL", args[1] + " " + args[2]]
            self.scrapeFromURLtree([sT])
        elif len(args) == 2 and args[0] == "debug":
            print "nothing right now!"
        elif not args[0] == "done" :
            print "Unrecognized command!"
        return message

    def scrapeDataLoop(self):
        """Scrapes Data interactively."""
        choice = ''
        message = ''
        self.scrapeInstructs()
        sT = blankTQFR() # search template
        allPages = []
        # The loop
        while not (choice == 'done'):
            print message
            message = ""
            choice = raw_input("[Scraping] Command: ") 
            sT.setMatchAny()
            # View choices
            if self.debugOn:
                message = self.scraperChoices(choice, sT)
            else:
                try: 
                    message = self.scraperChoices(choice, sT)
                except:
                    message = "Unexpected Error! Sorry for the bad message, but I thought you'd prefer this to having to log back in again."     
            #print sT.toString()
            if choice == "done":
                return allPages               





                                                                                       



