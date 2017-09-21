import sklearn.svm
import sklearn.preprocessing
import sklearn.linear_model
import sklearn.feature_extraction.text
import sklearn.naive_bayes
import sklearn.ensemble
import sklearn.tree

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

##########################################
##==== Wrappers for sklearn modules ====##
##########################################
#########################################################
## Classifier
#########################################################
def sklearnLinearSVC(*args, **kwargs):
    return sklearn.svm.LinearSVC(*args, **kwargs)

def sklearnSGDClassifier(*args, **kwargs):
    return sklearn.linear_model.SGDClassifier(*args, **kwargs)

def sklearnLogRClassifier(*args, **kwargs):
    return sklearn.linear_model.LogisticRegression(*args, **kwargs)

def sklearnPassiveAggressiveClassifier(*args, **kwargs):
    return sklearn.linear_model.PassiveAggressiveClassifier(*args, **kwargs)

def sklearnMultinomialNB(*args, **kwargs):
    return sklearn.naive_bayes.MultinomialNB(*args, **kwargs)

def sklearnGaussianNB(*args, **kwargs):
    return sklearn.naive_bayes.GaussianNB(*args, **kwargs)

def sklearnRandomForestClassifier(*args, **kwargs):
    return sklearn.ensemble.RandomForestClassifier(*args, **kwargs)

def sklearnAdaBoostClassifier(*args, **kwargs):
    return sklearn.ensemble.AdaBoostClassifier(*args, **kwargs)

def sklearnDecisionTreeClassifier(*args, **kwargs):
    return sklearn.tree.DecisionTreeClassifier(*args, **kwargs)


#########################################################
## Feature Extraction
#########################################################
def sklearnTfidf(*args, **kwargs):
    return sklearn.feature_extraction.text.TfidfVectorizer(*args, **kwargs)

def sklearnCountVect(*args, **kwargs):
    return CountVectorizer(*args, **kwargs)

def sklearnTfTransformer(*args, **kwargs):
    return TfidfTransformer(*args, **kwargs)


#########################################################
## Pre processing
#########################################################
def sklearn_OneHotEncoder(*args, **kwargs):
    return sklearn.preprocessing.OneHotEncoder(*args, **kwargs)

##############################################
##==== END Wrappers for sklearn modules ====##
##############################################
