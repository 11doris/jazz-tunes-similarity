

class NGrams:
    def __init__(self, sequences):
        self.sequences = sequences
        self.ngrams = []
        self.total = 0

    def build(self, n=4):

        # TODO check that this is a list of tune sequences

        for tune in self.sequences:
            # Use the zip function to help us generate n-grams
            # Concatenate the tokens into ngrams and return
            tune_ngrams = zip(*[tune[i:] for i in range(n)])
            tune_ngrams = [" ".join(ngram) for ngram in tune_ngrams]

            # print(tune_ngrams)
            self.ngrams += [tune_ngrams]

        return self.ngrams

