from coronaplots import CoronaPlots

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_table


# data
confirmed_url = ('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/'
                 'master/csse_covid_19_data/csse_covid_19_time_series/'
                 'time_series_covid19_confirmed_global.csv')
deaths_url = ('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/'
              'master/csse_covid_19_data/csse_covid_19_time_series/'
              'time_series_covid19_deaths_global.csv')
recovered_url = ('https://raw.githubusercontent.com/CSSEGISandData/COVID-19'
                 '/master/csse_covid_19_data/csse_covid_19_time_series/'
                 'time_series_covid19_recovered_global.csv')
country_codes_file = './country_codes.csv'

cp = CoronaPlots(confirmed_url, deaths_url, recovered_url, country_codes_file)

choropleth = cp.build_map()
timeline = cp.build_timeline()
summary_table = cp.summary_table
summary = f'''
             **Last update**: {cp.last_update}

             **Number of countries**: {cp.total_countries}

             **Total confirmed cases**: {cp.total_confirmed_cases}
            '''


# setting up DASH server
app = dash.Dash(
    __name__, external_stylesheets=[
        "https://codepen.io/chriddyp/pen/bWLwgP.css",
    ]
)
server = app.server
app.title = 'COVID-19 Live Dashboard'


# app layout
app.layout = html.Div(id='container', children=[
    # header
    html.H1(["Coronavirus (COVID-19) Live Dashboard", ], id='h1'),

    html.Div(id='columns', children=[
        # left column (map)
        html.Div(id='left-col',
                 children=[
                     dcc.Graph(id="map", config={
                         'displayModeBar': False}, figure=choropleth),
                 ]),

        # right column: summary and datatable
        html.Div(id='right-col',
                 children=[
                     html.Div([dcc.Markdown([summary])],
                              id='summary'),

                     dash_table.DataTable(
                         data=summary_table.to_dict('records'),
                         columns=[{'id': c, 'name': c}
                                  for c in summary_table.columns],
                         fixed_rows={'headers': True, 'data': 0},

                         style_cell={
                             'font-family': 'PT Sans',
                             'font-size': '1.4rem',
                         },

                         style_table={
                             'maxHeight': '300px',
                             'overflowY': 'auto',

                         },

                         style_cell_conditional=[

                             {'if': {'column_id': 'Country/Region'},
                              'width': '80px',
                              'textAlign': 'left'},
                             {'if': {'column_id': 'Confirmed'},
                              'width': '85px'},
                         ],
                         style_data_conditional=[
                             {
                              'if': {'row_index': 'odd'},
                              'backgroundColor': 'rgb(248, 248, 248)'
                             }
                         ],
                         style_header={
                             'backgroundColor': 'rgb(230, 230, 230)',
                             'fontWeight': 'bold'
                         },
                         style_as_list_view=True,
                     ),
                 ]), ]),
    # timeline
    dcc.Graph(id="timeline", config={
              'displayModeBar': False}, figure=timeline),
    # footer
    html.Div([dcc.Markdown(('Data source: [COVID-19 (2019-nCoV)'
                            ' Data Repository by Johns Hopkins CSSE]'
                            '(https://github.com/CSSEGISandData/COVID-19)'))],
             id='source'),

])

if __name__ == '__main__':
    app.run_server(debug=True)