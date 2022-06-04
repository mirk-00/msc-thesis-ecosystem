from http import server
from dash import Dash, html, dcc
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from glob import glob
import plotly.graph_objects as go

#### Creazione delle Fig da inserire poi nell'applicazione Dash
sharks = ['Bathyraja_brachyurops', 'Chimaera_monstrosa', 'Dalatias_licha',
'Dipturus_oxyrinchus', 'Etmopterus_spinax', 'Galeus_melastomus',
'Mustelus_asterias', 'Mustelus_mustelus', 'Myliobatis_aquila', 'RSH',
'RSS', 'Raja_asterias', 'Raja_clavata', 'Raja_miraletus',
'Raja_polystigma', 'SSH', 'SSS', 'Scyliorhinus_canicula',
'Squalus_blainville', 'Torpedo_marmorata', 'Torpedo_torpedo',
'RSH_C1', 'RSS_C1', 'SSH_C1', 'SSS_C1', 'SSS_C2', 'ESH',
'ESS', 'RAY', 'SHK']
models = [
    'TOT',
    'CUT3',
    'CUT2',
    'CUT1',
    'ORI',
    'ESSESH',
    'SHKRAY']
Pastel = px.colors.qualitative.Pastel
mycolorlist=[
    [0, Pastel[0]],
    [0.13, 'rgb(255,255,255)'],
    [0.75, Pastel[1]],
    [1, Pastel[2]],
]
mycolorgrad = [
    [0, 'rgb(255,255,255)'],
    [1, Pastel[2]],
]
mti_color_grad=[
    [0, Pastel[0]],
    [0.5, 'rgb(255,255,255)'],
    [1, Pastel[2]],
]



def get_model_complete_analysis(model):
    econet_stats = pd.read_excel(model+'\\EcoNet_Results.xlsx', sheet_name='stats', header=None).rename(columns={0:'indicator',2:model})[['indicator',model]]
    econet_control = pd.read_excel(model+'\\EcoNet_Results.xlsx', sheet_name='control').rename(columns={'Unnamed: 0':model}).set_index(model)
    econet_utility = pd.read_excel(model+'\\EcoNet_Results.xlsx', sheet_name='utility').rename(columns={'Unnamed: 0':model}).set_index(model)

    ascend_ind = pd.read_csv(model+'\\ascend.csv')
    betweenness = pd.read_csv(model+'\\betweenness.csv')
    enar_flow = pd.read_csv(model+'\\flowStats.csv')
    keystoness = pd.read_excel(model+'\\keystoness.xlsx')
    ewe_mti = pd.read_excel(model+'\\mti.xlsx')
    ewe_stats = pd.read_csv(glob(model+'\\Ecopath SoS*-Statistics.csv')[0])

    ## STRUTTURAZIONE DEI DATI
    stat_rep = {
        ':':'',
        '.*\(FCI\)':'FCI',
        '.*Capacity':'Capacity',
        '^Syne.*':'Synergism',
        '^Mutual.*':'Mutualism',
        '.*Aggrad.*':'APL',
    }
    stat_indicators = ['Link density','Connectance','FCI','Ascendency','Capacity','Synergism','Mutualism','APL']
    econet_stats = econet_stats.loc[~econet_stats['indicator'].isna()].reset_index(drop=True).replace(stat_rep, regex=True).set_index('indicator')
    econet_stats = econet_stats.loc[stat_indicators]
    econet_utility = econet_utility.loc[:, ~econet_utility.columns.str.contains('^Unnamed')]
    econet_control = econet_control.loc[:, ~econet_control.columns.str.contains('^Unnamed')]

    ascend_ind = ascend_ind.rename(columns={'Unnamed: 0':'indicator'}).set_index('indicator').T.rename(columns={1:model})
    betweenness = betweenness.loc[:, ~betweenness.columns.str.contains('^Unn')].rename(columns={'namelist':'FG', 'betw':model}).set_index('FG')
    enar_flow = enar_flow.rename(columns={'Unnamed: 0':'indicator'}).set_index('indicator').T.rename(columns={1:model})
    keystoness = keystoness.rename(columns={'Group name':'FG',
                                'Keystone index #1': 'Key1 '+model,
                                'Keystone index #2': 'Key 2 '+model,
                                'Keystone index #3': 'Key3 '+model,
                                'Relative total impact': 'RTI '+model,
                                }).set_index('FG').reindex(betweenness.index)

    ewe_mti = ewe_mti.rename(columns={'Impacting / Impacted':'FG'}).set_index('FG')
    ewe_stats = ewe_stats[['Parameter','Value']].rename(columns={'Value':model}).set_index('Parameter')
    return [econet_stats, econet_utility, econet_control, ascend_ind, betweenness, enar_flow, keystoness, ewe_mti, ewe_stats]


def make_indicators_df(index_vec):
    empty_df = pd.DataFrame()
    for i in models:
        df = get_model_complete_analysis(i)[index_vec]
        empty_df = pd.concat([empty_df, df],axis=1)
    return empty_df



## Econet 0
econet_stats_df = pd.read_csv('.\\indicators0.csv').set_index('indicator')
# econet_std_stats_df = econet_stats_df.sub(econet_stats_df['ORI'], axis=0).T
legend_dic = {
    'Ascendency':'Ascendency<br><sup>[bits t/km2/year]</sup>',
    'Capacity':'Capacity<br><sup>[bits t/km2/year]</sup>',
    'Overhead':'Overhead<br><sup>[bits t/km2/year]</sup>',
}
econet_std_stats_df = econet_stats_df.T.rename(columns=legend_dic)
fig = px.bar(econet_std_stats_df, color_discrete_sequence=Pastel)
fig.update_layout(legend_title='', template='plotly_white', title='EcoNet Analysis')
fig.update_xaxes(title_text='Model')
fig.update_yaxes(title_text='')
fig_econet = fig

## Econet 1
econet_utility_list  = []
econet_utility_fig_dic={}
for model in models:
    econet_utility_list.append(pd.read_csv('.\\indicators1\\'+model+'.csv').set_index(model))

for index, df in enumerate(econet_utility_list):
    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        zmin=-3,
        zmax=20,
        z=df.values.tolist(),
        x=df.index.tolist(),
        y=df.index.tolist(),
        colorscale=mycolorlist,
    ))
    fig.update_layout(
        title=models[index]
    )
    econet_utility_fig_dic[models[index]] = fig

## Econet 2
econet_control_list  = []
econet_control_fig_dic = {}
for model in models:
    econet_control_list.append(pd.read_csv('.\\indicators2\\'+model+'.csv').set_index(model))
for index, df in enumerate(econet_control_list):
    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        zmin=-3,
        zmax=20,
        z=df.values.tolist(),
        x=df.index.tolist(),
        y=df.index.tolist(),
        colorscale=mycolorlist,
    ))
    fig.update_layout(
        title=models[index])
    econet_control_fig_dic[models[index]] = fig
## La dalatias licha ha un controllo elevatissimo forse outlier


## Ascendency enar 3
ascend_df = pd.read_csv('.\\indicators3.csv').set_index('Unnamed: 0')

indicators=[
    'TD',
    'ASC',
    'CAP',
    'OH',
    'ASC.CAP',
    'OH.CAP',
    'A.internal',
    'CAP.internal',
    'OH.internal',
]
legend_dic = {
    'ASC':'Ascendency<br><sup>[bits t/km2/year]</sup>',
    'CAP':'Capacity<br><sup>[bits t/km2/year]</sup>',
    'OH':'Overhead<br><sup>[bits t/km2/year]</sup>',
    'TD':'Trophic Depth',
    'ASC.CAP':'A/C',
    'OH.CAP':'O/C',
    'A.internal':'A (internal)<br><sup>[bits t/km2/year]</sup>',
    'OH.internal':'O (internal)<br><sup>[bits t/km2/year]</sup>',
    'CAP.internal':'C (internal)<br><sup>[bits t/km2/year]</sup>',
}
ascend_std_df = ascend_df.T[indicators].rename(columns=legend_dic)
fig = px.bar(ascend_std_df, color_discrete_sequence=Pastel)
fig.update_layout(legend_title='', template='plotly_white', title='Ascendency Analysis')
fig.update_xaxes(title_text='Model')
fig.update_yaxes(title_text='')
enar_asc_fig = fig


## Betweenness 4
betweennness_df = pd.read_csv('.\\indicators4.csv').set_index('FG')
## elimino i detriti che sono ovviamente outlier di betweenness e mascherano l'effetto degli altri
betweennness_df = betweennness_df.loc[~betweennness_df.index.isin(['DC','SPOM','BD'])]
box_betw_df = betweennness_df.stack().rename('Betweenness').reset_index().rename(columns={'level_1':'Model'})
fig=go.Figure()
fig.add_trace(go.Box(
    y=box_betw_df['Betweenness'],
    x=box_betw_df['FG'],
    boxpoints=False,
    hoverinfo='none',
    marker=dict(
        color=Pastel[0]
    ),
    line=dict(
        color='rgba(102, 197, 204,0.5)'
    ),
    fillcolor='rgba(102, 197, 204,0.2)',
))
fig.add_traces(
    list(px.strip(box_betw_df, x='FG', y='Betweenness', hover_data=['Model'],stripmode='overlay', color_discrete_sequence=[Pastel[0]]).select_traces())
) 
fig.update_layout(hovermode='x', template='plotly_white', title='Betweenness', showlegend=False)
betweenness_fig = fig


## enaR Flow 5
flow_df = pd.read_csv('.\\indicators5.csv').set_index('Unnamed: 0')
flow_df = flow_df.loc[~flow_df.index.str.contains('^mode')]
indicators = [
    'TST',
    'TSTp',
    'APL',
    'FCI',
]
legend_dic = {
    'TST':'TST<br><sup>[t/km2/year]</sup>',
    'TSTp':'TSTp<br><sup>[t/km2/year]</sup>',
}
flow_std_df = flow_df.T[indicators].rename(columns=legend_dic)
fig = px.bar(flow_std_df, color_discrete_sequence=Pastel)
fig.update_xaxes(title='Model')
fig.update_yaxes(title='')
fig.update_layout(legend_title_text='', title='Flow Analysis', template='plotly_white')
enar_flow_fig=fig


## Keystoneness 6
keystoness_df = pd.read_csv('.\\indicators6.csv').set_index('FG')
key_plot_df = keystoness_df.loc[:, keystoness_df.columns.str.contains(('^RTI.*|^Key1.*'))]
shrk_palette = [
    'rgba(102, 197, 204, 0.4)',
    'rgb(248, 156, 116)',
]
keystone_fig_dic={}
for idx,model in enumerate(models):
    px_df = key_plot_df.loc[:, key_plot_df.columns.str.contains('{}$'.format(model))].copy()
    px_df['shark'] = px_df.index.isin(sharks)
    fig = px.scatter(px_df, x='RTI {}'.format(model), y='Key1 {}'.format(model), hover_data=[px_df.index], color='shark', color_discrete_sequence=shrk_palette)
    fig.update_layout(title=model, showlegend=False, template='plotly_white')
    fig.update_xaxes(title='RTI')
    fig.update_yaxes(title='Key1')
    keystone_fig_dic[model] = fig



## Ecopath MTI 7
mti_list  = []
mti_fig_dic = {}

for model in models:
    mti_list.append(pd.read_csv('.\\indicators7\\'+model+'.csv').set_index('FG'))

for index, df in enumerate(mti_list):
    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        zmin=-1,
        zmax=1,
        z=df.values.tolist(),
        x=df.index.tolist(),
        y=df.index.tolist(),
        colorscale=mti_color_grad,
    ))
    fig.update_layout(
        title=models[index])
    mti_fig_dic[models[index]] = fig



## Ecopath statistics 8
ewe_stats_df = pd.read_csv('.\\indicators8.csv').set_index('Parameter')
ewe_ascend_df = pd.read_csv('.\\indicators_ewe.csv').rename(columns={'Unnamed: 0':'Model'}).set_index('Model')

ewe_std_stats_df = ewe_stats_df.sub(ewe_stats_df['ORI'], axis=0).T
ewe_std_stats_df = ewe_stats_df.T
fig = px.bar(ewe_std_stats_df, color_discrete_sequence=Pastel)
fig.update_xaxes(title='Model')
fig.update_yaxes(title='')
fig.update_layout(template='plotly_white', legend_title_text='', title='Ecopath System Indicators')
ewe_stats_fig = fig

ewe_ascend_df = pd.read_csv('.\\indicators_ewe.csv').rename(columns={'Unnamed: 0':'Model'}).set_index('Model')
fig = px.bar(ewe_ascend_df, title='Ecopath Information Statistics', color_discrete_sequence=Pastel)
fig.update_layout(legend_title='', template='plotly_white')
fig.update_yaxes(title='')
fig.update_xaxes(title='Model')
ewe_ascend_fig = fig







######################################################################################################
#####################################################################################################
#### Creazione della Dashboard
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
server = app.server


app.layout = html.Div([
    dbc.Tabs([
        dbc.Tab(
            label='Home',
        ),
        dbc.Tab(
            label='Ecopath Statistics',
            children=[
                dcc.Graph(
                    figure=ewe_stats_fig,
                    id='ewe_stats_fig'
                ),
                dcc.Graph(
                    figure=ewe_ascend_fig,
                    id='ewe_ascend_fig'
                )
            ]
        ),
        dbc.Tab(
            label='EcoNet Information Analysis',
            children=[
                dcc.Graph(
                    figure=fig_econet,
                    id='econet_fig'
                )
            ]
        ),
        dbc.Tab(
            label='enaR Analysis',
            children=[
                dcc.Graph(
                    figure=enar_asc_fig,
                    id='enar_asc_fig'
                ),
                dcc.Graph(
                    figure=enar_flow_fig,
                    id='enar_flow_fig',
                )
            ]
        ),
        dbc.Tab(
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(
                            figure=econet_utility_fig_dic['TOT'],
                            id='utility_tot',
                        ),
                        dcc.Graph(
                            figure=econet_utility_fig_dic['CUT2'],
                            id='utility_cut2',
                        ),
                        dcc.Graph(
                            figure=econet_utility_fig_dic['ORI'],
                            id='utility_ori',
                        ),
                        dcc.Graph(
                            figure=econet_utility_fig_dic['SHKRAY'],
                            id='utility_shkray',
                        ),
                    ]),
                ], width=6),
                dbc.Col([
                    html.Div([
                        dcc.Graph(
                            figure=econet_utility_fig_dic['CUT3'],
                            id='utility_cut3',
                        ),
                        dcc.Graph(
                            figure=econet_utility_fig_dic['CUT1'],
                            id='utility_cut1',
                        ),
                        dcc.Graph(
                            figure=econet_utility_fig_dic['ESSESH'],
                            id='utility_essesh',
                        ),
                    ]),
                ], width=6),
            ],
            style={
                'margin':'auto',
                'width':'90vw',
            }),
            label='Utility Analysis',
        ),
        dbc.Tab(
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(
                            figure=econet_control_fig_dic['TOT'],
                            id='control_tot',
                        ),
                        dcc.Graph(
                            figure=econet_control_fig_dic['CUT2'],
                            id='control_cut2',
                        ),
                        dcc.Graph(
                            figure=econet_control_fig_dic['ORI'],
                            id='control_ori',
                        ),
                        dcc.Graph(
                            figure=econet_control_fig_dic['SHKRAY'],
                            id='control_shkray',
                        ),
                    ]),
                ], width=6),
                dbc.Col([
                    html.Div([
                        dcc.Graph(
                            figure=econet_control_fig_dic['CUT3'],
                            id='control_cut3',
                        ),
                        dcc.Graph(
                            figure=econet_control_fig_dic['CUT1'],
                            id='control_cut1',
                        ),
                        dcc.Graph(
                            figure=econet_control_fig_dic['ESSESH'],
                            id='control_essesh',
                        ),
                    ]),
                ], width=6),
            ],
                style={
                    'margin':'auto',
                    'width':'90vw',
                }
            ),
            label='Control Analysis',
        ),
        dbc.Tab(
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(
                            figure=mti_fig_dic['TOT'],
                            id='mti_tot',
                        ),
                        dcc.Graph(
                            figure=mti_fig_dic['CUT2'],
                            id='mti_cut2',
                        ),
                        dcc.Graph(
                            figure=mti_fig_dic['ORI'],
                            id='mti_ori',
                        ),
                        dcc.Graph(
                            figure=mti_fig_dic['SHKRAY'],
                            id='mti_shkray',
                        ),
                    ]),
                ], width=6),
                dbc.Col([
                    html.Div([
                        dcc.Graph(
                            figure=mti_fig_dic['CUT3'],
                            id='mti_cut3',
                        ),
                        dcc.Graph(
                            figure=mti_fig_dic['CUT1'],
                            id='mti_cut1',
                        ),
                        dcc.Graph(
                            figure=mti_fig_dic['ESSESH'],
                            id='mti_essesh',
                        ),
                    ]),
                ], width=6),
            ],
                style={
                        'margin':'auto',
                        'width':'90vw',
                    }
            ),
            label='Mixed Trophic Impact',
        ),
        dbc.Tab(
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(
                            figure=keystone_fig_dic['TOT'],
                            id='keystone_tot',
                        ),
                        dcc.Graph(
                            figure=keystone_fig_dic['CUT2'],
                            id='keystone_cut2',
                        ),
                        dcc.Graph(
                            figure=keystone_fig_dic['ORI'],
                            id='keystone_ori',
                        ),
                        dcc.Graph(
                            figure=keystone_fig_dic['SHKRAY'],
                            id='keystone_shkray',
                        ),
                    ]),
                ], width=6),
                dbc.Col([
                    html.Div([
                        dcc.Graph(
                            figure=keystone_fig_dic['CUT3'],
                            id='keystone_cut3',
                        ),
                        dcc.Graph(
                            figure=keystone_fig_dic['CUT1'],
                            id='keystone_cut1',
                        ),
                        dcc.Graph(
                            figure=keystone_fig_dic['ESSESH'],
                            id='keystone_essesh',
                        ),
                    ]),
                ], width=6),
            ],
            style={
                    'margin':'auto',
                    'width':'90vw',
            }
            ),
            label='Keystone Species',
        ),
        dbc.Tab(
            label='Betweenness',
            children=[
                dcc.Graph(
                    figure=betweenness_fig,
                    id='betweenness_plot',
                    style={'width': '80vw', 'height':'90vh', 'margin':'auto'}
                ),
            ]
        ),
    ])
],
style={
                    'margin':'auto',
                    'width':'90vw',
}
)



if __name__ == '__main__':
    app.run_server(debug=True)