from utils.loader import Loader
import json

class ACTION(object):
    def __init__(self, dataset_folder=None, json_dir=None, json_file=None, json_ent_file=None):
        self.dataset_folder = dataset_folder
        self.json_dir = json_dir
        self.json_file = json_file

        ## Per 23 Agustus 2016, `json_ent_file` juga ditambahkan ke dalam dictvocab
        ##      untuk komparasi deteksi NONE type class
        self.json_ent_file = json_ent_file
    
    def wordTokenize(self, text, tolower=False):
        import re
        if tolower:
            return [x.strip().lower() for x in re.split('(\W+)?', text) if x.strip()]
        else:
            return [x.strip() for x in re.split('(\W+)?', text) if x.strip()]

    def vocaber(self, verbose=True):
        """ This function will return only unique word in all dataset

        Params
        -------
            json_dir: string
            json_file: string
            
            dataset_folder: String
                            '/opt/pydev/boss-ai/dataset/intent/'
        Returns
        -------
            vocab = List
                    a set of distinct Words
        """
        classes = []
        ent_classes = [] #For handling entity_list.json
        vocab = []

        if verbose:
            print "vocaber using json_dir: ", self.json_dir
            print "vocaber using json_file: ", self.json_file
            print "vocaber using json_ent_file: ", self.json_ent_file
            print "vocaber using dataset_folder: ", self.dataset_folder

        def loadIntentClassifier():
            output_json = json.load(open(self.json_dir + self.json_file))

            return output_json
        
        def loadEntitiesJson():
            output_json = json.load(open(self.json_dir + self.json_ent_file))
            return output_json

        if self.json_dir:
            json_data = loadIntentClassifier()

            ## json_ent_data tidak digunakan kedalam classifier,
            ##      hanya digunakan untuk komparasi `NONE` class
            json_ent_data = loadEntitiesJson()

            if json_data:
                classes = json_data.keys()
                
                if verbose:
                    print "JSON data in vocabber():\n", json_data,"\n"
                    print "Using json as training, so adding some new class, and classes become:\n",
                    print classes

            if json_ent_data:
                ent_classes = json_ent_data.keys()

                if verbose:
                    print "JSON Entities data in vocabber():\n", json_ent_data,"\n"
                    print "Including entity list, so adding some new class, and entity classes become:\n",
                    print ent_classes
        
        if self.dataset_folder:
            train_dir = self.dataset_folder + 'classifier/'
            classes = ['int_greetings', 'int_ask']
            
        for z in classes:
            if json_data:
                if z.lower()!='none':#Dont classify NONE sentence
                    f = json_data[z]["trained_data"]
                    
                    for sent in f:
                        for word in self.wordTokenize(sent):
                            if word not in vocab:
                                vocab.append(word)
    
            else:
                ld = Loader(train_dir)
                f = ld.loadLarge(z+'.txt', lazy_load=True)
                w = ld.processRaw(f,to_lower=True)
                r = ld.rawForLangmodel(w,punct_remove=True,to_token=True)
            
                for lst in r:
                    for word in lst:
                        if word not in vocab:
                            vocab.append(word)

        if ent_classes:
            for z in ent_classes:
                for k, v in json_ent_data[z.lower()].iteritems():
                    for word in v:
                        if word not in vocab:
                            vocab.append(word)

        if verbose:
            print "Final vocabber: ", vocab                   
        return vocab