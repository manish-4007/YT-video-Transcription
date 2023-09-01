from pytube import YouTube
import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.utils import which
from pydub.silence import split_on_silence
from pydub.silence import detect_nonsilent
import time,tempfile,which
from googletrans import Translator
import streamlit as st

@st.cache_resource
def set_ffmpeg():
    AudioSegment.ffmpeg = "/usr/bin/ffmpeg"
    AudioSegment.converter = which("ffmpeg")

start= time.time()

directory = tempfile.gettempdir() 
r = sr.Recognizer()

languages_coded={"": "",
                  "Hindi" :	"hi-IN" ,
                  "English" :	"en-IN" ,
                  "Bengali" :	"bn-IN" ,
                  "Gujarati" :	"gu-IN" ,
                  "Kannada" :	"kn-IN" ,
                  "Malayalam" :	"ml-IN" ,
                  "Marathi" :	"mr-IN" ,
                  "Nepali" :	"ne-NP" ,
                  "Punjabi": "pa-Guru-IN",
                  "Tamil" :	"ta-IN" ,
                  "Telugu" :	"te-IN" ,
                  "Urdu" :	"ur-IN" 
                 }


def download_audio(url):
    yt = YouTube(url)

    try:
        if yt.streams.filter(only_audio = True,file_extension='mp4') :
            audio = yt.streams.filter(only_audio = True,file_extension='mp4')[0]
        else:
            audio = yt.streams.filter(only_audio = True)[0]
    except Exception as e:
        print("No audio found!!")
    print('Downloading Audio...')  # Downloading Audio...
    st.write('Downloading Audio...') 
    print(audio)
    destination = './audio_files'
    # audio.download(destination, filename = 'audio.mp4')
    audio.download(directory, filename = 'audio.wav')
    print(yt.title + " has been successfully downloaded in .mp4 format.")


def text_translator(text,lang):
    translator = Translator()
    # detect a language
    detection = translator.detect(text)
    print("Language code:", detection.lang)

    translation = translator.translate(text,dest=lang)
    print(f"({translation.dest}) : {translation.text} ")

    return translation.origin,translation.text


# a function to recognize speech in the audio file
# so that we don't repeat ourselves in in other functions
def transcribe_audio(path,lang = ""):
    # use the audio file as the audio source
    start = time.time()
    with sr.AudioFile(path) as source:
        try: 
            audio_listened = r.record(source)
            if len(lang)>0:
                # try converting it to text
                text = r.recognize_google(audio_listened, language=lang)
            else:
                text = r.recognize_google(audio_listened)
        except Exception as e:
            st.write(" Try Transcription for  another video ")
            print(" Try Transcription for  another video ")
            text = ""
            print("Error: ",e)
    
    st.write("Transcribing time of the chunk : ", (time.time()-start)/60, "min\n")
    return text

def get_chunks(sound, sil):
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = sil,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=3*sil,
    )
    return chunks, sil


# a function that splits the audio file into chunks on silence
# and applies speech recognition
def get_large_audio_transcription_on_silence(path,src_lang, dest_lang):
    """Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks"""

    print("reading audio........")
    st.write("reading audio........")
    # open the audio file using pydub
    sound = AudioSegment.from_file(path)  
    # split audio sound where silence is 500 miliseconds or more and get chunks
    
    start= time.time()  
    sil_ = 1000
    print("chunking audio..........")
    st.write("chunking audio..........")
    chunks, sil_ = get_chunks(sound,sil_)
    print("chunks : ", len(chunks), "Silence : ", sil_)
    if len(chunks)<25:
        chunks, sil_= get_chunks(sound, int(sil_/2))
        print("Silence if chunks less than 20 : ", sil_)

    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)

    
    print("chunk creation time: ", (time.time()-start)/60, "min")
    print('processing each chunk.......... ')
    st.write("chunk creation time: ", (time.time()-start)/60, "min")
    print("Total Chuncks: ",len(chunks))
    st.write("Total Chuncks: ",len(chunks))
    whole_text = ""
    src_text_dict={}
    dest_text_dict={}


    st.write('processing each chunk.......... ')
    start= time.time()  
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(directory, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        try:
            text = transcribe_audio(chunk_filename, lang=src_lang)
        except sr.UnknownValueError as e:
            print("Error:", str(e))
            text = " "
        else:
            
            src_text,dest_text = text_translator(text,dest_lang)
            src_text_dict[i] = src_text
            dest_text_dict[i] = dest_text 
            text = f"{text.capitalize()}. "
            print(chunk_filename, ":", text)
            st.write(f"\nAnalyzed chunk{i}.wav :    ","\n\n",text)
            whole_text += text
    print("chunk processing time: ", (time.time()-start)/60, "min")
    st.write("chunk processing time: ", (time.time()-start)/60, "min")
    # return the text for all chunks detected
    return whole_text,src_text_dict, dest_text_dict, sil_


#adjust target amplitude
def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)  

def get_timestamp(file, sil):
    audio_segment = AudioSegment.from_file(file)

    #normalize audio_segment to -20dBFS 
    # normalized_sound = match_target_amplitude(audio_segment, -20.0)
    # print("length of audio_segment={} seconds".format(len(normalized_sound)/1000))

    nonsilent_data = detect_nonsilent(audio_segment, min_silence_len=sil, silence_thresh=audio_segment.dBFS-14, seek_step=1)

    #convert ms to seconds
    print("total timestamp: ", len(nonsilent_data))
    # print("start,Stop")
    start_stop ={}
    for i,chunks in enumerate(nonsilent_data, start=1):
        start_stop[i] = [chunk/1000 for chunk in chunks]
        # print(i,":", [chunk/1000 for chunk in chunks]) 
    return start_stop
