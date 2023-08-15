from model_factory.train_baseline import train_baseline
import click
import os
import pickle
import time
import mlflow
from datetime import datetime


@click.command()
@click.option("--tfidf", is_flag=True)
@click.option("--data-path", default="/mnt/data/")
@click.option("--fraction", default=0.1)
@click.option("--out-path", default="books_classifier/artifacts/models/")
@click.option("--save-in-file", is_flag=True)
@click.option("--mlflow-addr", default="mlflow-service")
def train_and_save(
    tfidf, data_path, fraction, out_path, save_in_file, mlflow_addr
):
    mlflow.set_tracking_uri(f"http://{mlflow_addr}:5000")
    with mlflow.start_run(
        run_name=f"baseline_{datetime.now().strftime('%Y%m%d')}"
    ):
        elapsed = time.perf_counter()
        model, metrics = train_baseline(tfidf, data_path, fraction)
        mlflow.log_metrics(metrics)
        elapsed = time.perf_counter() - elapsed
        print(f"{model} trained in {elapsed}s")
        if save_in_file:
            vectorizer = "tfidf" if tfidf else "count"
            out_path = os.path.join(out_path, f"{vectorizer}_logreg")
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            with open(os.path.join(out_path, "model.bin"), "wb") as fp:
                pickle.dump(model, fp)
            print(f"Model saved in {out_path}")


if __name__ == "__main__":
    train_and_save()
