from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Helsinki-NLP models (supports many languages)
en2xx_model_name = "Helsinki-NLP/opus-mt-en-mul"
xx2en_model_name = "Helsinki-NLP/opus-mt-mul-en"

en2xx_model = AutoModelForSeq2SeqLM.from_pretrained(en2xx_model_name).to(DEVICE)
en2xx_tokenizer = AutoTokenizer.from_pretrained(en2xx_model_name)

xx2en_model = AutoModelForSeq2SeqLM.from_pretrained(xx2en_model_name).to(DEVICE)
xx2en_tokenizer = AutoTokenizer.from_pretrained(xx2en_model_name)

def translate_to_english(text):
    batch = xx2en_tokenizer(text, return_tensors="pt", truncation=True).to(DEVICE)
    output = xx2en_model.generate(**batch)
    return xx2en_tokenizer.decode(output[0], skip_special_tokens=True)

def translate_from_english(text):
    batch = en2xx_tokenizer(text, return_tensors="pt", truncation=True).to(DEVICE)
    output = en2xx_model.generate(**batch)
    return en2xx_tokenizer.decode(output[0], skip_special_tokens=True)
