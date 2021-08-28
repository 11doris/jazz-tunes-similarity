import matplotlib.pyplot as plt
import networkx as nx
import random
from operator import itemgetter
import json
import pandas as pd
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import json


def networkx_to_cytoscape(G, attrs=None):
    """Returns data in Cytoscape JSON format (cyjs).

    Parameters
    ----------
    G : NetworkX Graph


    Returns
    -------
    data: dict
        A dictionary with cyjs formatted data.
    Raises
    ------
    NetworkXError
        If values in attrs are not unique.
    """
    if not attrs:
        attrs = dict(name="name", ident="id")
    else:
        attrs.update({k: v for (k, v) in _attrs.items() if k not in attrs})

    name = attrs["name"]
    ident = attrs["ident"]

    if len({name, ident}) < 2:
        raise nx.NetworkXError("Attribute names are not unique.")

    jsondata = {"data": list(G.graph.items())}
    jsondata["directed"] = G.is_directed()
    jsondata["multigraph"] = G.is_multigraph()
    jsondata["elements"] = {"nodes": [], "edges": []}
    nodes = jsondata["elements"]["nodes"]
    edges = jsondata["elements"]["edges"]

    for i, j in G.nodes.items():
        n = {"data": j.copy()}
        n["data"]["id"] = j.get(ident) or str(i)
        n["data"]["value"] = i
        n["data"]["label"] = j.get(name) or str(i)
        nodes.append(n)

    if G.is_multigraph():
        for e in G.edges(keys=True):
            n = {"data": G.adj[e[0]][e[1]][e[2]].copy()}
            n["data"]["source"] = e[0]
            n["data"]["target"] = e[1]
            n["data"]["key"] = e[2]
            edges.append(n)
    else:
        for e in G.edges():
            n = {"data": G.adj[e[0]][e[1]].copy()}
            n["data"]["source"] = e[0]
            n["data"]["target"] = e[1]
            edges.append(n)
    return jsondata


def plot_graph(graph_obj, title="graph.png", seed_val=None):
    # plt.figure(1, figsize=(20,20))
    node_sizes = [graph_obj.degree(n, weight='weight') * 100 for n in graph_obj.nodes]

    plt.figure(1)
    ax = plt.gca()
    ax.set_title(f'{title}, seed value = {seed_val}')
    nx.draw(graph_obj,
            with_labels=True,
            font_size=10,
            alpha=0.4,
            node_size=node_sizes,
            node_color='lightblue',
            pos=nx.spring_layout(G),
            )
    # plt.show()
    plt.savefig(f"{seed_val}_{title}.png", dpi=1000)


def draw_graph3(networkx_graph, notebook=True, output_filename='graph.html', show_buttons=True, directed=True,
                only_physics_buttons=False):
    """
    This function accepts a networkx graph object,
    converts it to a pyvis network object preserving its node and edge attributes,
    and both returns and saves a dynamic network visualization.

    Valid node attributes include:
        "size", "value", "title", "x", "y", "label", "color".

        (For more info: https://pyvis.readthedocs.io/en/latest/documentation.html#pyvis.network.Network.add_node)

    Valid edge attributes include:
        "arrowStrikethrough", "hidden", "physics", "title", "value", "width"

        (For more info: https://pyvis.readthedocs.io/en/latest/documentation.html#pyvis.network.Network.add_edge)


    Args:
        networkx_graph: The graph to convert and display
        notebook: Display in Jupyter?
        output_filename: Where to save the converted network
        show_buttons: Show buttons in saved version of network?
        only_physics_buttons: Show only buttons controlling physics of network?

    source: https://gist.github.com/quadrismegistus/92a7fba479fc1e7d2661909d19d4ae7e
    """

    # import
    from pyvis import network as net

    # make a pyvis network
    pyvis_graph = net.Network(notebook=notebook, directed=directed)

    # for each node and its attributes in the networkx graph
    for node, node_attrs in networkx_graph.nodes(data=True):
        pyvis_graph.add_node(str(node), **node_attrs)

    # for each edge and its attributes in the networkx graph
    for source, target, edge_attrs in networkx_graph.edges(data=True):
        # if value/width not specified directly, and weight is specified, set 'value' to 'weight'
        if not 'value' in edge_attrs and not 'width' in edge_attrs and 'weight' in edge_attrs:
            # place at key 'value' the weight of the edge
            edge_attrs['value'] = edge_attrs['weight']
        # add the edge
        pyvis_graph.add_edge(str(source), str(target), **edge_attrs)

    # turn buttons on
    if show_buttons:
        if only_physics_buttons:
            pyvis_graph.show_buttons(filter_=['physics'])
        else:
            pyvis_graph.show_buttons()
    else:
        pyvis_graph.set_options("""
                            var options = {
                              "nodes": {
                                "color": {
                                  "highlight": {
                                    "border": "rgba(233,206,61,1)",
                                    "background": "rgba(255,229,110,1)"
                                  },
                                  "hover": {
                                    "border": "rgba(19,156,204,1)",
                                    "background": "rgba(136,255,184,1)"
                                  }
                                },
                                "font": {
                                  "size": 26,
                                  "face": "tahoma"
                                }
                              },
                              "edges": {
                                "color": {
                                  "inherit": true
                                },
                                "smooth": false
                              },
                              "interaction": {
                                "hover": true,
                                "multiselect": true,
                                "navigationButtons": true
                              },
                              "physics": {
                                "barnesHut": {
                                  "gravitationalConstant": -26550,
                                  "centralGravity": 1.1,
                                  "springLength": 190,
                                  "springConstant": 0.125,
                                  "avoidOverlap": 0.89
                                },
                                "minVelocity": 0.75
                              }
                            }
    """)

    # return and also save
    return pyvis_graph.show(output_filename)


def plot_single_tunes(corpus, titles):
    i = 0
    for tune in corpus:
        G = nx.DiGraph()
        chords = tune.strip().split(' ')
        G.add_nodes_from(set(chords))

        edges = []
        for index in range(1, len(chords)):
            edges.append([chords[index-1], chords[index]])
        G.add_edges_from(edges)

        #plot_graph(G, f'{titles[i]}', seed_value)
        pp = draw_graph3(G, output_filename=f"{titles[i]}.html", directed=True, show_buttons=False)

        print()
        print(f'{titles[i]}')
        print(f'Number of Edges: {len(G.edges)}')
        print(f'Number of Chords: {len(G.nodes)}')
        print(sorted(G.in_degree(), key=itemgetter(1), reverse=True)[:5])

        # convert data to cytograph format
        cyto_graph = networkx_to_cytoscape(G)
        with open(f"{titles[i]}.json", 'w', encoding='utf-8') as f:
            json.dump(cyto_graph, f, ensure_ascii=False, indent=4)

        i += 1


def plot_all_tunes(corpus):
    G = nx.DiGraph()
    chords_list = []
    for tune in corpus:
        chords = tune.strip().split(' ')
        for index in range(1, len(chords)):
            chords_list.append([chords[index-1], chords[index]])

    df = pd.DataFrame(chords_list)
    df.columns = ['from', 'to']
    dd = df.value_counts(subset=['from', 'to'], sort=False).reset_index(name='weight')

    G = nx.from_pandas_edgelist(dd, 'from', 'to', edge_attr='weight')
    pp = draw_graph3(G, output_filename=f"all_titles.html", directed=False, show_buttons=True)

    F = G.copy()
    threshold = 70
    F.remove_edges_from([(n1, n2) for n1, n2, w in F.edges(data="weight") if w < threshold])
    F.remove_nodes_from(list(nx.isolates(F)))
    pp = draw_graph3(F, output_filename=f"all_titles_filtered.html", directed=True, show_buttons=False)
    print(f"Number of nodes after filtering: {F.number_of_nodes}")

    scatter_plot_2d(F, '.', 'plotly_filt')

    # convert data to cytograph format
    cyto_graph = nx.cytoscape_data(G)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(cyto_graph, f, ensure_ascii=False, indent=4)


def scatter_plot_2d(G, folderPath, name, savePng = False):
    print("Creating scatter plot (2D)...")

    Nodes = [comp for comp in nx.connected_components(G)] # Looks for the graph's communities
    Edges = G.edges()
    edge_weights = nx.get_edge_attributes(G,'weight')

    labels = [] # names of the nodes to plot
    group = [] # id of the communities
    group_cnt = 0

    print("Communities | Number of Nodes")
    for subgroup in Nodes:
        group_cnt += 1
        print("      %d     |      %d" % (group_cnt, len(subgroup)))
        for node in subgroup:
            labels.append(node)
            group.append(group_cnt)

    labels, group = (list(t) for t in zip(*sorted(zip(labels, group))))

    layt = nx.spring_layout(G, dim=2) # Generates the layout of the graph
    Xn = [layt[k][0] for k in list(layt.keys())]  # x-coordinates of nodes
    Yn = [layt[k][1] for k in list(layt.keys())]  # y-coordinates
    Xe = []
    Ye = []

    plot_weights = []
    for e in Edges:
        Xe += [layt[e[0]][0], layt[e[1]][0], None]
        Ye += [layt[e[0]][1], layt[e[1]][1], None]
        ax = (layt[e[0]][0]+layt[e[1]][0])/2
        ay = (layt[e[0]][1]+layt[e[1]][1])/2
        plot_weights.append((edge_weights[(e[0], e[1])], ax, ay))

    annotations_list =[
                        dict(
                            x=plot_weight[1],
                            y=plot_weight[2],
                            xref='x',
                            yref='y',
                            text=plot_weight[0],
                            showarrow=True,
                            arrowhead=7,
                            ax=plot_weight[1],
                            ay=plot_weight[2]
                        )
                        for plot_weight in plot_weights
                    ]

    trace1 = go.Scatter(  x=Xe,
                          y=Ye,
                          mode='lines',
                          line=dict(color='rgb(90, 90, 90)', width=1),
                          hoverinfo='none'
                        )

    trace2 = go.Scatter(  x=Xn,
                          y=Yn,
                          mode='markers+text',
                          name='Nodes',
                          marker=dict(symbol='circle',
                                      size=8,
                                      color=group,
                                      colorscale='Viridis',
                                      line=dict(color='rgb(255,255,255)', width=1)
                                      ),
                          text=labels,
                          textposition='top center',
                          hoverinfo='none'
                          )

    xaxis = dict(
                backgroundcolor="rgb(200, 200, 230)",
                gridcolor="rgb(255, 255, 255)",
                showbackground=True,
                zerolinecolor="rgb(255, 255, 255)"
                )
    yaxis = dict(
                backgroundcolor="rgb(230, 200,230)",
                gridcolor="rgb(255, 255, 255)",
                showbackground=True,
                zerolinecolor="rgb(255, 255, 255)"
                )

    layout = go.Layout(
        title=name,
        width=700,
        height=700,
        showlegend=False,
        plot_bgcolor="rgb(230, 230, 200)",
        scene=dict(
            xaxis=dict(xaxis),
            yaxis=dict(yaxis)
        ),
        margin=dict(
            t=100
        ),
        hovermode='closest',
        annotations=annotations_list
        , )
    data = [trace1, trace2]
    fig = go.Figure(data=data, layout=layout)
    plotDir = folderPath + "/"

    print("Plotting..")

    if savePng:
        plot(fig, filename=plotDir + name + ".html", auto_open=True, image = 'png', image_filename=plotDir + name,
         output_type='file', image_width=700, image_height=700, validate=False)
    else:
        plot(fig, filename=plotDir + name + ".html")




if __name__ == "__main__":

    seed_value = random.randint(1, 10000)
    print(f'Seed: {seed_value}')
    random.seed(seed_value)

    with open('../chord_sequences/chords/test_chords-full_relative_key.txt') as f:
        corpus = f.readlines()

    meta_json = json.load(open('../dataset/meta_info.json'))
    titles = []
    for tune in meta_json.items():
        titles.append(tune[1]['title'])

    plot_single_tunes(corpus, titles)


    with open('../chord_sequences/chords/full_chords-full_relative_key.txt') as f:
        corpus = f.readlines()

    meta_json = json.load(open('../dataset/meta_info.json'))
    titles = []
    for tune in meta_json.items():
        titles.append(tune[1]['title'])

    plot_all_tunes(corpus)
