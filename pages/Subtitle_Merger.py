import streamlit as st
from src.youtube_audio import YouTube,directory
import os, json
from faster_whisper import WhisperModel

from pytube import YouTube
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.colored_header import colored_header

import time,tempfile
import ffmpeg
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip,VideoFileClip, ColorClip

import numpy as np

start= time.time()

directory = tempfile.gettempdir() 


def create_audio(videofilename):
  audiofilename = videofilename.replace(".mp4",'.mp3')

  # Create the ffmpeg input stream
  input_stream = ffmpeg.input(videofilename)

  # Extract the audio stream from the input stream
  audio = input_stream.audio

  # Save the audio stream as an MP3 file
  output_stream = ffmpeg.output(audio, audiofilename)

  # Overwrite output file if it already exists
  output_stream = ffmpeg.overwrite_output(output_stream)

  ffmpeg.run(output_stream)

  return audiofilename

def download_video(url):
    yt = YouTube(url)

    try:
        if yt.streams.filter(only_audio = True,file_extension='mp4') :
            video = yt.streams.filter(res="720p",file_extension='mp4')[0]
        else:
            video = yt.streams.filter(mime_type="video/mp4")[0]
    except Exception as e:
        print("No video found!!")
    print('Downloading video...')  # Downloading video...
    print(video)
    video.download(directory, filename = 'video.mp4')
    print(yt.title + "vidoeo has been successfully downloaded in .mp4 format.")


def transcribe_audio(whisper_model, audiofilename):
  segments, info = whisper_model.transcribe(audiofilename, word_timestamps=True)
  segments = list(segments)  # The transcription will actually run here.
  wordlevel_info = []

  for segment in segments:
      for word in segment.words:
        wordlevel_info.append({'word':word.word,'start':word.start,'end':word.end})
  return wordlevel_info

def split_text_into_lines(data,v_type):

    if v_type.lower() !='reels':
      MaxChars = 30
    else:
      MaxChars = 15   #For Reels

    #maxduration in seconds
    MaxDuration = 2.5
    #Split if nothing is spoken (gap) for these many seconds
    MaxGap = 1.5

    subtitles = []
    line = []
    line_duration = 0
    line_chars = 0


    for idx,word_data in enumerate(data):
        word = word_data["word"]
        start = word_data["start"]
        end = word_data["end"]

        line.append(word_data)
        line_duration += end - start

        temp = " ".join(item["word"] for item in line)


        # Check if adding a new word exceeds the maximum character count or duration
        new_line_chars = len(temp)

        duration_exceeded = line_duration > MaxDuration
        chars_exceeded = new_line_chars > MaxChars
        if idx>0:
          gap = word_data['start'] - data[idx-1]['end']
          # print (word,start,end,gap)
          maxgap_exceeded = gap > MaxGap
        else:
          maxgap_exceeded = False


        if duration_exceeded or chars_exceeded or maxgap_exceeded:
            if line:
                subtitle_line = {
                    "word": " ".join(item["word"] for item in line),
                    "start": line[0]["start"],
                    "end": line[-1]["end"],
                    "textcontents": line
                }
                subtitles.append(subtitle_line)
                line = []
                line_duration = 0
                line_chars = 0


    if line:
        subtitle_line = {
            "word": " ".join(item["word"] for item in line),
            "start": line[0]["start"],
            "end": line[-1]["end"],
            "textcontents": line
        }
        subtitles.append(subtitle_line)

    return subtitles



def create_caption(textJSON, framesize,v_type,font = "Helvetica",color='white', highlight_color='yellow',stroke_color='black',stroke_width=1.5):
    wordcount = len(textJSON['textcontents'])
    full_duration = textJSON['end']-textJSON['start']

    word_clips = []
    xy_textclips_positions =[]

    x_pos = 0
    y_pos = 0
    line_width = 0  # Total width of words in the current line
    frame_width = framesize[0]
    frame_height = framesize[1]

    x_buffer = frame_width*1/10

    max_line_width = frame_width - 2 * (x_buffer)

    if v_type.lower() !='reels':
      fontsize = int(frame_height * 0.075) #7.5 percent of video height
    else:
      fontsize = int(frame_height * 0.05) #5 percent of video height for Reels

    space_width = ""
    space_height = ""

    for index,wordJSON in enumerate(textJSON['textcontents']):
      duration = wordJSON['end']-wordJSON['start']
      word_clip = TextClip(wordJSON['word'], font = font,fontsize=fontsize, color=color,stroke_color=stroke_color,stroke_width=stroke_width).set_start(textJSON['start']).set_duration(full_duration)
      word_clip_space = TextClip(" ", font = font,fontsize=fontsize, color=color).set_start(textJSON['start']).set_duration(full_duration)
      word_width, word_height = word_clip.size
      space_width,space_height = word_clip_space.size
      if line_width + word_width+ space_width <= max_line_width:
            # Store info of each word_clip created
            xy_textclips_positions.append({
                "x_pos":x_pos,
                "y_pos": y_pos,
                "width" : word_width,
                "height" : word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })

            word_clip = word_clip.set_position((x_pos, y_pos))
            word_clip_space = word_clip_space.set_position((x_pos+ word_width, y_pos))

            x_pos = x_pos + word_width+ space_width
            line_width = line_width+ word_width + space_width
      else:
            # Move to the next line
            x_pos = 0
            y_pos = y_pos+ word_height+10
            line_width = word_width + space_width

            # Store info of each word_clip created
            xy_textclips_positions.append({
                "x_pos":x_pos,
                "y_pos": y_pos,
                "width" : word_width,
                "height" : word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })

            word_clip = word_clip.set_position((x_pos, y_pos))
            word_clip_space = word_clip_space.set_position((x_pos+ word_width , y_pos))
            x_pos = word_width + space_width


      word_clips.append(word_clip)
      word_clips.append(word_clip_space)


    for highlight_word in xy_textclips_positions:

      word_clip_highlight = TextClip(highlight_word['word'], font = font,fontsize=fontsize, color=highlight_color,stroke_color=stroke_color,stroke_width=stroke_width).set_start(highlight_word['start']).set_duration(highlight_word['duration'])
      word_clip_highlight = word_clip_highlight.set_position((highlight_word['x_pos'], highlight_word['y_pos']))
      word_clips.append(word_clip_highlight)

    return word_clips,xy_textclips_positions

  
def get_final_cliped_video(videofilename, linelevel_subtitles, v_type ):
  input_video = VideoFileClip(videofilename)
  frame_size = input_video.size

  all_linelevel_splits=[]

  for line in linelevel_subtitles:
    out_clips,positions = create_caption(line,frame_size,v_type)

    max_width = 0
    max_height = 0

    for position in positions:
      # print (out_clip.pos)
      # break
      x_pos, y_pos = position['x_pos'],position['y_pos']
      width, height = position['width'],position['height']

      max_width = max(max_width, x_pos + width)
      max_height = max(max_height, y_pos + height)

    color_clip = ColorClip(size=(int(max_width*1.1), int(max_height*1.1)),
                        color=(64, 64, 64))
    color_clip = color_clip.set_opacity(.6)
    color_clip = color_clip.set_start(line['start']).set_duration(line['end']-line['start'])

    # centered_clips = [each.set_position('center') for each in out_clips]

    clip_to_overlay = CompositeVideoClip([color_clip]+ out_clips)
    clip_to_overlay = clip_to_overlay.set_position("bottom")


    all_linelevel_splits.append(clip_to_overlay)

  input_video_duration = input_video.duration


  final_video = CompositeVideoClip([input_video] + all_linelevel_splits)

  # Set the audio of the final video to be the same as the input video
  final_video = final_video.set_audio(input_video.audio)
  destination = os.path.join(directory,'output.mp4')
  # Save the final clip as a video file with the audio included
  final_video.write_videofile(destination, fps=24, codec="libx264", audio_codec="aac")
 
  return destination


def add_subtitle (videofilename, audiofilename, v_type):
  print("Video and Audio filesare : ", videofilename,audiofilename)

  model = st.session_state.whisp_model
  wordlevel_info = transcribe_audio(model,audiofilename)
  print(wordlevel_info)

  linelevel_subtitles = split_text_into_lines(wordlevel_info, v_type)
  print (linelevel_subtitles)

  for line in linelevel_subtitles:
    json_str = json.dumps(line, indent=4)
    print(json_str)
  outputfile = get_final_cliped_video(videofilename, linelevel_subtitles, v_type )
  return outputfile

      
def show_audio_video(audio,video):
      tab1, tab2 = st.tabs(['Edited video','audio'])
      with tab1:
        st.video(videofilename)
      with tab2:
        st.audio(audiofilename)
      

import subprocess

def install_img_magic_commands_linux():
   
    # # Run "apt install imagemagick"
    subprocess.run(["sudo", "apt", "install", "imagemagick"], capture_output=True, text=True)
    print("inagemagick installed successfully.")


    # Run "cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g'> /etc/ImageMagick-6/policy.xml"
    subprocess.run(
        ["sudo", "sh", "-c", "cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g'> /etc/ImageMagick-6/policy.xml"],
        capture_output=True,
        text=True
    )


@st.cache_resource()
def install_img_magic_commands():
    # # Replace 'download_link' with the actual download link of the ImageMagick installer
    # download_link = "https://imagemagick.org/archive/binaries/ImageMagick-7.1.1-15-Q16-HDRI-x64-dll.exe"
    # installer_path = "ImageMagickInstaller.exe"

    # # Download the installer
    # print("Downloding the installer......")
    # # subprocess.run(["curl", "-o", installer_path, download_link])

    # # Run the installer
    # print("Running the installer......")
    # # subprocess.run([installer_path])

    # # Clean up the installer
    # # subprocess.run(["del", installer_path])

    print(subprocess.run(["sudo", "apt", "install", "imagemagick"], capture_output=True, text=True))  

    # print("Setting Up environment.....")
    # # Replace 'installation_path' with the actual installation path of ImageMagick
    FFMPEG_BINARY='/usr/bin/ffmpeg'
    IMAGEMAGICK_BINARY='/usr/bin/convert'

    import moviepy.editor as mp

    # Set the path to the ImageMagick binary (replace '/usr/bin/convert' with your actual path)
    mp.config.change_settings(imagemagick_binary=IMAGEMAGICK_BINARY)

    # # Get the current PATH variable
    current_path = os.environ['PATH']

    # # Add ImageMagick installation directory to PATH
    os.environ['PATH'] = f"{IMAGEMAGICK_BINARY};{current_path}"

    # IMAGEMAGICK_BINARY  = os.getenv ('IMAGEMAGICK_BINARY', 'C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\convert.exe')
    
    # Run "apt install imagemagick"
    # subprocess.run(["sudo", "apt", "install", "imagemagick"], capture_output=True, text=True)
    print("inagemagick installed successfully.")

    # Run "cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g'> /etc/ImageMagick-6/policy.xml"
    # subprocess.run(
    #     ["sudo", "sh", "-c", "cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g'> /etc/ImageMagick-6/policy.xml"],
    #     capture_output=True,
    #     text=True
    # )

    install_img_magic_commands_linux()

    print("All Set-up completed...")

@st.cache_resource
def load_model():
  print('Loading the Wishper Model into the App............')

  model_size = "base"
  try:
      model = WhisperModel(model_size,  device="cuda", compute_type="float16")
  except RuntimeError as e:
      model = WhisperModel(model_size)
      print("Error: ", e)


  st.success("Loaded model!")
  return model




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

st.title('Reel Subtitle Generater ')
st.title('\n')
colored_header(
    label="Generate and Embed the subtitles into the video",
    description="❗works faster on smaller video like yt shots ❗ ",
    color_name="blue-green-70",
)
st.markdown('<h4>Enter a Youtube shorts Link or upload the video.<h4>',unsafe_allow_html=True)


if 'whisp_model' not in st.session_state:
  print("Downloading dependecies...")

  try:
     install_img_magic_commands()  
     print("Dependencise for video editing downloaded successfully.")
     st.session_state.img_magik = True
  except Exception as e:
      print('Some Errors ocurred while loading: ', e)

  model = load_model()
  st.session_state.whisp_model = model
  
  print('whisper Loaded.')

   

col1,col2 = st.columns(2)
with col1:

  video_url = st.text_input('Enter Url Link')
  clip_sbtitle = st.button("Edit Video")
  
with col2:

  v_type= st.radio("Video Type",['Reels', "Video"])
  st.subheader (" OR ")

video_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov"])


try: 
  if video_file is not None:
      video_url = None    
      clip_sbtitle = False

      videofilename = os.path.join(directory, video_file.name)
      with open(videofilename, "wb") as f:
          f.write(video_file.read())
      
      st.session_state.videofile_path = videofilename

  if clip_sbtitle:
      video_file = None
      download_video(video_url)
      videofilename = os.path.join(directory,"video.mp4")
      st.session_state.videofile_path = videofilename
      
    
  if "edit" not in st.session_state:
    st.session_state.edit = False

  if video_file or video_url:
    
      videofilename = st.session_state.videofile_path
      st.write("Title :", videofilename.split('\\')[-1])
      
      st.video(videofilename)
      
      cols = st.columns(2)

      with cols[0]:
        if st.button('Listen audio', use_container_width=True):
          st.session_state.outputfile_path = None
            
          with st.spinner('Converting Audio.......'):
            
            if 'audio' not in st.session_state:
              audiofilename = create_audio(videofilename)
              st.session_state.audio = audiofilename 
            
            st.success('Audio Created')
            st.audio(st.session_state.audio)
          print("OK")

      with cols[1]:      
        if st.button('Edit Video', use_container_width=True):
          st.session_state.edit =True

          try:
            if 'audio' not in st.session_state:
              with st.spinner('Converting Audio.......'):
                audiofilename = create_audio(videofilename) 
                st.success('Audio Created')
                st.session_state.audio = audiofilename 

          
            audiofilename =  st.session_state.audio 
            with st.spinner('Editing Video.......'):
              if 'img_magik' in st.session_state:
                  outputfile = add_subtitle(videofilename, audiofilename, v_type)
              else:
                  outputfile = videofilename
              st.write(outputfile)
              st.session_state.outputfile_path = outputfile
              st.success('Video Created')
          except Exception as e:
             st.write('There is an erro:',e)
      if 'outputfile_path'  in st.session_state and st.session_state.outputfile_path is not None:
        show_audio_video(audiofilename,st.session_state.outputfile_path)
        
except Exception as e:
  st.write(e)

if st.session_state.edit:
  show_hompage(key_1='sub_mer_rel', key_2='sub_mer_hm')