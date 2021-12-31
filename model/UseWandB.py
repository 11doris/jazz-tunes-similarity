import wandb
from model.config import lsi_config, get_test_tunes, test_topN, no_below


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

    def store_results(self, matches, df_sim):
        if not self.use:
            return

        model_name = 'lsi'
        wandb.log(
            {model_name: {
                'contrafacts': {
                    'topN': test_topN,
                    'success': matches / len(get_test_tunes()),
                    'results': wandb.Table(data=df_sim),
                    #'score_histogram': wandb.Image('plot.png'),
                },
                'model': {
                    'remove_tokens_below': no_below,
                }
            },
            })

    def store_artifacts(self):
        if not self.use:
            return

        model_artifact = wandb.Artifact(
            "model_lsi",
            type="model",
            description="LSI model",
            metadata="")

        #model_artifact.add_file("output/model/index/lsi.model")
        model_artifact.add_file("output/model/lsi_matrixsim.index")
        model_artifact.add_file("output/model/lsi.model.projection")
        model_artifact.add_file("output/model/recommender_lsi.zip")

        wandb.log_artifact(model_artifact)


    def finish(self):
        if not self.use:
            return

        wandb.finish()
