import os
import math
from collections import defaultdict
from pymorphy3 import MorphAnalyzer


class LemmaSearchEngine:
    def __init__(self, tfidf_dir="../hw4/results/lemmas"):
        self.tfidf_dir = tfidf_dir
        self.doc_vectors, self.all_idf = self._load_vectors_and_idf()
        self.morph = MorphAnalyzer()

    def _load_vectors_and_idf(self):
        vectors = {}
        idf_dict = {}

        for file in os.listdir(self.tfidf_dir):
            if file.startswith("tfidf_lemmas_page_") and file.endswith(".txt"):
                doc_id = file[len("tfidf_lemmas_page_"):-4]
                vectors[doc_id] = {}
                with open(os.path.join(self.tfidf_dir, file), "r", encoding="utf-8") as f:
                    for line in f:
                        lemma, idf, tfidf = line.strip().split()
                        vectors[doc_id][lemma] = float(tfidf)
                        # Берем IDF только один раз
                        if lemma not in idf_dict:
                            idf_dict[lemma] = float(idf)
        return vectors, idf_dict

    def lemmatize_query(self, query: str) -> list[str]:
        tokens = query.lower().split()
        lemmas = [self.morph.parse(token)[0].normal_form for token in tokens]
        print(f"Леммы запроса: {lemmas}")  # Для отладки
        return lemmas

    def build_query_vector(self, query_lemmas: list[str]) -> dict[str, float]:
        tf = defaultdict(float)
        total_terms = len(query_lemmas)
        for lemma in query_lemmas:
            tf[lemma] += 1 / total_terms
        return {lemma: tf[lemma] * self.all_idf.get(lemma, 0.0) for lemma in query_lemmas}

    def search(self, query: str, top_n=10) -> list[tuple[str, float]]:
        query_lemmas = self.lemmatize_query(query)
        query_vector = self.build_query_vector(query_lemmas)

        scores = []
        for doc, doc_vector in self.doc_vectors.items():
            similarity = self.cosine_similarity(query_vector, doc_vector)
            scores.append((doc, similarity))

        return sorted(scores, key=lambda x: x[1], reverse=True)[:top_n]

    def cosine_similarity(self, query_vec: dict, doc_vec: dict) -> float:
        dot = sum(query_vec.get(lemma, 0) * doc_vec.get(lemma, 0) for lemma in query_vec)
        norm_query = math.sqrt(sum(v ** 2 for v in query_vec.values()))
        norm_doc = math.sqrt(sum(v ** 2 for v in doc_vec.values()))
        return dot / (norm_query * norm_doc) if (norm_query * norm_doc) != 0 else 0.0


# Пример использования
if __name__ == "__main__":
    engine = LemmaSearchEngine()
    print("Поисковая система запущена. Введите 'exit' для выхода.\n")

    while True:
        try:
            query = input("Поисковый запрос: ").strip()
            if not query:
                continue
            if query.lower() == 'exit':
                print("Завершение работы...")
                break

            # Выполнение поиска
            results = engine.search(query)

            # Вывод результатов
            print(f"\nРезультаты для запроса '{query}':")
            for i, (doc, score) in enumerate(results, 1):
                print(f"{i}. {doc} (сходство: {score:.4f})")
            print()

        except KeyboardInterrupt:
            print("\nЗавершение работы...")
            break
        except Exception as e:
            print(f"\nОшибка: {str(e)}")
            continue