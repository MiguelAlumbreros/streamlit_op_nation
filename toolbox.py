# #file to store potential functionalities that were not added

# import streamlit as st
# #download CSV button

# st.cache(suppress_st_warning  = True)
# def convert_to_csv(df):
#     # IMPORTANT: Cache the conversion to prevent computation on every rerun
#     return df.to_csv(index=False).encode('utf-8')
# csv = convert_to_csv(df)


# # download button 1 to download dataframe as csv
# download1 = st.download_button(
#     label=" 📥 Download data as CSV",
#     data=csv,
#     file_name='large_df.csv',
#     mime='text/csv'
# )
import pandas as pd
from datetime import timedelta
import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_fase2(df: pd.DataFrame)-> go.Figure:
    """gets the vertical df from query_fase_2 and plots it

    Args:
        df (pd.DataFrame): query_fase_2(vertical = True)

    Returns:
        go.Figure:
    """
    color_list_dif = np.where(df['fase_2_volume']<0, '#e31b54', '#4ff771')

    trace1 = go.Scatter(
        x=df['datetime'],
        y=df['fase_2_spread'],
        name='fase_2_spread',
        marker=dict(
            color='black'
                )
    )

    trace3 = go.Bar(
        x=df['datetime'],
        y=df['fase_2_volume'],
        name='fase_2_volume',
        marker_color=color_list_dif,
        opacity=1
    )

    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.update_layout(template="plotly_white")

    fig.add_trace(trace1, secondary_y=True)
    fig.update_traces(line=dict(width=4))

    fig.add_trace(trace3)
    
    
    

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
        title=dict(text='Fase II', font=dict(size=30), automargin=False, yref='paper')
    )   
    
    return fig                


def main():
    pass

if __name__ == "__main__":
    main()
    