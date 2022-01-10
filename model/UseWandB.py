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
                "chords_preprocessing": data.chords_preprocessing,
                "ngrams_input": data.ngrams,
                "model": data.model_name,
                'remove_tokens_below': preprocess_config['no_below'],
                # "remove_repeated_chords": remove_repetitions,
                "lsi": data.model_config,
                "doc2vec": data.model_config,
                "comment": comment,
            }
        )

    def store_input_file(self, file_name):
        if not self.use:
            return
        artifact = wandb.Artifact('input_data', type='dataset')
        artifact.add_file(file_name)
        wandb.log_artifact(artifact)

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

    def store_result_chord_analogy(self, analogy, topn):
        if not self.use:
            return

        wandb.log(
            {
                'analogy': {
                    'perfect': analogy[0],
                    'topn': analogy[1],
                    'n': topn,
                },
            })


    def store_artifacts(self, data, chords_preprocessing):
        if not self.use:
            return

        model_artifact = wandb.Artifact(
            data.model_name,
            type="model",
            description=f"{data.model_name} Model",
            metadata="")

        # upload the model and the webapp recommender file
        model_artifact.add_file(f'output/model/{data.model_name}_{chords_preprocessing}.model')
        model_artifact.add_file(f'output/model/recommender_{data.model_name}_{chords_preprocessing}.zip')

        # not all methods use an index, so upload the index file only if is available
        index_file = f"output/model/{data.model_name}_matrixsim_{chords_preprocessing}.index"
        if exists(index_file):
            model_artifact.add_file(f"output/model/{data.model_name}_matrixsim_{chords_preprocessing}.index")

        wandb.log_artifact(model_artifact)

    def finish(self):
        if not self.use:
            return

        wandb.finish()
