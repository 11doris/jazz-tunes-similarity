# -*- coding: utf-8 -*-
"""colab_g_recommender_score

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/11doris/jazz-maestro/blob/colab_word_embeddings/model_01_lsi_sections.ipynb

# Sections as Input
"""

pip install wandb

!wandb login

import wandb

!pip uninstall gensim -y

!pip install gensim

!pip install hdbscan

import hdbscan

!pip install umap-learn

!pip install umap-learn[plot]

import umap
import umap.plot

import gensim
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
import pprint
import pandas as pd
import numpy as np
from collections import Counter
import plotly.express as px
from tqdm import tqdm 
from gensim.models.doc2vec import Doc2Vec
from gensim.models.tfidfmodel import TfidfModel
from gensim.models.lsimodel import LsiModel
from gensim.models import CoherenceModel
from gensim import corpora
from gensim import similarities
import pickle
import os
import zipfile

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

print(gensim.__version__)

!rm data.csv

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

"""# Configuration

"""

use_wandb = True

generate_webapp_data = True

docu = 'sections'
chords_preprocessing = 'rootAndDegreesSimplified'

ngrams_for_input = [1,2]

remove_repetitions = False

input_files = {
    'sections': {
        # M7 and 6 reduced to major triad, m7 reduced to m, dominant 7, m7b5, diminished, and all (b5) left as they are.
        'rootAndDegreesPlus': '1NP6trpfnEPnFqJbmcuClvkBB28PNdF8c',
        'rootAndDegrees7': '',
        'rootAndDegreesSimplified': '1vyC9voFf2vpcKmS5kZBJ9Rafm7wuuzD8',
    },
}

contrafacts = [
               ("26-2 [jazz1350]", "Confirmation [jazz1350]"),
               ("52nd Street Theme [jazz1350]", "I Got Rhythm [jazz1350]"), # not a good match
               ("Ablution [jazz1350]", "All The Things You Are [jazz1350]"),
               ("Anthropology [jazz1350]", "I Got Rhythm [jazz1350]"),
               ("Bright Mississippi [jazz1350]", "Sweet Georgia Brown [jazz1350]"),
               ("C.T.A. [jazz1350]", "I Got Rhythm [jazz1350]"),
               #( "Celia [jazz1350]", "I Got Rhythm [jazz1350]"),
               ("Cottontail [jazz1350]", "I Got Rhythm [jazz1350]"),
               ("Countdown [jazz1350]", "Tune Up [jazz1350]"),
               ("Dewey Square [jazz1350]", "Oh, Lady Be Good [jazz1350]"),
               ("Dexterity [jazz1350]", "I Got Rhythm [jazz1350]"),
               ("Dig [jazz1350]", "Sweet Georgia Brown [jazz1350]"),
               ("Donna Lee [jazz1350]", "Indiana (Back Home Again In) [jazz1350]"),
               ("Don't Be That Way [jazz1350]", "I Got Rhythm [jazz1350]"),  # cannot be found; bridge in different key
               #("Eternal Triangle [jazz1350]", "I Got Rhythm [jazz1350]"),
               ("Evidence [jazz1350]", "Just You, Just Me [jazz1350]"),
               ("Flintstones [jazz1350]", "I Got Rhythm [jazz1350]"),
               ("Four On Six [jazz1350]", "Summertime [jazz1350]"),
               ("Freight Train [jazz1350]", "Blues For Alice [jazz1350]"),
               ("Good Bait [jazz1350]", "I Got Rhythm [jazz1350]"),  # A sections
               ("Hackensack [jazz1350]", "Oh, Lady Be Good [jazz1350]"),
               ("Half Nelson [jazz1350]", "Lady Bird [jazz1350]"),
               ("Hot House [jazz1350]", "What Is This Thing Called Love [jazz1350]"),
               ("Impressions [jazz1350]", "So What [jazz1350]"),
               ("In A Mellow Tone (In A Mellotone) [jazz1350]", "Rose Room [jazz1350]"),
               ("In Walked Bud [jazz1350]", "Blue Skies [jazz1350]"),
               ("Ko Ko [jazz1350]", "Cherokee [jazz1350]"),
               ("Lennie's Pennies [jazz1350]", "Pennies From Heaven [jazz1350]"),   ## Lennie's Pennies is in minor and therefore transposed to Amin... not possible to recognize like that
               #( "Let's Call This [jazz1350]", "Honeysuckle Rose [jazz1350]"),
               ("Little Rootie Tootie [jazz1350]", "I Got Rhythm [jazz1350]"),
               ("Little Willie Leaps [jazz1350]", "All God's Chillun Got Rhythm [jazz1350]"),
               ("Lullaby Of Birdland [jazz1350]", "Love Me Or Leave Me [jazz1350]"),
               #("Moose The Mooche [jazz1350]", "I Got Rhythm [jazz1350]"),
               ("My Little Suede Shoes [jazz1350]", "Jeepers Creepers [jazz1350]"),
               #("Oleo [jazz1350]", "I Got Rhythm [jazz1350]"),
               ("Ornithology [jazz1350]", "How High The Moon [jazz1350]"),
               #("Passport [jazz1350]", "I Got Rhythm [jazz1350]"),
               ("Quasimodo (Theme) [jazz1350]", "Embraceable You [jazz1350]"),
               #("Rhythm-a-ning [jazz1350]", "I Got Rhythm [jazz1350]"),
               ("Room 608 [jazz1350]", "I Got Rhythm [jazz1350]"),
               #("Salt Peanuts [jazz1350]", "I Got Rhythm [jazz1350]"),
               ("Satellite [jazz1350]", "How High The Moon [jazz1350]"),
               ("Scrapple From The Apple [jazz1350]", "Honeysuckle Rose [jazz1350]"), # A section
               ("Scrapple From The Apple [jazz1350]", "I Got Rhythm [jazz1350]"), # B section
               #("Segment [jazz1350]", "I Got Rhythm [jazz1350]"),
               #("Seven Come Eleven [jazz1350]", "I Got Rhythm [jazz1350]"),
               #("Shaw 'Nuff [jazz1350]", "I Got Rhythm [jazz1350]"),
               #("Theme, The [jazz1350]", "I Got Rhythm [jazz1350]"),
               ("Tour De Force [jazz1350]", "Jeepers Creepers [jazz1350]"),
               ("Wow [jazz1350]", "You Can Depend On Me [jazz1350]"),
               ("Yardbird Suite [jazz1350]", "Rosetta [jazz1350]"),

               # following tunes are not from wikipedia),
               ("Sweet Sue, Just You [jazz1350]", "Honeysuckle Rose [jazz1350]"),  # A section
               #("All Of Me [jazz1350]", "Pennies From Heaven [jazz1350]"), # bars 25-28 of All of Me are same as bars 17-20 of Pennies From Heaven, but different key!
               ("Sweet Sue, Just You [jazz1350]", "Bye Bye Blackbird [jazz1350]"), # Bridge same
               ("These Foolish Things [jazz1350]", "Blue Moon [jazz1350]"), # first 8 bars same
               ("These Foolish Things [jazz1350]", "More Than You Know [jazz1350]"),
               ("These Foolish Things [jazz1350]", "Isn't It A Pity [jazz1350]"),
               ("These Foolish Things [jazz1350]", "Soultrane [jazz1350]"),
               ("These Foolish Things [jazz1350]", "Why Do I Love You [jazz1350]"),
               ("Misty [jazz1350]", "Portrait Of Jennie [jazz1350]"),
               ("Misty [jazz1350]", "September In The Rain [jazz1350]"),
               ("Misty [jazz1350]", "I May Be Wrong [jazz1350]"),  

               # identical tunes
               ("Five Foot Two [trad]", "Please Don't Talk About Me When I'm Gone [trad]"),
               ("What Is This Thing Called Love [jazz1350]", "Subconscious Lee [jazz1350]"),
               ("Sweet Georgia Brown [jazz1350]", "Dig [jazz1350]"),


               # almost identical tunes
               ("What Is This Thing Called Love [jazz1350]", "Hot House [jazz1350]"),
               ("Jeannie's Song [jazz1350]", "Shiny Stockings [jazz1350]"),
               ("Alone Together [jazz1350]", "Segment [jazz1350]"),
               ("Baubles, Bangles and Beads [jazz1350]", "Bossa Antigua [jazz1350]"),
               ("There Will Never Be Another You [jazz1350]", "A Weaver Of Dreams [jazz1350]"),
               ("Moten Swing [jazz1350]", "Once In A While (Ballad) [trad]"), # same bridge, similar A
               ("All I Do Is Dream Of You [trad]", "L-O-V-E [jazz1350]"),


               # same A section
               ("Nancy (With The Laughing Face) [jazz1350]", "Body And Soul [jazz1350]"),
               ("Exactly Like You [jazz1350]", "True (You Don't Love Me ) [trad]"),
               ("Exactly Like You [jazz1350]", "Jersey Bounce [jazz1350]"),
               ("Take The A Train [jazz1350]", "Girl From Ipanema, The [jazz1350]"),
               ("My Heart Stood Still [jazz1350]", "All Too Soon [jazz1350]"),
               ("Undecided [jazz1350]", "Broadway [jazz1350]"),
               ("Let's Fall In Love [jazz1350]", "Heart And Soul [jazz1350]"),
               ("Come Back To Me [jazz1350]", "I Wish I Knew [jazz1350]"),
               ("Wait Till You See Her [jazz1350]", "A Certain Smile [jazz1350]"),
               ("Killer Joe [jazz1350]", "Straight Life [jazz1350]"),
               ("Softly, As In A Morning Sunrise [jazz1350]", "Segment [jazz1350]"),
               ("Bei Mir Bist Du Schon (Root Hog Or Die) [trad]", "Egyptian Fantasy [trad]"),
               ("Bei Mir Bist Du Schon (Root Hog Or Die) [trad]", "Puttin' On The Ritz [jazz1350]"),
               ("Coquette [trad]", "Pretend You're Happy When You're Blue [trad]"),
               ("Softly, As In A Morning Sunrise [jazz1350]", "Strode Rode [jazz1350]"),
               ("Glory Of Love, The [jazz1350]", "I've Got My Fingers Crossed [trad]"),
               ("Charleston, The [jazz1350]", "As Long As I Live [trad]"),
               ("Fine And Dandy [jazz1350]", "I Can't Give You Anything But Love [jazz1350]"),
               ("I'll Close My Eyes [jazz1350]", "Bluesette [jazz1350]"),
               ("I'll Close My Eyes [jazz1350]", "There Will Never Be Another You [jazz1350]"),



               # same bridge
               ("If I Had You [jazz1350]", "Too Young To Go Steady [jazz1350]"),
               ("Undecided [jazz1350]", "Satin Doll [jazz1350]"),
               ("Billy Boy [jazz1350]", "Elora [jazz1350]"),
               ("Dearly Beloved [jazz1350]", "We See [jazz1350]"),
               ("Alone Together [jazz1350]", "A Night In Tunisia [jazz1350]"),
               ("A Night In Tunisia [jazz1350]", "Segment [jazz1350]"),
               ("Oh! Lady Be Good [trad]", "Sentimental Journey [jazz1350]"),
               ("You Can Depend On Me [jazz1350]", "Move [jazz1350]"),
               ("I Want To Be Happy [jazz1350]", "A Beautiful Friendship [jazz1350]"),
               ("Flying Home [jazz1350]", "Down For Double [jazz1350]"),
               ("Cheek To Cheek [jazz1350]", "Violets For Your Furs [jazz1350]"),
               ("Let's Fall In Love [jazz1350]", "At Last [jazz1350]"),
               ("Don't Be That Way [jazz1350]", "Long Ago And Far Away [jazz1350]"),
               ("On The Sunny Side Of The Street [jazz1350]", "I'm Confessin' That I Love You [jazz1350]"),
               ("On The Sunny Side Of The Street [jazz1350]", "Eclypso [jazz1350]"),
               ("On The Sunny Side Of The Street [jazz1350]", "You Stepped Out Of A Dream [jazz1350]"),
               ("Satin Doll [jazz1350]", "Undecided [jazz1350]"),
               

               

               # similar A section
               ("I Like The Likes Of You [jazz1350]", "Mountain Greenery [jazz1350]"),
               ("My Secret Love [jazz1350]", "Samba De Orfeu [jazz1350]"),
               ("Let's Call The Whole Thing Off [jazz1350]", "Fine And Dandy [jazz1350]"),


               # similar B section
               ("Folks Who Live On The Hill, The [jazz1350]", "My One And Only Love [jazz1350]"),
               ("As Long As I Live [trad]", "I'm Glad There Is You [jazz1350]"),
               ("I May Be Wrong [jazz1350]", "Teach Me Tonight [jazz1350]"),
               ("Am I Blue [jazz1350]", "Come Back To Me [jazz1350]"),
               ("My One And Only Love [jazz1350]", "Am I Blue [jazz1350]"),
               ("On The Sunny Side Of The Street [jazz1350]", "September In The Rain [jazz1350]"),
               ("On The Sunny Side Of The Street [jazz1350]", "Mountain Greenery [jazz1350]"),
               ("On The Sunny Side Of The Street [jazz1350]", "There's No You [jazz1350]"),
               ("These Foolish Things [jazz1350]", "Embraceable You [jazz1350]"),
               ("These Foolish Things [jazz1350]", "Rosetta [jazz1350]"),

               # same C section
               ("Bill Bailey [jazz1350]", "Bourbon Street Parade [jazz1350]"),

               # Stella C is like Woody B
               ("Woody'n You [jazz1350]", "Stella By Starlight [jazz1350]"),

               # similar vocabulary, different progressions
               ("Tangerine [jazz1350]", "Tea For Two [jazz1350]"),
               ("I Can't Give You Anything But Love [jazz1350]", "You Can Depend On Me [jazz1350]"),
               ("This Year's Kisses [jazz1350]", "My Monday Date [trad]"),
               ("A Blossom Fell [jazz1350]", "Among My Souvenirs [jazz1350]"),

]

test_tunes = []
for ref, sim in contrafacts:
  if ref not in test_tunes:
    test_tunes.append(ref)
  if sim not in test_tunes:
    test_tunes.append(sim)

test_tunes.sort()
len(test_tunes)

test_contrafacts = [
               ("These Foolish Things [jazz1350]", "Why Do I Love You [jazz1350]"),
]

len(contrafacts)

"""# Initialization

## Download the Data
"""

input_data = input_files['sections'][chords_preprocessing]

input_path = f"https://docs.google.com/uc?export=download&id={input_data}"
data_file_name = 'data.csv'

input_path

!wget --no-check-certificate "$input_path" -O "$data_file_name"

"""### Read Chords Input Data"""

df = pd.read_csv(data_file_name, sep='\t', index_col="id")
df = df.reset_index()
df.head(5)

df.shape

"""### Meta Data"""

titles = df.loc[:, ['id', 'tune_id', 'section_id', 'section_name', 'title', 'title_playlist', 'tune_mode']]
titles[:5]

titles_dict = titles.to_dict()

sectionid_to_title = titles_dict['title_playlist']
sectionid_to_titleid = titles_dict['tune_id']

tunes = df.loc[:, ['tune_id', 'title_playlist']].drop_duplicates()
tunes = tunes.set_index('tune_id').to_dict()
titleid_to_title = tunes['title_playlist']

len(titleid_to_title)

title_to_titleid = {v: k for k, v in titleid_to_title.items()}

titles_rows = titles.to_dict(orient='records')
sectionid_to_section = []
for i, row in enumerate(titles_rows):
  name = f"{row['title']}, section{row['section_id']} ({row['section_name']})"
  sectionid_to_section.append(name)

sectionid_to_sectionlabel = []
for i, row in enumerate(titles_rows):
  sectionid_to_sectionlabel.append(row['section_name'])

title_to_sectionid = {}

for row in titles.iterrows():
  title = row[1]['title_playlist']
  if title not in title_to_sectionid:
    title_to_sectionid[title] = [row[1]['id']]
  else:
    title_to_sectionid[title].append(row[1]['id'])

"""### Create Directories on Colab"""

!rm -R output
!mkdir output

"""## Initialization for wandb variables"""

recommender_results_cols = ['reference', 'id', 'method', 'similar', 'score_div_max', 'score']
recommender_results = pd.DataFrame(columns=recommender_results_cols)

lsi_config = {
    'num_topics': 70 #22, # 100 gives a better value for the contrafacts test
}

if use_wandb:
  wandb.init(
        # Set entity to specify your username or team name
        # ex: entity="carey",
        # Set the project where this run will be logged
        project="lsi_model", 
        
        # Track hyperparameters and run metadata
        config={
            "input_data": input_path,
            "chords_preprocessing": chords_preprocessing,
            "ngrams_input": ngrams_for_input,
            "comparison": docu,
            "lsi": lsi_config,
            "remove_repeated_chords": remove_repetitions,
            "comment": ""
        }
    )

if use_wandb:
  artifact = wandb.Artifact('input_data', type='dataset')
  artifact.add_file('data.csv')
  wandb.log_artifact(artifact)

"""## Helpers functions"""

def ngrams(tokens, n=2, sep='-'):
    return [sep.join(ngram) for ngram in zip(*[tokens[i:] for i in range(n)])]

def raw_chords_to_df(tunes):
  tunes_chords = [item for tune in tunes for item in tune]
  counts = Counter(tunes_chords)
  df = pd.DataFrame(counts.items(),
                    columns=['chord', 'count']).sort_values(by='count', ascending=False)

  return df

"""# Data Preparation"""

def remove_chord_repetitions(chords):
  previous = ''
  chords_norep = []
  for c in chords:
    if c != previous:
      chords_norep.append(c)
      previous = c
  return chords_norep

lines = df.loc[:, 'chords'].tolist()
data = [line.split(' ') for line in lines]

test_tunes[:5]

test_tune_sectionid = []
for title in test_tunes:
  test_tune_sectionid.extend(title_to_sectionid[title])

test_tune_sectionid[:10]

len(data)

processed_corpus = []
test_corpus = []

#for line in data:
for id, line in enumerate(data):  
  tune_n = []
  if remove_repetitions:
    line = remove_chord_repetitions(line)
  for n in ngrams_for_input:
    tune_n.extend(ngrams(line, n=n))
  processed_corpus.append(tune_n)
  if id not in test_tune_sectionid:
    test_corpus.append(tune_n)

for line in processed_corpus[:10]:
  print(line)

len(processed_corpus)

"""#### Corpus Overview"""

tokens = [item for l in processed_corpus for item in l]
total_tokens = len(tokens)
vocab_size = len(set(tokens))
vocab_prop = 100*vocab_size/total_tokens

print(f"Total Number of tokens: {total_tokens}")
print(f"Size of vocabulary: {vocab_size}")
print(f"Proportion of vocabulary in corpus: {vocab_prop:.02f}%")

df_chords = raw_chords_to_df(processed_corpus)
df_chords.head(10)

df_chords = pd.DataFrame.from_dict(df_chords)
df_chords.sort_values(by=['count'], ascending=False, inplace=True)
df_chords_top = df_chords.query('count > 100')

fig = px.bar(df_chords_top, x='chord', y='count', log_y=True)
fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
fig.show()

"""Plot Distribution accoring to Zipf's Law

source: https://stats.stackexchange.com/questions/331219/characterizing-fitting-word-count-data-into-zipf-power-law-lognormal
"""

from collections import Counter

counter_of_words = df_chords.set_index('chord').to_dict(orient='dict')
counter_of_words = Counter(counter_of_words['count'])

word_counts = sorted(counter_of_words.values(), reverse=True)
frequency_rank = np.array(list(range(1, len(word_counts) + 1)))

plt.figure(figsize=(20, 3))

plt.subplot(1, 2, 1)

n = 30
df_top = df_chords_top.head(n)
plt.bar(df_top['chord'], np.log(df_top['count']))
plt.xlabel('')
plt.ylabel('Absolute Counts (log)')
plt.title(f'Top {n} Most Frequent Chords in the Corpus')
ax = plt.gca()
ax.set_xticklabels(labels=df_chords_top['chord'],rotation=90);

plt.subplot(1, 2, 2)

plt.scatter(np.log(frequency_rank), np.log(word_counts))
plt.xlabel('Frequency Rank of Token (log)')
plt.ylabel('Absolute Count of Token (log)')
plt.title('Zipf Plot for Chord Frequencies')

plt.savefig('plot.png')

plt.figure(figsize=(22, 3))

n = 100

df_top = df_chords_top.head(n)
plt.bar(df_top['chord'], np.log(df_top['count']))
plt.xlabel('')
plt.ylabel('Absolute Counts (log)')
plt.title(f'Top {n} Most Frequent Chords and n-gram Chords in the Corpus')
ax = plt.gca()
ax.set_xticklabels(labels=df_chords_top['chord'],rotation=90);

if use_wandb:
  wandb.log(
      {"corpus": {
              "total_tokens": total_tokens,
              "vocab_size": vocab_size,
              "vocab_proportion_in_corpus": vocab_prop,
              "zipf_plot": wandb.Image('plot.png'),
              "data_encoding": "bow",
              }
      }
  )

!rm -R index
!mkdir index

"""## Test Functions

"""

def get_sim_scores(tunes, index, model, topn=50):

    df_sim = pd.DataFrame(columns=['reference_title',
                                   'reference_titleid',
                                   'similar_title',
                                   'similar_titleid',
                                   'ref_section', 
                                   'ref_section_label',
                                   'ref_sectionid',
                                   'similar_section',
                                   'similar_section_label',
                                   'similar_sectionid',
                                   'score', 
                                  ])

    for tune in tqdm(tunes):
      for s1 in title_to_sectionid[tune]:
      
          query = processed_corpus[s1]
          query_bow = dictionary.doc2bow(query)

          # perform a similarity query against the corpus
          similarities = index[model[query_bow]]
          sims = sorted(enumerate(similarities), key=lambda item: -item[1])
          
          n = 0
          for s2, s2_score in sims:
            
            # store the top N best results
            if n > topn:
                break
            # don't count self-similarity between sections of the same tune
            if s2 not in title_to_sectionid[tune]:
                # print(f"\t{s2_score:.3f} {sectionid_to_section[s2]}")
                n += 1
                df_sim.loc[len(df_sim)] = [tune,
                                           title_to_titleid[tune],
                                           sectionid_to_title[s2],
                                           sectionid_to_titleid[s2],
                                           sectionid_to_section[s1],
                                           sectionid_to_sectionlabel[s1],
                                           s1,
                                           sectionid_to_section[s2], 
                                           sectionid_to_sectionlabel[s2],
                                           s2,
                                           s2_score, 
                                           ]
    return df_sim

"""## Test Contrafacts

With the model, query the top N highest matches for each section. For a tune, if at least one section receives the recommendation  for the expected title, increase the match counter.
"""

def test_contrafacts(tunes, index, model, N=15):
  matches = 0
  number_of_sections = 0
  results = {}

  for tune, similar_tune in tunes:

    # loop over all sections of the tune
    section_matches = 0
    rank = 0
    score = 0

    for s1 in title_to_sectionid[tune]:
      query = processed_corpus[s1]
      query_bow = dictionary.doc2bow(query) 

      # perform a similarity query against the corpus
      similarities = index[model[query_bow]]
      sims = sorted(enumerate(similarities), key=lambda item: -item[1])
      #print(f"s1: {s1}")
      #print(f"similar_tune: {similar_tune}, {title_to_sectionid[similar_tune]}")
      #print(sims)
      #print(len(sims))
      
      # check if the section matches the expected title; consider only the first N recommendations
      i = 0
      for sectionid, value in sims:
        if i >= N:
          break
        if sectionid_to_title[sectionid] == similar_tune:
          section_matches += 1
          print(f"Found {tune} - {similar_tune} {sectionid_to_sectionlabel[sectionid]} with value {value}")
          if value > score:
            rank = i
            score = value
          break
        i += 1

    # for each title, increase matches if at least one of the section matched the expected title
    if section_matches > 0:
      matches += 1  
      results[f'{tune}, {similar_tune}'] = {'found': 1,
                                            'score': score,
                                            'rank': rank}
    else:
      score = 0
      for sectionid in title_to_sectionid[similar_tune]:
        sim_value = similarities[sectionid]
        score = sim_value if sim_value > score else score

      results[f'{tune}, {similar_tune}'] = {'found': 0,
                                            'score': score,
                                            'rank': rank}
  
  return matches, results

"""# LSA (Latent Semantic Analysis), aka LSI (Latent Semantic Index) """

from collections import defaultdict

"""Use the Test Corpus to train the LSI Model."""

no_below = 5

def prepare_corpus(doc_clean):
    """
    Input  : cleaned tunes
    Purpose: create term dictionary of our courpus and Converting list of documents (corpus) into Document Term Matrix
    Output : term dictionary and Document Term Matrix
    """
    # Creating the term dictionary of our courpus, where every unique term is assigned an index. dictionary = corpora.Dictionary(doc_clean)
    dic = corpora.Dictionary(doc_clean)
    # Filter out words that occur less than 20 documents.
    dic.filter_extremes(no_below=no_below, no_above=1.0)
    print(len(dic))

    # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
    doc_term_matrix = [dic.doc2bow(text) for text in doc_clean]

    # generate LDA model
    return dic, doc_term_matrix

test_dictionary, test_bow_corpus = prepare_corpus(test_corpus)

dictionary, bow_corpus = prepare_corpus(processed_corpus)

if False:
  dictionary = corpora.Dictionary(processed_corpus)

  # Filter out words that occur less than 20 documents, or more than 50% of the documents.
  dictionary.filter_extremes(no_below=no_below, no_above=1.0)
  print(len(dictionary))

  bow_corpus = [dictionary.doc2bow(text) for text in processed_corpus]

if False:
  test_dictionary = corpora.Dictionary(test_corpus)
  print(len(test_dictionary))
  # Filter out words that occur less than 20 documents, or more than 50% of the documents.
  test_dictionary.filter_extremes(no_below=no_below, no_above=1.0)
  print(len(test_dictionary))

  ### here we're using the dictionary of the full dataset! Gives a bit better results!
  test_bow_corpus = [dictionary.doc2bow(text) for text in test_corpus]

num_topics = lsi_config['num_topics']

lsi = LsiModel(test_bow_corpus, 
               id2word=test_dictionary, 
               num_topics=num_topics)

"""## Store Similarity Matrix

Use the Full Corpus to calculate the similarity matrix.
"""

index_lsi = similarities.Similarity('/content/index/index_lsi', lsi[bow_corpus], num_features=len(dictionary))

#index_lsi = similarities.SparseMatrixSimilarity(lsi[bow_corpus], num_features = len(dictionary))
#index_lsi = similarities.MatrixSimilarity(lsi[bow_corpus])  # transform corpus to LSI space and index it

lsi.save('/content/index/lsi.model')
index_lsi.save('/content/index/lsi_matrixsim.index')

!ls -la /content/index

"""## Visualize LSI Model Topics

### Plot Topics
"""

topics = lsi.get_topics()

"""Topics for each token in the vocabulary: y-axis Topics vector, x-axis tokens"""

fig = plt.figure()
ax = fig.add_subplot(111)

ax.imshow(topics, interpolation='nearest')
ax.set_aspect(5)

"""Plot topics for each tune section. 

x-axis: topics vector; y-axis: sectionid
"""

tunes_matrix = []
for i in range(len(processed_corpus)):
  query_bow = dictionary.doc2bow(processed_corpus[i])
  V = gensim.matutils.sparse2full(lsi[query_bow], len(lsi.projection.s)).T / lsi.projection.s
  tunes_matrix.append(V)

df_matrix = pd.DataFrame(tunes_matrix)

fig = plt.figure()
ax = fig.add_subplot(111)

ax.imshow(tunes_matrix, interpolation='nearest')
ax.set_aspect(0.01)

"""### T-SNE"""

if True:
  tsne = TSNE(n_components=2, 
              random_state=42,
              perplexity = 30,
              #learning_rate=100.0,
              #n_iter_without_progress=200,
              #n_iter=2000
              )
  #np.set_printoptions(suppress=True)
  T = tsne.fit_transform(tunes_matrix)

title_to_display = 'Embraceable You [jazz1350]'

sectionid = title_to_sectionid[title_to_display]
sectionid

marker_size = np.ones(len(df)) * 0.11
for s in sectionid:
  marker_size[s] = 3

label  = [''] * len(df)
for s in sectionid:
  label[s] = f"{sectionid_to_title[s]} ({sectionid_to_sectionlabel[s]})"

if True:
  projected = pd.DataFrame(T)
  #projected['tune'] = titles['title']
  #projected['cluster'] = df_cluster['ClusterLabel'].astype(str)
  #projected['mode'] = meta['tune_mode']

  fig = px.scatter(
      projected, 
      x=0, y=1,
      color=df.tune_mode, labels={'color': 'tune_mode'},
      hover_name=df.title + ' (' + df.section_name + ')',
      width=600, height=500,
      size=marker_size,
  )
  fig.update_traces(textposition='top center')
  fig.update_traces(textfont_size=8, selector=dict(type='scatter'))
  fig.show()

if True:
  clusterer = hdbscan.HDBSCAN(min_cluster_size=8)
  clusterer.fit(T)

  clusterer.labels_


  clust_proj = pd.DataFrame(T)
  #clust_proj['tune'] = titles['title']
  clust_proj['cluster'] = clusterer.labels_.astype(str)
  #clust_proj['mode'] = titles['tune_mode']

  fig = px.scatter(
      clust_proj, 
      x=0, y=1,
      color='cluster',
      hover_name=df.title + ' (' + df.section_name + ')',
      width=600, height=500
  )
  fig.update_traces(textposition='top center')
  fig.update_traces(textfont_size=8, selector=dict(type='scatter'))
  fig.show()

"""### UMAP"""

from sklearn.preprocessing import StandardScaler, MinMaxScaler

umap_2d = umap.UMAP(n_components=2, 
                    init='random', 
                    random_state=31,
                    #n_neighbors=6,
                    #min_dist=0.05,
                    metric='hellinger',
                    )

scaled_data = MinMaxScaler().fit_transform(tunes_matrix)  # scale to range 0..1 because Hellinger cannot handle negative values
proj_2d = umap_2d.fit_transform(scaled_data)

mapper = umap_2d.fit(scaled_data)

fig_2d = px.scatter(
    proj_2d, 
    x=0, y=1,
    color=df.tune_mode, labels={'color': 'tune_mode'},
    hover_name=df.title + ' (' + df.section_name + ')',
)

fig_2d.show()

umap.plot.output_notebook()

hover_data = pd.DataFrame({'label': df.title + ' (' + df.section_name + ')'})

p = umap.plot.interactive(mapper, 
                          labels=df.tune_mode, 
                          hover_data=hover_data, 
                          point_size=2)
ax_interactive = umap.plot.show(p)

ax_network = umap.plot.connectivity(mapper, show_points=True, edge_bundling='hammer')

"""Visualize the location of a tune:"""

df_umap = pd.DataFrame.from_records(proj_2d, columns=['x', 'y'])

search = ['These Foolish Things [jazz1350]']
params = {}

df_umap['title'] = df.title_playlist
df_umap['title_section'] = df.title + ' (' + df.section_name + ')'

df_umap['size'] = df_umap['title'].map(lambda w: 5 if w in search else 0.2)
params.update({'size': 'size'})

if len(search) > 0: # colorize with closest search word
    df_umap['label'] = df.title + ' (' + df.section_name + ')'
    df_umap['color'] = 'blue'
    df_umap['color'] = df_umap['title'].map(lambda w: 'blue' if w in search else 'red')
    params.update({'color': 'color'})

params.update({'hover_name': 'label'})

# removing the default hover text is not possible with this version of plotly
#params.update({'hover_data': {c: False for c in df.columns}, 'hover_name': 'label'})

params.update({'width': 800, 'height': 800})

fig = px.scatter(df_umap, x="x", y="y", opacity=0.3, **params)
fig.update_xaxes(showticklabels=False, showgrid=True, title='', zeroline=False, visible=True)
fig.update_yaxes(showticklabels=False, showgrid=True, title='', zeroline=False, visible=True)
fig.update_traces(textposition='middle center', marker={'line': {'width': 0}})
fig.update_layout(font=dict(family="Franklin Gothic", size=12, color="#000000"))
fig.show()

df_umap.to_csv(f'output/umap.csv', index_label='sectionid')

with zipfile.ZipFile(f'output/umap.zip', 'w') as zf:
  zf.write(f'output/umap.csv')

# save to wandb
if use_wandb:
  model_artifact = wandb.Artifact(
      f"umap", 
      type="csv",
      description=f"UMAP Visualization for sections for LSI model (csv file)",
      metadata="")

  model_artifact.add_file(f'output/umap.zip')
  wandb.log_artifact(model_artifact)

"""## Tests

### Tests for Contrafacts
"""

len(contrafacts)

topN = 30
matches, results = test_contrafacts(contrafacts, index_lsi, lsi, topN)

print(f"Found matches: {matches} out of {len(results)}: {100*matches/len(results):.3f}%")
print() 
for rr, val in results.items():
  if val == 0:
    print(f"{val}: {rr}")

results

df_sim = pd.DataFrame.from_dict(results, orient='index')
df_sim = df_sim.reset_index()
df_sim.sort_values('index')
print(df_sim)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))
sns.histplot(ax=ax[0],
             data=df_sim, 
             x='score', 
             hue='found', 
             stat='count', 
             edgecolor=None)
ax[0].set_title('LSI Scores for Contrafact Tunes')

sns.histplot(ax=ax[1],
             data=df_sim[df_sim.found==1], 
             x='rank', 
             stat='count', 
             edgecolor=None)
ax[1].set_title('Rank for found tunes')

plt.savefig('plot.png')

fig = px.histogram(df_sim, x="score", color='found', title='LSI Scores for found tunes')
fig.show()

fig = px.histogram(df_sim[df_sim.found==1], x="rank", title='Rank on which tune is found')
fig.show()

model_name = 'lsi'
if use_wandb:
  wandb.log(
      {model_name: {
                'contrafacts': {
                    'topN': topN,
                    'success': matches/len(contrafacts),
                    'results': wandb.Table(data=df_sim),
                    'score_histogram': wandb.Image('plot.png'),
                    },
                'model': {
                    'remove_tokens_below': no_below,
                }
                   },
       })

"""### Get Recommender Data for WebApp"""

test_data = [
  "Sweet Sue, Just You [jazz1350]",
  "On The Sunny Side Of The Street [jazz1350]",
  "These Foolish Things [jazz1350]", 
  "Blue Moon [jazz1350]",
  "I Got Rhythm [jazz1350]",
  "Old Fashioned Love [trad]",
  "Exactly Like You [jazz1350]",
  "Honeysuckle Rose [jazz1350]",
  "Misty [jazz1350]",
  "Wow [jazz1350]",
  "Take The A Train [jazz1350]"
]

test_data = sorted(test_data)

# Commented out IPython magic to ensure Python compatibility.
# %%time
# if True:
#   _tunes = list(tunes['title_playlist'].values())
#   #_tunes = test_data
# 
#   method = 'lsi'
# 
#   # save the mapping between titleid and title to disk
#   pd.DataFrame.from_dict(tunes).to_csv(f'output/index_{method}.csv', index_label='titleid')
#   with zipfile.ZipFile(f'output/index_{method}.zip', 'w') as zf:
#     zf.write(f'output/index_{method}.csv')
# 
#   df_sim = get_sim_scores(_tunes, index_lsi, lsi, topn=30)
# 
#   # save to file
#   (df_sim
#    .loc[:,[#'reference_title',
#            'reference_titleid',
#            #'similar_title',
#            'similar_titleid',
#            'ref_section_label',
#            'similar_section_label',
#            'score'
#            ]]
#    .groupby(['reference_titleid', 
#           #'reference_title', 
#           'similar_titleid',
#           #'similar_title', 
#           'ref_section_label', 
#           'similar_section_label'])
#    .max('score')
#    .reset_index()
#    .to_csv(f'output/recommender_{method}.csv', encoding='utf8', index=False)
#   )
#   
#   with zipfile.ZipFile(f'output/recommender_{method}.zip', 'w') as zf:
#     zf.write(f'output/recommender_{method}.csv')
# 
#   # save to wandb
#   if use_wandb:
#     model_artifact = wandb.Artifact(
#         f"recommender_{method}", 
#         type="csv",
#         description=f"Recommendations for each Tune using {method} Model (csv file)",
#         metadata="")
# 
#     model_artifact.add_file(f'output/recommender_{method}.zip')
#     model_artifact.add_file(f'output/index_{method}.zip')
#     wandb.log_artifact(model_artifact)

"""## Store Model to W&B"""

if use_wandb:
  model_artifact = wandb.Artifact(
      "model_lsi", 
      type="model",
      description="LSI model",
      metadata="")

  model_artifact.add_file("/content/index/lsi.model")
  model_artifact.add_file("/content/index/lsi_matrixsim.index")
  model_artifact.add_file("/content/index/lsi.model.projection")
  wandb.log_artifact(model_artifact)

"""## Determine Number of Topics for LSI Model

This sample comes from Datacamp: 

https://www.datacamp.com/community/tutorials/discovering-hidden-topics-python

What is the best way to determine k (number of topics) in topic modeling? Identify the optimum number of topics in the given corpus text is a challenging task. We can use the following options for determining the optimum number of topics:

* One way to determine the optimum number of topics is to consider each topic as a cluster and find out the effectiveness of a cluster using the Silhouette coefficient.
* Topic coherence measure is a realistic measure for identifying the number of topics.

Topic Coherence measure is a widely used metric to evaluate topic models. It uses the latent variable models. Each generated topic has a list of words. In topic coherence measure, you will find average/median of pairwise word similarity scores of the words in a topic. The high value of topic coherence score model will be considered as a good topic model.
"""

def compute_coherence_values(dictionary, doc_term_matrix, doc_clean, stop, start=2, step=3):
    """
    Input   : dictionary : Gensim dictionary
              corpus : Gensim corpus
              texts : List of input texts
              stop : Max num of topics
    purpose : Compute c_v coherence for various number of topics
    Output  : model_list : List of LSA topic models
              coherence_values : Coherence values corresponding to the LDA model with respective number of topics
    """
    coherence_values = []
    model_list = []
    for num_topics in range(start, stop, step):
        # generate LSA model
        model = LsiModel(doc_term_matrix, num_topics=num_topics, id2word = dictionary)  # train model
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model, texts=doc_clean, dictionary=dictionary, coherence='c_v')
        coherence_values.append(coherencemodel.get_coherence())
    return model_list, coherence_values

def plot_graph(doc_clean,start, stop, step):
    dictionary, doc_term_matrix = prepare_corpus(doc_clean)

    runs = 5
    for i in range(runs):
      model_list, coherence_values = compute_coherence_values(dictionary, 
                                                              doc_term_matrix,
                                                              doc_clean,
                                                              stop, start, step)
      # Show graph
      x = range(start, stop, step)
      plt.plot(x, coherence_values, color='blue')

    plt.xlabel("Number of Topics")
    plt.ylabel("Coherence score")
    plt.show()

# evaluate a good number of topics for the LSI Model. This takes some time.

if False:
  start, stop, step = 10, 300, 10
  plot_graph(test_corpus, start, stop, step)

"""For unigrams, the best number of topics that is most consistently for the 5 runs seems to be around 22.

For unigrams plus bigrams, the coherence score drops down until 100 and then continuously rises until 500 and continues to rise. Same for bigrams-only.

# W&B Logging and Finish
"""

if use_wandb:
  wandb.finish()



