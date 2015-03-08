# WFTDA Database Scraper

This script can be used to scrape the exposed skater database
found at [http://www.wftda.com/dashboard](http://wftda.com/dashboard).

It will compile a list of skaters that, at time of writing,
is roughly 8000 strong. The compiled list is currently about
5MB in size. There are some things worth noting:

  * Dependencies include:
    * [lxml.html](http://lxml.de/lxmlhtml.html)
    * [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/)
  * This script requires a wftda.com username and password
  * The script has built-in request throttling to 60/min.

Each skater's entry includes:

  * Skater Name
  * Skater Supplementary Name Information (Optional)
  * Skater Position (e.g. Captain; Optional)
  * Skater Number
  * League Name
  * League Region
  * League Location
  * League Status (Member/Apprentice)
    * City
    * State/Province (if applicable)
    * Country
  * Skater Teams (A skater may be on more than one team)
    * Team Name
    * Team Roster URI (the URI for them roster in the dashboard)
    * Team Type (Charter, Travel, or Home)
  * WFTDA URI (the URI for the league in the dashboard)

Thanks for reading!
