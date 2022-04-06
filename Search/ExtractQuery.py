import Classes.Query as Query
import Classes.Path as Path
from nltk.stem import *

class ExtractQuery:

    def __init__(self):
        # 1. you should extract the 4 queries from the Path.TopicDir
        # 2. the query content of each topic should be 1) tokenized, 2) to lowercase, 3) remove stop words, 4) stemming
        # 3. you can simply pick up title only for query.
        # List of Query objects
        self.queries = []

        # Create stemmer object
        self.stemmer = PorterStemmer()

        stop_words = []
        # Read stop words into memory
        with open(Path.StopWordsDir) as s:
            for line in s:
                stop_words.append(line.strip().lower())
        s.close()

        # Read file into string, this can be done since the topic file is so small
        with open(Path.TopicDir) as f:
            for line in f:
                if "<title>" in line:
                    # Remove the <title> tag at the beginning of each topic, strip any whitespace, convert everything to lowercase, and tokenize
                    words = (line.replace("<title>", "").replace("\"", "").strip().lower().split(" "))

                    # Remove stop words and stem words not in the stop word list
                    for i, word in enumerate(words):
                        if word in stop_words:
                            words.remove(word)
                        else:
                            words[i] = self.stemmer.stem(word)
                            
                    # Create query object and add it to the list
                    query = Query.Query()
                    query.setQueryContent(words)
                    query.setTopicId(len(self.queries))
                    self.queries.append(query)
        f.close() 
        return

    # Return extracted queries with class Query in a list.
    def getQuries(self):
        return self.queries

