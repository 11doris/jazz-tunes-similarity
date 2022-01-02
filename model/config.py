from data_preparation.utils import output_preprocessing_directory

use_wandb = True

input_files = {
        # M7 and 6 reduced to major triad, m7 reduced to m, dominant 7, m7b5, diminished, and all (b5) left as they are.
        'rootAndDegreesPlus': f'{output_preprocessing_directory}/03b_input_wordembedding_sections_rootAndDegreesPlus.csv',
        'rootAndDegrees7': '',
        'rootAndDegreesSimplified': f'{output_preprocessing_directory}/03b_input_wordembedding_sections_simplified.csv',
}

lsi_config = {
    'num_topics': 100 #22, # 100 gives a better value for the contrafacts test
}

# TODO clean up
ngrams = [1,2]
test_topN = 30
no_below = 5
remove_repetitions = False

def get_test_tunes():
    return [
        ("26-2 [jazz1350]", "Confirmation [jazz1350]"),
        ("52nd Street Theme [jazz1350]", "I Got Rhythm [jazz1350]"),  # not a good match
        ("Ablution [jazz1350]", "All The Things You Are [jazz1350]"),
        ("Anthropology [jazz1350]", "I Got Rhythm [jazz1350]"),
        ("Bright Mississippi [jazz1350]", "Sweet Georgia Brown [jazz1350]"),
        ("C.T.A. [jazz1350]", "I Got Rhythm [jazz1350]"),
        # ( "Celia [jazz1350]", "I Got Rhythm [jazz1350]"),
        ("Cottontail [jazz1350]", "I Got Rhythm [jazz1350]"),
        ("Countdown [jazz1350]", "Tune Up [jazz1350]"),
        ("Dewey Square [jazz1350]", "Oh, Lady Be Good [jazz1350]"),
        ("Dexterity [jazz1350]", "I Got Rhythm [jazz1350]"),
        ("Dig [jazz1350]", "Sweet Georgia Brown [jazz1350]"),
        ("Donna Lee [jazz1350]", "Indiana (Back Home Again In) [jazz1350]"),
        ("Don't Be That Way [jazz1350]", "I Got Rhythm [jazz1350]"),  # cannot be found; bridge in different key
        # ("Eternal Triangle [jazz1350]", "I Got Rhythm [jazz1350]"),
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
        ("Lennie's Pennies [jazz1350]", "Pennies From Heaven [jazz1350]"),
        # Lennie's Pennies is in minor and therefore transposed to Amin... not possible to recognize like that
        # ( "Let's Call This [jazz1350]", "Honeysuckle Rose [jazz1350]"),
        ("Little Rootie Tootie [jazz1350]", "I Got Rhythm [jazz1350]"),
        ("Little Willie Leaps [jazz1350]", "All God's Chillun Got Rhythm [jazz1350]"),
        ("Lullaby Of Birdland [jazz1350]", "Love Me Or Leave Me [jazz1350]"),
        # ("Moose The Mooche [jazz1350]", "I Got Rhythm [jazz1350]"),
        ("My Little Suede Shoes [jazz1350]", "Jeepers Creepers [jazz1350]"),
        # ("Oleo [jazz1350]", "I Got Rhythm [jazz1350]"),
        ("Ornithology [jazz1350]", "How High The Moon [jazz1350]"),
        # ("Passport [jazz1350]", "I Got Rhythm [jazz1350]"),
        ("Quasimodo (Theme) [jazz1350]", "Embraceable You [jazz1350]"),
        # ("Rhythm-a-ning [jazz1350]", "I Got Rhythm [jazz1350]"),
        ("Room 608 [jazz1350]", "I Got Rhythm [jazz1350]"),
        # ("Salt Peanuts [jazz1350]", "I Got Rhythm [jazz1350]"),
        ("Satellite [jazz1350]", "How High The Moon [jazz1350]"),
        ("Scrapple From The Apple [jazz1350]", "Honeysuckle Rose [jazz1350]"),  # A section
        ("Scrapple From The Apple [jazz1350]", "I Got Rhythm [jazz1350]"),  # B section
        # ("Segment [jazz1350]", "I Got Rhythm [jazz1350]"),
        # ("Seven Come Eleven [jazz1350]", "I Got Rhythm [jazz1350]"),
        # ("Shaw 'Nuff [jazz1350]", "I Got Rhythm [jazz1350]"),
        # ("Theme, The [jazz1350]", "I Got Rhythm [jazz1350]"),
        ("Tour De Force [jazz1350]", "Jeepers Creepers [jazz1350]"),
        ("Wow [jazz1350]", "You Can Depend On Me [jazz1350]"),
        ("Yardbird Suite [jazz1350]", "Rosetta [jazz1350]"),

        # following tunes are not from wikipedia),
        ("Sweet Sue, Just You [jazz1350]", "Honeysuckle Rose [jazz1350]"),  # A section
        # ("All Of Me [jazz1350]", "Pennies From Heaven [jazz1350]"), # bars 25-28 of All of Me are same as bars 17-20 of Pennies From Heaven, but different key!
        ("Sweet Sue, Just You [jazz1350]", "Bye Bye Blackbird [jazz1350]"),  # Bridge same
        ("These Foolish Things [jazz1350]", "Blue Moon [jazz1350]"),  # first 8 bars same
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
        ("Moten Swing [jazz1350]", "Once In A While (Ballad) [trad]"),  # same bridge, similar A
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

