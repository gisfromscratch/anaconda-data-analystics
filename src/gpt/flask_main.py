import flask
from flask import request, jsonify
import glob
import os
from transformers import pipeline

files_dir = os.environ['QA_CONTEXT_PATH']

for txt_file in glob.glob('{0}/*.txt'.format(files_dir)):
    with open(txt_file, 'r') as in_stream:
        qa_context = in_stream.read()
        qa_context += '\n'

app = flask.Flask('GPT-Generator')
app.config['DEBUG'] = True

qa_guide = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')

#text_generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')
text_generator = pipeline('text-generation', model='EleutherAI/gpt-neo-125M')

@app.route('/answer', methods=['GET'])
def answer_question():
    if 'question' in request.args:
        question = request.args['question']
    else:
        return "Error: No question provided. Please specify a question."

    if '?' != question[-1:]:
        question += '?'

    qa_result = qa_guide(question, qa_context)
    return qa_result['answer']
    

@app.route('/generate', methods=['GET'])
def generate_text():
    if 'prefix' in request.args:
        prefix = request.args['prefix']
    else:
        return "Error: No prefix provided. Please specify a prefix."

    gen_result = text_generator(prefix, do_sample=True, min_length=75, max_length=175, no_repeat_ngram_size=2, early_stopping=False, top_k=50, temperature=0.7)[0]
    return gen_result['generated_text']


app.run()