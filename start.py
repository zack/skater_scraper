import urllib
import urllib2
import json
from bs4 import BeautifulSoup

SMALL = True

BASE_URI = 'https://www.wftda.com'
COOKIE = 'fill me in'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
REFERER = 'https://wftda.com/dashboard/teams/list/9xdnvp4h1tvs'
HEADERS = {'User-Agent' : USER_AGENT, 'Cookie' : COOKIE}

# String -> List
# Takes a URI for a leagues search result and returns a list of all league URIs on the page
def get_league_uris_by_page(league_list_page):
  # Get the page
  req = urllib2.Request(league_list_page, headers=HEADERS)
  html = urllib2.urlopen(req).read()
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
    uri = 'https://wftda.com/dashboard/leagues/member-leagues?page=%i' % (i, )
    league_uris.extend(get_league_uris_by_page(uri))
  return league_uris

# -> List
# Returns a list of all apprentice league URIs
def compile_apprentice_league_uris():
  league_uris = []
  # Want a full set of data, or no?
  s = 6 if SMALL else 1
  for i in range(s,7):
    uri = 'https://wftda.com/dashboard/leagues/apprentice-leagues?page=%i' % (i, )
    league_uris.extend(get_league_uris_by_page(uri))
  return league_uris

# -> List
# Returns a list of all league URIs
def compile_all_league_uris():
  apprentice = compile_all_apprentice_league_uris()
  members = compile_all_member_league_uris()
  members.extend(apprentice)
  return members

# String -> Dictionary
# Takes a league page URI and returns a dictionary of relevant info
# Includes: Name, Membership Status, Location, Region
def get_league_data(league_page_uri):
  league_data = {'wftda_uri': league_page_uri}

  # Get the page
  req = urllib2.Request(league_page_uri, headers=HEADERS)
  html = urllib2.urlopen(req).read()
  soup = BeautifulSoup(html, 'lxml')

  # Get league name
  name = soup.find('h1').text.encode('ascii', 'ignore')
  league_data['league_name'] = name

  # Get league location
  loc = soup.find('div', 'leagueHeader').findAll('span')[2]['title'].split('-')
  if len(loc) == 3:
      location = {'Country' : loc[0], 'State/Province': loc[1], 'City' : loc[2]}
  if len(loc) == 2:
      location = {'Country' : loc[0], 'City': loc[1]}
  league_data['league_location'] = location

  # Get league membership status and region (since they're in the same tag)
  league_info = soup.find('div', 'columnThird').findNext('div', 'columnThird').find('p').text.encode('ascii', 'ignore')
  league_info = [data.strip() for data in league_info.split('\n') if data != '']
  league_data['league_status'] = league_info[0].split(' ')[1]
  league_data['league_region'] = league_info[1].split(' ')[0]

  # Get uri to teams list
  league_team_uri_list = soup.findAll('div', 'columnThird')[1].findAll('a')[4]['href']
  league_data['team_uri_list'] = BASE_URI + league_team_uri_list

  return league_data

# String -> Dictionary
# Takes the team page of a league and returns a dictionary of the teams' data
def get_league_teams_data(league_teams_page_uri):
  # Get the page
  req = urllib2.Request(league_teams_page_uri, headers=HEADERS)
  html = urllib2.urlopen(req).read()
  soup = BeautifulSoup(html, 'lxml')

  rows = soup.findAll('tr', 'even')
  rows.extend(soup.findAll('tr', 'odd'))

  teams = []
  for row in rows:
    team_name = row.td.a.text.encode('ascii', 'ignore')
    team_type = row.findAll('td')[1].text.encode('ascii', 'ignore')
    team = {
        'team name': team_name,
        'team type': team_type
        }
    teams.append(team)

  return teams
# String -> Dictionary
# Takes a team roster URI and returns a dictinoary of skaters
def get_team_roster(roster_uri, league_data, team_data):
  # Get the page
  req = urllib2.Request(roster_uri, headers=HEADERS)
  html = urllib2.urlopen(req).read()
  soup = BeautifulSoup(html, 'lxml')

  # Get the rows
  rows = soup.findAll('tr', 'alignMiddle')

  # Get the skaters
  skaters = []
  for row in rows:
    skater_number = row.find('td').text.encode('ascii', 'ignore')
    skater_name = row.a.text.encode('ascii', 'ignore')
    position = row.findAll('td')[2].text.encode('ascii', 'ignore')
    skater = {
      'name': skater_name,
      'number': skater_number,
      }
    skater.update(league_data)
    if position:
      skater.update({'position': position})
    skaters.append(skater)
  return skaters


league_uris = compile_member_league_uris()
leagues = []
for league in league_uris:
  leagues.append(get_league_data(league))

print json.dumps(leagues, indent=4)
