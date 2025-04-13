import os
import json
import math
from collections import defaultdict
import re
from bs4 import BeautifulSoup

# Загрузка инвертированного индекса
with open('../hw3/inverted_index.json', 'r', encoding='utf-8') as f:
    inverted_index = json.load(f)

# Конфигурация путей
downloaded_pages_dir = '../hw1/downloaded_pages'
tokens_lemmas_dir = '../hw2/results'
output_terms_dir = 'results/terms'
output_lemmas_dir = 'results/lemmas'

# Создание директорий для результатов
os.makedirs(output_terms_dir, exist_ok=True)
os.makedirs(output_lemmas_dir, exist_ok=True)

# Получение списка всех документов
all_docs = [f for f in os.listdir(downloaded_pages_dir) if f.startswith('page_')]
n_documents = len(all_docs)


def clean_text(html):
    """Очищает HTML и возвращает текст."""
    soup = BeautifulSoup(html, "html.parser")

    # Получаем текст с сохранением пробелов
    text = soup.get_text(separator=" ", strip=True)

    # Заменяем множественные пробелы на один
    text = re.sub(r'\s+', ' ', text)
    return text


def get_words(text):
    text = clean_text(text)
    words = re.findall(r'\b[а-яА-ЯёЁ]+\b', text.lower())
    return words


def process_document(doc_name):
    # Извлечение номера страницы
    page_num = doc_name.split('_')[1].split('.')[0]

    # Чтение исходного документа и подсчёт частоты терминов
    with open(os.path.join(downloaded_pages_dir, doc_name), 'r', encoding='utf-8') as f:
        text = f.read()
    tokens = get_words(text)
    term_freq = defaultdict(int)
    for token in tokens:
        term_freq[token] += 1
    total_terms = len(tokens)

    # if page_num == "1":
    #     print(term_freq)

    # Загрузка уникальных токенов документа из tokens_page_X.txt
    tokens_file = os.path.join(tokens_lemmas_dir, f'tokens_page_{page_num}.txt')
    if not os.path.exists(tokens_file):
        return
    with open(tokens_file, 'r', encoding='utf-8') as f:
        unique_tokens = [line.strip() for line in f if line.strip()]

    # Расчет TF-IDF для терминов
    terms_output = []
    for token in unique_tokens:
        freq = term_freq.get(token, 0)
        tf = freq / total_terms

        # if page_num == "1":
        #     print(f'token = {token}, freq = {freq}, tf = {tf}\n')

        # IDF из инвертированного индекса
        df = len(inverted_index.get(token, []))
        idf = math.log(n_documents / df)

        terms_output.append(f"{token} {idf:.4f} {(tf * idf):.4f}")

    # Сохранение результатов для терминов
    with open(os.path.join(output_terms_dir, f'tfidf_terms_{doc_name}'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(terms_output))

    # Обработка лемм ----------------------------------------------------------
    lemmas_file = os.path.join(tokens_lemmas_dir, f'lemmas_page_{page_num}.txt')
    if not os.path.exists(lemmas_file):
        return

    # Чтение лемм и связанных токенов
    lemma_tokens = defaultdict(list)
    with open(lemmas_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(' ', 1)
            if len(parts) < 2:
                continue
            lemma, tokens_str = parts
            lemma_tokens[lemma] = tokens_str.split()

    # Расчет TF-IDF для лемм
    lemmas_output = []
    for lemma, tokens in lemma_tokens.items():
        # Сумма частот всех токенов леммы
        sum_freq = sum(term_freq.get(t, 0) for t in tokens)
        tf = sum_freq / total_terms

        # Документы, содержащие хотя бы один токен леммы
        docs_with_lemma = set()
        for token in tokens:
            docs_with_lemma.update(inverted_index.get(token, []))
        idf = math.log(n_documents / len(docs_with_lemma)) if docs_with_lemma else 0.0

        lemmas_output.append(f"{lemma} {idf:.4f} {(tf * idf):.4f}")

    # Сохранение результатов для лемм
    with open(os.path.join(output_lemmas_dir, f'tfidf_lemmas_{doc_name}'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lemmas_output))


# Обработка всех документов
for doc in all_docs:
    process_document(doc)
