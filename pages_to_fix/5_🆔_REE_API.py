import streamlit as st
from datetime import timedelta

import pandas as pd

import plotly.graph_objects as go

# add path to get the functions from the file that access the API
import sys
sys.path.insert(0, r'Z:\04. Dispatching\04. Turno\05. Carpetas personales\Miguel\Github\ESIOS-sraper')
import helper_files_streamlit


# default_start_date = datetime.today().date() - timedelta(days = 1)
# default_end_date = default_start_date


with st.sidebar:
    # start_date = st.date_input("start date", default_start_date)
    # end_date = st.date_input("end date", default_end_date)
    
    multi_toggle = st.toggle("Multi day selection", st.session_state.multi_day_selection, key = "multi_day_selection")
    plot_toggle = st.toggle("Plot", key = "plot_selection",value = True)
    
    if not multi_toggle:
        st.session_state.end_day_selection = st.session_state.start_day_selection
    start_date = st.date_input("start date", st.session_state.start_day_selection, key = "start_day_selection")
    end_date = st.date_input("end date", st.session_state.end_day_selection, key = "end_day_selection", disabled = not (st.session_state.multi_day_selection))

end_date = end_date + timedelta(days= 1) # REE API is date exclusive

id_list = st.text_input(label = 'Indicators to be queried. Only accepts ints and lists of ints (e.g. 1814 or 1814,615)', value = '1814')

# parse input string as list

indicator_id_list = list(id_list.split(","))

for idx, i in enumerate(indicator_id_list):
    indicator_id_list[idx] = int(i)

# make API query
TOKEN = "a3be9b11f1b98f92cff5087a9bfc6dbb27f09ae05c98c0ec018a6eefd3331598"  # token personal para acceder a la API
df =helper_files_streamlit. ESIOS_call_all_ids(indicator_id_list=indicator_id_list, start_date=start_date, end_date=end_date, TOKEN=TOKEN)


# st.plotly_chart(px.bar(df_output, x = 'datetime', y = indicator_id_list), use_container_width = True)
if plot_toggle:
    fig = go.Figure()

    for indicator_id in indicator_id_list:
        fig.add_trace(go.Scatter(x=df.datetime, y=df[indicator_id], name=indicator_id,
                        line_shape='hv'))

    fig.update_layout(template="plotly_white")

    for date in df['datetime'].dt.date.unique():
        # add black vertical line between each day
        fig.add_vline(x = date, line_width=1.5 )

        # separate parts by color
            # valley = blue
            # 1 shoulder = 
            # solar = yellow
            # 2 shoulder = green
        
        # opacity_float = 0.1
        
        # fig.add_vrect(x0=date, x1=f"{date} 5:00", 
        #             #   annotation_text="decline", annotation_position="top left",
        #             fillcolor="blue", opacity=opacity_float, line_width=0)
        # fig.add_vrect(x0=f"{date} 5:00", x1=f"{date} 8:00", 
        #             #   annotation_text="decline", annotation_position="top left",
        #             fillcolor="grey", opacity=opacity_float, line_width=0)
        # fig.add_vrect(x0=f"{date} 8:00", x1=f"{date} 18:00", 
        #             #   annotation_text="decline", annotation_position="top left",
        #             fillcolor="yellow", opacity=opacity_float, line_width=0)
        # fig.add_vrect(x0=f"{date} 18:00", x1=f"{date + timedelta(days=1)} 00:00", 
        #             #   annotation_text="decline", annotation_position="top left",
        #             fillcolor="grey", opacity=opacity_float, line_width=0)


    st.plotly_chart(fig, use_container_width = True)
        # fig.add_trace()
    # # for indicator_id in indicator_id_list:
    #     df_output[1814].head()

# data in columns. Left is dataframe, right is information df
col1, col2 = st.columns(2)
with col1:
    st.dataframe(df.set_index('datetime'))
with col2:
    df_data = pd.read_excel('support_files/ESIOS_indicators_complete.xlsx')
    # convert string to list of ints
    id_list_int = []
    id_list_temp = id_list.split(',')
    for id in id_list_temp:
        id_list_int.append(int(id))
    
    df_info = df_data.loc[df_data['id'].isin(id_list_int)][['id','name', 'description']]
    st.dataframe(df_info.set_index('id'))

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
                                    file_name= 'df_API.xlsx')