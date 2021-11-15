id_to_name = {
    'B83C5E': 'R1',
    'B8FEB4': 'R2',
    'B82A56': 'R3',
    '95B94D': 'R4',
    'B8BCEF': 'R5',
    'B8E936': 'R6',
    'B90FBF': 'R7',
    '95A4CF': 'R8',
    'B7D681': 'R9',
    '965FC2': 'R10',
    'B81B6D': 'R11',
    'B7FFD6': 'R12',
    '95CE73': 'R13',
    'B9070A': 'R14',
    'B85958': 'R15',
    '967390': 'R16',
    'B9043F': 'R17',
    '96145D': 'R18',
    'B848C1': 'R19',
    'B8A72A': 'R20',
    'B8B714': 'R21'
}

def getName(id):
    return id_to_name.get(id, 'wrong id')

# getName("967390") returns 'R16'
