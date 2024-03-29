import flask
from flask import request, jsonify
import glob
import os

os.environ['TRANSFORMERS_CACHE'] = '/mnt/data/ml'

import spacy
import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer, pipeline

"""
files_dir = os.environ['QA_CONTEXT_PATH']

for txt_file in glob.glob('{0}/*.txt'.format(files_dir)):
    with open(txt_file, 'r') as in_stream:
        qa_context = in_stream.read()
        qa_context += '\n'
"""

app = flask.Flask('GPT-Generator')
app.config['DEBUG'] = True

qa_guide = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')

text_generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')
#text_generator = pipeline('text-generation', model='EleutherAI/gpt-neo-125M')

text_summarizer = pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')


# Rewriting/Paraphrasing
torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
tokenizer = PegasusTokenizer.from_pretrained('tuner007/pegasus_paraphrase')
model = PegasusForConditionalGeneration.from_pretrained('tuner007/pegasus_paraphrase').to(torch_device)

# NLP model
nlp = spacy.load('en_core_web_sm')



@app.route('/answer', methods=['GET'])
def answer_question():
    if 'question' in request.args:
        question = request.args['question']
    else:
        return "Error: No question provided. Please specify a question."

    if len(question) < 7:
        return "Error: Question is too short. Please use a longer question."

    if '?' != question[-1:]:
        question += '?'

    qa_result = qa_guide(question, qa_context)
    return qa_result['answer']
    

@app.route('/generate', methods=['GET', 'POST'])
def generate_text():
    if 'prefix' in request.args:
        prefix = request.args['prefix']
    elif 'prefix' in request.form:
        prefix = request.form['prefix']
    else:
        return "Error: No prefix provided. Please specify a prefix."

    if len(prefix) < 10:
        return "Error: Prefix is too short. Please use a longer prefix."

    #min_length = 75
    #max_length = 175
    min_length = int(0.5 * len(prefix))
    max_length = int(2.5 * min_length)
    if 'min' in request.args:
        min_length = int(request.args['min'])
    elif 'min' in request.form:
        min_length = int(request.form['min'])
    if 'max' in request.args:
        max_length = int(request.args['max'])
    elif 'max' in request.form:
        max_length = int(request.form['max'])
    
    gen_result = text_generator(prefix, do_sample=True, min_length=min_length, max_length=max_length, no_repeat_ngram_size=2, early_stopping=False, top_k=50, temperature=0.9)[0]
    return gen_result['generated_text']

@app.route('/rewrite', methods=['GET', 'POST'])
def rewrite_text():
    if 'text' in request.args:
        text = request.args['text']
    elif 'text' in request.form:
        text = request.form['text']
    else:
        return "Error: No text provided. Please specify a text."

    if len(text) < 30:
        return "Error: Text is too short. Please use a longer text."

    parsed_paragraph = nlp(text)
    paraphrased_samples = []
    num_beams = 10
    max_length = 60
    for sentence in parsed_paragraph.sents:
        batch = tokenizer([str(sentence)], truncation=True, padding='longest', max_length=max_length, return_tensors='pt').to(torch_device)
        translated = model.generate(**batch, max_length=max_length, num_beams=num_beams, num_return_sequences=1, temperature=1.5)
        tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
        paraphrased_samples.extend(tgt_text)
    return ' '.join(paraphrased_samples)

@app.route('/summarize', methods=['GET'])
def summarize_text():
    if 'text' in request.args:
        text = request.args['text']
    else:
        return "Error: No text provided. Please specify a text."

    if len(text) < 30:
        return "Error: Text is too short. Please use a longer text."

    sum_result = text_summarizer(text, do_sample=True, min_length=30, max_length=130, no_repeat_ngram_size=2, early_stopping=False, top_k=50, temperature=0.7)[0]
    return sum_result['summary_text']



app.run()