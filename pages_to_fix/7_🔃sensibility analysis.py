import streamlit as st
import pandas as pd

from plotly.subplots import make_subplots
import plotly.graph_objects as go

with st.sidebar:
    
    multi_toggle = st.toggle("Multi day selection", False, key = "multi_day_selection", disabled = True)

    if not multi_toggle:
        st.session_state.end_day_selection = st.session_state.start_day_selection
    start_date = st.date_input("start date", st.session_state.start_day_selection, key = "start_day_selection")
    end_date = st.date_input("end date", st.session_state.end_day_selection, key = "end_day_selection", disabled = not (st.session_state.multi_day_selection))

# import functions for queries
import sys
sys.path.insert(0, r'Z:\04. Dispatching\04. Turno\05. Carpetas personales\Miguel\Github\query_SQL')
import query_SQL

# import functions for parsing data
import sys
sys.path.insert(0, r'Z:\04. Dispatching\04. Turno\05. Carpetas personales\Miguel\Github\curvas_MD')
import helper_files


df_PMD = query_SQL.query_auctions(start_date, ['MD'])
df_curve_parsed = query_SQL.query_curve_data(start_date)

energy_gap_list = [250, 500, 750, 1000]
df_results = helper_files.find_forecast_volatility_prices(df_PMD, df_curve_parsed, start_date, energy_gap_list)



def plot_sensitivity(df: pd.DataFrame, df_PMD: pd.DataFrame):
    """Plots plotly figure with the sensitivity bars and line

    Args:
        df (pd.DataFrame): DataFrame with data on sensitivities
        df_PMD (pd.DataFrame): DataFrame with DA prices

    Returns:
        _type_: fig object with fig.show()
    """

    opacity = 0.5

    # fig = go.Figure()

    fig = make_subplots(specs=[[{"secondary_y": True}]])


    x = df.period.unique().tolist()

    df.energy_gap = df.energy_gap.astype('float') # if energy_gap is an int .query does not work with negative values
    y1 = df.query('energy_gap == 250').spread
    y2 = df.query('energy_gap == 500').spread
    y3 = df.query('energy_gap == 750').spread
    y4 = df.query('energy_gap == 1000').spread

    y5 = df.query('energy_gap == -250').spread
    y6 = df.query('energy_gap == -500').spread
    y7 = df.query('energy_gap == -750').spread
    y8 = df.query('energy_gap == -1000').spread


    fig.add_bar(x=x, y=y1, opacity=opacity, name = '250', marker_color = '#991d1d', secondary_y=False)
    fig.add_bar(x=x, y=y2, opacity=opacity, name = '500', marker_color = '#b51818', secondary_y=False)
    fig.add_bar(x=x, y=y3, opacity=opacity, name = '750', marker_color = '#de1010', secondary_y=False)
    fig.add_bar(x=x, y=y4, opacity=opacity, name = '1000', marker_color = '#ff0000', secondary_y=False)

    fig.add_bar(x=x, y=y5, opacity=opacity, name = '-250', marker_color = '#29942d', secondary_y=False)
    fig.add_bar(x=x, y=y6, opacity=opacity, name = '-500', marker_color = '#25b02a', secondary_y=False)
    fig.add_bar(x=x, y=y7, opacity=opacity, name = '-750', marker_color = '#15d61c', secondary_y=False)
    fig.add_bar(x=x, y=y8, opacity=opacity, name = '-1000', marker_color = '#00ff08', secondary_y=False)


    # df.energy_gap = df.energy_gap.astype('float')
    # y1 = df.query('energy_gap == 100').spread
    # y2 = df.query('energy_gap == 200').spread
    # y3 = df.query('energy_gap == 300').spread
    # y4 = df.query('energy_gap == 400').spread
    # y5 = df.query('energy_gap == 500').spread

    # y6 = df.query('energy_gap == -100').spread
    # y7 = df.query('energy_gap == -200').spread
    # y8 = df.query('energy_gap == -300').spread
    # y9 = df.query('energy_gap == -400').spread
    # y10 = df.query('energy_gap == -500').spread


    # fig.add_bar(x=x, y=y1, opacity=opacity, name = '100', marker_color = '#991d1d', secondary_y=False)
    # fig.add_bar(x=x, y=y2, opacity=opacity, name = '200', marker_color = '#b51818', secondary_y=False)
    # fig.add_bar(x=x, y=y3, opacity=opacity, name = '300', marker_color = '#de1010', secondary_y=False)
    # fig.add_bar(x=x, y=y4, opacity=opacity, name = '400', marker_color = '#ff0000', secondary_y=False)
    # fig.add_bar(x=x, y=y5, opacity=opacity, name = '500', marker_color = '#29942d', secondary_y=False)
    
    # fig.add_bar(x=x, y=y6, opacity=opacity, name = '-100', marker_color = '#25b02a', secondary_y=False)
    # fig.add_bar(x=x, y=y7, opacity=opacity, name = '-200', marker_color = '#15d61c', secondary_y=False)
    # fig.add_bar(x=x, y=y8, opacity=opacity, name = '-300', marker_color = '#00ff08', secondary_y=False)
    # fig.add_bar(x=x, y=y9, opacity=opacity, name = '-400', marker_color = '#00ff08', secondary_y=False)
    # fig.add_bar(x=x, y=y10, opacity=opacity, name = '-500', marker_color = '#00ff08', secondary_y=False)


    fig.add_trace(go.Scatter(
        x=x
        ,y=df_PMD.price.values
        ,mode='lines'
        ,name='DA price'
        ,line=dict(
            color='royalblue'
            ,dash ='dot'
            ,width= 4
        )
        )
        ,secondary_y=True)

    fig.update_layout(barmode='overlay', title = f'Price sensitivity for day {df.date.iloc[0]}')

    fig.update_xaxes( 
        tickmode="array",
        tickvals=df.period.unique().tolist()
    )

    fig.update_yaxes( 
        title_text="spread"             
        ,showgrid=True
        ,tickmode="array"
        ,tickvals=list(range(-150,150, 10))
        , gridwidth = 1.5
        ,secondary_y= False
    )

    fig.update_yaxes( 
        title_text="DA price"             
        ,secondary_y= True
    )
    fig.update_layout(
        template="simple_white"
    )

    fig.update_layout(
        font_size = 15
    )

    # fig.update_traces(
    #     width=0.9
    # )             
    return fig

fig = plot_sensitivity(df_results, df_PMD)

st.plotly_chart(fig, use_container_width = True)

st.write(df_results.set_index('date'))

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
    
    df_xlsx = to_excel(df_results)
    st.download_button(label='📥 Download data as XLSX',
                                    data=df_xlsx ,
                                    file_name= 'df_KPI.xlsx')
