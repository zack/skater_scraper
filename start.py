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
def compile_all_member_league_uris():
  league_uris = []
  # Want a full set of data, or no?
  s = 13 if SMALL else 1
  for i in range(s,14):
    uri = 'https://wftda.com/dashboard/leagues/member-leagues?page=%i' % (i, )
    league_uris.extend(get_league_uris_by_page(uri))
  return league_uris

# -> List
# Returns a list of all apprentice league URIs
def compile_all_apprentice_league_uris():
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
def get_league_identifying_data(league_page_uri):
  league_data = {}

  # Get the page
  req = urllib2.Request(league_page_uri, headers=HEADERS)
  html = urllib2.urlopen(req).read()
  soup = BeautifulSoup(html, 'lxml')

  # Get league name
  name = soup.find('h1').text.encode('ascii', 'ignore')
  league_data['name'] = name

  # Get league location
  loc = soup.find('div', 'leagueHeader').findAll('span')[2]['title'].split('-')
  if len(loc) == 3:
      location = {'Country' : loc[0], 'State/Province': loc[1], 'City' : loc[2]}
  if len(loc) == 2:
      location = {'Country' : loc[0], 'City': loc[1]}
  league_data['location'] = location

  # Get league membership status and region (since they're in the same tag)
  league_info = soup.find('div', 'columnThird').findNext('div', 'columnThird').find('p').text.encode('ascii', 'ignore')
  league_info = [data.strip() for data in league_info.split('\n') if data != '']
  league_data['status'] = league_info[0].split(' ')[1]
  league_data['region'] = league_info[1].split(' ')[0]

  return league_data

# String -> Dictionary
# Takes a team roster URI and returns a dictinoary of skaters
# Dictionary key is skater name, keys are number and position (captain?)
def get_team_roster(roster_uri):
  # Get the page
  req = urllib2.Request(roster_uri, headers=HEADERS)
  html = urllib2.urlopen(req).read()
  soup = BeautifulSoup(html, 'lxml')

  # Get the rows
  rows = soup.findAll('tr', 'alignMiddle')

  # Get the skaters
  skaters = {}
  for row in rows:
    skater_number = row.find('td').text.encode('ascii', 'ignore')
    skater_name = row.a.text.encode('ascii', 'ignore')
    skaters.update({skater_name: skater_number})
  return skaters

print get_team_roster('https://wftda.com/dashboard/teams/roster/mu7sm8zfdeiq/1')
