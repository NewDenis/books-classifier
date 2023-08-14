from books_classifier.app.classifier.base_model import Classifier

single_model = Classifier()


def get_ml_model_clf() -> Classifier:
    return single_model
