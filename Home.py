import streamlit as st 
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.streaming_write import write
from streamlit_extras.grid import grid
from streamlit_extras.colored_header import colored_header
import os,time,subprocess,sys

@st.cache_resource
def load_spacy():
    print("Loading spacy dependencies.....")
    
    virtual_env_path = "./venv"
    # activate_script = os.path.join(virtual_env_path, "Scripts", "activate")
    # subprocess.run([activate_script], shell=True, text=True)
    os.environ['PATH'] = f"{virtual_env_path}\\Scripts;{os.environ['PATH']}"
    print(subprocess.run("pip install spacy".split(),check=True))
    print(subprocess.run([sys.executable, "-m", "spacy", "download", 'en_core_web_sm'], text=True))

    print("Loaded Sucessfully")

@st.cache_resource
def intall_ffmpeg():
   
    try:
        print('Installing ffmpeg and ffprobe dependencies ............')
        # # Run "apt install ffmpeg and ffprobe "
        
        # print(subprocess.run([sys.executable, "pip", "install", "pydub"], text=True))
        print(subprocess.run(["sudo", "apt", "install", "ffmpeg"], capture_output=True, text=True))
        print("ffmpeg and ffprobe installed successfully.")
        
        virtual_env_path = "./venv"
        lib_path = "/usr/bin/ffmpeg"
        # lib_path = "/usr/local/bin/ffmpeg"
        # lib_path = "/opt/ffmpeg/bin/ffmpeg"

        import pydub,ffmpeg 
        ffmpeg_binary = f"{lib_path}"
        ffprobe_binary = "/usr/bin/ffmpeg"
        # pydub.AudioSegment.ffmpeg = ffmpeg_binary
        ffmpeg.input.ffmpeg = ffmpeg_binary
        # pydub.AudioSegment.ffprobe = ffprobe_binary
        ffmpeg.input.ffprobe = ffprobe_binary

        print("ffmpeg and ffprobe setup done completely.")
    except Exception as e:
       print('Error :', e)
       print('Installing Unsucessful.')


st.title('Welcome To The Homepage ')
st.title("\n")

intro = "This Web App is an AI tool which has a lot of features and can perform many functions on a particular 'Youtube Video', Youtube Shots or any  Video like Transcription and Scrolling Subtitle Embeddings.\n "
app_description= """

    - It generates the **subtitles** for the video by analyzing the speech of the Video with the help of speech Recognition
    - It generated the subtiles along with timestamps and also can translate them into any languages\n
    - It can give the custom generated Description by summarizing the word uttered in the video along with we can perform "Name Entity Recognition (NER)" into the Subtitles and Description \n
    - gives the sentiment of the video using Sentiment Analysis based on the user comments in the video. And gives the full insights of the video along with the Video Analytics based on comments and shows the comment based on the sentiment\n
    - Another most important feature of this web app that it help to embedd the subtitles into the video which is a scrolling subtitles on he video
    - Suggest the keyword or the topic for the video analyzing the video speech with the help of Topic Modelling (under processing. . . . . . . . .  😴🤕 Stay Tuned for more. 🤞😊)
"""

def show_text(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.08)
    
    time.sleep(0.1)

colored_header(
    label="Youtube Video Analyzer ",
    description=" ",
    color_name="blue-green-70",
)
if 'app_desc' not in st.session_state:

    write(show_text(intro))
    time.sleep(0.4)
    write(show_text("\nThis is a simple web app to analyze youtube videos and get insights about the video like:\n"))

    st.session_state.app_desc = True


else:
    st.write(intro)
    st.write("\nThis is a simple web app to analyze youtube videos and get insights about the video like:\n")


st.markdown(f"{app_description}",unsafe_allow_html=True)

colored_header(
    label="Apps",
    description=" ",
    color_name="blue-green-70",
)

def show_apps():
    
    cols = st.columns(2)
    with cols[0]:
        if st.button('Video Transcription',use_container_width=True,key='trans_btn_hm'):
            switch_page('Transcripter')
    with cols[1]:
        if st.button('Subtitle Editor',use_container_width=True,key='sub_btn_hm'):
            switch_page('Subtitle_Merger')



if 'more_app' not in st.session_state:
    st.session_state.more_app = False 

st.session_state.more_app = st.checkbox('Click here to know more about our Apps')
if st.session_state.more_app:
    tab1,tab2 = st.tabs(['📈Transcription', 'Subtitle Merger'])
    with tab1:
        st.subheader('Youtube Video Transcription')
        st.write('Youtube Video Transcriptor is best to extract subtiles from content of the video for all types of video Language and then returns the subtiles in any Languages along with the timestamps. It can also suggest Description and sentiment of the particular video and by analysing the video speech.\n')

        app_1 = """ 
        With this tool, one can play around with the script of the video with the help of NLP like Sentiment Analysis, NER and Topic Modelling.\n
            - Extract Sentiment by scanning Comment and the Video using Sentiment Analyis 
            - Suggest best Description, Topics or Keywords that fit for the video usning NLP
            - Download or play online any Youtube Videos within this app
            - Name Entitiy Recognition on entire Subtitle and the decription\n
            """
        st.write(app_1)
        st.markdown("<br><br>",unsafe_allow_html=True)
       

        my_grid = grid([3,2],vertical_align='center')
        my_grid.markdown('<h3>Click here to use the Transcripter</h3>',unsafe_allow_html=True,)
        trans_btn =  my_grid.button('Video Transcription',use_container_width=True)
        if trans_btn:
            switch_page('Transcripter')


    with tab2:
        st.subheader('Subtitle Editor')
        app_2 = """
        - This tool can convert your Youtube Videos into audio files which you can download or listen to it.\n
        - Easily create Subtiles and embedd them into reel videos or any uploaded videos
        - Add a scrolling Subtiles into the video and highlights the words as the word uttered in the video
        """
        st.markdown(app_2)
        st.markdown("<br>",unsafe_allow_html=True)
       
        my_grid = grid([3,1.5],vertical_align='center')
        my_grid.markdown('<h3>Click here to use the Subtitle Merger</h3>',unsafe_allow_html=True,)
        sub_btn =  my_grid.button('Subtitle Editor',use_container_width=True)
        if sub_btn:
            
            switch_page('Subtitle_Merger')

    
# if not st.session_state.more_app:
else:
    show_apps()


if "dependencies" not in st.session_state:
    st.session_state.dependencies = True 
    try:
        load_spacy()
        # intall_ffmpeg()
    except Exception as e:
        print('Error in Loading :', e)
        pass
    