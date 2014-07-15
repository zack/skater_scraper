from __future__ import division
from os import system
from sys import stdout
from math import ceil
from time import time
from json import dumps
from time import sleep
from bs4 import BeautifulSoup
from datetime import timedelta
from session import SessionManager
from urllib2 import Request, urlopen

# Global constants
SESSION_MANAGER = SessionManager()
BASE_URI = 'https://www.wftda.com'
START = time()

# Request data vars
total_reqs = 0
reqs = []
last_req_idx = -1
req_debug = []

# Count data vars
skater_count = 0
team_count = 0 # Increment for every team
roster_count = 0 # Increment for every team roster with skaters
roster_empty_count = 0
league_count = 0
total_league_count = 358 # At time of writing...
apprentice_league_page_count = 7 # At time of writing...
member_league_page_count = 14 # At time of writing...

def main():
    global league_count
    global total_league_count
    get_cookie()
    update_league_counts()
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

    skaters = {'timestamp': time(), 'skaters': skaters}
    f = open('skaters.json', 'w')
    f.write(dumps(skaters, indent=4))
    f.close()

    dur = time() - START
    dur_m = dur//60
    dur_s = dur%60

    result = ('Found %i skaters on %i rosters on %i teams from %i leagues'
              ' with %i empty rosters.                       '
             % (skater_count, roster_count, team_count,
                league_count, roster_empty_count))
    stdout.write(result + '\n')
    stdout.flush()
    print ('Completed using %i requests in %i minutes and %i seconds.' %
          (total_reqs, dur_m, dur_s))

# Update cookie used for authentication
# ->
def get_cookie(update=False):
    global cookie
    if update:
        SESSION_MANAGER.update_cookie()
    cookie = 'wftda_session=%s' % SESSION_MANAGER.get_session_id()

# Because status bars are important, dammit.
def update_league_counts():
    global apprentice_league_page_count
    global member_league_page_count
    global total_league_count

    member_uri = 'https://wftda.com/dashboard/leagues/member-leagues'
    apprentice_uri = 'https://wftda.com/dashboard/leagues/apprentice-leagues'
    html = uopen(member_uri).read()
    soup = BeautifulSoup(html, 'lxml')
    m_league_count = int(soup.find('li', 'selection').a.text.split(" ")[0])

    member_league_page_count = int(ceil(m_league_count / 20))

    html = uopen(apprentice_uri).read()
    soup = BeautifulSoup(html, 'lxml')
    a_league_count = int(soup.find('li', 'selection').a.text.split(" ")[0])

    apprentice_league_page_count = int(ceil(a_league_count / 20))

    total_league_count = m_league_count + a_league_count

# Update the command line with the current status of the process
def update_status(status, wait=0):
    percent_finished = float(league_count) / total_league_count * 100
    if status == 'throttling':
        status += ' (%is)' % wait
    elapsed = str(timedelta(seconds=time() - START))
    status = ('%i skaters | %i teams | %i leagues | %d%% | %s | status: %s' %
             (skater_count, team_count, league_count,
                 percent_finished, elapsed, status))
    stdout.write(status + '                    \r')
    stdout.flush()

# No more than 60 requests per minute
def uopen(uri):
    global total_reqs
    global reqs
    global last_req_idx

    if len(reqs) < 60:
        # Just add the request time to the list
        reqs.append(time())
    else:
        # This is the index of time of the request from 60 requests ago
        test_req_idx = (last_req_idx + 1) % 60
        # Duration between now and time of the request 60 requests ago
        dur = time() - reqs[test_req_idx]

        while dur < 60:
            wait = 60-dur
            update_status('throttling', wait)
            sleep(1)
            dur = time() - reqs[test_req_idx]
        # Replace the oldest request time with the current time
        reqs[test_req_idx] = time()

    # Update the last request index
    last_req_idx = ((last_req_idx + 1) % 60)
    total_reqs += 1
    update_status('working')
    req = Request(uri, headers={'Cookie' : cookie})
    resp = urlopen(req)
    while 'login' in resp.geturl():
        update_status('reauthenticating')
        get_cookie(True)
        req = Request(uri, headers={'Cookie' : cookie})
        resp = urlopen(req)
    else:
        update_status('working')
    return resp

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
    for i in range(1, member_league_page_count+1):
        uri = 'https://wftda.com/dashboard/leagues/member-leagues?page=%i' % i
        league_uris.extend(get_league_uris_by_page(uri))
    return league_uris

# -> List
# Returns a list of all apprentice league URIs
def compile_apprentice_league_uris():
    league_uris = []
    # Want a full set of data, or no?
    for i in range(1, apprentice_league_page_count+1):
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
    spans = soup.find('div', 'leagueHeader').findAll('span')
    if len(spans) >= 1:
        loc = spans[-1].get('title', '').split('-')
    if len(loc) == 2:
        location = {
            'country' : loc[0],
            'city': loc[1].title()
        }
    elif len(loc) == 3:
        location = {
            'country' : loc[0],
            'state/province': loc[1],
            'city' : loc[2].title()
        }
    elif len(loc) == 4:
        location = {
            'country' : loc[0],
            'state/province': loc[1],
            'city' : loc[2].title() + '-' + loc[3].title()
        }
    else:
        location={'country':'','state/province':'','city':''}
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

    global team_count
    team_count += 1

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
        skater = {}
        # Sometimes there's extra name text. If so, keep elsewhere and clear.
        span = row.a.find('span')
        if span:
            supplemental = span.text.encode('ascii', 'ignore')
            skater.update({'skater_name_supplemental': supplemental})
            span.clear()
        skater_name = row.a.text.encode('ascii', 'ignore')
        skater_number = row.find('td').text.encode('ascii', 'ignore')
        position = row.findAll('td')[2].text.encode('ascii', 'ignore')
        skater.update({'skater_name': skater_name})
        skater.update({'skater_number': skater_number})
        skater.update({'skater_teams': [team_data]})
        # Some skaters have a position (Captain)
        if position:
            skater.update({'position': position})
        skater.update(league_data)
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

system('tput civis')
try:
    main()
except:
    stdout.flush()
finally:
    system('tput cnorm')
