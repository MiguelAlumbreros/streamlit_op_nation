import streamlit as st

import pandas as pd
from datetime import datetime
from datetime import timedelta

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# add path to get the functions from the file that access the API
import sys
sys.path.insert(0, r'Z:\04. Dispatching\04. Turno\05. Carpetas personales\Miguel\Github\query_SQL')
import query_SQL


with st.sidebar:
    
    multi_toggle = st.toggle("Multi day selection", st.session_state.multi_day_selection, key = "multi_day_selection")

    if not multi_toggle:
        st.session_state.end_day_selection = st.session_state.start_day_selection
    start_date = st.date_input("start date", st.session_state.start_day_selection, key = "start_day_selection")
    end_date = st.date_input("end date", st.session_state.end_day_selection, key = "end_day_selection", disabled = not (st.session_state.multi_day_selection))

    tech_list = ['All', 'Wind', 'Solar']
    terc_list = ['All', 'SSAA', 'NO_SSAA']

    tech_selection = st.selectbox(label = 'Technology', options = tech_list)
    terc_selection = st.selectbox(label = 'TERC', options = terc_list)

# create list of days between date selections
date_list = []
date = start_date
while date <= end_date:
    date_list.append(date)
    date = date + timedelta(days = 1)

# create mapping of selectbox inputs to query parameters
if tech_selection == 'All':
    query_tech_option = 'NULL'
elif tech_selection == 'Wind':
    query_tech_option = '8'
else:
    query_tech_option = '13'

if terc_selection == 'All':
    query_terc_option = 'NULL'
elif terc_selection == 'SSAA':
    query_terc_option = '1'
else:
    query_terc_option = '0'

 

# # concat output
df_list = []
for date in date_list:
    df_temp = query_SQL.query_desvios_portfolio(date = date, option_tech=query_tech_option, option_terc=query_terc_option)
    df_list.append(df_temp)
df_merge = pd.concat(df_list)

st.write("""
# Portfolio desvíos
""")

# st.plotly_chart(fig, use_container_width = True)

# display the dataframe on streamlit app

df_merge['Fecha'] = pd.to_datetime(df_merge['Fecha'])

df_temp = df_merge.melt(id_vars = ['Fecha', 'var'], value_vars=df_merge.columns.to_list(), var_name='period',value_name='MWh')

def get_datetime(row):
    ts = row['Fecha']
    hour = int (row['period'][1:]) - 1
    return datetime(year = ts.year, month = ts.month, day = ts.day, hour = hour)

df_temp['datetime'] = df_temp.apply(get_datetime, axis = 1)
df_temp = df_temp.sort_values(by = 'datetime')

def plot_portfolio_desvios(df: pd.DataFrame):
    """plots desvios portfolio

    Args:
        df (pd.DataFrame): [Fecha	var	period	MWh	datetime],
        with var = ['Measurement', 'Forecast', 'p48', 'imbalance']

    Returns:
        _type_: _description_
    """
    df_meas = df.query('var == "Measurement"')
    df_fore = df.query('var == "Forecast"')
    df_p48 = df.query('var == "p48"')
    df_imba = df.query('var == "imbalance"')
    # plot


    trace1 = trace1 = go.Scatter(
    x=df_meas['datetime'],
    y=df_meas['MWh'],
    name='Measurement',
    marker=dict(
        color='#1f8503'
               ),
    line_shape='spline'
    )

    trace2 = go.Scatter(
        x=df_fore['datetime'],
        y=df_fore['MWh'],name='Forecast',
        marker=dict(
            color='#cf0a11'
                ),
        line_shape='spline'
    )


    trace3 = go.Scatter(
        x=df_p48['datetime'],
        y=df_p48['MWh'],
        name='p48',
        marker=dict(    
            color='#faf202'
                ),
        line_shape='spline'
    )

    trace4 = go.Bar(
        x=df_imba['datetime'],
        y=df_imba['MWh'],
        name='imbalance',
        yaxis='y2',
        opacity = 0.3,
        marker=dict(
        color='#1f07f5'
                )
    )



    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = go.Figure()
    fig.update_layout(template="plotly_white")


    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.add_trace(trace3)
    
    fig.update_traces(line=dict(width=4))


    fig.add_trace(trace4)

    # place legend in the top left (horizontal)
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ))


    for date in df['Fecha'].dt.date.unique():
        fig.add_vline(x = date, line_width=1.5, )

        # separate parts by color
            # valley = blue
            # 1 shoulder = 
            # solar = yellow
            # 2 shoulder = green
        
        opacity_float = 0.1
        
        fig.add_vrect(x0=date, x1=f"{date} 5:00", 
                    #   annotation_text="decline", annotation_position="top left",
                    fillcolor="blue", opacity=opacity_float, line_width=0)
        fig.add_vrect(x0=f"{date} 5:00", x1=f"{date} 8:00", 
                    #   annotation_text="decline", annotation_position="top left",
                    fillcolor="grey", opacity=opacity_float, line_width=0)
        fig.add_vrect(x0=f"{date} 8:00", x1=f"{date} 18:00", 
                    #   annotation_text="decline", annotation_position="top left",
                    fillcolor="yellow", opacity=opacity_float, line_width=0)
        fig.add_vrect(x0=f"{date} 18:00", x1=f"{date + timedelta(days=1)} 00:00", 
                    #   annotation_text="decline", annotation_position="top left",
                    fillcolor="grey", opacity=opacity_float, line_width=0)
    return fig

fig = plot_portfolio_desvios(df_temp)
font_size = 19
fig.update_layout(xaxis_tickfont_size = font_size, yaxis_tickfont_size = font_size, yaxis2_tickfont_size = font_size)

st.plotly_chart(fig, use_container_width = True)

# plot df
st.dataframe(df_merge.set_index('Fecha').sort_values(by = 'Fecha'))

# download button on the sidebar
with st.sidebar:
    from io import BytesIO
    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        format1 = workbook.add_format({'num_format': '0.00'}) 
        worksheet.set_column('A:A', None, format1)  
        writer.close()
        processed_data = output.getvalue()
        return processed_data
    df_xlsx = to_excel(df_merge)
    st.download_button(label='📥 Download data as XLSX',
                                    data=df_xlsx ,
                                    file_name= 'df_portfolio_desvios.xlsx')