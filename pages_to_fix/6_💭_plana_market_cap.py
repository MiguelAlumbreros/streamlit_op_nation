import streamlit as st
from datetime import datetime
import pandas as pd

with st.sidebar:
    # start_date = st.date_input("start date", default_start_date)
    # end_date = st.date_input("end date", default_end_date)
    
    multi_toggle = st.toggle("Multi day selection", st.session_state.multi_day_selection, key = "multi_day_selection")

    if not multi_toggle:
        st.session_state.end_day_selection = st.session_state.start_day_selection
    start_date = st.date_input("start date", st.session_state.start_day_selection, key = "start_day_selection")
    end_date = st.date_input("end date", st.session_state.end_day_selection, key = "end_day_selection", disabled = not (st.session_state.multi_day_selection))

#add path to functions from the SQL queries py file
import sys
sys.path.insert(0, r'Z:\04. Dispatching\04. Turno\05. Carpetas personales\Miguel\Github\query_SQL')
import plot_plana_market_cap

df = plot_plana_market_cap.get_market_cap_data(datetime(start_date.year, start_date.month, start_date.day), datetime(end_date.year, end_date.month, end_date.day))
fig = plot_plana_market_cap.plot_plana_market_cap(df)

font_size = 19
fig.update_layout(xaxis_tickfont_size = font_size, yaxis_tickfont_size = font_size, yaxis2_tickfont_size = font_size)
# make figure longer
fig.update_layout(
    # autosize=False,
    # width=800,
    height=650
)

st.plotly_chart(fig, use_container_width = True)

st.dataframe(df, hide_index = True)


# download button
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

