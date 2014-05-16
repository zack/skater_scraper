import urllib
import urllib2
import json
import time
import sys
from session import get_session_id
from bs4 import BeautifulSoup

SMALL = True

# Global constants
BASE_URI = 'https://www.wftda.com'
COOKIE = 'wftda_session=%s' % get_session_id()
HEADERS = {'Cookie' : COOKIE}
START = time.time()

# Request data vars
total_reqs = 0
reqs = []
last_req_idx = -1
req_debug = []

# Count data vars
skater_count = 0
roster_count = 0
roster_empty_count = 0
league_count = 0
total_league_count = 358 # At time of writing...

def main():
    global league_count
    global total_league_count
    total_league_count = update_total_league_count()
    update_status('working')

    skaters = []
    for league_uri in compile_all_league_uris():
        league_skaters = []
        league_data = get_league_data(league_uri)
        for team_data in get_league_teams_data(league_data['team_uri_list']):
            roster = get_team_roster(
                        team_data['team_roster_uri'],
                        league_data, team_data
                     )
            if roster:
                for skater in roster:
                    add_skater_to_list(skater, league_skaters)
        skaters.extend(league_skaters)
        league_count += 1

    f = open('skaters', 'w')
    f.write(json.dumps(skaters, indent=4))
    f.close()

    dur = time.time() - START

    result = ('Found %i skaters on %i teams from %i leagues '
              'with %i empty rosters.'
          % (skater_count, roster_count, league_count, roster_empty_count))
    sys.stdout.write(result + '\n')
    sys.stdout.flush()
    print 'Completed using %i requests in %i seconds.' % (total_reqs, dur)

# Because status bars are important, dammit.
def update_total_league_count():
    member_uri = 'https://wftda.com/dashboard/leagues/member-leagues'
    apprentice_uri = 'https://wftda.com/dashboard/leagues/apprentice-leagues'
    html = uopen(member_uri).read()
    soup = BeautifulSoup(html, 'lxml')

    m_league_count = int(soup.find('li', 'selection').a.text.split(" ")[0])

    html = uopen(apprentice_uri).read()
    soup = BeautifulSoup(html, 'lxml')

    a_league_count = int(soup.find('li', 'selection').a.text.split(" ")[0])

    return m_league_count + a_league_count


# Update the command line with the current status of the process
def update_status(status, wait=0):
    percent_finished = float(league_count) / total_league_count * 100
    if status == 'throttling':
        status = 'throttling (%is)' % wait
    status = (' %i skaters | %i teams | %i leagues | %d%% | status: %s' %
             (skater_count, roster_count, league_count,
                 percent_finished, status))
    sys.stdout.write(status + '                    \r')
    sys.stdout.flush()

# No more than 60 requests per minute
def uopen(uri):
    global total_reqs
    global reqs
    global last_req_idx

    if len(reqs) < 60:
        # Just add the request time to the list
        reqs.append(time.time())
    else:
        # This is the index of time of the request from 60 requests ago
        test_req_idx = (last_req_idx + 1) % 60
        # Duration between now and time of the request 60 requests ago
        dur = time.time() - reqs[test_req_idx]

        while dur < 60:
            wait = 60-dur
            update_status('throttling', wait)
            time.sleep(1)
            dur = time.time() - reqs[test_req_idx]
        # Replace the oldest request time with the current time
        reqs[test_req_idx] = time.time()

    # Update the last request index
    last_req_idx = ((last_req_idx + 1) % 60)
    total_reqs += 1
    update_status('working')
    req = urllib2.Request(uri, headers=HEADERS)
    return urllib2.urlopen(req)

# String -> List
# Takes a URI for a leagues search result and returns
# a list of all league URIs on the page
def get_league_uris_by_page(league_list_page):
    # Get the page
    html = uopen(league_list_page).read()
    soup = BeautifulSoup(html, 'lxml')

    # Get the URIs
    leagues = soup.findAll('a', 'tableLeagueLinkThumb')
    league_uris = [BASE_URI + a['href'] for a in leagues]
    return league_uris

# -> List
# Returns a list of all member league URIs
def compile_member_league_uris():
    league_uris = []
    # Want a full set of data, or no?
    s = 13 if SMALL else 1
    for i in range(s,14):
        uri = 'https://wftda.com/dashboard/leagues/member-leagues?page=%i' % i
        league_uris.extend(get_league_uris_by_page(uri))
    return league_uris

# -> List
# Returns a list of all apprentice league URIs
def compile_apprentice_league_uris():
    league_uris = []
    # Want a full set of data, or no?
    s = 6 if SMALL else 1
    for i in range(s,7):
        uri = ('https://wftda.com/dashboard/leagues/apprentice-leagues?page=%i'
              % i)
        league_uris.extend(get_league_uris_by_page(uri))
    return league_uris

# -> List
# Returns a list of all league URIs
def compile_all_league_uris():
    apprentice = compile_apprentice_league_uris()
    members = compile_member_league_uris()
    members.extend(apprentice)
    return members

# String -> Dictionary
# Takes a league page URI and returns a dictionary of relevant info
# Includes: Name, Membership Status, Location, Region
def get_league_data(league_page_uri):
    league_data = {'wftda_uri': league_page_uri}

    # Get the page
    html = uopen(league_page_uri).read()
    soup = BeautifulSoup(html, 'lxml')

    # Get league name
    name = soup.find('h1').text.encode('ascii', 'ignore')
    league_data['league_name'] = name

    # Get league location
    # Titling cities because some are all caps and that's annoying
    loc = (soup.find('div', 'leagueHeader')
              .findAll('span')[-1]['title'].split('-'))
    if len(loc) == 2:
        location = {
            'Country' : loc[0],
            'City': loc[1].title()
        }
    elif len(loc) == 3:
        location = {
            'Country' : loc[0],
            'State/Province': loc[1],
            'City' : loc[2].title()
        }
    elif len(loc) == 4:
        location = {
            'Country' : loc[0],
            'State/Province': loc[1],
            'City' : loc[2].title() + '-' + loc[3].title()
        }
    else:
        print "Unexpected hyphens in header location"
        raise
    league_data['league_location'] = location

    # Get league membership status and region (since they're in the same tag)
    league_info = (soup.find('div', 'columnThird').
                      findNext('div', 'columnThird').
                      p.text.encode('ascii', 'ignore'))
    league_info = [data.strip() for data in
                      league_info.split('\n') if data != '']
    league_data['league_status'] = league_info[0].split(' ')[1]
    league_data['league_region'] = league_info[1].split(' ')[0]

    # Get uri to teams list
    league_team_uri_list = (soup.findAll('div', 'columnThird')[1].
                               findAll('a')[4]['href'])
    league_data['team_uri_list'] = BASE_URI + league_team_uri_list

    return league_data

# String -> List of Dictionaries
# Takes the team page of a league and returns a dictionary of the teams' data
def get_league_teams_data(league_teams_page_uri):
    # Get the page
    html = uopen(league_teams_page_uri).read()
    soup = BeautifulSoup(html, 'lxml')

    rows = soup.findAll('tr', 'even')
    rows.extend(soup.findAll('tr', 'odd'))

    teams = []
    for row in rows:
        team_name = row.td.a.text.encode('ascii', 'ignore')
        team_type = row.findAll('td')[1].text.encode('ascii', 'ignore')
        team_roster_uri = (row.findAll('a')[-1]['href'].
                              encode('ascii', 'ignore'))
        team = {
            'team_name': team_name,
            'team_type': team_type,
            'team_roster_uri': BASE_URI + team_roster_uri
        }
        teams.append(team)

    return teams
# String -> Dictionary
# Takes a team roster URI and returns a list of skaters
# A skater is a dictionary
def get_team_roster(roster_uri, league_data, team_data):
    # Get the page
    html = uopen(roster_uri).read()
    soup = BeautifulSoup(html, 'lxml')

    # Check for no roster
    if 'No skaters' in (soup.find('div', {'id': 'pageContent'}).
                           findAll('p')[-1].text):
        global roster_empty_count
        roster_empty_count += 1
        return
    global roster_count
    roster_count += 1

    # Get the rows
    rows = soup.findAll('tr', 'alignMiddle')

    # Get the skaters
    skaters = []
    for row in rows:
        skater_number = row.find('td').text.encode('ascii', 'ignore')
        skater_name = row.a.text.encode('ascii', 'ignore')
        position = row.findAll('td')[2].text.encode('ascii', 'ignore')
        skater = {
            'skater_name': skater_name,
            'skater_number': skater_number,
            'skater_teams': [team_data]
        }
        skater.update(league_data)
        if position:
            skater.update({'position': position})
        skaters.append(skater)
    global skater_count
    skater_count += len(skaters)
    return skaters

# Dict, List -> List
# Takes a list of skaters and a skater and combine the skaters
# with the list, merging skaters of the same number.
# This is necessary due to the fact that some skaters may
# be rostered on multiple teams within a league.
def add_skater_to_list(skater, ls):
    for s in ls:
        if s['skater_number'] == skater['skater_number']:
            s['skater_teams'].extend(skater['skater_teams'])
            return
    ls.append(skater)
    return

main()
