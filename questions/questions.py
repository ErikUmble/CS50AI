import nltk
import sys
import os
import string

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = {}
    for file in os.listdir(directory):
        path = os.path.join(directory, file)
        if path.endswith(".txt"):
            with open(path, "r", encoding="utf8") as text:
                files[file] = text.read()

    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by converting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    tokens = nltk.word_tokenize(document)
    words = []
    for token in tokens:
        token = token.lower()
        if not (token in string.punctuation or token in nltk.corpus.stopwords.words("english")):
            words.append(token)
    return words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idfs = {}
    for word_lists in documents.values():
        for word in word_lists:
            idfs[word] = idfs.get(word, 0)

    for word in idfs.keys():
        doc_count = 0
        for word_lists in documents.values():
            if word in word_lists:
                doc_count += 1

        idfs[word] = len(documents)/doc_count

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    file_scores = {}
    for file, word_list in files.items():
        file_score = 0
        for word in query:
            if word in word_list:
                file_score += idfs[word] * word_list.count(word)

        file_scores[file] = file_score

    ordered_files = sorted(file_scores.keys(), key=lambda x: file_scores[x], reverse=True)
    return ordered_files[0:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_scores = {}
    sentence_densities = {}
    for sentence, word_list in sentences.items():
        sentence_score = 0
        sentence_density = 0
        for word in query:
            if word in word_list:
                sentence_score += idfs[word]

        for word in word_list:
            if word in query:
                sentence_density += 1

        # sentence score is just the sum of idfs values for every word that appears in both the query and the sentence
        sentence_scores[sentence] = sentence_score
        # sentence density is (the number of word in sentence that appear in query) / (number of words in sentence)
        sentence_densities[sentence] = sentence_density/(len(word_list))

    # order by sentence score, breaking ties by sentence density
    ordered_sentences = sorted(sentence_scores.keys(),
                               key=lambda x: (sentence_scores[x], sentence_densities[x]), reverse=True)
    return ordered_sentences[0:n]


if __name__ == "__main__":
    main()
