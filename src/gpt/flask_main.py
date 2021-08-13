import flask
from flask import request, jsonify
from transformers import pipeline

app = flask.Flask('GPT-Generator')
app.config['DEBUG'] = True

text_generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.8B')

@app.route('/generate', methods=['GET'])
def generate_text():
    if 'prefix' in request.args:
        prefix = request.args['prefix']
    else:
        return "Error: No prefix provided. Please specify a prefix."

    gen_result = text_generator(prefix, do_sample=True, min_length=75, max_length=175)[0]
    return gen_result['generated_text']


app.run()