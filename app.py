# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 12:34:52 2021

@author: user
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output
import plotly.graph_objs as go
import pandas as pd
from datetime import date, datetime
import plotly.express as px
from urllib.request import urlopen
import json
import numpy as np



url_country = 'https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/cases_malaysia.csv'
url_state = 'https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/cases_state.csv'
url_population ='https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/static/population.csv'
url_testing = 'https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/tests_malaysia.csv'
url_malaysia = 'https://query.data.world/s/4gtzoe6nkuueyikifwpsiko5rbqzxl'
url_malaysia_State = 'https://query.data.world/s/64itw4xd4l43sq7n6fwgagvsqcojjd'
url_death_malaysia = 'https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/deaths_malaysia.csv'

#read csv
country = pd.read_csv(url_country)
malaysia = pd.read_csv(url_malaysia)
malaysiastate = pd.read_csv(url_malaysia_State)
state = pd.read_csv(url_state)
population = pd.read_csv(url_population)
testing = pd.read_csv(url_testing)
deaths = pd.read_csv(url_death_malaysia)


#change column date type 
country["date"] = pd.to_datetime(country["date"])
malaysia["date"] = pd.to_datetime(malaysia["date"])
malaysiastate["date"] = pd.to_datetime(malaysiastate["date"])
state["date"] = pd.to_datetime(state["date"])
deaths["date"] = pd.to_datetime(deaths["date"])
testing["date"] = pd.to_datetime(testing["date"])

#column for total cumulative
country['total_cases'] = country['cases_new'].cumsum(axis = 0)
#state['total_case'] = state['cases_new'].cumsum(axis = 0)
deaths['total_deaths'] = deaths['deaths_new'].cumsum(axis = 0)
state["total_cases"]=state.groupby(['state'])['cases_new'].cumsum(axis=0)


#data last updated 
update = country['date'].dt.strftime('%B %d, %Y').iloc[-1]

#important variables
daily_new_cases = country['cases_new'].iloc[-1]
daily_new_death = deaths['deaths_new'].iloc[-1]
total_cases =  country['total_cases'].iloc[-1]
total_death =  deaths['total_deaths'].iloc[-1]
total_recover =  country['cases_recovered'].sum()
total_active = total_cases - total_death- total_recover


dash_colors = {
    'background': '#111111',
    'text': '#BEBEBE',
    'grid': '#333333',
    'red': '#BF0000',
    'blue': '#466fc2',
    'green': '#5bc246'
}


#malaysiastate['state'] = malaysiastate['state'].replace(rename_dict)
country['Rolling Ave.'] = country['cases_new'].rolling(window=7).mean()
deaths['Rolling Ave.'] = deaths['deaths_new'].rolling(window=7).mean()
#state['Rolling Ave.'] = state['cases_new'].rolling(window=7).mean()
state['Rolling Ave.'] = state.groupby('state')['cases_new'].transform(lambda x: x.rolling(7).mean())

current_rate = country['cases_new'].iloc[-7:].sum()/population['pop'].iloc[0] * 100000
#line graph for total cases 


#pie chart value
total_recover = country['cases_recovered'].sum()
colors = ['red', 'chartreuse', 'blue']
active_value = total_cases - total_death - total_recover


#for chloropleth  covid cases spread state 
with urlopen('https://raw.githubusercontent.com/mshumayl/malaysia-vaccination/main/Malaysia.geojson') as response:
    negeri = json.load(response)



state_id_map = {}
for feature in negeri['features']:
    feature['id'] = feature['properties']['id']
    state_id_map[feature['properties']['name']] = feature['id']


map_case_state_df = state
map_case_state_df = pd.merge(population, map_case_state_df, on="state")
map_case_state_df['cases_perpop'] = map_case_state_df['Rolling Ave.']/map_case_state_df['pop'] * 100000
#map_case_state_df = map_case_state_df.groupby(['state','timeframe']).sum().groupby(level=0).cumsum().reset_index()
map_case_state_df['id'] = map_case_state_df['state'].apply(lambda x: state_id_map[x])



def display_choropleth():
    fig = px.choropleth(map_case_state_df, 
                      locations='id', 
                      geojson=negeri, 
                      color='cases_perpop',
                      hover_name='state',
                      labels='Cases per 100k Population',
                      template='plotly_dark',
                      color_continuous_scale="Portland",
                      range_color=(0,100))
    fig.update_geos(fitbounds='locations', visible=False)            
    fig.update_layout(width=1230, height=550, margin={"r":0,"t":0,"l":0,"b":0},title={'text': 'Daily COVID-19 Cases in Malaysia State per 100k Population ('+ update+')',
                   'xanchor': 'center',
                   'yanchor': 'top'}, 
            titlefont={'color': 'white',
                       'size': 15},
            font=dict(family='Roboto Mono',
                      color='white',
                      size=12),title_x = 0.5,title_y = 0.97 )

    return fig


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


### SECTION TWO - LAYOUT ##
app.layout = html.Div( children=[ 

html.Div(children = 'Data last updated: {}'.format(update),style = {
    'textAlign':'left',
    'color': '#dfe7fd'
}),



html.Div([
            html.Img(src=app.get_asset_url('malaysia.png'),
                     id = 'jalurgemilang-image',
                     style={'height': '60px',
                            'width': 'auto',
                            'margin-bottom': '25px',
                            'display' : 'inline'
}),
    

html.H1('COVID-19 MALAYSIA DASHBOARD',
style = {
    'display' : 'inline',
    'textAlign':'center',
    'color' : '#dfe7fd',
    'margin-left': '25px',
    'fontFamily': 'Roboto Mono'

}),

],style={'textAlign':'center'}),


html.Div( children = [html.B(str(int(current_rate)),style = {'color':'#F5CBA7', 'fontSize': 20}),' infection per 100k people reported last 7 days'],style = {
    'textAlign':'center',
    'color': '#dfe7fd'
}),

html.Div([
    
html.Div([
    
    html.H6(children='TOTAL CASES',
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(f"{country['total_cases'].iloc[-1]:,.0f}",
                    style={'textAlign': 'center',
                           'color': 'orange',
                           'fontSize': 40}),
            html.P('new confirmed cases: ' + f"{country['cases_new'].iloc[-1]:,.0f}",
                   style={'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'})
       
        ],className='card_container three columns'),

html.Div([
    
    html.H6(children='TOTAL DEATHS',
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(children = "{:,}".format(deaths['total_deaths'].iloc[-1]),
                    style={'textAlign': 'center',
                           'color': 'crimson',
                           'fontSize': 40}),
            html.P(children = 'new death cases: ' + "{:,}".format(deaths['deaths_new'].iloc[-1]),      
                   style={'textAlign': 'center',
                          'color': 'crimson',
                          'fontSize': 15,
                          'margin-top': '-18px'}),
       

        ],className='card_container three columns') ,

html.Div([
#no data yet
    html.H6(children='TOTAL RECOVERED CASES',
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(children = "{:,}".format(country['cases_recovered'].sum()),
                    style={'textAlign': 'center',
                           'color': 'chartreuse',
                           'fontSize': 40}),
            html.P(children = 'new recovered cases: ' + "{:,}".format(country['cases_recovered'].iloc[-1]),
                   style={'textAlign': 'center',
                          'color': 'chartreuse',
                          'fontSize': 15,
                          'margin-top': '-18px'})
       
        ],className='card_container three columns'),

            
html.Div([
#no data yet  
    html.H6(children='TOTAL ACTIVE CASES',
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(children = "{:,}".format(total_active),
                    style={'textAlign': 'center',
                           'color': 'dodgerblue',
                           'fontSize': 40}),
       
        ],className='card_container three columns'),

],className='row flex-display'),


 html.Div(dcc.RadioItems(id='global_format',
            options=[{'label': i, 'value': i} for i in ['Daily Cases', 'Daily Deaths']],
            value='Daily Cases',
            labelStyle={'float': 'center', 'display': 'inline-block'},
            inputStyle={"margin-right": "20px"}
            ), style={'textAlign': 'center',
                'color': '#dfe7fd',
                'width': '100%',
                'float': 'center',
                'display': 'inline-block',
                'margin-right':2
            }
           
        ),

html.Div([
dcc.Graph(id = 'pie_chart',figure = {'data': [go.Pie(
            labels=['Death', 'Recovered', 'Active'],
            values=[total_death, total_recover, active_value],
            marker=dict(colors=colors),
            hoverinfo='label+value+percent',
            textinfo='label+value',
            hole=.7,
            rotation=45,
            # insidetextorientation= 'radial'

        )],

        'layout': go.Layout(
            title={'text': 'Total Cases: ' + 'Malaysia',
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='Roboto Mono',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            legend={'orientation': 'h',
                    'bgcolor': '#1f2c56',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7}


        )},config={'displayModeBar': 'hover'}

)], className='create_container four columns'),



html.Div([
dcc.Graph(id = 'line_chart',config={'displayModeBar': 'hover'}

)], style={'width': '1500'}, className='create_container seven columns'),


html.Div([dcc.Graph(figure = display_choropleth() )


],className = 'create_container eleven columns'),  


html.Div(dcc.Markdown('''
            &nbsp;  
            &nbsp;  
            Built by [Aisyah Razak (aisyahrazak171@gmail.com)](https://www.linkedin.com/in/aisyahh-razak/)  
            Source data: [MOH Github](https://github.com/MoH-Malaysia/covid19-public)
            View [App Source] (https://github.com/aisyahrzk/covid-19-dashboard)
            '''),
            style={
                'textAlign': 'center',
                'color': '#000000',
                'width': '100%',
                'float': 'center',
                'display': 'inline-block'}
            )

##end of div  
])



### SECTION 3 - Callbacks ###
@app.callback(Output('line_chart', 'figure'),
              [Input('global_format','value')])
def update_graph(global_format):

    if global_format == 'Daily Cases':
        date = country['date']
        show = country['cases_new']
        average = country['Rolling Ave.']
        name_title = 'Daily COVID-19 Cases: Malaysia'
        legend_date = country['date'].astype(str)

    elif global_format == 'Daily Deaths':
        date = deaths['date']
        show = deaths['deaths_new']
        average = deaths['Rolling Ave.']
        name_title = 'Daily Death Cases: Malaysia'
        legend_date = deaths['date'].astype(str)

    return {
        'data': [go.Bar(
            x=date,
            y=show,
            name=name_title,
            marker=dict(color='red'),
            hoverinfo='text',
            hovertext=
            '<b>Date</b>: ' + legend_date + '<br>' +
            '<b>Daily Cases</b>: ' + [f'{x:,.0f}' for x in show] 


        ),
            go.Scatter(
                x=date,
                y=average,
                mode='lines',
                name='Rolling Average of the last 7 days',
                line=dict(width=3, color='#FF00FF'),
                hoverinfo='text',
                hovertext=
                '<b>Date</b>: ' + legend_date + '<br>' +
                '<b>Rolling Average Daily Confirmed Cases</b>: ' + [f'{x:,.0f}' for x in average] 


            )],

        'layout': go.Layout(
            title={'text': name_title,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='Roboto Mono',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={'orientation': 'h',
                    'bgcolor': '#1f2c56',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(r=0),
            xaxis=dict(title='<b>Date</b>',
                       color = 'white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Roboto Mono',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title='<b>Daily Confirmed Cases</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Roboto Mono',
                           color='white',
                           size=12
                       )
                       )


        )
    }




# automatically update HTML display if a change is made to code
if __name__ == '__main__':
    
    server = app.server
    