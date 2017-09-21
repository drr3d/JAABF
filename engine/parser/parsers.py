from engine.chunker.chunk import TagChunker
from actions.action import ACTION

from bot import hmm_tagger

class Parser(ACTION):
    def __init__(self):
        self.model_fname = ''#model_fname
    
    def simpleSlotFillint(self):
        ## Alur sementara:
        ##  postag by HMM -> replace tag result by HMM with tag in entity_list.json
        ##      -> 
        print "simple slot filling"

    def simpleHMMTagger(self, sent, hmmtrainedmodel=None):
        
        chunk = TagChunker()
        
        if hmmtrainedmodel:
            taggedText, entropy = hmm_tagger.tag(sent)
        else:
            taggedText, entropy = hmm_tagger.tag(sent, savemodel=True)

        return taggedText, chunk.tagChunk(taggedText),entropy

    def parser(self, sent, lastaction_taken, method='hmm', hmmdatasetloc=None, \
                hmmtaggedner=None, hmmtrainedmodel=None, nerto_chunk=None):
        """ A Chunk Parser
    
        Params
        -------
            method: String
                    :> keras = using bi-directional LSTM Neural Network tagger
                    :> hmm = using Hidden Markov Model tagger (default)
                
        Returns
        -------
            isgoalachieved: Boolean
        
            actionmainretvalue: Dict
                                ActionName
                                ActionResult
        
            confidencescore: Float
        """
        isgoalachieved = False
        confidencescore = 0.
        
        text = sent
        ner={}

        taggedText=None
        taggedChunk=None
        
        nertochunk = nerto_chunk if nerto_chunk else ['INTENT','LOC','TIMES','PERSON','NP']
        scorefactor = 100./len(nertochunk)
        
        if method=='hmm':
            chunk = TagChunker()
            taggedText, taggedChunk, entropy = self.simpleHMMTagger(text, hmmtrainedmodel=hmmtrainedmodel)

            for ners in nertochunk:
                chunk_trextract = chunk.treeExtractor(taggedChunk, lambda t: t.label() == ners)
                ner[ners] = chunk_trextract

                if len(ner[ners]) > 0:
                    confidencescore += scorefactor
 
        # {k: v for k, v in ner.items() if v} <<== used for removing every key with empty value
        retval={k: v for k, v in ner.items() if v}
        if len(retval) > 0:
            isgoalachieved = True
            
        return (isgoalachieved, {'ActionName':'parser', 'ActionResult':retval, \
                                 'TaggedText':taggedText, 'TaggedChunk':taggedChunk, 'entropy':entropy} , confidencescore)