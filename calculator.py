import json

json_data=open('skaters').read()
data = json.loads(json_data)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

member_1 = 0
member_a = 0
member_s = 0
member_l = 0
apprentice_1 = 0
apprentice_a = 0
apprentice_s = 0
apprentice_l = 0

member_f = 0
apprentice_f = 0

counts = {
        'Total': {},
        'Members': {
            'Total': 0,
            'Numeric': 0,
            'Alphanumeric': 0,
            'Long': 0,
            'Short': 0,
            'Terrible' : 0
            },
        'Apprentices': {
            'Total': 0,
            'Numeric': 0,
            'Alphanumeric': 0,
            'Long': 0,
            'Short': 0,
            'Terrible' : 0
            }
        }


# Let's look a skater
for skater in data:
    num = skater['skater_number']

    if skater['league_status'] == 'Member':
        skater_type = 'Members'
    else:
        skater_type = 'Apprentices'

    counts[skater_type]['Total'] += 1

    if is_number(num):
        counts[skater_type]['Numeric'] += 1
    else:
        counts[skater_type]['Alphanumeric'] += 1
        if len(num) == 4:
            counts[skater_type]['Terrible'] += 1
    if len(num) > 2:
        counts[skater_type]['Long'] += 1
    else:
        counts[skater_type]['Short'] += 1

for field in counts['Members']:
    counts['Total'][field] = (counts['Members'][field] +
                              counts['Apprentices'][field])

print json.dumps(counts, indent=4)
