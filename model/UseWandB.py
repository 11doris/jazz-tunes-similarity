import wandb
from model.config import get_test_tunes, preprocess_config
from os.path import exists


class UseWandB:
    def __init__(self, use, project_name='', data=None, comment=""):
        self.use = use
        if not self.use:
            return

        wandb.init(
            # Set entity to specify your username or team name
            # ex: entity="carey",
            # Set the project where this run will be logged
            project=project_name,

            # Track hyperparameters and run metadata
            config={
                "comment": comment,
                "model": data.model_name,
                "chords_preprocessing": data.chords_preprocessing,
                "ngrams_input": data.ngrams,
                'remove_tokens_below': preprocess_config['no_below'],
                "remove_repeated_chords": preprocess_config['remove_repetitions'],
                "params": data.model_config,

            }
        )

    def store_input_file(self, file_name):
        if not self.use:
            return
        artifact = wandb.Artifact('input_data', type='dataset')
        artifact.add_file(file_name)
        wandb.log_artifact(artifact)

    def store_result_vocab(self, vocab_counts):
        if not self.use:
            return
        wandb.log(vocab_counts)

    def store_result_contrafacts(self, model_name, matches, df_sim):
        if not self.use:
            return

        wandb.log(
            {
                'contrafacts': {
                    'topN': preprocess_config['test_topN'],
                    'success': matches / len(get_test_tunes()),
                    'results': wandb.Table(data=df_sim),
                },
            })

    def store_result_self_similarity(self, selfsimilar):
        if not self.use:
            return

        wandb.log(
            {
                'self-similarity': {
                    'first': selfsimilar[0],
                    'second': selfsimilar[1],
                },
            })

    def store_result_chord_analogy(self, analogy, df_scores, topn):
        if not self.use:
            return

        wandb.log(
            {
                'analogy': {
                    'correct': analogy[0],
                    'topn': analogy[1],
                    'n': topn,
                    'results': wandb.Table(data=df_scores),
                },
            })


    def store_artifacts(self, data, chords_preprocessing, recommender_filename):
        if not self.use:
            return

        model_artifact = wandb.Artifact(
            data.model_name,
            type="model",
            description=f"{data.model_name} Model",
            metadata="")

        # upload the model and the webapp recommender file
        model_artifact.add_file(data.model_filename)
        model_artifact.add_file(f'{recommender_filename}.zip')

        # not all methods use an index, so upload the index file only if is available
        index_file = f"output/model/{data.model_name}_matrixsim_{chords_preprocessing}.index"
        if exists(index_file):
            model_artifact.add_file(f"output/model/{data.model_name}_matrixsim_{chords_preprocessing}.index")

        wandb.log_artifact(model_artifact)

    def finish(self):
        if not self.use:
            return

        wandb.finish()
