from bs4 import BeautifulSoup
import os
import json
import re

class Posting:
    def __init__(self, doc_id, freq,tf, pos):
        self.doc_id = doc_id
        self.freq = freq
        self.tf = tf
        self.pos = pos
    def get_docid(self):
        return self.doc_id
    def get_freq(self):
        return self.freq
    def __str__(self):
        return 'Posting(' + str(self.doc_id) + ', ' + str(self.freq) +',' + str(self.tf)+ ',' + str(self.pos) + ')'
    def __repr__(self):
        return 'Posting(' + str(self.doc_id) + ', ' + str(self.freq) +',' + str(self.tf)+ ','+ str(self.pos) + ')'


# Call this function to add a document's text to inverted index
# doc = json file representing doc
# docid = integer representing the document id
def tokenize(text):
    ps = PorterStemmer()
    text = re.sub(r'[^a-zA-Z0-9 \n]', ' ', text)
    text = text.lower().split()
    token = []
    
    for t in text:
        token.append(ps.stem(t))
        
    return token

def processWordInformation(tokenList):
    # create a dict, iterate through each token in tokenlist and add it to the dict
    freq = dict()
    positions = dict()
    i = 0
    for token in tokenList:
        if token in freq:
            freq[token] += 1
            positions[token].append(i)
        else:
            freq[token] = 1
            positions[token] = [i]
        i+=1
    return freq, positions

def getTf(significantTokens,tokenFreq,significantFreq):
    tfScores = {}
    for token in tokenFreq:
        tf = tokenFreq[token]
        if token in significantTokens:
            tf = 2 + math.log10(tf) + math.log(significantFreq[token])
        elif token not in significantTokens:
            tf = 1 + math.log10(tf)
        
        tfScores[token] = tf
    return tfScores

def addtoInvertedIndex(tokenFreq, doc_id, inv_index, positions, tfScores):
    for token in tokenFreq:
        p = Posting(doc_id, tokenFreq[token], tfScores[token], positions[token])
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

def createIndex():
    # get list of all files in a folder
    files = getListOfFiles('DEV')
    # inverted index: key = token; value = list of postings
    inv_index = {}
    # iterate through the docs (in json)
    url_map = {}
    i = 1

    for doc in files:
        # Process the current file text
        cur_doc = open(doc, 'r')
        data = json.load(cur_doc)
        soup = BeautifulSoup(data['content'], "html.parser")
        text = soup.get_text()

        # Retrieve tokens of the text
        tokens = tokenize(text)

        # Find the corresponding token frequencies and position
        tokenFreq, tokenPos = processWordInformation(tokens)

        # Find the more significant words
        significantTags = ["title","strong","b", "h1", "h2", "h3"]
        significantText = ""
        for words in soup.findAll(significantTags):
            significantText += " " + words.text.strip()
        significantToken = tokenize(importantText)
        significantFreq,significantPos = processWordInformation(significantToken)

        # Find the tf scores of each token
        tfScores = getTf(significantToken, tokenFreq,significantFreq)
        addtoInvertedIndex(tokenFreq, i, inv_index, tokenPos, tfScores)
        
        url_map[i] = data['url']
        i += 1
        cur_doc.close()

    inv_index_file = open('result.txt', 'w')
    inv_index_file.write(str(inv_index))
    inv_index_file.close()