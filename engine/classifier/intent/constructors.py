from components import *
import numpy as np
##################################################
##==== Liblinear SVM classifier constructor ====##
def liblinearSVC(name="clf.linSVC",
                  C=1.0,
                  loss='squared_hinge',
                  penalty='l2',
                  dual=True,
                  tol=1e-4,
                  multi_class='ovr',
                  fit_intercept=True,
                  intercept_scaling=1,
                  class_weight='balanced',
                  random_state=np.random.RandomState(),
                  verbose=False,
                  max_iter=1000):
    # decrease parameter C of Linear SVC to increase regularization of classifier
    rval = sklearnLinearSVC(
        C=C,
        loss=loss,
        penalty=penalty,
        dual=dual,
        tol=tol,
        multi_class=multi_class,
        fit_intercept=fit_intercept,
        intercept_scaling=intercept_scaling,
        class_weight=class_weight,
        random_state=random_state,
        verbose=verbose,
        max_iter=max_iter,
    )
    return rval


#############################################################
##==== Random forest classifier ====##
#############################################################
def _trees_hp_space(
        name_func="clf.rndf",
        n_estimators=10,
        max_features="auto",
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        bootstrap=True,
        oob_score=False,
        n_jobs=1,
        random_state=np.random.RandomState(),
        verbose=False):

    hp_space = dict(
        n_estimators= n_estimators,
        max_features=max_features,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf= min_samples_leaf,
        bootstrap=bootstrap,
        oob_score=oob_score,
        n_jobs=n_jobs,
        random_state=random_state,
        verbose=verbose,
    )
    return hp_space

def randomForest(name="clf.rndf", criterion="gini", **kwargs):
    def _name(msg):
        return '%s.%s_%s' % (name, 'rfc', msg)

    hp_space = _trees_hp_space(_name, **kwargs)
    hp_space['criterion'] = criterion
    return sklearnRandomForestClassifier(**hp_space)


###################################################
##==== SGD classifier constructors ====##
###################################################
def sgd(name="clf.sgd",
        loss='log',  # default - 'hinge', use 'log'' so we can get predict_proba
        penalty='l2',  # default - 'l2'
        alpha=0.0001,  # default - 0.0001
        l1_ratio=0.15,  # default - 0.15, must be within [0, 1]
        fit_intercept=True,  # default - True
        n_iter=5,  # default - 5
        shuffle=True,  # default - True
        random_state=np.random.RandomState(),  # default - None
        epsilon=None,
        n_jobs=1,  # default - 1 (-1 means all CPUs)
        learning_rate='optimal',  # default - 'optimal'
        eta0=0.0,  # default - 0.0
        power_t=0.5,  # default - 0.5
        class_weight='balanced',
        warm_start=False,
        verbose=False):

    rval = sklearnSGDClassifier(
        loss=loss,
        penalty=penalty,
        alpha=alpha,
        l1_ratio=l1_ratio,
        fit_intercept=fit_intercept,
        n_iter=n_iter,
        shuffle=shuffle,
        random_state=random_state,
        epsilon=None,
        n_jobs=n_jobs,
        learning_rate=learning_rate,
        eta0=eta0,
        power_t=power_t,
        class_weight=class_weight,
        warm_start=False,
        verbose=verbose,
        
    )
    return rval


#########################################################
##==== Logistic Regression classifiers constructor ====##
#########################################################
def logisticRegresion(name="clf.logr", penalty='l2', dual=False, tol=1e-5, C=1.0,
                 fit_intercept=True, intercept_scaling=1, class_weight=None,
                 random_state=np.random.RandomState(), solver='liblinear', max_iter=100,
                 multi_class='ovr', verbose=0, warm_start=False, n_jobs=1):

    rval = sklearnLogRClassifier(
        penalty=penalty,
        dual=dual,
        tol=tol,
        C=C,
        fit_intercept=fit_intercept,
        intercept_scaling=intercept_scaling,
        class_weight=class_weight,
        random_state=random_state,
        solver=solver,
        max_iter=max_iter,
        multi_class=multi_class,
        verbose=verbose,
        warm_start=warm_start,
        n_jobs=n_jobs
        
    )
    return rval


#################################################
##==== Naive Bayes classifiers constructor ====##
#################################################
def multinomialNB(name="clf.multinb",
                   alpha=1.0,
                   fit_prior=True,
                   class_prior=None,
                   ):

    rval = sklearnMultinomialNB(
        alpha=alpha,
        fit_prior=fit_prior,
        class_prior=class_prior
    )
    return rval

def gaussianNB(name="clf.gausnb"):
    rval = sklearnGaussianNB()
    return rval

########################################################
##==== AdaBoost classifier/regressor constructors ====##
########################################################
def _ada_boost_hp_space(
    name_func,
    base_estimator=None,
    n_estimators=50,
    learning_rate=0.01,
    random_state=np.random.RandomState(),
    algorithm='SAMME.R'):
    '''Generate AdaBoost hyperparameters search space
    '''
    hp_space = dict(
        base_estimator=base_estimator,
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        random_state=random_state,
        algorithm=algorithm
    )
    return hp_space

def adaBoost(name="clf.adaboost", algorithm=None, **kwargs):
    '''
    '''
    def _name(msg):
        return '%s.%s_%s' % (name, 'ada_boost', msg)

    hp_space = _ada_boost_hp_space(_name, **kwargs)
    return sklearnAdaBoostClassifier(**hp_space)


##################################################
##==== Decision tree classifier constructor ====##
##################################################
def decisionTree(name="clf.dectree",
                  criterion="gini",
                  splitter="best",
                  max_features=None,
                  max_depth=None,
                  min_samples_split=2,
                  min_samples_leaf=1,
                  presort=False,
                  class_weight='balanced',
                  random_state=np.random.RandomState()):


    rval = sklearnDecisionTreeClassifier(
        criterion=criterion,
        splitter=splitter,
        max_features=max_features,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        presort=presort,
        class_weight=class_weight,
        random_state=random_state,
        )
    return rval


###############################################
##==== Various preprocessor constructors ====##
###############################################
def tfidfVectorizer(name="pre.tfidf",
          analyzer='word',
          ngram_range=(1, 1),
          stop_words=None,
          lowercase=True,
          max_df=1.0,
          min_df=1,
          max_features=None,
          binary=False,
          norm='l2',
          use_idf=True,
          smooth_idf=True,
          sublinear_tf=False,
          tokenizer=None,
          ):

    rval = sklearnTfidf(
        analyzer=analyzer,
        ngram_range=ngram_range,
        stop_words=stop_words,
        lowercase=lowercase,
        max_df=max_df,
        min_df=min_df,
        max_features=max_features,
        binary=binary,
        norm=norm,
        use_idf=use_idf,
        smooth_idf=smooth_idf,
        sublinear_tf=sublinear_tf,
        tokenizer=tokenizer,
    )
    return rval

def countVectorizer(name="pre.countvec", max_df=1.0,
                    min_df=1, max_features=None,
                    stop_words=None, ngram_range=(1,1),
                    analyzer='word'):
    #This implementation produces a sparse representation of the counts using
    #scipy.sparse.coo_matrix.
    rval = sklearnCountVect(max_df=max_df,
                    min_df=min_df, max_features=max_features,
                    stop_words=stop_words, ngram_range=ngram_range,
                    analyzer=analyzer
    )
    return rval

def tfidfTransformer(name="pre.tftransformer", norm='l2', use_idf=True, smooth_idf=True, sublinear_tf=False):
    rval = sklearnTfTransformer(norm=norm, use_idf=use_idf, smooth_idf=smooth_idf, sublinear_tf=sublinear_tf)
    return rval

def oneHotEncoder(name="pre.onehot",
                    n_values=None,
                    categorical_features=None,
                    dtype=None):
    rval = sklearnOneHotEncoder(
        n_values=n_values,
        categorical_features=categorical_features,
        dtype=np.float if dtype is None else dtype,
    )
    return rval