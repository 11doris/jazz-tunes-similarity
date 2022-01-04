import pandas as pd
from dataset.utils import set_pandas_display_options
from model.CalculateLsiModel import *
import numpy as np  # Linear algebra library
from sklearn.decomposition import PCA  # PCA library
import pandas as pd  # Data frame library
import plotly.express as px
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import xarray as xr
import umap
from sklearn.manifold import TSNE


##
if __name__ == "__main__":
    set_pandas_display_options()
    np.random.seed(31)

    # Load the LSI Model
    mod = CalculateLsiModel('rootAndDegreesPlus')
    mod.load_model()
    #mod.load_similarity_matrix()


    # a) Plot topics
    topics = mod.lsi.get_topics()
    vocab = list(mod.lsi.id2word.id2token.values())

    data = xr.DataArray(
        topics,
        coords={
            "topics": list(range(mod.lsi.num_topics)),
            "vocab": vocab,
        },
        dims=["topics", "vocab"],
    )
    data = data.sortby("vocab")


    fig = px.imshow(data,
                    title="Visualization of Topics",
                    color_continuous_scale='RdBu',
                    #color_continuous_midpoint=0.5,
                    #width=500, height=400
                    )
    fig.update_layout(coloraxis_showscale=False)
    fig.show()


    ###TITLES ARE WRONG; probably use get_train_test_sectionid

    # get the LSI topics for each tune
    df_vectors = mod.get_train_tune_vectors()
    titles = list(mod.df_section['title_playlist'] + ', ' + mod.df_section['section_name'])
    titles = mod.get_train_test_meta()

    # b) Plot Tunes

    if False:
        data = xr.DataArray(
            df_vectors,
            coords={
                "sectionid": list(mod.df_section['sectionid']),
                "topics": list(range(mod.lsi.num_topics)),

            },
            dims=["sectionid", "topics"],
        )

        fig = px.imshow(data,
                        title="Visualization of Topics",
                        color_continuous_scale='RdBu',
                        #color_continuous_midpoint=0.5,
                        #width=500, height=400
                        )
        fig.update_layout(coloraxis_showscale=False)
        fig.show()

    ##
    # UMAP
    if True:
        metric = 'euclidean'
        n_neighbors = 40
        min_dist = 0.01
        umap_2d = umap.UMAP(n_components=2,
                            init='random',
                            random_state=31,
                            n_neighbors=n_neighbors,
                            min_dist=min_dist,
                            metric=metric,
                            )

        scaled_data = MinMaxScaler().fit_transform(df_vectors)  # scale to range 0..1 because Hellinger cannot handle negative values
        proj_2d = umap_2d.fit_transform(scaled_data)
        mapper = umap_2d.fit(scaled_data)

        fig_2d = px.scatter(
            proj_2d,
            x=0, y=1,
            color=titles['tune_mode'],
            hover_name=titles['title_section'],
            title=f"metric: {metric}, n_neighbors: {n_neighbors}, min_dist: {min_dist}",
            width=600, height=500,
        )
        fig_2d.show()


    ## TSNE
    perplexity = 10
    init = 'random'
    tsne = TSNE(n_components=2,
                random_state=31,
                perplexity=perplexity,
                metric='euclidean',
                init=init,
                learning_rate='auto',
                # n_iter_without_progress=200,
                # n_iter=2000
                )
    scaled_data = StandardScaler().fit_transform(df_vectors)  # scale to range 0..1 because Hellinger cannot handle negative values

    T = tsne.fit_transform(scaled_data)

    if True:
        projected = pd.DataFrame(T)

        fig = px.scatter(
            projected,
            x=0, y=1,
            color=titles['tune_mode'],
            hover_name=titles['title_section'],
            width=600, height=500,
            title=f"perplexity: {perplexity}, init: {init}"
        )
        fig.show()
