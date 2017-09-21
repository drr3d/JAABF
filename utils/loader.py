import re,os,sys,string
import collections

from time import time

from engine.tokenizer import tokenize

pattern = ['(?<!\w\.\w.)(?<![A-Z][a-z\.])(?<=\.|\?)\s',
           '(?<=[^A-Z].[.?]) #(?=[A-Z])',
           '\s\s+',
	       '\n\n+',
	       '\b([a-zA-Z]+)-[a-z]+']

class Loader():
    languageDBFolder =  ''#os.getcwd()#'/libraries/languagedb/'

    def __init__(self, langFolder):
        self.languageDBFolder = self.languageDBFolder + langFolder
   
    def processRaw(self, f, clear_newline = True, clear_dblspace = True, \
                   to_lower=False, verbose=False):
        t0 = time()
        if verbose:
            print("Processing raw text...")
        words = ''.join(f)
        if to_lower:
            words = words.lower()
        words = re.sub(r'[^\x00-\x7F]+','',words).strip()
        if clear_newline: words = re.sub(r'\r\n',' ',words).strip()
        if clear_dblspace: words = re.sub(r'\s\s+',' ',words).strip()

        if verbose:
            print("Processing raw text done in %fs" % (time() - t0))
            print("\n")
        
        return words # print first 5000 word       
        
    def readInChunks(self, file_object, chunk_size=1024):
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data
            
    def lazyRead(self, file_object):
        return file_object.readlines()
        
    def loadLarge(self, corpusname, lazy_load=False, verbose=False):
        if verbose:
            print("Loading training corpus...")
        t0 = time()
        f = open(self.languageDBFolder + corpusname)
        
        if verbose:
            print("Loading Corpus done in %fs" % (time() - t0))
            print("\n")
        if lazy_load:
            return self.lazyRead(f)
        else:
            return self.readInChunks(f)

    def rawForVector(self, f, min_word=2, verbose=False):
        """ Word level vector """
        tok = tokenize()
        t0 = time()
        if verbose:
            print "Splitting sentence for vector processing..."
        table = string.maketrans("","")
        
        words = re.split(r''+pattern[0]+'',f)
        words = [z.translate(table, string.punctuation) for z in words]
        words = filter(lambda x: len(tok.WordTokenize(x)) >= min_word, words)
        words = [tok.WordTokenize(z) for z in words]

        if verbose:
            print "total sentence for process: ", len(words)
            print "total unique words(vocabulary): ", len(self.word_constructor(words))
            print("Splitting sentence for vector done in %fs" % (time() - t0))
            print "\n"
        
        return words
    
    def rawForLangmodel(self, f, punct_remove=False, to_token=True, min_word=2):
        tok = tokenize()
        table = string.maketrans("","")

        # Splitting sentence based on new line then Regex pattern[0]
        words = re.split(r'\n',f)
        words = re.split(r''+pattern[0]+'',f)
        
        if punct_remove: words = [z.translate(table, string.punctuation) for z in words]

        if to_token:
            words = [tok.WordTokenize(z) for z in words]
            words = filter(lambda x: len(x) >= min_word, words)
        else:
            words = filter(lambda x: len(tok.WordTokenize(x)) >= min_word, words)
        return words

