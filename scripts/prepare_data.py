import boto3
from tqdm import tqdm
import os
import pandas as pd
import io
import zipfile
import time
from data_processing.s3zipfile import S3File
from collections import defaultdict
from typing import List, Dict, Tuple
import click
from data_processing.text_extracting import safe_extract_text_from


def nice_size(sz, threshold=1, divisor=1024, units="Bites", precision=2):
    for prefix in ["", "K", "M", "G", "T"]:
        if sz < threshold * divisor:
            return f"{sz:.{precision}f}{prefix}{units}"
        sz /= 1024
    return f"{sz:.{precision}f}Peta{units}"


chunk_size = 1 * 1024 * 1024 * 1024


def download_s3file(file_obj: S3File, save_path: str):
    if (
        os.path.exists(save_path)
        and os.path.getsize(save_path) == file_obj.size
    ):
        return save_path
    saved = 0
    total = file_obj.size
    pbar = tqdm(
        total=total,
        unit="bytes",
        unit_scale=True,
        unit_divisor=1024,
        leave=False,
    )
    with open(save_path, "wb") as fp:
        while saved < total:
            to_download = min(chunk_size, total - saved)
            elapsed = time.perf_counter()
            buf = file_obj.read(to_download)
            elapsed = time.perf_counter() - elapsed
            read_spd = nice_size(len(buf) / elapsed) + "/s"
            elapsed = time.perf_counter()
            writed = 0
            while writed < len(buf):
                writed += fp.write(buf)
            elapsed = time.perf_counter() - elapsed
            write_spd = nice_size(len(buf) / elapsed) + "/s"
            saved += len(buf)
            pbar.update(len(buf))
            pbar.set_description(f"{read_spd=}, {write_spd=}")
    return save_path


def save_sentences(
    classes: Dict[Tuple[str, ...], List[str]], findx: int, path_to_save: str
):
    dataset = []
    for cls_key, sentence_list in classes.items():
        cls_key = {f"cls{i}": cls for i, cls in enumerate(cls_key[::-1])}
        data = [{"text": sentence, **cls_key} for sentence in sentence_list]
        dataset.append(pd.DataFrame(data))
    dataset = pd.concat(dataset, ignore_index=True)
    dataset.to_parquet(
        os.path.join(path_to_save, f"sentences_{findx:0>6}.pqt")
    )


@click.command()
@click.option("--bucket-name", default="books-raw-data")
@click.option("--samples", default=10000000)
@click.option("--out-path", default="/mnt/data/")
def prepare_data(bucket_name, samples, out_path):
    session = boto3.session.Session()
    s3 = session.resource(
        service_name="s3",
        region_name="ru-central1",
        endpoint_url="https://storage.yandexcloud.net",
    )
    bucket = s3.Bucket(bucket_name)

    zipfiles = [
        key
        for obj in bucket.objects.iterator()
        if (key := obj.key).endswith(".zip")
    ]

    main_pbar = tqdm(
        zipfiles,
        leave=False,
        nrows=4,
    )

    classes = defaultdict(list)
    sentence_count_to_save = 2_000_000
    sentence_count = 0
    samples_count = 0
    findx = 0
    path_to_save = os.path.join(out_path, "datasets", "raw")
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)

    for zipfile_key in main_pbar:
        if samples_count >= samples:
            break
        obj = bucket.Object(zipfile_key)
        file = S3File(obj)
        saved_path = download_s3file(file, os.path.join(out_path, zipfile_key))
        try:
            with open(saved_path, "rb") as fp:
                with zipfile.ZipFile(fp) as zf:
                    for zipname in tqdm(zf.namelist(), leave=False):
                        if samples_count >= samples:
                            break
                        cls = tuple(
                            os.path.splitext(os.path.basename(zipname))[
                                0
                            ].split("_")
                        )
                        with zf.open(zipname) as zfp, zipfile.ZipFile(
                            zfp
                        ) as inner_zf:
                            for doc_file in inner_zf.namelist():
                                if samples_count >= samples:
                                    break
                                doc_path, doc_ext = os.path.splitext(doc_file)
                                doc_ext = doc_ext.lower()
                                sentences = safe_extract_text_from(
                                    inner_zf, doc_file, doc_ext
                                )
                                classes[cls].extend(sentences)
                                sentence_count += len(sentences)
                            if sentence_count >= sentence_count_to_save:
                                save_sentences(classes, findx, path_to_save)
                                findx += 1
                                del classes
                                classes = defaultdict(list)
                                samples_count += len(sentences)
                                sentence_count = 0
                            main_pbar.set_description(
                                str(findx)
                                + "|".join(
                                    f"{key[-2]}({nice_size(len(val), divisor=1000, units='', precision=0)})"
                                    for key, val in sorted(
                                        classes.items(),
                                        key=lambda x: len(x[-1]),
                                        reverse=True,
                                    )
                                )
                            )
        except zipfile.BadZipFile as e:
            print(zipfile_key, e)
    save_sentences(classes, findx, path_to_save)
    print(
        *[
            f"{key[-2]}({nice_size(len(val), divisor=1000, units='', precision=0)})"
            for key, val in sorted(
                classes.items(),
                key=lambda x: len(x[-1]),
                reverse=True,
            )
        ],
        sep="\n",
    )


if __name__ == "__main__":
    prepare_data()
