import io
import json
import newspaper
from newspaper import Article
import nltk
import random
import spacy
from transformers import GPTNeoForCausalLM, GPT2Tokenizer
import urllib.request
import uuid

class TextGenerator(object):

    def prepare_generation(self):
        print('Loading model...')
        self._model = GPTNeoForCausalLM.from_pretrained('EleutherAI/gpt-neo-125M', cache_dir='D:/Data/ML/cache')
        #self._model = GPT2LMHeadModel.from_pretrained.from_pretrained('openai-gpt', cache_dir='D:/Data/ML/cache')
        print('Loading model done.')
        print('Loading tokenizer...')
        self._tokenizer = GPT2Tokenizer.from_pretrained('EleutherAI/gpt-neo-125M', cache_dir='D:/Data/ML/cache')
        print('Loading tokenizer done.')

    def prepare_parsing(self):
        self._nlp = spacy.load('en_core_web_sm')
        nltk.download('punkt')

    def parse_articles(self, url):
        web_newspaper = newspaper.build(url, memoize_articles=False)
        articles = []
        for article in web_newspaper.articles:
            try:
                article.download()
                article.parse()
                article.nlp()
                articles.append(article)
            except:
                pass
            
        return articles

    def query_articles(self, query):
        query_params = {
            'query': query,
            'mode': 'artlist',
            'timespan': '1day',
            'sort': 'datedesc',
            'format': 'json'
        }
        query_string = urllib.parse.urlencode(query_params)
        gdelt_request = urllib.request.Request('https://api.gdeltproject.org/api/v2/doc/doc?{0}'.format(query_string),
                                headers={'content-type': 'application/json'})
        web_response = json.loads(urllib.request.urlopen(gdelt_request).read().decode('utf8'))
        gdelt_articles = []
        article_titles = {}
        if 'articles' in web_response:
            for article_entry in web_response['articles']:
                if ('title' in article_entry
                    and 'url' in article_entry):
                    web_articles = self.parse_articles(article_entry['url'])
                    gdelt_articles.extend(web_articles)
                    # Just add the unparsed one
                    '''
                    if not article_entry['title'] in article_titles:
                        gdelt_articles.append(article_entry)
                        article_titles[article_entry['title']] = article_entry
                    '''

        return gdelt_articles               

    def generate(self, input_text):
        print('Tokenize text...')
        max_text_length = 1024
        if max_text_length < len(input_text):
            input_text = input_text[:max_text_length]
        input_ids = self._tokenizer(input_text, return_tensors='pt').input_ids
        print('Tokenize text done.')

        print('Generate text...')
        input_length = input_ids.shape[1]
        if 1.25*input_length < 100:
            max_length = 100
        else:
            max_length = random.randint(int(1.25*input_length), int(1.5*input_length))
        gen_tokens = self._model.generate(input_ids, do_sample=True, temperature=0.9, max_length=max_length)
        print('Generate text done.')
        print('Decode text...')
        gen_text = self._tokenizer.batch_decode(gen_tokens)[0]
        print('Decode text done.')
        if -1 != gen_text.find('<|endoftext|>'):
            gen_text = gen_text.split('<|endoftext|>', 1)[0]
        return ' '.join(gen_text.split())

    def validate(self, text):
        text_doc = self._nlp(text)
        sentences = list(text_doc.sents)
        if 0 < len(sentences):
            return sentences
        else:
            return None



class TextBuilder(object):

    def __init__(self, max_sentences=50):
        self._sentences = []
        self._max_sentences = max_sentences
    
    def append_sentence(self, sentence):
        if len(self._sentences) < self._max_sentences:
            self._sentences.append(sentence)
            return True
        else:
            return False

    def append_sentences(self, sentences):
        for sentence in sentences:
            if not self.append_sentence(sentence):
                return False

        return True

    def get_last_sentence(self):
        if len(self._sentences) < 1:
            return self.to_text()

        return self.to_text(self._sentences[-1:])
    
    def pop_last_sentence(self):
        text = self.to_text(self._sentences[-1:])
        self._sentences = self._sentences[:-1]
        return text

    def pop_last_sentences(self):
        if len(self._sentences) < 4:
            return self.pop_last_sentence()

        text = self.to_text(self._sentences[-3:])
        self._sentences = self._sentences[:-3]
        return text

    def pop_sentences(self):
        text = self.to_text()
        self._sentences = []
        return text

    def to_text(self, sentences=None):
        if None is sentences:
            sentences = self._sentences
        return ' '.join([str(sentence) for sentence in sentences])

    def to_ptext(self, sentences=None):
        if None is sentences:
            sentences = self._sentences
        return '\n'.join([str(sentence) for sentence in sentences])



if __name__ == '__main__':
    #input_text = 'A geographic information system (GIS) is a system that creates, manages, analyzes, and maps all types of data. GIS connects data to a map, integrating location data and make the world a better place. Thats is our promise.'
    #input_text = input('Input text:')
    input_lines = []

    '''
    with io.open('input.txt', 'r', encoding='utf8') as in_stream:
        input_lines = [' '.join(line.split()) for line in in_stream.readlines()]
        #input_text = ' '.join(in_stream.read().split())
    '''

    max_sentences = 10
    generator = TextGenerator()
    generator.prepare_generation()
    generator.prepare_parsing()

    query = '"location intelligence" AND sourcelang:eng AND repeat3:"location"'
    #query = '"Germany" AND sourcelang:eng AND repeat3:"location"'
    gdelt_articles = generator.query_articles(query)
    article_count = len(gdelt_articles)
    
    print('articles: ', article_count)

    new_uuid = str(uuid.uuid4()).replace('-', '')
    out_file = 'generated_{0}.txt'.format(new_uuid)
    for article_index in range(article_count):
        article = gdelt_articles[article_index]
        input_text = article.title
        if len(input_text) < 10:
            print('Text too short!')
            continue

        with io.open(out_file, 'a', encoding='utf8') as out_stream:
            out_stream.write(article.title)
            out_stream.write('\n')
            out_stream.write(article.url)
            out_stream.write('\n')
            out_stream.write(article.summary)
            out_stream.write('\n\n')

        generate = True
        builder = TextBuilder(max_sentences)
        while generate:
            generated_text = generator.generate(input_text)
            #generated_text = input_text
            
            print('### Generated ###')
            print(generated_text)
            print('### End of Generated ###')
            
            sentences = generator.validate(generated_text)
            if None is sentences:
                print('Sentences could not be generated!')
                generate = False        
            else:
                if builder.append_sentences(sentences):
                    input_text = builder.pop_last_sentences()
                    '''
                    print('### Abstract ###')
                    print(builder.to_text())
                    print('### End of Abstract ###')
                    print('### Input ###')
                    print(last_text)
                    print('### End of Input ###')
                    '''
                else:
                    generate = False

        print()
        print(builder.to_text())
        print()
    
        with io.open(out_file, 'a', encoding='utf8') as out_stream:
            out_stream.write(builder.to_ptext())
            out_stream.write('\n### End of Article ###\n\n')
