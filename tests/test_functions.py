import unittest
from pathlib import Path
import sys
import os 

pkgPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if pkgPath not in sys.path: sys.path.append(pkgPath)

import slounik

class testClass(unittest.TestCase):

    def testFormSearchSimple(self):
        """
        Form search without arguments
        """
        requested = slounik.formSearch('афалін')
        correct = ({'FormData': {'ID': 1998472, 'Form': 'афалін', 'Accent': '5', 'Case': 'Gen', 'Number': 'Plur'}, 'LemmaData': {'ID': 77115, 'Lemma': 'афаліна', 'POS': 'NOUN', 'InflClass': '2d', 'Gender': 'Fem', 'Animacy': True}, 'Variant': 1}, {'FormData': {'ID': 1998474, 'Form': 'афалін', 'Accent': '5', 'Case': 'Acc', 'Number': 'Plur'}, 'LemmaData': {'ID': 77115, 'Lemma': 'афаліна', 'POS': 'NOUN', 'InflClass': '2d', 'Gender': 'Fem', 'Animacy': True}, 'Variant': 1})
        self.assertEqual(requested, correct, 'Simple form search result mismatch')


    def testFormSearchComplex(self):
        """
        Form search with arguments
        """
        requested = slounik.formSearch(query = 'Е??а', keepLetterCase = True, l_gender = 'Fem')
        correct = ({'FormData': {'ID': 2776613, 'Form': 'Езва', 'Accent': '1', 'Case': 'Nom', 'Number': 'Sing'}, 'LemmaData': {'ID': 158694, 'Lemma': 'Езва', 'POS': 'PROPN', 'InflClass': '2d', 'Gender': 'Fem'}, 'Variant': 1}, {'FormData': {'ID': 2776736, 'Form': 'Елка', 'Accent': '1', 'Case': 'Nom', 'Number': 'Sing'}, 'LemmaData': {'ID': 158710, 'Lemma': 'Елка', 'POS': 'PROPN', 'InflClass': '2d', 'Gender': 'Fem'}, 'Variant': 1})
        self.assertEqual(requested, correct, 'Complex form search result mismatch')


    def testFormByIDSimple(self):
        """
        Form by ID without arguments
        """
        requested = slounik.formByID(14233)
        correct = {'FormData': {'ID': 14233, 'Form': 'аблыжнаю', 'Accent': '4', 'Gender': 'Fem', 'Case': 'Ins', 'Number': 'Sing'}, 'LemmaData': {'ID': 509, 'Lemma': 'аблыжны', 'POS': 'ADJ', 'AdjType': 'Rel', 'Degree': 'Pos'}, 'Variant': 1}
        self.assertEqual(requested, correct, 'Simple form by ID result mismatch')
    

    def testFormByIDComplex(self):
        """
        Form by ID with arguments
        """
        requested = slounik.formByID(14233, toConllu = True, includeForm = False)
        correct = {'LEMMA': 'аблыжны', 'UPOS': 'ADJ', 'FEATS': 'AdjType=Rel|Case=Ins|Degree=Pos|Gender=Fem|Number=Sing'}
        self.assertEqual(requested, correct, 'Complex form by ID result mismatch')


    def testLemmaSearchSimple(self):
        """
        Lemma search without arguments
        """
        requested = slounik.lemmaSearch('Ева')
        correct = ({'ID': 158670, 'Lemma': 'Ева', 'POS': 'PROPN', 'InflClass': '2d', 'Gender': 'Fem', 'Animacy': True, 'Personal': True},)
        self.assertEqual(requested, correct, 'Simple lemma search result mismatch')


    def testFormSearchComplex(self):
        """
        Lemma search with arguments
        """
        requested = slounik.lemmaSearch(query = 'аа*й', Animaсy = True, POS = 'NOUN')
        correct = ({'ID': 69987, 'Lemma': 'аагоній', 'POS': 'NOUN', 'InflClass': '1d', 'Gender': 'Masc'},)
        self.assertEqual(requested, correct, 'Complex lemma search result mismatch')


    def testLemmaByID(self):
        """
        Lemma by ID 
        """
        requested = slounik.lemmaByID(210293)
        correct = {'ID': 210293, 'Lemma': 'задрыжэць', 'POS': 'VERB', 'InflClass': '2c', 'Aspect': 'Perf', 'SubCat': 'Intr'}
        self.assertEqual(requested, correct, 'Lemma by ID result mismatch')
    

    def testAllForms(self):
        """
        Paradigm by lemma ID 
        """
        requested = slounik.allForms(120900)
        correct = {'LemmaData': {'ID': 120900, 'Lemma': 'паўакружына', 'POS': 'NOUN', 'InflClass': '2d', 'Gender': 'Fem', 'Abbr': True}, 'Variants': ({'Variant': 1, 'Paradigm': ({'ID': 2425598, 'Form': 'паўакружына', 'Accent': '7', 'Case': 'Nom', 'Number': 'Sing'}, {'ID': 2425599, 'Form': 'паўакружыны', 'Accent': '7', 'Case': 'Gen', 'Number': 'Sing'}, {'ID': 2425600, 'Form': 'паўакружыне', 'Accent': '7', 'Case': 'Dat', 'Number': 'Sing'}, {'ID': 2425601, 'Form': 'паўакружыну', 'Accent': '7', 'Case': 'Acc', 'Number': 'Sing'}, {'ID': 2425602, 'Form': 'паўакружынай', 'Accent': '7', 'Case': 'Ins', 'Number': 'Sing'}, {'ID': 2425603, 'Form': 'паўакружынаю', 'Accent': '7', 'Case': 'Ins', 'Number': 'Sing'}, {'ID': 2425604, 'Form': 'паўакружыне', 'Accent': '7', 'Case': 'Loc', 'Number': 'Sing'}, {'ID': 2425605, 'Form': 'паўакружыны', 'Accent': '7', 'Case': 'Nom', 'Number': 'Plur'}, {'ID': 2425606, 'Form': 'паўакружын', 'Accent': '7', 'Case': 'Gen', 'Number': 'Plur'}, {'ID': 2425607, 'Form': 'паўакружынам', 'Accent': '7', 'Case': 'Dat', 'Number': 'Plur'}, {'ID': 2425608, 'Form': 'паўакружыны', 'Accent': '7', 'Case': 'Acc', 'Number': 'Plur'}, {'ID': 2425609, 'Form': 'паўакружынамі', 'Accent': '7', 'Case': 'Ins', 'Number': 'Plur'}, {'ID': 2425610, 'Form': 'паўакружынах', 'Accent': '7', 'Case': 'Loc', 'Number': 'Plur'})},)}
        self.assertEqual(requested, correct, 'Paradigm result mismatch')

    
    def testTokenizer(self):
        """
        Word-level tokenization
        """
        sample = 'Маргарыта Старасценка таксама расказала адну з гісторый з жыцця тэатра: "З дакументаў, якія датычацца ваеннага жыцця, мы даведаемся аб тым, што тэатр не проста рэпеціраваў п\'есы, а сапраўды ездзіў у ваенныя часці. Як пішацца ў справаздачах, яны выступалі перад салдатамі. Напрыклад, за перыяд з 9 па 24 чэрвеня далі 65 спектакляў, паказы праходзілі амаль кожны дзень па некалькі разоў. Гэтыя спектаклі настолькі натхнялі байцоў, што кожны раз яны ператваралі паказ у "мітынг" - плакалі над спектаклямі, успаміналі родны дом і сваіх блізкіх. Гэтыя спектаклі сталі сувязным звяном паміж вайной і мірным жыццём, салдатамі і тымі, хто застаўся далёка". '
        requested = slounik.tokenize(sample)
        correct = ('Маргарыта', ' ', 'Старасценка', ' ', 'таксама', ' ', 'расказала', ' ', 'адну', ' ', 'з', ' ', 'гісторый', ' ', 'з', ' ', 'жыцця', ' ', 'тэатра', ':', ' ', '"', 'З', ' ', 'дакументаў', ',', ' ', 'якія', ' ', 'датычацца', ' ', 'ваеннага', ' ', 'жыцця', ',', ' ', 'мы', ' ', 'даведаемся', ' ', 'аб', ' ', 'тым', ',', ' ', 'што', ' ', 'тэатр', ' ', 'не', ' ', 'проста', ' ', 'рэпеціраваў', ' ', "п'есы", ',', ' ', 'а', ' ', 'сапраўды', ' ', 'ездзіў', ' ', 'у', ' ', 'ваенныя', ' ', 'часці', '.', ' ', 'Як', ' ', 'пішацца', ' ', 'ў', ' ', 'справаздачах', ',', ' ', 'яны', ' ', 'выступалі', ' ', 'перад', ' ', 'салдатамі', '.', ' ', 'Напрыклад', ',', ' ', 'за', ' ', 'перыяд', ' ', 'з', ' ', '9', ' ', 'па', ' ', '24', ' ', 'чэрвеня', ' ', 'далі', ' ', '65', ' ', 'спектакляў', ',', ' ', 'паказы', ' ', 'праходзілі', ' ', 'амаль', ' ', 'кожны', ' ', 'дзень', ' ', 'па', ' ', 'некалькі', ' ', 'разоў', '.', ' ', 'Гэтыя', ' ', 'спектаклі', ' ', 'настолькі', ' ', 'натхнялі', ' ', 'байцоў', ',', ' ', 'што', ' ', 'кожны', ' ', 'раз', ' ', 'яны', ' ', 'ператваралі', ' ', 'паказ', ' ', 'у', ' ', '"', 'мітынг', '"', ' ', '-', ' ', 'плакалі', ' ', 'над', ' ', 'спектаклямі', ',', ' ', 'успаміналі', ' ', 'родны', ' ', 'дом', ' ', 'і', ' ', 'сваіх', ' ', 'блізкіх', '.', ' ', 'Гэтыя', ' ', 'спектаклі', ' ', 'сталі', ' ', 'сувязным', ' ', 'звяном', ' ', 'паміж', ' ', 'вайной', ' ', 'і', ' ', 'мірным', ' ', 'жыццём', ',', ' ', 'салдатамі', ' ', 'і', ' ', 'тымі', ',', ' ', 'хто', ' ', 'застаўся', ' ', 'далёка', '"', '.')
        self.assertEqual(requested, correct, 'Word-level tokenization result mismatch') 

    def testAnnotateToken(self):
        """
        Annotation of tokens
        """
        requested = slounik.annotateToken('прытрудна')
        correct = {'Form': 'прытрудна', 'Results': {1: {'FormData': {'ID': 3310524, 'Form': 'прытрудна', 'Accent': '6', 'Degree': 'Pos'}, 'LemmaData': {'ID': 192964, 'Lemma': 'прытрудна', 'POS': 'ADV'}, 'Variant': 1}}}
        self.assertEqual(requested, correct, 'Token annotation result mismatch')


    def testAnnotateTokenConllu(self):
        """
        Annotation of tokens in ConLL-U compatible output
        """
        requested = slounik.annotateToken('прытрудна', toConllu = True)
        correct = {'FORM': 'прытрудна', 'MISC': '_', 'Results': {1: {'LEMMA': 'прытрудна', 'UPOS': 'ADV', 'FEATS': 'Degree=Pos'}}}
        self.assertEqual(requested, correct, 'Token ConLL-U annotation result mismatch')


    def testAnnotateSentence(self):
        """
        Annotation of a sentence with default settings
        """
        requested = slounik.annotateSentence(slounik.tokenize('А ты?😎'))
        correct = {1: {'Form': 'А', 'Results': {1: {'FormData': {'ID': 1927626, 'Form': 'а', 'Accent': '1'}, 'LemmaData': {'ID': 68780, 'Lemma': 'а', 'POS': 'CCONJ'}, 'Variant': 1}, 2: {'FormData': {'ID': 1927693, 'Form': 'а', 'Accent': '1'}, 'LemmaData': {'ID': 68846, 'Lemma': 'а', 'POS': 'PART'}, 'Variant': 1}, 3: {'FormData': {'ID': 1927838, 'Form': 'а', 'Accent': '1'}, 'LemmaData': {'ID': 68982, 'Lemma': 'а', 'POS': 'ADP'}, 'Variant': 1}, 4: {'FormData': {'ID': 1928098, 'Form': 'а', 'Accent': '1'}, 'LemmaData': {'ID': 69221, 'Lemma': 'а', 'POS': 'INTJ'}, 'Variant': 1}, 5: {'FormData': {'ID': 1930997, 'Form': 'а', 'Accent': '1', 'Case': 'Nom', 'Number': 'Sing'}, 'LemmaData': {'ID': 69984, 'Lemma': 'а', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 6: {'FormData': {'ID': 1930998, 'Form': 'а', 'Accent': '1', 'Case': 'Gen', 'Number': 'Sing'}, 'LemmaData': {'ID': 69984, 'Lemma': 'а', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 7: {'FormData': {'ID': 1930999, 'Form': 'а', 'Accent': '1', 'Case': 'Dat', 'Number': 'Sing'}, 'LemmaData': {'ID': 69984, 'Lemma': 'а', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 8: {'FormData': {'ID': 1931000, 'Form': 'а', 'Accent': '1', 'Case': 'Acc', 'Number': 'Sing'}, 'LemmaData': {'ID': 69984, 'Lemma': 'а', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 9: {'FormData': {'ID': 1931001, 'Form': 'а', 'Accent': '1', 'Case': 'Ins', 'Number': 'Sing'}, 'LemmaData': {'ID': 69984, 'Lemma': 'а', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 10: {'FormData': {'ID': 1931002, 'Form': 'а', 'Accent': '1', 'Case': 'Loc', 'Number': 'Sing'}, 'LemmaData': {'ID': 69984, 'Lemma': 'а', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 11: {'FormData': {'ID': 1931003, 'Form': 'а', 'Accent': '1', 'Case': 'Nom', 'Number': 'Plur'}, 'LemmaData': {'ID': 69984, 'Lemma': 'а', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 12: {'FormData': {'ID': 1931004, 'Form': 'а', 'Accent': '1', 'Case': 'Gen', 'Number': 'Plur'}, 'LemmaData': {'ID': 69984, 'Lemma': 'а', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 13: {'FormData': {'ID': 1931005, 'Form': 'а', 'Accent': '1', 'Case': 'Dat', 'Number': 'Plur'}, 'LemmaData': {'ID': 69984, 'Lemma': 'а', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 14: {'FormData': {'ID': 1931006, 'Form': 'а', 'Accent': '1', 'Case': 'Acc', 'Number': 'Plur'}, 'LemmaData': {'ID': 69984, 'Lemma': 'а', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 15: {'FormData': {'ID': 1931007, 'Form': 'а', 'Accent': '1', 'Case': 'Ins', 'Number': 'Plur'}, 'LemmaData': {'ID': 69984, 'Lemma': 'а', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 16: {'FormData': {'ID': 1931008, 'Form': 'а', 'Accent': '1', 'Case': 'Loc', 'Number': 'Plur'}, 'LemmaData': {'ID': 69984, 'Lemma': 'а', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}}}, 2: {'Form': 'ты', 'Results': {1: {'FormData': {'ID': 3315827, 'Form': 'ты', 'Accent': '2', 'Case': 'Nom', 'Number': 'Sing'}, 'LemmaData': {'ID': 195995, 'Lemma': 'ты', 'POS': 'PRON', 'PronType': 'Prs', 'InflClass': 'Ntype', 'Person': 2}, 'Variant': 1}}, 'SpaceAfter': False}, 3: {'Form': '?', 'Results': {1: {'POS': 'PUNCT'}}, 'SpaceAfter': False}, 4: {'Form': '😎'}}
        self.assertEqual(requested, correct, 'Sentence annotation result mismatch')


    def testAnnotateSentenceConllu(self):
        """
        Annotation of a sentence in ConLL-U with token features limited to the DB only
        """
        requested = slounik.annotateSentence(slounik.tokenize('А ты?😎'), toConllu = True, extended = False)
        correct = {1: {'FORM': 'А', 'MISC': '_', 'Results': {1: {'LEMMA': 'а', 'UPOS': 'CCONJ', 'FEATS': '_'}, 2: {'LEMMA': 'а', 'UPOS': 'PART', 'FEATS': '_'}, 3: {'LEMMA': 'а', 'UPOS': 'ADP', 'FEATS': '_'}, 4: {'LEMMA': 'а', 'UPOS': 'INTJ', 'FEATS': '_'}, 5: {'LEMMA': 'а', 'UPOS': 'NOUN', 'FEATS': 'Case=Nom|Gender=Neut|InflClass=Ind|Number=Sing'}, 6: {'LEMMA': 'а', 'UPOS': 'NOUN', 'FEATS': 'Case=Gen|Gender=Neut|InflClass=Ind|Number=Sing'}, 7: {'LEMMA': 'а', 'UPOS': 'NOUN', 'FEATS': 'Case=Dat|Gender=Neut|InflClass=Ind|Number=Sing'}, 8: {'LEMMA': 'а', 'UPOS': 'NOUN', 'FEATS': 'Case=Acc|Gender=Neut|InflClass=Ind|Number=Sing'}, 9: {'LEMMA': 'а', 'UPOS': 'NOUN', 'FEATS': 'Case=Ins|Gender=Neut|InflClass=Ind|Number=Sing'}, 10: {'LEMMA': 'а', 'UPOS': 'NOUN', 'FEATS': 'Case=Loc|Gender=Neut|InflClass=Ind|Number=Sing'}, 11: {'LEMMA': 'а', 'UPOS': 'NOUN', 'FEATS': 'Case=Nom|Gender=Neut|InflClass=Ind|Number=Plur'}, 12: {'LEMMA': 'а', 'UPOS': 'NOUN', 'FEATS': 'Case=Gen|Gender=Neut|InflClass=Ind|Number=Plur'}, 13: {'LEMMA': 'а', 'UPOS': 'NOUN', 'FEATS': 'Case=Dat|Gender=Neut|InflClass=Ind|Number=Plur'}, 14: {'LEMMA': 'а', 'UPOS': 'NOUN', 'FEATS': 'Case=Acc|Gender=Neut|InflClass=Ind|Number=Plur'}, 15: {'LEMMA': 'а', 'UPOS': 'NOUN', 'FEATS': 'Case=Ins|Gender=Neut|InflClass=Ind|Number=Plur'}, 16: {'LEMMA': 'а', 'UPOS': 'NOUN', 'FEATS': 'Case=Loc|Gender=Neut|InflClass=Ind|Number=Plur'}}}, 2: {'FORM': 'ты', 'MISC': 'SpaceAfter=No', 'Results': {1: {'LEMMA': 'ты', 'UPOS': 'PRON', 'FEATS': 'Case=Nom|InflClass=Ntype|Number=Sing|Person=2|PronType=Prs'}}}, 3: {'FORM': '?', 'MISC': 'SpaceAfter=No', 'Results': {1: {'LEMMA': '_', 'UPOS': 'X', 'FEATS': '_'}}}, 4: {'FORM': '😎', 'MISC': '_', 'Results': {1: {'LEMMA': '_', 'UPOS': 'X', 'FEATS': '_'}}}}
        self.assertEqual(requested, correct, 'Sentence ConLL-U annotation result (DB tokens only) mismatch')


    def testSplitSentences(self):
        """
        Sentence-level tokenization
        """
        sample = 'У 47 установах вышэйшай адукацыі рэспублікі на пачатак 2024/2025 навучальнага года навучалася: 224,2 тыс. студэнтаў, 10,4 тыс. магістрантаў. Сярод іх: больш за 7,5 тыс. (23,6%) - будучыя інжынеры, 3,9 тыс. (12,3%) - педагогі, 3,4 тыс. (10,8%) - медыкі, аграрыі - 2,8 тыс.'
        requested = slounik.splitSentences(slounik.tokenize(sample))
        correct = (('У', ' ', '47', ' ', 'установах', ' ', 'вышэйшай', ' ', 'адукацыі', ' ', 'рэспублікі', ' ', 'на', ' ', 'пачатак', ' ', '2024', '/', '2025', ' ', 'навучальнага', ' ', 'года', ' ', 'навучалася', ':', ' ', '224,2', ' ', 'тыс.', ' ', 'студэнтаў', ',', ' ', '10,4', ' ', 'тыс.', ' ', 'магістрантаў', '.'), ('Сярод', ' ', 'іх', ':', ' ', 'больш', ' ', 'за', ' ', '7,5', ' ', 'тыс.', ' ', '(', '23,6', '%', ')', ' ', '-', ' ', 'будучыя', ' ', 'інжынеры', ',', ' ', '3,9', ' ', 'тыс.', ' ', '(', '12,3', '%', ')', ' ', '-', ' ', 'педагогі', ',', ' ', '3,4', ' ', 'тыс.', ' ', '(', '10,8', '%', ')', ' ', '-', ' ', 'медыкі', ',', ' ', 'аграрыі', ' ', '-', ' ', '2,8', ' ', 'тыс', '.'))
        self.assertEqual(requested, correct, 'Sentence-level tokenization result mismatch')


    def testAnnotateText(self):
        """
        Annotation of a text with default settings
        """
        requested = slounik.annotateText('Аня была там у 2023 г.')
        correct = {'Paragraphs': {1: {'Text': 'Аня была там у 2023 г.', 'Sentences': {1: {'Text': 'Аня была там у 2023 г.', 'Tokens': {1: {'Form': 'Аня'}, 2: {'Form': 'была', 'Results': {1: {'FormData': {'ID': 1927724, 'Form': 'была', 'Accent': '4'}, 'LemmaData': {'ID': 68873, 'Lemma': 'было', 'POS': 'PART'}, 'Variant': 3}, 2: {'FormData': {'ID': 3406054, 'Form': 'была', 'Accent': '4', 'Gender': 'Fem', 'Number': 'Sing', 'Tense': 'Past'}, 'LemmaData': {'ID': 203078, 'Lemma': 'быць', 'POS': 'VERB', 'InflClass': 'Com', 'Aspect': 'Imp', 'SubCat': 'Intr'}, 'Variant': 1}}}, 3: {'Form': 'там', 'Results': {1: {'FormData': {'ID': 1927813, 'Form': 'там', 'Accent': '2'}, 'LemmaData': {'ID': 68957, 'Lemma': 'там', 'POS': 'PART'}, 'Variant': 1}, 2: {'FormData': {'ID': 3312240, 'Form': 'там', 'Accent': '2', 'Degree': 'Pos'}, 'LemmaData': {'ID': 194324, 'Lemma': 'там', 'POS': 'ADV'}, 'Variant': 1}}}, 4: {'Form': 'у', 'Results': {1: {'FormData': {'ID': 1928071, 'Form': 'у'}, 'LemmaData': {'ID': 69196, 'Lemma': 'у', 'POS': 'ADP'}, 'Variant': 1}, 2: {'FormData': {'ID': 2642919, 'Form': 'у', 'Accent': '1', 'Case': 'Nom', 'Number': 'Sing'}, 'LemmaData': {'ID': 143458, 'Lemma': 'у', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 3: {'FormData': {'ID': 2642920, 'Form': 'у', 'Accent': '1', 'Case': 'Gen', 'Number': 'Sing'}, 'LemmaData': {'ID': 143458, 'Lemma': 'у', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 4: {'FormData': {'ID': 2642921, 'Form': 'у', 'Accent': '1', 'Case': 'Dat', 'Number': 'Sing'}, 'LemmaData': {'ID': 143458, 'Lemma': 'у', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 5: {'FormData': {'ID': 2642922, 'Form': 'у', 'Accent': '1', 'Case': 'Acc', 'Number': 'Sing'}, 'LemmaData': {'ID': 143458, 'Lemma': 'у', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 6: {'FormData': {'ID': 2642923, 'Form': 'у', 'Accent': '1', 'Case': 'Ins', 'Number': 'Sing'}, 'LemmaData': {'ID': 143458, 'Lemma': 'у', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 7: {'FormData': {'ID': 2642924, 'Form': 'у', 'Accent': '1', 'Case': 'Loc', 'Number': 'Sing'}, 'LemmaData': {'ID': 143458, 'Lemma': 'у', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 8: {'FormData': {'ID': 2642925, 'Form': 'у', 'Accent': '1', 'Case': 'Nom', 'Number': 'Plur'}, 'LemmaData': {'ID': 143458, 'Lemma': 'у', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 9: {'FormData': {'ID': 2642926, 'Form': 'у', 'Accent': '1', 'Case': 'Gen', 'Number': 'Plur'}, 'LemmaData': {'ID': 143458, 'Lemma': 'у', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 10: {'FormData': {'ID': 2642927, 'Form': 'у', 'Accent': '1', 'Case': 'Dat', 'Number': 'Plur'}, 'LemmaData': {'ID': 143458, 'Lemma': 'у', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 11: {'FormData': {'ID': 2642928, 'Form': 'у', 'Accent': '1', 'Case': 'Acc', 'Number': 'Plur'}, 'LemmaData': {'ID': 143458, 'Lemma': 'у', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 12: {'FormData': {'ID': 2642929, 'Form': 'у', 'Accent': '1', 'Case': 'Ins', 'Number': 'Plur'}, 'LemmaData': {'ID': 143458, 'Lemma': 'у', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 13: {'FormData': {'ID': 2642930, 'Form': 'у', 'Accent': '1', 'Case': 'Loc', 'Number': 'Plur'}, 'LemmaData': {'ID': 143458, 'Lemma': 'у', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}}}, 5: {'Form': '2023', 'Results': {1: {'POS': 'NUM'}}}, 6: {'Form': 'г', 'Results': {1: {'FormData': {'ID': 2083355, 'Form': 'г', 'Case': 'Nom', 'Number': 'Sing'}, 'LemmaData': {'ID': 85714, 'Lemma': 'г', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 2: {'FormData': {'ID': 2083356, 'Form': 'г', 'Case': 'Gen', 'Number': 'Sing'}, 'LemmaData': {'ID': 85714, 'Lemma': 'г', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 3: {'FormData': {'ID': 2083357, 'Form': 'г', 'Case': 'Dat', 'Number': 'Sing'}, 'LemmaData': {'ID': 85714, 'Lemma': 'г', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 4: {'FormData': {'ID': 2083358, 'Form': 'г', 'Case': 'Acc', 'Number': 'Sing'}, 'LemmaData': {'ID': 85714, 'Lemma': 'г', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 5: {'FormData': {'ID': 2083359, 'Form': 'г', 'Case': 'Ins', 'Number': 'Sing'}, 'LemmaData': {'ID': 85714, 'Lemma': 'г', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 6: {'FormData': {'ID': 2083360, 'Form': 'г', 'Case': 'Loc', 'Number': 'Sing'}, 'LemmaData': {'ID': 85714, 'Lemma': 'г', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 7: {'FormData': {'ID': 2083361, 'Form': 'г', 'Case': 'Nom', 'Number': 'Plur'}, 'LemmaData': {'ID': 85714, 'Lemma': 'г', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 8: {'FormData': {'ID': 2083362, 'Form': 'г', 'Case': 'Gen', 'Number': 'Plur'}, 'LemmaData': {'ID': 85714, 'Lemma': 'г', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 9: {'FormData': {'ID': 2083363, 'Form': 'г', 'Case': 'Dat', 'Number': 'Plur'}, 'LemmaData': {'ID': 85714, 'Lemma': 'г', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 10: {'FormData': {'ID': 2083364, 'Form': 'г', 'Case': 'Acc', 'Number': 'Plur'}, 'LemmaData': {'ID': 85714, 'Lemma': 'г', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 11: {'FormData': {'ID': 2083365, 'Form': 'г', 'Case': 'Ins', 'Number': 'Plur'}, 'LemmaData': {'ID': 85714, 'Lemma': 'г', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}, 12: {'FormData': {'ID': 2083366, 'Form': 'г', 'Case': 'Loc', 'Number': 'Plur'}, 'LemmaData': {'ID': 85714, 'Lemma': 'г', 'POS': 'NOUN', 'InflClass': 'Ind', 'Gender': 'Neut'}, 'Variant': 1}}, 'SpaceAfter': False}, 7: {'Form': '.', 'Results': {1: {'POS': 'PUNCT'}}}}}}}}}
        self.assertEqual(requested, correct, 'Text annotation result mismatch')


    def testAnnotateTextConllu(self):
        """
        Annotation of a sentence in ConLL-U format
        """
        requested = slounik.annotateText('Аня была там у 2023 г.', toConllu = True)
        correct = {'Paragraphs': {1: {'Text': 'Аня была там у 2023 г.', 'Sentences': {1: {'Text': 'Аня была там у 2023 г.', 'Tokens': {1: {'FORM': 'Аня', 'MISC': '_', 'Results': {1: {'LEMMA': '_', 'UPOS': 'X', 'FEATS': '_'}}}, 2: {'FORM': 'была', 'MISC': '_', 'Results': {1: {'LEMMA': 'было', 'UPOS': 'PART', 'FEATS': '_'}, 2: {'LEMMA': 'быць', 'UPOS': 'VERB', 'FEATS': 'Aspect=Imp|Gender=Fem|InflClass=Com|Number=Sing|SubCat=Intr|Tense=Past'}}}, 3: {'FORM': 'там', 'MISC': '_', 'Results': {1: {'LEMMA': 'там', 'UPOS': 'PART', 'FEATS': '_'}, 2: {'LEMMA': 'там', 'UPOS': 'ADV', 'FEATS': 'Degree=Pos'}}}, 4: {'FORM': 'у', 'MISC': '_', 'Results': {1: {'LEMMA': 'у', 'UPOS': 'ADP', 'FEATS': '_'}, 2: {'LEMMA': 'у', 'UPOS': 'NOUN', 'FEATS': 'Case=Nom|Gender=Neut|InflClass=Ind|Number=Sing'}, 3: {'LEMMA': 'у', 'UPOS': 'NOUN', 'FEATS': 'Case=Gen|Gender=Neut|InflClass=Ind|Number=Sing'}, 4: {'LEMMA': 'у', 'UPOS': 'NOUN', 'FEATS': 'Case=Dat|Gender=Neut|InflClass=Ind|Number=Sing'}, 5: {'LEMMA': 'у', 'UPOS': 'NOUN', 'FEATS': 'Case=Acc|Gender=Neut|InflClass=Ind|Number=Sing'}, 6: {'LEMMA': 'у', 'UPOS': 'NOUN', 'FEATS': 'Case=Ins|Gender=Neut|InflClass=Ind|Number=Sing'}, 7: {'LEMMA': 'у', 'UPOS': 'NOUN', 'FEATS': 'Case=Loc|Gender=Neut|InflClass=Ind|Number=Sing'}, 8: {'LEMMA': 'у', 'UPOS': 'NOUN', 'FEATS': 'Case=Nom|Gender=Neut|InflClass=Ind|Number=Plur'}, 9: {'LEMMA': 'у', 'UPOS': 'NOUN', 'FEATS': 'Case=Gen|Gender=Neut|InflClass=Ind|Number=Plur'}, 10: {'LEMMA': 'у', 'UPOS': 'NOUN', 'FEATS': 'Case=Dat|Gender=Neut|InflClass=Ind|Number=Plur'}, 11: {'LEMMA': 'у', 'UPOS': 'NOUN', 'FEATS': 'Case=Acc|Gender=Neut|InflClass=Ind|Number=Plur'}, 12: {'LEMMA': 'у', 'UPOS': 'NOUN', 'FEATS': 'Case=Ins|Gender=Neut|InflClass=Ind|Number=Plur'}, 13: {'LEMMA': 'у', 'UPOS': 'NOUN', 'FEATS': 'Case=Loc|Gender=Neut|InflClass=Ind|Number=Plur'}}}, 5: {'FORM': '2023', 'MISC': '_', 'Results': {1: {'LEMMA': '2023', 'UPOS': 'NUM', 'FEATS': '_'}}}, 6: {'FORM': 'г', 'MISC': 'SpaceAfter=No', 'Results': {1: {'LEMMA': 'г', 'UPOS': 'NOUN', 'FEATS': 'Case=Nom|Gender=Neut|InflClass=Ind|Number=Sing'}, 2: {'LEMMA': 'г', 'UPOS': 'NOUN', 'FEATS': 'Case=Gen|Gender=Neut|InflClass=Ind|Number=Sing'}, 3: {'LEMMA': 'г', 'UPOS': 'NOUN', 'FEATS': 'Case=Dat|Gender=Neut|InflClass=Ind|Number=Sing'}, 4: {'LEMMA': 'г', 'UPOS': 'NOUN', 'FEATS': 'Case=Acc|Gender=Neut|InflClass=Ind|Number=Sing'}, 5: {'LEMMA': 'г', 'UPOS': 'NOUN', 'FEATS': 'Case=Ins|Gender=Neut|InflClass=Ind|Number=Sing'}, 6: {'LEMMA': 'г', 'UPOS': 'NOUN', 'FEATS': 'Case=Loc|Gender=Neut|InflClass=Ind|Number=Sing'}, 7: {'LEMMA': 'г', 'UPOS': 'NOUN', 'FEATS': 'Case=Nom|Gender=Neut|InflClass=Ind|Number=Plur'}, 8: {'LEMMA': 'г', 'UPOS': 'NOUN', 'FEATS': 'Case=Gen|Gender=Neut|InflClass=Ind|Number=Plur'}, 9: {'LEMMA': 'г', 'UPOS': 'NOUN', 'FEATS': 'Case=Dat|Gender=Neut|InflClass=Ind|Number=Plur'}, 10: {'LEMMA': 'г', 'UPOS': 'NOUN', 'FEATS': 'Case=Acc|Gender=Neut|InflClass=Ind|Number=Plur'}, 11: {'LEMMA': 'г', 'UPOS': 'NOUN', 'FEATS': 'Case=Ins|Gender=Neut|InflClass=Ind|Number=Plur'}, 12: {'LEMMA': 'г', 'UPOS': 'NOUN', 'FEATS': 'Case=Loc|Gender=Neut|InflClass=Ind|Number=Plur'}}}, 7: {'FORM': '.', 'MISC': '_', 'Results': {1: {'LEMMA': '.', 'UPOS': 'PUNCT', 'FEATS': '_'}}}}}}}}}
        self.assertEqual(requested, correct, 'Text ConLL-U annotation result mismatch')

    
    
    def testGenerateConllu(self):
        """
        Generate ConLL-U file content from an annotated text 
        """
        sample = 'У 47 установах вышэйшай адукацыі рэспублікі на пачатак 2024/2025 навучальнага года навучалася: 224,2 тыс. студэнтаў, 10,4 тыс. магістрантаў. Сярод іх: больш за 7,5 тыс. (23,6%) - будучыя інжынеры, 3,9 тыс. (12,3%) - педагогі, 3,4 тыс. (10,8%) - медыкі, аграрыі - 2,8 тыс.'
        requested = slounik.generateConllu(slounik.annotateText(sample, toConllu = True))  
        with open('conllu_sample.txt', 'r') as samplefile: correct = samplefile.read()      
        self.assertEqual(requested, correct, 'ConLL-U file output result mismatch')


if __name__ == '__main__':
   unittest.main(verbosity = 2)