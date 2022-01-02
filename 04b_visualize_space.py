import pandas as pd
from dataset.utils import set_pandas_display_options
from model.CalculateLsiModel import *
from model.UseWandB import *
import zipfile
import numpy as np  # Linear algebra library
import matplotlib.pyplot as plt  # library for visualization
from sklearn.decomposition import PCA  # PCA library
import pandas as pd  # Data frame library
import math  # Library for math functions
import random  # Library for pseudo random numbers
import plotly.express as px
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from gensim.models.lsimodel import LsiModel


def apply_pca(input_matrix):

    # scale to 0..1
    scaled_data = MinMaxScaler().fit_transform(input_matrix)
    # max(map(max, scaled_data))
    # min(map(min, scaled_data))

    pca = PCA(n_components=2, random_state=31)

    # Create the transformation model for this data. Internally, it gets the rotation matrix and the explained variance
    pcaTr = pca.fit(scaled_data)
    rotatedData = pcaTr.transform(scaled_data)  # Transform the data base on the rotation matrix of pcaTr

    # # Create a data frame with the new variables. We call these new variables PC1 and PC2
    _df = pd.DataFrame(data=rotatedData, columns=['PC1', 'PC2']).reset_index()
    _df.columns = ['id', 'PC1', 'PC2']

    return _df


def visualize_pca(pca, subset, title="", comment=""):

    df_pca = pca.merge(subset, on='id', how='inner')
    df_pca['marker_size'] = df_pca['relevance'].apply(lambda x: 10.0 if x == 'reference' else 1.5)

    fig = px.scatter(
        df_pca,
        x='PC1', y='PC2',
        title=f"{title}<br><sup>{comment}</sup>",
        hover_name='title',
        color='score',
        symbol='relevance',
        symbol_sequence={0: 'circle', 1: 'x', 2: 'diamond'},
        size='marker_size',
        size_max=12,
        color_continuous_scale='RdBu',
        color_continuous_midpoint=0.5,
        width=500, height=400
    )
    fig.update_traces(marker=dict(line=dict(width=0,
                                            color=None)),
                      selector=dict(mode='markers'))
    fig.update_layout(coloraxis_showscale=False)
    return fig


##
if __name__ == "__main__":
    set_pandas_display_options()
    np.random.seed(31)

    # Configuration
    topn = 15  # number of documents to consider for the relevance feedback

    # Load the LSI Model
    prep = CalculateLsiModel('rootAndDegreesPlus')
    prep.corpus()
    prep.load_model()
    prep.load_similarity_matrix()

    # get the LSI weights for each tune
    df_vectors = prep.get_train_tune_vectors()

    # make sure there are no nan or inf values in the weights
    invalid = df_vectors[df_vectors.isin([np.nan, np.inf, -np.inf]).any(1)]
    #print(invalid)
    assert(len(invalid) == 0)


    ##
    # Define Reference query

    title_name = 'These Foolish Things [jazz1350]'
    sectionid = prep.title_to_sectionid_unique_section(title_name)[0]
    id_ref = prep.sectionid_to_row_id(sectionid)

    # store the topn relevant and irrelevant recommendations into a dataframe
    sims = prep.get_similar_tunes(sectionid)

    df_sim = pd.DataFrame(sims)
    df_sim.columns = ['id', 'score']
    df_sim['sectionid'] = df_sim['id'].apply(lambda id: prep.row_id_to_sectionid(id))
    df_sim['title'] = df_sim['sectionid'].apply(lambda sectionid: prep.sectionid_to_title(sectionid))

    df_plot = pd.concat([
        df_sim.head(topn).assign(relevance = 'relevant'),
        df_sim.tail(topn).assign(relevance='irrelevant')
        ]
    )
    df_plot = df_plot.set_index('id')
    df_plot.at[prep.sectionid_to_row_id(sectionid), 'relevance'] = 'reference'
    df_plot = df_plot.reset_index()


    ##
    # PCA: Visualize LSI Weights
    data = df_vectors.values.tolist()

    dataPCA = apply_pca(data)
    fig = visualize_pca(pca=dataPCA, subset=df_plot, title=title_name, comment=f"Original Query")
    fig.show()



     ## Rocchio

    # original vector of the reference tune
    q0 = df_vectors.iloc[id_ref]

    # simulate a positive feedback
    pos_feedback = "Fools Rush In [jazz1350]"
    sectionid = prep.title_to_sectionid_unique_section(pos_feedback)[1]
    id = prep.sectionid_to_row_id(sectionid)
    vec_positive = df_vectors.iloc[id]

    # Apply Rocchio
    _alpha = 0.8
    _beta = 1.0 - _alpha
    q1 = _alpha * q0 + _beta * vec_positive

    # Update the weights of the reference tune with the new vector
    df_vectors.iloc[id_ref] = q1

    # Re-evaluate PCA and visualize
    data = df_vectors.values.tolist()
    dataPCA = apply_pca(data)
    fig = visualize_pca(pca=dataPCA, subset=df_plot, title=title_name, comment=f"Rocchio alpha={_alpha:.1f}, beta={_beta:.1f}")
    fig.show()


    ##
    # Apply Rocchio
    _alpha = 0.0
    _beta = 1.0 - _alpha
    q1 = _alpha * q0 + _beta * vec_positive

    # Update the weights of the reference tune with the new vector
    df_vectors.iloc[id_ref] = q1

    # Re-evaluate PCA and visualize

    data = df_vectors.values.tolist()
    dataPCA = apply_pca(data)
    fig = visualize_pca(pca=dataPCA, subset=df_plot, title=title_name, comment=f"Rocchio alpha={_alpha:.1f}, beta={_beta:.1f}")
    fig.show()


   ## Centroid of relevant documents (could be used later for Pseudo-relevant Feedback)

    # calculate mean of relevant tunes
    df_plot = df_plot.set_index('id')
    vec_relevant = df_vectors.merge(df_plot.query('relevance == "relevant"')['relevance'], left_index=True, right_index=True)
    vec_relevant = vec_relevant.drop(columns=['relevance'])

    # calculate the vector to the centroid of the relevant documents
    q_relevant_centroid = vec_relevant.mean(axis=0)

    # Apply Rocchio
    _alpha = 0.0
    _beta = 1.0 - _alpha
    q1 = _alpha * q0 + _beta * q_relevant_centroid

    # Update the weights of the reference tune with the new vector
    df_vectors.iloc[id_ref] = q1

    # Re-evaluate PCA and visualize
    data = df_vectors.values.tolist()
    dataPCA = apply_pca(data)
    fig = visualize_pca(pca=dataPCA, subset=df_plot, title=title_name, comment=f"Set to Centroid of relevant tunes: alpha={_alpha:.1f}, beta={_beta:.1f}")
    fig.show()
