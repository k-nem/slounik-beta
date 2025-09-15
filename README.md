# Slounik 
`slounik` is a Python module that performs the tokenization, lemmatization, morphological analysis and annotation of Belarusian text. It uses [Universal Dependencies](https://universaldependencies.org/) annotation standard ([UD-BE](https://universaldependencies.org/be/index.html)) and supports [CoNLL-U](https://universaldependencies.org/format.html) output. Where possible, [UD Belarusian HSE](https://universaldependencies.org/treebanks/be_hse/index.html) approach to annotation was adopted. UTF-8 encoding is assumed and should be used for input.

## Data source
 The morhological analysis is largely based on the dictionary database which can be found on https://github.com/k-nem/BelGrammarDB with the detailed documentation. The following changes were applied to the database version of this module:
- `Sources` & `Ortho` columns were dropped from `Form` & `Variant` tables since these values are not used in morphological annotation.
- For the speed of processing, `Lowercase` & `Len` columns were added to `Form` & `Lemma` tables. They contain lowercase versions and the lengths in characters correspondingly. This increases the file size but allows to forego slow SQL string operations during search.
- The original alphabetical variant IDs were replaced with numerical, e.g., `a` becomes `1`, etc.

### Attribute names (database columns)
- `Type` column name (`Lemma` table in the database) is converted into `{POS}Type` on output generation, e.g., an adjective's type is labelled as `AdjType`, to adhere to UD standard.
- Attributes that correspond to reserved words in SQLite are converted on input and output, so SQLite `Cas` becomes `Case`, `Len` becomes `Length` as function attributes. This allows to input arguments in intuitive UD format as opposed to SQLite schema names.

### Values
The content of the annotation corresponds to the database values, see README at https://github.com/k-nem/BelGrammarDB. An exception is the conversion of logically Boolean SQLite values (`0` & `1` integers corresponding to `False` & `True`) to their CoNLL-U and Pythonic versions:
- SQLite "boolean" integer to UD string: `0 → 'No'`, `1 → 'Yes'`.
- UD string to integer: `'No' → 0`, `'Yes' → 1`.
- SQLite "boolean" integer to UD `Animacy` value string: `0 → 'Inan'`, `1 → 'Anim'`.
- UD `Animacy` value to integer: `'Inan' → 0`, `'Anim' → 1`.
- SQLite "boolean" integer to Python Boolean: `0 → False`, `1 → True`.
- Python Boolean to integer: `False → 0`, `True → 1`.

Most functions have `toConllu` flag which derermines the output format. `toConllu == True` converts logically Boolean values into UD strings, and `toConllu == False` outputs such values as Pythonic Boolean. 

**⚠️ Note**: Functions accept arguments in Pythonic format. 

## Installation
The installation follows the standard Python module import procedure.
1. Clone this repository to your machine.
2. Import `sys` module in your Python script:
    ```
    import sys
    ```
3. Append the path to the cloned repository's directory (where `slounik.py` is) to `sys.path`:
    ```
    sys.path.append('{your local path}/slounik')
    ```
4. Import `slounik` module in your Python script...
    
    ...using full name:
    ```
    import slounik
    ```
    ...or with a shortcut:
    ```
    import slounik as sl
    ```
    where any valid shortcut can be used instead of `sl`.
5. Use the module's functions by adding the name from **#4** before a function's name:
    ```
    slounik.formSearch('Ева')
    ```

## Segmentation
### Paragraph segmentation
In plain text the paragraph boundaries are detected at `\n` new line symbol.
### Sentence segmentation
Sentence segmentation takes place after tokenization. A paragraph token group is split into sentence token sub-groups at the following conditions:
- Conventional sentence end punctuation: `.`, `!`, `?`, `…`, `⁈`, `...`, `?..`, `!..`, `?!`, `???`, `!!!`. The pattern can be requested by `sentenceEnd` key from `slounik.tokenCategories` dictionary.
- Emoticons (see Extended token types)

If no such tokens are detected, it is assumed that the token group is one sentence.

## Tokenization
The initial tokenization is performed by applying the following expression to plain text via `re.findall()` function:
```
'''
[а-яА-ЯЁёУўІі]{1,2}[23²³]  # Units of measurements with digits: `м2`
|(?<!\d)((8\s?\(?\d{3}\)?)|(\(?\+?\d{3}\s?\(?\d{2}\)?))\s?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}(?!\d) # Phone numbers: `+375(33)123-45-67`, `8(017)2613202`
|(?<!\d)[0123]\d\.[01]\d(\.((\d{2})|(\d{4})))?(?!\d) # Dot-separated dates: `01.02.03`
|(@[a-zA-Z_\.]+(?![\.\w])) # Usernames: `@user`
|([a-zA-Z_\.]+@[a-zA-Z\-]+(\.[a-zA-Z]+)+) # Email adresses: `a_b@mail.com.by`
|(http(s)?://)?(www\.)?[a-zA-Z-]+(\.[a-zA-Z]+)+(/.+)? # URLs: `https://www.domain.com.by/home?=213`
|((?=[MDCLXVI])M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})) # Roman numerals: `XXI`
|([\(\)]{3,}|\.\.\.|\?\.\.|\!\.\.|\?\!|,\s?\-|[:;]\-?[\(\)]+|°[CС]) # Some multi-character symbol sequences: `...`, `?..`, `?!`, `))))`, `:)`, `°C`, `,-`
|([а-яА-ЯЁёЎўІі]+\.[а-яА-ЯЁёЎўІі]+\.) # Compound abbreviations with periods: `н.э.`
|([А-ЯЁЎІ]?[а-яёўі]+\.\-[а-яёўі]+\.) # Compound abbreviations with periods and hyphens: `с.-г.`
|([а-яА-ЯЁёЎўІі]+\/[а-яА-ЯЁёЎўІі]+) # Compound abbreviations with slashes: `к/т`
|([А-ЯЁЎІ]\.)(?=\s?[А-ЯЁЎІ]) # Initials: `Д. [Свіфт]`
|((?<=\s)([а-яёўі]+\.)(?=\s[^\sА-ЯЁЎІ])) # Abbreviations with periods before anything except capitalized characters: `тыс. [студэнтаў]`
|((?<!\d)[012]?\d:[012345]\d(:[012345]\d)?(?!\d)) # Time and duration: `12:34`, `12:34:56`
|(\d*[A-ZА-ЯЁЎІ]+(\d+[A-ZА-ЯЁЎІ]*)+) # Alphanumeric codes: `BY1A2C33330000`
|[а-яА-ЯЁёУўІі]+(([\'‘’][а-яА-ЯЁёУўІі]+)|(-[а-яА-ЯЁёУўІі]+){1,2})? # Word-like tokens: `аб'ект`, `ха-ха`, `слова`, `ААН`
|[a-zA-Z]+ # Latin word-like tokens: `Google`
|((?<!\d)([1-9]\d{,2}(\s\d{3})+)(?!\d)) # Space-separated numbers: `1 000 000`
|(\d+\-[а-яёўі]+([\'‘’][а-яёўі]+)*) # Numerical expressions with cyrillic endings: `1-шы`
|(\d+(,\d+)?) # Numbers: `1,234`, `2025`
|[\.,:;\!\?…\-–—«»„“"\(\)\[\]\{\}\///%№#\^@_\+=\*<>~$€£₽℃℉×÷&§⁈°®©™] # Punctuation marks and symbols: `!`, `%`
|\s # Spaces
|[^\s]+ # Other characters not captured by prevous expression groups: `👻`
''', re.X
```
### Tokens with spaces
The only token type that can contain spaces is a number with space-separated thousand groups like `1 000 000`.

## Sentence boundary vs. abbreviation with `.` full stop
Contractions with `.` full stop characters pose a problem for both word-level tokenization and sentence segmentation, since it is impossible to formally distinguish them from a word at the end of a sentence. During initial tokenization such sequences are split into two tokens, one word-like token and one punctuation token for the full stop. 

Additionally, the following subset of contractions that are improbable to be at the end of a sentence is marked for a separate check: `акад.`, `б.`, `бухг.`, `в.`, `воз.`, `вул.`, `гл.`, `гр.`, `дац.`, `заг.`, `зб.`, `нам.` `напр.`, `параўн.`, `праф.`, `р.`, `св.`, `сп.`, `тав.`. The list can be requested by `stopNonFinal` key from `slounik.abbreviations` dictionary.

If one of these abbreviations is detected in a sequence with a full stop, the sequence is grouped into one token and marked with `Abbr=Yes` (`'Abbr': True`). Otherwise, the tokens remain separate. Paragraph and sentence tokenization then proceeds normally, and sentences are split by `.` tokens.

## Token categories
### Word tokens
Word tokens can include `'` apostrophes or `-` hyphens. If a word-like token is not matched in the database, the part of speech is tagged as `X`. The pattern can be requested by `word` key from `slounik.tokenCategories` dictionary.
|Feature|Value|
|:-|:-|
|Detection|RegEx|
|Definition|`[а-яА-ЯЁёУўІі]+(([\'‘’][а-яА-ЯЁёУўІі]+)\|(-[а-яА-ЯЁёУўІі]+){1,2})?`|
|Examples|`аб'ект`, `ха-ха`, `слова`, `ААН`|
|`UPOS` value|As in database if matched, otherwise `X`|
|`FEATS` value|As in database if matched, otherwise `_`|

### Extended token types
In the current implementation the databased remains unmodified as it is assembled in https://github.com/k-nem/BelGrammarDB. In addition to the lexical tokens present in the dictionary database, it is possible to approximate some other token types, as defined either in static lists or with regular expressions (see below). This option is enabled by default and can be disabled by passing `extended = False` flag in annotation functions. The classification rules can be requested from `slounik.tokenCategories` dictionary (all keys except `word` & `sentenceEnd`).

**Note**: Tokenization RegEx patterns use lookarounds, while token classification does not need the context because it is applied to already tokenized strings. Tokenizer also has more expressions than this classification, though they largely overlap, because it extracts some token types that later remain unclassified (`UPOS = X`).

|Group|Category|Detection|Definition|Examples|`UPOS` value|`FEATS` value|
|:-|:-|:-|:-|:-|:-|:-|
|Non-alphanumeric|Punctuation marks|Literal match|`.` `,` `:` `;` `!` `?` `…` `-` `–` `—` `«` `»` `„` `“` `"` `(` `)` `[` `]` `{` `}` `⁈`|~|`PUNCT`||
|Non-alphanumeric|Multi-charachter punctuation|Literal match|`...` `?..` `!..` `!!!` `???` `?!` `-,` `- ,` `–,` `– ,`|~|`PUNCT`||
|Non-alphanumeric|Symbols|Literal match|`\`, `/`, `%`, `№`, `#`, `^`, `+`, `=`, `*`, `<`, `>`, `~`, `×`, `÷`, `@`, `_`, `&`, `$`, `§`, `€`, `£`, `₽`, `℃`, `°С`, `℉`, `°`, `®`, `©`, `™`|~|`SYM`||
|Non-alphanumeric|Emoticons|RegEx|`(\({3,}\|\){3,}\|[:;]\-?[\(\)]+)`|`:)`, `:-(`, `)))))))`|`SYM`||
|Abbreviations|Units of measurements|RegEx|`а-яА-ЯЁёУўІі]{1,2}[23²³]`|`км2`, `м³`||`Abbr=Yes`|
|Abbreviations|Compounds with `.`full stops|RegEx|`[а-яА-ЯЁёУўІі]+\.[а-яА-ЯЁёУўІі]+\.`|`н.э.`||`Abbr=Yes`|
|Abbreviations|Compounds with `.`full stops and `-`hyphens|RegEx|`[А-ЯЁУІ]?[а-яёўі]+\.\-[а-яёўі]+\.`|`с.-г.`||`Abbr=Yes`|
|Abbreviations|Compounds with `/`slashes|RegEx|`[а-яА-ЯЁёУўІі]+\/[а-яА-ЯЁёУўІі]+`|`к/т`||`Abbr=Yes`|
|Abbreviations|Contractions with `.`full stops|RegEx|`[а-яА-ЯЁёУўІі]+\.`|`тыс.`||`Abbr=Yes`|
|Abbreviations|Initials|RegEx|`[А-ЯЁУІ]\.`|`Д. [Свіфт]`||`Abbr=Yes`|
|Abbreviations|Numerical expressions|RegEx|`\d+\-[а-яёўі]+([\'‘’][а-яёўі]+)*`|`1-шы`||`Abbr=Yes`|
|Non-lexical|Alphanumeric codes|RegEx|`\d*[A-ZА-ЯЁУІ]+(\d+[A-ZА-ЯЁУІ]*)+`|`A10001222030B`|`PROPN`||
|Numerals|Whole or fractional numbers|RegEx|`\d+([,\.]\d+)?`|`2050`, `1,234`, `2.34`|`NUM`||
|Numerals|Numbers with space-separated thousand groups|RegEx|`\d{1,3}(\s\d{3})+`|`1 000 000`|`NUM`||
|Numerals|Dates|RegEx|`[0123]\d\.[01]\d(\.((\d{2})\|(\d{4})))?`|`01.02.03`, `01.02.2003`|`NUM`||
|Numerals|Time|RegEx|`[012]?\d:[012345]\d(:[012345]\d)?`|`01:23`, `01:23:45`|`NUM`||
|Numerals|Roman numerals|RegEx|`M*(C[MD]\|D?C{0,3})(X[CL]\|L?X{0,3})(I[XV]\|V?I{0,3})`|`LXXVIII`, `XX`|`NUM`||
|Numerals|Phone numbers|RegEx|`((8\s?\(?\d{3}\)?)\|(\(?\+?\d{3}\s?\(?\d{2}\)?))\s?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}`|`8(017)123-45-67`, `+375(12)3456789`|`NUM`||

The following abbreviations cannot be distinguished with RegEx:

`в-аў`, `п-аў`, `р-н`, `т-ва`, `ун-т`, `млн`, `млрд`, `см`, `га`, `м`, `мм`, `мг`, `кг`, `км`, `л`, `дж`, `кал`, `ккал`, `гц`, `мін`, `сут`.

A token is checked against the list, which can be requested by `noStop` key from `slounik.abbreviations` dictionary, and marked with `Abbr=Yes` (`'Abbr': True`) if it has a match.

## Stop words
Lemmas can be excluded from search results by adding them to the list of stop words under `slounik.stopWords` variable. This is done via `setStopWords()` function, see documentation below. The default location of the list is `slounik/assets/stop_words.txt`. It can only include lemma IDs (`ID` in `Lemma` database table) separated with commas as in `1, 2, 3`. The content of this file is automatically assigned to `slounik.stopWords` variable on the module's import. It could be overriden by another call to `setStopWords()` function, find its documentation below.

## Default paths
**⚠️ ADVANCED USERS ONLY**: It is possible to change the defaults paths to the database, stop words list file and CSV export location by modifying `defaults` dictionary on top of `slounik.py` **at your own risk**. It can be convenient if one needs to regularly use a modified database file, stop word file or CSV export locations.

## Functions

Do use `help()` function to request any function's documentation. Example: `help(slounik.formByID)`.

### `formSearch`
Find all forms than match the query and return their full form, lemma and variant data.
#### [ARGUMENTS]:
- **`query`** (str) : 
A word form to look for in the database. It can be submitted with or without the keyword: 'а' or `query = 'а'`. 
    It supports [globbing](https://en.wikipedia.org/wiki/Glob_(programming)):
    - `?` : Any character once.
    - `*` : Zero or more of any characters.
    - `[абв]` or `[а-в]` : Any character in the range specified in the brackets, once.
    - `[!абв]` or `[!а-в]` : Any character NOT in the range specified in the brackets, once.
- **Attribute** (keyword argument) OPTIONAL : Form or lemma database attributes in *keyword = value* format, e.g., `Case = 'Nom'`. 

    See the attribute options listed below. For available categorical values refer to [the database documentation](https://github.com/k-nem/BelGrammarDB). Keywords are case-insensitive. Values are case-sensitive and use their respective Python data types: `POS = 'NOUN'`, `Person = 2`, `Abbr = True`.

    *Note*: Attributes that can be applied to both form and lemma level (`Degree`, `Person`, `Gender`, `Tense`, `Animacy`, `VerbForm`) must to be prefixed with `f_` and `l_` correspondingly. For example, `Degree` column value in Lemma database table is submitted under `l_Degree` keyword, the column of the same name in Form table is denoted by `f_Degree`. 

    [ATTRIBUTES]:
    - Form attributes: `Accent`, `Case`, `Number`, `Mood`, `Short`, `f_Degree`, `f_Person`, `f_Gender`, `f_Tense`, `f_Animacy`, `f_VerbForm`.
    - Lemma attributes: `POS`, `AdjType`, `NumType`, `PronType`, `InflClass`, `Voice`, `Aspect`, `Abbr`, `NumForm`, `Personal`, `Origin`, `Poss`, `Reflex`, `SubCat`, `l_Degree`, `l_Person`, `l_Gender`, `l_Tense`, `l_Animacy`, `l_VerbForm`.
- **`keepLetterCase`** (bool) OPTIONAL : Case sensitivity of the search.

    [VALUE OPTIONS]:
    - `False` DEFAULT: Case-insensitive search.
    - `True` : Case-sensitive search.
- **`fastMode`** (bool) : Output format which affects the speed of the search.

    [VALUE OPTIONS]:
    - `False` DEFAULT: All non-empty form and lemma attributes, as well as the form's variant, are returned for each result in dictionary format.
    - `True` : Only form IDs are returned, but the search is significantly faster. This format is used as an intermediate step for some operations.
- **`length`** (int) OPTIONAL : The length of forms in characters.

#### [RETURNS]:
- **`output`** (tuple) : 

    [If `fastMode == False`]: A tuple of search results, sorted alphabetically by form, each represented by a dictionary with the following keys:
    - `FormData` (dict) : Non-empty form attributes.
    - `LemmaData` (dict) : Non-empty attributes of the form's lemma.
    - `Variant` (int) : The form's variant within the parent lemma.

    OR

    [If `fastMode == True`]: A tuple of integer form IDs sorted alphabetically by form.

OR
- **`None`** (NoneType) : Returned if search does not yield any results.

#### Examples
```
formSearch('афалін')

[Output]:

({'FormData': {'ID': 1996051,
   'Form': 'афалін',
   'Accent': '5',
   'Case': 'Gen',
   'Number': 'Plur'},
  'LemmaData': {'ID': 76959,
   'Lemma': 'афаліна',
   'POS': 'NOUN',
   'InflClass': '2d',
   'Gender': 'Fem',
   'Animacy': True},
  'Variant': 1},
 {'FormData': {'ID': 1996053,
   'Form': 'афалін',
   'Accent': '5',
   'Case': 'Acc',
   'Number': 'Plur'},
  'LemmaData': {'ID': 76959,
   'Lemma': 'афаліна',
   'POS': 'NOUN',
   'InflClass': '2d',
   'Gender': 'Fem',
   'Animacy': True},
  'Variant': 1})
```

```
formSearch(query = 'Е??а', keepLetterCase = True, l_gender = 'Fem')

[Output]:

({'FormData': {'ID': 2773763,
   'Form': 'Езва',
   'Accent': '1',
   'Case': 'Nom',
   'Number': 'Sing'},
  'LemmaData': {'ID': 158464,
   'Lemma': 'Езва',
   'POS': 'PROPN',
   'InflClass': '2d',
   'Gender': 'Fem'},
  'Variant': 1},
 {'FormData': {'ID': 2773886,
   'Form': 'Елка',
   'Accent': '1',
   'Case': 'Nom',
   'Number': 'Sing'},
  'LemmaData': {'ID': 158480,
   'Lemma': 'Елка',
   'POS': 'PROPN',
   'InflClass': '2d',
   'Gender': 'Fem'},
  'Variant': 1})
```

### `formByID`
Request a form's data by its form ID.

#### [ARGUMENTS]:
- **`formID`** (int) : Form ID as it is stored in the `ID` column of `Form` database table.
- **`toConllu`** (bool) OPTIONAL : Output format.
    [VALUE OPTIONS]:
    - `False` DEFAULT : Pythonic format. Form, lemma and variant data are separated, each non-empty attribute is outputted as a key-value pair.
    - `True` : The output is grouped into `FORM`, `LEMMA`, `UPOS`, `FEATS` according to CoNLL-U table structure.
- **`includeForm`** (bool) OPTIONAL : Whether `FORM` value is included in CoNLL-U output. Has effect only if `toConllu == True`. This option is used for an intermediate step in CoNLL-U generation, where form is available as a token.

    [VALUE OPTIONS]:
    - `False` DEFAULT : `FORM` value is included in the output.
    - `True` : Only `LEMMA`, `UPOS` and `FEATS` are returned.

#### [RETURNS]:
- **`output`** (dict) : A dictionary of the form's attributes.
    
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
- **`None`** (NoneType) : Returned if the form ID does not exist. 

#### Examples
```
formByID(14233)

[Output]:

{'FormData': {'ID': 14233,
  'Form': 'аблётаны',
  'Accent': '4',
  'Gender': 'Masc',
  'Case': 'Nom',
  'Number': 'Sing'},
 'LemmaData': {'ID': 1533,
  'Lemma': 'аблётаны',
  'POS': 'ADJ',
  'AdjType': 'Rel',
  'Degree': 'Pos'},
 'Variant': 1}
```

```
formByID(14233, toConllu = True, includeForm = False)

[Output]:

{'LEMMA': 'аблётаны',
 'UPOS': 'ADJ',
 'FEATS': 'AdjType=Rel|Case=Nom|Degree=Pos|Gender=Masc|Number=Sing'}
```

### `lemmaSearch`
Find all lemmas (dictionary forms) that match the query and return their data.

#### [ARGUMENTS]:
- **`query`*** (str) : A word form to look for in the database. It can be submitted with or without the keyword: 'а' or `query = 'а'`. 
    It supports [globbing](https://en.wikipedia.org/wiki/Glob_(programming)):
    - `?` : Any character once.
    - `*` : Zero or more of any characters.
    - `[абв]` or `[а-в]` : Any character in the range specified in the brackets, once.
    - `[!абв]` or `[!а-в]` : Any character NOT in the range specified in the brackets, once.
- **Attribute** (keyword argument) OPTIONAL : Any lemma database attribute in *keyword = value* format, e.g., `Gender = 'Masc'`.

    Keywords are not case sensitive and should not be put in quotation  marks. 
    Values are case sensitive and use their respective Python data types: POS = 'NOUN', Person = 2, Animacy = True.

    [ATTRIBUTES]: 

    `POS`, `AdjType`, `NumType`, `PronType`, `InflClass`, `Voice`, `Aspect`, `Abbr`, `NumForm`, `Personal`, `Origin`, `Poss`, `Reflex`, `SubCat`, `Degree`, `Person`, `Gender`, `Tense`, `Animacy`, `VerbForm`.
- **`keepLetterCase`** (bool) OPTIONAL : Case sensitivity of the search.

    [VALUE OPTIONS]:
    - `False` DEFAULT: Case-insensitive search.
    - `True` : Case-sensitive search.
- **`fastMode`** (bool) : Output format which affects the speed of the search.

    [VALUE OPTIONS]:
    - `False` DEFAULT: All non-empty lemma attributes are returned for each result in dictionary format.
    - `True` : Only lemma IDs are returned, but the search is significantly faster. This format is used as an intermediate step for some operations.
- `length` (int) OPTIONAL : The length of forms in characters.

#### [RETURNS]:
- **`output`** (tuple) : 

    [If `fastMode == False`]: A tuple of search results, sorted alphabetically by lemma, each represented by a dictionary with non-empty lemma attributes.

    OR

    [If `fastMode == True`]: A tuple of integer lemma IDs sorted alphabetically by lemma.

OR
- **`None`** (NoneType) : Returned if search does not yield any results.

#### Examples
```
lemmaSearch(query = 'аа*й', Animaсy = True, POS = 'NOUN')

[Output]:

({'ID': 69842,
  'Lemma': 'аагоній',
  'POS': 'NOUN',
  'InflClass': '1d',
  'Gender': 'Masc'},)
```

### `lemmaByID`
Request a lemma's data by its lemma ID.

#### [ARGUMENTS]:
- **`lemID`** (int) : Lemma ID as it is stored in the `ID` column of `Lemma` database table.

#### [RETURNS]:
- **`output`** (dict) : A dictionary of non-empty lemma attributes.

OR
- **`None`** (NoneType) : Returned if the lemma ID does not exist. 

#### Examples
```
lemmaByID(210293)

[Output]:

{'ID': 210293,
 'Lemma': 'прыляпіць',
 'POS': 'VERB',
 'Aspect': 'Perf',
 'SubCat': 'Tran'}
```

### `allForms`
Request a lemma's full paradigm by lemma ID.

#### [ARGUMENTS]:
- **`lemID`** (int) : Lemma ID as it is stored in the `ID` column of `Lemma` database table.

#### [RETURNS]:
- **`output`** (tuple) : A tuple of the lemma's forms as dictionaries with all non-empty form attributes.

OR
- **`None`** (NoneType) : Returned if the lemma ID does not exist. 

#### Examples
```
allForms(120900)

[Output]:

{'LemmaData': {'ID': 120900,
  'Lemma': 'паўпралетарыят',
  'POS': 'NOUN',
  'InflClass': '1d',
  'Gender': 'Masc',
  'Abbr': True},
 'Variants': ({'Variant': 1,
   'Paradigm': ({'ID': 2424711,
     'Form': 'паўпралетарыят',
     'Accent': '13',
     'Case': 'Nom',
     'Number': 'Sing'},
    {'ID': 2424712,
     'Form': 'паўпралетарыяту',
     'Accent': '13',
     'Case': 'Gen',
     'Number': 'Sing'},
    {'ID': 2424713,
     'Form': 'паўпралетарыяту',
     'Accent': '13',
     'Case': 'Dat',
     'Number': 'Sing'},
    {'ID': 2424714,
     'Form': 'паўпралетарыят',
     'Accent': '13',
     'Case': 'Acc',
     'Number': 'Sing'},
    {'ID': 2424715,
     'Form': 'паўпралетарыятам',
     'Accent': '13',
     'Case': 'Ins',
     'Number': 'Sing'},
    {'ID': 2424716,
     'Form': 'паўпралетарыяце',
     'Accent': '13',
     'Case': 'Loc',
     'Number': 'Sing'})},)}
```

### `tokenize`
Converts a plain text in Belarusian into a tuple of word-level tokens.

#### [ARGUMENTS]:
- **`text`** (str) : Plain text in Belarusian.

#### [RETURNS]:
- **`output`** (tuple) : The tuple of tokens extracted from the text.

#### [USAGE]:
This operation is intended to be used after paragraph segmentation and before sentence segmentation.

#### Examples 
```
tokenize(r'Начальнік галоўнага ўпраўлення Міністэрства адукацыі')

[Output]:

('Начальнік', ' ', 'галоўнага', ' ', 'ўпраўлення', ' ', 'Міністэрства', ' ', 'адукацыі')
```

### `annotateToken`
Annotate a token regardless of whether it is present in the database. `(U)POS` values and features are specified at search result level since there can be multiple matches for a token.

#### [ARGUMENTS]:
- **`token`** (str) : A word-level token.
- **`toConllu`** (bool) OPTIONAL: The structure of token annotation.
    
    [VALUE OPTIONS]:
    - `False` DEFAULT : The output is similar to the return of database search functions. If there are no matches, 'Results' dictionary is omitted.
    - `True` : The output is mapped to the columns of a tabulated CoNLL-U file. The empty values belonging to mandatory CoNLL-U columns are populated with placeholders. There is always at least one item in 'Results' dictionary, so a placeholder result is generated if there are no matches.
- **`extended`** (bool) OPTIONAL: This attribute indicates whether additional token types are included in the search.
    
    [VALUE OPTIONS]:
    - `False` : Only database results are returned.
    - `True` DEFAULT : Tokens are checked against extended token types as defined in `tokenCategories`, e.g. numbers, punctuation marks, symbols etc. See "Token categories" for the definitions.

#### [RETURNS]:
- **`output`** (dict) : Annotated tokens, structured according to `toConllu` value. 'Results' dictionary is optional if `toConllu == False`.
    
    [If `toConllu == False`]: 
    ``` 
    {'Form': [token], 'Results': {1: { [formByID() output structure] }, ... }}
    ```

    [If `toConllu == True`]:
    ```
    {'FORM': [token], 'MISC': [...], 'Results': {1: {'LEMMA': [...], 'UPOS': [...], 'FEATS': [...]}, ...}}
    ```

#### [USAGE]:
This operation is intended to be used after tokenization.

#### Examples
```
annotateToken('.')

[Output]:

{'Form': '.', 'Results': {1: {'POS': 'PUNCT'}}}
```

```
annotateToken('яго', toConllu = True)

[Output]:

{'FORM': 'яго',
 'MISC': '_',
 'Results': {1: {'LEMMA': 'ён',
   'UPOS': 'PRON',
   'FEATS': 'Case=Gen|Gender=Masc|InflClass=Ntype|Number=Sing|Person=3|PronType=Prs'},
  2: {'LEMMA': 'ён',
   'UPOS': 'PRON',
   'FEATS': 'Case=Acc|Gender=Masc|InflClass=Ntype|Number=Sing|Person=3|PronType=Prs'},
  3: {'LEMMA': 'ён',
   'UPOS': 'PRON',
   'FEATS': 'Case=Gen|Gender=Neut|InflClass=Ntype|Number=Sing|Person=3|PronType=Prs'},
  4: {'LEMMA': 'ён',
   'UPOS': 'PRON',
   'FEATS': 'Case=Acc|Gender=Neut|InflClass=Ntype|Number=Sing|Person=3|PronType=Prs'},
  5: {'LEMMA': 'яго',
   'UPOS': 'PRON',
   'FEATS': 'InflClass=Ind|Poss=None|PronType=Prs'}}}
```

### `annotateSentence`

Convert a list of tokens into a numbered list with JSON-like or CoNLL-U annotation.

##### [ARGUMENTS]:
- **`tokens`** (tuple) : A tuple of tokens.
- **`toConllu`** (bool) OPTIONAL: The structure of token annotation.

    [VALUE OPTIONS]:
    - `False` DEFAULT : The output is similar to the return of database search functions. If there are no matches, 'Results' dictionary is omitted.
    - `True` : The output is mapped to the columns of a tabulated CoNLL-U file. The empty values belonging to mandatory CoNLL-U columns are populated with placeholders. There is always at least one item in 'Results' dictionary, so a placeholder result is generated if there are no matches.
- **`extended`** (bool) OPTIONAL: This attribute indicates whether additional token types are included in the search.

    [VALUE OPTIONS]:
    - `False` : Only database results are returned.
    - `True` DEFAULT : Tokens are checked against extended token types as defined in `tokenCategories`, e.g. numbers, punctuation marks, symbols etc. See "Token categories" for the definitions.

#### [RETURNS]:
- `output` (dict) : Nummered and annotated tokens, structured according to `toConllu` value.

#### [USAGE]:
This operation is intended to be used after sentence segmentation, as the token's number denotes its position within the sentence.

#### Examples
```
annotateSentence(tokenize('А ты?😎'), toConllu = False, extended = False)

[Output]:

{1: {'Form': 'А',
  'Results': {1: {'FormData': {'ID': 1, 'Form': 'а', 'Accent': '1'},
    'LemmaData': {'ID': 1, 'Lemma': 'а', 'POS': 'PART'},
    'Variant': 1},
   2: {'FormData': {'ID': 146, 'Form': 'а', 'Accent': '1'},
    'LemmaData': {'ID': 137, 'Lemma': 'а', 'POS': 'ADP'},
    'Variant': 1},
   3: {'FormData': {'ID': 406, 'Form': 'а', 'Accent': '1'},
    'LemmaData': {'ID': 376, 'Lemma': 'а', 'POS': 'INTJ'},
    'Variant': 1},
   4: {'FormData': {'ID': 1043, 'Form': 'а', 'Accent': '1'},
    'LemmaData': {'ID': 998, 'Lemma': 'а', 'POS': 'CCONJ', 'CconjType': 'Crd'},
    'Variant': 1}}},
 2: {'Form': 'ты',
  'Results': {1: {'FormData': {'ID': 2857240,
     'Form': 'ты',
     'Accent': '2',
     'Case': 'Nom',
     'Number': 'Sing'},
    'LemmaData': {'ID': 170601,
     'Lemma': 'ты',
     'POS': 'PRON',
     'PronType': 'Prs',
     'InflClass': 'Ntype',
     'Person': 2},
    'Variant': 1}},
  'SpaceAfter': False},
 3: {'Form': '?', 'SpaceAfter': False},
 4: {'Form': '😎'}}
```

```
annotateSentence(tokenize('А ты?😎'), toConllu = True, extended = True)

[Output]:

{1: {'FORM': 'А',
  'MISC': '_',
  'Results': {1: {'LEMMA': 'а', 'UPOS': 'PART', 'FEATS': '_'},
   2: {'LEMMA': 'а', 'UPOS': 'ADP', 'FEATS': '_'},
   3: {'LEMMA': 'а', 'UPOS': 'INTJ', 'FEATS': '_'},
   4: {'LEMMA': 'а', 'UPOS': 'CCONJ', 'FEATS': 'CconjType=Crd'}}},
 2: {'FORM': 'ты',
  'MISC': 'SpaceAfter=No',
  'Results': {1: {'LEMMA': 'ты',
    'UPOS': 'PRON',
    'FEATS': 'Case=Nom|InflClass=Ntype|Number=Sing|Person=2|PronType=Prs'}}},
 3: {'FORM': '?',
  'MISC': 'SpaceAfter=No',
  'Results': {1: {'LEMMA': '?', 'UPOS': 'PUNCT', 'FEATS': '_'}}},
 4: {'FORM': '😎',
  'MISC': '_',
  'Results': {1: {'LEMMA': '_', 'UPOS': 'X', 'FEATS': '_'}}}}
```

### `splitSentences`
Segmentation of a token list into groups corresponding to sentences, see Sentence segmentation.
    
#### [ARGUMENTS]:
- **`tokens`** (tuple) : A tuple of tokens belonging to a paragraph.

#### [RETURNS]:
- **`sentences`** (tuple) : A tuple of nested tuples corresponding to sentences.

#### [USAGE]:
This operation is intended for use after tokenization and paragraph segmentation.

#### Examples
```
sample = 'У 47 установах вышэйшай адукацыі рэспублікі на пачатак 2024/2025 навучальнага года навучалася: 224,2 тыс. студэнтаў, 10,4 тыс. магістрантаў. Сярод іх: больш за 7,5 тыс. (23,6%) - будучыя інжынеры, 3,9 тыс. (12,3%) - педагогі, 3,4 тыс. (10,8%) - медыкі, аграрыі - 2,8 тыс.'

splitSentences(tokenize(sample))

[Output]:

(
    ('У', ' ', '47', ' ', 'установах', ' ',  'вышэйшай', ' ', 'адукацыі', ' ', 'рэспублікі', ' ', 'на', ' ', 'пачатак', ' ', '2024', '/', '2025', ' ', 'навучальнага', ' ', 'года', ' ', 'навучалася', ':', ' ', '224,2', ' ', 'тыс.', ' ', 'студэнтаў', ',', ' ', '10,4', ' ', 'тыс.', ' ', 'магістрантаў', '.'),

    ('Сярод', ' ', 'іх', ':', ' ', 'больш', ' ', 'за', ' ', '7,5', ' ', 'тыс.', ' ', '(', '23,6', '%', ')', ' ', '-', ' ', 'будучыя', ' ', 'інжынеры', ',', ' ', '3,9', ' ', 'тыс.', ' ', '(', '12,3', '%', ')', ' ', '-', ' ', 'педагогі', ',', ' ', '3,4', ' ', 'тыс.', ' ', '(', '10,8', '%', ')', ' ', '-', ' ', 'медыкі', ',', ' ', 'аграрыі', ' ', '-', ' ', '2,8', ' ', 'тыс', '.')
)
```

### `annotateText`
Segment plain text into nested numbered paragraphs, sentences and word-level tokens, and provide token annotation. Paragraphs are segmented at `\n` new line character.

#### [ARGUMENTS]:
- **`text`** (str) : Plain text with paragraphs and sentences.
- **`toConllu`** (bool) OPTIONAL: The structure of token annotation.

    [VALUE OPTIONS]:
    - `False` DEFAULT : The output is similar to the return of database search functions. If there are no matches, 'Results' dictionary is omitted.
    - `True` : The output is mapped to the columns of a tabulated CoNNL-U file. The empty values belonging to mandatory CoNLL-U columns are populated with placeholders. There is always at least one item in 'Results' dictionary, so a placeholder result is generated if there are no matches.
- **`extended`** (bool) OPTIONAL: This attribute indicates whether additional token types are included in the search.
    [VALUE OPTIONS]:
    - `False` : Only database results are returned.
    - `True` DEFAULT : Tokens are checked against extended token types as defined in `tokenCategories`, e.g. numbers, punctuation marks, symbols etc. See documentations for the definitions.

#### [RETURNS]:
- **`output`** (dict) : Segmented, tokenized and annotated text. 

#### Examples
```
annotateText('Аня была там у 2023 г.', toConllu = False, extended = False)

[Output]:

{'Paragraphs': {1: {'Text': 'Аня была там у 2023 г.',
   'Sentences': {1: {'Text': 'Аня была там у 2023 г.',
     'Tokens': {1: {'Form': 'Аня'},
      2: {'Form': 'была',
       'Results': {1: {'FormData': {'ID': 32, 'Form': 'была', 'Accent': '4'},
         'LemmaData': {'ID': 28, 'Lemma': 'было', 'POS': 'PART'},
         'Variant': 3},
        2: {'FormData': {'ID': 2947411,
          'Form': 'была',
          'Gender': 'Fem',
          'Number': 'Sing',
          'Tense': 'Past'},
         'LemmaData': {'ID': 177679,
          'Lemma': 'быць',
          'POS': 'VERB',
          'Aspect': 'Imp',
          'SubCat': 'Intr'},
         'Variant': 1}}},
      3: {'Form': 'там',
       'Results': {1: {'FormData': {'ID': 121, 'Form': 'там', 'Accent': '2'},
         'LemmaData': {'ID': 112, 'Lemma': 'там', 'POS': 'PART'},
         'Variant': 1},
        2: {'FormData': {'ID': 3978013,
          'Form': 'там',
          'Accent': '2',
          'Degree': 'Pos'},
         'LemmaData': {'ID': 246746, 'Lemma': 'там', 'POS': 'ADV'},
         'Variant': 1}}},
      4: {'Form': 'у',
       'Results': {1: {'FormData': {'ID': 379, 'Form': 'у', 'Accent': '1'},
         'LemmaData': {'ID': 351, 'Lemma': 'у', 'POS': 'ADP'},
         'Variant': 1}}},
      5: {'Form': '2023'},
      6: {'Form': 'г', 'SpaceAfter': False},
      7: {'Form': '.'}}}}}}}
```

```
annotateText('Аня была там у 2023 г.', toConllu = True, extended = True)

[Output]:

{'Paragraphs': {1: {'Text': 'Аня была там у 2023 г.',
   'Sentences': {1: {'Text': 'Аня была там у 2023 г.',
     'Tokens': {1: {'FORM': 'Аня',
       'MISC': '_',
       'Results': {1: {'LEMMA': '_', 'UPOS': 'X', 'FEATS': '_'}}},
      2: {'FORM': 'была',
       'MISC': '_',
       'Results': {1: {'LEMMA': 'было', 'UPOS': 'PART', 'FEATS': '_'},
        2: {'LEMMA': 'быць',
         'UPOS': 'VERB',
         'FEATS': 'Aspect=Imp|Gender=Fem|Number=Sing|SubCat=Intr|Tense=Past'}}},
      3: {'FORM': 'там',
       'MISC': '_',
       'Results': {1: {'LEMMA': 'там', 'UPOS': 'PART', 'FEATS': '_'},
        2: {'LEMMA': 'там', 'UPOS': 'ADV', 'FEATS': 'Degree=Pos'}}},
      4: {'FORM': 'у',
       'MISC': '_',
       'Results': {1: {'LEMMA': 'у', 'UPOS': 'ADP', 'FEATS': '_'}}},
      5: {'FORM': '2023',
       'MISC': '_',
       'Results': {1: {'LEMMA': '2023', 'UPOS': 'NUM', 'FEATS': '_'}}},
      6: {'FORM': 'г',
       'MISC': 'SpaceAfter=No',
       'Results': {1: {'LEMMA': '_', 'UPOS': 'X', 'FEATS': '_'}}},
      7: {'FORM': '.',
       'MISC': '_',
       'Results': {1: {'LEMMA': '.', 'UPOS': 'PUNCT', 'FEATS': '_'}}}}}}}}}
```

### `generateConllu`
Generate a tab-separated CoNLL-U table from annotated text in dictionary format, mapping the latter to the columns `ID`, `FORM`, `LEMMA`, `UPOS`, `XPOS`, `FEATS`, `HEAD`, `DEPREL`, `DEPS` & `MISC`. Only `ID`, `FORM`, `LEMMA`, `UPOS`, `MISC` columns are populated, the rest use the standard '_' placeholer.

#### [ARGUMENTS]:
- **`annotatedText`** (dict) : Annotated text as outputted by `annotateText()` function with `toConllu == True`.

#### [RETURNS]:
- **`output`** (str) : Tab-separated CoNLL-U table.

#### Examples
```
sample = annotateText('Аня была там у 2023 г.', toConllu = True, extended = True)

print(generateConllu(sample))

[Output]:

newpar id = p1
# sent_id = p1s1
# text = Аня была там у 2023 г.
1	Аня	_	X	_	_	_	_	_	_
2	была	_	_	_	_	_	_	_	_
2.1	_	было	PART	_	_	_	_	_	_
2.2	_	быць	VERB	_	Aspect=Imp|Gender=Fem|Number=Sing|SubCat=Intr|Tense=Past	_	_	_	_
3	там	_	_	_	_	_	_	_	_
3.1	_	там	PART	_	_	_	_	_	_
3.2	_	там	ADV	_	Degree=Pos	_	_	_	_
4	у	у	ADP	_	_	_	_	_	_
5	2023	2023	NUM	_	_	_	_	_	_
6	г	_	X	_	_	_	_	_	SpaceAfter=No
7	.	.	PUNCT	_	_	_	_	_	_
```

### `completeConllu`
Parse a CoNLL-U tble and fill `LEMMA`, `UPOS` & `FEATS` values for tokens that have placeholders in these columns.

#### [ARGUMENTS]:
- **`incompleteConllu`** (str) : CoNLL-U table as a string. To be completed a token must have the placeholder values corresponding to `{'LEMMA': '_', 'UPOS': 'X', 'FEATS': '_'}` and no children nodes denoted by IDs in `1.1` format.
- **`extended`** (bool) OPTIONAL: This attribute indicates whether additional token types are included in the search.

    [VALUE OPTIONS]:
    - `False` : Only database results are returned.
    - `True` DEFAULT : Tokens are checked against extended token types as defined in `tokenCategories`, e.g. numbers, punctuation marks, symbols etc. See Token categories for the definitions.

#### [RETURNS]:
- **`output`** (str) : Tab-separated CoNLL-U table with token annotation added where possible.

#### Examples
```
input = '''
        newpar id = p1
        # sent_id = p1s1
        # text = Аня была там у 2023 г.
        1	Аня	_	X	_	_	_	_	_	_
        2	была	_	X	_	_	_	_	_	_
        3	там	_	X	_	_	_	_	_	_
        4	у	_	X	_	_	_	_	_	_
        5	2023	2023	NUM	_	_	_	_	_	_
        6	г	_	X	_	_	_	_	_	SpaceAfter=No
        7	.	.	PUNCT	_	_	_	_	_	_
        '''

print(completeConllu(input))

[Output]:

newpar id = p1
# sent_id = p1s1
# text = Аня была там у 2023 г.
1	Аня	_	X	_	_	_	_	_	_
2	была	_	_	_	_	_	_	_	_
2.1	_	было	PART	_	_	_	_	_	_
2.2	_	быць	VERB	_	Aspect=Imp|Gender=Fem|Number=Sing|SubCat=Intr|Tense=Past	_	_	_	_
3	там	_	_	_	_	_	_	_	_
3.1	_	там	PART	_	_	_	_	_	_
3.2	_	там	ADV	_	Degree=Pos	_	_	_	_
4	у	у	ADP	_	_	_	_	_	_
5	2023	2023	NUM	_	_	_	_	_	_
6	г	_	X	_	_	_	_	_	SpaceAfter=No
7	.	.	PUNCT	_	_	_	_	_	_
```

### `setStopWords`
Set stop-words, i.e. the list of comma-separated lemma IDs in string format, to be excluded from database search results. 
    
#### [ARGUMENTS]:
- **`lemIDlist`** (NoneType, tuple, str) : Stop-word list source. If not specified, the default `stopWordsPath` value is used as the file path. 

    [VALUE OPTIONS]:
    - File path (str) : OS path to a TXT file with comma-separated lemma IDs.
    - IDs (tuple) - Lemma IDs in integer format.
    - `None` (NoneType) - Removes all stop words.

[RETURNS]:
- **`stopWords`** VAR VALUE (dict) : Populates `stopWords` value with a dictionary with the following keys:
    - `List` (list) : The list of integers.
    - `String` (str) : The list in string format to be appended to SQL search statements. 

#### Examples
```
setStopWords()

[Output]:

'The stop-word list was updated with values from {your path}/slounik/assets/stop_words.txt.'
```

```
setStopWords('{your path}/{your file}.txt')

[Output]:

'The stop-word list was updated with values from {your path}/{your file}.txt.'
```

```
setStopWords(None)

[Output]:

'The stop-word list was emptied.'
```

```
setStopWords((81473, 69839, 77432, 81473))

[Output]:

'The stop-word list was updated. Some of the submitted values were removed due to duplication or invalid format.'
```

### `exportCSV`
Export `formSearch()` or `lemmaSearch()` search results into a CSV file in the specified directory of local file system.
    
#### [ARGUMENTS]:
- **`data`** (dict) : `formSearch()` or `lemmaSearch()` functions' output.
- **`level`** (str) : Input data structure.

    [VALUE OPTIONS]:
    - 'f' : Form, for `formSearch()` results.
    - 'l' : Lemma, for `lemmaSearch()` results.
- **`path`** (str) OPTIONAL : OS path to the target directory. If not specified, the default `exportPath` value is used. 

#### [RETURNS]:
`Slounik_Export_{YYYY-MM-DD_HH-MM-SS}.csv` (File) OS : CSV file with the inputted data generated in the specified directory of local file system.

#### Examples
```
sample = formSearch(query = 'ева')
exportCSV(sample, 'f')

[Output]:

'{your path}/slounik/exports/Slounik_Export_2025-09-04_11-17-19.csv was created.'
```

### `accentuate`
Add word stress diacritic marks to a word form. The mark used is Unicode `\u0301`.

#### [ARGUMENTS]:
- **`form`** (str) : Word form as it is stored in `Form` column of `Form` database table and outputted under ['FormData']['Form'] key of a form dictionary.
- **`accentData`** (str) : Accent position data as it is stored in `Accent` column of Form table and outputted under ['FormData']['Accent'] key of a form dictionary. Numbering starts with 1.

#### [RETURNS]:
- **`accentedForm`** (str) : The inputted word form with diacritic marks.

OR
- **`None`** (NoneType) : Returned if the submittef data is invalid.

#### Examples
```
accentuate('цік-цік-цік', '0-0-2')

[Output]:
'цік-цік-ці́к'
```