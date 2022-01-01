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


if __name__ == "__main__":
    set_pandas_display_options()

    # Load the LSI Model
    prep = CalculateLsiModel('rootAndDegreesPlus')
    prep.corpus()
    prep.load_model()
    prep.load_similarity_matrix()

    #
    df_vectors = prep.get_tune_vectors()

    # print rows with nan or inf values
    invalid = df_vectors[df_vectors.isin([np.nan, np.inf, -np.inf]).any(1)]
    print(invalid)
    assert(len(invalid) == 0)

    #df_vectors = df_vectors[~df_vectors.isin([np.nan, np.inf, -np.inf]).any(1)]


    ###
    title_name = 'These Foolish Things [jazz1350]'
    sectionid = prep.title_to_sectionid_unique_section(title_name)[1]
    sims = prep.get_similar_tunes(sectionid, 10)

    tunes = []
    for id, score in sims:
        s2 = prep.row_id_to_sectionid(id)
        print(s2, id, prep.sectionid_to_title(s2), score)
        tunes.append(id)

    df_sim = pd.DataFrame(sims).set_index(0)


    ##
    # Visualize LSI Weights with PCA
    if True:
        data = df_vectors.values.tolist()

        # scale to 0..1
        scaled_data = MinMaxScaler().fit_transform(data)
        # max(map(max, scaled_data))
        # min(map(min, scaled_data))

        pca = PCA(n_components=2)

        # Create the transformation model for this data. Internally, it gets the rotation matrix and the explained variance
        pcaTr = pca.fit(scaled_data)
        rotatedData = pcaTr.transform(scaled_data)  # Transform the data base on the rotation matrix of pcaTr

        # # Create a data frame with the new variables. We call these new variables PC1 and PC2
        dataPCA = pd.DataFrame(data=rotatedData, columns=['PC1', 'PC2'])
        dataPCA['title'] = list(prep.df_section['title_playlist'])
        dataPCA['reference'] = 'similar'
        dataPCA.at[prep.sectionid_to_row_id(sectionid), 'reference'] = 'reference'
        dataPCA['size'] = 1.5
        dataPCA.at[prep.sectionid_to_row_id(sectionid), 'size'] = 10.0
        dataPCA['score']= 1.0
        dataPCA.at[tunes, 'score'] = df_sim.iloc[:,0]

        tunes.append(prep.sectionid_to_row_id(sectionid))


        fig = px.scatter(
            dataPCA.iloc[tunes],
            x='PC1', y='PC2',
            title=f'{title_name}',
            hover_name='title',
            color='score',
            symbol='reference',
            symbol_sequence={0:'circle', 1:'x'},
            size='size',
            size_max=12,
            color_continuous_scale='RdBu',
            color_continuous_midpoint=0.5,
            width=500, height=400
        )
        fig.update_traces(marker=dict(line=dict(width=0,
                                                color=None)),
                          selector=dict(mode='markers'))
        fig.update_layout(coloraxis_showscale=False)
        #fig.update_traces(textposition='top center')
        #fig.update_traces(textfont_size=10, selector=dict(type='scatter'))
        fig.show()


