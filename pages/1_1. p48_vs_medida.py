import streamlit as st
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

#create sidebar with toggles
with st.sidebar:
    
    multi_toggle = st.toggle("Multi day selection", st.session_state.multi_day_selection, key = "multi_day_selection")

    if not multi_toggle:
        st.session_state.end_day_selection = st.session_state.start_day_selection
    start_date = st.date_input("start date", st.session_state.start_day_selection, key = "start_day_selection",
                               min_value = datetime(2024,6,1), max_value=datetime(2024,6,30))
    end_date = st.date_input("end date", st.session_state.end_day_selection, key = "end_day_selection", 
                             min_value = datetime(2024,6,1), max_value=datetime(2024,6,30), 
                             disabled = not (st.session_state.multi_day_selection))


# read input dataset
df = pd.read_csv('./data/1_data.csv', sep = ",")
df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
df['date'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')

del df['date']

df = df[(df['datetime'] >= datetime(start_date.year, start_date.month, start_date.day)) & (df['datetime'] < datetime(end_date.year, end_date.month, end_date.day) + timedelta(days = 1))]      
          
fig_var_list = [['Wind', 'p48_wind', 'medida_wind', 'dif_wind'],
                ['Solar','p48_solar', 'medida_solar', 'dif_solar'],
                ['Demand','p48_demand', 'medida_demand', 'dif_demand']] # 3 lists for 3 figures. 0: title, 1: var p48, 2: var medida, 3: var dif_demand
fig_plot_list = []  # this list stores the fig objects for wind, solar and demand

for fig_var in fig_var_list:
    
    title = fig_var[0] # e.g. "Solar" 
    p48 = fig_var[1] # e.g. 'p48_solar
    medida = fig_var[2] # e.g. 'medida_solar'
    dif = fig_var[3] # e.g. 'dif_solar'
    
    color_list_dif = np.where(df[dif]<0, '#ff0000', '#008216')
    
    trace1 = go.Scatter(
        x=df['datetime'],
        y=df[p48],
        name=p48,
        marker=dict(
            color='#b50505'
                   )
    )
    trace2 = go.Scatter(
        x=df['datetime'],
        y=df[medida],
        name=medida,
        marker=dict(
            color='#000000'
                   )
    )

    trace3 = go.Bar(
        x=df['datetime'],
        y=df[dif],
        name=dif,
        marker_color=color_list_dif,
        opacity=0.6
    )

    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.update_layout(template="plotly_white")

    fig.add_trace(trace1)
    fig.add_trace(trace2)

    fig.update_traces(line=dict(width=4))

    fig.add_trace(trace3, secondary_y=True)

    for date in df['datetime'].dt.date.unique():
        fig.add_vline(x = date, line_width=1.5, )

        # separate parts by color
            # valley = blue
            # 1 shoulder = grey
            # solar = yellow
            # 2 shoulder = grey

        opacity_float = 0.15

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


    # place legend in the top left (horizontal)
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ))

    # add title
    fig.update_layout(
        title=dict(text=title, font=dict(size=30), automargin=False, yref='paper')
    )

    if not title == "Demand":
        fig.update_yaxes(rangemode="tozero") # start graph at 0
    
    fig_plot_list.append(fig)


st.plotly_chart(fig_plot_list[0], use_container_width = True)
st.plotly_chart(fig_plot_list[1], use_container_width = True)
st.plotly_chart(fig_plot_list[2], use_container_width = True)

st.dataframe(df, hide_index = True)

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
    
    df_xlsx = to_excel(df)
    st.download_button(label='📥 Download data as XLSX',
                                    data=df_xlsx ,
                                    file_name= 'df_p48_medida.xlsx')