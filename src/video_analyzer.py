import streamlit as st
import nltk
import string
from heapq import nlargest
from spacy import displacy

from pytube import YouTube

import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd
from spacytextblob.spacytextblob import SpacyTextBlob
import spacy
from dotenv import load_dotenv
import os,requests,time

# Load environment variables from the .env file
load_dotenv()
# st.write(st.session_state)
dev_key = os.getenv("DEVELOPER_KEY")
HUGGING_FACE_TOKEN=os.getenv("HUGGING_API_KEY")

def youtube_api_setup(dev_key):
    # youtube api ver3 setup

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = dev_key

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)
    return youtube
youtube = youtube_api_setup(dev_key)


 # Video ID of the YouTube video

yt = YouTube("https://www.youtube.com/watch?v=2B0q2k5BTVo")
d = {
      "id": yt.video_id,
      "channel_url":yt.channel_url,
      "title": yt.title,
      "views": yt.views,
      "length":yt.length,
      "publish_date": yt.publish_date,
      "Description": yt.description,
      "keywords": yt.keywords,
}

v_id =  d["id"]

def video_ratings(v_id):
        
        
    description = youtube.videos().list(part='snippet',id= v_id).execute()
    video_snippet = description["items"][0]['snippet']
    video_description = video_snippet['description']

    video_response = youtube.videos().list(part="statistics", id=v_id).execute()
    video_statistics = video_response["items"][0]["statistics"]

    views = int(video_statistics["viewCount"])
    likes = int(video_statistics["likeCount"])
    totalComments = int(video_statistics['commentCount'])

    print("View Count : ", views)
    print("like Count : ", likes)
    print("Comment Count : ", totalComments )
    print(f"\n{round(likes/views*100, 2)}% viewers likes the video ")
    print(f"{round(totalComments/views*100)}% viewers commented on  the video ")

    return video_description,views, likes, totalComments

def comment_analyzer(v_id):
    st.session_state.comment_df = True
    comments = []

    next_page_token = None

    while True:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=v_id,
            maxResults=1000,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append([
                comment['authorDisplayName'],
                comment['publishedAt'],
                comment['updatedAt'],
                comment['likeCount'],
                comment['textDisplay']
            ])

        # Check if there are more comments to fetch
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    print("Collected")
    df = pd.DataFrame(comments, columns=['author', 'published_at', 'updated_at', 'like_count', 'comments'])

    df['published_at'] = pd.to_datetime(df['published_at'])
    df['published_at'] = df['published_at'].dt.date

    return df


def senti_polar(text):
  try:
      nlp = st.session_state.nlp
      doc = nlp(text)
      pol = doc._.polarity
      if pol>0:
        return "Positive"
      elif pol<0:
        return "Negative"
      else:
        return "Neutral"
  except:
    return "NA"

def detect_sentiment(df):
    sentiment=[]
    for text in df['comments']:
        try:
            sentiment.append(senti_polar(text))
        except RuntimeError:
            print(f'Broke for the {text}')
            sentiment.append("NA")

    df['sentiment']= sentiment
    x = df['sentiment'].value_counts().sort_values(ascending = False)
    print(x)
    print('Scanning Completed')
    video_sentiment = f"  More towards '{x.index[0]} Sentiment' with a little {x.index[1]} Tone"

    return df, video_sentiment

def summarize(text):
  if text.count(". ") > 20:
      length = int(round(text.count(". ")/10, 0))
  else:
      length = 1

  nopuch =[char for char in text if char not in string.punctuation]
  nopuch = "".join(nopuch)

  processed_text = [word for word in nopuch.split() if word.lower() not in nltk.corpus.stopwords.words('english')]

  word_freq = {}
  for word in processed_text:
      if word not in word_freq:
          word_freq[word] = 1
      else:
          word_freq[word] = word_freq[word] + 1

  max_freq = max(word_freq.values())
  for word in word_freq.keys():
      word_freq[word] = (word_freq[word]/max_freq)

  sent_list = nltk.sent_tokenize(text)
  sent_score = {}
  for sent in sent_list:
      for word in nltk.word_tokenize(sent.lower()):
          if word in word_freq.keys():
              if sent not in sent_score.keys():
                  sent_score[sent] = word_freq[word]
              else:
                  sent_score[sent] = sent_score[sent] + word_freq[word]

  summary_sents = nlargest(length, sent_score, key=sent_score.get)
  summary = " ".join(summary_sents)
  return summary

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
    predicted_topic = result["labels"][:5]
#  Adding suggested keywords into existing keyword of a youtube video
    data = st.session_state.video_info
    a= data['keywords']
    predicted_topic.extend(a)
    st.write(predicted_topic.keys()   )

    # Updating the keywords into the session state
    st.session_state.video_info['keywords'] = predicted_topic


def main():

    st.header('Youtube Analyzer')


    # if st.checkbox("Video Info"):
    views,likes,totalComments = video_ratings(v_id)
    st.markdown(f"Channel URL - {d['channel_url']}")
    st.write(f"Description -  published at {d['publish_date']}, ")

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

    print('\ncollecting comments....')
    if 'comment_df' not in  st.session_state:
        print('Creating comments in session_state and store into it..............')
        st.session_state.comment_df = comment_analyzer(v_id)
        nlp = spacy.load("en_core_web_lg")
        nlp.add_pipe('spacytextblob')
        st.session_state.nlp = nlp
        print("NLP loaded from SpaCy")

    # if st.session_state.comments:
    #     print('getting the comment dataframe from session_state.............')
    #     com_df =  st.session_state.comment_df
    #     nlp = st.session_state.nlp
    # else:
    #     print("Checking and storing data to session_state ..................")
        # st.session_state.comment_df = comment_analyzer(v_id)



    # # whole_text = st.session_state.subtiles_eng 
    whole_text = "Did you know that you can see how many people are getting notifications on your channel as well as how many notifications were sent for each of your videos? you must know hi i am gabru a product expert youtube to see how many people watch your channel send notifications Open the song and your computer and look for the Audience tabYou can see how many people ring the bell on your channelAnd those who really like notifications from YouTube give an accurate representation of who will receive it Notification Videos You want to see Honey notifications when you're out for specific videos How to write videos and songsand click on the middle tabHere you can also see the notifications as well as the resulting number of windows usage Notification that any post is ready to be viewed"

    if st.checkbox("show_info"):
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

            
        if st.checkbox("Show Video Analytics"):

            st.subheader('Line chart for comment counts on the video in each day from the day of video publish')
            print("comments colletection Done\n")
            
        
            df1 = com_df.groupby('published_at').count().reset_index()

            min_date = df1['published_at'].min()
            max_date = df1['published_at'].max()
            date_range = st.slider('Enter the date Range :',min_date,max_date, (min_date,max_date))

            df1 = df1[df1['published_at']>=date_range[0]]
            df1 = df1[df1['published_at']<=date_range[1]]

            df2 = st.session_state.top_comm_df
            
            df2 = df2[df2['published_at']>=date_range[0]]
            df2 = df2[df2['published_at']<=date_range[1]]

            #Grabbing top comments using filters 
            tabs = st.tabs(['Comment Analytics','Comments'])
            with tabs[0]:
                df1.rename(columns={'published_at': 'Comments (By Date)', 'comments':'Comments count'}, inplace=True)
                st.line_chart(data = df1,x = 'Comments (By Date)', y = 'Comments count')

            with tabs[1]:
                rev_sentiment = st.selectbox("Select_ratings", options = ['All','Positive',"Neutral","Negative"])
                with st.spinner("Loading Comments...."):
                    st.subheader(f"{rev_sentiment} comments are : ")
                    if rev_sentiment=='All':
                        st.dataframe(df2[['author', 'published_at','comments']].set_index('published_at'))
                    else:
                        st.dataframe(df2[df2['sentiment']==rev_sentiment][['author', 'published_at','comments']].set_index('published_at'))

            


        # nlp = spacy.load("en_core_web_lg")

        # nlp.add_pipe('spacytextblob')

        # Video Sentiment Analysis using Comment


        # Text Summarization

    print('Summarizing  Video Content....')
    if 'text_summ' not in  st.session_state:
        nltk.download('stopwords')
        nltk.download('punkt')
        # nlp = spacy.load("en_core_web_lg")
        # nlp.add_pipe('spacytextblob')
        # st.session_state.nlp = nlp
        print("For Summarize  nltk dependencies loaded")
        st.session_state.text_summ = ""


    # if st.button('Summarize'):
    # st.write("Summarized Text / Description :")
    st.session_state.text_summ = summarize(whole_text)
    # st.write(st.session_state.text_summ )

        
    from streamlit_extras.stoggle import stoggle

    tabs = st.tabs(['Description','NER'])
    with tabs[0]:
        stoggle(
            "Description: ",
            f"""🥷 {st.session_state.text_summ }""",
        )


    # ner = st.checkbox("Show Name Entity Recognition")
    # if ner :
    with tabs[1]:
        tab1,tab2 = st.tabs(["Whole Text","Summarized Text"])
        nlp = st.session_state.nlp
        with tab1:
            doc = nlp(whole_text)
            st.write("NER on whole Subtile Text from video : \n")
            st.markdown(displacy.render(doc, style="ent",jupyter=False), unsafe_allow_html=True)

        with tab2:
            summ_doc = nlp(summarize(whole_text))
            st.write("\nNER on Summarized Transcribe Text: \n")
            st.markdown(displacy.render(summ_doc, style="ent",jupyter=False), unsafe_allow_html=True)

    # if  d['Description'] is None:
    #   d['Description']= st.session_state.text_summ 



    # st.write(st.session_state)

if __name__=='__main__':
    main()