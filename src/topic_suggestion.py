import streamlit as st
import time
import nltk
import string
from heapq import nlargest
import spacy
from spacy import displacy
from src.video_analyzer import summarize
  
import requests

HUGGING_FACE_TOKEN="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"

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
# API_URL = "https://api-inference.huggingface.co/models/tuner007/pegasus_summarizer"

API_TOPIC_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
headers = {"Authorization": f"Bearer {HUGGING_FACE_TOKEN}"}

def topic_query(payload):
	topic_response = requests.post(API_TOPIC_URL, headers= headers, json=payload)
	return topic_response.json()

def query(payload, api= API_URL):
	response = requests.post(api, headers=headers, json=payload)
	return response.json()


    
def summarize_option(text):
    
    if len(summarize(text))>1500:
      text = summarize(text)
    try:
        print('\ntrying with Bart summarizer')
        output = query({
            "inputs":text,
        })
        if type(output) == dict and 'error' in output.keys() :
          print('\nPegasus Summarizer')
          output = query({
              "inputs": text[:10000],
          },api="https://api-inference.huggingface.co/models/tuner007/pegasus_summarizer")
          print(output,type(output))
          
          if type(output) == dict and 'error' in output.keys() :
              print("\nsummaring my function")
              return summarize(text)
    except Exception as e:
        print(e)
        print('Normal summary')
        return summarize(text)
    return output[0]["summary_text"]    


def topic_suggest_option(text):
    
    if st.session_state.text_summ is None:
        text = summarize_option(text)
        st.session_state.text_summ =  text     
     
    text = st.session_state.text_summ
    result = topic_query({
        "inputs": text,
        "parameters": {
            "candidate_labels": ['Business & Market & Finance & Economics', 'Health',  'Education & Science',
                                 'Politics & Government','Travel & Tourism','Gadgets & Technology',
                                 'Scientific Discovery & Space',"Fashion & Social Media, Law & Crime" ,
                                 'Entertainment',"Environment,Development & Socialization"
                                 ]},
        
    })
    return result["labels"][:5]


if 'topics' not in st.session_state:
    st.session_state.topics = None


if 'nlp' not in st.session_state:
    # load_spacy_depend()
    print('Creating nlp in session_state and loading it..............')
    nlp = spacy.load("en_core_web_lg")
    # nlp.add_pipe('spacytextblob')
    st.session_state.nlp = nlp
    print("NLP loaded from SpaCy in the transcription video info")
