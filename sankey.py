
"""
sankey.py: A reusable library for sankey visualizations

How to make links and nodes same color:
https://stackoverflow.com/questions/69494044/making-the-color-of-links-the-same-as-source-nodes-in-sankey-plot-plotly-in-r
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd


def _code_mapping(df, src, targ):
    # Get distinct labels
    labels = sorted(list(set(list(df[src]) + list(df[targ]))))

    # Get integer codes
    codes = list(range(len(labels)))

    # Create label to code mapping
    lc_map = dict(zip(labels, codes))

    # Substitute names for codes in dataframe
    df = df.replace({src: lc_map, targ: lc_map})

    return df, labels


def make_sankey(df, cols, vals=None, title=None, threshold=20, prep=True, **kwargs):
    """
    Create a sankey diagram linking src values to
    target values with thickness vals
    :param df: dataframe
    :param cols: list; columns to plot data from
    :param vals: str; column with values that correspond to link thickness
    :param title: str; title of graph
    :param threshold: int; threshold to filter values based on
    :param prep: boolean; if true, preps dataframe for analysis by aggregating and labeling
    :param kwargs: optional parameters for go.sankey function

    :return: nothing. plots a sankey diagram
    """
    if len(cols) < 2:
        raise Exception('must pass at least two columns')

    # make new df to hold sankey data
    sankey_df = pd.DataFrame()

    for col in cols:
        df[col] = df[col].astype(str).str.upper()

    if prep:
        vals = 'count'

        # merge all source --> target mapping under two columns
        for i in range(len(cols)-1):
            cur_df = df[[cols[i], cols[i + 1]]]
            cur_df = cur_df.groupby([cols[i], cols[i + 1]]).size().reset_index(name='count')
            cur_df.columns = ['source', 'target', 'count']
            sankey_df = pd.concat([sankey_df, cur_df])
    else:
        # label columns
        sankey_df = df
        sankey_df.columns = ['source', 'target', 'count']

    # filter on threshold
    sankey_df = sankey_df[sankey_df['count'] >= threshold]

    # mapping
    sankey_df, labels = _code_mapping(sankey_df, 'source', 'target')

    if vals:
        values = sankey_df['count']
    else:
        values = [1] * len(sankey_df)

    # match link colors to node colors
    nodes = np.unique(sankey_df[['source', 'target']], axis=None)
    nodes = pd.Series(index=nodes, data=range(len(nodes)))
    link_colors = [
        'rgba' +
        str(px.colors.hex_to_rgb(px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]) + (0.3,))
        for i in nodes.loc[sankey_df['source']]
        ]
    node_colors = [
        px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
        for i in nodes
        ]

    # establish links
    link = {'source': sankey_df['source'], 'target': sankey_df['target'], 'value': values,
            'color': link_colors}

    # adjust padding width and thickness of links
    pad = kwargs.get('pad', 50)
    thickness = kwargs.get('thickness', 20)

    # establish nodes
    node = {'label': labels, 'thickness': thickness, 'pad': pad, 'color': node_colors}

    # construct sankey
    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)
    fig.update_layout(title_text=title)

    return fig
