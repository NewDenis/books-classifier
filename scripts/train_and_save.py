from model_factory.train_baseline import train_baseline
import click
import os
import pickle


@click.command()
@click.option("--tfidf", is_flag=True)
@click.option("--data-path", default="/mnt/data/")
@click.option("--fraction", default=1.0)
@click.option("--out-path", default="/mnt/models/")
def train_and_save(tfidf, data_path, fraction, out_path):
    model = train_baseline(tfidf, data_path, fraction)
    vectorizer = "tfidf" if tfidf else "count"
    out_path = os.path.join(out_path, f"{vectorizer}_logreg")
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    with open(os.path.join(out_path, "model.bin"), "wb") as fp:
        pickle.dump(model, fp)
    print(f"Model saved in {out_path}")


if __name__ == "__main__":
    train_and_save()
