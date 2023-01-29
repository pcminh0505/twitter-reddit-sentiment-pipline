import plotly.express as px
import plotly.graph_objects as go
import re
import string
import numpy as np
from PIL import Image
from nltk.corpus import stopwords
import nltk
# nltk.download('stopwords')
from nltk.tokenize import word_tokenize
import os
import pandas as pd
from s3bucket import *
from wordcloud import WordCloud, STOPWORDS
from collections import Counter

def date_chart(dfTwitter, dfReddit, topic):
    if (topic == 'twitter'):
        df = dfTwitter
    else: 
        df = dfReddit

    fig=go.Figure()
    graph_data = df.copy()
    graph_data['created_ns'] = pd.to_datetime(graph_data['created_at'])
    graph_data.set_index('created_ns',inplace=True) # setting the index to 'created' column
    sent_dict = {'1': 'NEGATIVE', '2': 'NEUTRAL', '3': 'POSITIVE'} # mapping sentiment numbers to text values
    sent_colors= {'1': 'red', '2': '#e3a817', '3': 'green'} # mapping sentiment numbers to colors

    for i in range(1,4):
        data=graph_data[graph_data['sentiment']== sent_dict[str(i)]] # looping through the data filtered with each sentiment
        data=data.resample('1D').count() # getting the count of tweets for each day

        # line chart

        if (topic == 'twitter'):
            id_col = 'tweet_id'
        else: id_col = 'reddit_id'

        fig.add_trace(
            go.Scatter(x=data.index, y=data[id_col].astype('int64'), mode='lines', name=sent_dict[str(i)].capitalize(),
                       marker_color=sent_colors[str(i)]
                       ))

    fig.update_layout(
        xaxis_title='<b>Date<b>', yaxis_title='<b>Count<b>',
        xaxis=dict(
            tickwidth=2, tickcolor='#80ced6',
            ticks="outside",
            tickson="labels",
            rangeslider_visible=False
        ),margin=dict(l=0, r=0, t=30, b=0)
    )
    fig.update_xaxes(showgrid=False, showline=True, zeroline=False, linecolor='black')
    fig.update_yaxes(showgrid=False, showline=True, zeroline=False, linecolor='black')
    return fig

def create_freq_bar(dfTwitter, dfReddit, source):
    if (source == 'twitter'): 
        word_list = dfTwitter['cleaned_text'].tolist()
    elif (source == 'reddit'):
        word_list = dfReddit['cleaned_text'].tolist()
    else:
        frames = [dfReddit, dfTwitter]
        dfAll = pd.concat(frames)
        word_list = dfAll['cleaned_text'].tolist()

    text = " ".join([str(i) for i in word_list])
    text = re.sub('chatgpt','a', text)

    shortword = re.compile(r'\W*\b\w{1,5}\b')
    count_dict = Counter(shortword.sub('',text).split(' '))
    
    most_common_words_df = pd.DataFrame(count_dict.most_common(20), columns=['word', 'count'])
    
    fig=go.Figure()
    fig.add_trace(go.Bar(x=most_common_words_df['word'], y=most_common_words_df['count'],
                         marker_color='#FF4500',
                         textposition='auto', textfont=dict(
            size=13,color='black'

        ))
                  )

    fig.update_layout(
            xaxis_title='<b>{}<b>'.format('words'.capitalize()), yaxis_title='<b>Frequency<b>',
            font=dict(size=13, family='Arial', color='black'), hoverlabel=dict(
                font_size=14, font_family="Rockwell"), plot_bgcolor='#f7f7f7',
            paper_bgcolor='#f7f7f7',margin=dict(l=0, r=0, t=20, b=0)

        )
    fig.update_xaxes(showgrid=False, showline=True, zeroline=False, linecolor='black',visible=True)
    fig.update_yaxes(showgrid=False, showline=True, zeroline=False, linecolor='black',visible=True,showticklabels=True)
    return fig


'''
vertical bar chart
'''
def create_ver_bar(df,location):
    graph_data = df.copy()
    graph_data=graph_data.groupby(location,sort=False)['tweet_id'].count() # grouping by city or country column and get tweets count for each
    graph_data.sort_values(inplace=True, ascending=False)
    graph_data = graph_data.nlargest(5)  # gettting the largest 5 countries or cities with tweets
    fig=go.Figure()
    fig.add_trace(go.Bar(x=graph_data.index, y=graph_data.astype('int64'),
                         marker_color='#1dabdd', text=graph_data.astype('int64'),
                         textposition='auto', textfont=dict(
            size=13,color='black'

        ))
                  )

    fig.update_layout(
            xaxis_title='<b>{}<b>'.format(location.capitalize()), yaxis_title='<b>Number of Tweets<b>',
            font=dict(size=13, family='Arial', color='black'), hoverlabel=dict(
                font_size=14, font_family="Rockwell"), plot_bgcolor='#f7f7f7',
            paper_bgcolor='#f7f7f7',margin=dict(l=0, r=0, t=20, b=0)

        )
    fig.update_xaxes(showgrid=False, showline=True, zeroline=False, linecolor='black',visible=True)
    fig.update_yaxes(showgrid=False, showline=True, zeroline=False, linecolor='black',visible=True,showticklabels=True)

    return fig

def create_word_cloud(dfTwitter, dfReddit, source):
    if (source == 'twitter'): 
        arr_token_list = dfTwitter['cleaned_text'].tolist()
    elif (source == 'reddit'):
        arr_token_list = dfReddit['cleaned_text'].tolist()
    else:
        frames = [dfReddit, dfTwitter]
        dfAll = pd.concat(frames)
        arr_token_list = dfAll['cleaned_text'].tolist()

    wc_text = " ".join([str(i) for i in arr_token_list])


    mask = np.array(Image.open(f'./assets/{source}_mask.png'))

    stopwords = set(STOPWORDS)
    stopwords.add("said")
    stopwords.add("will")
    stopwords.add("m")
    stopwords.add("u")
    stopwords.add("s")
    stopwords.add("t")
    stopwords.add("v")
    stopwords.add("ve")
    stopwords.add("dan")
    stopwords.add("nan")
    stopwords.add("chatgpt")


    wordcloud = WordCloud(collocations=False,
                        stopwords=stopwords,
                        background_color='white',
                        mask=mask
                ).generate(wc_text)

    return wordcloud.to_image()
