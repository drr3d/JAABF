## http://stackoverflow.com/questions/9575920/unsupervised-hmm-training-in-nltk
## https://sites.google.com/site/gothnlp/labs/lab2
## http://www.nltk.org/howto/probability.html
## http://stats.stackexchange.com/questions/581/differences-between-baum-welch-and-viterbi-training
## http://stackoverflow.com/questions/23704361/how-to-use-the-confusion-matrix-module-in-nltk

#from nltk.tag.hmm import HiddenMarkovModelTagger,HiddenMarkovModelTrainer
#from nltk.probability import LidstoneProbDist, SimpleGoodTuringProbDist, KneserNeyProbDist, WittenBellProbDist
import random
import nltk

#from nltk.corpus.reader import TaggedCorpusReader

from engine.tokenizer import tokenize
import dill

"""
    Some Note:
    ==========

    1.  An important problem when tracking a process with an HMM is estimating the uncertainty present in the solution.
    2. The entropy of a random variable provides a measure of its uncertainty. 
        The entropy of the state sequence that explains an observation sequence, given a model, 
        can be viewed as the minimum number of bits that, on average, will be needed to encode the state sequence (given the
            model and the observations) .
            
    3. The higher this entropy, the higher the uncertainty involved in tracking the hidden process with the current model
"""
class HMMTag():
    def __init__(self, corpusroot, pastmodel):
		#print corpusroot+pastmodel
		self.hmm=dill.load(open(corpusroot+pastmodel,'rb'))
        
    def TextTokenizer(self, sent):
        stopwords= ['kah','lah','pun','jah','jeh','mu','ku','ke','di','tapi','saya','kamu','mereka','dia', \
              'kita','adalah','dan','jika','kalau','sama','yang', \
              'sekarang','nanti','besok','kemarin','kemaren','nya','na',\
              'at','apa','ini','itu','juga','ketika','namun',\
              'sebab','oleh','malah','memang']
            
        tok = tokenize()
        kata = tok.WordTokenize(sent,removepunct=False)

        return kata
    
    def tag(self, sent, verbose=False):
        #test_sent=['Walaupun', 'Philip', 'Morris', 'secara', 'khas', 'mencoba', 'membela', 'hak', 'para', 'perokok']
        #normWords = nltk.bigrams(test_sent)

        tok_sent = self.TextTokenizer(sent)
        if verbose:
            print "-"*60
            print "HMM NER Tagger Result"
            print "\nself.hmm.probability: ", self.hmm.probability(tok_sent)
            print "self.hmm._transitions: ", self.hmm._transitions
            print "_transitions_matrix: ", self.hmm._transitions_matrix
            print "_outputs_vector: ",self.hmm._outputs_vector
            print "_priors: ", self.hmm._priors
            print "\ntok_sent is: ", self.hmm.tag(tok_sent),"\n"
            self.hmm.test([self.hmm.tag(tok_sent)], verbose=verbose)

        logprob = self.hmm.entropy([(token, None) for (token, tag) in self.hmm.tag(tok_sent)])
        if verbose:
            print("Entropy for text: ", logprob)
            print "-"*60
        return self.hmm.tag(tok_sent), logprob

 
