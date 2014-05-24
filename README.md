WFTDA Database Scraper
======================

This script can be used to scrape the exposed skater database
found at [http://www.wftda.com/dashboard](wftda.com/dashboard).

It will compile a list of skaters that, at time of writing,
is roughly 8000 strong. The compiled list is currently about
5MB in size. There are some things worth noting:

  * Dependencies include:
    * [xmlx.html](lxml.de/lxmlhtml.html)
    * [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/)
  * This script requires a wftda.com username and password
  * The script has built-in request throttling to 60/min.
    * **Please do not remove this!**

Addtionally, each skater's dataset includes:

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

Example (used with permission):
    <pre><code>
    {
        "league_region": "East",
        "skater_number": "B4",
        "wftda_uri": "https://wftda.com/dashboard/leagues/detail/mu7sm8zfdeiq",
        "skater_name_supplemental": "Ever Been Slapt",
        "skater_name": "Evabyn Slapt",
        "team_uri_list": "https://www.wftda.com/dashboard/teams/list/mu7sm8zfdeiq",
        "league_name": "Boston Derby Dames",
        "league_location": {
            "State/Province": "MA",
            "Country": "United States",
            "City": "Boston"
        },
        "skater_teams": [
            {
                "team_name": "Boston B-Party",
                "team_roster_uri": "https://www.wftda.com/dashboard/teams/roster/mu7sm8zfdeiq/2",
                "team_type": "Travel Team"
            },
            {
                "team_name": "Wicked Pissahs",
                "team_roster_uri": "https://www.wftda.com/dashboard/teams/roster/mu7sm8zfdeiq/5",
                "team_type": "Home Team"
            }
        ],
        "league_status": "Member"
    }
    </code></pre>

Thanks for reading!

You++

Official

Boston Derby Dames
