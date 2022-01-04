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


def year_to_decade(year):
    return int(np.floor(year / 10) * 10)

def year_to_period(year):
    _year = int(year)
    if _year == 0:
        return "missing"
    if _year < 1919:
        return "1919"
    if _year < 1929:
        return "1929"
    if _year < 1939:
        return "1939"
    if _year < 1949:
        return "1949"
    else:
        return "1950+"


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
                    title=f"Visualization of LSI Topics<br><sup>{preprocessing}</sup>",
                    color_continuous_scale='RdBu',
                    #color_continuous_midpoint=0.5,
                    #width=500, height=400
                    )
    fig.update_layout(coloraxis_showscale=False)
    fig.show()


    # get the LSI topics for each tune
    df_vectors = mod.get_train_tune_vectors()
    titles = mod.get_train_test_meta()

    # b) Plot Tunes

    if True:
        data = xr.DataArray(
            df_vectors.T,
            coords={
                "topics": list(range(mod.lsi.num_topics)),
                "sectionid": list(mod.df_section['sectionid']),
            },
            dims=["topics", "sectionid"],
        )

        fig = px.imshow(data,
                        title=f"Visualization of Tune Vectors<br><sup>{preprocessing}</sup>",
                        color_continuous_scale='RdBu',
                        #color_continuous_midpoint=0.5,
                        #width=500, height=400
                        )
        fig.update_layout(coloraxis_showscale=False)
        fig.show()

    ##
    # UMAP
    if True:
        metric = 'cosine'
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
        df_umap['year'] = titles['year_truncated']
        df_umap['decade'] = df_umap['year'].replace(np.nan, 0).apply(lambda year: year_to_decade(year))
        df_umap['period'] = df_umap['year'].replace(np.nan, 0).apply(lambda year: year_to_period(year))

        title = 'These Foolish Things [jazz1350], B'
        index_tune = df_umap[df_umap['title_section'] == title].index
        df_umap['size'] = 3
        df_umap.at[index_tune, 'size'] = 30

        fig_2d = px.scatter(
            df_umap,
            x='UMAP0', y='UMAP1',
            opacity=0.5,
            color=df_umap['period'].astype(str),
            hover_name='title_section',
            size='size',
            size_max=30,
            title=f"UMAP for {preprocessing}<br><sup>metric: {metric}, n_neighbors: {n_neighbors}, min_dist: {min_dist}</sup>",
            #width=600, height=500,
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
                metric=metric,
                init=init,
                learning_rate='auto',
                # n_iter_without_progress=200,
                # n_iter=2000
                )
    scaled_data = StandardScaler().fit_transform(df_vectors)  # scale to range 0..1 because Hellinger cannot handle negative values

    T = tsne.fit_transform(scaled_data)

    df_tsne = pd.DataFrame(T, columns=['TSNE0', 'TSNE1'])
    df_tsne['tune_mode'] = titles['tune_mode']
    df_tsne['title_section'] = titles['title_section']
    df_tsne['titleid'] = titles['tune_id']
    df_tsne['sectionid'] = titles['sectionid']
    df_tsne['year'] = titles['year_truncated']
    df_tsne['decade'] = df_umap['year'].replace(np.nan, 0).apply(lambda year: year_to_decade(year))
    df_tsne['period'] = df_umap['year'].replace(np.nan, 0).apply(lambda year: year_to_period(year))

    fig = px.scatter(
        df_tsne,
        x='TSNE0', y='TSNE1',
        opacity=0.5,
        color='period',
        hover_name='title_section',
        #width=600, height=500,
        title=f"T-SNE for {preprocessing}<br><sup>metric: {metric}, perplexity: {perplexity}, init: {init}</sup>"
    )
    fig.show()
