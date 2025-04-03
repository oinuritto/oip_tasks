import json
import re


class BooleanSearch:
    def __init__(self, index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            self.index = json.load(f)
        # Собираем множество всех документов
        self.all_docs = set()
        for docs in self.index.values():
            self.all_docs.update(docs)

    def parse_query(self, query):
        """Разбор запроса с поддержкой скобок и операторов"""
        tokens = re.findall(r'\(|\)|AND|OR|NOT|\w+', query.upper())
        output = []
        operators = []
        precedence = {'NOT': 3, 'AND': 2, 'OR': 1}

        for token in tokens:
            if token == '(':
                operators.append(token)
            elif token == ')':
                while operators[-1] != '(':
                    output.append(operators.pop())
                operators.pop()
            elif token in precedence:
                while (operators and operators[-1] != '(' and
                       precedence[operators[-1]] >= precedence[token]):
                    output.append(operators.pop())
                operators.append(token)
            else:
                output.append(token)

        while operators:
            output.append(operators.pop())

        return output

    def search(self, postfix_expr):
        """Выполнение поиска по постфиксному выражению"""
        stack = []

        for token in postfix_expr:
            if token == 'AND':
                right = set(stack.pop())
                left = set(stack.pop())
                stack.append(left & right)
            elif token == 'OR':
                right = set(stack.pop())
                left = set(stack.pop())
                stack.append(left | right)
            elif token == 'NOT':
                operand = set(stack.pop())
                stack.append(self.all_docs - operand)
            else:
                # Ищем токен в нижнем регистре
                docs = set(self.index.get(token.lower(), []))
                stack.append(docs)

        return sorted(stack.pop()) if stack else []

    def process_query(self, query):
        """Обработка пользовательского запроса"""
        postfix = self.parse_query(query)
        return self.search(postfix)


if __name__ == '__main__':
    searcher = BooleanSearch('inverted_index.json')

    print("Булев поиск по индексу. Поддерживаются операторы AND, OR, NOT и скобки.")
    print("Пример запроса: (кошка AND собака) OR попугай NOT черепаха")

    while True:
        try:
            query = input("\nВведите запрос (или 'exit' для выхода): ").strip()
            if query.lower() == 'exit':
                break

            results = searcher.process_query(query)
            print(f"\nНайдено документов: {len(results)}")
            if results:
                print("Совпадающие документы:")
                for doc in results:
                    print(f"- {doc}")
            else:
                print("Совпадений не найдено")

        except Exception as e:
            print(f"Ошибка: {e}. Проверьте синтаксис запроса.")