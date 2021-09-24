from tests.conftest import get_test_root_path, get_test_root_file
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def test_read_json_sequences():
    json_path = get_test_root_file("tests/chord_sequences/chords/chord_sequences.json")
    df = pd.read_json(json_path, orient='index')
    print(df.columns)

    df = pd.concat([df, df["default_key"].apply(pd.Series)], axis=1)
    df = pd.concat([df, df["time_signature"].apply(pd.Series)], axis=1)
    df = df.drop(columns=["default_key", "time_signature", "out"])

    assert json_path is not None
