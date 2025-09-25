import argparse
import hashlib
import json
import os
import pickle
from datetime import datetime
from pathlib import Path

from src.data_processing.loader import DataLoader
from src.data_processing.preprocessor import Preprocessor
from src.data_processing.embedder import Embedder

def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Ingest a single file (PDF/DOCX/TXT/Audio) and save processed text and embeddings.")
    # 让 input_path 变为可选位置参数，提供默认路径
    parser.add_argument(
        "input_path",
        nargs="?",
        default=r"D:\@Python\@PyCharm\RAG_Agent\data\raw\9month.pdf",
        help="Path to the input file, e.g. data/raw/your.pdf"
    )
    parser.add_argument("--processed-dir", default="./data/processed", help="Directory to save processed text")
    parser.add_argument("--embeddings-dir", default="./data/embeddings", help="Directory to save embeddings")
    parser.add_argument("--metadata-file", default="./data/processed/ingestion_metadata.jsonl", help="JSONL to append metadata")
    args = parser.parse_args()

    input_path = Path(args.input_path)
    if not input_path.exists():
        parser.error(f"默认/传入的路径不存在: {input_path}")

    processed_dir = Path(args.processed_dir)
    embeddings_dir = Path(args.embeddings_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    embeddings_dir.mkdir(parents=True, exist_ok=True)

    # 1) 加载原始内容
    loader = DataLoader()
    raw_text = loader.load(str(input_path))

    # 2) 预处理（清洗、分句）
    pre = Preprocessor()
    cleaned = pre.clean_text(raw_text)
    sentences = pre.split_sentences(cleaned)
    processed_text = "\n".join(sentences)

    # 3) 保存处理后的文本
    processed_file = processed_dir / f"{input_path.stem}_processed.txt"
    processed_file.write_text(processed_text, encoding="utf-8")

    # 4) 生成并保存嵌入
    embedder = Embedder()
    embeddings = embedder.encode([processed_text])
    embedding_file = embeddings_dir / f"{input_path.stem}_embeddings.pkl"
    with open(embedding_file, "wb") as f:
        pickle.dump(embeddings, f)

    # 5) 记录元数据（便于长期追踪）
    metadata = {
        "file_name": input_path.name,
        "file_path": str(input_path),
        "size_bytes": input_path.stat().st_size,
        "sha256": sha256(str(input_path)),
        "processed_text_path": str(processed_file),
        "embedding_path": str(embedding_file),
        "processed_time": datetime.utcnow().isoformat() + "Z",
    }
    meta_path = Path(args.metadata_file)
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    with meta_path.open("a", encoding="utf-8") as mf:
        mf.write(json.dumps(metadata, ensure_ascii=False) + "\n")

    print("处理完成：")
    print(f"- 处理后文本: {processed_file}")
    print(f"- 嵌入文件:   {embedding_file}")
    print(f"- 元数据记录: {meta_path}")

if __name__ == "__main__":
    main()