
import nltk
import numpy
from nltk import word_tokenize
import pandas as pd
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from collections import Counter
from operator import itemgetter

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")


def sort_key_words(list_in):
    """
    Sort the keyValue so that the best resuls are at the top.
    Assumes input is a list of lists, with the inner list holding the word and the value
    [
     [word, value],
     [word, value],
     [word, value],
        :       :
        :       :
     [word, value],
     [word, value],
     [word, value]
    ]
    :param list_in:
    :return:
    """

    list_in.sort(key=itemgetter(1), reverse=True)
    new_list = [x[:1][0] for x in list_in]
    return new_list


def assign_value(words):
    """
    This is where you rank the words. Takes in a list of words, and returns a list of lists, with the inner list holding the word and the value
    [
     [word, value],
     [word, value],
     [word, value],
        :       :
        :       :
     [word, value],
     [word, value],
     [word, value]
    ]
    """
    w_counts = Counter(words)
    word_and_value = []
    for w in w_counts:
        if w.count(' ') == 0:
            mult = 1
        else:
            mult = w.count(' ') + 1

        word_and_value.append([w, w_counts[w] * mult])
    return word_and_value


def get_lemitized_words_in_order(file_in):
    # We want to lemmatize words so that plurals etc. are counted as the same word
    lemmitizer = WordNetLemmatizer()
    # We are not interested in stop words
    stop_words = set(stopwords.words("english"))
    lexicon=[]
    with open(file_in, 'r') as f:
        contents = f.readlines()
        for l in contents[:]:
            all_words = word_tokenize(l)
            for i in all_words:
                if i.lower() not in stop_words:
                    # We don't want numbers or punctuation
                    if i.isalnum():
                        lexicon.append(i.lower())

    lexicon = [lemmitizer.lemmatize(i) for i in lexicon]
    return lexicon


def create_all_key_words(fileIn):
    """
    This is where I create all of the key words.   I assume that keywords will appear in the text in order,
    and the maximum length of the key words is 3. Stop words can appear between keywords.
    :param fileIn:
    :return:
    """
    lexicon2 = []

    key_words = get_lemitized_words_in_order(fileIn)

    for i in range(1, len(key_words)-2):
        double_keyword = key_words[i] + " " + key_words[i + 1]
        triple_keyword = double_keyword + " " + key_words[i + 2]
        key_words.append(double_keyword)
        key_words.append(triple_keyword)

    return key_words


def get_most_important_words(file_in, n):
    """
    Return the top n words in the database.
    file_in is the path to the file, and n is the number of words to get
    """
    # Get all key words
    key_words = create_all_key_words(file_in)

    words_and_values = assign_value(key_words)

    new_list = sort_key_words(words_and_values)

    return new_list[0:n]


def main():
    number = eval(input("How many words do you want to get?"))

    results = get_most_important_words("script1.txt", number)

    print (results)

if __name__ == "__main__":
    main()
