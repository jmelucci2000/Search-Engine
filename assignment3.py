from bs4 import BeautifulSoup
import os
import json
import re
from nltk import PorterStemmer

class Posting:
    def __init__(self, doc_id, freq):
        self.doc_id = doc_id
        self.freq = freq
    def get_docid(self):
        return self.doc_id
    def get_freq(self):
        return self.freq
    def __str__(self):
        return 'Posting(' + str(self.doc_id) + ', ' + str(self.freq) + ')'
    def __repr__(self):
        return 'Posting(' + str(self.doc_id) + ', ' + str(self.freq) + ')'


# Call this function to add a document's text to inverted index
# doc = json file representing doc
# docid = integer representing the document id
def tokenizeDoc(doc_data):
    # might need to change doc later so that it is proper type for BeautifulSoup
    soup = BeautifulSoup(doc_data['content'], "html.parser")
    text = soup.get_text()
    text = re.sub(r'[^a-zA-Z0-9 \n]', ' ', text)
    text = text.lower()
    tokens = text.split()
    return tokens

def computeWordFrequencies(tokenList):
    # create a dict, iterate through each token in tokenlist and add it to the dict
    ans = dict()
    for token in tokenList:
        if token in ans:
            ans[token] += 1
        else:
            ans[token] = 1
    return ans

def addtoInvertedIndex(tokenfreqdict, doc_id, inv_index):
    for token in tokenfreqdict:
        p = Posting(doc_id, tokenfreqdict[token])
        if token in inv_index:
            inv_index[token].append(p)
        else:
            inv_index[token] = [p]

# retrieves list of all files within a directory (including subdirectories)
def getListOfFiles(cur_dir):
    files = []
    ls = os.listdir(cur_dir)
    for f in ls:
        path = os.path.join(cur_dir, f)
        if os.path.isdir(path):
            files = files + getListOfFiles(path)
        else:
            files.append(path)
    return files

# Retrieves a postings list for a token
def get_Postings(token):
    return inv_index[token]

# Returns a set of valid documents from an AND Query
def and_Query(p1, p2):
    p1i = 0
    p2i = 0
    r = set()
    while p1i < len(p1) and p2i < len(p2):
        if p1[p1i].doc_id == p2[p2i].doc_id:
            r.add(p1[p1i].doc_id)
            p1i += 1
            p2i += 1
        elif p1[p1i].doc_id > p2[p2i].doc_id:
            p2i += 1
        else:
            p1i += 1
    return r

# Returns a set of valid documents from an AND Query 
def set_and_Query(s, p):
    si = 0
    pi = 0
    s = list(s)
    r = set()
    while si < len(s) and pi < len(p):
        if s[si] == p[pi].doc_id:
            r.add(s[si])
            si += 1
            pi += 1
        elif s[si] > p[pi].doc_id:
            pi += 1
        else:
            si += 1
    return r

if __name__ == '__main__':
    # get list of all files in a folder
    files = getListOfFiles('DEV')
    # inverted index: key = token; value = list of postings
    inv_index = {}
    # iterate through the docs (in json)
    url_map = {}
    i = 1
    for doc in files:
        cur_doc = open(doc, 'r')
        data = json.load(cur_doc)
        tokens = tokenizeDoc(data)
        tokenfreqdict = computeWordFrequencies(tokens)
        addtoInvertedIndex(tokenfreqdict, i, inv_index)
        url_map[i] = data['url']
        i += 1
        cur_doc.close()

#    inv_index_file = open('result.txt', 'w')
#    inv_index_file.write(str(inv_index))
#    inv_index_file.close()


    # Ask user for queries
    while True:
        query = input('Enter a query: ')
        tokens = query.lower().split()
        # do we process tokens in user queries ? (i.e. stemming)
        # retrieve postings lists of each token and do an AND query for them
        valid_documents = set()
        i = 1
        if len(tokens) == 1:
            if tokens[0] in inv_index:
                for posting in get_Postings(tokens[0]):
                    valid_documents.add(posting.doc_id)
        while i < len(tokens):
            if i == 1:
                p1 = []
                p2 = []
                if tokens[0] in inv_index:
                    p1 = get_Postings(tokens[0])
                if tokens[1] in inv_index:
                    p2 = get_Postings(tokens[1])
                valid_documents = and_Query(p1, p2)
                i += 1
            else:
                if len(valid_documents) < 1:
                    break
                p = []
                if tokens[i] in inv_index:
                    p = get_Postings(tokens[i])
                valid_documents = set_and_Query(valid_documents, p)
                i += 1

        # Show first 5 results from valid_postings (haven't done ranking yet)
        valid_documents = list(valid_documents)
        if len(valid_documents) < 1:
            print("No matching documents.")
        for j in range(len(valid_documents)):
            if j < 5:
                print(url_map[valid_documents[j]])

            



    
