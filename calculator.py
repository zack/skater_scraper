from __future__ import division
import json
from operator import add
from copy import deepcopy
from numpy import zeros

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
            'Syllables': [0]*12,
            'Letters': [[0 for i in range(4)] for i in range(4)]
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

    count = lambda l1,l2: sum([1 for x in l1 if x in l2])
    lets = len(num) - count(num, "0123456789")
    counts[skater_type]['Letters'][len(num)-1][lets] += 1

# Compute totals (no longer used but might in the future)
#for field in counts['Members']:
    #if field == 'Syllables' or field == 'Chars':
        #counts['All'][field] = map(add,
                #counts['Members'][field],
                #counts['Apprentices'][field])
    #elif field == 'Letters':
        #pass
    #else:
        #counts['All'][field] = (counts['Members'][field] +
            #counts['Apprentices'][field])

# Normalize some fields
for s in ['Members', 'Apprentices']:
    for q in ['Chars', 'Syllables']:
        counts[s][q] = [round(n*100/counts[s]['Total'], 2) for n in counts[s][q]]
for s in ['Members', 'Apprentices']:
    a_new = [[0 for i in range(4)] for i in range(4)]
    for i, l in enumerate(counts[s]['Letters']):
        counts[s]['Letters'][i] = [round(x*100/sum(l),2) for x in l]
        # Rotate array
        for row_i, row in enumerate(counts[s]['Letters']):
            for col_i, col in enumerate(row):
                a_new[col_i][row_i] = col
    counts[s]['Letters'] = a_new

f = open('skater_data.json', 'w')
f.write(json.dumps(counts, indent=4))
f.close()
