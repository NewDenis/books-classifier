import os
import pickle
from sklearn.pipeline import Pipeline
from books_classifier.app.config import settings


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance


@singleton
class Classifier:
    def __init__(self) -> None:
        model_path = os.path.join(
            settings.PATH_TO_MODELS, settings.model_name, "model.bin"
        )
        with open(model_path, "rb") as fp:
            self.model: Pipeline = pickle.load(fp)

    def predict(self, text):
        return self.model.predict([text])[0]
