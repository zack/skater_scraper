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
        'Members': {
            'Numeric': 0,
            'Alphanumeric': 0,
            'Long': 0,
            'Short': 0,
            'Terrible' : 0
            },
        'Apprentices': {
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
    if skater['league_status'] == "Apprentice":
        if is_number(num):
            counts['Apprentices']['Numeric'] += 1
        else:
            apprentice_a += 1
            counts['Apprentices']['Alphanumeric'] += 1
            if len(num) == 4:
                counts['Apprentices']['Terrible'] += 1
        if len(num) > 2:
            counts['Apprentices']['Long'] += 1
        else:
            counts['Apprentices']['Short'] += 1
    else:
        if is_number(num):
            counts['Members']['Numeric'] += 1
        else:
            counts['Members']['Alphanumeric'] += 1
            if len(num) == 4:
                counts['Members']['Terrible'] += 1
        if len(num) > 2:
            counts['Members']['Long'] += 1
        else:
            counts['Members']['Short'] += 1

print json.dumps(counts, indent=4)
