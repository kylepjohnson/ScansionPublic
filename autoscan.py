#!/usr/bin/env python 
# -*- coding: utf-8 -*-
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

__author__ = 'Tyler Kirby <joseph.kirby12@ncf.edu>, Bradley Baker <bradley.baker12@ncf.edu>'
__license__ = 'MIT License'


class KirbyScanner:
    """Scan macronized text."""

    def __init__(self):
        self.punc = '#$%^&*()_+={}[]|:;"\'\/,<>`~'
        self.numbers = '1234567890'
        self.abrev = ['Agr.', 'Ap.', 'A.', 'K.', 'D.', 'F.', 'C.', 'Cn.', 'L.', 'Mam.', 'M\'', 'M.', 'N.', 'Oct.', 'Opet.', 'Post.', 'Pro.', 'P.', 'Q.', 'Sert.', 'Ser.', 'Sex.', 'S.', 'St.', 'Ti.', 'T.', 'V.', 'Vol.', 'Vop.', 'Pl.'] #This is an exhaustive list of Latin praenomen abreviations.
        self.vowels = ['a', 'e', 'i', 'o', 'u']
        self.sing_cons = ['b', 'c', 'd', 'f', 'g', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z']
        self.doub_cons = ['x', 'z']
        self.long_vowels = ['ā', 'ē', 'ī', 'ō', 'ū']
        self.diphthongs = ['ae', 'au', 'eu', 'ei', 'oe', 'ui', 'uī']
        self.stops = ['t', 'p', 'd', 'k', 'b']
        self.liquids = ['r', 'l']

    def tokenize(self, text):
        """Splits the text into a list of sentences with a list of words.

        :param text: pre-processed text
        :return: tokenized text
        """

        sent = []
        tmp = []
        for word in text.split(" "): #splitting the text on spaces, iterate over each word
            if (word not in self.abrev) and (word not in self.punc) and (word not in self.numbers):
                tmp.append(word.lower()) #forces lower case on all words
                if "." in word: #reached end of sentence
                    word.replace('.', '')
                    sent.append(tmp)
                    tmp = []
        return sent #Text is tokenized


    def syllabify(self, text):
        """
        Divides the word tokens into a list of syllables. Note that a syllable in this instance is defined as a vocalic
        group (i.e., a vowel or a diphthong). This means that all syllables which are not the last syllable in the word
        will end with a vowel or diphthong.

        :param text: pre-processed text
        :return: syllabified text
        """

        text = self.tokenize(text)
        all_syllables = []
        for sentence in text:
            syll_per_sent = []
            for word in sentence:
                syll_start = 0 #Begins syllable iterator
                syll_per_word = []
                cur_letter_in = 0 #Begins general iterator
                while cur_letter_in < len(word):
                    letter = word[cur_letter_in]
                    if (cur_letter_in != len(word) - 1) and (word[cur_letter_in] + word[cur_letter_in + 1]) in self.diphthongs:
                        cur_letter_in += 1
                        syll_per_word.append(word[syll_start:cur_letter_in + 1]) #Syllable ends with a diphthong
                        syll_start = cur_letter_in + 1
                    elif (letter in self.vowels) or (letter in self.long_vowels):
                        syll_per_word.append(word[syll_start:cur_letter_in + 1]) #Syllable ends with a vowel
                        syll_start = cur_letter_in + 1
                    cur_letter_in += 1
                last_vowel = syll_per_word[-1][-1] #Last vowel of a word
                cur_letter_in = len(word) - 1 #Modifies general iterator to accomandate consonants after the last syllable in a word
                leftovers = '' #Contains all of the consonants after the last vowel in a word
                while word[cur_letter_in] != last_vowel:
                    if word[cur_letter_in] != '.':
                        leftovers = word[cur_letter_in] + leftovers #Adds consonants to leftovers
                    cur_letter_in -= 1
                syll_per_word[-1] += leftovers #Adds leftovers to last syllable in a word
                syll_per_sent.append(syll_per_word)
            all_syllables.append(syll_per_sent)
        return all_syllables


    def qu_fix(self, text):
        """
        Ensures that 'qu' is not treated as its own syllable.

        :param text: pre-processed
        :return: syllabified text with 'qu' counted as a single consonant
        """

        text = self.syllabify(text)
        for sent in text:
            for word in sent:
                for syll in word:
                    if 'qu' in syll:
                        qu_syll_index = word.index(syll)
                        next_syll = qu_syll_index + 1
                        word[qu_syll_index:(next_syll + 1)] = [''.join(word[qu_syll_index:(next_syll + 1)])]
                    else:
                        pass
        return text


    def elidable_end(self, word):
        """
        Checks word ending to see if it is elidable. Elidable endings include:
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
        """
        Checks word beginning to see if it is elidable. Elidable beginnings include:
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


    def elision_fixer(self, text):
        """
        Elides words by combining the last syllable of a word with the first of the next word if the words elide.
        E.g. [['quo'], [['us'], ['que']] => [[], ['quous', 'que']]

        :param text: syllabified/'qu'fixed text
        :return: elided text
        """

        syll_text = self.qu_fix(text)
        for sent in syll_text:
            for word in sent:
                try:
                    next_word = sent[sent.index(word) + 1]
                    if self.elidable_end(word) and self.elidable_begin(next_word):
                        next_word[0] = str(str(word[-1]) + str(next_word[0])) #Adds syllable to elided syllable
                        word.pop(-1) #Removes redundant syllable
                    else:
                        pass
                except IndexError:
                    break
        return syll_text


    def syllable_condenser(self, text):
        """
        Reduces the tokenized/syllablfied text to simply a list of syllables in a list of sentences, with elision accounted
        for. This allows for simplier scansion functions.

        :param text: elided text
        :return: text tokenized only at the sentence and syllable level
        """

        text = self.elision_fixer(text)
        syllables = []
        for sent in text:
            syllables_sent = []
            for word in sent:
                syllables_sent += word
            syllables.append(syllables_sent)
        return syllables


    ##########
    #Scansion#
    ##########

    def long_by_nature(self, syll):
        """
        Checks if syllable is long by nature. Long by nature includes:
        1) Syllable contains a diphthong
        2) Syllable contains a long vowel

        :param syll: current syllable
        :return: True if long by nature
        """

        vowel_group = '' #Vowel group used to check for diphthongs
        for char in syll:
            if char not in self.sing_cons:
                vowel_group += char
            if char in self.long_vowels:
                return True
        if vowel_group in self.diphthongs:
            return True
        else:
            pass


    def long_by_position(self, syll, sent):
        """
        Checks if syllable is long by position. Long by position includes:
        1) Next syllable begins with two consonants, unless those consonants are a stop + liquid combination
        2) Next syllable begins with a double consonant
        3) Syllable ends with a consonant and the next syllable begins with a consonant

        :param syll: current syllable
        :param sent: current sentence
        :return: True if syllable is long by position
        """

        try:
            next_syll = sent[sent.index(syll) + 1]
            if (next_syll[0] in self.sing_cons and next_syll[1] in self.sing_cons) and \
                (next_syll[0] not in self.stops and next_syll[1] not in self.liquids):
                return True #Long by postion by case 1
            elif (syll[-1] in self.vowels and next_syll[0] in self.doub_cons):
                return True #Long by position by case 2
            elif (syll[-1] in self.sing_cons and next_syll[0] in self.sing_cons):
                return True #Long by position by case 3
            else:
                pass
        except IndexError:
            pass

    def scan(self, input_text):
        """Scan text."""
        process_text = self.syllable_condenser(input_text)
        scanned_text = []
        for sent in process_text:
            scanned_sent = []
            for syll in sent:
                if self.long_by_position(syll, sent) or self.long_by_nature(syll):
                    scanned_sent.append('–')
                else:
                    scanned_sent.append('˘')
            scanned_text.append(''.join(scanned_sent))
        return scanned_text


if __name__ == "__main__":
    text = 'quō usque tandem abūtēre, Catilīna, patientiā nostrā aetatis.'
    scanner = KirbyScanner()
    scanned = scanner.scan(text)
    print(scanned)
