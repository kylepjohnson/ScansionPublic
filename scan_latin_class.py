"""
This program returns the prosimetric scansion of Latin texts.

A user is first prompted to supply the file path of the text they wish to scan. Note that this text must be a relatively
'clean' text, as the opening function (i.e., tokenize) will only remove numbers, abbreviations, and all punctuation
that is not a period. The tokenizer will also force lover the text.
The text will then be tokenized, syllabified, and all elidable syllables will be accounted for. Before the text
undergoes the actual scansion functions, the text will be re-tokenized into a simple list of words and syllables.
Finally, the simplified tokenized text will be scanned according to typical Latin scansion rules. The details of these
rules are delineated in the docstrings of the specific scansion functions. The final output is the resulting scansion.

Forthcoming features:
1) A proper clean text function
2) A classification function for the resulting scansion

Known bugs:
1) Reduplicated syllables in a single sentence are not scanned seperately
"""

from cltk.tokenize.sentence import TokenizeSentence
from nltk.tokenize.punkt import PunktLanguageVars

__author__ = 'Tyler Kirby <joseph.kirby12@ncf.edu>, Bradley Baker <bradley.baker12@ncf.edu>'
__license__ = 'MIT License'


class Scansion:

    def __init__(self):
        """"""
        self.punc = '#$%^&*()_+={}[]|:;"\'\/,<>`~'
        #? Can we change this to a list? I think it's easier to read and should be a little faster
        #punc = ['#', '$', '%', '^', '&', '*', '(', ')', "'", '_', '+', '=', '{', '}', '[', ']', '|', ':', ';', '"', "'", '/','<', '>', '`', '~']

        # numbers would be better filtered out with a regex (see below)
        self.numbers = '1234567890'

        self.abbreviations = ['Agr.', 'Ap.', 'A.', 'K.', 'D.', 'F.', 'C.', 'Cn.',
                 'L.', 'Mam.', 'M\'', 'M.', 'N.', 'Oct.', 'Opet.', 'Post.', 'Pro.',
                 'P.', 'Q.', 'Sert.', 'Ser.', 'Sex.', 'S.', 'St.', 'Ti.', 'T.',
                 'V.', 'Vol.', 'Vop.', 'Pl.']  # This is an exhaustive list of Latin praenomen abbreviations.
        self.vowels = ['a', 'e', 'i', 'o', 'u']
        self.sing_cons = ['b', 'c', 'd', 'f', 'g', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z']
        self.doub_cons = ['x', 'z']
        self.long_vowels = ['ā', 'ē', 'ī', 'ō', 'ū']
        self.diphthongs = ['ae', 'au', 'eu', 'ei', 'oe', 'ui', 'uī']
        self.stops = ['t', 'p', 'd', 'k', 'b']
        self.liquids = ['r', 'l']

    def tokenize(self, text):
        """
        Use NLTK's standard tokenizer, rm punctuation

        :param text: pre-processed text
        :return: tokenized text
        """
        sentence_tokenizer = TokenizeSentence('latin')
        sentences = sentence_tokenizer.tokenize_sentences(text.lower())

        sent_words = []
        p = PunktLanguageVars()
        for sentence in sentences:
            words = p.word_tokenize(sentence)

            assert isinstance(words, list)
            words_new = []
            for w in words:
                if w not in (self.punc or self.abbreviations or self.numbers or self.abbreviations):
                    words_new.append(w)

            # rm all numbers here with: re.compose(r'[09]')
            sent_words.append(words_new)

        return sent_words


    def make_syllables(self, sents_words):
        """
        Divides the word tokens into a list of syllables. Note that a syllable in this instance is defined as a vocalic
        group (i.e., a vowel or a diphthong). This means that all syllables which are not the last syllable in the word
        will end with a vowel or diphthong.

        :param sents_words: pre-processed sents_words
        :return: syllabified sents_words
        """
        #sents_words = tokenize(sents_words)
        all_syllables = []
        for sentence in sents_words:
            syll_per_sent = []
            for word in sentence:
                syll_start = 0  # Begins syllable iterator
                syll_per_word = []
                cur_letter_in = 0  # Begins general iterator
                while cur_letter_in < len(word):
                    letter = word[cur_letter_in]
                    if (cur_letter_in != len(word) - 1) and (word[cur_letter_in] + word[cur_letter_in + 1]) in self.diphthongs:
                        cur_letter_in += 1
                        syll_per_word.append(word[syll_start:cur_letter_in + 1])  # Syllable ends with a diphthong
                        syll_start = cur_letter_in + 1
                    elif (letter in self.vowels) or (letter in self.long_vowels):
                        syll_per_word.append(word[syll_start:cur_letter_in + 1])  # Syllable ends with a vowel
                        syll_start = cur_letter_in + 1
                    cur_letter_in += 1
                last_vowel = syll_per_word[-1][-1]  # Last vowel of a word
                cur_letter_in = len(
                    word) - 1  # Modifies general iterator to accomandate consonants after the last syllable in a word
                leftovers = ''  # Contains all of the consonants after the last vowel in a word
                while word[cur_letter_in] != last_vowel:
                    if word[cur_letter_in] != '.':
                        leftovers = word[cur_letter_in] + leftovers  # Adds consonants to leftovers
                    cur_letter_in -= 1
                syll_per_word[-1] += leftovers  # Adds leftovers to last syllable in a word
                syll_per_sent.append(syll_per_word)
            all_syllables.append(syll_per_sent)

        return all_syllables


    def qu_fix(self, sents_syllables):
        """
        Ensures that 'qu' is not treated as its own syllable.

        :param syllables: pre-processed
        :return: syllabified syllables with 'qu' counted as a single consonant
        """

        for sentence in sents_syllables:
            for word in sentence:
                for syllable in word:
                    if 'qu' in syllable:
                        qu_syll_index = word.index(syllable)
                        next_syll = qu_syll_index + 1
                        fixed_syllable = [''.join(word[qu_syll_index:(next_syll + 1)])]
                        word[qu_syll_index:(next_syll + 1)] = fixed_syllable

        return sents_syllables


    def elidable_end(self, word):
        """Checks word ending to see if it is elidable. Elidable endings include:
        1) A word ends with 'm'
        2) A word ends with a vowel
        3) A word ends with a diphthong

        :param word: syllabified/'qu' fixed word
        :return: True if the ending of the word is elidable, otherwise False
        """

        if str(word[-1]).endswith('m'):
            return True
        elif str(word[-1][-1]) in self.long_vowels:
            return True
        elif str(word[-1][-1]) in self.vowels:
            return True
        elif str(word[-1][-2] + word[-1][-1]) in self.diphthongs:
            return True
        else:
            return False

    def elidable_begin(self, word):
        """Checks word beginning to see if it is elidable. Elidable beginnings include:
        1) A word begins with 'h'
        2) A word begins with a vowel
        3) A word begins with a diphthong

        :param word: syllabified/'qu' fixed word
        :return: True if the beginning of a word is elidable, otherwise False
        """

        if str(word[0]).startswith('h'):
            return True
        elif str(word[0][0]) in self.long_vowels:
            return True
        elif str(word[0][0]) in self.vowels:
            return True
        elif str(word[0][0] + word[0][-1]) in self.diphthongs:
            return True
        else:
            return False


    def elision_fixer(self, sent_syllables):
        """
        Elides words by combining the last syllable of a word with the first of the next word if the words elide.
        E.g. [['quo'], [['us'], ['que']] => [[], ['quous', 'que']]

        :param syllables: syllabified/'qu'fixed syllables
        :return: elided syllables
        """
        for sent in sent_syllables:
            for word in sent:
                try:
                    next_word = sent[sent.index(word) + 1]
                    if self.elidable_end(word) and self.elidable_begin(next_word):
                        next_word[0] = str(str(word[-1]) + str(next_word[0]))  # Adds syllable to elided syllable
                        word.pop(-1)  # Removes redundant syllable
                    else:
                        pass
                except IndexError:
                    break
        return sent_syllables


    def syllable_condenser(self, words_syllables):
        """Reduces a list of [sentence [word [syllable]]] to [sentence [syllable]].

        :param syllables_words: elided text
        :return: text tokenized only at the sentence and syllable level
        """

        sentences_syllables = []
        for sentence in words_syllables:
            syllables_sentence = []
            for word in sentence:
                syllables_sentence += word
            sentences_syllables.append(syllables_sentence)
        return sentences_syllables


    def long_by_nature(self, syllable):
        """
        Checks if syllable is long by nature. Long by nature includes:
        1) Syllable contains a diphthong
        2) Syllable contains a long vowel

        :param syllable: current syllable
        :return: True if long by nature
        """

        # Find diphthongs
        vowel_group = ''
        for char in syllable:
            if char in self.long_vowels:
                return True
            elif char not in self.sing_cons:
                vowel_group += char

        if vowel_group in self.diphthongs:
            return True


    def long_by_position(self, syllable, sentence):
        """
        Checks if syllable is long by position. Long by position includes:
        1) Next syllable begins with two consonants, unless those consonants are a stop + liquid combination
        2) Next syllable begins with a double consonant
        3) Syllable ends with a consonant and the next syllable begins with a consonant

        :param syllable: current syllable
        :param sentence: current sentence
        :return: True if syllable is long by position
        """

        try:
            next_syll = sentence[sentence.index(syllable) + 1]
            #Long by postion by case 1
            if (next_syll[0] in self.sing_cons and next_syll[1] in self.sing_cons) and \
                    (next_syll[0] not in self.stops and next_syll[1] not in self.liquids):
                return True
            #Long by position by case 2
            elif syllable[-1] in self.vowels and next_syll[0] in self.doub_cons:
                return True
            #Long by position by case 3
            elif syllable[-1] in self.sing_cons and next_syll[0] in self.sing_cons:
                return True
            else:
                pass
        except IndexError:
            pass


    def scansion(self, sentence_syllables):
        """Scan text. A '-' represents a long syllable while a 'u' represents a short syllable.

        :param sentence_syllables: condensed syllabified text
        :return: scansion of text
        """

        scanned_text = []
        for sentence in sentence_syllables:
            scanned_sent = []
            for syllable in sentence:
                if self.long_by_position(syllable, sentence) or self.long_by_nature(syllable):
                    scanned_sent.append('-')
                else:
                    scanned_sent.append('u')
            scanned_text.append(''.join(scanned_sent))
        return scanned_text


    def syllabify(self, unsyllabified_tokens):
        """Helper class for calling syllabification-related methods.
        :param unsyllabified_tokens:
        :return:
        """
        syllables = self.make_syllables(unsyllabified_tokens)
        qu_fixed_syllables = self.qu_fix(syllables)
        elision_fixed_syllables = self.elision_fixer(qu_fixed_syllables)

        return elision_fixed_syllables

    def scan_text(self, input_string):
        tokens = self.tokenize(unscanned_text)
        syllables = self.syllabify(tokens)
        sentence_syllables = self.syllable_condenser(syllables)
        meter = self.scansion(sentence_syllables)
        return meter

if __name__ == "__main__":
    unscanned_text = 'quō usque tandem abūtēre, Catilīna, patientiā nostrā aetatis. quam diū etiam furor iste tuus nōs ēlūdet.'
    scan = Scansion()
    scanned_meter = scan.scan_text(unscanned_text)
    print(scanned_meter)
