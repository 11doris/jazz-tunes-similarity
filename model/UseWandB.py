import wandb
from model.config import lsi_config, get_test_tunes, preprocess_config


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
                #"remove_repeated_chords": remove_repetitions,
                "lsi": lsi_config,
                "comment": comment,
            }
        )


    def store_input_file(self, file_name):
        if not self.use:
            return
        artifact = wandb.Artifact('input_data', type='dataset')
        artifact.add_file(file_name)
        wandb.log_artifact(artifact)

    def store_results(self, model_name, matches, df_sim, model_config):
        if not self.use:
            return

        wandb.log(
            {'results': {
                'contrafacts': {
                    'topN': preprocess_config['test_topN'],
                    'success': matches / len(get_test_tunes()),
                    'results': wandb.Table(data=df_sim),
                    #'score_histogram': wandb.Image('plot.png'),
                },
                'model': {
                    'remove_tokens_below': preprocess_config['no_below'],
                    'doc2vec': model_config,
                    'lsi': lsi_config,
                }
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

        model_artifact.add_file(f"output/model/{data.model_name}_matrixsim_{chords_preprocessing}.index")
        model_artifact.add_file(f'output/model/{data.model_name}_{chords_preprocessing}.model')
        model_artifact.add_file(f'output/model/recommender_{data.model_name}_{chords_preprocessing}.zip')

        wandb.log_artifact(model_artifact)


    def finish(self):
        if not self.use:
            return

        wandb.finish()
