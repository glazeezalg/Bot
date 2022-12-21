import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import six

df = pd.DataFrame()

def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=12,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[-0.11, -0.1, 1.19, 1.2], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w', size=20)
            cell.set_facecolor(header_color)
        else:
            cell.set_text_props(size=15)
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax

def create_table(matrix):
    df = pd.DataFrame()
    for i in range(len(matrix[0])):
        df[matrix[0][i]] = [matrix[k][i] for k in range(1, len(matrix))]
    maxs = 0
    maxs_n = 0

    for i in matrix:
        for j in i:
            if j != '':
                maxs = max(max(list(map(lambda d: len(d), j.replace(' ', '').split("\n")) )), maxs)
                maxs_n = max(j.count('\n'), maxs_n)

    render_mpl_table(df, header_columns=0, col_width=maxs*0.17, row_height=maxs_n*0.4)
    plt.savefig("table.png", bbox_inches="tight", pad_inches=0)
