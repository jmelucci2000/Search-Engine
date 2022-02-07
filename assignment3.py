from bs4 import BeautifulSoup

#   Steps to Complete
# 1: Calculate/fetch the tokens from each doc
# 2: Create Inverted Index using these tokens

class Posting:
    def __init__(self, doc_id, freq):
        this.doc_id = doc_id
        this.freq = freq
    def get_docid(self):
        return this.doc_id
    def get_freq(self):
        return this.freq

# inverted index: key = token; value = list of postings
inv_index = {}
# iterate through the docs
for i, doc in enumerate(docs):
    tokens = tokenizeDoc(doc)
    tokenfreqdict = computeWordFrequencies(tokens)
    addtoInvertedIndex(tokenfreqdict, i, inv_index)

# Call this function to add a document's text to inverted index
# doc = json file representing doc
# docid = integer representing the document id
def tokenizeDoc(doc):
    # might need to change doc later so that it is proper type for BeautifulSoup
    soup = BeautifulSoup(doc, "html.parser")
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