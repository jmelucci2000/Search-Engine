from bs4 import BeautifulSoup
import os
import json
import re
from nltk import PorterStemmer
import math

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

def writeUrlmap(url_map):
    url_map_file = open('urlmap.txt', 'w')
    for doc_id in url_map:
        url_map_file.write(str(doc_id) + ' ' + url_map[doc_id] + '\n')

def writePartialIndex(inv_index, n):
    f = open('pi' + str(n) + '.txt', 'w')
    for tok in sorted(inv_index):
        lstr = tok + ":["
        for posting in inv_index[tok]:
            lstr += "(" + str(posting.doc_id) + "," + str(posting.freq) + "),"
        lstr = lstr[:-1] + "]\n"
        f.write(lstr)

def mergePartialIndex():
    # open all partial index files simultaneously and maintain a read buffer for each one and a write buffer
    pi1f = open('pi1.txt', 'r', 10000000)
    pi2f = open('pi2.txt', 'r', 10000000)
    pi3f = open('pi3.txt', 'r', 10000000)
    l1 = pi1f.readline()
    l2 = pi2f.readline()
    l3 = pi3f.readline()
    wf = open('invertedindex.txt', 'w')
    # use a bookkeeping dict that we will load into memory to process queries
    bookkeeping = open('bk.txt', 'w')
    bk_dict = {}
    while l1 or l2 or l3:
        if l1:
            tok1, p1 = l1.split(':')
        else:
            # set token to lexographically large string
            tok1 = 'zzzzzzzzzzzzzzzz'
        if l2:
            tok2, p2 = l2.split(':')
        else:
            tok2 = 'zzzzzzzzzzzzzzzz'
        if l3:
            tok3, p3 = l3.split(':')
        else:
            tok3 = 'zzzzzzzzzzzzzzzz'
        ntok = min(tok1, tok2, tok3)
        if ntok[0] not in bk_dict:
            bk_dict[ntok[0]] = wf.tell()
        ps = []
        if tok1 == ntok:
            ps += eval(p1[:-1])
            l1 = pi1f.readline()
        if tok2 == ntok:
            ps += eval(p2[:-1])
            l2 = pi2f.readline()
        if tok3 == ntok:
            ps += eval(p3[:-1])
            l3 = pi3f.readline()
        wf.write(ntok + ":" + str(ps) + '\n')
    pi1f.close()
    pi2f.close()
    pi3f.close()
    wf.close()
    bookkeeping.write(str(bk_dict))
    bookkeeping.close()

def createIndex():
    # get list of all files in a folder
    files = getListOfFiles('DEV')
    # inverted index: key = token; value = list of postings
    inv_index = {}
    # Use a url_map to map doc_ids to urls (will write this to disk)
    url_map = {}

    # i will represent the current doc_id being processed
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
        significantToken = tokenize(significantText)
        significantFreq,significantPos = processWordInformation(significantToken)

        # Find the tf scores of each token
        tfScores = getTf(significantToken, tokenFreq,significantFreq)


        addtoInvertedIndex(tokenFreq, i, inv_index, tokenPos, tfScores)
        
        url_map[i] = data['url']
        cur_doc.close()
        # if we are 1/3 or 2/3 through the documents, dump inv_index onto disk
        if i == (int)(len(files) / 3):
            writePartialIndex(inv_index, 1)
            inv_index = {}
        elif i == 2 * (int)(len(files) / 3):
            writePartialIndex(inv_index, 2)
            inv_index = {}
        i += 1

    writePartialIndex(inv_index, 3)
    writeUrlmap(url_map)
        
    mergePartialIndex()