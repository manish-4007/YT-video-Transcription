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



def create_caption(textJSON, framesize,v_type,font = "Arial",color='white', highlight_color='yellow',stroke_color='black',stroke_width=1.5):
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
  print("word_level: ",wordlevel_info)

  linelevel_subtitles = split_text_into_lines(wordlevel_info, v_type)
  print ("line_level_subtitles :",linelevel_subtitles)
  st.session_state.linelevel_subtitles = linelevel_subtitles

  for line in linelevel_subtitles:
    json_str = json.dumps(line, indent=4)
    print("whole json: ",json_str)
  outputfile = get_final_cliped_video(videofilename, linelevel_subtitles, v_type )
  return outputfile

      
def show_audio_video(audiofilename,videofilename):
      tab1, tab2 = st.tabs(['Edited video','audio'])
      with tab1:
        st.video(videofilename)
      with tab2:
        st.audio(audiofilename)
      

import subprocess
from getpass import getuser   

@st.cache_resource
def install_img_magic_commands_linux():
   try: 
      shell_script_path = "./img_magic.sh"

    # Use subprocess to execute the shell script
      try:
          print(subprocess.run(['chmod', '+x', 'img_magic.sh'], check=True))
          print(f"File {shell_script_path} is now executable.")

          print(subprocess.run(['mkdir', '-p', '~/.config/ImageMagick'], check=True)) 
          print("Directory Created .config/ImageMagick")
          print(subprocess.run(['chmod', '+w', '~/.config/ImageMagick'], check=True)) 
          print("permission give as write to .config/ImageMagick")
          
          # print(subprocess.run(["./img_magic.sh"]), capture_output=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
          source_path = "/etc/ImageMagick-6/policy.xml"
          destination_path = "~/.config/ImageMagick/policy.xml"
          destination_path = os.path.expanduser(destination_path)
          
          # Check if the destination directory exists, and create it if not
          destination_dir = os.path.dirname(destination_path)
          if not os.path.exists(destination_dir):
              os.makedirs(destination_dir)
                        
          # Read the content of the input file  
          with open(source_path, "r") as input_file:
              file_content = input_file.read()

          modified_content = file_content.replace("none", "read,write")
          
          # Write the modified content to the output file
          with open(destination_path, "w+") as output_file:
              output_file.write(modified_content)
              
          
          with open(destination_path, "r") as input_file:
              file_content = input_file.read()
        
          print(file_content)
          # st.write(subprocess.run(["cat","~/.config/ImageMagick/policy.xml"] text=True))
          print(subprocess.run(["convert", "-list", "policy"], capture_output=True, text=True))
          print('Sucessful')
      except Exception as e:
          print(f"Error: {e}")
          st.write(e)

   except Exception as e:
      st.write(e)


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
     install_img_magic_commands_linux()  
     print("Dependencise for video editing downloaded successfully.")
     st.session_state.img_magik = True
  except Exception as e:
      print('Some Errors ocurred while loading: ', e)

  model = load_model()
  st.session_state.whisp_model = model
  
  print('whisper Loaded.')

   

col1,col2 = st.columns(2)
with col1:

  video_url = st.text_input('Enter Url Link ')
  st.write('( Remove the video below, if uploaded any video )')
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
      st.session_state.audio = None
      
  if clip_sbtitle:
      video_file = None
      download_video(video_url)
      videofilename = os.path.join(directory,"video.mp4")
      st.session_state.videofile_path = videofilename
      st.session_state.audio = None
      
      if 'outputfile_path'  in st.session_state and st.session_state.outputfile_path is not None:
        st.session_state.outputfile_path = None
    
  if "edit" not in st.session_state:
    st.session_state.edit = False

  if video_file or video_url:
      
      # if 'outputfile_path'  in st.session_state and st.session_state.outputfile_path is not None:
      #   st.session_state.outputfile_path = None
    
      videofilename = st.session_state.videofile_path
      st.write("Title :", videofilename.split('\\')[-1])
      
      st.video(videofilename)
      
      cols = st.columns(2)

      with cols[0]:
        if st.button('Listen audio', use_container_width=True):
          st.session_state.outputfile_path = None
            
          with st.spinner('Converting Audio.......'):
            
            if st.session_state.audio is None:
              audiofilename = create_audio(videofilename)
              st.session_state.audio = audiofilename 
            
            st.success('Audio Created')
            st.audio(st.session_state.audio)
          print("OK")

      with cols[1]:      
        if st.button('Edit Video', use_container_width=True):
          st.session_state.edit =True

          try:
            if st.session_state.audio is None:
              with st.spinner('Converting Audio.......'):
                audiofilename = create_audio(videofilename) 
                st.success('Audio Created')
                st.session_state.audio = audiofilename 

          
            audiofilename =  st.session_state.audio 
            with st.spinner('Editing Video.......'):
              if 'img_magik' in st.session_state:
                  try:
                      outputfile = add_subtitle(videofilename, audiofilename, v_type)
                    
                  except Exception as e:
                      outputfile = videofilename
                      print('There is an erro:',e)
                      st.session_state.add_subtitles = False
                      
                  st.session_state.add_subtitles = True
              else:
                  outputfile = videofilename
              st.session_state.outputfile_path = outputfile
              st.success('Video Created')
          except Exception as e:
             st.write('There is an error, please refresh the page or upload other video:',e)

      if 'outputfile_path'  in st.session_state and st.session_state.outputfile_path is not None:
        show_audio_video(st.session_state.audio,st.session_state.outputfile_path)
        
  # if 'add_subtitles'  in st.session_state and st.session_state.add_subtitles is True:
  #     st.session_state.add_subtitles = False
        
except Exception as e:
  print(e)

if st.session_state.edit:
  if 'add_subtitles'  in st.session_state:
    if st.checkbox("Subtitle"):
      st.subheader('Generated Subtile for the video :')
      st.write('( There is problem while embedding subtitles into video)')
      for line_s in st.session_state.linelevel_subtitles:
          st.write(f"{round(line_s['start'],2)} - {round(line_s['end'],2)} : {line_s['word']}")
  show_hompage(key_1='sub_mer_rel', key_2='sub_mer_hm')