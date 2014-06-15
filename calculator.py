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

# Let's look at numbers
for skater in data:
    num = skater['skater_number']
    if skater['league_status'] == "Apprentice":
        if is_number(num):
            apprentice_1 += 1
        else:
            apprentice_a += 1
            if len(num) == 4:
                apprentice_f += 1
        if len(num) > 2:
            apprentice_l += 1
        else:
            apprentice_s += 1
    else:
        if is_number(num):
            member_1 += 1
        else:
            member_a += 1
            if len(num) == 4:
                member_f += 1
        if len(num) > 2:
            member_l += 1
        else:
            member_s += 1

print "apprentice numeric: %i" % apprentice_1
print "apprentice alphanumeric: %i" % apprentice_a
print "apprentice short: %i" % apprentice_s
print "apprentice long: %i" % apprentice_l
print "apprentice f: %i" % apprentice_f
print "member numeric: %i" % member_1
print "member alphanumeric: %i" % member_a
print "member short: %i" % member_s
print "member long: %i" % member_l
print "member f: %i" % member_f
