import pandas as pd
from dataset.utils import set_pandas_display_options
from model.CalculateDoc2VecModel import *
import numpy as np  # Linear algebra library
from sklearn.decomposition import PCA  # PCA library
import pandas as pd  # Data frame library
import plotly.express as px
from sklearn.preprocessing import StandardScaler, MinMaxScaler, normalize
import numpy as np
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine


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
        #color_continuous_scale='RdBu',
        #color_continuous_midpoint=0.5,
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
    mod = CalculateDoc2VecModel('rootAndDegreesPlus')
    mod.load_model()
    model = mod.doc2vec

    # get the topics for each tune
    df_vectors = mod.get_train_tune_vectors()


##
## Before doing Rocchio, normalize vectors to unit length:
    vectors = df_vectors.to_numpy()
    vectors_norm = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


    ##
    # Define Reference query

    title_name = 'These Foolish Things [jazz1350]'
    section_name = 'A'
    row = mod.df_section.query(f"title_playlist == '{title_name}' and section_name == '{section_name}'")['sectionid']
    s1 = int(row)
    print(f"Reference Section: {mod.df.loc[s1]['title_section']}")

    # store the topn relevant and irrelevant recommendations into a dataframe
    id = mod.df_train_test.loc[s1]['index']

    # check if the current tune belongs to the training set, then we can directly access the embedding vector
    if id in model.dv.index_to_key:
        sims = model.dv.similar_by_key(id, topn=len(model.dv.index_to_key))
    else:
        # infer the embedding vector for the tune which is in test set
        vector = model.infer_vector(mod.df_train_test.loc[s1]['chords'])
        sims = model.dv.similar_by_vector(vector, topn=len(model.dv.index_to_key))


    df_sim = pd.DataFrame(sims)
    df_sim.columns = ['id', 'score']
    df_sim['sectionid'] = df_sim['id'].apply(lambda id: mod.get_train_test_sectionid(id))
    df_sim['title'] = df_sim['sectionid'].apply(lambda sectionid: mod.sectionid_to_title(sectionid))
    df_sim.set_index('sectionid', inplace=True)

    df_plot = pd.concat([
        df_sim.head(topn).assign(relevance = 'relevant'),
        df_sim.tail(topn).assign(relevance='irrelevant')
        ]
    )

    df_plot.at[s1, 'id'] = id
    df_plot.at[s1, 'score'] = 1.0
    df_plot.at[s1, 'title'] = title_name
    df_plot.at[s1, 'relevance'] = 'reference'



    ##
    # PCA: Visualize LSI Weights
    # Note: plots are not identical because StandardScaler is used. Use MinMaxScaler to keep them consistent if needed.
    #data = df_vectors.values.tolist()
    data = df_vectors.values.tolist()
    dataPCA = apply_pca(data)
    fig = visualize_pca(pca=dataPCA, subset=df_plot, title=title_name, comment=f"Original Query")
    fig.show()



    ## Rocchio
    df_vectors_original = df_vectors.copy()

    # original vector of the reference tune
    q0 = df_vectors.loc[s1]

    # simulate a positive feedback
    pos_feedback = "Down For Double [jazz1350]"
    pos_sectionid = mod.title_to_sectionid_unique_section(pos_feedback)[0]
    vec_positive = df_vectors.loc[pos_sectionid]


    ##
    # Apply Rocchio
    df_vectors = df_vectors_original.copy()

    _alpha = 0.8
    _beta = 1.0 - _alpha
    q1 = _alpha * q0 + _beta * vec_positive

    # Update the weights of the reference tune with the new vector
    df_vectors.loc[s1] = q1

    # Re-evaluate PCA and visualize
    data = df_vectors.values.tolist()
    dataPCA = apply_pca(data)
    fig = visualize_pca(pca=dataPCA, subset=df_plot, title=title_name, comment=f"Rocchio alpha={_alpha:.1f}, beta={_beta:.1f}")
    fig.show()

    # Calculate Cosine Similarity Matrix
    A = df_vectors.to_numpy()
    sim_matrix = 1 - pairwise_distances(A, metric="cosine")
    # get sorted similarities for the reference tune
    similarities = sim_matrix[id]
    sims = sorted(enumerate(similarities), key=lambda item: -item[1])
    # remove the reference tune from the list of similarities
    sims = sims[1:-1]

    # Create dataframe of the new recommnder result for the reference tune
    df_sim2 = pd.DataFrame(sims)
    df_sim2.columns = ['id', 'score']
    df_sim2['sectionid'] = df_sim2['id'].apply(lambda id: mod.get_train_test_sectionid(id))
    df_sim2['title'] = df_sim2['sectionid'].apply(lambda sectionid: mod.sectionid_to_title(sectionid))
    df_sim2.set_index('sectionid', inplace=True)

    print()