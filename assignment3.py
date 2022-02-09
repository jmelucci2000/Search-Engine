from bs4 import BeautifulSoup
import os
import json
import re

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
def tokenizeDoc(doc):
    # might need to change doc later so that it is proper type for BeautifulSoup
    data = json.load(doc)
    soup = BeautifulSoup(data['content'], "html.parser")
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

if __name__ == '__main__':
    # get list of all files in a folder
    files = getListOfFiles('DEV')
    # inverted index: key = token; value = list of postings
    inv_index = {}
    # iterate through the docs (in json)
    i = 1
    for doc in files:
        cur_doc = open(doc, 'r')
        tokens = tokenizeDoc(cur_doc)
        tokenfreqdict = computeWordFrequencies(tokens)
        addtoInvertedIndex(tokenfreqdict, i, inv_index)
        i += 1
        cur_doc.close()

    # number of unique words, number of indexed documents, and total size (in KB) of index on disk
    print(len(inv_index))
    print(i-1)
    inv_index_file = open('result.txt', 'w')
    inv_index_file.write(str(inv_index))
    inv_index_file.close()
    
            



    
