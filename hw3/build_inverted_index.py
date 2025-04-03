import os
import json
import re
from collections import defaultdict


def extract_page_number(doc_id):
    match = re.search(r'_(\d+)\.', doc_id)
    return int(match.group(1)) if match else 0


def build_index_from_tokens(tokens_dir):
    inverted_index = defaultdict(list)

    for filename in os.listdir(tokens_dir):
        if filename.startswith('tokens') and filename.endswith('.txt'):
            doc_id = filename.replace('tokens_', '')

            with open(os.path.join(tokens_dir, filename), 'r', encoding='utf-8') as f:
                # Читаем уникальные токены
                tokens = set(line.strip() for line in f if line.strip())

                for token in tokens:
                    inverted_index[token].append(doc_id)

    sorted_index = {k: sorted(v, key=extract_page_number) for k, v in sorted(inverted_index.items())}

    return sorted_index


def save_index(index, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    INDEX_FILE = 'inverted_index.json'
    TOKENS_DIR = '../hw2/results'  # Папка с файлами tokens_page_*.txt

    index = build_index_from_tokens(TOKENS_DIR)
    save_index(index, INDEX_FILE)
    print(f'Инвертированный индекс сохранен в {INDEX_FILE}')