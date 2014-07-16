import json
from operator import add
from copy import deepcopy

json_data=open('skaters.json').read()
data = json.loads(json_data)['skaters']

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_syllables(n):
    s = 0
    for c in n.upper():
        if c == 'W':
            s +=3
        elif c == '7' or c == '0':
            s += 2
        else:
            s += 1
    return s

counts = {
        'All': {
            'Total': 0,
            'Numeric': 0,
            'Alphanumeric': 0,
            'Chars': [0]*4,
            'Syllables': [0]*12
            }
        }
counts['Members'] = deepcopy(counts['All'])
counts['Apprentices'] = deepcopy(counts['All'])

# Let's look a skater
for skater in data:
    num = skater['skater_number']
    syl_count = get_syllables(num)

    if skater['league_status'] == 'Member':
        skater_type = 'Members'
    else:
        skater_type = 'Apprentices'

    counts[skater_type]['Total'] += 1
    counts[skater_type]['Syllables'][syl_count] += 1

    if is_number(num):
        counts[skater_type]['Numeric'] += 1
    else:
        counts[skater_type]['Alphanumeric'] += 1

    counts[skater_type]['Chars'][len(num)-1] += 1

# Compute totals
for field in counts['Members']:
    if field == 'Syllables' or field == 'Chars':
        counts['All'][field] = map(add,
                counts['Members'][field],
                counts['Apprentices'][field])
    else:
        counts['All'][field] = (counts['Members'][field] +
            counts['Apprentices'][field])

# Normalize some fields
for s in ['All', 'Members', 'Apprentices']:
    for q in ['Chars', 'Syllables']:
        counts[s][q] = [n*10000/counts[s]['Total']/100.00 for n in counts[s][q]]

f = open('skater_data.json', 'w')
f.write(json.dumps(counts, indent=4))
f.close()
