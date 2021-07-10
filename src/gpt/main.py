from transformers import GPTNeoForCausalLM, GPT2Tokenizer



if __name__ == "__main__":
    model = GPTNeoForCausalLM.from_pretrained("EleutherAI/gpt-neo-1.3B")
    tokenizer = GPT2Tokenizer.from_pretrained("EleutherAI/gpt-neo-1.3B")

    input_text = "A geographic information system (GIS) is a system that creates, manages, analyzes, and maps all types of data. GIS connects data to a map, integrating location data"
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids

    gen_tokens = model.generate(input_ids, do_sample=True, temperature=0.9, max_length=100)
    gen_text = tokenizer.batch_decode(gen_tokens)[0]
    print(gen_text)