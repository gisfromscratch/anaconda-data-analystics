import io
import spacy
from transformers import GPTNeoForCausalLM, GPT2Tokenizer
import uuid

class TextGenerator(object):

    def prepare_generation(self):
        print('Loading model...')
        self._model = GPTNeoForCausalLM.from_pretrained('EleutherAI/gpt-neo-125M', cache_dir='D:/Data/ML/cache')
        print('Loading model done.')
        print('Loading tokenizer...')
        self._tokenizer = GPT2Tokenizer.from_pretrained('EleutherAI/gpt-neo-125M', cache_dir='D:/Data/ML/cache')
        print('Loading tokenizer done.')

    def prepare_parsing(self):
        self._nlp = spacy.load('en_core_web_sm')

    def generate(self, input_text):
        print('Tokenize text...')
        input_ids = self._tokenizer(input_text, return_tensors='pt').input_ids
        print('Tokenize text done.')

        print('Generate text...')
        gen_tokens = self._model.generate(input_ids, do_sample=True, temperature=0.9, max_length=100)
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

    def pop_last_sentence(self):
        text = self.to_text(self._sentences[-1:])
        self._sentences = self._sentences[:-1]
        return text

    def pop_last_sentences(self):
        if len(self._sentences) < 3:
            text = self.to_text(self._sentences[1:])
            self._sentences = self._sentences[:1]
            return text

        text = self.to_text(self._sentences[-2:])
        self._sentences = self._sentences[:-2]
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
    with io.open('input.txt', 'r', encoding='utf8') as in_stream:
        input_text = ' '.join(in_stream.read().split())

    max_sentences = 50
    builder = TextBuilder(max_sentences=50)
    generator = TextGenerator()
    generator.prepare_generation()
    generator.prepare_parsing()

    input_sentences = generator.validate(input_text)
    sentences_count = len(input_sentences)
    paragraph_count = int(max_sentences/sentences_count)
    if paragraph_count < 1:
        paragraph_count = 1
    
    print('sentences: ', sentences_count)
    print('paragraphs: ', paragraph_count)

    generate = True
    for sentence_index in range(sentences_count):
        if not generate:
            break

        input_text = str(input_sentences[sentence_index])
        for paragraph_index in range(paragraph_count):
            if not generate:
                break
            
            generated_text = generator.generate(input_text)
            #generated_text = input_text
            '''
            print('### Generated ###')
            print(generated_text)
            print('### End of Generated ###')
            '''
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
                    '''
                    print('### Input ###')
                    print(input_text)
                    print('### End of Input ###')
                else:
                    generate = False

    print()
    print(builder.to_text())
    print()

    new_uuid = str(uuid.uuid4()).replace('-', '')
    out_file = 'generated_{0}.txt'.format(new_uuid)
    with io.open(out_file, 'w', encoding='utf8') as out_stream:
        out_stream.write(builder.to_ptext())