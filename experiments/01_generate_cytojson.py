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
    _attrs = dict(name="name", ident="id")
    if not attrs:
        attrs = _attrs
    else:
        attrs.update({k: v for (k, v) in _attrs.items() if k not in attrs})

    name = attrs["name"]
    ident = attrs["ident"]

    if len({name, ident}) < 2:
        raise nx.NetworkXError("Attribute names are not unique.")

    jsondata = {"data": list(G.graph.items()),
                "directed": G.is_directed(),
                "multigraph": G.is_multigraph(),
                "elements": {"nodes": [], "edges": []}
                }
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


def parse_single_tunes(corpus, titles):
    i = 0
    for tune in corpus:
        G = nx.DiGraph()
        chords = tune.strip().split(' ')
        G.add_nodes_from(set(chords))

        edges = []
        for index in range(1, len(chords)):
            edges.append([chords[index-1], chords[index]])
        G.add_edges_from(edges)

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


if __name__ == "__main__":

    # read input chord sequences
    with open('../chord_sequences/chords/test_chords-full_relative_key.txt') as f:
        corpus = f.readlines()
    meta_json = json.load(open('../dataset/meta_info.json'))

    # read titles
    titles = []
    for tune in meta_json.items():
        titles.append(tune[1]['title'])

    parse_single_tunes(corpus, titles)
