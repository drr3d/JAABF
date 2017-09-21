import json
import numpy as np
"""
    This class would handle Answer Sentence Selection.
"""

# Untuk JSON yang baru, menggunakan `simple_intent_classifier.json`, pada bagian actions,
#   berlaku sistem ordering, dalam artian `param` yang paling atas, memiliki prioritas
#   untuk ditanyakan terlebih dahulu.
class SentenceSelection():

    def __init__(self, bypass_ent=['NP']):
        self.bypass_ent = bypass_ent

    def entityProcess(self, lsentity):
        ## SubRoutine for bypassing specific entity, like NP(Noun Phrase)
        ent={}
        if lsentity:
            # assert type(bypass_ent) is list , 'bypass_ent must be a list'
            try:
                ent=dict((key,value) for key, value in lsentity.iteritems() if key not in self.bypass_ent)
            except:
                pass
        return ent

    def generateRandProbDist(self, ns, totals, method=None):
        """
            Params:
                ns = how many sample we have
                totals = sum of total probability to
        """
        # Mekanisme ini nanti digunakan untuk menggenerate jawaban
        #   lebih tepatnya mungkin memilih jawaban
        # ==> print np.random.choice(5,5,p=generateRandProbDist(5,1))
        if method == 'drc':
            # When alpha=1[1], the symmetric Dirichlet distribution is equivalent to a uniform distribution 
            #   over the open standard (K-1)simplex, i.e. it is uniform over all points in its support.
            #   This particular distribution is known as the flat Dirichlet distribution.
            # But in our case, we cannot assign flat distribution, in order agent must
            #   choose, at least one of sentence exist in Sample Space.
            probdist = np.random.dirichlet(np.ones(ns), size = totals)
            probdist = probdist[0]
        else:
            import random

            def rand_constrained(n, total):
                # l is a sorted list of n-1 random numbers between 0 and total
                l = sorted([0] + [total * random.random() for i in range(n - 1)] + [total])
                # Return the intervals between each successive element
                return [l[i + 1] - l[i] for i in range(n)]
            
            # [0.33022261483938276, 8.646666440311822, 1.0231109448487956]
            probdist = rand_constrained(ns, totals)
        return probdist

    def sentenceSelection(self, label, lastaction_taken=None, detected_entity=None, json_dir=None, \
                            json_file=None, dataset_folder=None, \
                            isapi=False ,apidict_responses=None, verbose=False):
        """ This function will select dialog answer proper to user sentence utterance,
            based on what class that sentence belong to.
    
        Params
        -------
            label: String
                Classification label class

            lastaction_taken: String (Optional)
                last action taken from MDP

            detected_entity

        Returns
        -------
            isgoalachieved: Boolean
        
            actionmainretvalue: Dict
                                ActionName
                                ActionResult
        
            confidencescore: Float
                            setiap step pada method yang tidak sesuai harapan,
                            mungkin bisa mengurangi score ini
        """
        isgoalachieved = False
        confidencescore = 0.
        
        usedresponses_keys = None # used if detected entity found
        intersect = [] # used if detected entity found, to detect intersected entity

        # used for replacing user defined entity with detected intersected entity
        #   user defined entity is all {WORD} in json_settings
        key_entities = []

        def loadIntentClassifier():
            output_json = json.load(open(json_dir+json_file))

            return output_json

        try:
            if label.lower()=='none':
                if json_dir and json_file:
                    json_datas = loadIntentClassifier()
                    responses_keys = json_datas['none']["responses"]
                    f = responses_keys["default"]["res"]
                    answer = np.random.choice(f, 1, p = self.generateRandProbDist(len(f), 1, method='drc'))
                    ## Dirasa akan lebih dinamis jika Bot bisa menanyakan pertanyaan beruntun
                    ##  secara terpisah(ada jeda, mengirim 2-3 pesan sekaligus), karena itu
                    ##  pada answer dalam intentclassifier, ditambahkan `//`
                    answerseparator = '//'
                    if answer:
                        if answerseparator in answer[0]:
                            answer = answer[0].split(answerseparator)

                    if verbose:
                        print "Final answer from sentSelection: ", answer

                return (isgoalachieved, {'ActionName':'sentenceSelection' , 'ActionResult':answer} , 0.)
        except:
            return (isgoalachieved, {'ActionName':'sentenceSelection' , 'ActionResult':None} , 0.)

        ## Labeling harus lebih dynamic, karena akan dibuat modular,
        ##  jika Tidak, dashboard akan sulit
        ## karena ini berhubungan dengan setting tiap user berbeda,
        ##  mungkin lebih baik construct dari json
        if json_dir and json_file:
                
            json_datas = loadIntentClassifier()
            finalent = self.entityProcess(detected_entity)

            if isapi:
                responses_keys = apidict_responses
            else:
                responses_keys = json_datas[label]["responses"]
            
            LABELS = json_datas.keys()
            
            if finalent:
                key_entities = finalent.keys()
                if verbose:
                    print "\nDETECTED ENTITY ON action.py: ", finalent,"\n"
                    print "final key_entities: ", key_entities

                word_entities = []

                ## Ekstrakting word from final entity
                for k, v in finalent.iteritems():
                    for item in v:
                        if item[0] not in word_entities:
                            word_entities.append(item[0])
                
                # Removin "default" response
                ot_keys = dict((key,value) for key, value in responses_keys.iteritems() if key != "default")
                
                if verbose:
                    print "\nResponses key left after removing default:\n",ot_keys,"\n"

                if len(ot_keys) > 0:

                    detectedentity_fromjson = []
                    for k,v in ot_keys.iteritems():
                        for k2,v2 in v.iteritems():
                            if k2 == 'detected_entity':
                                for ent in v2:
                                    if ent not in detectedentity_fromjson:
                                        detectedentity_fromjson.append(ent)

                                isec=list(set(word_entities).intersection(detectedentity_fromjson))

                                for word in isec:
                                    if word not in intersect:
                                        intersect.append(word)

                                if isec:
                                    if verbose:
                                        print "Found intersection on Response Key: ", k, " ==>> ",detectedentity_fromjson
                                        print "The intersect words is: ", intersect , "\n"
                                    usedresponses_keys=k

                                detectedentity_fromjson = []

                    if len(intersect) > 0:
                        f = responses_keys[usedresponses_keys.strip()]["res"]
                    else:
                        f = responses_keys["default"]["res"]

                else:
                    f = responses_keys["default"]["res"]
            else:
                f = responses_keys["default"]["res"]
        else:
            responses_dir = dataset_folder + 'context/'
            LABELS = {'sayhi':{'general':['responses_greetings'], 'hitime':['responses_greetings_time']}, \
                    'ask':'responses_general_ask'}
                    
            if detected_entity:
                if verbose:
                    print "\nDETECTED ENTITY ON action.py: ", detected_entity,"\n"
            else:
                z = LABELS[label]['general'][0] if label=='sayhi' else LABELS[label]
            
            # Loading training dataset
            ld = Loader(responses_dir)
            f = ld.loadLarge(z+'.txt', lazy_load=True)
        
        answer = np.random.choice(f, 1, p = self.generateRandProbDist(len(f), 1, method='drc'))
        ## Dirasa akan lebih dinamis jika Bot bisa menanyakan pertanyaan beruntun
        ##  secara terpisah(ada jeda, mengirim 2-3 pesan sekaligus), karena itu
        ##  pada answer dalam intentclassifier, ditambahkan `//`
        answerseparator = '//'
        if answer:
            if answerseparator in answer[0]:
                answer = answer[0].split(answerseparator)

        if verbose:
            print "Final answer from sentSelection: ", answer

        # Replacing user defined entities, for now, only good for one entity
        #   for multiple entites consider using dictionary
        if len(key_entities) > 0 and len(intersect) > 0:
            ans=answer[0].replace('{'+key_entities[0]+'}', ' '.join(intersect))
            answer=[ans]

        isgoalachieved = True if len(answer) > 0 else False
        confidencescore = 100. if len(answer) > 0 else 0.
        
        return (isgoalachieved, {'ActionName':'sentenceSelection' , 'ActionResult':answer}, confidencescore)