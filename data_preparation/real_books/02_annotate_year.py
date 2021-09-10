import subprocess
import os
import pandas as pd
import csv


if __name__ == "__main__":
    """
    Helper script to retrieve the publishing year from each tune. 
    The script loops over all tunes:
    - the pdf of one lead sheet is opened in Adobe Acrobat
    - manually scroll down and read the publishing year at the bottom of the sheet
    - switch back to the python script, press enter to close Adobe Acrobat
    - enter the publishing year for that song
    - the year is added to the dataframe and stored to disk.
    """

    dir_path = "out"
    acrobat_path = "C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe"

    # read the csv file that was generated with 01_rename_files.py
    df = pd.read_csv('songlist.csv')

    # open the output csv file and write the header
    with open('songlist_year.csv', 'w', newline='', encoding='utf-8') as csvfile:
        song_csv = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        song_csv.writerow(["Id", "Title", "OldFilename", "NewFilename", "Volume", "Year"])

    # loop over all tunes
    for song in df.itertuples():
        pdf_file = os.path.join(dir_path, song.NewFilename)
        if os.path.isfile(pdf_file):
            print(pdf_file)
            p = subprocess.Popen([acrobat_path, pdf_file])
            input('Press a key to terminate Adobe')
            p.kill()
            year = input(f"Enter Year for {song.NewFilename}:")
            # store result to disk
            with open('songlist_year.csv', 'a', newline='', encoding='utf-8') as csvfile:
                song_csv = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                song_csv.writerow([song.Id, song.Title, song.OldFilename, song.NewFilename, song.Volume, year])

