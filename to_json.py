import json

array = []

with open('keywords', encoding='utf-8') as r:
    for i in r:
        n = i.lower().split('\n')[0]
        if n != '':
            array.append(n)


with open('keywords.json', 'w', encoding='utf-8') as e:
    json.dump(array, e)