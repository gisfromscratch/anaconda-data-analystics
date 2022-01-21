# conda install sentencepiece
import spacy
import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer


model_name = 'tuner007/pegasus_paraphrase'
torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name, cache_dir='D:/Data/ML/cache').to(torch_device)

def get_response(input_text, num_return_sequences, num_beams):
    max_length = 60
    batch = tokenizer([input_text], truncation=True, padding='longest', max_length=max_length, return_tensors='pt').to(torch_device)
    translated = model.generate(**batch, max_length=max_length, num_beams=num_beams, num_return_sequences=num_return_sequences, temperature=1.5)
    tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
    return tgt_text

def paraphrase_paragraph(input_paragraph):
    num_beams = 10
    nlp = spacy.load('en_core_web_sm')
    parsed_paragraph = nlp(input_paragraph)
    paraphrased_samples = []
    for sentence in parsed_paragraph.sents:
        paraphrased_sample = get_response(str(sentence), num_return_sequences=1, num_beams=num_beams)
        paraphrased_samples.extend(paraphrased_sample)
    
    return ' '.join(paraphrased_samples)



if __name__ == '__main__':
    paragraph = "Mapping the geospatial patterns of broadcasted news allows a geospatial analyst to gain insights into common and unusual geospatial patterns. We decided using one of the most comprehensive news collection named “Global Database Events of Tone and Language” (GDELT) as the ground truth."
    paraphrased_text = paraphrase_paragraph(paragraph)
    print(paraphrased_text)