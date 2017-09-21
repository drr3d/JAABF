#!flask/bin/python

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""

import os, sys
if os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')) not in sys.path:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')))
print sys.path
from flask import Flask, jsonify, abort, Response
from flask.ext.restful import Api, Resource, reqparse, fields, marshal

import json

### LOAD ANOTHER TAGGER HERE ###
################################
###

#Loading hmm model
from engine.tagger.hmm import HMMTag
hmm_root_path = os.path.abspath(os.path.curdir)
hmm_dataset_path = '/dataset/'
print "using hmm root path:",hmm_root_path
hmm_tagger = HMMTag(hmm_root_path+hmm_dataset_path,'hmmtag_trained_file')
###

app = Flask(__name__, static_url_path="")
app.config['DEBUG'] = True
api = Api(app)


from selection import Selections
api.add_resource(Selections, '/api/selection', endpoint = 'sentselection')

@app.route('/service/info')
def info():
    metadata = {'name': 'jaabf', 'version': '1.0.1', 'api': ['/selection']}
    return Response(json.dumps(metadata), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
