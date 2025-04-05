import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from datetime import timedelta
import pandas as pd

default_start_date = datetime.today().date() - timedelta(days = 2)
default_end_date = default_start_date

with st.sidebar:
    
    multi_toggle = st.toggle("Multi day selection", st.session_state.multi_day_selection, key = "multi_day_selection")

    if not multi_toggle:
        st.session_state.end_day_selection = st.session_state.start_day_selection
    start_date = st.date_input("start date", st.session_state.start_day_selection, key = "start_day_selection")
    end_date = st.date_input("end date", st.session_state.end_day_selection, key = "end_day_selection", 
                             min_value = datetime(2024,6,1), max_value=datetime(2024,6,30),
                             disabled = not (st.session_state.multi_day_selection))


#add path to the helper functions from the SQL queries py file
# import sys
# sys.path.insert(0, r'Z:\04. Dispatching\04. Turno\05. Carpetas personales\Miguel\Github\query_SQL')
# import query_SQL

# df_temp = query_SQL.query_informe_desvios(start_date, end_date)

df_temp = pd.read_csv(r'./data/2_data.csv', sep = ',')
df_temp['date'] = pd.to_datetime(df_temp['date'])
df_temp = df_temp[(df_temp['date'] >= datetime(start_date.year, start_date.month, start_date.day)) 
        & (df_temp['date'] < datetime(end_date.year, end_date.month, end_date.day) + timedelta(days = 1))]

trace1 = go.Scatter(
    x=df_temp['date'],
    y=df_temp['spread_desvio_subir'],
    name='spread_desvio_subir',
    marker=dict(
        color='#04b309'
               )

)
trace11 = go.Scatter(
    x=df_temp['date'],
    y=df_temp['spread_desvio_bajar'],
    name='spread_desvio_bajar',
    marker=dict(
        color='#d91d0f'
               )
)

trace2 = go.Bar(
    x=df_temp['date'],
    y=df_temp['is_desvio_unico_a_subir'],
    name='desvio_unico_a_subir',
    yaxis='y2',
    marker=dict(
    color='#04b309',
    opacity = 0.8
               )
)

trace3 = go.Bar(
    x=df_temp['date'],
    y=df_temp['is_desvio_unico_a_bajar'],
    name='desvio_unico_a_bajar',
    yaxis='y2',
    marker=dict(
    color='#d91d0f',
    opacity = 0.8
               )
)



fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.update_layout(template="plotly_white")

fig.layout.yaxis2.update(showticklabels=False)

fig.add_trace(trace2,secondary_y=True)
fig.add_trace(trace3,secondary_y=True)

fig.add_trace(trace1)
fig.add_trace(trace11)

for date in df_temp['date'].dt.date.unique():
    # add black vertical line between each day
    fig.add_vline(x = date, line_width=1.5, )

    # separate parts by color
        # valley = blue
        # 1 shoulder = 
        # solar = yellow
        # 2 shoulder = green
    
    opacity_float = 0.2
    
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

    
# fig = make_subplots(specs=[[{"secondary_y": True}]])
# fig.update_layout(template="plotly_white")
# fig.add_trace(trace1)
# fig.add_trace(trace11)
# fig.add_trace(trace2,secondary_y=True)
# fig.add_trace(trace3,secondary_y=True)
# fig.show ()

st.write("""
# Spread de desvíos y desvíos únicos
""")

st.plotly_chart(fig, use_container_width = True)
# test download buttons
df = df_temp

# display the dataframe on streamlit app
st.write(df.set_index('date'))

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
                                    file_name= 'df_desvios.xlsx')