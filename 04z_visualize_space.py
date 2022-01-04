import pandas as pd
from dataset.utils import set_pandas_display_options
from model.CalculateLsiModel import *
import numpy as np  # Linear algebra library
from sklearn.decomposition import PCA  # PCA library
import pandas as pd  # Data frame library
import plotly.express as px
from sklearn.preprocessing import StandardScaler, MinMaxScaler


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
    prep.load_model()
    prep.load_similarity_matrix()

    # get the LSI topics for each tune
    df_vectors = prep.get_train_tune_vectors()

    # make sure there are no nan or inf values in the weights
    invalid = df_vectors[df_vectors.isin([np.nan, np.inf, -np.inf]).any(1)]
    assert(len(invalid) == 0)


    ##
    # Define Reference query

    title_name = 'These Foolish Things [jazz1350]'
    ref_sectionid = prep.title_to_sectionid_unique_section(title_name)[1]

    # store the topn relevant and irrelevant recommendations into a dataframe
    sims = prep.get_similar_tunes(ref_sectionid)

    df_sim = pd.DataFrame(sims)
    df_sim.columns = ['id', 'score']
    df_sim['sectionid'] = df_sim['id'].apply(lambda id: prep.get_train_test_sectionid(id))
    df_sim['title'] = df_sim['sectionid'].apply(lambda sectionid: prep.sectionid_to_title(sectionid))
    df_sim.set_index('sectionid', inplace=True)

    df_plot = pd.concat([
        df_sim.head(topn).assign(relevance = 'relevant'),
        df_sim.tail(topn).assign(relevance='irrelevant')
        ]
    )
    df_plot.at[ref_sectionid, 'relevance'] = 'reference'


    ##
    # PCA: Visualize LSI Weights
    # Note: plots are not identical because StandardScaler is used. Use MinMaxScaler to keep them consistent if needed.
    data = df_vectors.values.tolist()

    dataPCA = apply_pca(data)
    fig = visualize_pca(pca=dataPCA, subset=df_plot, title=title_name, comment=f"Original Query")
    fig.show()



    ## Rocchio

    # original vector of the reference tune
    q0 = df_vectors.loc[ref_sectionid]

    # simulate a positive feedback
    pos_feedback = "Fools Rush In [jazz1350]"
    pos_sectionid = prep.title_to_sectionid_unique_section(pos_feedback)[1]
    vec_positive = df_vectors.loc[pos_sectionid]

    # Apply Rocchio
    _alpha = 0.8
    _beta = 1.0 - _alpha
    q1 = _alpha * q0 + _beta * vec_positive

    # Update the weights of the reference tune with the new vector
    df_vectors.loc[ref_sectionid] = q1

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
    df_vectors.loc[ref_sectionid] = q1

    # Re-evaluate PCA and visualize
    data = df_vectors.values.tolist()
    dataPCA = apply_pca(data)
    fig = visualize_pca(pca=dataPCA, subset=df_plot, title=title_name, comment=f"Rocchio alpha={_alpha:.1f}, beta={_beta:.1f}")
    fig.show()


   ## Centroid of relevant documents (could be used later for Pseudo-relevant Feedback)

    # calculate mean of relevant tunes
    vec_relevant = df_vectors.merge(df_plot.query('relevance == "relevant"')['relevance'], left_index=True, right_index=True)
    vec_relevant = vec_relevant.drop(columns=['relevance'])

    # calculate the vector to the centroid of the relevant documents
    q_relevant_centroid = vec_relevant.mean(axis=0)

    # Apply Rocchio
    _alpha = 0.0
    _beta = 1.0 - _alpha
    q1 = _alpha * q0 + _beta * q_relevant_centroid

    # Update the weights of the reference tune with the new vector
    df_vectors.loc[ref_sectionid] = q1

    # Re-evaluate PCA and visualize
    data = df_vectors.values.tolist()
    dataPCA = apply_pca(data)
    fig = visualize_pca(pca=dataPCA, subset=df_plot, title=title_name, comment=f"Set to Centroid of relevant tunes: alpha={_alpha:.1f}, beta={_beta:.1f}")
    fig.show()
