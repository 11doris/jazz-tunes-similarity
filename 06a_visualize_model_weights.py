from dataset.utils import set_pandas_display_options
from model.CalculateLsiModel import *
from model.CalculateDoc2VecModel import *
import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import xarray as xr
import umap
from sklearn.manifold import TSNE
import zipfile
import re
from sklearn.decomposition import PCA
import hdbscan

def year_to_decade(year):
    return int(np.floor(year / 10) * 10)

def year_to_period(year):
    _year = int(year)
    if _year == 0:
        return "missing"
    if _year < 1929:
        return "1929"
    if _year < 1939:
        return "1939"
    if _year < 1949:
        return "1949"
    else:
        return "1950+"


def get_model_term_weights(model):
    """
    Returns a dictionary with the model weights as a matrix, with size num_topics x vocab_size
    LSI weights: (100, 446)
    LSI vocab: 446
    """
    if model.model_name == 'lsi':
        topics = mod.lsi.get_topics()
        vocab = list(mod.lsi.id2word.id2token.values())
        return {'weights': topics,
                'vocab': vocab}

    if model.model_name == 'doc2vec':

        return {'weights': model.doc2vec.wv.vectors.T,
                'vocab': model.doc2vec.wv.index_to_key}

def plot_model_weights(model, preprocessing, vocab_weights):
    weights = vocab_weights['weights']
    vocab = vocab_weights['vocab']
    data = xr.DataArray(
        weights,
        coords={
            "weights": list(range(len(weights))),
            "vocab": vocab,
        },
        dims=["weights", "vocab"],
    )
    data = data.sortby("vocab")

    fig = px.imshow(data,
                    title=f"Visualization of {model.model_name} Weights<br><sup>{preprocessing}</sup>",
                    color_continuous_scale='RdBu',
                    #color_continuous_midpoint=0.5,
                    #width=500, height=400
                    )
    fig.update_layout(coloraxis_showscale=False)
    return fig

def plot_section_vectors(model, preprocessing, df):
    data = xr.DataArray(
        df.T,
        coords={
            "topics": list(range(df.shape[1])),
            "sectionid": list(mod.df_section['sectionid']),
        },
        dims=["topics", "sectionid"],
    )

    fig = px.imshow(data,
                    title=f"Visualization of Tune Vectors<br><sup>{preprocessing}</sup>",
                    color_continuous_scale='RdBu',
                    #hover_data=titles['title_section'], # imshow does not have a hover_data function...
                    # color_continuous_midpoint=0.5,
                    # width=500, height=400
                    )
    fig.update_layout(coloraxis_showscale=False)
    return fig


def plot_umap_tunes(df, metric='euclidean', cluster_size=10):
    n_neighbors = 40
    min_dist = 0.01
    umap_2d = umap.UMAP(n_components=2,
                        init='random',
                        random_state=31,
                        n_neighbors=n_neighbors,
                        min_dist=min_dist,
                        metric=metric,
                        )

    scaled_data = MinMaxScaler().fit_transform(df)
    U = umap_2d.fit_transform(scaled_data)
    df_umap = pd.DataFrame(U, columns=['UMAP0', 'UMAP1'])
    df_umap['tune_mode'] = titles['tune_mode']
    df_umap['title_section'] = titles['title_section']
    df_umap['titleid'] = titles['tune_id']
    df_umap['sectionid'] = titles['sectionid']
    df_umap['year'] = titles['year_truncated']
    df_umap['decade'] = df_umap['year'].replace(np.nan, 0).apply(lambda year: year_to_decade(year))
    df_umap['period'] = df_umap['year'].replace(np.nan, 0).apply(lambda year: year_to_period(year))

    # cluster the result
    clusterer = hdbscan.HDBSCAN(min_cluster_size=cluster_size)
    clusterer.fit(U)
    df_umap['cluster'] = clusterer.labels_.astype(str)

    fig = px.scatter(
        df_umap,
        x='UMAP0', y='UMAP1',
        opacity=0.5,
        color=clusterer.labels_.astype(str),
        hover_name='title_section',
        title=f"UMAP for {preprocessing}<br><sup>metric: {metric}, n_neighbors: {n_neighbors}, min_dist: {min_dist}, cluster_size: {cluster_size}</sup>",
        width=800, height=700,
    )
    fig.show()

    # plot
    fig = px.scatter(
        df_umap,
        x='UMAP0', y='UMAP1',
        opacity=0.5,
        color=df_umap['period'].astype(str),
        hover_name='title_section',
        title=f"UMAP for {preprocessing}<br><sup>metric: {metric}, n_neighbors: {n_neighbors}, min_dist: {min_dist}</sup>",
        width=800, height=700,
    )
    fig.show()

    f = 'output/model/umap'
    df_umap.to_csv(f'{f}_{preprocessing}.csv', encoding='utf8', index=None)
    with zipfile.ZipFile(f'{f}_{preprocessing}.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(f'{f}_{preprocessing}.csv')


def plot_tsne_tunes(df, metric='euclidean'):
    perplexity = 10
    init = 'random'
    tsne = TSNE(n_components=2,
                random_state=31,
                perplexity=perplexity,
                metric=metric,
                init=init,
                learning_rate='auto',
                # n_iter_without_progress=200,
                # n_iter=2000
                )
    scaled_data = StandardScaler().fit_transform(df)  # scale to range 0..1 because Hellinger cannot handle negative values

    T = tsne.fit_transform(scaled_data)

    df_tsne = pd.DataFrame(T, columns=['TSNE0', 'TSNE1'])
    df_tsne['tune_mode'] = titles['tune_mode']
    df_tsne['title_section'] = titles['title_section']
    df_tsne['titleid'] = titles['tune_id']
    df_tsne['sectionid'] = titles['sectionid']
    df_tsne['year'] = titles['year_truncated']
    df_tsne['decade'] = df_tsne['year'].replace(np.nan, 0).apply(lambda year: year_to_decade(year))
    df_tsne['period'] = df_tsne['year'].replace(np.nan, 0).apply(lambda year: year_to_period(year))

    fig = px.scatter(
        df_tsne,
        x='TSNE0', y='TSNE1',
        opacity=0.5,
        color='period',
        hover_name='title_section',
        width=800, height=700,
        title=f"T-SNE for {preprocessing}<br><sup>metric: {metric}, perplexity: {perplexity}, init: {init}</sup>"
    )
    return fig

def get_chord_plot_styling(vocab):
    ##
    mode = []
    mode_size = []
    for chord in vocab:
        if chord in ['', '[UNK]']:
            mode.append('UNK')
            mode_size.append(0.1)
        elif re.search("dim", chord):
            mode.append('dim')
            mode_size.append(0.5)
        elif re.search("m7b5$", chord):
            mode.append('m7b5')
            mode_size.append(0.5)
        elif re.search("[A-G][#b]?7$", chord):
            mode.append('dom7')
            mode_size.append(1)
        elif re.search("m$", chord):
            mode.append('min')
            mode_size.append(0.5)
        elif re.search("m7$", chord):
            mode.append('min7')
            mode_size.append(0.5)
        elif 'mM7' in chord:
            mode.append('mM7')
            mode_size.append(0.1)
        elif re.search("[A-G][#b]?M7", chord):
            mode.append('M7')
            mode_size.append(0.5)
        elif re.search("[A-G][#b]?$", chord):
            mode.append('root')
            mode_size.append(3)
        else:
            mode.append('else')
            mode_size.append(0.5)

    _df = pd.DataFrame(list(zip(vocab, mode, mode_size)),
                            columns=['chord', 'mode', 'print_size'])
    return _df


def plot_umap_vocab(vocab_weights, metric='euclidean'):
    weights= vocab_weights['weights'].T
    vocab = vocab_weights['vocab']

    df_style = get_chord_plot_styling(vocab)

    ##
    n_neighbors = 15
    min_dist = 0.1
    umap_2d = umap.UMAP(n_components=2,
                        init='random',
                        random_state=31,
                        n_neighbors=n_neighbors,
                        min_dist=min_dist,
                        metric=metric,
                        )

    scaled_data = MinMaxScaler().fit_transform(weights)
    proj_2d = umap_2d.fit_transform(scaled_data)
    df_umap = pd.DataFrame(proj_2d, columns=['UMAP0', 'UMAP1'])
    df_umap['vocab'] = vocab
    df_umap['print_size'] = df_style['print_size']
    df_umap['mode'] = df_style['mode']

##
    fig = px.scatter(
        df_umap,
        x='UMAP0', y='UMAP1',
        text='vocab',
        color='mode',
        size='print_size',
        opacity=0.5,
        title=f"Vocabulary UMAP, {preprocessing}<br><sup>metric: {metric}, n_neighbors: {n_neighbors}, min_dist: {min_dist}</sup>",
        width=800, height=700,
    )
    fig.update_traces(textposition='top center')
    fig.update_traces(textfont_size=8, selector=dict(type='scatter'))
    return fig


def plot_pca_vocab(vocab_weights, metric='euclidean'):
    weights= vocab_weights['weights'].T
    vocab = vocab_weights['vocab']

    df_style = get_chord_plot_styling(vocab)

    pca = PCA(n_components=2)
    scaled_data = MinMaxScaler().fit_transform(weights)

    pcaTr = pca.fit(scaled_data)
    rotatedData = pcaTr.transform(scaled_data)

    # # Create a data frame with the new variables. We call these new variables PC1 and PC2
    df_pca = pd.DataFrame(data=rotatedData, columns=['PC1', 'PC2'])
    df_pca['vocab'] = vocab
    df_pca['print_size'] = df_style['print_size']
    df_pca['mode'] = df_style['mode']

    fig = px.scatter(
        df_pca,
        x='PC1', y='PC2',
        text='vocab',
        color='mode',
        size='print_size',
        opacity=0.5,
        title=f"Vocabulary PCA, {preprocessing}<br><sup>metric: {metric}</sup>",
        width=800, height=700,
    )
    fig.update_traces(textposition='top center')
    fig.update_traces(textfont_size=8, selector=dict(type='scatter'))
    return fig



##
if __name__ == "__main__":
    set_pandas_display_options()
    np.random.seed(31)

    # select the model
    model = 'doc2vec'
    preprocessing = 'rootAndDegreesPlus'

    # Load the Model
    if model == 'lsi':
        mod = CalculateLsiModel(preprocessing)
    elif model == 'doc2vec':
        mod = CalculateDoc2VecModel(preprocessing)

    mod.load_model()

    # get the LSI topics for the vocab
    vocab_weights = get_model_term_weights(mod)
    # get the LSI topics for each tune
    df_vectors = mod.get_train_tune_vectors()

    if False:
        # a) Plot model weights (topics for LSI)
        fig = plot_model_weights(mod, preprocessing, vocab_weights)
        fig.show()

        # b) Plot Tunes
        fig = plot_section_vectors(mod, preprocessing, df_vectors)
        fig.show()


    ## Plot weights in 2D scatter plot
    #
    titles = mod.get_train_test_meta()
    metric = 'cosine'

    # UMAP
    if False:
        fig = plot_pca_vocab(vocab_weights, metric)
        fig.show()

        fig = plot_umap_vocab(vocab_weights, metric)
        fig.show()

    if True:
        plot_umap_tunes(df_vectors, metric, cluster_size=8)


    # TSNE
    if False:
        fig = plot_tsne_tunes(df_vectors, metric)
        fig.show()
