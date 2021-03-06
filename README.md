# TQFRanalysis BETA 
A project that helps with course planning by pulling data
from the TQFRs website, and analyzing it.




<h2>Capabilities</h2>

1. Scraping pages from the TQFR system matching any number of year, term,
professor(s), a range of numbers, department, A/B/C designations, whether it's
practical or analytical, or by actual classname in their system.

2. Aggregating and displaying data on a class or professor from files you have
scraped, and displaying a number of analytics on said aggregate, including the
mean, standard deviation, number respondents and quartiles for basically any
numerical data collected by TQFRs. It will also allow you to select which of the
pages to include in the aggregate, and recalculate based on that.

3. Constructing class aggregates for all TQFRpages currently loaded. Displaying
statistics on numerical values for those classes. Sorting by one of those
numerical values, and redisplaying. Doing everything in item # 2 for individual
classes within this list. (Note: Some classes may not have a certain metric for
all of its pages, perhaps because it was a pass-fail only class for some of them
and thus doesn't report expected grade, or in one year no students submitted
data for that metric. In this case, the aggregate will say there is no data
rather than reporting the average of the pages that do have it. Selecting
individual years in the aggregate menu for the class will work around this.)

<h2>Requirements</h2>

TQFRscraper is written in Python 2.7. It requires the following non-standard
library packages: 
* [bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [requests](https://pypi.python.org/pypi/requests)
* [numpy](http://www.numpy.org/)

If you have pip, these are easily installable with
```
py -2 -m pip install <packagename>
```

You must have an internet connection and an access.caltech username and password
to pull new data. The project includes pages that I've already scraped, as well,
if you just want to use the analysis part.




<h2>Project structure overview</h2>

Files:

======= runThisOne.py

Initializes the TQFRscraper and TQFRanalyzer classes, sets debugOn on or off,
and runs the main menu.

======= TQFRpage.py

Contains some utility functions (like prettyPrintTable and ensureFolder) and a
number of classes used to represent TQFR pages and associated data for both
TQFRscraper and TQFRanalyzer. 



Classes:
* TQFRpage
    * Represents EITHER a TQFRpage file, or a template TQFR page that you can 
	  match actual instances or other templates to, for use in sorting.
    * Notes year, term, division, className, termChar (A/B/C, I.e. which set of
	  a class it is, not necessarily which term it is given in), 
	  classNameForFileName (standardized), url, pracOrAnal, classNum, professors,
	  departments.
    * Contains a TQFRdata instance, though it doesn't necessarily do anything 
	  with it; the scraper doesn't, anyway. Its most important methods are 
	  probably initFromFilenameAndPath(self, filename, path), setMatchAny(self),
	  copy(self), and especially matches(self, other).
* TQFRdata
    * A large class that represents the actual contents of a TQFR page. The big
      difference between it and TQFRpage is whether you want to bother with 
	  stripping data out of the tables (sometimes you don't.).
    * Contains the methods for actually scanning a scraped file and inputting a
      representation of all the data on the page. 3 of them, actually; sCont, 
	  pCont, and nCont, though I should probably get rid of that middle one, I'm 
	  not using it like I thought I would. It then sorts this data into a bunch 
	  of containers, many of which are or contain...
* StatObj
    * A small class that stores a data set of integers or floats plus some 
	  statistical information on them and methods for presenting it.
* ProfessorData
    * A container class for the 'Instructor Section' part of a TQFR page. 
	  TQFRdata stores a list of them, which could have anywhere from 0 (PA16A 
	  Cooking Basics) to 16 (CMS300 Research in Computing and Mathematical 
	  Sciences) professors (or more, if I find a class with more Instructor
	  Sections...though in fact right now it can't have a 16-professor class, 
	  because the filename needed to read it in is above Windows' 260-character 
	  path limit. I have some ideas for getting around this without huge 
	  restructuring, but given that there is only one respondent to that class,
	  it's not a huge priority.).
* TAdata
    * A container class for the 'Teaching Assistant Section' of a TQFR page. 
	  TQFRdata stores a list of them, exactly as it does for professors. It 
	  would be pretty easy to make it possible to scrape and aggregate by TA;
	  the way the classes are set up, I would mostly just be copying bits of 
	  code I wrote for professors and changing some regular expressions and 
	  variable names.

======= TQFRscraper.py

One class:

* TQFRscraper	  
    * Handles login and scraping.
	  
======= TQFRanalyzer.py

Classes:

* TQFRanalyzer
    * The main analyzing program, that contains methods to let you interactively
      create Aggragates and view data on them. It is the one that messes with 
	  the TQFRdata object in each TQFRpage; TQFRscraper just looks at TQFRpage. 
	  Speaking of aggregates...
* Aggregate
    * A class that aggregates TQFRdata instances, and contains a menu that lets
	  the user manipulate its contents. Mostly for easy manipulation of packs of
	  TQFRpage instances where you care about the TQFRdata part, it is set up to
	  be quite flexible: you give it a bunch of pages, it scans them all, and 
	  keeps all the tables that are present in all of the given pages (actually, 
	  a lot of this is done with methods in TQFRdata, because Aggregate's most 
	  important class variable is a TQFRpage instance named aggPage, but Aggregate
	  orchestrates it.). So you don't have to tell it what kind of aggregate 
	  you're trying to make; if you give it six pages of the same class, it will
	  report back data on that class and nothing else (unless somebody has 
	  taught/TA'd it in all six of those years, in which case you probably want to
	  know that anyway.).

<h2> Possible future development </h2>

<h3>Relatively quick </h3>

* Reading in files with tons of professors without making windows complain.
* Being able to scrape and aggregate by TA.

<h3>More lengthy</h3>

* Being able to search for professors/TAs by their statistical quantities, e.g.
  "Average overall class rating > X".
* Construct a list of any number of professors/TA's and rank them by statistical
  quantities (okay, this one is more a curiosity than actually super useful.).
* [In development] Being able to scrape data from the registrar's course page, so
  that it knows which classes are available this term, and taught by whom...
* ...so I can use that data to write functions like "Tell me how many units this
  schedule ACTUALLY is" or "Find a Hum of number 200 or above that fits in this
  schedule that involves less than 6 hours of work outside of class when taught by
  the professor it's going to be taught by this term." Honestly, just "list all
  Hums and SS's that fit in this schedule that don't have horrible TQFR ratings"
  would be a nice thing to have.

<h2> Other notes </h2>

<h3>Program time note</h3> 

Scraping can take a long time, because access.caltech
will kick you out if you request too many pages too quickly. Further, since the
numbers they use in the URL were nonsensical (at time of program creation), the
program navigates the file tree instead of just straight up requesting class X:
so if you're searching by a quantity that is only displayed in the TQFRpage
(like professor), it has to actually request every single page in all of TQFRs
if you aren't giving it any other information to narrow things down (the
advancedScrape option is GREAT for this if you know your professor only teaches
in a certain division or just a few departments).

<h3> Historical note </h3>

TQFR scraper was first uploaded to Github when it was first developed in
September 2016. However, this first commit is not noted on Git because I somehow
uploaded it without actually making the code on my laptop a Git repository.