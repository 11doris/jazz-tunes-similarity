from dataset.utils import set_pandas_display_options
from model.CalculateLsiModel import *
import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import xarray as xr
import umap
from sklearn.manifold import TSNE
import zipfile


##
if __name__ == "__main__":
    set_pandas_display_options()
    np.random.seed(31)

    # Load the LSI Model
    preprocessing = 'rootAndDegreesPlus'
    mod = CalculateLsiModel(preprocessing)
    mod.load_model()


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
        df_umap = pd.DataFrame(proj_2d, columns=['UMAP0', 'UMAP1'])
        df_umap['tune_mode'] = titles['tune_mode']
        df_umap['title_section'] = titles['title_section']
        df_umap['titleid'] = titles['tune_id']
        df_umap['sectionid'] = titles['sectionid']


        fig_2d = px.scatter(
            df_umap,
            x='UMAP0', y='UMAP1',
            opacity=0.5,
            color='tune_mode',
            hover_name='title_section',
            title=f"metric: {metric}, n_neighbors: {n_neighbors}, min_dist: {min_dist}",
            width=600, height=500,
        )
        fig_2d.show()

        f = 'output/model/umap'
        df_umap.to_csv(f'{f}_{preprocessing}.csv', encoding='utf8', index=None)
        with zipfile.ZipFile(f'{f}_{preprocessing}.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(f'{f}_{preprocessing}.csv')

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
            opacity=0.5,
            color=titles['tune_mode'],
            hover_name=titles['title_section'],
            width=600, height=500,
            title=f"perplexity: {perplexity}, init: {init}"
        )
        fig.show()
