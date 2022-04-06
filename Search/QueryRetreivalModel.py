import Classes.Query as Query
import Classes.Document as Document
import datetime
class QueryRetrievalModel:

    indexReader=[]
    docWordScores = {}
    def __init__(self, ixReader):
        self.indexReader = ixReader
        return


    # query:  The query to be searched for.
    # topN: The maximum number of returned documents.
    # The returned results (retrieved documents) should be ranked by the score (from the most relevant to the least).
    # You will find our IndexingLucene.Myindexreader provides method: docLength().
    # Returned documents should be a list of Document.
    def retrieveQuery(self, query, topN):
        # Dict of probabilities
        probs = {}
        # Miu value
        mu = 8000
        # Dict of postings lists of all current query terms
        pls = {}
        # Dict containing the collection frequency of each token in the query divided by the total length of the entire corpus
        pwcs = {}
        # Loop through all query terms and add their corresponding values to the dict one time
        for token in query.queryContent:
            pls[token] = self.indexReader.getPostingList(token)
            pwcs[token] = self.indexReader.CollectionFreq(token) / self.indexReader.total_length
        # Loop through all documents
        for doc in self.indexReader.doc_data:
            self.docWordScores[doc] = {}
            # Get the document length
            d = self.indexReader.doc_data[doc]
            # Assign a temporary probability value to 1
            temp_prob = 1
            # Loop through query terms
            for token in query.queryContent:
                # Get the postings list for the current term
                pl = pls[token]
                # If the list exists, then evaluate the term
                if pl:
                    # Get the pwc value for the current term
                    pwc =  pwcs[token]
                    # Calculate the frequency of the current term in the current document. 0 if it does not appear, but appears in another document(s)
                    cwd = 0
                    if doc in pl:
                        cwd = pl[doc]
                    smoothing = ((cwd + (mu * pwc)) / (d + mu))
                    # Calculate the probability the term came from this document with smoothing. Then multiply this probability by the current temp value
                    temp_prob = temp_prob * smoothing
                    # Add term probability to our dictionary for the current document
                    self.docWordScores[doc][token] = smoothing
            # Add final probability to our dictionary
            probs[doc] = temp_prob
        # When finished, we should have a dictionary of doc IDs and their query likelihood. Sort these values to get the top N items
        sorted_keys = sorted(probs, key=probs.get, reverse=True)

        top_docs = []
        # Add dict entries to list of Document objects and return them
        for key in sorted_keys[:topN]:
            temp = Document.Document()
            temp.setDocId(key)
            temp.setDocNo(self.indexReader.getDocNo(key))
            temp.setScore(probs[key])
            top_docs.append(temp)

        return top_docs