import dash
import dash_html_components as html

import dash_cytoscape as cyto
import json

app = dash.Dash(__name__)
server = app.server

# load data
f = open('All Of Me.json')
cyjs = json.load(f)
elements = cyjs['elements']

# define style
styles = {
    'container': {
        'position': 'fixed',
        'display': 'flex',
        'flex-direction': 'column',
        'height': '100%',
        'width': '100%'
    },
    'cy-container': {
        'flex': '1',
        'position': 'relative'
    },
    'cytoscape': {
        'position': 'absolute',
        'width': '100%',
        'height': '100%',
        'z-index': 999
    }
}

my_stylesheet = [
    # Group selectors
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)'
        }
    },

    # Class selectors
    {
        'selector': '.A',
        'style': {
            'background-color': 'red',
            'line-color': 'red'
        }
    },
    {
        'selector': '.B',
        'style': {
            'shape': 'triangle'
        }
    },
    {
        "selector": "node:selected",
        "style": {
            "border-width": "6px",
            "border-color": "#AAD8FF",
            "border-opacity": "0.5",
            "background-color": "#77828C",
            "text-outline-color": "#77828C"
        }
    },
    {
        "selector": "edge",
        "style": {
            "curve-style": "haystack",
            "haystack-radius": "0.5",
            "opacity": "0.4",
            "line-color": "#bbb",
            "width": "mapData(weight, 1, 10, 0, 2)",
            "overlay-padding": "3px"
        }
    }
]

# App
app.layout = html.Div(style=styles['container'], children=[
    html.Div([
        html.Button("Responsive Toggle", id='toggle-button'),
        html.Div(id='toggle-text')
    ]),
    html.Div(className='cy-container', style=styles['cy-container'], children=[
        cyto.Cytoscape(
            id='cytoscape-elements-basic',
            layout={'name': 'cose'},
            style=styles['cytoscape'],
            stylesheet=my_stylesheet,
            elements=elements,
            responsive=True,
        )
    ])
])

app.run_server(debug=True)
