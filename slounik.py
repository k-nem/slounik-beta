import sqlite3
import re
import csv
import os
from datetime import datetime

# DEFAULTS
# default paths assumed by functions if no arguments are passed
defaults = {'databaseFile': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assets', 'dictionary.db'), # _connectToDB()  
            'stopWordsFile': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assets', 'stop_words.txt'), # setStopWords()
            'exportDirectory': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'exports') # exportCSV()
            }

# MAPPINGS & CLASSIFICATIONS
# database columns
DBcolumns = {
    # used to label search result attributes (redundant table columns are omitted)
    'schema': {
        'form': ('ID', 'LemID', 'VarID', 'Form', 'Accent', 'Gender', 'Person', 'Cas', 'Number', 'Degree', 'Tense', 'Mood', 'VerbForm', 'Animacy', 'Short'),
        'lemma': ('ID', 'Lemma', 'POS', 'Type', 'InflClass', 'Degree', 'Person', 'Gender', 'Voice', 'Tense', 'Aspect', 'Animacy', 'Abbr', 'NumForm', 'VerbForm', 'Personal', 'Origin', 'Poss', 'Reflex', 'SubCat')
        },
    # same column lists as strings for SQL statements
    'SQL': {
        'form': 'ID, LemID, VarID, Form, Accent, Gender, Person, Cas, Number, Degree, Tense, Mood, VerbForm, Animacy, Short',
        'lemma': 'ID, Lemma, POS, Type, InflClass, Degree, Person, Gender, Voice, Tense, Aspect, Animacy, Abbr, NumForm, VerbForm, Personal, Origin, Poss, Reflex, SubCat'
        },
    # used to map arbitrary search keyword arguments to SQL 
    'search': {
        'dual': ('degree', 'person', 'gender', 'tense', 'animacy', 'verbform'),
        'form': ('cas', 'number', 'mood', 'short'),
        'lemma': ('pos', 'type', 'inflclass', 'voice', 'aspect', 'abbr', 'numform', 'personal', 'origin', 'poss', 'reflex', 'subcat')
        }
    }

# the list of valid search query characters
validQueryCharacters = 'абвгдеёжзійклмнопрстуўфхцчшыьэюяАБВГДЕЁЖЗІЙКЛМНОПРСТУЎФХЦЧШЫЬЭЮЯ-\'‘’!?*[]'

# token classification
tokenCategories = {
    # word-like tokens to be queried in the database
    'word': re.compile(r'([а-яА-ЯЁёУўІі]+([\-\'‘’][а-яА-ЯЁёУўІі]+)*)'),
    # sentence-ending punctuation marks to be used for sentence segmentation
    'sentenceEnd': ('...', '?..', '!..', '?!', '???', '!!!', '.', '!', '?', '…', '⁈'),

    # the key-value pairs below are used for to approximate the category of tokens that are not present in the database
    ## abbreviations
    'abbr': re.compile(r'''
                         ([а-яА-ЯЁёУўІі]{1,2}[23²³] # Quadratic or cubic units of measurements: `м2`
                         |([а-яА-ЯЁёУўІі]+\.[а-яА-ЯЁёУўІі]+\.) # Compound abbreviations with periods: `н.э.`
                         |([А-ЯЁУІ]?[а-яёўі]+\.\-[а-яёўі]+\.) # Compound abbreviations with periods and hyphens: `с.-г.`
                         |([а-яА-ЯЁёУўІі]+\/[а-яА-ЯЁёУўІі]+) # Compound abbreviations with slashes: `к/т`
                         |([А-ЯЁУІ]\.) # Initials: `Д. [Свіфт]`
                         |(\d+\-[а-яёўі]+([\'‘’][а-яёўі]+)*) # Numerical expressions with cyrillic endings: `1-шы`
                         |[а-яА-ЯЁёУўІі]+\.) # 
                         ''',
                         re.X),
    ## alphanumeric codes
    'code': re.compile(r'(\d*[A-ZА-ЯЁУІ]+(\d+[A-ZА-ЯЁУІ]*)+)'),
    ## some emoticons
    'emo': re.compile(r'(\({3,}|\){3,}||[:;]\-?[\(\)]+)'),
    ## numbers
    'num': re.compile(r'''
                         ([0123]\d\.[01]\d(\.((\d{2})|(\d{4})))? # Dot-separated dates: `01.02.03`
                         |[012]?\d:[012345]\d(:[012345]\d)? # Time `12:34`
                         |(M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})) # Roman numerals
                         |(\d+([,\.]\d+)?) # Numbers: `1,234`, `2025`
                         |((8\s?\(?\d{3}\)?)|(\(?\+?\d{3}\s?\(?\d{2}\)?))\s?\d{3}[\-\s]?\d{2}[\-\s]?\d{2} ) # Phone numbers
                         ''',
                         re.X),
    ## numbers with space-separated thousand groups
    'numSpace': re.compile(r'[1-9]\d{,2}(\s\d{3})+'),
    ## punctuation marks
    'punct': ('...', '?..', '!..', '!!!', '???', '?!', '⁈', '-,', '- ,', '–,', '– ,', '.', ',', ':', ';', '!', '?', '…', '-', '–', '—', '«', '»', '„', '“', '"', '(', ')', '[', ']', '{', '}'),
    ## symbols
    'sym': ('\\', '/', '%', '№', '#', '^', '+', '=', '*', '<', '>', '~', '×', '÷', '@', '_', '&', '$', '§', '€', '£', '₽', '℃', '°С', '℉', '°', '®', '©', '™')
    }

# the list of abbreviations used for token and sentence segmentation, and token classification
abbreviations = {
    # abbreviations without `.` full stop
    'noStop': ('в-аў', 'п-аў', 'р-н', 'т-ва', 'ун-т', 'млн', 'млрд', 'см', 'га', 'м', 'мм', 'мг', 'кг', 'км', 'л', 'дж', 'кал', 'ккал', 'гц', 'мін', 'сут'),
    # abbreviations with `.` full stop that are can occur at the end of a sentence
    'stopAmbiguous': ('вобл', 'г', 'гг', 'інш', 'пад', 'руб', 'с', 'сc', 'ст', 'стст', 'т', 'тт', 'тыс'),
    # abbreviations with `.` full stop that are unlikely to occur at the end of a sentence
    'stopNonFinal': ('акад', 'б', 'бухг', 'в', 'воз', 'вул', 'гл', 'гр', 'дац', 'заг', 'зб', 'нам', 'напр', 'параўн', 'праф', 'р', 'св', 'сп', 'тав')
}




# SERVICE FUNCTIONS (NOT FOR DIRECT USE)

def _connectToDB(DBpath = defaults['databaseFile']):
    '''
    Create an SQLite database connection.

    [ARGUMENTS]:
    - `path` (str) OPTIONAL : OS path to the dictionary database file. If not specified, the default `databaseFile` value is used. Defaults can be modified using `config.ini`.

    [RETURNS]:
    - `(connection, cursor)` tuple:
        - `connection` : SQLite connection object.
        - `cursor` : SQLite database cursor.
    
    [USAGE]:
    This function is used as an interim operation and is not intended for stand-alone use.
    '''
    # RESET 
    connection, cursor = [None] * 2
    
    # CHECK FOR PATH VALIDITY
    if DBpath.endswith('.db') and os.path.exists(DBpath):
        # CONNECT
        try:
            connection = sqlite3.connect(DBpath)
            cursor = connection.cursor()
        except sqlite3.Error as exception:
            return exception

        return connection, cursor
    
    else:
        return 'Connection failed: Invalid database file path.'


def _boolly(value, direction):
    '''
    Convert SQLite "Boolean" integers to Universal Dependencies or Python Boolean format, or vice versa, for the annotation of database response. 
    
    [ARGUMENTS]:
    - `value` (int, str) : The value to be converted.
    - `direction` (int) : The direction and type of conversion:
        - 1 : SQLite "boolean" integer to UD string: 0 -> 'No', 1 -> 'Yes'.
        - 2 : UD string to integer: 'No' -> 0, 'Yes' -> 1.
        - 3 : SQLite "boolean" integer to UD `Animacy` value string: 0 -> 'Inan', 1 -> 'Anim'.
        - 4 : UD `Animacy` value to integer: 'Inan' -> 0, 'Anim' -> 1.
        - 5 : SQLite "boolean" integer to Python Boolean: 0 -> False, 1 -> True.
        - 6 : Python Boolean to integer: False -> 0, True -> 1.

    [RETURNS]:
    - Output (int, str) : Converted value. 
    
    [USAGE]:
    This function is used as an interim operation and is not intended for stand-alone use.
    '''
    if direction == 1: return {0: 'No', 1: 'Yes'}[value]
    elif direction == 2: return {'No': 0, 'Yes': 1}[value]
    elif direction == 3: return {0: 'Inan', 1: 'Anim'}[value]
    elif direction == 4: return {'Inan': 0, 'Anim': 1}[value]
    elif direction == 5: return {0: False, 1: True}[value]
    elif direction == 6: return {False: 0, True: 1}[value]


def _generateSearchSQL(kwargDictionary):
    '''
    Generate SQL search arguments from a dictionary of user-generated keyword attributes passed as Form or Lemma search filters. 

    [ARGUMENTS]:
    - `kwargDictionary` (dict) : The dictionary of search keyword arguments specified by the user in `formSearch()`, `lemSearch()`, `fastFormSearch()`, `fastLemSearch()`.

    [RETURNS]:
    - `searchFiltersSQL` (str) : SQL arguments to be added to SQL search statement.

    [USAGE]:
    This function is used for an interim operation in search functions and is not intended for stand-alone use.
    '''
    kwargStrings = ()
    
    for key, value in kwargDictionary.items():
        if isinstance(value, bool): kwargStrings += (' = '.join((key, str(_boolly(kwargDictionary[key], 6)))),)
        elif isinstance(value, int): kwargStrings += (' = '.join((key, str(kwargDictionary[key]))),)
        elif isinstance(value, str): kwargStrings += (' = '.join((key, ''.join(('\"', kwargDictionary[key], '\"')))),)

    searchFiltersSQL = ' AND '.join(kwargStrings)
    
    return searchFiltersSQL


def _UDify(data, level):
    '''
    Converting a database search result into a Python dictionary using Universal Dependencies notation, depending on the specified level. 
    
    [ARGUMENTS]:
    - `data` (tuple) : SQL response in tuple format, depending on the level.
    - `level` (str) : The flag that determines the output format.
      [VALUE OPTIONS]:
        - 'f' : Form format.
        - 'l' : Lemma format.

    [RETURNS]:
    - `Output` (dict) : Form or Lemma annotation.
    
    [USAGE]:
    This function is used as an interim operation and is not intended for stand-alone use.
    '''
    output = {}
 
    # FORM ANNOTATION
    if level == 'f':
        for i, value in enumerate(data):   
            # detect non-empty values excluding redundant LemID and VarID
            if value and i not in (1, 2):
                # rename Cas to Case (restricted word in SQLite)
                if i == 7: output['Case'] = value
                # convert "Boolean" integer to Python format
                elif i in (13, 14): output[DBcolumns['schema']['form'][i]] = _boolly(value, 5)
                # add other values without modification
                else: output[DBcolumns['schema']['form'][i]] = value

    # LEMMA ANNOTATION
    elif level == 'l':
        for i, value in enumerate(data):
            if value:
                # convert `Type` label to POS-specific, e.g., NumType
                if i == 3: output[f'{data[2].title()}Type'] = value  
                # convert "Boolean" integers to Python format
                elif i in (11, 12, 15, 17, 18): output[DBcolumns['schema']['lemma'][i]] = _boolly(value, 5)
                # add other values without modification    
                else: output[DBcolumns['schema']['lemma'][i]] = value

    return output if output else None




# UTILITY FUNCTIONS

def setStopWords(lemIDs = defaults['stopWordsFile']):
    '''
    Set stop-words, i.e. the list of comma-separated lemma IDs in string format, to be excluded from database search results. 
    
    [ARGUMENTS]:
    - `lemIDlist` (NoneType, tuple, str) : Stop-word list source. If not specified, the default `stopWordsPath` value is used as the file path. Defaults can be modified using `config.ini`.
      [VALUE OPTIONS]:
        - File path (str) : OS path to a TXT file with comma-separated lemma IDs.
        - IDs (tuple) - Lemma IDs in integer format.
        - `None` (NoneType) - Removes all stop words.

    [RETURNS]:
    - `stopWords` VAR VALUE (dict) : Populates `stopWords` value with a dictionary with the following keys:
        - `List` (list) : The list of integers.
        - `String` (str) : The list in string format to be appended to SQL search statements.  
    '''
    global stopWords
    
    if lemIDs == None:
        stopWords = {'List': [], 'String': ''}
        return 'The stop-word list was emptied.'
        
    elif isinstance(lemIDs, tuple):
        lemIDlist = sorted(list(set([lemID for lemID in lemIDs if isinstance(lemID, int)])))
        if not lemIDlist:
            return 'The stop-word list was not updated: No valid values were found.'
        else:
            stopWords = {'List': lemIDlist,
                         'String': ', '.join([str(lemID) for lemID in lemIDlist])}
            if len(lemIDs) != len(lemIDlist):
                return 'The stop-word list was updated. Some of the submitted values were removed due to duplication or invalid format.'
            else:
                return 'The stop-word list was updated.'
   
    elif isinstance(lemIDs, str) and lemIDs.endswith('.txt'):
        if not os.path.exists(lemIDs):
            return 'The stop-word list was not updated. Invalid file path.'
        else:
            with open(lemIDs, 'r+', encoding = 'utf-8') as file:
                fileContents = file.read()
                fileList = [item.strip() for item in fileContents.split(',')]
                lemIDlist = sorted(list(set([int(lemID) for lemID in fileList if lemID.isdigit()])))
                             
            if not lemIDlist:
                return f'The stop-word list was not updated with values from {os.path.abspath(lemIDs)}. No valid values were found.'
            else:
                stopWords = {'List': lemIDlist,
                             'String': ', '.join([str(lemID) for lemID in lemIDlist])}
                if len(fileList) != len(lemIDlist):
                    return f'The stop-word list was updated with values from {os.path.abspath(lemIDs)}. Some values were removed due to duplication or invalid format.'
                else:
                    return f'The stop-word list was updated with values from {os.path.abspath(lemIDs)}.'

    else:
        return 'Unsupported list format.'

    return message


def accentuate(form, accentData):
    '''
    Add word stress diacritic marks to a word form. The mark used is Unicode `\u0301`.

    [ARGUMENTS]:
    - `form` (str) : Word form as it is stored in `Form` column of `Form` database table and outputted under ['FormData']['Form'] key of a form dictionary.
    - `accentData` (str) : Accent position data as it is stored in `Accent` column of Form table and outputted under ['FormData']['Accent'] key of a form dictionary. Numbering starts with 1.

    [RETURNS]:
    - `accentedForm` (str) : The inputted word form with diacritic marks.
    OR
    - `None` (NoneType) : Returned if the submitted data is invalid.
    '''
    # validate arguments
    if not isinstance(form, str): return None
    if (isinstance(accentData, str) and any(c for c in accentData if c not in '0123456789-')) or (isinstance(accentData, int)) or (accentData in (0, '0')): return None
    
    accentedForm = None

    # simple word stress
    if '-' not in form and '-' not in accentData:
        if len(form) >= int(accentData):
            accentedForm = ''.join([form[:int(accentData)], u'\u0301', form[int(accentData):]])
    # compound word stress
    else:
        positions = [int(p) for p in accentData.split('-')]
        parts = form.split('-')
        if (len(parts) != len(positions)) or (all(p == 0 for p in positions)): return None
            
        accentedParts = ()
        for i, position in enumerate(positions):
            if position != 0: accentedParts += (''.join([parts[i][:position], u'\u0301', parts[i][position:]])),
            else: accentedParts += (parts[i]),
                
        accentedForm = '-'.join(accentedParts)

    return accentedForm


def exportCSV(data, level, directory = defaults['exportDirectory']):
    '''
    Export `formSearch()` or `lemmaSearch()` search results into a CSV file in the specified directory of local file system.
     
    [ARGUMENTS]:
    - `data` (dict) : `formSearch()` or `lemmaSearch()` functions' output.
    - `level` (str) : Input data structure.
      [VALUE OPTIONS]:
        - 'f' : Form, for `formSearch()` results.
        - 'l' : Lemma, for `lemmaSearch()` results.
    - `path` (str) OPTIONAL : OS path to the target directory. If not specified, the default `exportPath` value is used.

    [RETURNS]:
    `Slounik_Export_{YYYY-MM-DD_HH-MM-SS}.csv` (File) OS : CSV file with the inputted data generated in the specified directory of local file system.
    '''
    rows = ()
    columns = ('Lemma_ID', 
               'Lemma', 
               'POS',
               'Lemma_Type',
               'Lemma_InflClass',
               'Lemma_Degree',
               'Lemma_Person',
               'Lemma_Gender',
               'Lemma_Voice',
               'Lemma_Tense',
               'Lemma_Aspect',
               'Lemma_Animacy',
               'Lemma_Abbr',
               'Lemma_NumForm',
               'Lemma_VerbForm',
               'Lemma_Personal',
               'Lemma_Origin',
               'Lemma_Poss',
               'Lemma_Reflex',
               'Lemma_SubCat',
               'Variant',
               'Form_ID',
               'Form',
               'Form_Accent',
               'Form_Gender',
               'Form_Person',
               'Form_Cas',
               'Form_Number',
               'Form_Degree',
               'Form_Tense',
               'Form_Mood',
               'Form_VerbForm',
               'Form_Animacy',
               'Form_Short')
    
    #VALIDITY CHECK
    if not os.path.exists(directory): dirCheck = False; return 'Invalid directory path.'
    else: dirCheck = True

    if not isinstance(data, tuple): dataCheck = False; return 'Invalid data format.'
    else: dataCheck = True
    
    if dirCheck and dataCheck:
        def _makeRow(result, mode):
            '''
            Convert a single search result into a tuple mapped to CSV file row.

            [ARGUMENTS]:
            - `result` (dict) : The search result of `formSearch()` or `lemSearch()` function.
            - `mode` (str) : The flag that determines the data structure.
              [VALUE OPTIONS]:
                - 'f' - Form, for `formSearch()` results
                - 'l' - Lemma, for `lemmaSearch()` results
            
            [RETURNS]:
            - `row` (tuple) : CSV table row.

            [USAGE]:
            This function is used as an interim operation in `exportCSV()` and is not intended for stand-alone use.
            '''
            row = ()
            
            # FORM LEVEL - combines Form & Lemma attributes
            if mode == 'f':
                # lemma attribute columns correspond to lemSchema, including empty
                for lemAttribute in DBcolumns['schema']['lemma']:
                    if lemAttribute in result['LemmaData']: row += (result['LemmaData'][lemAttribute],)
                    else: row += (None,)
                # variant value
                row += (entry['Variant'],)
                # form attribute columns correspond to formSchema, including empty
                for i, formAttribute in [item for item in enumerate(DBcolumns['schema']['form']) if item[0] not in (1, 2)]:
                    if formAttribute in result['FormData']: row += (result['FormData'][formAttribute],)
                    else: row += (None,)
        
            # LEMMA LEVEL
            elif mode == 'l':
                # lemma attribute columns correspond to lemSchema, including empty
                for attribute in DBcolumns['schema']['lemma']:
                    if attribute in entry: row += (entry[attribute],)
                    else: row += (None,)
                # form attributes are empty by definition
                row += (None,) * 14
    
            return row
    
        # GENERATE FILE
        for entry in data: rows += (_makeRow(entry, level),)
        filename = os.path.join(directory, ''.join(('Slounik_Export_', datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), '.csv')))
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            wr = csv.writer(file, delimiter=',')
            wr.writerow(columns)
            wr.writerows(rows)
    
        print(f'{os.path.abspath(filename)} was created.')



# CORE FUNCTIONALITY

def formSearch(query, keepLetterCase = False, fastMode = False, **kwargs):
    '''
    Find all forms than match the query and return their full form, lemma and variant data.

    [ARGUMENTS]:
    - `query` (str) : A word form to look for in the database. It can be submitted with or without the keyword: 'а' or `query = 'а'`. 
      It supports globbing (https://en.wikipedia.org/wiki/Glob_(programming)):
        - `?` : Any character once.
        - `*` : Zero or more of any characters.
        - `[абв]` or `[а-в]` : Any character in the range specified in the brackets, once.
        - `[!абв]` or `[!а-в]` : Any character NOT in the range specified in the brackets, once.
    - Attribute (keyword argument) OPTIONAL : Form or lemma database attributes in `keyword = value` format, e.g., "Case = 'Nom'". See the attribute options listed below. For available categorical values refer to README.
      Keywords are not case sensitive and should not be put in quotation  marks. Values are case sensitive and use their respective Python data types: POS = 'NOUN', Person = 2, Abbr = True.
      Note: Attributes that can be applied to both form and lemma level (`Degree`, `Person`, `Gender`, `Tense`, `Animacy`, `VerbForm`) must to be prefixed with 'f_' and 'l_' correspondingly. 
      For example, `Degree` column value in Lemma database table is submitted under `l_Degree` keyword, the column of the same name in Form table is denoted by `f_Degree`. 
      [ATTRIBUTES]:
        - Form attributes: `Accent`, `Case`, `Number`, `Mood`, `Short`, `f_Degree`, `f_Person`, `f_Gender`, `f_Tense`, `f_Animacy`, `f_VerbForm`.
        - Lemma attributes: `POS`, `AdjType`, `NumType`, `PronType`, `InflClass`, `Voice`, `Aspect`, `Abbr`, `NumForm`, `Personal`, `Origin`, `Poss`, `Reflex`, `SubCat`, `l_Degree`, `l_Person`, `l_Gender`, `l_Tense`, `l_Animacy`, `l_VerbForm`.
    - `keepLetterCase` (bool) OPTIONAL : Case sensitivity of the search.
      [VALUE OPTIONS]:
        - `False` DEFAULT: Case-insensitive search.
        - `True` : Case-sensitive search.
    - `fastMode` (bool) : Output format which affects the speed of the search.
      [VALUE OPTIONS]:
        - `False` DEFAULT: All non-empty form and lemma attributes, as well as the form's variant, are returned for each result in dictionary format.
        - `True` : Only form IDs are returned, but the search is significantly faster. This format is used as an intermediate step for some operations.
    - `length` (int) OPTIONAL : The length of forms in characters.

    [RETURNS]:
    - `output` (tuple) : 
      [If `fastMode == False`]: A tuple of search results, sorted alphabetically by form, each represented by a dictionary with the following keys:
        - `FormData` (dict) : Non-empty form attributes.
        - `LemmaData` (dict) : Non-empty attributes of the form's lemma.
        - `Variant` (int) : The form's variant within the parent lemma.
      OR
      [If `fastMode == True`]: A tuple of integer form IDs sorted alphabetically by form.
    OR
    - `None` (NoneType) : Returned if search does not yield any results.
    '''
    # PREPARATION
    # Check for `query` value validity
    if any(character for character in query if character not in validQueryCharacters): return None
    
    # Reset
    connection, response, formValues, formValue, lemValue, varValue, output = [None] * 7
    
    # Replace `Ў` for `У`
    if query.startswith('ў'): query = 'у' + query[1:]
    elif query.startswith('Ў'): query = 'У' + query[1:]
    
    # Separate form & lemma key-argument pairs, skipping unknown keywords
    formKwargs = {}
    lemKwargs = {}
    for keyword in kwargs.keys():
        # flag ambiguous attributes
        if keyword.lower() in DBcolumns['search']['dual']: return 'Ambiguous search keywords. Request `help(formSearch)` for details.'
        # substitute UD attributes that are reserved words in SQLite
        elif keyword.lower() == 'case': formKwargs['Cas'] = kwargs[keyword]
        elif keyword.lower() == 'length': formKwargs['Len'] = kwargs[keyword]
        # mapping `AdjType`, `NumType`, `PronType` to `Type` column in Lemma table
        elif 'type' in keyword.lower(): lemKwargs['Type'] = kwargs[keyword]
        # separate attributes by their presense in Form or Lemma table columns (excluding dual)
        elif keyword.lower() in DBcolumns['search']['form']: formKwargs[keyword] = kwargs[keyword]
        elif keyword.lower() in DBcolumns['search']['lemma']: lemKwargs[keyword] = kwargs[keyword]
        # parse prefixed dual-use attributes
        elif '_' in keyword:
            keywordParts = keyword.lower().split('_')
            if len(keywordParts) == 2:
                if keywordParts[0] == 'f' and keywordParts[1] in DBcolumns['search']['dual']: formKwargs[keywordParts[1]] = kwargs[keyword]
                elif keywordParts[0] == 'l' and keywordParts[1] in DBcolumns['search']['dual']: lemKwargs[keywordParts[1]] = kwargs[keyword]
                
    # Generate SQL arguments as strings
    lemSearchSQL = _generateSearchSQL(lemKwargs) if lemKwargs else ''
    formSearchSQL = _generateSearchSQL(formKwargs) if formKwargs else ''
    stopWordSQL = f'ID NOT IN ({stopWords['String']})' if stopWords['String'] else ''
    
    # Generate Lemma table sub-query if necessary
    lemmaSubquery = ''
    if lemSearchSQL and stopWordSQL: lemmaSubquery = f' AND LemID IN (SELECT ID FROM Lemma WHERE {lemSearchSQL} AND {stopWordSQL})' 
    elif lemSearchSQL or stopWordSQL: lemmaSubquery = f' AND LemID IN (SELECT ID FROM Lemma WHERE {lemSearchSQL}{stopWordSQL})' 

    # Assemble the statement
    statement = f'''SELECT {DBcolumns['SQL']['form'] if fastMode == False else 'ID'} FROM Form 
                    WHERE {'Lowercase' if keepLetterCase == False else 'Form'} GLOB \"{query.lower() if keepLetterCase == False else query}\"
                    {f' AND {formSearchSQL} ' if formSearchSQL else ''} {lemmaSubquery} ORDER BY Form'''
    
    # DATABASE QUERY
    try:
        connection = _connectToDB()
        if connection:
            cursor = connection[1]
            response = ()
            with connection[0]:
                
                # request matching Form table rows
                cursor.execute(statement) 
                formValues = cursor.fetchall()
                
                if formValues:
                    if fastMode == False:
                        # provide lemma and variant data for each search result
                        for formValue in formValues: 
                            cursor.execute(f'SELECT {DBcolumns['SQL']['lemma']} FROM Lemma WHERE ID = {formValue[1]}')
                            lemValue = connection[1].fetchall()[0]
                            cursor.execute(f'SELECT Variant FROM Variant WHERE ID = {formValue[2]}')
                            varValue = connection[1].fetchall()[0][0]
    
                            response += ((formValue, lemValue, varValue),)
                            
                    elif fastMode == True:
                        # no further requests necessary
                        response = [result[0] for result in formValues]
                    
            connection[0].close()

    except sqlite3.Error as exception:
        return exception

    # ANNOTATION OF RESULTS
    if response:
        if fastMode == False:
            output = ()
            for result in response:
                #check for structure validity
                if len(result) == 3 and isinstance(result, tuple):
                    output += ({'FormData': _UDify(result[0], 'f'), 'LemmaData': _UDify(result[1], 'l'), 'Variant': result[2]},)
        
        elif fastMode == True:
            output = tuple(response)

    return output


def formByID(formID, toConllu = False, **kwargs):
    '''
    Request a form's data by its form ID.

    [ARGUMENTS]:
    - `formID` (int) : Form ID as it is stored in the `ID` column of `Form` database table.
    - `toConllu` (bool) OPTIONAL : Output format.
      [VALUE OPTIONS]:
        - `False` DEFAULT : Form, lemma and variant data are separated, each non-empty attribute is outputted as a key-value pair.
        - `True` : The output is grouped into `FORM`, `LEMMA`, `UPOS`, `FEATS` according to CoNLL-U table structure.

    [RETURNS]:
    - `output` (dict) : A dictionary of the form's attributes.
      [If `toConllu == False`]:
        - `FormData` (dict) : Non-empty form attributes.
        - `LemmaData` (dict) : Non-empty attributes of the form's lemma.
        - `Variant` (int) : The form's variant within the parent lemma.
      OR
      [If `toConllu == True`]:
        - `FORM` (str) OPTIONAL : Form, included unless `includeForm == False`.
        - `LEMMA` (str) : The form's dictionary form.
        - `UPOS` (str) : Part of speech tag.
        - `FEATS` (str): Non-empty form and lemma attributes in alphabetical order, separated by '|' vertical line.
    OR
    - `None` (NoneType) : Returned if the form ID does not exist. 
    '''
    # CHECK FORM ID VALIDITY
    if not isinstance(formID, int): return None

    # RESET
    connection, response, formValue, lemValue, varValue, features, output = [None] * 7

    if toConllu == True:
        if 'includeForm' in kwargs.keys():
            includeForm = kwargs['includeForm']
        else:
            includeForm = True

    # QUERY DATABASE
    try:
        connection = _connectToDB()
        if connection:
            cursor = connection[1]
            response = ()
            with connection[0]:
                # request Form table row
                cursor.execute(f'SELECT {DBcolumns['SQL']['form']} FROM Form WHERE ID = {formID}')
                formValue = cursor.fetchone()
                
                 # provide lemma and variant data for the result
                if formValue:
                    cursor.execute(f'SELECT {DBcolumns['SQL']['lemma']} FROM Lemma WHERE ID = {formValue[1]}')
                    lemValue = cursor.fetchone()
                        
                    response = (formValue, lemValue)

                    if toConllu == False:
                        cursor.execute(f'SELECT Variant FROM Variant WHERE ID = {formValue[2]}')
                        varValue = cursor.fetchone()[0]

                        response += (varValue,)
                        
            connection[0].close()

    except sqlite3.Error as exception:
        return exception

    # ANNOTATE RESULTS
    if response:
        if toConllu == False:
            # check for structure validity
            if isinstance(response, tuple) and len(response) == 3:
                output = {'FormData': _UDify(response[0], 'f'), 'LemmaData': _UDify(response[1], 'l'), 'Variant': response[2]}
                
        elif toConllu == True:
            # check for structure validity
            if len(response) == 2 and isinstance(response[0], tuple) and isinstance(response[1], tuple):
                output, features = ({}, {})

                # FORM DATA
                if includeForm == True: output['FORM'] = response[0][3] 
                # detect non-empty values excluding redundant attributes
                for i, value in [item for item in enumerate(response[0][5:]) if item[1]]:
                    # rename Cas to Case (restricted word in SQLite)
                    if i == 2: features['Case'] = value
                    # integer to UD `Animacy` value string
                    elif i == 8: features['Animacy'] = _boolly(value, 3)
                    # integer to UD "boolean" string
                    elif i == 9: features['Short'] = _boolly(value, 0)
                    # add other values without modification
                    else: features[DBcolumns['schema']['form'][5:][i]] = value
    
                # LEMMA DATA
                output['LEMMA'] = response[1][1]
                # detect non-empty values excluding redundant attributes
                for i, value in [item for item in enumerate(response[1][2:]) if item[1]]:
                    # UPOS value
                    if i == 0: output['UPOS'] = value
                    # convert `Type` label to POS-specific, e.g., NumType
                    elif i == 1: features[f'{response[1][2].title()}Type'] = value
                    # integer to UD `Animacy` value string
                    elif i == 9: features['Animacy'] = _boolly(value, 3)
                    # integers to UD "boolean" strings
                    elif i in (10, 13, 15, 16): features[DBcolumns['schema']['lemma'][2:][i]] = _boolly(value, 0)
                    # add other values without modification
                    else: features[DBcolumns['schema']['lemma'][2:][i]] = value

                # joining FEATS key-value pairs
                if features: output['FEATS'] = '|'.join([''.join([key, '=', str(features[key])])for key in sorted(features.keys())])
                else: output['FEATS'] = '_'
        
    return output


def lemmaSearch(query, keepLetterCase = False, fastMode = False, **kwargs):
    '''
    Find all lemmas (dictionary forms) that match the query and return their data.

    [ARGUMENTS]:
    - `query` (str) : A word form to look for in the database. It can be submitted with or without the keyword: 'а' or `query = 'а'`. 
      It supports globbing (https://en.wikipedia.org/wiki/Glob_(programming)):
        - `?` : Any character once.
        - `*` : Zero or more of any characters.
        - `[абв]` or `[а-в]` : Any character in the range specified in the brackets, once.
        - `[!абв]` or `[!а-в]` : Any character NOT in the range specified in the brackets, once.
    - Attribute (keyword argument) OPTIONAL : Any lemma database attribute in `keyword = value` format, e.g., "Gender = 'Masc'".
      Keywords are not case sensitive and should not be put in quotation  marks. 
      Values are case sensitive and use their respective Python data types: POS = 'NOUN', Person = 2, Animacy = True.
      [ATTRIBUTES]: 
        `POS`, `AdjType`, `NumType`, `PronType`, `InflClass`, `Voice`, `Aspect`, `Abbr`, `NumForm`, `Personal`, `Origin`, `Poss`, `Reflex`, `SubCat`, `Degree`, `Person`, `Gender`, `Tense`, `Animacy`, `VerbForm`.
    - `keepLetterCase` (bool) OPTIONAL : Case sensitivity of the search.
      [VALUE OPTIONS]:
        - `False` DEFAULT: Case-insensitive search.
        - `True` : Case-sensitive search.
    - `fastMode` (bool) : Output format which affects the speed of the search.
      [VALUE OPTIONS]:
        - `False` DEFAULT: All non-empty lemma attributes are returned for each result in dictionary format.
        - `True` : Only lemma IDs are returned, but the search is significantly faster. This format is used as an intermediate step for some operations.
    - `length` (int) OPTIONAL : The length of forms in characters.

    [RETURNS]:
    - `output` (tuple) : 
      [If `fastMode == False`]: A tuple of search results, sorted alphabetically by lemma, each represented by a dictionary with non-empty lemma attributes.
      OR
      [If `fastMode == True`]: A tuple of integer lemma IDs sorted alphabetically by lemma.
    OR
    - `None` (NoneType) : Returned if search does not yield any results.
    '''
    # PREPARATION
    # Check for `query` value validity
    if any(character for character in query if character not in validQueryCharacters): return None
    
    # Reset
    connection, response, output = [None] * 3
    
    # Replace `Ў` for `У`
    if query.startswith('ў'): query = 'у' + query[1:]
    elif query.startswith('Ў'): query = 'У' + query[1:]
    
    # Parse keyword agruments, skipping unknown keywords
    lemKwargs = {}
    for keyword in kwargs.keys():
        # substitute UD attributes that are reserved words in SQLite
        if keyword.lower() == 'length': lemKwargs['Len'] = kwargs[keyword]
        # mapping `AdjType`, `NumType`, `PronType` to `Type` column in Lemma table
        elif 'type' in keyword.lower(): lemKwargs['Type'] = kwargs[keyword]
        # collect lemma attributes
        elif keyword.lower() in DBcolumns['search']['lemma'] or keyword.lower() in DBcolumns['search']['dual']: lemKwargs[keyword] = kwargs[keyword]
                
    # Generate SQL arguments as strings
    lemSearchSQL = _generateSearchSQL(lemKwargs) if lemKwargs else ''
    stopWordSQL = f'ID NOT IN ({stopWords['String']})' if stopWords['String'] else ''

    # Assemble the statement
    statement = f'''SELECT {DBcolumns['SQL']['lemma'] if fastMode == False else 'ID'} FROM Lemma
                    WHERE {'Lowercase' if keepLetterCase == False else 'Lemma'} GLOB \"{query.lower() if keepLetterCase == False else query}\"
                    {f' AND {lemSearchSQL} ' if lemSearchSQL else ''} 
                    {f' AND {stopWordSQL} ' if stopWordSQL else ''} ORDER BY Lemma'''
    
    # DATABASE QUERY
    try:
        connection = _connectToDB()
        if connection:
            cursor = connection[1]
            response = ()
            with connection[0]:
                # request matching Lemma table rows
                cursor.execute(statement) 
                response = cursor.fetchall()
                
            connection[0].close()

    except sqlite3.Error as exception:
        return exception

    # ANNOTATION OF RESULTS
    if response:
        output = ()
        if fastMode == False:
            for result in response:
                output += (_UDify(result, 'l'),)
        elif fastMode == True:
            output = tuple([result[0] for result in response])

    return output


def lemmaByID(lemID):
    '''
    Request a lemma's data by its lemma ID.

    [ARGUMENTS]:
    - `lemID` (int) : Lemma ID as it is stored in the `ID` column of `Lemma` database table.

    [RETURNS]:
    - `output` (dict) : A dictionary of non-empty lemma attributes.
    OR
    - `None` (NoneType) : Returned if the lemma ID does not exist. 
    '''
    # CHECK LEMMA ID VALIDITY
    if not isinstance(lemID, int): return None
        
    # RESET
    connection, response, output = [None] * 3

    # QUERY DATABASE
    try:
        connection = _connectToDB()
        if connection:
            cursor = connection[1]
            response = ()
            with connection[0]:
                # request Lemma table row
                cursor.execute(f'SELECT {DBcolumns['SQL']['lemma']} FROM Lemma WHERE ID = {lemID}')
                response = cursor.fetchone()
                    
            connection[0].close()

    except sqlite3.Error as exception:
        return exception

    # ANNOTATE RESULTS
    if response:
        # check for structure validity
        output = _UDify(response, 'l')
        
    return output


def allForms(lemID):
    '''
    Request a lemma's full paradigm by lemma ID.

    [ARGUMENTS]:
    - `lemID` (int) : Lemma ID as it is stored in the `ID` column of `Lemma` database table.

    [RETURNS]:
    - `output` (tuple) : A tuple of the lemma's forms as dictionaries with all non-empty form attributes.
    OR
    - `None` (NoneType) : Returned if the lemma ID does not exist. 
    
    '''
    # CHECK LEMMA ID VALIDITY
    if not isinstance(lemID, int): return None
        
    # RESET
    connect, response, output, lemValue, varValue, formValue, formValues = [None] * 7
    
    # QUERY DATABASE
    try:
        connection = _connectToDB()
        if connection:
            cursor = connection[1]
            
            with connection[0]:
                # request Lemma table row 
                cursor.execute(f'SELECT {DBcolumns['SQL']['lemma']} FROM Lemma WHERE ID = {lemID}')
                lemValue = cursor.fetchone()
                
                if lemValue:
                    # request forms and their variants
                    response = {'lemma': lemValue, 'forms':[]}     
                    cursor.execute(f'SELECT {DBcolumns['SQL']['form']} FROM Form WHERE LemID = {lemValue[0]} ORDER BY ID')
                    formValues = cursor.fetchall()

                    if formValues:
                        forms = ()
                        for formValue in formValues:
                            cursor.execute(f'SELECT Variant FROM Variant WHERE ID = {formValue[2]}')
                            varValue = cursor.fetchone()[0]
                            forms += ((varValue, formValue),)

                        response['forms'] = forms
                    
            connection[0].close()

    except sqlite3.Error as exception:
        return exception
    
    # ANNOTATE RESULTS
    if response:
        # check for structure validity
        if isinstance(response, dict) and 'lemma' in response.keys() and 'forms' in response.keys():
            output = {'LemmaData': {}, 'Variants': ()}
            # annotate lemma attributes
            output['LemmaData'] = _UDify(response['lemma'], 'l')
            # generate form tuples (paradigms) grouped by variant
            variants = {}
            for form in response['forms']:
                if form[0] not in variants.keys(): variants[form[0]] = (_UDify(form[1], 'f'),)
                else: variants[form[0]] += (_UDify(form[1], 'f'),)           
            # add form groups to the output
            for variant in sorted(variants.keys()):
                output['Variants'] += ({'Variant': variant, 'Paradigm': variants[variant]},)

    return output


# PLAIN TEXT PROCESSING

def tokenize(text):
    '''
    Converts a plain text in Belarusian into a tuple of word-level tokens. Tokens are segmented based on standard Belarusian number, date etc. formats. 
    Supported token types: Words in Cyrillic and Latin script, Arabic and Roman numerals, abbreviations, punctuation marks, symbols, alphanumeric codes, date and time, Belarusian phone numbers, usernames, emails, top level URLs, some emoticons. See README for full description.

    [ARGUMENTS]:
    - `text` (str) : Plain text in Belarusian.

    [RETURNS]:
    - `output` (tuple) : The tuple of tokens extracted from the text.

    [USAGE]:
    This operation is intended to be used by text annotation functions after paragraph segmentation and before sentence segmentation. 
    '''
    # check `text` value validity
    if not isinstance(text, str): return None
    
    # reset
    matches, output = [None] * 2
    
    tokenPattern = re.compile(r'''
                        ([а-яА-ЯЁёУўІі]{1,2}[23²³]  # Units of measurements with digits: `м2`
                        |(?<!\d)((8\s?\(?\d{3}\)?)|(\(?\+?\d{3}\s?\(?\d{2}\)?))\s?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}(?!\d) # Phone numbers: `+375(33)123-45-67`, `8(017)2613202`
                        |(?<!\d)[0123]\d\.[01]\d(\.((\d{2})|(\d{4})))?(?!\d) # Dot-separated dates: `01.02.03`
                        |(@[a-zA-Z_\.]+(?![\.\w])) # Usernames: `@user`
                        |([a-zA-Z_\.]+@[a-zA-Z\-]+(\.[a-zA-Z]+)+) # Email adresses: `a_b@mail.com.by`
                        |(http(s)?://)?(www\.)?[a-zA-Z-]+(\.[a-zA-Z]+)+(/.+)? # URLs: `https://www.domain.com.by/home?=213`
                        |((?=[MDCLXVI])M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})) # Roman numerals: `XXI`
                        |([\(\)]{3,}|\.\.\.|\?\.\.|\!\.\.|\?\!|,\s?\-|[:;]\-?[\(\)]+|°[CС]) # Some multi-character symbols: `...`, `?..`, `?!`, `))))`, `:)`, `°C`, `,-`
                        |([а-яА-ЯЁёЎўІі]+\.[а-яА-ЯЁёЎўІі]+\.) # Compound abbreviations with periods: `н.э.`
                        |([А-ЯЁЎІ]?[а-яёўі]+\.\-[а-яёўі]+\.) # Compound abbreviations with periods and hyphens: `с.-г.`
                        |([а-яА-ЯЁёЎўІі]+\/[а-яА-ЯЁёЎўІі]+) # Compound abbreviations with slashes: `к/т`
                        |([А-ЯЁЎІ]\.)(?=\s?[А-ЯЁЎІ]) # Initials: `Д. [Свіфт]`
                        |((?<=\s)([а-яёўі]+\.)(?=\s[^\sА-ЯЁЎІ])) # Abbreviations with periods before anything except capitalized characters: `тыс. [студэнтаў]`
                        |((?<!\d)[012]?\d:[012345]\d(:[012345]\d)?(?!\d)) # Time and duration: `12:34`, `12:34:56`
                        |(\d*[A-ZА-ЯЁЎІ]+(\d+[A-ZА-ЯЁЎІ]*)+) # Alphanumeric codes: `BY1A2C33330000`
                        |([а-яА-ЯЁёЎўІі]+([\-\'‘’][а-яА-ЯЁёЎўІі]+)*) # Word-like tokens: `аб'ект`, `ха-ха`, `слова`, `ААН`
                        |[a-zA-Z]+ # Latin word-like tokens: `Google`
                        |((?<!\d)([1-9]\d{,2}(\s\d{3})+)(?!\d)) # Space-separated numbers: `1 000 000`
                        |(\d+\-[а-яёўі]+([\'‘’][а-яёўі]+)*) # Numerical expressions with cyrillic endings: `1-шы`
                        |(\d+(,\d+)?) # Numbers: `1,234`, `2025`
                        |[\.,:;\!\?…\-–—«»„“"\(\)\[\]\{\}\///%№#\^@_\+=\*<>~$€£₽℃℉×÷&§⁈°®©™] # Punctuation marks and symbols: `!`, `%`
                        |\s # Spaces
                        |[^\s]+) # Other characters not captured by prevous expression groups: `👻`
                        ''', 
                      re.X)

    matches = tokenPattern.findall(text.strip())
    output = tuple([result[0] for result in [[group for group in groups if group] for groups in matches] if result])
                 
    return output


def splitSentences(tokens):
    '''
    Segmentation of a token list into groups corresponding to sentences. The end of a sentence is detected at either at sentence-end punctuation marks like '.', or at text emoticons like ':)'.
    
    [ARGUMENTS]:
    - `tokens` (tuple) : The list of tokens belonging to a paragraph.

    [RETURNS]:
    -  `sentences` (tuple) : A tuple of tuples corresponding to sentences.

    [USAGE]:
    This operation is intended for use after tokenization and paragraph segmentation.
    '''
    # CHECK `TOKENS` VALUE VALIDITY
    if not isinstance(tokens, tuple): return None
    
    # DETECT SENTENCE BOUNDARIES
    sentenceBoundaries = ()
    for i, token in enumerate(tokens):
        # detect positions of sentence-end punctuation 
        if token in tokenCategories['sentenceEnd']:  sentenceBoundaries += (i,)
        # plaintext emoticons like ':)', ')))' are considered sentence-ending 
        elif ('(' in token or ')' in token) and len(token) > 1:
            if re.fullmatch(tokenCategories['emo'], token): sentenceBoundaries += (i,)

    # SPLIT TOKENS INTO GROUPS BY SENTENCE
    segments = ()
    if sentenceBoundaries:
        for i, boundary in enumerate(sentenceBoundaries):
            if i == 0:
                # sentence-end pattern at the beginning of the paragraph is added as a group
                if boundary == 0: segments += (tokens[0],)
                # tokens from the beginning to the first sentence-end pattern are added as a group
                else: segments += (tokens[0:boundary+1],)
            # tokens from the previous boundary to the current boundary are added as a group
            else: segments += (tokens[sentenceBoundaries[i-1]+1:boundary+1],)
        # if there are tokens after the last sentence-end pattern, add tokens from the last boundary to the end as a group
        if sentenceBoundaries[-1] < len(tokens) - 1:
            segments += (tokens[sentenceBoundaries[-1]+1:],)

        # finalize by removing spaces at sentence start
        sentences = ()
        for segment in segments:
            # skip segments that only contain a space
            if len(segment) == 1 and segment[0] == ' ': continue
            # remove spaces in the beginning of sentence groups
            elif len(segment) > 1 and segment[0] == ' ': sentences += (segment[1:],)
            # otherwise no modifications are made
            else: sentences += (segment,)

        return sentences
                
    # IF NO BOUNDARIES ARE DETECTED, THE TOKENS ARE CONSIDERED ONE SENTENCE GROUP 
    else: return (tokens,)


def annotateToken(token, toConllu = False, extended = True):
    '''
    Annotate a token regardless of whether it is present in the database. `(U)POS` values and features are specified at search result level since there can be multiple matches for a token.
    The following extended token types are optionally supported: Arabic and Roman numerals, abbreviations, punctuation marks, symbols, alphanumeric codes, date and time, Belarusian phone numbers, usernames, emails, top level URLs, some emoticons. See README for full description.
    
    [ARGUMENTS]:
    - `token` (str) : A word-level token.
    - `toConllu` (bool) OPTIONAL: The structure of token annotation.
      [VALUE OPTIONS]:
        - False DEFAULT : The output is similar to the return of database search functions. If there are no matches, 'Results' dictionary is omitted.
        - True : The output is mapped to the columns of a tabulated CoNLL-U file. The empty values belonging to mandatory CoNLL-U columns are populated with placeholders. There is always at least one item in 'Results' dictionary, so a placeholder result is generated if there are no matches.
    - `extended` (bool) OPTIONAL: This attribute indicates whether additional token types are included in the search.
      [VALUE OPTIONS]:
        - False : Only database results are returned.
        - True DEFAULT : Tokens are checked against extended token types as defined in `tokenCategories`, e.g. numbers, punctuation marks, symbols etc. See README for the definitions.

    [RETURNS]:
    - `output` (dict) : Annotated tokens, structured according to `toConllu` value. 'Results' dictionary is optional if `toConllu == False`.
      [If `toConllu == False`]: 
        {'Form': [token], 'Results': {1: { [formByID() output structure] }, ... }}
      [If `toConllu == True`]:
        {'FORM': [token], 'MISC': [...], 'Results': {1: {'LEMMA': [...], 'UPOS': [...], 'FEATS': [...]}, ...}}

    [USAGE]:
    This operation is intended to be used after tokenization.
    '''
    # CHECK FOR `TOKENS` VALUE VALIDITY
    if not isinstance(token, str): return None
    
    # RESET
    output = {}
    
    # DATABASE LOOKUP
    def DBresults(token):
        '''
        Format one or multiple results returned by a token database search. If `toConllu == True` and there were no results, a placeholder will be generated.

        [ARGUMENTS]:
        - `token` (str) : A token to look up in database.

        [RETURNS]:
        - `results` (dict) : A dictionary of annotated search results.
        OR
        - None (NoneType) : Returned if there are no database search results and `toConllu == False`. 
        '''
        # reset
        results, resultData = [None] * 2
        resultID = 1
        
        # first request with case sensitivity, repeat without sensitivity if there were no results
        search = formSearch(query = token, keepLetterCase = True, fastMode = True)
        if not search: search = formSearch(query = token, keepLetterCase = False, fastMode = True)    
        # requesting data for each result    
        if search:
            results = {}
            for result in search:
                if toConllu == False:  results[resultID] = formByID(formID = result); resultID += 1
                elif toConllu == True:
                    # adding a result, while skipping duplicates where all features except word stress are the same, since CoNLL-U doesn't support it
                    resultData = formByID(formID = result, toConllu = True, includeForm = False)
                    if resultData not in results.values(): results[resultID] = resultData; resultID += 1
        # add placeholder values for queries without matches
        elif (not search) and (toConllu == True): results = {1: {'LEMMA': '_', 'UPOS': 'X', 'FEATS': '_'}}

        return results

    # GENERATE TOKEN ANNOTATION
    if toConllu == False: output = {'Form': token, 'Results': {}}
    elif toConllu == True:  output = {'FORM': token, 'MISC': '_', 'Results': {}}

    if extended == False:
        # database lookup for word-like tokens
        if re.fullmatch(tokenCategories['word'], token):
            output['Results'] = DBresults(token)
        else:
            # everything else is empty
            if toConllu == True: output['Results'][1] = {'LEMMA': '_', 'UPOS': 'X', 'FEATS': '_'}

    elif extended == True:
        # "cheap" checks first
        if token in tokenCategories['punct']:
            if toConllu == False: output['Results'][1] = {'POS': 'PUNCT'}
            elif toConllu == True: output['Results'][1] = {'LEMMA': token, 'UPOS': 'PUNCT', 'FEATS': '_'}
        elif token in tokenCategories['sym']:
            if toConllu == False: output['Results'][1] = {'POS': 'SYM'} 
            elif toConllu == True: output['Results'][1] = {'LEMMA': token, 'UPOS': 'SYM', 'FEATS': '_'}
        elif token.isdigit():
            if toConllu == False: output['Results'][1] = {'POS': 'NUM'} 
            elif toConllu == True: output['Results'][1] = {'LEMMA': token, 'UPOS': 'NUM', 'FEATS': '_'}
        elif token in abbreviations['noStop']:
            if toConllu == False: output['Results'][1] = {'Abbr': True} 
            elif toConllu == True: output['Results'][1] = {'LEMMA': '_', 'UPOS': 'X', 'FEATS': 'Abbr=Yes'}
        elif ('(' in token or ')' in token) and len(token) > 1:
            if re.fullmatch(tokenCategories['emo'], token):
                if toConllu == False: output['Results'][1] = {'POS': 'SYM'} 
                elif toConllu == True: output['Results'][1] = {'LEMMA': token, 'UPOS': 'SYM', 'FEATS': '_'}
        elif ' ' in token and len(token) > 4:
            if re.fullmatch(tokenCategories['numSpace'], token):
                if toConllu == False: output['Results'][1] = {'POS': 'NUM'} 
                elif toConllu == True: output['Results'][1] = {'LEMMA': token, 'UPOS': 'NUM', 'FEATS': '_'}
        # database lookup for word-like tokens
        elif re.fullmatch(tokenCategories['word'], token):
            output['Results'] = DBresults(token)
        # checking against regex categories
        elif re.fullmatch(tokenCategories['num'], token): 
            if toConllu == False: output['Results'][1] = {'POS': 'NUM'} 
            elif toConllu == True: output['Results'][1] = {'LEMMA': token, 'UPOS': 'NUM', 'FEATS': '_'}
        elif re.fullmatch(tokenCategories['code'], token):
            if toConllu == False: output['Results'][1] = {'POS': 'PROPN'} 
            elif toConllu == True: output['Results'][1] = {'LEMMA': token, 'UPOS': 'PROPN', 'FEATS': '_'}
        elif re.fullmatch(tokenCategories['abbr'], token):
            if toConllu == False: output['Results'][1] = {'Abbr': True} 
            elif toConllu == True: output['Results'][1] = {'LEMMA': '_', 'UPOS': 'X', 'FEATS': 'Abbr=Yes'}
        
        # add placeholder values for queries without matches
        else: 
             if toConllu == True: output['Results'][1] = {'LEMMA': '_', 'UPOS': 'X', 'FEATS': '_'}

    if (not output['Results']) and (toConllu == False): del output['Results']

    return output


def annotateSentence(tokens, toConllu = False, extended = True):
    '''
    Convert a list of tokens into a numbered list with JSON-like or CoNLL-U annotation.
    
    [ARGUMENTS]:
    - `tokens` (tuple) : A tuple of tokens.
    - `toConllu` (bool) OPTIONAL: The structure of token annotation.
      [VALUE OPTIONS]:
        - False DEFAULT : The output is similar to the return of database search functions. If there are no matches, 'Results' dictionary is omitted.
        - True : The output is mapped to the columns of a tabulated CoNLL-U file. The empty values belonging to mandatory CoNLL-U columns are populated with placeholders. There is always at least one item in 'Results' dictionary, so a placeholder result is generated if there are no matches.
    - `extended` (bool) OPTIONAL: This attribute indicates whether additional token types are included in the search.
      [VALUE OPTIONS]:
        - False : Only database results are returned.
        - True DEFAULT : Tokens are checked against extended token types as defined in `tokenCategories`, e.g. numbers, punctuation marks, symbols etc. See README for the definitions.

    [RETURNS]:
    - `output` (dict) : Nummered and annotated tokens, structured according to `toConllu` value.

    [USAGE]:
    This operation is intended to be used after sentence segmentation, as the token's number denotes its position within the sentence.
    '''
    # CHECK FOR `TOKENS` VALUE VALIDITY
    if not isinstance(tokens, tuple): return None
    
    # RESET
    tokenData = None
    output = {}
    tokenID = 1

    # GENERATE TOKEN ANNOTATION
    for i, token in [item for item in enumerate(tokens) if item[1] != ' ']:

        tokenData = annotateToken(token, toConllu, extended)
    
        # check for SpaceAfter value
        if i < (len(tokens) - 1):
            if tokens[i+1] != ' ':
                if toConllu == False: tokenData['SpaceAfter'] = False
                elif toConllu == True: tokenData['MISC'] = 'SpaceAfter=No'
    
        output[tokenID] = tokenData
        tokenID += 1
    
    return output


def annotateText(text, toConllu = False, extended = True):
    '''
    Segment plain text into nested numbered paragraphs, sentences and word-level tokens, and provide token annotation. Paragraphs are segmented at `\n` new line character.

    [ARGUMENTS]:
    - `text` (str) : Plain text with paragraphs and sentences.
    - `toConllu` (bool) OPTIONAL: The structure of token annotation.
      [VALUE OPTIONS]:
        - False DEFAULT : The output is similar to the return of database search functions. If there are no matches, 'Results' dictionary is omitted.
        - True : The output is mapped to the columns of a tabulated CoNNL-U file. The empty values belonging to mandatory CoNLL-U columns are populated with placeholders. There is always at least one item in 'Results' dictionary, so a placeholder result is generated if there are no matches.
    - `extended` (bool) OPTIONAL: This attribute indicates whether additional token types are included in the search.
      [VALUE OPTIONS]:
        - False : Only database results are returned.
        - True DEFAULT : Tokens are checked against extended token types as defined in `tokenCategories`, e.g. numbers, punctuation marks, symbols etc. See README for the definitions.

    [RETURNS]:
    - `output` (dict) : Segmented, tokenized and annotated text. 
    '''
    # check `text` value validity
    if not isinstance(text, str): return None
    
    # reset
    output = {'Paragraphs': {}}
    paragraphID = 1
    
    # paragraphs are split at `\n` new line character
    paragraphs = [paragraph.strip() for paragraph in text.split('\n') if paragraph]
    
    for paragraph in paragraphs:
        tokensApprox = tokenize(paragraph)
        sentenceID = 1
        sentences = ()

        # finalize token list
        tokensToRegroup = ()
        # search for abbreviations to regroup with `.` full stop marks
        for i, token in [item for item in enumerate(tokensApprox) if (item[0] > 0) and (item[1] == '.')]:
            if tokensApprox[i-1].lower() in abbreviations['stopNonFinal']: tokensToRegroup += (i - 1,)                   
        # regroup tokens
        if tokensToRegroup:
            tokens = ()
            for i, token in enumerate(tokensApprox):
                if i in tokensToRegroup: tokens += (token + '.',)
                elif i - 1 in tokensToRegroup: continue
                else: tokens += (token,)
        else: tokens = tokensApprox
                    
        # GENERATE SENTENCE LEVEL ANNOTATION
        sentences = {}
        sentenceID = 1
        sentenceTokens = ()
        
        for sentence in splitSentences(tokens): 
            sentences[sentenceID] = {'Text': ''.join(sentence), 'Tokens': annotateSentence(sentence, toConllu, extended)}
            sentenceID += 1

        output['Paragraphs'][paragraphID] = {'Text': paragraph, 'Sentences': sentences}
        paragraphID += 1 

    return output




# CONLL-U TABLE OPERATIONS

def generateConllu(annotatedText):
    '''
    Generate a tab-separated CoNLL-U table from annotated text in dictionary format, mapping the latter to the columns `ID`, `FORM`, `LEMMA`, `UPOS`, `XPOS`, `FEATS`, `HEAD`, `DEPREL`, `DEPS` & `MISC`. Only `ID`, `FORM`, `LEMMA`, `UPOS`, `MISC` columns are populated, the rest use the standard '_' placeholer.

    [ARGUMENTS]:
    - `annotatedText` (dict) : Annotated text as outputted by `annotateText()` function with `toConllu == True`.

    [RETURNS]:
    - `output` (str) : Tab-separated CoNLL-U table.
    '''
    # check the validity of `annotatedText` value
    if (not isinstance(annotatedText, dict)) or (isinstance(annotatedText, dict) and 'Paragraphs' not in annotatedText.keys()): return None

    # reset
    output = '' 

    for paragraphID in sorted(annotatedText['Paragraphs'].keys()):
        outputParagraphID = f'p{str(paragraphID)}'
        # add paragraph header row
        output += f'newpar id = {outputParagraphID}\n'
        
        for sentenceID in sorted(annotatedText['Paragraphs'][paragraphID]['Sentences'].keys()):
            outputSententenceID = f'{outputParagraphID}s{str(sentenceID)}'
            # add sentence header row
            output += f'# sent_id = {outputSententenceID}\n# text = {annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Text']}\n'
            # add token rows
            for tokenID in sorted(annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'].keys()):
                # tokens with one search result use basic one-row structure
                if len(annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['Results']) == 1:
                    output += '\t'.join(
                        (str(tokenID),
                        annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['FORM'],
                        annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['Results'][1]['LEMMA'],
                        annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['Results'][1]['UPOS'],
                        '_',
                        annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['Results'][1]['FEATS'],
                        '_', '_', '_',
                        annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['MISC'])) + '\n'

                # tokens with multiple search results have the main row as the header and a node for each result
                elif len(annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['Results']) > 1:
                    # add token header row
                    output += '\t'.join((str(tokenID), annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['FORM'], '_', '_', '_', '_', '_', '_', '_', annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['MISC'])) + '\n'
                    # add result nodes
                    for result in sorted(annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['Results'].keys()):
                        outputResultID = '.'.join((str(tokenID), str(result)))

                        output += '\t'.join(
                            (outputResultID,
                             '_',
                             annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['Results'][result]['LEMMA'],
                             annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['Results'][result]['UPOS'],
                             '_',
                             annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['Results'][result]['FEATS'],
                             '_', '_', '_', '_')) + '\n'

                # placeholder for the unlikely event of the absense of search results
                elif len(annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['Results']) == 0:
                    output += '\t'.join((str(tokenID), annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['FORM'], '_', 'X', '_', '_', '_', '_', '_', annotatedText['Paragraphs'][paragraphID]['Sentences'][sentenceID]['Tokens'][tokenID]['MISC'])) + '\n'

            # a sentence must be separated by an empty line
            output += '\n'

    return output.strip()


def completeConllu(incompleteConllu, extended = True):
    '''
    Parse a CoNLL-U tble and fill `LEMMA`, `UPOS` & `FEATS` values for tokens that have placeholders in these columns.

    [ARGUMENTS]:
    - `incompleteConllu` (str) : CoNLL-U table as a string. To be completed a token must have the placeholder values {'LEMMA': '_', 'UPOS': 'X', 'FEATS': '_'} and no children nodes denoted by IDs in `1.1` format.
    - `extended` (bool) OPTIONAL: This attribute indicates whether additional token types are included in the search.
      [VALUE OPTIONS]:
        - False : Only database results are returned.
        - True DEFAULT : Tokens are checked against extended token types as defined in `tokenCategories`, e.g. numbers, punctuation marks, symbols etc. See README for the definitions.

    [RETURNS]:
    - `output` (str) : Tab-separated CoNLL-U table with token annotation added where possible.
    '''
    # CHECK VALIDITY FOR `incompleteConllu` VALUE
    if not isinstance(incompleteConllu, str): return None
    
    # RESET
    completedLines = ()
    output = ''

    # PARSE AND SEARCH
    lines = incompleteConllu.split('\n')
    for i, line in enumerate(lines):  
        # retain empty lines
        if line == '': completedLines += ('',)
        
        # detect token rows by tabulated structure
        elif '\t' in line:
            columns = line.split('\t')
            # check whether the token is annotated
            if columns[0].isdigit() and len(columns) == 10 and (columns[2], columns[3], columns[5]) == ('_', 'X', '_'):
                # check for the lack of child nodes by '.' in `ID` column
                if i < (len(lines) - 1):
                    if '.' in lines[i+1].split('\t')[0]: break

                # request annotation
                search = annotateToken(columns[1], True, extended)
                
                # tokens with one search result use basic one-row structure
                if len(search['Results']) == 1:
                    completedLines += ('\t'.join(columns[0:2] + 
                                                 [search['Results'][1]['LEMMA'], search['Results'][1]['UPOS']] +
                                                 [columns[4]] +
                                                 [search['Results'][1]['FEATS']] +
                                                 columns[6:]),)

                # tokens with multiple search results have the main row as the header and a node for each result
                elif len(search['Results']) > 1:                    
                    # add token header
                    completedLines += ('\t'.join(columns[:3] + ['_'] + columns[4:]),)  
                    # add result nodes
                    for result in sorted(search['Results'].keys()):
                        completedLines += ('\t'.join(
                            ['.'.join((columns[0], str(result))),
                             '_',
                             search['Results'][result]['LEMMA'],
                             search['Results'][result]['UPOS'],
                             '_',
                             search['Results'][result]['FEATS']] + ['_'] * 4),)
                        
        # ADDING WITHOUT MODIFICATION: 
            # not an empty token
            else: completedLines += (line,) 
        # non-tabulated row (header)
        else: completedLines += (line,)

    # REASSEMBLE CONLLU
    output = '\n'.join(completedLines)

    return output


# STARTUP

if __name__ == 'slounik':
    setStopWords()