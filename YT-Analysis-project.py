#!/usr/bin/env python
# coding: utf-8

# In[1]:


from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns


# In[2]:


api_key = 'AIzaSyAYS7Bbea_Whbcp9ZIwyrCk65OGNoKaq5A'

# Amend both channel ids and channel names
channel_ids = ['UCrPseYLGpNygVi34QpGNqpA', #Ludwig
               'UCgv4dPk_qZNAbUW9WkuLPSA', #Atrioc
               'UCpJZz0NtSgIdFhaXSPV4YqQ'  #Stanz
              ]

channel_names = ['Ludwig', 'Atrioc', 'Stanz']

youtube = build('youtube', 'v3', developerKey=api_key)


# ## Function to get channel statistics

# In[3]:


def get_channel_stats(youtube, channel_ids):
    all_data = []
    request = youtube.channels().list(
                part='snippet,contentDetails,statistics',
                id=','.join(channel_ids))
    response = request.execute()
    
    for i in range(len(response['items'])):
        data = dict(Channel_name = response['items'][i]['snippet']['title'],
                    Subscribers = response['items'][i]['statistics']['subscriberCount'],
                    Views = response['items'][i]['statistics']['viewCount'],
                    Total_videos = response['items'][i]['statistics']['videoCount'],
                    Playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
        all_data.append(data)
        
    return all_data


# In[4]:


channel_statistic = get_channel_stats(youtube, channel_ids)


# In[5]:


channel_data = pd.DataFrame(channel_statistic)


# In[6]:


channel_data


# In[7]:


channel_data['Subscribers'] = pd.to_numeric(channel_data['Subscribers'])
channel_data['Views'] = pd.to_numeric(channel_data['Views'])
channel_data['Total_videos'] = pd.to_numeric(channel_data['Total_videos'])
channel_data['Ratio'] = channel_data['Views']/channel_data['Total_videos']


# ## Function to get video ids

# In[8]:


playlist_ids = []
for x in channel_names:
    playlist_ids.append(channel_data.loc[channel_data['Channel_name']==x, 'Playlist_id'].iloc[0])


# In[9]:


def get_video_ids(youtube,playlist_id):
    
    request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId = playlist_id,
                maxResults = 50)
    response = request.execute()
    
    video_ids = []
    
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
    
    next_page_token = response['nextPageToken']
    more_pages = True
    
    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                        part='contentDetails',
                        playlistId = playlist_id,
                        maxResults = 50,
                        pageToken = next_page_token)
            response = request.execute()

            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
                
            next_page_token = response.get('nextPageToken')
            
    return video_ids


# In[10]:


video_ids = []
for x in playlist_ids:
    each_video_list = get_video_ids(youtube, x)
    
    for y in each_video_list:
        video_ids.append(y)


# ## Function to get video details

# In[11]:


def get_video_details(youtube, video_ids):
    all_video_stats = []
    
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
                    part='snippet,statistics',
                    id=','.join(video_ids[i:i+50]))
        response = request.execute()
        
        for video in response['items']:
            video_stats = dict(Name = video['snippet']['channelTitle'],
                               Title = video['snippet']['title'],
                               Published_date = video['snippet']['publishedAt'],
                               Views = video['statistics']['viewCount'],
                               Likes = video['statistics']['likeCount'],
                               Dislikes = video['statistics']['dislikeCount'],
                               Comments = video['statistics']['commentCount']
                              )
            all_video_stats.append(video_stats)

    return all_video_stats


# In[12]:


video_details = get_video_details(youtube, video_ids)


# In[13]:


video_data = pd.DataFrame(video_details)


# In[14]:


video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data['Dislikes'] = pd.to_numeric(video_data['Dislikes'])
video_data['Comments'] = pd.to_numeric(video_data['Comments'])


# In[15]:


video_data['Month'] = pd.to_datetime(video_data['Published_date']).dt.strftime('%b')


# In[16]:


video_data


# In[17]:


video_data.to_csv('Video_Details.csv')

