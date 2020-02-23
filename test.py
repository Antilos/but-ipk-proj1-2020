import re

m1 = re.search('(GET)|(POST)', 'GET')
m2 = re.search('(GET)|(POST)', 'POST')

print(f'1:{m1.group(1)} 2:{m1.group(2)}\n1:{m2.group(2)} 2:{m2.group(2)}')