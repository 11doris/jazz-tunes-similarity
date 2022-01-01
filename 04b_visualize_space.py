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
    df_vectors = pd.read_csv('output/model/weights_tunes_vectors.csv')

    # print rows with nan or inf values
    invalid = df_vectors[df_vectors.isin([np.nan, np.inf, -np.inf]).any(1)]
    print(invalid)
    assert(len(invalid) == 0)

    #df_vectors = df_vectors[~df_vectors.isin([np.nan, np.inf, -np.inf]).any(1)]
    tune_legend = pd.read_csv('output/model/weights_tune_vectors_legend.csv')

    assert(len(df_vectors) == len(tune_legend))

    # Visualize LSI Weights with PCA
    if False:
        data = df_vectors.values.tolist()

        # scale to 0..1
        scaled_data = MinMaxScaler().fit_transform(data)
        # max(map(max, scaled_data))
        # min(map(min, scaled_data))

        pca = PCA(n_components=3)

        # Create the transformation model for this data. Internally, it gets the rotation matrix and the explained variance
        pcaTr = pca.fit(scaled_data)
        rotatedData = pcaTr.transform(scaled_data)  # Transform the data base on the rotation matrix of pcaTr

        # # Create a data frame with the new variables. We call these new variables PC1 and PC2
        dataPCA = pd.DataFrame(data=rotatedData, columns=['PC1', 'PC2', 'PC3'])
        dataPCA['title'] = tune_legend
        projected = pd.DataFrame(dataPCA)

        fig = px.scatter_3d(
            dataPCA,
            x='PC1', y='PC2', z='PC3',
            hover_name='title',
            opacity=0.2,
            #width=500, height=400
        )
        fig.update_traces(textposition='top center')
        fig.update_traces(textfont_size=10, selector=dict(type='scatter'))
        fig.show()


    # Load the LSI Model
    prep = CalculateLsiModel('rootAndDegreesPlus')
    prep.corpus()
    prep.load_model()
    prep.load_similarity_matrix()

    id = prep.title_to_sectionid_unique_section('These Foolish Things [jazz1350]')[1]
    sims = prep.get_similar_tunes(id)

    for id, score in sims:
        s2 = prep.row_id_to_sectionid(id)
        print(s2, prep.sectionid_to_title(s2), score)



