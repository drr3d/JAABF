import json, re
import numpy as np
import random
from collections import defaultdict

from actions.action import ACTION
from intent.classify import IntentClassifier
from utils.loader import Loader

def whatisthis(s):
    if isinstance(s, str):
        print "ordinary string"
        return True
    elif isinstance(s, unicode):
        return True
    else:
        return False

def intentReqParamLoader(param, ENT_JSONFILE):
    # Loading Entities
    def loadEntityParam():
        output_json = json.load(open(ENT_JSONFILE))

        return output_json
    
    json_datas = loadEntityParam()
    # harus dibuat error trap, jika seting keys di `simple_intent_classifier`,
    #   tidak sama dengan key di `entity_list`
    return json_datas[param]['value'], json_datas[param]['type']

def fit(sentence, dataset_folder=None, json_data=None, json_ent = None, verbose=False):
    if dataset_folder:
        train_dir = dataset_folder + 'classifier/'
    
    # Read the data
    train_data = []
    train_labels = []
    classes = []
    test_data = [sentence]
    test_labels = ['NONE']
    
    if verbose:
        print "Begin train to classifying sentence..."
    
    if json_data:
        classes = json_data.keys()
        
        if verbose:
            print "Using json as training, so adding some new class, and classes become:\n",
    else:
        classes = ['int_greetings', 'int_ask']
    
    ## Per 17-October 2016, 
    ##  dimaksud jika user menambahkan specific char @ pada trained data, maka secara otomatis
    ##  system akan menambahkan kata tersebut berulang sebanyak entities yg dimaksud
    regex = re.compile('\@\w+')

    for z in classes:
        if json_data:
            if z.lower()!='none':#Dont process none data
                f = json_data[z]["trained_data"]
            else:
                pass
        else:
            ld = Loader(train_dir)
            f = ld.loadLarge(z+'.txt', lazy_load=True)  
        
        if z.lower()!='none':
            label = z
            
            ttl = len(f)
            i=0
            
            txtre=[]
            for x in f:
                i+=1
                
                #### sub untuk autogenerate trained data addition = v0.1 ####
                regex_string = re.search(regex, x.lower())

                if regex_string:
                    xx=list(set(re.findall(regex, x.lower())))
                    ents=defaultdict(list)
                    for ii in range(len(xx)):
                        ent,type = intentReqParamLoader(xx[ii][1:], json_ent)      
                        for k, v in ent.iteritems():
                            for it in v:
                                if it not in ents:
                                    ents[xx[ii][1:]].append(it)

                    for ii in ents.keys():
                        for iii in range(len(ents[ii])):
                            random.shuffle(ents[ii])

                            train_data.append(re.sub(r'@'+ii+'',ents[ii][0],x))
                            train_labels.append(label)
                    
                ##### End Sub ####
                else:
                    if verbose:
                        msg = "Processing train data {} of {}".format(i, ttl)
                        sys.stdout.write("\r {:<10}".format(msg))
                        sys.stdout.flush()

                    sen = x
                    
                    if len(sen) >=1:
                        train_data.append(sen.lower())
                        train_labels.append(label)
        if verbose:
            print "\n"

    ######################## Begin Training to Classifying Data ########################
    model=IntentClassifier(solver_algo='linsvc')

    models=model.train(train_data, train_labels, max_df=1.0, minword=1)#, multi_class='multinomial', solver='newton-cg')
    predicted_label = [models.predict(test_data)[0]]

    from operator import itemgetter
    predict_proba=sorted(zip(models.clf.classes_, models.predict_proba(test_data)[0]), key=itemgetter(1), reverse=True)
    ####################################################################################
    
    if verbose:
        print "Hasil klasifikasi kalimat: %s , adalah: %s" %(sentence, predicted_label)
        print "\n"
    
    return predicted_label, predict_proba
    

class SentenceClassifier(ACTION):
    def __init__(self, dataset_folder=None, json_dir=None, json_file=None, json_ent_file=None):
        ACTION.__init__(self,dataset_folder, json_dir, json_file)

        self.dataset_folder = dataset_folder
        self.json_dir = json_dir
        self.json_file = json_file

        ## Per 23 Agustus 2016, `json_ent_file` juga ditambahkan ke dalam dictvocab
        ##      untuk komparasi deteksi NONE type class
        self.json_ent_file = json_ent_file
    
    def sentenceClassifier(self, sent, lastaction_taken):
        """ This function will select dialog answer proper to user sentence utterance,
            based on what class that sentence belong to.
    
        Params
        -------
            label: String
                Classification label class             
                
        Returns
        -------
            isgoalachieved: Boolean
        
            actionmainretvalue: Dict
                                ActionName
                                ActionResult
        
            confidencescore: Float
        """
        dataset_dir = self.dataset_folder
        json_datas = None

        json_ent_datas = None
        
        isgoalachieved = False
        confidencescore = 0.
        
        def loadIntentClassifier(jsondir, jsonfile):
            output_json = json.load(open(jsondir + jsonfile,'r'))
            return output_json

        if self.json_dir and self.json_file:
            ## json_datas hanya ambil `trained_data`
            json_datas = loadIntentClassifier(self.json_dir,self.json_file)
        
        def compareSentToDict(sent, dictvocab):
            # Compare 2 list and return matches
            #   if no matches than set label=NONE
            # [i for i, j in zip(sent, dictvocab) if i == j]
            return set(sent).intersection(dictvocab)
        
        if not whatisthis:
            label = ['NONE'], []
        else:
            if len(compareSentToDict(self.wordTokenize(sent), self.vocaber(verbose=False))) <=0 :
                label = ['NONE'], []
            else:
                if len(sent.strip()) > 0:
                    label = fit(sent, dataset_folder=dataset_dir, \
                                json_data = json_datas, \
                                json_ent = self.json_dir+self.json_ent_file , \
                                verbose=False)
                    isgoalachieved = True
                    confidencescore = 100.
                else:
                    label = ['NONE'], []
        
        return (isgoalachieved, {'ActionName':'sentenceClassifier', 'ActionResult':label}, confidencescore)