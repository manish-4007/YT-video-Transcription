from src.youtube_audio import download_audio,get_large_audio_transcription_on_silence,get_timestamp,text_translator
import os, time,tempfile,requests
from pytube import YouTube
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.colored_header import colored_header
from streamlit_extras.streaming_write import write
from streamlit_extras.stoggle import stoggle
from streamlit_extras.grid import grid
from src.video_analyzer import video_ratings,comment_analyzer,detect_sentiment

import googleapiclient.discovery
import googleapiclient.errors
import spacy

dev_key = os.environ["DEVELOPER_KEY"]

def youtube_api_setup(dev_key):
    # youtube api ver3 setup

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = dev_key

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)
    return youtube
youtube = youtube_api_setup(dev_key)


start_entire= time.time()
directory = tempfile.gettempdir() 

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
                    "Original" : "",
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

def get_first_link():
    # Fetch the HTML content of YouTube homepage
    homepage_url = "https://www.youtube.com/"
    response = requests.get(homepage_url)
    html_content = response.text

    # Find the first video link in the HTML content
    start_index = html_content.find('/watch?v=')
    end_index = html_content.find('"', start_index)
    video_id = html_content[start_index + len('/watch?v='):end_index]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    return video_url


def downloader_btn(url):
    yt = YouTube(url)
    videos= yt.streams.filter(file_extension='mp4')

    if len(videos)>0:
        vid_down = yt.streams.filter(file_extension='mp4')[0]
    else:
        vid_down = yt.streams.filter(type='video')[0]
    print(vid_down)
    
    print(f"Downloading video - {yt.title}")
    vid_down.download(directory, filename = 'video.mp4')
    
    videofilename = os.path.join(directory, 'video.mp4')
    with open(videofilename, "rb") as file:
        btn = st.download_button(
                label="Download Video",
                data=file,
                file_name=f"{yt.title}.mp4",
                use_container_width=True
            )
    print(f"Downloaded video - {yt.title}")


@st.cache_data
def load_dataFrame(df, filter_col, date_range):
    df = df[df[filter_col]>=date_range[0]]
    df = df[df[filter_col]<=date_range[1]]

    return df

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


colored_header(
    label="Youtube Transcripter",
    description="Transcribe and translate subtiles along with timestamps of video, get the sentiment, analytics and do other NLP tasks",
    color_name="blue-green-70",
)
st.markdown('<br><h3>Enter Youtube Link Here</h3>',unsafe_allow_html=True)
try:

    col1,col2 = st.columns(2)
    with col1:
        yt_url = st.text_input('Youtube', placeholder='Url Link')
        if len(yt_url)==0:
            yt_url = get_first_link()
            st.write(yt_url)      
        st.session_state.video = yt_url 
    with col2:
        search = st.button('search',use_container_width=True)
        transcribe = st.button('Video Transcription',use_container_width=True)
    if 'video' in st.session_state:
        yt_url = st.session_state.video
    yt = YouTube(yt_url)


            
    d = {
        "id": yt.video_id,
        "video_url":yt_url,
        "channel_url":yt.channel_url,
        "title": yt.title,
        "views": yt.views,
        "length":yt.length,
        "publish_date": yt.publish_date,
        "Description": yt.description,
        "keywords": yt.keywords,
    }


    if 'transcribe' not in st.session_state and 'search' not in st.session_state:
        
        st.session_state.transcribe = None
        st.session_state.search = None

    if search:
        st.session_state.clear()
        st.session_state.search = True

    if transcribe:
        st.session_state.clear()
        st.session_state.transcribe = True
        st.session_state.search = False
        st.session_state.video_info = d
        st.session_state.video = d['video_url']

    if st.session_state.search:
        st.session_state.transcribe = False


        v_id =  d["id"]
        description, views,likes,totalComments = video_ratings(v_id)
        d['Description'] = description
        st.session_state.video_info = d

        st.video(yt_url)
        
        st.subheader(f"**{yt.title}**")   
        if st.checkbox('Download options'):
            with st.spinner(f"Downloading video - {yt.title}"):
                downloader_btn(yt_url)
            st.success('Video Downloaded Successfully😎😃 !! Click on the Download Button to Save into local.')
        
        my_grid = grid( [3,1],[4,1], vertical_align="bottom")
        my_grid.subheader(' Channel URL - ')
        my_grid.subheader(' Published at ')

        
        my_grid.markdown(f"{d['channel_url']}")
        my_grid.markdown(f"{d['publish_date'].date()}, ")


        main_col = st.columns(2)
        with main_col[0]:
            st.markdown(f"<br>**{round(likes/views*100, 2)}%** viewers likes the video ",unsafe_allow_html=True)
            st.write(f"**{round(totalComments/views*100, 2)}%** viewers commented on  the video ")

        with main_col[1]:

            col = st.columns(3)
            with col[0]:
                st.subheader(f" Views" )
                st.write(f"{views}")

            with col[1]:
                st.subheader(f"Likes ")
                st.write(f"{likes} ")
            with col[2]:
                st.subheader(f"Comments " )
                st.write(f"{totalComments} " )


        if yt.description is not None:
            st.subheader('Description: ')
            st.write(yt.description[:76])

        elif d['Description'] is not None:
            
            def show_text():
                for word in des.split():
                    yield word + " "
                    time.sleep(0.05)
            des = "\n".join(d['Description'].split('\n')[0:5])
            print("lenght", len(d['Description'].split('\n')))

            st.subheader('Description: ')
            if "main_yt_desc" not in st.session_state:
                write(show_text())
                st.session_state.main_yt_desc = des
            else:
                st.write(des)
            try:
                rest_des = "\n".join(d['Description'].split('\n')[5:])
                stoggle(' . . . . ',rest_des)
            except Exception as e:
                print("description error:",e)
                pass


        print('\ncollecting comments....')
        if 'comment_df' not in  st.session_state:
            with st.spinner('Loading More Info about the video......'):
                print('Creating comments in session_state and store into it..............')
                st.session_state.comment_df = comment_analyzer(v_id)
                nlp = spacy.load("en_core_web_lg")
                nlp.add_pipe('spacytextblob')
                st.session_state.nlp = nlp
                print("NLP loaded from SpaCy")
                
        print("comments colletection Done\n")


        if st.checkbox("more_info"):
            com_df = st.session_state.comment_df
            
            print('Scanning Sentiment....')
            nlp = st.session_state.nlp
            
            if 'sentiment' not in  st.session_state:
                with st.spinner("Scanning Sentiments through comments....."):
                    top_comm_df, video_sentiment = detect_sentiment(com_df.iloc[:,:1000])
                    st.session_state.sentiment = video_sentiment
                    st.session_state.top_comm_df = top_comm_df

                    st.success("Scanning Completed.")

            st.subheader('Overall sentiment of the video : ')
            st.write(st.session_state.sentiment)
            print(f"Get sentiment : {st.session_state.sentiment}")

                
            if st.checkbox("Show Video Analytics"):

                st.subheader('Line chart for comment counts on the video in each day from the day of video publish')
                
            
                df1 = com_df.groupby('published_at').count().reset_index()

                min_date = df1['published_at'].min()
                max_date = df1['published_at'].max()
                date_range = st.slider('Enter the date Range :',min_date,max_date, (min_date,max_date))

                # df1 = df1[df1['published_at']>=date_range[0]]
                # df1 = df1[df1['published_at']<=date_range[1]]
                
                # df2 = df2[df2['published_at']>=date_range[0]]
                # df2 = df2[df2['published_at']<=date_range[1]]
                
                df2 = st.session_state.top_comm_df
                    
                df1 = load_dataFrame(df1,'published_at', date_range)
                df2 = load_dataFrame(df2,'published_at', date_range)


                #Grabbing top comments using filters 
                tabs = st.tabs(['Comment Analytics','Comments'])
                with tabs[0]:
                    st.write(f"Selected Date Range: {date_range[0]} to {date_range[1]}")
                    df1.rename(columns={'published_at': 'Comments (By Date)', 'comments':'Comments count'}, inplace=True)
                    st.line_chart(data = df1,x = 'Comments (By Date)', y = 'Comments count')

                with tabs[1]:
                    rev_sentiment = st.selectbox("Select_ratings", options = ['All','Positive',"Neutral","Negative"])
                    with st.spinner("Loading Comments...."):
                        if rev_sentiment=='All':
                            all_senti_df = df2[['author', 'published_at','comments']].set_index('published_at')
                            st.subheader(f"{rev_sentiment} {len(all_senti_df)} comments ")
                            st.dataframe(all_senti_df)
                        else:
                            com_senti_df = df2[df2['sentiment']==rev_sentiment][['author', 'published_at','comments']].set_index('published_at')
                            st.subheader(f" {rev_sentiment} comments : {len(com_senti_df)}")
                            st.dataframe(com_senti_df)


    if st.session_state.transcribe:
        
        st.session_state.search = False
        st.image(yt.thumbnail_url)
        st.write(f"**{yt.title}**")
        col1,col2  = st.columns(2)
        with col1:
            src_language = st.selectbox("Select video Language", options = languages_coded.keys())
        with col2: 
            dest_language = st.radio("Transcription Language: ", options=['english',"hindi"])
            

        timestamps ={}  
        Transcribed_Text = st.button('Transcribe the video',use_container_width=True)
        st.session_state.video = yt_url
        
        if Transcribed_Text:
            st.subheader(f'**Transcribing video into text from {src_language} to {dest_language.capitalize()}**')
            
            st.session_state.transcription_complete = False
            st.session_state.src_language = src_language
            st.session_state.dest_language = dest_language

            with st.spinner('Transcribing.......'):
                log_container = st.empty()
                with log_container:

                    # time.sleep(5)
                    src_text_dict={}
                    dest_text_dict ={}

                    src_lang = ""
                    download_audio(yt_url)

                    audio_file = os.path.join(directory,'audio.wav')
                    src_lang = languages_coded[src_language]
                    x,src_text_dict, dest_text_dict, sil_ = get_large_audio_transcription_on_silence(audio_file,src_lang,dest_language)

                    st.session_state.transcription_complete = True
                    st.session_state.src_text_dict = src_text_dict
                    st.session_state.dest_text_dict = dest_text_dict

                    st.write(x)
                    # print(x)
                    print('Translating')
                    
                    end = time.time()
                    print("The time of execution of entire transcription program is :",
                        (end-start_entire)/60, "min")

                    
                log_container.empty()
                    
                # a = " ".join(src_text_dict.values())
                # st.write(f"Translated from {src_language} Text :  \n{a}")

                a = " ".join(dest_text_dict.values())
                st.session_state.transcribed_src_text = " ".join(src_text_dict.values())
                st.session_state.transcribed_text = a
                st.session_state.transcribed_src_dict = src_text_dict
                st.session_state.transcribed_dest_dict = dest_text_dict
                st.session_state.show_transcribe_text = None
                
                if src_language=='English':
                    st.session_state.subtiles_eng =st.session_state.transcribed_src_text
                else:
                    subtiles_eng = []
                    for l in dest_text_dict.values():
                        subtiles_eng.append(text_translator(l, lang='en')[1])
                    st.session_state.subtiles_eng = " ".join(subtiles_eng)
                
                st.success('Transcription Done!')
                def show_text():
                    for word in a.split():
                        yield word + " "
                        time.sleep(0.05)

                st.write(f"Translated {dest_language} Text :  \n")
                write(show_text)

                end = time.time()
                print("The time of execution of entire transcription program is :",
                    (end-start_entire)/60, "min")
            
            with st.spinner('Getting TimeStamps.......'):
                log_container = st.empty()
                with log_container:
                    start= time.time() 
                    
                    print("getting the timestamps")

                    timestamps =get_timestamp(audio_file, sil_)
                    st.session_state.timestamps = timestamps
                    # print(timestamps)
                    end = time.time()
                    print("The time of execution of above program is :",
                        (end-start)/60, "min")
                    print("completed")
                    
                log_container = st.empty()
                st.success('Timestamps extraction from the video Done !!')

            st.markdown('\nTranscribed Text with timestamps :')
            for key, value in timestamps.items():
                if key in dest_text_dict:
                    # st.write(f" {key} - [ {value[0]} - {value[1]} ]   :   {src_text_dict[key]}")
                    st.write(f" {key} - [ {value[0]} - {value[1]} ]   :   {st.session_state.transcribed_dest_dict[key]}")
                    

        subtiles = st.button("Click for the detailed infromation about the video and subtitles !")
        if subtiles:
            switch_page("Video_info")
            st.experimental_rerun()

except Exception as e:
    st.subheader("Some Error Occured😢, please select the video again😊")
    print("Error Occured: ",e)
    st.write(e)
    # st.write(st.session_state)

if st.session_state.search or st.session_state.transcribe:
            
    show_hompage('trans_reload_key','trans_hm_key')

