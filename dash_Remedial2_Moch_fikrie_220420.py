import pandas as pd
from sqlalchemy import create_engine
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import mysql.connector
conn = mysql.connector.connect(host='localhost',user='root',passwd='323121',use_pure = True, database="ujian_remedial2")
cursor = conn.cursor(dictionary = True)
cursor.execute('SELECT * FROM auto_imports_ujian')
result = cursor.fetchall()
data = pd.DataFrame(result)


# data = pd.read_csv('auto_imports_ujian.csv')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def generate_table(dataframe, page_size = 10):
     return dash_table.DataTable(
                    id = 'dataTable',
                    columns = [{"name": i, "id": i} for i in dataframe.columns],
                    data=dataframe.to_dict('records'),
                    style_table={'overflowX': 'scroll'},
                    page_action="native",
                    page_current= 0,
                    page_size= page_size,
                )

app.layout = html.Div([
        html.H1('Ujian Remedial Modul 2 Dashboard Auto Import'),
        html.P('Created by: Mochammad Fikrie'),
        html.Div([html.Div(children =[
        dcc.Tabs(value = 'tabs', id = 'tabs-1', children = [
            dcc.Tab(value = 'Tabel', label = 'DataFrame Table', children =[
                html.Center(html.H1('DATAFRAME AUTO IMPORTS')),
                html.Div(children =[
                    html.Div(children =[
                        html.P('Fuel-Type:'),
                        dcc.Dropdown(value = '', id='filter-fuel', 
                                    options = [{'label': 'gas', 'value': 'gas'},
                                    {'label': 'diesel', 'value': 'diesel'}])
                    ], className = 'col-3')
                ], className = 'row'),
                html.Div([
                    html.P('Max Rows : '),
                    dcc.Input(
                        id='filter-row',
                        type='number',
                        value=10,
                    )
                ], className = 'row col-3'),
                html.Br(),
                html.Div(children =[
                        html.Button('search',id = 'filter')
                    ],className = 'col-4'),
                html.Br(),    
                html.Div(id = 'div-table', children =[generate_table(data)
            ])
            ]), ### End tab baru disini###


            dcc.Tab(label = 'Bar-Chart', value = 'tab-satu', children=
                [html.Div(children =[
                    html.Div(children =[
                        html.P('Y1:'),    
                        dcc.Dropdown(id = 'y-axis-1', options = [{'label': i, 'value': i} for i in data.select_dtypes('number').columns], 
                        value = 'Wheel-Base')
                    ], className = 'col-3'),

                    html.Div(children =[
                        html.P('Y2:'),    
                        dcc.Dropdown(id = 'y-axis-2', options = [{'label': i, 'value': i} for i in data.select_dtypes('number').columns], 
                        value = 'Height')
                    ], className = 'col-3'),

                    html.Div(children =[
                        html.P('X:'),    
                        dcc.Dropdown(id = 'x-axis-1', options = [{'label': i, 'value': i} for i in ['Drive-Wheels', 'Engine-Location','Engine-Type']], 
                        value = 'Drive-Wheels')
                        ], className = 'col-3')    
                    ], className = 'row'),

                    html.Div([
                    ###Bar-graph###
                        dcc.Graph(
                        id = 'graph-bar',
                        figure ={
                            'data' : [
                                {'x': data['Drive-Wheels'], 'y': data['Wheel-Base'], 'type': 'bar', 'name' :'Wheel-Base'},
                                {'x': data['Drive-Wheels'], 'y': data['Height'], 'type': 'bar', 'name': 'Height'}
                            ], 
                            'layout': {'title': 'Bar Chart'}  
                            }
                        )
                    ])
            ]),###tab Bar-graph ###


            dcc.Tab(label = 'Scatter-Chart', value = 'tab-dua', children =[
                html.Div(children = dcc.Graph(
                id = 'scatter-graph',
                figure = {'data': [
                    go.Scatter(
                        x = data[data['Drive-Wheels'] == i]['Horsepower'],
                        y = data[data['Drive-Wheels'] == i]['Price'],
                        text = data[data['Drive-Wheels'] == i]['Make'],
                        mode='markers',
                        name = '{}'.format(i)
                        ) for i in data['Drive-Wheels'].unique()
                    ],
                    'layout':go.Layout(
                        xaxis= {'title': 'Horsepower'},
                        yaxis={'title': 'Price'},
                        hovermode='closest'
                    )
                    }
                )),
            ]),###Tab Scatter-plot###


            dcc.Tab(label ='Pie-Chart', value = 'tab-tiga', children =[
                html.Div(
                    dcc.Dropdown(id ='pie-dropdown', 
                    options = [{'label': i, 'value': i} for i in data.select_dtypes('number').columns], 
                    value = 'Length'), 
                    className = 'col-3'),
                html.Div([
                    ## Graph Pie
                    dcc.Graph(
                    id = 'pie-graph',
                    figure ={
                        'data' : [
                            go.Pie(labels = ['{}'.format(i) for i in list(data['Fuel-System'].unique())], 
                                    values = [data.groupby('Fuel-System').mean()['Length'][i] for i in list(data['Fuel-System'].unique())],
                                    sort = False)
                        ], 
                            'layout': {'title': 'Mean Pie Chart'}}
                    )
                ])###pie-graph###   
            ])
        ], 
        ###Content Style###
        content_style = {
        'fontFamily': 'Arial',
        'borderBottom': '1px solid #d6d6d6',
        'borderLeft': '1px solid #d6d6d6',
        'borderRight': '1px solid #d6d6d6',
        'padding': '44px'
    })
        ])
    ])
], style ={
        'maxWidth': '1200px',
        'margin': '0 auto'
    })


@app.callback(
    Output(component_id = 'div-table', component_property = 'children'),
    [Input(component_id = 'filter', component_property = 'n_clicks')],
    [State(component_id = 'filter-fuel', component_property = 'value'),
    State(component_id = 'filter-row', component_property = 'value')]
)
def update_table(n_clicks, fuel, row):
    if fuel == '':
        children = [generate_table(data, page_size = row)]
    else:
        children = [generate_table(data[data['Fuel-Type'] == fuel], page_size = row)]            
    return children

@app.callback(
    Output(component_id = 'graph-bar', component_property = 'figure'),
    [Input(component_id = 'y-axis-1', component_property = 'value'),
    Input(component_id = 'y-axis-2', component_property = 'value'),
    Input(component_id = 'x-axis-1', component_property = 'value'),]
)
def create_graph_bar(y1, y2, x1):
    figure = {
                    'data' : [
                        {'x': data[x1], 'y': data[y1], 'type': 'bar', 'name' :y1},
                        {'x': data[x1], 'y': data[y2], 'type': 'bar', 'name': y2}
                    ], 
                    'layout': {'title': 'Bar Chart'}  
                    }
    return figure                


@app.callback(
    Output(component_id = 'pie-graph', component_property = 'figure'),
    [Input(component_id = 'pie-dropdown', component_property = 'value')]
)
def create_graph_pie(x):
    figure = {
                    'data' : [
                        go.Pie(labels = ['{}'.format(i) for i in list(data['Fuel-System'].unique())], 
                                        values = [data.groupby('Fuel-System').mean()[x][i] for i in list(data['Fuel-System'].unique())],
                                        sort = False)
                    ], 
                        'layout': {'title': 'Mean Pie Chart'}}

    return figure                    
    



if __name__ == '__main__':
    app.run_server(debug=True)