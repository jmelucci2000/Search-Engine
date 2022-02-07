from bs4 import BeautifulSoup

#   Steps to Complete
# 1: Calculate/fetch the tokens from each doc
# 2: Create Inverted Index using these tokens
# Design of the Index:
# Dictionary with token as key, value is posting

inv_index = {}

# Call this function to add a document's text to inverted index
# doc = html file representing doc
# docid = integer representing the document id
def indexDoc(doc, docid):
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    text = soup.get_text()
    text = re.sub(r'[^a-zA-Z0-9 \n]', ' ', text)
    text = text.lower()
    tokens = text.split()
    for token in tokens:
        if token in inv_index:
            inv_index[token].add(docid)
        else:
            inv_index[term] = {docid}
