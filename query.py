# Joseph Melucci 14795164, Raymond Anggono 93379391, Andrew Tian 66931790

from indexcreation import Posting
import indexcreation
import math
import time
from nltk import PorterStemmer

# Retrieves a postings list for a token
def get_Postings(bk_dict, token, inv_index_f):
    if token[0] in bk_dict:
        inv_index_f.seek(bk_dict[token[0]])
        line = inv_index_f.readline()
        while line:
            curtok, postings = line.split(':')
            if token == curtok:
                postlist = eval(postings[:-1])
                newpostlist = []
                for doc_id, ns in postlist:
                    p = Posting(doc_id, ns)
                    newpostlist += [p]
                return newpostlist
            elif token < curtok:
                return []
            else:
                line = inv_index_f.readline()
        return []

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

# load bookkeeping dict into memory
def loadBookkeeping():
    bk_file = open('bk.txt', 'r')
    return eval(bk_file.readline())

# load url map into memory
def loadUrlmap():
    uf = open('urlmap.txt', 'r')
    url_map = {}
    for line in uf:
        sline = line.split(' ')
        url_map[(int)(sline[0])] = sline[1][:-1]
    return url_map

def getIdf(df, n):
    if df > 0:
        return math.log10(n/df)
    return 0.0

def getTfIdf(freq, idf):
    tf = 1 + math.log10(freq)
    return tf*idf

if __name__ == '__main__':
    
    # update or create inverted index
    indexcreation.createIndex()
    
    bk_dict = loadBookkeeping()
    inv_index_f = open('invertedindex.txt', 'r')
    url_map = loadUrlmap()
    with open("stopwords.txt", "r") as file:
            sw = [line.rstrip('\n') for line in file]
    file.close()
    sw = {'hadn', 'she', 'aren', 'and', 't', 'am', 'herself', 'hi', 'hasn', 'they', 'should', 'for', 'himself', 'over', 'such', 'more', 'out', 've', 'while', 'ourselv', 'where', 'he', 'it', 'same', 'further', 'couldn', 'myself', 'again', 'are', 'both', 'after', 'befor', 'with', 'be', 'which', 'all', 'no', 'by', 'me', 'm', 'ha', 'that', 'these', 'of', 'to', 'each', 'into', 'wouldn', 'than', 'shouldn', 'were', 'what', 'would', 'shan', 'wa', 'i', 'did', 'from', 'him', 'the', 'onli', 'do', 'isn', 'there', 'ought', 'won', 'if', 'is', 'been', 'your', 'had', 'so', 'when', 'not', 's', 'becaus', 'itself', 'my', 'some', 'thi', 'd', 'themselv', 'then', 'doesn', 'can', 'against', 'haven', 'how', 'nor', 'didn', 'down', 'veri', 'you', 'mustn', 'yourselv', 'let', 'we', 'an', 'them', 'own', 'through', 'onc', 'between', 'whi', 'cannot', 'ani', 'could', 'on', 'those', 'their', 'up', 'at', 'or', 'as', 'off', 'don', 'other', 'below', 'here', 'dure', 'who', 'in', 'whom', 're', 'but', 'have', 'her', 'too', 'abov', 'until', 'a', 'under', 'wasn', 'weren', 'doe', 'our', 'few', 'yourself', 'most', 'll', 'about'}

    # Ask user for queries
    while True:
        query = input('Enter a query: ')
        numberOfLink = int(input('Enter the number of link you want to see: '))
        start_time = time.perf_counter()

        tokens = indexcreation.tokenize(query)
        # do we process tokens in user queries ? (i.e. stemming)
        # retrieve postings lists of each token and do an AND query for them
        query_freq = indexcreation.processWordInformation(tokens)

        # remove common stopwords from query, unless there is only stopwords in the query
        for token in tokens:
            if len(query_freq) > 1 and token in sw and token in query_freq:
                query_freq.pop(token)

        # get idf score for query terms, remove low idf terms
        idf_scores = {}
        query_scores = {}
        postings_lists = {}

        
        for token in query_freq:
            postings_lists[token] = get_Postings(bk_dict, token, inv_index_f)
            idf_scores[token] = getIdf(len(postings_lists[token]), len(url_map))

        for token in idf_scores:
            if idf_scores[token] > 0.5:
                query_scores[token] = getTfIdf(query_freq[token], idf_scores[token])
            else:
                postings_lists.pop(token)

        query_normalized = indexcreation.getNormalize(query_scores)
        
        # for each document that has at least one query term, compute score using cosine similarity
        # document_scores = {doc_id:score}
        document_scores = {}
        for token in postings_lists:
            postings = postings_lists[token]
            for posting in postings:
                document_normalize = posting.ns
                if posting.doc_id in document_scores:
                    document_scores[posting.doc_id] += (document_normalize*query_normalized[token])
                else:
                    document_scores[posting.doc_id] = document_normalize*query_normalized[token]

        
        # sort document_scores by value and return top k results 
        sdoc_scores = sorted(document_scores.items(), key = lambda d: d[1], reverse=True)
        sdoc_scores = sdoc_scores[:numberOfLink]

        end_time = time.perf_counter()
        print(f"Query time: {end_time-start_time:0.4f} seconds")

        if len(sdoc_scores) < 1:
            print("No matching results.")
        for doc_id, score in sdoc_scores:
            print(url_map[doc_id])

    # Code below is for AND Boolean Queries

        # valid_documents = set()
        # i = 1
        # if len(tokens) == 1:
        #     postings = get_Postings(bk_dict, tokens[0], inv_index_f)
        #     for posting in postings:
        #         valid_documents.add(posting.doc_id)
        # while i < len(tokens):
        #     if i == 1:
        #         p1 = get_Postings(bk_dict, tokens[0], inv_index_f)
        #         p2 = get_Postings(bk_dict, tokens[1], inv_index_f)
        #         valid_documents = and_Query(p1, p2)
        #         i += 1
        #     else:
        #         if len(valid_documents) < 1:
        #             break
        #         p = []
        #         p = get_Postings(bk_dict, tokens[i], inv_index_f)
        #         valid_documents = set_and_Query(valid_documents, p)
        #         i += 1

        # # Show first 5 results from valid_postings (haven't done ranking yet)
        # valid_documents = list(valid_documents)
        # if len(valid_documents) < 1:
        #     print("No matching documents.")
        # for j in range(len(valid_documents)):
        #     if j < 5:
        #         print(url_map[valid_documents[j]])

            



    
