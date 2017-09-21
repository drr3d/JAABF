from __future__ import print_function

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import FeatureUnion, Pipeline, make_pipeline
from sklearn.cross_validation import KFold
from sklearn.utils import shuffle
from sklearn.multiclass import OneVsRestClassifier
from sklearn import cross_validation
from sklearn import metrics

import time
import sys

# For saving trained model
from sklearn.externals import joblib

### Decorator for check if Estimator is trained or not ###
def classAttribute(func):
    def decorated(*args, **kwargs):
        try:
            getattr(args[0], "models_")
        except AttributeError:
            raise RuntimeError("You must neither train estimator or load previous first!")
        return func(*args, **kwargs)
    return decorated

class YbEstimator(BaseEstimator, ClassifierMixin):
    def __init__(self,
                    preprocessing=None,
                    vectorizer=None,
                    transformer=None,
                    classifier=None,             
                    verbose=False,
                    seed=None,
                    use_partial_fit=False,
                 ):
        self.clf = classifier
        self.preprocessing = preprocessing
        self.vectorizer = vectorizer
        self.transformer = transformer
        self.verbose = verbose
        self.seed = seed
        self.use_partial_fit = use_partial_fit

    def __buildPipeline(self, X, y):
        self.__vectorizers = make_pipeline(self.vectorizer, self.transformer)
        #usually want to extract more features, and that means parallel processes that need to be performed
        #   with the data before putting the results together.
        #   Using a FeatureUnion, you can model these parallel processes, which are often Pipelines themselves.
        if type(self.clf).__name__ == "LinearSVC":
            from sklearn.svm import SVC
            print("Converting to OneVsRestClassifier...")
            self.clf = OneVsRestClassifier(SVC(kernel='linear', probability=True, class_weight='balanced'))

        pipeline = Pipeline([
                            ('features', FeatureUnion([
                                ('ngram_tf_idf', Pipeline([
                                ('vectorizers', self.__vectorizers)
                                ]))
                            ])),
                            ('classifier', self.clf)
                            ])
        return pipeline.fit(X,y)
    
    def fit(self, X, y):
        """
        This should fit classifier. All the "work" should be done here.

        """
        self.models_ = self.__buildPipeline(X, y)
        return self

    @classAttribute
    def getFeatureNames(self):
        return self.vectorizer.get_feature_names()
    
    @classAttribute
    def predict(self, X):
        return self.models_.predict(X)
        
    @classAttribute
    def predict_proba(self, X):
        try:
            pp = self.models_.predict_proba(X)
            return pp
        except:
            print("Unexpected error:", sys.exc_info()[0])
    
    @classAttribute
    def score(self, X, y):
        return self.models_.score(X, y)
    
    @classAttribute
    def crossValScore(self, X, y, X_Test, y_test):
        ## Getting num of features for cross-validation
        x_test = self.__vectorizers.transform(X_Test)
        print("num of test_samples: %d, num of test_features: %d \n" % x_test.shape)

        kfold = KFold(n=x_test.shape[1], n_folds=4, shuffle=True, random_state=337)
            
        X_shuf, Y_shuf = shuffle(X_Test, y_test)
        cross_val_score = cross_validation.cross_val_score(self.models_, X_shuf, \
                                                            Y_shuf, cv=kfold, \
                                                            scoring='accuracy', n_jobs=-1  # -1 = use all cores = faster
                                                            )
        print("\ncross_validation:\n",cross_val_score , "\n")
        print("Baseline: %.2f%% (%.2f%%)" % (cross_val_score.mean()*100, cross_val_score.std()*100))
    
    @classAttribute
    def saveModel(self, name, save_dir=None):
        savefile_name = name + '.pkl'
        if save_dir:
            joblib.dump(self.models_, save_dir + savefile_name)
        else:
            joblib.dump(self.models_, savefile_name)
    
    def loadModel(self, name, load_dir=None):
        if load_dir:
            self.models_=joblib.load(load_dir + name)
        else:
            self.models_=joblib.load(name)
        
        return self