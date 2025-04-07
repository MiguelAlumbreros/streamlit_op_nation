import streamlit as st
import plotly.graph_objects as go
# from plotly.subplots import make_subplots
from datetime import datetime
from datetime import timedelta
import pandas as pd

with st.sidebar:
    
    multi_toggle = st.toggle("Multi day selection", st.session_state.multi_day_selection, key = "multi_day_selection")

    if not multi_toggle:
        st.session_state.end_day_selection = st.session_state.start_day_selection
    start_date = st.date_input("start date", st.session_state.start_day_selection, key = "start_day_selection",
                                min_value = datetime(2024,6,1), max_value=datetime(2024,6,30))
    end_date = st.date_input("end date", st.session_state.end_day_selection, key = "end_day_selection", 
                             min_value = datetime(2024,6,1), max_value=datetime(2024,6,30)
                             ,disabled = not (st.session_state.multi_day_selection))
    
    


# #add path to the helper functions from the SQL queries py file
# import sys
# sys.path.insert(0, r'Z:\04. Dispatching\04. Turno\05. Carpetas personales\Miguel\Github\query_SQL')
# import query_SQL


st.write("""
# SSAA acumulados
""")


# df_query = query_SQL.query_SSAA_volume(start_date, end_date)

df = pd.read_csv(r'./data/3_data.csv', sep = ',')
df['date'] = pd.to_datetime(df['date'])

df = df[(df['date'] >= datetime(start_date.year, start_date.month, start_date.day)) & (df['date'] < datetime(end_date.year, end_date.month, end_date.day) + timedelta(days = 1))]

# aggregate query
# aggregate data summing
df_agg = df.copy()
del(df_agg['date'])
df_agg = df_agg.groupby(by = 'period', as_index = False).sum()

######
# PLOT 
######

fig = go.Figure()
fig.update_layout(template="plotly_white")

# create traces for each data field
trace1 = go.Bar(
    x=df_agg['period'],
    y=df_agg['RR_subir'],
    name='RR_subir',
    marker=dict(
    color='#038009'
               )
                 
)

trace2 = go.Bar(
    x=df_agg['period'],
    y=df_agg['RR_bajar'],
    name='RR_bajar',
    marker=dict(
    color='#a81b27'
               )
)

trace3 = go.Bar(
    x=df_agg['period'],
    y=df_agg['terc_subir'],
    name='terc_subir',
    marker=dict(
    color='#07e312'
               ),
               opacity=1
)

trace4 = go.Bar(
    x=df_agg['period'],
    y=df_agg['terc_bajar'],
    name='terc_bajar',
    marker=dict(
    color='#eb071a'
               )
)

# secondary
trace5 = go.Bar(
    x=df_agg['period'],
    y=df_agg['sec_subir'],
    name='sec_subir',
    visible='legendonly', # by default this is ticked off
    marker=dict(
    color='#26b0de'
               )
)

trace6 = go.Bar(
    x=df_agg['period'],
    y=df_agg['sec_bajar'],
    name='sec_bajar',
    visible='legendonly', # by default this is ticked off
    marker=dict(
    color='#045cb5'
               )
)

#update layout so bars are not staked and negative values appear in the bottom of the x axis
fig.update_layout(barmode='relative')

# update xtick so all periods show and y tick is every 250 megs
fig.update_layout(
   xaxis = dict(
      tickmode = 'linear',
      tick0 = 1,
      dtick = 1
   ),
   # yaxis = dict(
   #    tickmode = 'linear',
   #    tick0 = 250,
   #    dtick = 250
   # )
)

fig.update_traces(textposition='top center')

# update figure with background colors according to each region (valle = 1-6, punta 1 = 7-9, solares=10-18, punta 2 = 19-24)
opacity_float = 0.2
fig.add_vrect(x0=0.5, x1=6.5, 
            fillcolor="blue", opacity=opacity_float, line_width=0)
fig.add_vrect(x0=6.5, x1=9.5, 
            fillcolor="grey", opacity=opacity_float, line_width=0)
fig.add_vrect(x0=9.5, x1=18.5, 
            fillcolor="#eff54c", opacity=opacity_float, line_width=0) # slightly modified yellow. More mellow, otherwise it's too intrusive
fig.add_vrect(x0=18.5, x1=24.5, 
            fillcolor="grey", opacity=opacity_float, line_width=0)

# plot traces
fig.add_trace(trace1)
fig.add_trace(trace2)
fig.add_trace(trace3)
fig.add_trace(trace4)
fig.add_trace(trace5)
fig.add_trace(trace6)


# format text
fig.update_traces( textangle=0, textposition="auto", cliponaxis=True,texttemplate='%{y:.0f}')

fig.update_layout(uniformtext_minsize=17, uniformtext_mode='hide')
# fig.update_layout(uniformtext_minsize=9)

# make figure longer
fig.update_layout(
    # autosize=False,
    # width=800,
    height=650
)

fig.update_layout(font=dict(
        size=18
    ))
# format grid
fig.update_yaxes(gridcolor='black', gridwidth = 0.5)

# add total values

# fig.add_trace(go.Scatter(
#     x=df_plot.period, 
#     y=df_plot['total_ssaa'],
#     name = 'total',
#     text=df_plot['total_ssaa'],
#     # mode='text',
#     textposition='top center',
#     # textfont=dict(
#     #     size=10,
#     # ),
#     # showlegend=False
# ))

# place legend in the top left (horizontal)
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="left",
    x=0
))

fig.update_traces(width=0.85)


st.plotly_chart(fig, use_container_width = True)

# make two columns inside container to plot them in parallel
with st.container():
    col1, col2= st.columns(2)
    # show dfs, both agg and daily
    with col1:
        st.write("Daily data")
        st.dataframe(df.set_index('date'), use_container_width  = True)
    with col2:
        st.write("Aggregated data")
        st.dataframe(df_agg.set_index('period'),  use_container_width  = True)


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
    df_xlsx = to_excel(df)
    st.download_button(label='📥 Download data as XLSX',
                                    data=df_xlsx ,
                                    file_name= 'df_SSAA.xlsx')