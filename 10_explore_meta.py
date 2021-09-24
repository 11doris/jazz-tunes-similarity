from chords.ChordSequence import ChordSequence
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def rename_composers():
    return [
        ["^Monk", "Thelonious Monk"],
        ["^Rodgers", "Richard Rodgers"],
        ["^Porter$", "Cole Porter"],
        ["^Cole Albert Porter", "Cole Porter"],
        ["^Irvin Berlin", "Irving Berlin"],
        ["^Silver", "Horace Silver"],
        ["^Kern", "Jerome Kern"],
        ["^Leo Robin Jerome Kern", "Jerome Kern"],
        ["^Carmichael", "Hoagy Carmichael"],
        ["^Warren", "Earl Warren"],
        ["^Corea Chick", "Chick Corea"],
        ["^Donaldson", "Walter Donaldson"],
        ["^Burke", "Joseph A Burke"],
        ["^VanHeusen", "Jimmy Van Heusen"],
        ["^William Basie", "Count Basie"],
        ["^Trad.", "Traditional"],
        ["^$", "Unknown Composer"],
        ["^Waller", "Fats Waller"],
        ["^\'Fats\' Waller", "Fats Waller"],
        ["^Ellington", "Duke Ellington"],
        ["^Edward Kennedy (Duke) Ellington", "Duke Ellington"],
        ["^Strayhorn", "Billy Strayhorn"],
        ["^Armstrong", "Louis Armstrong"],
        ["^Lillian Hardin Armstrong", "Lillian Armstrong"],
        ["^L H Armstrong", "Lillian Armstrong"]
    ]

if __name__ == "__main__":
    cs = ChordSequence()
    df = pd.read_json(cs.get_chord_sequences_path(), orient='index')

    df = pd.concat([df, df["default_key"].apply(pd.Series)], axis=1)
    df = pd.concat([df, df["time_signature"].apply(pd.Series)], axis=1)
    df = df.drop(columns=["default_key", "time_signature", "out"])

    df = df.assign(composer=df.composer.str.split(',')).explode('composer')
    df = df.assign(composer=df.composer.str.split('-')).explode('composer')
    df = df.assign(composer=df.composer.str.split('/')).explode('composer')
    df['composer'] = df['composer'].str.strip()

    composer_tunes = df.groupby('composer').title.count().sort_values(ascending=False)
    print(composer_tunes.head(50))

    composer_tunes.to_csv('composers_before_cleaning.csv', sep='\t', index=True)

    # clean the composer names
    rename_list = rename_composers()
    for _from, _to in rename_list:
        df['composer'] = df['composer'].str.replace(_from, _to, regex=True)

    composer_tunes = df.groupby('composer').title.count().sort_values(ascending=False)
    print(composer_tunes.head(50))

    composer_tunes.to_csv('composers_after_cleaning.csv', sep='\t', index=True)

    df.to_csv('meta.csv', sep='\t', index=True)