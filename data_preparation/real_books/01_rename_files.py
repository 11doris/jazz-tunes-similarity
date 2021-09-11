from bs4 import BeautifulSoup
import re
import os
import pandas as pd
from shutil import copyfile


def get_valid_filename(s):
    """Remove invalid characters from the file name."""
    # s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w\s.\']', '', s)


if __name__ == "__main__":
    """ 
    The Real Books Vol 1-3 are available on CD-ROM from Hal Leonard. The sheet music comes with a html index page
    to find the lead sheet of a tune. The tunes are stored on the CD-ROM as pdf files with a number identifier.
    This script parses the html index page to create the mapping between the original file name and the title.
    Then, it copies the files into an output directory and renames them with the title of the tune.
    """

    song_id = []
    title = []
    old_filename = []
    new_filename = []
    volume = []

    # loop over the 3 volumes, each one has its own html index files
    for i in range(1, 4):
        volume_name = f"Vol{i}"
        html_file = os.path.join("in", volume_name, "contents.html")
        with open(html_file) as fp:
            soup = BeautifulSoup(fp, "html.parser")

        # parse the html file
        find_all_a = soup.find_all('a', href=True)
        for el in find_all_a:
            _id = re.search("Song=(\d{6})\&", el['href'])
            if _id is not None:
                _id = _id[1]
                song_id.append(_id)
                title.append(el.text)
                old_filename.append(f"{_id}.pdf")
                new_filename.append(get_valid_filename(f"{el.text}.pdf"))
                volume.append(volume_name)

    df = pd.DataFrame(list(zip(song_id, title, old_filename, new_filename, volume)),
                      columns =['id', 'title', 'old_filename', 'file_name', 'volume'])

    # write mapping table to disk
    df = df.sort_values('NewFilename')
    df.to_csv('songlist.csv')

    # copy and rename files
    for row in df.itertuples():
        print(row.Title)
        copy_from = os.path.join("in", row.Volume, "songs", row.OldFilename)
        copy_to = os.path.join("out", row.NewFilename)

        copyfile(src=copy_from, dst=copy_to)






