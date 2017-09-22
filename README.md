JAABF
===

Stands for Just Another Anoying chat Bot Framework

Chatbot framework ini menggunakan mekanisme Intent-Action, dimana setiap hasil klasifikasi Intent yang diperoleh akan dipasangkan dengan Action tertentu.

JAABF dijalankan menggunakan Flask, sehingga memudahkan untuk integrasi dengan aplikasi lain.

Code is still very messed up, i still working hard and need all your help guys, to make this chatbot framework event better.

## Environtment and Package Set Up

> *	Python 2.7
> *	[Flask](http://flask.pocoo.org/)
> *	[Flask-restful](http://flask-restful-cn.readthedocs.io/en/0.3.4/installation.html)
> * NLTK 3.2.1 (pip install "nltk==3.2.1")
> * NumPy
> * Scikit Learn
___

Flow and Set-Up
===

## Basic Bot Flow

<p align="center">
<img src="https://github.com/drr3d/JAABF/blob/assets/basic-flow.PNG" width="650" height="275"/>
</p>

## First time BOT Set-Up

1. Prepare conversation settings, and place under: ``` settings/conversation ```.
2. Prepare Entity settings, and place under: ``` settings/conversation ```.
3. Set up ``` settings/config/main.json ``` based on your own preferences and settings.
___

## How To Run

just execute `python __init__.py` to run the server

___

A.P.I Resource
===

## SentenceSelection


`ccurl -i -H "Content-Type: application/json" -X POST -d '{"sentence":"mau beli tiket pesawat ke Bandung", "method":"hmm"}' http://127.0.0.1:5000/api/selection`

	Argument:
		<method> = (String) `hmm` or other you make_it_your_own_tagger , default is `hmm`
		<sentence> = (String) just a common sentence



___


JSON Settings Explained:
===

## entity_list.json

Berisi setting untuk entitas, bisa dianggap ini bagian dari NER (Named Entity Recognition), Used for **simple slot filling** mechanism.

	{
    	"time":{
	        "pagi":["pagi", "pg","pgi"],
	        "siang":["siang","syang","siyang"],
	        "sore":["sore","sre"],
	        "malam":["malam","malem","mlm","malm"],
	        "besok":["besok","bsok","bsk"]
	    },
	    "dayname":{
	        "senin":["senin"],
	        "selasa":["selasa"],
	        "rabu":["rabu"],
	        "kamis":["kamis"],
	        "jumat":["jumat"],
	        "sabtu":["sabtu"],
	        "minggu":["minggu"]
	    }
	}


## intent_classifier.json

{TIME} slot pada contoh key `responses` di bawah akan di replace berdasar user input detected Entity yang terkain dengan **entity_list.json**.

slot yang akan direplace hanya ada pada `responses` default direct action dari `intent classifier`, 
sedangkan responses pada `action` tidak akan dilakukan proses slot filling

	{
		"greetings":{
	        "trained_data":[
	            "halo bos .",
	            "hai bos .",
	            "selamat pagi ."
	        ],
	        "responses":{
	            "default":{
	                "res":[
	                    "Halo , {TIME} juga boss",
	                    "Hai , {TIME} juga boss",
	                    "Ya {TIME} , ada yang bisa kami bantu boss ?",
	                    "{TIME} juga, apa kabar hari ini boss ?"
	                ]
	            }
	        },
	        "domain":"general_conversation",
	        "actions":{
	            "say_time":{
	                "param":{
	                    "time":{
	                        "responses":{
	                            "default":{
	                                "res":[
	                                    "Halo boss",
	                                    "Hai juga boss",
	                                    "Ya, ada yang bisa kami bantu boss ?",
	                                    "Halo juga, apa kabar hari ini boss ?"
	                                ]
	                            }
	                        },
	                        "is_required":["True"]
	                    }
	                }
	            }
	        }
	    }
	}

Notes
===

## Things can not be forgotten

- Classifier
	- used for classify user utterance.
- Named Entity Recognizer
	- Used for detecting Intent.
	- Available method for this version:
		- HMM (using NLTK)


## Example result:

A.P.I would return JSON result.

<img src="https://github.com/drr3d/JAABF/blob/assets/result-2.PNG" width="425"/> <img src="https://github.com/drr3d/JAABF/blob/assets/result-2_1.PNG" width="425"/> 
___


License
===

This project is licensed under the GPL-3.0 License - see the LICENSE.md file for details