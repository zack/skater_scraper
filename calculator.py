import json
from copy import deepcopy

json_data=open('skaters').read()
data = json.loads(json_data)

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
        elif c == '7':
            s += 2
        else:
            s += 1
    return s

counts = {
        'All': {
            'Total': 0,
            'Numeric': 0,
            'Alphanumeric': 0,
            '1': 0,
            '2': 0,
            '3': 0,
            '4': 0,
            }
        }
counts['All']['Syllables'] = dict.fromkeys(range(1, 12), 0)
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
    if len(num) == 1:
        counts[skater_type]['1'] += 1
    if len(num) == 2:
        counts[skater_type]['2'] += 1
    if len(num) == 3:
        counts[skater_type]['3'] += 1
    else:
        counts[skater_type]['4'] += 1


for field in counts['Members']:
    if field == 'Syllables':
        for n in counts['All'][field]:
            counts['All'][field][n] = (counts['Members'][field][n] +
                counts['Apprentices'][field][n])
    else:
        counts['All'][field] = (counts['Members'][field] +
            counts['Apprentices'][field])

f = open('skater_data.json', 'w')
f.write(json.dumps(counts, indent=4))
f.close()
