id_to_name = {
    'B83C5E': 'R-01',
    'B8FEB4': 'R-02',
    'B82A56': 'R-03',
    '95B94D': 'R-04',
    'B8BCEF': 'R-05',
    'B8E936': 'R-06',
    'B90FBF': 'R-07',
    '95A4CF': 'R-08',
    'B7D681': 'R-09',
    '965FC2': 'R-10',
    'B81B6D': 'R-11',
    'B7FFD6': 'R-12',
    '95CE73': 'R-13',
    'B9070A': 'R-14',
    'B85958': 'R-15',
    '967390': 'R-16',
    'B9043F': 'R-17',
    '96145D': 'R-18',
    'B848C1': 'R-19',
    'B8A72A': 'R-20',
    'B8B714': 'R-21'
}

def getName(id):
    return id_to_name.get(id, 'wrong id')

# getName("967390") returns 'R16'
