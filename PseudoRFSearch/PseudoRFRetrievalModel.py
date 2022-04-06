from Search import QueryRetreivalModel

class PseudoRFRetreivalModel:

    indexReader=[]

    def __init__(self, ixReader):
        self.indexReader = ixReader
        # Create QueryRetrievalModel object
        self.search  = QueryRetreivalModel.QueryRetrievalModel(self.indexReader)
        return

    # Search for the topic with pseudo relevance feedback.
    # The returned results (retrieved documents) should be ranked by the score (from the most relevant to the least).
    # query: The query to be searched for.
    # TopN: The maximum number of returned document
    # TopK: The count of feedback documents
    # alpha: parameter of relevance feedback model
    # return TopN most relevant document, in List structure

    def retrieveQuery(self, query, topN, topK, alpha):
        # this method will return the retrieval result of the given Query, and this result is enhanced with pseudo relevance feedback
        # (1) you should first use the original retrieval model to get TopK documents, which will be regarded as feedback documents  
        feedback_documents = self.search.retrieveQuery(query, topK)

        # (2) implement GetTokenRFScore to get each query token's P(token|feedback model) in feedback documents
        feedback_scores = self.GetTokenRFScore(query, feedback_documents)
        # (3) implement the relevance feedback model for each token: combine the each query token's original retrieval score P(token|document) with its score in feedback documents P(token|feedback model)
        for doc in feedback_documents:
            revised_score = 1
            for token in feedback_scores.keys():
                curr_score = 0
                # Compute the revised probability of the current token coming from the current document and then multiply it by our current revised score
                if token in self.search.docWordScores[doc.getDocId()]:
                    curr_score = self.search.docWordScores[doc.getDocId()][token]
                revised_score = revised_score * ((alpha * curr_score) + ((1 - alpha) * feedback_scores[token]))
                    
            # Once we have the revised score for the query coming from this document, update the document's score
            doc.setScore(revised_score)

        # sort all retrieved documents from most relevant to least, and return TopN
        results = sorted(feedback_documents, key=lambda x: x.getScore(), reverse=True)[:topN]
        return results

    def GetTokenRFScore(self, query, feedback_docs):
        # for each token in the query, you should calculate token's score in feedback documents: P(token|feedback documents)
        # use Dirichlet smoothing
        # save {token: score} in dictionary TokenRFScore, and return it
        mu = 2000
        # Total document length for the feedback model
        feedback_length = 0

        # Dict containing postings lists for each query term
        postings = {}
        # Dict containing probability that each token came from the entire corpus
        pwcs = {}
        # Dict containing count of each term from the feedback model
        lengths = {}

        for token in query.queryContent:
            # Create dict of postings lists
            postings[token] = self.indexReader.getPostingList(token)
            # Create dict of collection probabilities
            pwcs[token] = self.indexReader.CollectionFreq(token) / self.indexReader.total_length
            # Create empty dict of word counts from the feedback model, initialized to 0
            lengths[token] = 0
        
        for doc in feedback_docs:
            # Get total length of the feedback model
            feedback_length = feedback_length + self.indexReader.doc_data[doc.getDocId()]
            # Calculate the total # of times the token appears in the feedback model
            for token in query.queryContent:
                pl = postings[token]
                if pl:
                    if doc.getDocId() in postings[token]:
                        lengths[token] = lengths[token] + postings[token][doc.getDocId()]

        TokenRFScore={}
        # Calculate score using Dirichlet prior smoothing for each token in the feedback model
        for token in query.queryContent:
            # Ensure words not in the corpus are not evaluated
            if lengths[token] > 0:
                TokenRFScore[token] = ((lengths[token] + (mu * pwcs[token])) / (feedback_length + mu)) 

        return TokenRFScore

