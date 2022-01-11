import pandas as pd
from dataset.utils import set_pandas_display_options
from model.CalculateDoc2VecModel import *
import numpy as np
from sklearn.decomposition import PCA
import plotly.express as px
from sklearn.preprocessing import StandardScaler, MinMaxScaler, normalize
from sklearn.metrics import pairwise_distances


def apply_pca(input_matrix):
    # scale input data to unit variance for PCA
    scaled_data = StandardScaler().fit_transform(input_matrix)
    pca = PCA(n_components=2, random_state=31)

    # Create the transformation model for this data. Internally, it gets the rotation matrix and the explained variance
    pcaTr = pca.fit(scaled_data)
    # apply PCA
    rotatedData = pcaTr.transform(scaled_data)

    # Create a data frame with the new variables for the two principal components
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
        # color_continuous_scale='RdBu',
        # color_continuous_midpoint=0.5,
        width=500, height=400
    )
    fig.update_traces(marker=dict(line=dict(width=0,
                                            color=None)),
                      selector=dict(mode='markers'))
    fig.update_layout(coloraxis_showscale=False)
    return fig


def get_tune_id(mod, title, section):
    row = mod.df_section.query(f"title_playlist == '{title}' and section_name == '{section}'")['sectionid']
    sectionid = int(row)
    id = mod.df_train_test.loc[sectionid]['index']

    return {'id': id,
            'sectionid': sectionid,
            'title': title,
            'section': section}


def get_relevant_and_irrelevant_tunes(A, ref, n=10):
    id = ref['id']

    # Calculate Cosine Similarity Matrix
    sim_matrix = 1 - pairwise_distances(A, metric="cosine")
    # get sorted similarities for the reference tune
    similarities = sim_matrix[id]
    sims = sorted(enumerate(similarities), key=lambda item: -item[1])
    # remove the reference tune from the list of similarities
    sims = sims[1:-1]

    df_sim = pd.DataFrame(sims)
    df_sim.columns = ['id', 'score']
    df_sim['sectionid'] = df_sim['id'].apply(lambda id: mod.get_train_test_sectionid(id))
    df_sim['title'] = df_sim['sectionid'].apply(lambda sectionid: mod.sectionid_to_title(sectionid))
    df_sim.set_index('sectionid', inplace=True)

    df_plot = pd.concat([
        df_sim.head(n).assign(relevance='relevant'),
        df_sim.tail(n).assign(relevance='irrelevant')
    ]
    )

    df_plot = df_plot.append({'id': id,
                              'score': 1.0,
                              'title': ref['title'],
                              'relevance': 'reference'
                              },
                             ignore_index=True)

    return df_plot


##
if __name__ == "__main__":
    set_pandas_display_options()
    np.random.seed(31)

    # Configuration
    topn = 15  # number of documents to consider for the relevance feedback

    # Load the LSI Model
    mod = CalculateDoc2VecModel('rootAndDegreesPlus')
    mod.load_model()
    model = mod.doc2vec

    # get the topics for each tune
    df_vectors = mod.get_train_tune_vectors()

    # Before doing Rocchio, normalize vectors to unit length:
    vectors = df_vectors.to_numpy()
    vectors_norm = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    ##
    # Define Reference query

    ref_tune = get_tune_id(mod, 'These Foolish Things [jazz1350]', 'A')
    print(f"Reference Section: {ref_tune['title']}, {ref_tune['section']}")

    ##
    # Define Positive Feedback
    pos_tune = get_tune_id(mod, 'Down For Double [jazz1350]', 'A')
    print(f"Positive Feedback from: {pos_tune['title']}, {pos_tune['section']}")

    ##
    # Get the top-n relevant and irrelevant recommendations for the reference tune
    df_plot = get_relevant_and_irrelevant_tunes(vectors_norm, ref_tune, topn)
    print(df_plot)

    ##
    # PCA: Visualize Vectors of relevant and irrelevant recommendations
    # Note: plots are not identical because StandardScaler is used. Use MinMaxScaler to keep them consistent if needed.
    dataPCA = apply_pca(vectors_norm)
    fig = visualize_pca(pca=dataPCA, subset=df_plot, title=ref_tune['title'], comment=f"Original Query")
    fig.show()

    ##
    # Rocchio

    # create a copy of the weights to enable multiple identical trials
    A = vectors_norm.copy()

    # original vector of the reference tune
    q0 = A[ref_tune['id']]
    vec_positive = A[pos_tune['id']]

    _alpha = 0.8
    _beta = 1.0 - _alpha
    q1 = _alpha * q0 + _beta * vec_positive

    # Update the weights of the reference tune with the new vector
    A[ref_tune['id']] = q1

    # Get the new recommendations
    df_plot2 = get_relevant_and_irrelevant_tunes(A, ref_tune, topn)
    print(df_plot2)
    print()

    # Re-evaluate PCA and visualize
    dataPCA = apply_pca(A)
    fig = visualize_pca(pca=dataPCA, subset=df_plot2, title=ref_tune['title'],
                        comment=f"Rocchio alpha={_alpha:.1f}, beta={_beta:.1f}")
    fig.show()


