import re
import docx
import rarfile
import textract
from chardet import UniversalDetector
from lxml import etree, html as html_module
from rtfparse.entities import Plain_Text
from rtfparse.parser import Rtf_Parser


import os
import tempfile
import zipfile
from typing import List


def safe_extract_text_from(
    zf: zipfile.ZipFile, file_name: str, file_ext: str
) -> List[str]:
    try:
        return extract_text_from(zf, file_name, file_ext)
    except Exception as e:
        # print(type(e), e, file_name)
        return []


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
