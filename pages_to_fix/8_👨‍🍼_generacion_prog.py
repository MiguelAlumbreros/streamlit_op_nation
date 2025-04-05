from flask import Flask, request, render_template, send_file
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import io
import sys
import plotly.graph_objs as go

sys.path.append(r'Z:\04. Dispatching\04. Turno\05. Carpetas personales\Juan Carlos\02. Code\00. code')
from esios_scrap_jc import esios_download, esios_download2 # type: ignore

generation_ids = {
    'CICLO COMBINADO': [600, 9, 44, 114],
    'CONSUMO BOMBEO': [600, 25, 60, 130],
    'EÓLICA': [600, 10073, 10158, 10159],
    'NUCLEAR': [600, 4, 39, 109],
    'SOLAR FOTOVOLTAICA': [600, 14, 49, 119],
    'TURBINACIÓN BOMBEO': [600, 3, 38, 108],
    'UGH + NO UGH': [600, 10064, 10065, 10066],
}

# Diccionario que mapea los IDs a sus nombres correspondientes
id_names = {
    600: 'PMD',
    9: 'GENERACIÓN PROGRAMADA PBF CICLO COMBINADO',
    44: 'GENERACIÓN PROGRAMADA PVP CICLO COMBINADO',
    114: 'GENERACIÓN PROGRAMADA PHF1 CICLO COMBINADO',
    25: 'GENERACIÓN PROGRAMADA PBF CONSUMO BOMBEO',
    60: 'GENERACIÓN PROGRAMADA PVP CONSUMO BOMBEO',
    130: 'GENERACIÓN PROGRAMADA PHF1 CONSUMO BOMBEO',
    10073: 'GENERACIÓN PROGRAMADA PBF EÓLICA',
    10158: 'GENERACIÓN PROGRAMADA PVP EÓLICA',
    10159: 'GENERACIÓN PROGRAMADA PHF1 EÓLICA',
    4: 'GENERACIÓN PROGRAMADA PBF NUCLEAR',
    39: 'GENERACIÓN PROGRAMADA PVP NUCLEAR',
    109: 'GENERACIÓN PROGRAMADA PHF1 NUCLEAR',
    14: 'GENERACIÓN PROGRAMADA PBF SOLAR FOTOVOLTAICA',
    49: 'GENERACIÓN PROGRAMADA PVP SOLAR FOTOVOLTAICA',
    119: 'GENERACIÓN PROGRAMADA PHF1 SOLAR FOTOVOLTAICA',
    3: 'GENERACIÓN PROGRAMADA PBF TURBINACIÓN BOMBEO',
    38: 'GENERACIÓN PROGRAMADA PVP TURBINACIÓN BOMBEO',
    108: 'GENERACIÓN PROGRAMADA PHF1 TURBINACIÓN BOMBEO',
    10064: 'GENERACIÓN PROGRAMADA PBF UGH + NO UGH',
    10065: 'GENERACIÓN PROGRAMADA PVP UGH + NO UGH',
    10066: 'GENERACIÓN PROGRAMADA PHF1 UGH + NO UGH',
}

################################################################################################################################
# FUNCIONES

# Función para cargar datos
def load_data(date_start, generation_type):
    ids = generation_ids[generation_type]
    df = esios_download(date_start, ids)

    # Cambiar nombres de las columnas según los IDs
    df = df.rename(columns={id: id_names[id] for id in ids})

    # Cambiar NaN a 0
    df = df.fillna(0)

    # Eliminar última fila si el periodo es 1
    if df.iloc[-1]['period'] == 1:
        df.drop(df.tail(1).index, inplace=True)

    return df

# Función para generar el gráfico
def generate_plot(df, generation_type):
    df['Variación PVP-PBF'] = df[f'GENERACIÓN PROGRAMADA PVP {generation_type}'] - df[f'GENERACIÓN PROGRAMADA PBF {generation_type}']
    df['Variación PHF1-PVP'] = df[f'GENERACIÓN PROGRAMADA PHF1 {generation_type}'] - df[f'GENERACIÓN PROGRAMADA PVP {generation_type}']

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['period'] - 1, 
        y=df[f'GENERACIÓN PROGRAMADA PBF {generation_type}'], 
        mode='lines', 
        name='PBF',
        marker_color='#3786bc'
    ))

    fig.add_trace(go.Scatter(
        x=df['period'] - 1, 
        y=df[f'GENERACIÓN PROGRAMADA PHF1 {generation_type}'], 
        mode='lines', 
        name='PHF1',
        marker_color='#ff860e'
    ))

    fig.add_trace(go.Bar(
        x=df['period'] - 1, 
        y=df['Variación PVP-PBF'], 
        name='Variación PVP-PBF',
        marker_color='#aeccdb'
    ))

    fig.add_trace(go.Bar(
        x=df['period'] - 1 + 0.2,  
        y=df['Variación PHF1-PVP'], 
        name='Variación PHF1-PVP',
        marker_color='#ebbd81'
    ))

    # fig.add_shape(type='line', x0=0, x1=1, y0=0, y1=0, xref='paper', yref='y', line=dict(color='lightgray', dash='dash'))

    fig.update_layout(
        title=f'Comparación de Generación Programada y Variación - {generation_type} - {date_start}',
        xaxis_title='Periodo',
        yaxis_title='Programa (MWh)',
        # legend_title='Tipo',
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
    )

    return fig

################################################################################################################################

# Interfaz de Streamlit

tab1, tab2 = st.tabs(['Gráfico','Data'])

with st.sidebar:
    date_start = st.date_input('Fecha de inicio')
    date_start_str = date_start.strftime('%Y-%m-%d')
    generation_type = st.radio('Selecciona tecnología:', list(generation_ids.keys()))

with tab1:
    st.title("Generación Programada")

    # Cargar datos y generar gráfico
    df = load_data(date_start_str, generation_type)
    fig = generate_plot(df, generation_type)
    st.plotly_chart(fig)

with tab2:
    df = load_data(date_start_str, generation_type)
    df.columns = ['date', 'year', 'month', 'day', 'period', 'PMD', 'PBF', 'PVP', 'PHF1']
    # df = df[['date', 'period', 'PMD', 'PBF', 'PVP', 'PHF1']]
    # df.columns = ['date', 'period'] + [f'{col}' for col in df.columns if col not in ['date', 'period']]


    st.title(f"{generation_type} {date_start_str}")
    st.dataframe(df)
    # st.table(df.iloc[0:10])
    # st.json({'foo':'bar','fu':'ba'})
    # st.metric(label="Temp", value="273 K", delta="1.2 K")