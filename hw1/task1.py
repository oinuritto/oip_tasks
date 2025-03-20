import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Настройки
start_url = "https://bigenc.ru"  # URL сайта
max_pages = 100  # Максимальное количество страниц для скачивания
output_folder = "downloaded_pages"
os.makedirs(output_folder, exist_ok=True)

# Файл для индекса
index_file = "index.txt"

# Множество для хранения уже посещенных URL
visited_urls = set()


# Функция для проверки, является ли URL допустимым
def is_valid_url(url):
    # Проверяем, что URL начинается с http/https и не ведет на внешний сайт
    return url.startswith("http") and (start_url + "/c") in url


def clean_response(resp):
    soup = BeautifulSoup(resp.text, "html.parser")
    for script in soup(["script", "style", "link"]):
        script.decompose()
    return str(soup)


# Функция для скачивания страницы
def download_page(url, page_number):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Сохраняем страницу в файл
        cleaned_response = clean_response(response)
        filename = os.path.join(output_folder, f"page_{page_number}.txt")
        with open(filename, "w", encoding="utf-8") as file:
            file.write(cleaned_response)

        # Записываем информацию в индекс
        with open(index_file, "a", encoding="utf-8") as index:
            index.write(f"{page_number}\t{url}\n")

        print(f"Страница {page_number} успешно скачана: {url}")
        return True

    except requests.RequestException as e:
        print(f"Ошибка при скачивании страницы {url}: {e}")
        return False


# Функция для поиска ссылок на странице
def find_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Находим все ссылки на странице
        links = set()
        for a_tag in soup.find_all("a", href=True):
            link = urljoin(url, a_tag["href"])
            if is_valid_url(link) and link not in visited_urls:
                links.add(link)

        return links

    except requests.RequestException as e:
        print(f"Ошибка при загрузке страницы {url}: {e}")
        return set()


# Основная функция краулера
def crawl(start_url, max_pages):
    queue = []
    page_number = 1

    if not is_valid_url(start_url):
        new_links = find_links(start_url)
        queue.extend(new_links)
    else:
        queue = [start_url]

    while queue and page_number <= max_pages:
        url = queue.pop(0)

        if url not in visited_urls:
            visited_urls.add(url)

            # Скачиваем страницу
            if download_page(url, page_number):
                page_number += 1

                # Ищем ссылки на текущей странице
                new_links = find_links(url)
                queue.extend(new_links)


if __name__ == "__main__":
    # Очищаем файл индекса перед началом
    with open(index_file, "w", encoding="utf-8") as index:
        index.write("")

    crawl(start_url, max_pages)
    print("Выкачка завершена.")
