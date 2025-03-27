import os
import re
import nltk
import pymorphy3
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")

morph = pymorphy3.MorphAnalyzer()

# Стоп-слова на русском языке
russian_stopwords = set(stopwords.words("russian"))

# Папка с HTML-файлами
INPUT_FOLDER = "../hw1/downloaded_pages"
OUTPUT_FOLDER = "results"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Регулярное выражение для фильтрации только русских слов
RUSSIAN_WORDS = re.compile(r"^[а-яА-ЯёЁ]+$")


def clean_text(html):
    """Очищает HTML и возвращает текст."""
    soup = BeautifulSoup(html, "html.parser")

    # Получаем текст с сохранением пробелов
    text = soup.get_text(separator=" ", strip=True)

    # Заменяем множественные пробелы на один
    text = re.sub(r'\s+', ' ', text)
    return text


def tokenize(text):
    """Токенизирует текст, оставляя только русские слова."""
    words = word_tokenize(text, language="russian")
    tokens = {word.lower() for word in words if RUSSIAN_WORDS.match(word) and word.lower() not in russian_stopwords}
    return tokens


def lemmatize(tokens):
    """Лемматизирует список токенов и группирует их."""
    lemma_dict = {}
    for token in tokens:
        lemma = morph.parse(token)[0].normal_form  # Получаем лемму
        if lemma in lemma_dict:
            lemma_dict[lemma].add(token)
        else:
            lemma_dict[lemma] = {token}
    return lemma_dict


def process_files():
    """Обрабатывает файлы из папки и создаёт файлы с токенами и леммами."""

    for filename in os.listdir(INPUT_FOLDER):
        all_tokens = set()
        filepath = os.path.join(INPUT_FOLDER, filename)
        with open(filepath, "r", encoding="utf-8") as file:
            html = file.read()
            text = clean_text(html)
            tokens = tokenize(text)
            all_tokens.update(tokens)

            output_tokens = os.path.join(OUTPUT_FOLDER, f"tokens_{filename}")
            output_lemmas = os.path.join(OUTPUT_FOLDER, f"lemmas_{filename}")
            # Записываем токены в файл
            with open(output_tokens, "w", encoding="utf-8") as file:
                file.write("\n".join(sorted(all_tokens)))

            # Лемматизируем и записываем леммы
            lemmas = lemmatize(all_tokens)
            with open(output_lemmas, "w", encoding="utf-8") as file:
                for lemma, words in sorted(lemmas.items()):
                    file.write(f"{lemma} {' '.join(sorted(words))}\n")

    print(f"Готово! Файлы сохранены.")


# Запуск обработки
process_files()
