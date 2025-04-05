import streamlit as st


tech_list = ['Solar fotovoltaica', 'Eólica terrestre no SSAA', 'Eólica terrestre SSAA', 'Gas Natural Cogeneración', 'No SSAA', 'All']
kpi_list = ['optim_mercados', 'optim_desv', 'optim_total', 'sobrecoste_prev', 'sobrecoste_apant', 'sobrecoste_final', 'generation']
with st.sidebar:
    # start_date = st.date_input("start date", default_start_date)
    # end_date = st.date_input("end date", default_end_date)
    
    multi_toggle = st.toggle("Multi day selection", st.session_state.multi_day_selection, key = "multi_day_selection")

    if not multi_toggle:
        st.session_state.end_day_selection = st.session_state.start_day_selection
    start_date = st.date_input("start date", st.session_state.start_day_selection, key = "start_day_selection")
    end_date = st.date_input("end date", st.session_state.end_day_selection, key = "end_day_selection", disabled = not (st.session_state.multi_day_selection))
    
    # drop down lists
    tech_selection = st.selectbox(label = 'Technology', options = tech_list)
    kpi_selection = st.selectbox(label = 'KPI', options = kpi_list)
    
    # radio button for selecting kpi or money
    kpi_or_money = st.radio(label = "1", options = ["kpi", "money"], label_visibility="collapsed")


from datetime import datetime
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt  
import numpy as np
# from  matplotlib.colors import LinearSegmentedColormap

import sys
sys.path.insert(0, r'Z:\04. Dispatching\04. Turno\05. Carpetas personales\Miguel\Github\query_SQL')
import query_SQL

def get_pivot(df:pd.DataFrame, values: str) -> pd.DataFrame:
    df = df.pivot_table(index = 'Fecha', columns = 'Periodo', values = values , aggfunc = 'sum', margins = True)
    return df


def parse_df_query(df_query: pd.DataFrame, tech_selection: str, kpi_selection: str, kpi_or_money:str) -> pd.DataFrame:
    """parses the df queried from the DB into a partitioned df

    Args:
        df_query (pd.DataFrame): input df from query
        tech_selection (str): selection of tech to be queried
            ['Solar fotovoltaica', 'Eólica terrestre no SSAA', 'Eólica terrestre SSAA', 'Gas Natural Cogeneración', 'No SSAA', 'All']
        kpi_selection (str): selection of kpi to be queried
            ['optim_mercados', 'optim_desv', 'optim_total', 'sobrecoste_apant', 'sobrecoste_final']
        kpi_or_money (str): shor kpi or money
            ['kpi', 'money']

    Returns:
        pd.DataFrame: partitioned df according to tech, kpi and kpi_or_money
    """
    
    # partition by type of tech
    def partition_tech_selection (df_temp: pd.DataFrame, tech_selection: str) -> pd.DataFrame:
        if tech_selection == 'Solar fotovoltaica':
            df = df_temp.query('Tecnología == "Solar fotovoltaica"')
        elif tech_selection == 'Eólica terrestre no SSAA':
            df = df_temp.query('Tecnología == "Eólica terrestre" and SSAA == "No"')
        elif tech_selection == 'Eólica terrestre SSAA':
            df = df_temp.query('Tecnología == "Eólica terrestre" and SSAA == "Si"')
        elif tech_selection == 'Gas Natural Cogeneración':
            df = df_temp.query('Tecnología == "Gas Natural Cogeneración"')
        elif tech_selection ==  'No SSAA':
            df = df_temp.query('Tecnología in ["Solar fotovoltaica", "Eólica terrestre"] and SSAA == "No"')
        else:
            df = df_temp
        return df
    
    df = partition_tech_selection(df_query, tech_selection)

    def get_kpi(df_tech: pd.DataFrame, kpi_selection: str, kpi_or_money: str) -> list:
        """calculate a df by kpi if selected. Otherwise just money values

        Args:
            df_tech (pd.DataFrame): df partioned by the tech selected previously
            kpi_selection (str): selection of kpi to be viewed. "kpi" or "money"

        Returns:
            list: 1. df with the money values
                  2. df with the kpi values
        """

        df_gen = get_pivot(df_tech, 'generacion')

        # if kpi_selection is generation then return generation and break function
        if kpi_selection == 'generation':
            return df_gen
        
        df_money = get_pivot(df_tech, kpi_selection)
        df_kpi = df_money/df_gen

        if kpi_or_money == "kpi":
            return df_kpi
        else:
            return df_money

    df = get_kpi(df, kpi_selection, kpi_or_money)

    return df


# query, parse and partition df
df_query = query_SQL.query_informe_portfolio_detalle(start_date= start_date, end_date= end_date)
df_plot = parse_df_query(df_query, tech_selection, kpi_selection, kpi_or_money)

# if money convert data into thousands
if kpi_or_money == "money":
    df_plot = df_plot/1000
    
###
# PLOT
###

# partion dfs for the different plots
df_center = df_plot.copy()
df_vertical = df_plot['All'].to_frame() # keep only vertical column
df_horizontal = df_plot.tail(1)
    
# plot
if kpi_or_money == "money":
    title = f'{tech_selection} - {kpi_selection} ({kpi_or_money} in thousands)'
else:
    title = f'{tech_selection} - {kpi_selection} ({kpi_or_money})'

    

# chart size
height = (df_plot.shape[0] - 1)/2  # height is equals to the number of days / 2
width = 15
    
# set max and min color values programmatically
if kpi_selection == 'generation':
    vmax = abs(df_center).iloc[:-1].max()[:-1].max()*0.75 # get the maximum value for all hours across all days. Does not include 'All' column/row. vmax is 75% of that value
elif kpi_or_money == 'money':
    vmax = abs(df_center).iloc[:-1].max()[:-1].max()*0.75 # get the maximum value for all hours across all days. Does not include 'All' column/row. vmax is 25% of that value
elif tech_selection == 'Eólica terrestre SSAA':
    vmax = 50
elif kpi_selection == 'optim_desv':
    vmax = 10
else:
    vmax = 30


fig, axs=plt.subplots(2,2,figsize=(width,height), gridspec_kw={'hspace': 0, 
                                                        'wspace': 0,
                                                        'width_ratios': [10, 1],
                                                        'height_ratios': [1, 10]})

## CENTER PLOT

# ser color palette
# cmap=LinearSegmentedColormap.from_list('rg',["r", "w", "g"], N=100) # This one does not work for some reason
# cmap = sns.diverging_palette(h_neg=10, h_pos=150, s=99, l=55, sep=3, as_cmap=True)
cmap = sns.diverging_palette(10, 133, as_cmap=True)

if kpi_or_money == "money":
    number_format = ".2f"
else:
    number_format = ".1f"

ax0 = sns.heatmap(df_center, annot= True, fmt=number_format, linewidth=0, cmap = cmap,center = 0,vmax=vmax, vmin = -vmax, cbar = False, ax=axs[1,0])

# change tick size to center plot
ax0.tick_params(axis='both', which='major', labelsize=10)

# VERTICAL RIGHT PLOT
ax1 = sns.barplot(x='All', y=df_vertical.index, hue = df_vertical.index,data=df_vertical, palette=np.where(df_vertical['All'] > 0, 'g', 'r').tolist(), legend=False)  # the hue part is to avoid future warnings
ax1 = axs[1,1]

# add labels in the center
for i in ax1.containers:
    ax1.bar_label(i,fmt=f'%{number_format}', label_type = 'center')


### HORIZONTAL TOP PLOT
sns.barplot(df_horizontal, palette=np.where(df_horizontal.iloc[0] > 0, 'g', 'r').tolist(), ax = axs[0,0])
ax2 = axs[0,0]
    
# # add labels in the center
for i in ax2.containers:
    ax2.bar_label(i,fmt=f'%{number_format}', label_type = 'center')


# remove axis in all but center plot (which is in position [1,0])
axs[0,0].axis("off")
axs[0,1].axis("off")
axs[1,1].axis("off")

# plot title
fig.suptitle(title, fontsize=20)

# make K ticks for all annotations instead of thousands
# for t in ax0.texts:
#     current_text = t.get_text()
    
#     # https://stackoverflow.com/questions/67629794/pandas-format-large-numbers
#     text_transform = (
#         lambda x: 
#             f"{round(float(x/1000), 1)}K"
#     )
#     t.set_text(text_transform(float(current_text)))
    
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
    
    df_xlsx = to_excel(df_plot)
    st.download_button(label='📥 Download data as XLSX',
                                    data=df_xlsx ,
                                    file_name= 'df_KPI.xlsx')