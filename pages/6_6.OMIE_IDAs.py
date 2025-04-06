import streamlit as st
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from datetime import datetime

import pandas as pd
import json

import plotly.graph_objects as go


with st.sidebar:
    
    multi_toggle = st.toggle("Multi day selection", False, key = "multi_day_selection", disabled = True)

    if not multi_toggle:
        st.session_state.end_day_selection = st.session_state.start_day_selection
    start_date = st.date_input("start date", st.session_state.start_day_selection, key = "start_day_selection")
    end_date = st.date_input("end date", st.session_state.end_day_selection, key = "end_day_selection", disabled = not (st.session_state.multi_day_selection))
    
    net_buysell_selector = st.toggle("Net buy/sells", True)

    ida_session = st.radio(
        "IDA",
        key="visibility",
        options=[1, 2, 3],
    )

    

# Scrape data from OMIE IDAs
def scrape_omie_ida(date, session):

    year = date.year
    month = date.month
    day = date.day

    s = HTMLSession()
    url = f"https://www.omie.es/es/market-results/daily/ida-market/power-ida-market?scope=daily&date={year}-{month}-{day}&system=9&session={session}"

    r = s.get(url)
    # r.html.render
    soup = BeautifulSoup(r.html.html, 'html.parser')
    
    return soup

def parse_omie_ida(soup):
    
    mydivs = soup.find_all("div", {"class": "charts-highchart chart"})
    mydivs_str = str(mydivs[0])
    mydivs_separated = mydivs_str.split('"id "')
    mydivs_separated = mydivs_separated[1:]

    # Extract the JSON data from the div string
    data_json = json.loads(mydivs[0]['data-chart'])
    # Eliminate all elements except 'series' from the JSON data
    data_json = {'series': data_json['series']}
    # Extract the 'name' and the first letter of 'id ' from each series in the JSON data into a pandas dataframe
    names_and_ids = [(series['name'], series['id '][0]) for series in data_json['series']]
    df_names_and_ids = pd.DataFrame(names_and_ids, columns=['tech', 'V or C'])

    # Extract the 'data' from each series in the JSON data
    data = [series['data'] for series in data_json['series']]

    # Add new columns named 1 to 24 and fill with data
    for i in range(1, 25):
        df_names_and_ids[str(i)] = [series['data'][i-1] if i-1 < len(series['data']) else None for series in data_json['series']]

    # df_names_and_ids.to_excel(f'OMIE_{year}_{month}_{day}_session_{session}.xlsx', index=False)
    return df_names_and_ids

def plot_IDA_buysell(df:pd.DataFrame, date: datetime, session: int, net_power= net_buysell_selector):
    
    year = date.year
    month = date.month
    day = date.day
    
  
    fig = go.Figure()

    if net_power:
        for tech in df['tech'].unique():
            df_tech = df[df['tech'] == tech]
            fig.add_trace(go.Bar(
                x=df_tech['Hour'],
                y=df_tech['net_power'],
                name=tech
            ))
        title_net_str = 'NET ' 
    else:
        for tech in df_melted['tech'].unique():
            df_tech = df[df['tech'] == tech]
            fig.add_trace(go.Bar(
                x=df_tech['Hour'],
                y=df_tech['power'],
                name=tech
            ))
        title_net_str = '' 
    
    title = f'IDA buy/sell {title_net_str}by technology - {year}-{month}-{day} - Session {session}'
      
    fig.update_layout(
        barmode='relative',
        title= title,
        plot_bgcolor='white',
        xaxis=dict(
            title='Hour',
            tickmode='linear'
        ),
        yaxis=dict(
            title='Power',
            dtick=250,
            gridcolor = 'LightGray'
        )
    )

    opacity_float = 0.07
    fig.add_vrect(x0=0.5, x1=6.5, 
                fillcolor="blue", opacity=opacity_float, line_width=0)
    fig.add_vrect(x0=6.5, x1=9.5, 
                fillcolor="grey", opacity=opacity_float, line_width=0)
    fig.add_vrect(x0=9.5, x1=19.5, 
                fillcolor="#eff54c", opacity=opacity_float, line_width=0) # slightly modified yellow. More mellow, otherwise it's too intrusive
    fig.add_vrect(x0=19.5, x1=24.5, 
                fillcolor="grey", opacity=opacity_float, line_width=0)

    # Update the color for Comercializador/Cons. directo
    for trace in fig.data:
        if trace.name == 'Renovables':
            trace.marker.color = '#9FC259'
        elif trace.name == 'Ciclo combinado':
            trace.marker.color = '#898888'
        elif trace.name == 'Comercializador/Cons. directo':
            trace.marker.color = '#E8CD64'
        elif trace.name == 'Carbón':
            trace.marker.color = '#686969'
        elif trace.name == 'Hidráulica':
            trace.marker.color = '#73AECB'
        elif trace.name == 'Consumo bombeo':
            trace.marker.color = '#EEE0A3'
        elif trace.name == 'Nuclear':
            trace.marker.color = '#b8b4d4'
        
    # fig.update_layout(barmode='relative')


    # fig.update_yaxes(range=[-2100, 2100])
    fig.update_traces(opacity=1)
    fig.update_xaxes(
        tickvals=[i for i in range(1, 25)],
        categoryorder='array',
        categoryarray=[str(i) for i in range(1, 25)]
    )
    
    fig.update_layout(
        height = 800
    )
    
    fig.update_xaxes(tickfont=dict(size=20))

    fig.update_yaxes(tickfont=dict(size=20))
    
    fig.update_layout(
    legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1,
                xanchor="left",x=0,
                font=dict(size=20),itemwidth=30),
    )
    
    # fig.update_legends(tickfont=dict(size=20))
        # add title
    fig.update_layout(
        title=dict(text=title, font=dict(size=30), automargin=False, yref='paper')
    )
    return fig


soup = scrape_omie_ida(start_date, ida_session)
df = parse_omie_ida(soup)

df_melted = pd.melt(df, id_vars=['tech', 'V or C'], var_name='Hour', value_name='power')

df_melted = df_melted.fillna(0)
df_melted['Hour'] = df_melted['Hour'].astype(int)   


if net_buysell_selector:
    df_net = df_melted.pivot_table(index=['Hour', 'tech'], columns='V or C', values='power', aggfunc='first').reset_index()
    df_net['net_power'] = df_net['V'] + df_net['C']
    df_obj = df_net
else:
    df_obj = df_melted

fig = plot_IDA_buysell(df_obj, date=start_date, session = ida_session, net_power=net_buysell_selector)

st.plotly_chart(fig, use_container_width = True)

st.dataframe(df, hide_index = True)

