# -*- coding: utf-8 -*-
# Authors: Aulia Normansyah(aulia.normansyah@pantaw.com)
#
# License: GPL 3.
from flask import abort, Response
from flask import request
from flask.ext.restful import Resource,reqparse,abort
from collections import defaultdict

from engine.parser.parsers import Parser
from engine.selector.sentenceselection import SentenceSelection
from engine.classifier.sentenceclassifier import SentenceClassifier

from engine import lexical as lx

import os, json
import re, string
import ast

class Selections(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('history', type=str, required=False,
                                   help='history of conversation',default=None,
                                   location='json')
        self.reqparse.add_argument('sentence',type=str, required=False,location='json')

        self.MAIN_DIR = os.path.abspath(os.path.curdir)
        self.MAIN_JSONDIR = self.MAIN_DIR+'/settings'

        self.JSONDIR = self.MAIN_JSONDIR+'/conversation/'

        ### Load Main Config: main.json ###
        self.main_json = json.load(open(self.MAIN_JSONDIR+"/config/main.json"))
        ###################################

        ## Modify this Entity type based on your own TAG ##
        ## ntc == NER to chunk ##
        # this is the list of TAGs system will used by, and discard other TAGs
        #   that you have set in NER training data.
        # !! Please Modify this list based your own preferences !!
        self.ntc_hmm=self.main_json['run']['ntc']
        ###################################################

        self.INT_JSONFILE=self.main_json['run']['intent_jsonfile']
        self.ENT_JSONFILE=self.main_json['run']['entity_jsonfile']

        super(Selections, self).__init__()
    
    def sentClassfication(self, sent, turn_taker):
        ##### Do sentence classification first

        if turn_taker=='human':
            _act_sentclass = SentenceClassifier(method=self.main_json['classifier']['method'], \
                                                dataset_folder=None, json_dir=self.JSONDIR, \
                                                json_file=self.INT_JSONFILE, json_ent_file=self.ENT_JSONFILE)

        cresult, cactresult, cconfscore = _act_sentclass.sentenceClassifier(sent, None)
        sent_class=cactresult['ActionResult']
        #####

        return sent_class
    
    def sentParser(self, sent, ntc, method):
        ## Parsing sentence to get NER
        _act_parser = Parser()
        ia, ner, cscore = getattr(_act_parser, 'parser')(sent.lower(), None, method=method,\
                                                         nerto_chunk=ntc, \
                                                         hmmtrainedmodel=self.MAIN_DIR+self.main_json['ner']['trained_fileloc']+self.main_json['ner']['trained_filename'])
        listof_entities = ner['ActionResult']
        tagged_text = ner['TaggedText']
        tagged_chunk = ner['TaggedChunk']
        entropy = ner['entropy']

        return listof_entities, tagged_text, tagged_chunk, entropy

    def sentSelection(self, label, loe, json_dir, json_file, is_api=False, apidict_responses=None):
        ## Begin selecting best guest answer for input user sentence
        _act_sentselect = SentenceSelection()
        result, actresult, confscore = getattr(_act_sentselect, 'sentenceSelection')(label,None,\
                                                                                    detected_entity=loe,\
                                                                                    json_dir=json_dir, \
                                                                                    json_file=json_file,\
                                                                                    dataset_folder=None,\
                                                                                    verbose=False, isapi=is_api,\
                                                                                    apidict_responses=apidict_responses)
        
        return result, actresult 
    
    def intentParamProcessing(self, label):
        from collections import OrderedDict
        # Loading data for Intent Classifier
        ## We Need OrderedDict, so order to place entity param in `simple_intent_classifier` will work
        def loadIntentParam():
            output_json = json.load(open(self.JSONDIR + self.INT_JSONFILE), object_pairs_hook=OrderedDict)

            return output_json

        json_datas = loadIntentParam()
        
        if json_datas[label]["actions"]: # not all conversation require action, so make default
            if type(json_datas[label]["actions"])=='str':
                actionname = json_datas[label]["actions"].keys() if json_datas[label]["actions"].lower().strip() !='none' else None
                reqparam = json_datas[label]["actions"][actionname[0]] if actionname else None
            else:
                actionname = json_datas[label]["actions"].keys()
                reqparam = json_datas[label]["actions"][actionname[0]]
        else:
            actionname = None
            reqparam = None

        return actionname, reqparam["param"] if reqparam else None, json_datas[label]['domain']
    
    def intentReqParamLoader(self, param):
        # Loading Entities
        def loadEntityParam():
            output_json = json.load(open(self.JSONDIR + self.ENT_JSONFILE,'r'))

            return output_json
        
        json_datas = loadEntityParam()
        # harus dibuat error trap, jika seting keys di `simple_intent_classifier`,
        #   tidak sama dengan key di `entity_list`
        return json_datas[param]['value'], json_datas[param]['type']

    ## method for spell check, by matching dict value with their key
    def simpleSpellCheck(self, list,search_ent):
        for name,ent in list.iteritems():
            if search_ent in ent:
                return name

    def reqParamCollector(self, entitylists, hsentence):
        wordtok = Parser()

        table = string.maketrans("","")

        humansentence = None
        neededparam = []
        isecss = []
        for pkeys in entitylists.keys():
            ## Collecting required param from simple_intent_classifier
            reqparams, reqparams_type = self.intentReqParamLoader(pkeys)

            ## only include str type entities
            if reqparams_type.strip().lower()=='str':
                entitylist = [word.lower() for k, v in reqparams.iteritems() for word in v]

                is_needed = str(entitylists[pkeys]["is_required"][0].lower())

                ## Matching between assumed entities from human utterance with entity_list.json
                isec = set(wordtok.wordTokenize(hsentence.lower(),True)).intersection(entitylist)
                for wordrep in isec:
                    worttorep = self.simpleSpellCheck(reqparams, wordrep)
                    
                    if wordrep.lower().strip() != worttorep.lower().strip():
                        if humansentence:
                            humansentence = humansentence.replace(wordrep, worttorep)
                        else:
                            humansentence = hsentence.lower().replace(wordrep, worttorep)
            else:                        
                regex=re.compile(reqparams['pattern'].replace("\\","\\"))
                regex_string = re.search(regex, hsentence.lower())
                if regex_string:
                    regex_string = re.search(regex, hsentence.lower()).group()
                    isecss.append(unicode(regex_string.translate(table, string.punctuation)))
                
            if is_needed == "true":
                if pkeys.upper() not in neededparam:
                    if isec:
                        for z in isec:
                            if z not in isecss:
                                isecss.append(z)      
                    neededparam.append(pkeys.upper())    
        
        return humansentence, neededparam, isecss
        
    def primaryProcess(self, sent_class, human_sentence, ntc, method, history):
        final_bot_responses = None
        missing_entities = None
        param_to_process = None
        selected_action = None
        domain = None

        table = string.maketrans("","")
        final_outputbot_responses = []

        actionname, reqparam, dom = self.intentParamProcessing(sent_class[0])
        selected_action = actionname
        domain = dom

        if not actionname:
            # not all conversation require action, so make default
            result, actresult = self.sentSelection(sent_class[0], None\
                                                    , self.JSONDIR, self.INT_JSONFILE) 
            ## Return result
            for i in range(len(actresult['ActionResult'])):
                final_outputbot_responses.append(actresult['ActionResult'][i])

            ## Sept-16-2016, dirasa entities tetap perlu diberikan
            listof_entities, tagged_text, tagged_chunk, entropy = self.sentParser(human_sentence, ntc, method.lower().strip())
            print "User utterance entropy: ", entropy
        else:
            entity_list = reqparam

            needed_param = []
            isecs = []
            param_collected = {}

            if entity_list:
                expected_user_param_responses = []

                spelling, needed_param , isecs = self.reqParamCollector(entity_list, human_sentence)
                if spelling:
                    human_sentence = spelling
                    ## Reprocess if any spellcheck occur
                    spelling, needed_param , isecs = self.reqParamCollector(entity_list, human_sentence)
                    listof_entities, tagged_text, tagged_chunk, entropy = self.sentParser(human_sentence, ntc, method.lower().strip())
                    print "User utterance entropy: ", entropy
                else:
                    listof_entities, tagged_text, tagged_chunk, entropy = self.sentParser(human_sentence, ntc, method.lower().strip())
                    print "User utterance entropy: ", entropy

                ## Collecting param from Human sentence..
                ## Bagian replace HMM Tag dengan ini masih problem, apakah perlu di replace
                ##  atau tidak, perlu di pelajari lagi.
                needed_paramto_remove = []
                param_left_over = {}

                paramtrace = len(needed_param)
                
                for pkeys in needed_param:
                    index = -1
                    if method.lower().strip()=='hmm':
                        ## Loop over tagged text processed from NER to collect and match with required param (slot to fill)
                        for i, v in enumerate(tagged_text):
                            if v[1] in needed_param:
                                if v[1] not in needed_paramto_remove:
                                    needed_paramto_remove.append(v[1])
                            
                            wordtocheck = v[0].lower().encode('utf-8').translate(table, string.punctuation)
                            if wordtocheck in isecs:
                                index = i
                                if index >= 0:
                                    wordinprocess = tagged_text[index][0].lower().encode('utf-8').translate(table, string.punctuation)
                                    wips, wips_type=self.intentReqParamLoader(pkeys.lower())
                                    if wips_type.strip().lower()=='str':
                                        if wordinprocess in wips.keys():
                                            ## !! Disini ada kemungkinan error, jika ada kalimat yang memiliki, 
                                            ##      lebih dari 2 data untuk param yang sama
                                            if wordinprocess not in param_collected.keys():
                                                # Disini perlu untuk mereplace tag dari HMM dengan tag dari entity_list.json
                                                if tagged_text[index][1].upper() != pkeys.upper():
                                                    if pkeys.upper() not in needed_param:
                                                        param_collected[wordinprocess]=pkeys.upper()
                                                    else:
                                                        if pkeys.upper() not in param_collected.keys():
                                                            ## Get list of dict values and compare with tagged_text
                                                            if wordinprocess not in [pval.lower() for pval in param_collected.values()]:
                                                                param_left_over[wordinprocess]=pkeys.upper()

                                                    # ada indikasi bahwa tag terdapat di needed_param
                                                    if pkeys.upper() not in needed_paramto_remove:
                                                        if wordinprocess not in [pval.lower() for pval in param_collected.values()]:
                                                            needed_paramto_remove.append(pkeys.upper())
                                                else:
                                                    param_collected[wordinprocess]=tagged_text[index][1].upper()
                                            #########
                                    else:
                                        regex=re.compile(wips['pattern'].replace("\\","\\"))
                                        regex_string = re.search(regex, wordinprocess)
                                        if regex_string:
                                            regex_string = regex_string.group()
                                            param_collected[wordinprocess]=pkeys.upper()
                                            # ada indikasi bahwa tag terdapat di needed_param
                                            if pkeys.upper() not in needed_paramto_remove:
                                                if wordinprocess not in [pval.lower() for pval in param_collected.values()]:
                                                    needed_paramto_remove.append(pkeys.upper())

                ## Merge param collected left over
                if param_left_over:
                    for k,v in param_left_over.iteritems():
                        if k not in param_collected.keys():
                            param_collected[k]=v
                ###############################################################################

                ## swap value Key
                nparam_collected = defaultdict(list)
                
                ##############################
                for k, v in param_collected.items():
                    nparam_collected[v].append(k)
                del param_collected

                param_to_process = nparam_collected
                entlist = [i.upper() for i in entity_list.keys()]
                
                entlist = list(set(needed_paramto_remove).intersection(entlist))
                if len(entlist)!=paramtrace:#(len(needed_param)-len(entlist)) > 0 or (len(needed_param)-len(entlist)) < 0 :
                    # masih ada parameter yang harus ditanyakan sebelum di proses
                    ## Begin selecting best guest answer for input user sentence

                    ## Per 23okt2016 , jika ada data history, masih perlu identifikasi lebih lanjut
                    for xx in needed_paramto_remove:
                        if xx in needed_param:
                            needed_param.remove(xx)

                    missing_entities = needed_param

                    # ambil 1 missing entitas saja
                    result, actresult = self.sentSelection(sent_class[0], listof_entities\
                                                            , self.JSONDIR, self.ENT_JSONFILE,\
                                                            True, entity_list[missing_entities[:1][0].lower()]["responses"]) 

                    for i in range(len(actresult['ActionResult'])):
                        final_outputbot_responses.append(actresult['ActionResult'][i])
                                        
                else:
                    ## Seluruh parameter terpenuhi, give response dengan menyertakan parameter
                    ##  yang terdeteksi pada percakapan, sebagai rekonfirm data
                    result, actresult = self.sentSelection(sent_class[0], listof_entities\
                                                            , self.JSONDIR, self.INT_JSONFILE) 
                    ## Return Result                                                                     
                    final_bot_responses=str(actresult['ActionResult'][0])

                    m = re.findall(r"\{(\w+)\}", final_bot_responses)                                                                        
                        
                    for slottoreplace in m:
                        if slottoreplace in nparam_collected.keys():
                            ## Here replacing entity slot {ENTITY_NAME} with entity get from human sentence
                            final_bot_responses = final_bot_responses.replace('{'+slottoreplace+'}',nparam_collected[slottoreplace][0])
                        else:
                            ## Disini dirasa, alih-alih shufling ulang answer selection, gunakan
                            ##  dialog state tracking
                            ## Untuk tahap awal, lebih baik buat data jawaban defaul pada `simple_intent_classifier` serapih mungkin
                            ##  rapih disini, seluruh kemungkinan jawaban pada default response harus memiliki `is_required` = `True`
                            ##  -> atau bisa juga, load seluruh default response, simpan dalam list, jika masuk ke rutin ini, 
                            ##     hapus -> data dari list
                            final_bot_responses=None #Terpilih jawaban dimana parameter kosong
                            break
                    
                    ## Masukkan jawaban ke-2, agar lebih dynamic
                    if len(actresult['ActionResult']) > 1:
                        final_outputbot_responses.append(final_bot_responses)

                        for i in range(1, len(actresult['ActionResult'])):
                            final_outputbot_responses.append(actresult['ActionResult'][i])
                    else:
                        final_outputbot_responses.append(final_bot_responses)

        return final_outputbot_responses, listof_entities , \
                domain, missing_entities, param_to_process, selected_action


    def post(self):
        ## Trick sederhana untuk tracking dialog, kita create file json untuk
        ##  setiap pelanggan(bisa based on no hape)
        args = self.reqparse.parse_args()
        history=None

        if args['history']:
            history=ast.literal_eval(args['history'])
        
        domain = None

        method = "hmm"

        if method.lower().strip() == 'hmm':
            print("\nUsing HMM as NER modeler!!\n")
            ntc = self.ntc_hmm
        else:
            abort(410)

        human_sentence = str(args['sentence']).strip()
        final_bot_responses = None
        missing_entities = None
        param_to_process = None
        selected_action = None
 
        final_outputbot_responses = []

        ## Classify human sentence class label
        sent_class , predictproba = self.sentClassfication(human_sentence,turn_taker='human')


        if sent_class[0].lower() == 'none':
            ## Sentence belum dipelajari, berikan default responses
            result, actresult = self.sentSelection(sent_class[0], None\
                                                    , self.JSONDIR, self.INT_JSONFILE) 
            ## Return result
            final_bot_responses = actresult['ActionResult'][0]
            final_outputbot_responses.append(final_bot_responses)
            listof_entities = None
                   
        else:
            #listof_entities, tagged_text, tagged_chunk = self.sentParser(human_sentence, ntc, method.lower().strip())
             final_outputbot_responses, listof_entities , \
             domain, missing_entities, param_to_process, selected_action = self.primaryProcess(sent_class, human_sentence, ntc, \
                                                                                                method, history)
             if not param_to_process:
                 param_to_process = None
        
        
        ### Construct JSON output
        response = {'status': 'ok', 'result': { 'sentence':[human_sentence],
                                                'sys_action':[final_outputbot_responses], #Answer from system
                                                'usr_action':[sent_class[0]], #Human is talking
                                                'entities':listof_entities,
                                                'domain':[domain],
                                                'missing_param':missing_entities,
                                                'param_to_process':param_to_process,
                                                'selected_action':selected_action
                                                }
                        }
        
        return Response(json.dumps(response), status=200, mimetype='application/json')