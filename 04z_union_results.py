import pandas as pd
from dataset.utils import set_pandas_display_options
import matplotlib.pyplot as plt
from tqdm import tqdm

set_pandas_display_options()

df_simp = pd.read_csv('output/similarity/recommender_lsi_simp.zip')
df_plus = pd.read_csv('output/similarity/recommender_lsi_plus.zip')

df_simp.head()

ref_titles = (df_simp
              .loc[:, ['reference_titleid', 'ref_section_label']]
              .drop_duplicates()
              )

df_simp.value_counts(['reference_titleid', 'ref_section_label'])

len_common = []

dict_comparison = {
    'titleid': [],
    'section_label': [],
    'common': [],
    'unique_simp': [],
    'unique_plus': [],
}

for section in tqdm(ref_titles.iterrows()):
    titleid = section[1]['reference_titleid']
    section = section[1]['ref_section_label']
    q = f"reference_titleid == {titleid} & ref_section_label == '{section}'"
    simp_tunes = df_simp.query(q)
    plus_tunes = df_plus.query(q)

    recommend_simp = set(list(zip(simp_tunes.similar_titleid, simp_tunes.similar_section_label)))
    recommend_plus = set(list(zip(plus_tunes.similar_titleid, plus_tunes.similar_section_label)))

    common_set = recommend_plus.intersection(recommend_simp)
    unique_simp = len(recommend_simp) - len(common_set)
    unique_plus = len(recommend_plus) - len(common_set)
    assert(unique_simp == unique_plus)

    if False:
        print(f'Len Simp: {len(recommend_simp)}')
        print(f'Len Plus: {len(recommend_plus)}')
        print(f'Len Common: {len(common_set)}')
        print()

    # ['titleid', 'section_label', 'common', 'unique_simp', 'unique_plus']
    row = [titleid, section, len(common_set), unique_simp, unique_plus]

    dict_comparison['titleid'].append(titleid)
    dict_comparison['section_label'].append(section)
    dict_comparison['common'].append(len(common_set))
    dict_comparison['unique_simp'].append(unique_simp)
    dict_comparison['unique_plus'].append(unique_plus)


df = pd.DataFrame(dict_comparison)



# equivalent but more general
ax1 = plt.subplot(1, 2, 1)
plt.hist(df['common'], bins=30)
ax1.set_title('Common')

ax2 = plt.subplot(1, 2, 2, sharex=ax1)
plt.hist(df['unique_plus'], bins=30)
ax2.set_title('Unique')

plt.show()

