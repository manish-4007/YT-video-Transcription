<div align='center'>

<p align="center"><img src="https://socialify.git.ci/manish-4007/YT-video-Transcription/image?description=1&amp;descriptionEditable=This%20Web%20App%20is%20an%20AI-powered%20tool%20with%20a%20rich%20array%20of%20features%20designed%20to%20enhance%20the%20analysis%20of%20any%20video%20content.&amp;forks=1&amp;issues=1&amp;name=1&amp;owner=1&amp;pattern=Floating%20Cogs&amp;pulls=1&amp;stargazers=1&amp;theme=Auto" alt="project-image"></p>

<h1>Video Transcriptor</h1>
<p>This Web App is an AI tool packed with a wide array of capabilities designed to enhance the experience of interacting with YouTube videos YouTube Shots or any video content. It offers a versatile set of functionalities including transcription and scrolling subtitle embeddings. This versatile web app is a valuable resource for content creators researchers and anyone seeking to gain deeper insights into video content on YouTube or other platforms. Whether you need accurate transcriptions multi-language support sentiment analysis or enhanced accessibility through embedded subtitles into video with this tool. It also generates best description for the video and suggest the topics which are covered in the video.</p>

<h4> <a href=https://video-transcription-m.streamlit.app/>View Demo</a> <span> · </span> <a href="https://github.com/manish-4007/YT-video-Transcription/blob/master/README.md"> Documentation </a> <span> · </span> <a href="https://github.com/manish-4007/YT-video-Transcription/issues"> Report Bug </a> <span> · </span> <a href="https://github.com/manish-4007/YT-video-Transcription/issues"> Request Feature </a> </h4>


</div>

# :notebook_with_decorative_cover: Table of Contents

- [About the Project](#star2-about-the-project)
- [Getting Started](#toolbox-getting-started)
- [Roadmap](#compass-roadmap)
- [License](#warning-license)
- [Contact](#handshake-contact)
- [Acknowledgements](#gem-acknowledgements)


## :star2: About the Project

### :camera: Screenshots
<div align="center"> <a href="https://video-transcription-m.streamlit.app/"><img src="https://socialify.git.ci/manish-4007/YT-video-Transcription/image?description=1&descriptionEditable=This%20Web%20App%20is%20an%20AI-powered%20tool%20with%20a%20rich%20array%20of%20features%20designed%20to%20enhance%20the%20analysis%20of%20any%20video%20content.&forks=1&issues=1&name=1&owner=1&pattern=Floating%20Cogs&pulls=1&stargazers=1&theme=Auto" alt='image' width='800'/></a> </div>



### :dart: Features
- Video Scrapping and Data Visualization
- Content Analyzer
- Video Transcription
- Subtitle Embedding into Video
- Video Sentimental Analysis based comments
- Name Entity Recognition on Video Content
- Suggest Description and Topics by analyzing Video Content


### :key: Environment Variables
To run this project, you will need to add the following environment variables to your .env file

`ImageMagick`

`ffmpeg`

`API Keys`



## :toolbox: Getting Started

### :bangbang: Prerequisites

- ffmpeg<a href="https://ffmpeg.org/download.html"> Here</a>
- ImageMagick<a href="https://imagemagick.org/script/download.php"> Here</a>


<h2>🛠️ Installation Steps:</h2>

<p> First, set-up FFmpeg and ImageMagick packages into the system and save into the environmental variable path in the program to use ffmpeg and ffprobe</p>

<p> Check at the main file where we use these packages into the code must have detected the path of ffmpeg and ffprobe (or else add them manually as done in the setup.py file)</p>

```
ffmpeg_binary =  "/usr/bin/ffmpeg"
   
ffprobe_binary = "/usr/bin//ffprobe"
   
pydub.AudioSegment.ffmpeg = ffmpeg_binary

ffmpeg.input.ffmpeg = ffmpeg_binary

pydub.AudioSegment.ffprobe = ffprobe_binary

ffmpeg.input.ffprobe = ffprobe_binary
```

<p> Or For Streamlit we can add a packages.txt which installs all the required files and setup for the FFmpeg and ImageMagick, It actually automatically runs the command:</p>

```
apt-get install package ( for all the packages in the packages.txt)
```


### :gear: Installation

To use ImageMagick for editing the video with the Moviepy python package we need to allow permissions to read/write to the policy.xml ( as per default policy it is set as none )
```bash
sudo cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g'> /etc/ImageMagick-6/policy.xml
```


### :running: Run Locally

Clone the project

```bash
https://github.com/manish-4007/YT-video-Transcription
```
Go to the project directory
```bash
cd video_transcriptor
```
Create Virtual Environment
```bash
python -m venv venv
```
Activate the environment
```bash
./venv/Scripts/activate
```
Now run the setup.py file to install all the dependencies
```bash
python ./setup.py
```
if still some packages did not installed then run the the requirement.txt using pip
```bash
pip install -r ./requirements.txt
```
Now all setup done, just run the streamlit file from the terminal to run it in the local server
```bash
streamlit run ./Home.py
```


## :computer: Technologies Used in the Project
  
### :gear: Built with


*   Pytube and Youtube API v3 ( for Video Analysis )
*   Pydub Speech Recognition Fast Whisper (for Speech Recognition from Video to Text )
*   Moviepy ffmpeg and ImageMagick ( Editing Video)
*   NLTK SpaCy SpacyTextBlob ( For NLP Tasks like Sentiment Analysis and Text Summarizer )
*   Googletrans and Transformers ( For Text Translation and Topic Modelling )
*   Hugging Face Transformers - Bart Model by "facebook/bart-large-mnli"
*   Streamlit and Streamlit-extras ( Web App Creation and Deployment )

## :compass: Roadmap

* [x] Video Analyzer
* [x] Download Video Feature
* [x] Video Analatytics
* [x] Sentiment Analysis on Comments
* [x] Show comments based on Sentiment
* [x] Video Transcription to any languages
* [x] Subtitle Generator
* [x] Description Generator
* [x] Name Entity Recognition on Video Content
* [x] Subtitle Converter into any Languages
* [x] Subtile Embeding into Video
* [ ] Topic Modelling on Video Content


## :warning: License


This project is licensed under the Apache-2.0 license



## :handshake: Contact

Manish Rai Chodhury - [LinkedIn Profile](https://www.linkedin.com/in/manish-rai-chodhury-170318197/) - manish.rai709130@gmail.com

Project Link: [https://github.com/manish-4007/YT-video-Transcription](https://github.com/manish-4007/YT-video-Transcription)

## :gem: Acknowledgements

Use this section to mention useful resources and libraries that you have used in your projects.

- [YouTube API V3](https://developers.google.com/youtube/v3/docs)
- [Faster Whisper for Speech to Text](https://github.com/guillaumekln/faster-whisper)
- [Subtiles Embedding Scrolling Feature](https://github.com/ramsrigouthamg/Supertranslate.ai)
