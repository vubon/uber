# driver_list = ['Driver01', 'Driver02', 'Driver03', 'Driver04', 'Driver05', 'Driver06']
#
# d = {}
# for i in range(4):
#     text = input('Your data: ').split()
#     d[text[0]] = text[1]

import datetime


class InputData:
    name = str(input('Name: '))
    name2 = str(input('Name: '))
    now = datetime.datetime.now()
    print('{now}: {name} {name2}'.format(now=now, name=name, name2=name2))



