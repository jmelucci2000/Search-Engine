# Joseph Melucci 14795164, Raymond Anggono 93379391, Andrew Tian 66931790

from indexcreation import Posting
import indexcreation
from bs4 import BeautifulSoup
import os
import json
import re
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
                for doc_id, freq in postlist:
                    p = Posting(doc_id, freq, 0, 0)
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

if __name__ == '__main__':
    
    # update or create inverted index
    #indexcreation.createIndex()
    
    bk_dict = loadBookkeeping()
    inv_index_f = open('invertedindex.txt', 'r')
    url_map = loadUrlmap()

    # Ask user for queries
    while True:
        query = input('Enter a query: ')
        tokens = query.lower().split()
        # do we process tokens in user queries ? (i.e. stemming)
        # retrieve postings lists of each token and do an AND query for them
        valid_documents = set()
        i = 1
        if len(tokens) == 1:
            postings = get_Postings(bk_dict, tokens[0], inv_index_f)
            for posting in postings:
                valid_documents.add(posting.doc_id)
        while i < len(tokens):
            if i == 1:
                p1 = get_Postings(bk_dict, tokens[0], inv_index_f)
                p2 = get_Postings(bk_dict, tokens[1], inv_index_f)
                valid_documents = and_Query(p1, p2)
                i += 1
            else:
                if len(valid_documents) < 1:
                    break
                p = []
                p = get_Postings(bk_dict, tokens[i], inv_index_f)
                valid_documents = set_and_Query(valid_documents, p)
                i += 1

        # Show first 5 results from valid_postings (haven't done ranking yet)
        valid_documents = list(valid_documents)
        if len(valid_documents) < 1:
            print("No matching documents.")
        for j in range(len(valid_documents)):
            if j < 5:
                print(url_map[valid_documents[j]])

            



    
