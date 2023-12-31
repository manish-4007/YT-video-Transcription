import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.streaming_write import write
from streamlit_extras.stoggle import stoggle
from streamlit_extras.grid import grid
from pytube import YouTube
import time

import nltk,spacy
from spacy import displacy

from src.youtube_audio import text_translator
from src.video_analyzer import summarize
from src.topic_suggestion import summarize_option,topic_suggest_option
from transformers import pipeline


languages_coded={"": "",
                  "Hindi" :	"hi-IN" ,
                  "English" : "en-IN" ,
                  "Bengali" : "bn-IN" ,
                  "Gujarati" : "gu-IN" ,
                  "Kannada" : "kn-IN" ,
                  "Malayalam" : "ml-IN" ,
                  "Marathi" : "mr-IN" ,
                  "Nepali" : "ne-NP" ,
                  "Punjabi": "pa-Guru-IN",
                  "Tamil" :	"ta-IN" ,
                  "Telugu" : "te-IN" ,
                  "Urdu" : "ur-IN",
                  "Other Language":""
                 }

lang_encode_trans = {
                    "Original": "",
                    "Afrikaans" :	"af",
                    "Albanian" :	"sq",
                    "Amharic" :	"am",
                    "Arabic" :	"ar",
                    "Armenian" :	"hy",
                    "Assamese" :	"as",
                    "Aymara" :	"ay",
                    "Azerbaijani" :	"az",
                    "Bambara" :	"bm",
                    "Basque" :	"eu",
                    "Belarusian" :	"be",
                    "Bengali" :	"bn",
                    "Bhojpuri" :	"bho",
                    "Bosnian" :	"bs",
                    "Bulgarian" :	"bg",
                    "Catalan" :	"ca",
                    "Cebuano" :	"ceb",
                    "Chinese(Simplified)" 	: "zh-CN",
                    "Chinese(Traditional)"  :	"zh-TW",
                    "Corsican" :	"co",
                    "Croatian" :	"hr",
                    "Czech" :	"cs",
                    "Danish" :	"da",
                    "Dhivehi" :	"dv",
                    "Dogri" :	"doi",
                    "Dutch" :	"nl",
                    "English" :	"en",
                    "Esperanto" :	"eo",
                    "Estonian" :	"et",
                    "Ewe" :	"ee",
                    "Filipino(Tagalog)	" : "fil",
                    "Finnish" :	"fi",
                    "French" :	"fr",
                    "Frisian" :	"fy",
                    "Galician" :	"gl",
                    "Georgian" :	"ka",
                    "German" :	"de",
                    "Greek" :	"el",
                    "Guarani" :	"gn",
                    "Gujarati" :	"gu",
                    "Hausa" :	"ha",
                    "Hawaiian" :	"haw",
                    "Hebrew" :	 "iw",
                    "Hindi" :	"hi",
                    "Hmong" :	"hmn",
                    "Hungarian" :	"hu",
                    "Icelandic" :	"is",
                    "Igbo" :	"ig",
                    "Ilocano" :	"ilo",
                    "Indonesian" :	"id",
                    "Irish" :	"ga",
                    "Italian" :	"it",
                    "Japanese" :	"ja",
                    "Javanese" :	"jv",
                    "Kannada" :	"kn",
                    "Kazakh" :	"kk",
                    "Khmer" :	"km",
                    "Kinyarwanda" :	"rw",
                    "Konkani" :	"gom",
                    "Korean" :	"ko",
                    "Krio" :	"kri",
                    "Kurdish" :	"ku",
                    "Kurdish(Sorani)	" : "ckb",
                    "Kyrgyz" :	"ky",
                    "Lao" :	"lo",
                    "Latin" :	"la",
                    "Latvian" :	"lv",
                    "Lingala" :	"ln",
                    "Lithuanian" :	"lt",
                    "Luganda" :	"lg",
                    "Luxembourgish" :	"lb",
                    "Macedonian" :	"mk",
                    "Maithili" :	"mai",
                    "Malagasy" :	"mg",
                    "Malay" :	"ms",
                    "Malayalam" :	"ml",
                    "Maltese" :	"mt",
                    "Maori" :	"mi",
                    "Marathi" :	"mr",
                    "Meiteilon(Manipuri) " : "mni-Mtei",
                    "Mizo" :	"lus",
                    "Mongolian" :	"mn",
                    "Myanmar(Burmese)	" : "my",
                    "Nepali" :	"ne",
                    "Norwegian" :	"no",
                    "Nyanja(Chichewa) " :	"ny",
                    "Odia(Oriya) " :	"or",
                    "Oromo" :	"om",
                    "Pashto" :	"ps",
                    "Persian" :	"fa",
                    "Polish" :	"pl",
                    "Portuguese(Portugal, Brazil) " :	"pt",
                    "Punjabi" :	"pa",
                    "Quechua" :	"qu",
                    "Romanian" :	"ro",
                    "Russian" :	"ru",
                    "Samoan" :	"sm",
                    "Sanskrit" :	"sa",
                    "ScotsGaelic" : 	"gd",
                    "Sepedi" :	"nso",
                    "Serbian" :	"sr",
                    "Sesotho" :	"st",
                    "Shona" :	"sn",
                    "Sindhi" :	"sd",
                    "Sinhala (Sinhalese)" :	"si",
                    "Slovak" :	"sk",
                    "Slovenian" :	"sl",
                    "Somali" :	"so",
                    "Spanish" :	"es",
                    "Sundanese" :	"su",
                    "Swahili" :	"sw",
                    "Swedish" :	"sv",
                    "Tagalog (Filipino) ":	"tl",
                    "Tajik" :	"tg",
                    "Tamil" :	"ta",
                    "Tatar" :	"tt",
                    "Telugu" :	"te",
                    "Thai" :	"th",
                    "Tigrinya" :	"ti",
                    "Tsonga" :	"ts",
                    "Turkish" :	"tr",
                    "Turkmen" :	"tk",
                    "Twi (Akan)" :	"ak",
                    "Ukrainian" :	"uk",
                    "Urdu" :	"ur",
                    "Uyghur" :	"ug",
                    "Uzbek" :	"uz",
                    "Vietnamese" :	"vi",
                    "Welsh" :	"cy",
                    "Xhosa" :	"xh",
                    "Yiddish" :	"yi",
                    "Yoruba" :	"yo",
                    "Zulu" :	"zu",
}

# @st.cache_resource
# def check_nlp():
#     if 'nlp' not in st.session_state: 
            
#         nltk.download('stopwords')
#         nltk.download('punkt')
#         print('Creating nlp in session_state and loading it..............')
#         nlp = spacy.load("en_core_web_lg")
#         nlp.add_pipe('spacytextblob') 
#         st.session_state.nlp = nlp
#         print("NLP loaded from SpaCy in the transcription video info")

# check_nlp()
def show_text():
    for word in a.split():
        yield word + " "
        time.sleep(0.05)


def show_hompage(key_1 ="reload",key_2 = 'Home'):
        
    cols = st.columns(5)
    with cols[0]:
        if st.button('🔄️ Reload', key= key_1):
            st.session_state.clear()
            st.experimental_rerun()

    with cols[4]:
        if st.button('🏠 Home Page', key= key_2):
            st.session_state.clear()
            switch_page('Home')
        
show_hompage()

try:

    yt_url = st.session_state.video
    yt = YouTube (yt_url)


    # if 'topic_modeller' not in st.session_state:
    #     print("Loading topic modeller into session_state for topic suggestion...")
        
    #     topic_classifier = load_topic_transfomers()
    #     st.session_state.topic_modeller = topic_classifier
        
    #     st.success('Topic Modeller Transformer Loaded.')

    if st.button("home"):
        st.session_state.clear()
        switch_page('Transcripter')
    st.header ("Info about the video : ", yt.title)

    # if st.button("show text"):
    # st.write(f"Translated {st.session_state.dest_language} Text :  \n")
    
    st.subheader(f"Generate Description from the Contnt of the video :  \n")

    
    whole_text = st.session_state.subtiles_eng 
    a = st.session_state.text_summ  
               
    if st.session_state.summary_show_done is True:
        st.write(a)
            
    else:         
        write(show_text)
        st.session_state.summary_show_done=True

    if st.session_state.topics == True:
        if st.checkbox('Suggested Topics'):
            st.subheader('Topic suggestions related to the Video Content ')
            topics = st.session_state.video_info['keywords']
            top_cols = st.columns(2)
            for i,topic in enumerate(topics):
                with top_cols[i%2]:
                    st.markdown(topic)
        

    tabs = st.tabs(['Description','Name Entity Recognition - (NER)'])
    with tabs[0]:
        stoggle(f'Source Subtile Text ( in {st.session_state.src_language} )', st.session_state.transcribed_src_text)
        stoggle(f'Destination Subtile Text ( in {st.session_state.dest_language} )', st.session_state.transcribed_text)
        stoggle(
            f"Custom Generated Summarized Description in English : ",
            f"""🥷 {st.session_state.text_summ }""",
        )



    with tabs[1]:
        tab1,tab2 = st.tabs(["Summarized Subtile Text","Whole Text"])
        nlp = st.session_state.nlp
        whole_text = st.session_state.subtiles_eng
        
        with tab1:
            summ_doc = nlp(st.session_state.text_summ)
            st.write("\nNER on Summarized Transcribe Text: \n")
            st.markdown(displacy.render(summ_doc, style="ent",jupyter=False), unsafe_allow_html=True)

        with tab2:
            doc = nlp(whole_text)
            st.write("NER on whole Subtile Text from video : \n")
            st.markdown(displacy.render(doc, style="ent",jupyter=False), unsafe_allow_html=True)

    
    d = st.session_state.video_info 
    
    if  yt.description is None:
      d['Description']= st.session_state.text_summ 



    if st.checkbox('Show video'):
        
        st.video(yt_url )
        st.write(yt.title,f"( in {st.session_state.dest_language})")

    st.subheader("Translate Subtitle")
    my_grid = grid( [2, 2], vertical_align="bottom")
    subtitle_lang = my_grid.selectbox("Enter the language which you want to convert ", lang_encode_trans.keys())
    translate_subtitle = my_grid.button("translate subtitle", use_container_width=True)

    if translate_subtitle:
        st.markdown('\nTranslated Subtitle with timestamps :')
        for key, value in st.session_state.timestamps.items():
            if key in st.session_state.dest_text_dict:
                if subtitle_lang == "Original":
                    st.write(f" {key} - [ {value[0]} - {value[1]} ]   :   {st.session_state.transcribed_src_dict[key]}")
                else:
                    st.write(f" {key} - [ {value[0]} - {value[1]} ]   :   {text_translator(st.session_state.transcribed_src_dict[key], subtitle_lang)[1]}")

    if st.button("back to Transcription Page"):
        switch_page('Transcripter')

except Exception as e:
    st.subheader("Some Error Occured😢, please select the video again😊")
    print("Error:", e)
    # if st.button("home"):
    #     st.session_state.clear()
    #     switch_page('Transcripter')

show_hompage('trans_videoinf_reload_key','trans_videoinf_hm_key')