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

from nltk.tokenize.punkt import PunktLanguageVars
from cltk.tokenize.sentence import TokenizeSentence

__author__ = 'Tyler Kirby <joseph.kirby12@ncf.edu>, Bradley Baker <bradley.baker12@ncf.edu>'
__license__ = 'MIT License'


##################
# Global Variables#
##################

punc = '#$%^&*()_+={}[]|:;"\'\/,<>`~'

# numbers would be better filtered out with a regex (see below)
numbers = '1234567890'

abbreviations = ['Agr.', 'Ap.', 'A.', 'K.', 'D.', 'F.', 'C.', 'Cn.',
         'L.', 'Mam.', 'M\'', 'M.', 'N.', 'Oct.', 'Opet.', 'Post.', 'Pro.',
         'P.', 'Q.', 'Sert.', 'Ser.', 'Sex.', 'S.', 'St.', 'Ti.', 'T.',
         'V.', 'Vol.', 'Vop.', 'Pl.']  # This is an exhaustive list of Latin praenomen abbreviations.
vowels = ['a', 'e', 'i', 'o', 'u']
sing_cons = ['b', 'c', 'd', 'f', 'g', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z']
doub_cons = ['x', 'z']
long_vowels = ['ā', 'ē', 'ī', 'ō', 'ū']
diphthongs = ['ae', 'au', 'eu', 'ei', 'oe', 'ui', 'uī']
stops = ['t', 'p', 'd', 'k', 'b']
liquids = ['r', 'l']


################
# Pre-Processing#
################

def tokenize(text):
    """
	Use NLTK's standard tokenizer, rm punctuation

	:param text: pre-processed text
	:return: tokenized text
	"""
    sent = []
    tmp = []
    for word in text.split(" "):  # splitting the text on spaces, iterate over each word
        if (word not in abbreviations) and (word not in punc) and (word not in numbers):
            tmp.append(word.lower())  #forces lower case on all words
            if "." in word:  #reached end of sentence
                word.replace('.', '')
                sent.append(tmp)
                tmp = []
    return sent

def tokenize_new(text):
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
            if w not in (punc or abbreviations or numbers or abbreviations):
                words_new.append(w)

        # rm all numbers here with: re.compose(r'[09]')
        sent_words.append(words_new)

    return sent_words


def syllabify(text):
    """
	Divides the word tokens into a list of syllables. Note that a syllable in this instance is defined as a vocalic
	group (i.e., a vowel or a diphthong). This means that all syllables which are not the last syllable in the word
	will end with a vowel or diphthong.

	:param text: pre-processed text
	:return: syllabified text
	"""

    text = tokenize(text)
    all_syllables = []
    for sentence in text:
        syll_per_sent = []
        for word in sentence:
            syll_start = 0  # Begins syllable iterator
            syll_per_word = []
            cur_letter_in = 0  # Begins general iterator
            while cur_letter_in < len(word):
                letter = word[cur_letter_in]
                if (cur_letter_in != len(word) - 1) and (word[cur_letter_in] + word[cur_letter_in + 1]) in diphthongs:
                    cur_letter_in += 1
                    syll_per_word.append(word[syll_start:cur_letter_in + 1])  # Syllable ends with a diphthong
                    syll_start = cur_letter_in + 1
                elif (letter in vowels) or (letter in long_vowels):
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


def syllabify_new(sents_words):
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
                if (cur_letter_in != len(word) - 1) and (word[cur_letter_in] + word[cur_letter_in + 1]) in diphthongs:
                    cur_letter_in += 1
                    syll_per_word.append(word[syll_start:cur_letter_in + 1])  # Syllable ends with a diphthong
                    syll_start = cur_letter_in + 1
                elif (letter in vowels) or (letter in long_vowels):
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

    fixed_syllables = qu_fix_new(all_syllables)

    return fixed_syllables


def qu_fix(text):
    """
	Ensures that 'qu' is not treated as its own syllable.

	:param text: pre-processed
	:return: syllabified text with 'qu' counted as a single consonant
	"""

    text = syllabify(text)
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

def qu_fix_new(sents_syllables):
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

    return syllables


def elidable_end(word):
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
    elif str(word[-1][-1]) in long_vowels:
        return True
    elif str(word[-1][-1]) in vowels:
        return True
    elif str(word[-1][-2] + word[-1][-1]) in diphthongs:
        return True
    else:
        return False


def elidable_begin(word):
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
    elif str(word[0][0]) in long_vowels:
        return True
    elif str(word[0][0]) in vowels:
        return True
    elif str(word[0][0] + word[0][-1]) in diphthongs:
        return True
    else:
        return False


def elision_fixer(text):
    """
	Elides words by combining the last syllable of a word with the first of the next word if the words elide.
	E.g. [['quo'], [['us'], ['que']] => [[], ['quous', 'que']]

	:param text: syllabified/'qu'fixed text
	:return: elided text
	"""

    syll_text = qu_fix(text)
    for sent in syll_text:
        for word in sent:
            try:
                next_word = sent[sent.index(word) + 1]
                if elidable_end(word) and elidable_begin(next_word):
                    next_word[0] = str(str(word[-1]) + str(next_word[0]))  # Adds syllable to elided syllable
                    word.pop(-1)  # Removes redundant syllable
                else:
                    pass
            except IndexError:
                break
    return syll_text

def elision_fixer_new(text):
    """
	Elides words by combining the last syllable of a word with the first of the next word if the words elide.
	E.g. [['quo'], [['us'], ['que']] => [[], ['quous', 'que']]

	:param text: syllabified/'qu'fixed text
	:return: elided text
	"""

    syll_text = qu_fix(text)
    for sent in syll_text:
        for word in sent:
            try:
                next_word = sent[sent.index(word) + 1]
                if elidable_end(word) and elidable_begin(next_word):
                    next_word[0] = str(str(word[-1]) + str(next_word[0]))  # Adds syllable to elided syllable
                    word.pop(-1)  # Removes redundant syllable
                else:
                    pass
            except IndexError:
                break
    return syll_text


def syllable_condenser(text):
    """
	Reduces the tokenized/syllablfied text to simply a list of syllables in a list of sentences, with elision accounted
	for. This allows for simplier scansion functions.

	:param text: elided text
	:return: text tokenized only at the sentence and syllable level
	"""

    text = elision_fixer(text)
    syllables = []
    for sent in text:
        syllables_sent = []
        for word in sent:
            syllables_sent += word
        syllables.append(syllables_sent)
    return syllables


##########
# Scansion#
##########

def long_by_nature(syll):
    """
	Checks if syllable is long by nature. Long by nature includes:
	1) Syllable contains a diphthong
	2) Syllable contains a long vowel

	:param syll: current syllable
	:return: True if long by nature
	"""

    vowel_group = ''  #Vowel group used to check for diphthongs
    for char in syll:
        if char not in sing_cons:
            vowel_group += char
        if char in long_vowels:
            return True
    if vowel_group in diphthongs:
        return True
    else:
        pass


def long_by_position(syll, sent):
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
        if (next_syll[0] in sing_cons and next_syll[1] in sing_cons) and \
                (next_syll[0] not in stops and next_syll[1] not in liquids):
            return True  #Long by postion by case 1
        elif syll[-1] in vowels and next_syll[0] in doub_cons:
            return True  #Long by position by case 2
        elif syll[-1] in sing_cons and next_syll[0] in sing_cons:
            return True  #Long by position by case 3
        else:
            pass
    except IndexError:
        pass


def scansion(text):
    """
	Scans text. A '-' represents a long syllable while a 'u' represents a short syllable.

	:param text: condensed syllabified text
	:return: scansion of text
	"""

    process_text = syllable_condenser(text)
    scanned_text = []
    for sent in process_text:
        scanned_sent = []
        for syll in sent:
            if long_by_position(syll, sent) or long_by_nature(syll):
                scanned_sent.append('-')
            else:
                scanned_sent.append('u')
        scanned_text.append(''.join(scanned_sent))
    return scanned_text


def open_file(file_path):
    """Open file and return string."""
    file_path = input('Enter file path: ')
    with open(file_path) as file_open:
        return file_open.read()


if __name__ == "__main__":
    unscanned_text = 'quō usque tandem abūtēre, Catilīna, patientiā nostrā aetatis. quam diū etiam furor iste tuus nōs ēlūdet.'
    # old
    scanned_text = scansion(unscanned_text)
    print(scanned_text)

    # new
    tokens = tokenize_new(unscanned_text)
    syllables = syllabify_new(tokens)
    #fixed_syllables = qu_fix_new(syllables)
    elision_fixer_new(syllables)


