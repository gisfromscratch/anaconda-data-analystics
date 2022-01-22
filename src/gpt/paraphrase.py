# conda install sentencepiece
import spacy
import sys
import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer



model_name = 'tuner007/pegasus_paraphrase'
torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)

def get_response(input_text, num_return_sequences, num_beams):
    max_length = 60
    batch = tokenizer([input_text], truncation=True, padding='longest', max_length=max_length, return_tensors='pt').to(torch_device)
    translated = model.generate(**batch, max_length=max_length, num_beams=num_beams, num_return_sequences=num_return_sequences, temperature=1.5)
    tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
    return tgt_text

def paraphrase_paragraph(input_paragraph):
    min_text_length = 10
    num_beams = 10
    nlp = spacy.load('en_core_web_sm')
    parsed_paragraph = nlp(input_paragraph)
    paraphrased_samples = []
    for sentence in parsed_paragraph.sents:
        # Reduce all \n\t\s to simple whitespace
        stripped_sentence = ' '.join(str(sentence).split())
        if min_text_length <= len(stripped_sentence):
            paraphrased_sample = get_response(stripped_sentence, num_return_sequences=1, num_beams=num_beams)
            paraphrased_samples.extend(paraphrased_sample)
    
    return ' '.join(paraphrased_samples)



if __name__ == '__main__':
    if len(sys.argv) < 2:
        paragraph = "Mapping the geospatial patterns of broadcasted news allows a geospatial analyst to gain insights into common and unusual geospatial patterns. We decided using one of the most comprehensive news collection named “Global Database Events of Tone and Language” (GDELT) as the ground truth."
    else:
        with open(sys.argv[1], mode='r', encoding='utf-8') as in_stream:
            paragraph = in_stream.read()
    
    paraphrased_text = paraphrase_paragraph(paragraph)
    print(paraphrased_text)