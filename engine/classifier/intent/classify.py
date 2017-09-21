from __future__ import print_function

from constructors import *
from estimator import YbEstimator

class IntentClassifier():
    def __init__(self, validation_split=None, solver_algo=None, stopword=None):
        self.validation_split = validation_split

        algo_choice = {'sgd':sgd, 'logr':logisticRegresion, 'rndf':randomForest,\
                        'linsvc':liblinearSVC, 'multinb':multinomialNB,\
                        'dectree':decisionTree, 'adaboost':adaBoost}
        
        if solver_algo in algo_choice.keys():
            self.solver_algo = algo_choice[solver_algo]
        else:
            raise RuntimeError("Estimator algorithm you select is not available...")

        self.stoplist = stopword

    
    def train(self, X, y, max_df=1.0, minword=1, maxfeature=10000, **algoparam):
        #Convert a collection of text documents to a matrix of token counts
        #This implementation produces a sparse representation of the counts using scipy.sparse.coo_matrix.
        #If you do not provide an a-priori dictionary and you do not use an analyzer that does some kind of feature selection
        #   then the number of features will be equal to the vocabulary size found by analyzing the data
        # the count vectorizer produces a "bag of words" and for the term frequencies
        self._tf_vectorizer = countVectorizer(max_df=max_df, min_df=minword, max_features=maxfeature,\
                                        stop_words = self.stoplist, ngram_range=(1,3))

        self._tf_transformer = tfidfTransformer(norm='l2', use_idf=False, smooth_idf=True, sublinear_tf=False)

        from sklearn.cross_validation import train_test_split
        if self.validation_split:
            if type(self.validation_split) is float:
                # split into xx% for train and x% for test
                X_train, self.X_test, y_train, self.y_test = train_test_split(X, y, test_size=self.validation_split, \
                                                                                random_state=337, stratify=train_labels)
            else:
                raise RuntimeError("validation_split must float...")
        else:
             X_train = X
             y_train = y

        algo = self.solver_algo(**algoparam)
        model = YbEstimator(vectorizer=self._tf_vectorizer, transformer=self._tf_transformer, classifier=algo)
        
        return model.fit(X_train,y_train)
    
    def load(self, name, load_dir=None):
        model = YbEstimator()
        return model.loadModel(name=name, load_dir=load_dir)

