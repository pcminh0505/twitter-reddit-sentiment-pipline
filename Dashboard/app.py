# import pandas
import pandas as pd
import os
import base64
import datetime as dt
import dash
from dash import dcc
from dash import html
import dash.dependencies as dd
import dash_bootstrap_components as dbc
from io import BytesIO
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from scipy.stats import rayleigh
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import iplot
from plotly.subplots import make_subplots
from datetime import datetime

from s3bucket import *
import charts

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

'''
giving a title to the app to be displayed in browser tab
'''
app.title='Twitter & Reddit ChatGPT Sentiment Analysis'
'''
giving a flexibility to callback functions to exist even if the layout changes
'''
app.config.suppress_callback_exceptions = True

server = app.server

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

DATA_FOLDER = os.path.normpath(os.getcwd() + os.sep + os.pardir + "/Bucket/")
twitter_file=os.path.join(DATA_FOLDER, 'processed-twitter-latest.csv')
reddit_file=os.path.join(DATA_FOLDER, 'processed-reddit-latest.csv')

# twitter_key = 'processed-twitter-latest.csv'
# reddit_key = 'processed-reddit-latest.csv'

now = datetime.now()

current_time = now.strftime("%YY/%mm/%DD/%HH")
print("Current Time =", current_time)   

df = getOfflineDF(twitter_file)
dfReddit = getOfflineDF(reddit_file)

# df = getOfflineDF(getOfflineFilePath(twitter_key))
# dfReddit = getOfflineDF(getOfflineFilePath(reddit_key))

'''
##### layout creation starts here
'''

'''
creating the app header text
'''
header_text=html.H2('Twitter and Reddit',id='main_header_text',className='main-header',
                     style=dict(
                     fontWeight='bold',width='100%',paddingTop='2vh',
                     display= 'flex', alignItems= 'center', justifyContent= 'center'))

header_text_dashboard=html.H2('Sentiment Analysis Dashboard',id='main_header_text_sentiment',className='main-header',
                     style=dict(
                     fontWeight='bold',width='100%',paddingTop='1vh',
                     display= 'flex', alignItems= 'center', justifyContent= 'center'))
'''
creating the header of number of tweets box
'''
tweets_num_text= html.Div(html.H5('Total Number of Tweets',className= 'info-header',id='tweets_num_text',
                                    style=dict(fontWeight='bold', color='black')),
                            style=dict( textAlign="center", width='100%'))

'''
getting total no. tweets from the dataframe
'''
tweets_num=df['tweet_id'].count()

'''
creating an indicator figure and adding it to dash graph component to show total no. tweets
'''

tweets_num_fig = go.Figure()

indicator_size=27
tweets_num_fig.add_trace(go.Indicator(
    mode = "number",
    value = tweets_num,
    number={'font':{'color':'#1dabdd','size':indicator_size},'valueformat':","},
    domain={'row':0,'column':0}
))

tweets_num_fig.update_layout(paper_bgcolor = "#f7f7f7",plot_bgcolor='white',height=40,margin=dict(l=0, r=0, t=0, b=0),

                  )

tweets_num_indicator=html.Div(dcc.Graph(figure=tweets_num_fig,config={'displayModeBar': False},id='tweets_num_indicator',style=dict(width='100%')),className='num'
                           , style=dict(width='100%')  )


'''
creating the header of average no. retweets box
'''

retweets_avg_text= html.Div(html.H5('Average Number of Retweets',className= 'info-header',id='retweets_avg_text',
                                    style=dict(fontWeight='bold', color='black')),
                            style=dict(textAlign="center", width='100%'))

'''
getting average no. retweets from the dataframe
'''
retweets_avg=round(df['retweet_count'].mean() , 1)

'''
creating an indicator figure and adding it to dash graph component to show average no. retweets
'''

retweets_avg_fig = go.Figure()

retweets_avg_fig.add_trace(go.Indicator(
    mode = "number",
    value = retweets_avg,
    number={'font':{'color':'#1dabdd','size':indicator_size}},
   domain={'row':0,'column':0}
))

retweets_avg_fig.update_layout(paper_bgcolor = "#f7f7f7",plot_bgcolor='white',height=40,margin=dict(l=0, r=0, t=0, b=0),

                  )

retweets_avg_indicator=html.Div(dcc.Graph(figure=retweets_avg_fig,config={'displayModeBar': False},id='retweets_avg_indicator',style=dict(width='100%')),className='num'
                           , style=dict(width='100%')  )

'''
creating the header of average no. likes box
'''
likes_avg_text= html.Div(html.H5('Average Number of Likes',className= 'info-header',id='likes_avg_text',
                                    style=dict(fontWeight='bold', color='black')),
                            style=dict(textAlign="center", width='100%'))

'''
getting average no. likes from the dataframe
'''

likes_avg=int(df['like_count'].mean() )

'''
creating an indicator figure and adding it to dash graph component to show average no. likes
'''
likes_avg_fig = go.Figure()

likes_avg_fig.add_trace(go.Indicator(
    mode = "number",
    value = likes_avg,
    number={'font':{'color':'#1dabdd','size':indicator_size}},
   domain={'row':0,'column':0}
))

likes_avg_fig.update_layout(paper_bgcolor = "#f7f7f7",plot_bgcolor='white',height=40,margin=dict(l=0, r=0, t=0, b=0),

                  )

likes_avg_indicator=html.Div(dcc.Graph(figure=likes_avg_fig,config={'displayModeBar': False},id='likes_avg_indicator',style=dict(width='100%')),className='num'
                           , style=dict(width='100%')  )

'''
creating the header of average no. replies box
'''
replies_avg_text= html.Div(html.H5('Average Number of Replies',className= 'info-header',id='replies_avg_text',
                                    style=dict(fontWeight='bold', color='black')),
                            style=dict(textAlign="center", width='100%'))

'''
getting average no. replies from the dataframe
'''
replies_avg=int(df['reply_count'].mean() )

'''
creating an indicator figure and adding it to dash graph component to show average no. replies
'''
replies_avg_fig = go.Figure()

replies_avg_fig.add_trace(go.Indicator(
    mode = "number",
    value = replies_avg,
    number={'font':{'color':'#1dabdd','size':indicator_size}},
   domain={'row':0,'column':0}
))

replies_avg_fig.update_layout(paper_bgcolor = "#f7f7f7",plot_bgcolor='white',height=40,margin=dict(l=0, r=0, t=0, b=0),

                  )

replies_avg_indicator=html.Div(dcc.Graph(figure=replies_avg_fig,config={'displayModeBar': False},id='replies_avg_indicator',style=dict(width='100%')),className='num'
                           , style=dict(width='100%')  )


'''
creating the header of total no. countries box
'''
countries_num_text= html.Div(html.H5('Total Number of Countries',className= 'info-header',id='countries_num_text',
                                    style=dict(fontWeight='bold', color='black')),
                            style=dict(textAlign="center", width='100%'))


'''
getting total no. countries from the dataframe
'''
countries_num=int(df['country'].nunique() )

'''
creating an indicator figure and adding it to dash graph component to show total no. countries
'''
countries_num_fig = go.Figure()

countries_num_fig.add_trace(go.Indicator(
    mode = "number",
    value = countries_num,
    number={'font':{'color':'#1dabdd','size':indicator_size},'valueformat':","},
   domain={'row':0,'column':0}
))

countries_num_fig.update_layout(paper_bgcolor = "#f7f7f7",plot_bgcolor='white',height=40,margin=dict(l=0, r=0, t=0, b=0),

                  )

countries_num_indicator=html.Div(dcc.Graph(figure=countries_num_fig,config={'displayModeBar': False},id='countries_num_indicator',style=dict(width='100%')),className='num'
                           , style=dict(width='100%')  )

'''
creating the header of number of tweets box
'''
reddit_num_text= html.Div(html.H5('Total Number of Reddit Posts',className= 'info-header',id='reddit_num_text',
                                    style=dict(fontWeight='bold', color='black')),
                            style=dict( textAlign="center", width='100%'))

'''
getting total no. tweets from the dataframe
'''
reddit_num=dfReddit['reddit_id'].count()

'''
creating an indicator figure and adding it to dash graph component to show total no. tweets
'''

reddit_num_fig = go.Figure()

indicator_size=27
reddit_num_fig.add_trace(go.Indicator(
    mode = "number",
    value = reddit_num,
    number={'font':{'color':'#FF4500','size':indicator_size},'valueformat':","},
    domain={'row':0,'column':0}
))

reddit_num_fig.update_layout(paper_bgcolor = "#f7f7f7",plot_bgcolor='white',height=40,margin=dict(l=0, r=0, t=0, b=0),

                  )

reddit_num_indicator=html.Div(dcc.Graph(figure=reddit_num_fig,config={'displayModeBar': False},id='reddit_num_indicator',style=dict(width='100%')),className='num'
                           , style=dict(width='100%')  )


'''
creating the header of average no. upvots box
'''

upvotes_avg_text= html.Div(html.H5('Average Number of Upvotes',className= 'info-header',id='upvotes_avg_text',
                                    style=dict(fontWeight='bold', color='black')),
                            style=dict(textAlign="center", width='100%'))

'''
getting average no. upvotes from the dataframe
'''
upvotes_avg=round(dfReddit['up_votes'].mean() , 1)

'''
creating an indicator figure and adding it to dash graph component to show average no. upvotes
'''

upvotes_avg_fig = go.Figure()

upvotes_avg_fig.add_trace(go.Indicator(
    mode = "number",
    value = upvotes_avg,
    number={'font':{'color':'#FF4500','size':indicator_size}},
   domain={'row':0,'column':0}
))

upvotes_avg_fig.update_layout(paper_bgcolor = "#f7f7f7",plot_bgcolor='white',height=40,margin=dict(l=0, r=0, t=0, b=0),

                  )

upvotes_avg_indicator=html.Div(dcc.Graph(figure=upvotes_avg_fig,config={'displayModeBar': False},id='upvotes_avg_indicator',style=dict(width='100%')),className='num'
                           , style=dict(width='100%')  )


'''
##### Number of Tweets Over Days
creating header of the line chart graph
'''
date_chart_header= html.Div(html.H5('Number of Tweets Over Days',className= 'date-chart-header',id='date_chart_header',
                                    style=dict( fontWeight='bold', color='black')),
                            style=dict(textAlign="center", width='100%'))

'''
creating the line chart graph component ( filled with empty figure in beginning to be updated from the callback
when app starts depending on topics dropdown menu value )
'''
date_chart=go.Figure(charts.date_chart(df, dfReddit, 'twitter'))
date_chart_div=html.Div([
            dcc.Graph(id='date_chart', config={'displayModeBar': True,'displaylogo': False,'modeBarButtonsToRemove': ['lasso2d','pan']},className='date-fig',
                style=dict(backgroundColor='#f7f7f7') ,figure=date_chart
            ) ] ,id='date_chart_div'
        )

'''
##### Number of Tweets Over Days
creating header of the line chart graph
'''
date_chart_header_reddit= html.Div(html.H5('Number of Reddit posts Over Days',className= 'date-chart-header',id='date_chart_header_reddit',
                                    style=dict( fontWeight='bold', color='black')),
                            style=dict(textAlign="center", width='100%'))

'''
creating the line chart graph component ( filled with empty figure in beginning to be updated from the callback
when app starts depending on topics dropdown menu value )
'''
date_chart_reddit=go.Figure(charts.date_chart(df, dfReddit, 'reddit'))
date_chart_div_reddit=html.Div([
            dcc.Graph(id='date_chart_reddit', config={'displayModeBar': True,'displaylogo': False,'modeBarButtonsToRemove': ['lasso2d','pan']},className='date-fig',
                style=dict(backgroundColor='#f7f7f7') ,figure=date_chart_reddit
            ) ] ,id='date_chart_div_reddit'
        )

'''
##### Top 5 Cities With Tweets
creating header of the vertical bar chart graph 
'''
ver_bar_chart_header= html.Div(html.H5('Top 5 Cities With Tweets',className= 'date-chart-header',id='ver_bar_chart_header',
                                    style=dict( fontWeight='bold', color='black')),
                            style=dict(textAlign="center", width='100%'))

'''
creating a countries/cities radio button to choose from for the vertical bar chart
'''
location_filter = html.Div(
    [
        dbc.RadioItems( options=[ {"label": "Countries", "value": 'country'},
                                  {"label": "Cities", "value": 'city'},],
            value='city',
            id="location_filter",
            inline=True, label_class_name='filter-label',input_class_name='filter-button',input_checked_class_name='filter-button-checked' ,
            input_checked_style=dict(backgroundColor='#1dabdd',border='2px solid #1dabdd')
        )
    ])

'''
creating the vertical bar chart graph component where we got the figure from charts.py function
( filled with empty figure in beginning to be updated from the callback
when app starts depending on countries/cities radio buttons selected )
'''
ver_bar_chart=go.Figure(go.Bar())
ver_bar_chart_div=html.Div([
            dcc.Graph(id='ver_bar_chart', config={'displayModeBar': True,'displaylogo': False,
                                          'modeBarButtonsToRemove': ['lasso2d','pan','zoom2d','zoomIn2d','zoomOut2d','autoScale2d']}
                      ,className='ver-bar-fig',
                style=dict(backgroundColor='#f7f7f7') ,figure=ver_bar_chart
            ) ] ,id='ver_bar_chart_div'
        )

freq_chart_header = html.Div(html.H5('Top Frequency terms from Twitter',className= 'date-chart-header',id='freq_chart_header',
                                    style=dict( fontWeight='bold', color='black')),
                            style=dict(textAlign="center", width='100%'))
freq_chart=go.Figure(go.Bar())
freq_filter = html.Div(
    [
        dbc.RadioItems( options=[ {"label": "Twitter", "value": 'twitter'},
                                  {"label": "Reddit", "value": 'reddit'},
                                  {"label": "Both", "value": 'both'}
                                  ],
            value='twitter',
            id="freq_filter",
            inline=True, label_class_name='filter-label',input_class_name='filter-button',input_checked_class_name='filter-button-checked' ,
            input_checked_style=dict(backgroundColor='#1dabdd',border='2px solid #1dabdd')
        ),
    ], style=(dict(display='flex', justifyContent='center'))
)
freq_chart_div=html.Div([
            dcc.Graph(id='freq_chart', config={'displayModeBar': True,'displaylogo': False,
                                          'modeBarButtonsToRemove': ['lasso2d','pan','zoom2d','zoomIn2d','zoomOut2d','autoScale2d']}
                      ,className='ver-bar-fig',
                style=dict(backgroundColor='#f7f7f7') ,figure=freq_chart
            ) ] ,id='freq_chart_div'
        )

word_cloud_header = html.Div(html.H5('WordCloud by Twitter',className= 'date-chart-header',id='wc_header',
                                    style=dict( fontWeight='bold', color='black')),
                            style=dict(textAlign="center", width='100%'))

wc_source_filter = html.Div(
    [
        dbc.RadioItems( options=[ {"label": "Twitter", "value": 'twitter'},
                                  {"label": "Reddit", "value": 'reddit'},
                                  {"label": "Both", "value": 'both'}
                                  ],
            value='twitter',
            id="wc_source_filter",
            inline=True, label_class_name='filter-label',input_class_name='filter-button',input_checked_class_name='filter-button-checked' ,
            input_checked_style=dict(backgroundColor='#1dabdd',border='2px solid #1dabdd')
        ),
    ], style=(dict(display='flex', justifyContent='center'))
)
word_cloud_chart = html.Img(id="image_wc", style=dict(height="500px"))
word_cloud_chart_div=html.Div([
            word_cloud_chart,
        ], id='word-cloud_div', style=dict(display='flex',justifyContent='center', marginTop=10))

'''
adding all of the app components in app.layout object 
the design made using dash-bootstrap columns , rows and cards
'''
main_layout=html.Div([
                    dbc.Row(header_text,id='main_header'),
                    dbc.Row(header_text_dashboard,id='main_header_dashboard'),

                    html.Br(),

                    dbc.Row([
                        html.Div([

                        dbc.Card(dbc.CardBody([tweets_num_text,
                                                      dbc.Spinner([tweets_num_indicator], size="lg", color="primary",
                                                                  type="border", fullscreen=False,
                                                                  spinner_style=dict(marginTop=''))

                                                      ])
                                        , style=dict(backgroundColor='#f7f7f7', width='200px'), id='card1',
                                        className='info-card'),


                        dbc.Card(dbc.CardBody([retweets_avg_text,
                                                      dbc.Spinner([retweets_avg_indicator], size="lg", color="primary",
                                                                  type="border", fullscreen=False,
                                                                  spinner_style=dict(marginTop=''))

                                                      ])
                                        , style=dict(backgroundColor='#f7f7f7',width='200px', marginLeft='1vw'), id='card2',
                                        className='info-card'),

                        dbc.Card(dbc.CardBody([likes_avg_text,
                                                        dbc.Spinner([likes_avg_indicator], size="lg",
                                                                    color="primary",
                                                                    type="border", fullscreen=False,
                                                                    spinner_style=dict(marginTop=''))

                                                        ])
                                          , style=dict(backgroundColor='#f7f7f7',width='200px', marginLeft='1vw'), id='card4',
                                          className='info-card'),

                        dbc.Card(dbc.CardBody([replies_avg_text,
                                                        dbc.Spinner([replies_avg_indicator], size="lg",
                                                                    color="primary",
                                                                    type="border", fullscreen=False,
                                                                    spinner_style=dict(marginTop=''))

                                                        ])
                                          , style=dict(backgroundColor='#f7f7f7',width='200px', marginLeft='1vw'), id='card5',
                                          className='info-card'),

                        dbc.Card(dbc.CardBody([countries_num_text,
                                                        dbc.Spinner([countries_num_indicator], size="lg",
                                                                    color="primary",
                                                                    type="border", fullscreen=False,
                                                                    spinner_style=dict(marginTop=''))

                                                        ])
                                          , style=dict(backgroundColor='#f7f7f7',width='200px', marginLeft='1vw'), id='card6',
                                          className='info-card'),

                        dbc.Card(dbc.CardBody([reddit_num_text,
                                                      dbc.Spinner([reddit_num_indicator], size="lg", color="primary",
                                                                  type="border", fullscreen=False,
                                                                  spinner_style=dict(marginTop=''))
                                                      ])
                                        , style=dict(backgroundColor='#f7f7f7', width='200px', marginLeft='1vw'), id='card7',
                                        className='info-card'),

                        dbc.Card(dbc.CardBody([upvotes_avg_text,
                                                      dbc.Spinner([upvotes_avg_indicator], size="lg", color="primary",
                                                                  type="border", fullscreen=False,
                                                                  spinner_style=dict(marginTop=''))
                                                      ])
                                        , style=dict(backgroundColor='#f7f7f7',width='200px', marginLeft='1vw'), id='card8',
                                        className='info-card'),

                        ],style=dict(display= 'flex', alignItems= 'center',
                                    justifyContent= 'center', width='100%', flex='wrap'))
                    ]),

                        
                    html.Br(),

                    dbc.Row([
                        dbc.Col([dbc.Card(dbc.CardBody([date_chart_header_reddit,
                                                        dbc.Spinner([date_chart_div_reddit], size="lg", color="primary", type="border",
                                                                    fullscreen=False)
                                                        ])
                                    , style=dict(backgroundColor='#f7f7f7'), id='card10',
                                    className='charts-card'), html.Br()
                            ], lg=dict(size=6, offset=0),
                        md=dict(size=12, offset=0),
                        style=dict(paddingLeft='0.5vw',paddingRight='0.5vw')),

                        dbc.Col([dbc.Card(dbc.CardBody([date_chart_header,
                                                        dbc.Spinner([date_chart_div], size="lg", color="primary", type="border",
                                                                    fullscreen=False)
                                                        ])
                                    , style=dict(backgroundColor='#f7f7f7'), id='card9',
                                    className='charts-card'), html.Br()
                            ], lg=dict(size=6, offset=0),
                        md=dict(size=12, offset=0),
                        style=dict(paddingLeft='0.5vw',paddingRight='0.5vw')),
                    ]),

                    dbc.Row([
                        dbc.Col([dbc.Card(dbc.CardBody([
                                                        freq_chart_header,
                                                        freq_filter,
                                                        dbc.Spinner([freq_chart_div], size="lg", color="primary",
                                                                    type="border",
                                                                    fullscreen=False)
                                                        ])
                                            , style=dict(backgroundColor='#f7f7f7'), id='card11',
                                            className='charts-card'), html.Br()
                                    ], lg=dict(size=6, offset=0),
                                    md=dict(size=12, offset=0),
                                    style=dict(paddingLeft='0.5vw',paddingRight='0.5vw')),

                        dbc.Col([dbc.Card(dbc.CardBody([
                                                        ver_bar_chart_header,
                                                        location_filter,
                                                        dbc.Spinner([ver_bar_chart_div], size="lg", color="primary",
                                                                    type="border",
                                                                    fullscreen=False)
                                                        ])
                                            , style=dict(backgroundColor='#f7f7f7'), id='card12',
                                            className='charts-card'), html.Br()
                                    ], lg=dict(size=6, offset=0),
                                    md=dict(size=12, offset=0),
                                    style=dict(paddingLeft='0.5vw',paddingRight='0.5vw')),
                    ]),

                    dbc.Row(
                        [word_cloud_header,
                        wc_source_filter,
                        dbc.Spinner([word_cloud_chart_div], size="lg", color="primary",
                                    type="border",
                                    fullscreen=False)
                        ], style=dict(display='flex',justifyContent='center'))
                ], style=dict(marginLeft=20,marginRight=20))


app.layout = main_layout

'''
updating the vertical bar chart depending on radio button selected
'''
@app.callback([Output('ver_bar_chart','figure'),Output('ver_bar_chart_header','children')],
              Input('location_filter','value'))
def update_ver_bar_chart(selected_location):
    # checking if user choosed countries or cities and set the loc parameter that will be sent to the charts.py function according to it
    if selected_location=='city':
        loc='Cities'

    elif selected_location=='country':
        loc='Countries'

    return (charts.create_ver_bar(df,selected_location), 'Top 5 {} With Tweets'.format(loc))


'''
updating the freq bar chart depending on radio button selected
'''
@app.callback([Output('freq_chart','figure'),Output('freq_chart_header','children')],
              Input('freq_filter','value'))
def update_freq_chart(source):
    if source=='twitter':
        loc='Twitter'

    elif source=='reddit':
        loc='Reddit'
    else: 
        loc='Twitter and Reddit'

    return (charts.create_freq_bar(df, dfReddit, source), 'Top Frequency Terms From {}'.format(loc))

@app.callback([dd.Output('image_wc', 'src'), Output('wc_header','children')], [dd.Input('image_wc', 'id'), Input('wc_source_filter','value')])
def make_image(b, source):

    if source=='twitter':
        loc='Twitter'

    elif source=='reddit':
        loc='Reddit'
    else: 
        loc='Twitter and Reddit'

    img = BytesIO()
    charts.create_word_cloud(df, dfReddit, source).save(img, format='PNG')
    return (('data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())), 
                'WordCloud from {}'.format(loc))


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)


