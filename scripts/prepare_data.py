import boto3
from tqdm import tqdm
import os
import pandas as pd
import io
import zipfile
import time
from s3zipfile import S3File
from collections import defaultdict
import rarfile
import docx
import tempfile
import textract
import re
from rtfparse.parser import Rtf_Parser
from rtfparse.entities import Plain_Text
from chardet import UniversalDetector
from lxml import html as html_module
from lxml import etree
from typing import List, Dict, Tuple


def html2text(html_content):
    tree = html_module.fromstring(html_content)
    # text_list = tree.xpath('//text()')
    # text_list = tree.xpath('//text()[not(ancestor::script)]')
    text_list = tree.xpath(
        "//text()[not(ancestor::script) and normalize-space()]"
    )
    return "\n".join(text.strip() for text in text_list if (len(text) > 0))


SPACE_REG = re.compile(r"\s+")
POINT_REG = re.compile(r"(?<![\.А-ЯA-Z])\.(?!\.)")
RUSSIAN_REG = re.compile(r"[а-яА-ЯёЁ]{4,}")
CODE_REG = re.compile(r"(\\x[\da-fA-F]{4})|(\\x[\da-fA-F]{2})")


def split_text_to_sentences(text: str):
    text = SPACE_REG.sub(" ", text)
    text = CODE_REG.sub(" ", text)
    return list(
        map(
            str.strip,
            filter(
                lambda x: len(RUSSIAN_REG.findall(x)) > 5,
                filter(
                    lambda x: (len(x) > 20) and (x.count(" ") > 5),
                    POINT_REG.split(text),
                ),
            ),
        )
    )


def extract_text_from(
    zf: zipfile.ZipFile, file_name: str, file_ext: str
) -> List[str]:
    text = None
    if file_ext == ".zip":
        result = []
        with zf.open(file_name) as z, zipfile.ZipFile(z) as inner_zf:
            for doc_file in inner_zf.namelist():
                doc_ext = os.path.splitext(doc_file)[-1].lower()
                result.extend(
                    safe_extract_text_from(inner_zf, doc_file, doc_ext)
                )
        return result
    if file_ext == ".rar":
        result = []
        with zf.open(file_name) as z, rarfile.RarFile(z) as inner_zf:
            for doc_file in inner_zf.namelist():
                doc_ext = os.path.splitext(doc_file)[-1].lower()
                result.extend(
                    safe_extract_text_from(inner_zf, doc_file, doc_ext)
                )
        return result
    if file_ext == ".fb2":
        text = zf.read(file_name)
        try:
            root = etree.fromstring(text)
        except etree.LxmlError as e:
            return []
        text = "\n".join(
            txt
            for item in root.findall("*//p", namespaces=root.nsmap)
            if (txt := item.text) is not None
        )
    elif file_ext in {".html", ".htm"}:
        detector = UniversalDetector()
        with zf.open(file_name) as z:
            for line in z.readlines():
                detector.feed(line)
                if detector.done:
                    break
        detector.close()
        encoding = detector.result["encoding"]
        text = html2text(zf.read(file_name).decode(encoding))
    elif file_ext == ".txt":
        detector = UniversalDetector()
        with zf.open(file_name) as z:
            for line in z.readlines():
                detector.feed(line)
                if detector.done:
                    break
        detector.close()
        encoding = detector.result["encoding"]
        text = zf.read(file_name).decode(encoding)
    elif file_ext == ".rtf":
        with zf.open(file_name) as z:
            parsed = Rtf_Parser(rtf_file=z).parse_file()
            text = " ".join(
                [
                    item.text
                    for item in parsed.structure
                    if isinstance(item, Plain_Text)
                ]
            )
    elif file_ext == ".docx":
        with zf.open(file_name) as z:
            doc = docx.Document(z)
            text = " ".join([par.text for par in doc.paragraphs])
    elif file_ext == ".doc":
        with tempfile.NamedTemporaryFile(suffix=file_ext) as tmp:
            tmp.write(zf.read(file_name))
            tmp.flush()
            text = textract.process(tmp.name, encoding="utf-8").decode("utf-8")
    return split_text_to_sentences(text) if text is not None else []


def safe_extract_text_from(
    zf: zipfile.ZipFile, file_name: str, file_ext: str
) -> List[str]:
    try:
        return extract_text_from(zf, file_name, file_ext)
    except Exception as e:
        # print(type(e), e, file_name)
        return []


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


if __name__ == "__main__":
    session = boto3.session.Session()

    s3 = session.resource(
        service_name="s3",
        region_name="ru-central1",
        endpoint_url="https://storage.yandexcloud.net",
    )
    bucket_name = "books-raw-data"
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
    findx = 0
    path_to_save = os.path.join("/", "mnt", "data", "datasets", "raw")
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)

    for zipfile_key in main_pbar:
        obj = bucket.Object(zipfile_key)
        file = S3File(obj)
        saved_path = download_s3file(
            file, os.path.join("/", "mnt", "data", zipfile_key)
        )
        try:
            with open(saved_path, "rb") as fp:
                with zipfile.ZipFile(fp) as zf:
                    for zipname in tqdm(zf.namelist(), leave=False):
                        cls = tuple(
                            os.path.splitext(os.path.basename(zipname))[
                                0
                            ].split("_")
                        )
                        with zf.open(zipname) as zfp, zipfile.ZipFile(
                            zfp
                        ) as inner_zf:
                            for doc_file in inner_zf.namelist():
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
