from collections import Counter
from typing import Dict
from models.models import ProcessedFile, WordStat


def calculate_collection_statistics(collection_id: int, db) -> Dict:
    processed_files = db.query(ProcessedFile).filter(ProcessedFile.collection_id == collection_id).all()

    combined_text = []
    for processed_file in processed_files:
        try:
            with open(processed_file.file_path, 'r', encoding='utf-8') as file:
                combined_text.extend(file.readlines())
        except Exception as e:
            print(f"Error reading file {processed_file.file_path}: {e}")

    terms = []
    for line in combined_text:
        terms.extend(line.strip().lower().split())

    tf_counter = Counter(terms)

    unique_terms = set(terms)
    idf_values = {}
    for term in unique_terms:
        word_stat = db.query(WordStat).filter(WordStat.term == term).first()
        if word_stat:
            idf_values[term] = word_stat.idf

    statistics = {
        "tf": {term: tf_counter[term] for term in unique_terms},
        "idf": idf_values
    }

    return statistics
