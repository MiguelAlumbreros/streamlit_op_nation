import streamlit as st
import seaborn as sns
import pandas as pd


with st.sidebar:
    
    multi_toggle = st.toggle("Multi day selection", False, key = "multi_day_selection", disabled = True)

    if not multi_toggle:
        st.session_state.end_day_selection = st.session_state.start_day_selection
    start_date = st.date_input("start date", st.session_state.start_day_selection, key = "start_day_selection")
    end_date = st.date_input("end date", st.session_state.end_day_selection, key = "end_day_selection", disabled = not (st.session_state.multi_day_selection))
    
    precios_toggle = st.toggle("prices", False)

# import functions for queries
import sys
sys.path.insert(0, r'Z:\04. Dispatching\04. Turno\05. Carpetas personales\Miguel\Github\query_SQL')
import query_SQL

sesion_list = ['MD', 'I1', 'I2', 'I3', 'I4', 'I5', 'I6', 'I7']
df = query_SQL.query_auctions(start_date, sesion_list)

# pivot and order re-order indexes
df = df.pivot_table(values = 'price', index='session', columns='period')

index = sesion_list
df_precios = df.reindex(index)

# create spread table
df_spreads = df_precios

first_row = df_precios.iloc[[0]].values[0]
df_spreads = df_spreads.apply(lambda row: row - first_row, axis=1)

df_spreads.iloc[0] = first_row # substitute first row by


###
# PLOT
###
from  matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import numpy as np


# if toggle prices then change theme and data to prices
if precios_toggle:
    df_selection = df_precios
    
    #cmap is white grey
    cmap = LinearSegmentedColormap.from_list(
    name='test', 
    colors=['white','white', 'white', 'white', 'white', 'white', 'grey']
    ) 
    
    vmax = abs (df_selection[1:]).max().max()

else:
    df_selection = df_spreads
    
    #cmap is red white green
    cmap = LinearSegmentedColormap.from_list(
    name='cmap', 
    colors=['red', 'white', 'green']
    )
    
    vmax = abs (df_selection[1:]).max().max() / 2 # if spreads then make max and min more visible

    
# chart size
height = 3.5
width = 14.5
figsize=(width,height)

fig, ax = plt.subplots(figsize=figsize)


# the following is a copy pasta to NOT color the first row (color = white)
MASK = df_selection.apply(lambda x:np.arange(len(x))==0)
COL = [(0.9664744329104191, 0.9664744329104191, 0.9649365628604383)]
# COL = plt.get_cmap('blue')

g_first = sns.heatmap(df_selection, annot=True, fmt=f".1f", cbar=False, mask=~MASK,cmap=COL,vmin=-vmax, vmax=vmax, annot_kws={"fontsize":10})

g_rest = sns.heatmap(df_selection, annot=True, fmt=f".1f", cbar=False, mask=MASK,cmap=cmap,vmin=-vmax, vmax=vmax, linewidths=1.1, linecolor='white', annot_kws={"fontsize":10})


plt.tick_params(axis='both', which='major', labelsize=20, 
                labelbottom = False, bottom=False, top = False, labeltop=True)

# make axis bold, bigger and rotate y axis
g_rest.set_yticklabels(g_rest.get_yticklabels(), rotation = 0, fontsize = 11.5, weight = 'bold')
g_rest.set_xticklabels(g_rest.get_xticklabels(), fontsize = 11.5, weight = 'bold')

plt.title(start_date, loc = 'left',fontdict = {'fontsize': 14})
# hide axis titles
ax.set_ylabel('')    
ax.set_xlabel('')


st.pyplot(fig=fig, use_container_width=False)

# download button on the sidebar
with st.sidebar:
    from io import BytesIO
    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=True, sheet_name='Sheet1')
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        format1 = workbook.add_format({'num_format': '0.00'}) 
        worksheet.set_column('A:A', None, format1)  
        writer.close()
        processed_data = output.getvalue()
        return processed_data
    
    df_xlsx = to_excel(df_selection)
    st.download_button(label='📥 Download data as XLSX',
                                    data=df_xlsx ,
                                    file_name= 'df_spreads.xlsx')





