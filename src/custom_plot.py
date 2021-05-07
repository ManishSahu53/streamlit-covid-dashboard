import itertools
import copy

import streamlit as st
import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging

import config


@st.cache(show_spinner=False)
def normalisation(data, population, rule):
    if config.RULE_MAP[rule] == 'percentage':
        new_data = (int(data) / int(population) )* int(config.UNIT)
        try:
            new_data.name = data.name
        except:
            pass
        return new_data
    else:
        new_data = data
        try:
            new_data.name = data.name
        except:
            pass
        return new_data


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return list(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def get_default_palette(alpha=False):
    hex_palette = copy.deepcopy(plotly.colors.qualitative.Plotly)
    hex_palette.pop(3)
    rgb_palette = []
    for hex_color in hex_palette:
        rgb_color = hex_to_rgb(hex_color)
        if alpha:
            rgb_color.append(.3)
            rgb_palette.append('rgba({},{},{},{})'.format(*rgb_color))
        else:
            rgb_palette.append(hex_color)

    return itertools.cycle(rgb_palette)


def summary_plot_data(region, what, name):
    mapp = {
     'Daily Recovery' : 'daily_recovery',
     'Daily New Cases': 'daily_confirmed',
     'Daily Deaths': 'daily_deceased',
     'Daily Test': 'daily_test', 
     'Daily Active Cases': 'daily_active'
    }
    plot_data = region[mapp[what]].rolling(7).mean()

    if what == 'Daily Recovery':
        title = "Number of Daily Rocvery"
        yscale = 'log'
    
    elif what == 'Daily New Cases':
        title = "Number Daily New Cases"
        yscale = 'log'
    
    elif what == 'Daily Deaths':
        title = "Daily Number of Deaths"
        yscale = 'log'
    
    elif what == 'Daily Test':
        title = "Number of Daily Tests"
        yscale = 'linear'
    
    elif what == 'Daily Active Cases':
        title = "Net Daily Active Cases"
        yscale = 'log'

    return plot_data, title


@st.cache(allow_output_mutation=True, show_spinner=False)
def summary(data, what):
    titles = list(config.REGION_INDEX.keys())
    titles = sorted(titles)
    nrow, ncol = 6, 6
    fig = make_subplots(nrow, ncol, 
                        shared_xaxes='all', shared_yaxes='all', subplot_titles=titles,
                        vertical_spacing=.08)
    minus = 0
    PALETTE = get_default_palette()  # get_default_palette()
    maxs = []
    # plot_data_india, _ = summary_plot_data(data, what, name='India')
    for i, name in enumerate(titles):
        col = (i - minus) % ncol + 1
        row = (i - minus) // ncol + 1
        
        # logging.info(f'Custom Plot name: {name}')

        region = data[data['State'] == name]
        plot_data, title = summary_plot_data(region, what, name)
        maxs.append(plot_data.values[-90:].max())
        fig.add_trace(go.Scatter(x=data['date'][-90:], y=plot_data.values[-90:], showlegend=False,
                                 name=name, marker=dict(color=next(PALETTE)), fill='tozeroy'), row, col)

    fig.update_xaxes(showgrid=True, gridwidth=1, tickangle=45, gridcolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey', range=[0, max(maxs)])
    fig.update_layout(
        title=title,
        plot_bgcolor="white",
        margin=dict(t=50, l=10, b=50, r=10),
        # width=1300,
        height=600,
        autosize=True,
        hovermode="x unified",
    )
    PALETTE = get_default_palette()  # get_default_palette()
    for i in fig['layout']['annotations']:
        i['font'] = dict(size=12, color=next(PALETTE))
    return fig