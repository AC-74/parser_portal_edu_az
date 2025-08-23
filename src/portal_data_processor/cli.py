import argparse
from pathlib import Path

from .client import get_relevant_universities

def main():
    ap = argparse.ArgumentParser(description="Обработка данных портала edu.az.")
    ap.add_argument("--data-dir", type=Path, default=Path("."), help="Путь к директории с JSON-файлами.")
    args = ap.parse_args()

    print("---" + " Этап 1: Определение релевантных университетов" + "---")
    try:
        relevant_uni_ids = get_relevant_universities(args.data_dir)
        print("Найденные ID университетов:")
        print(relevant_uni_ids)
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        return

    # Следующие этапы (сбор данных, генерация отчета) будут добавлены сюда.
    print("\n" + "---" + " Следующий шаг: Сбор детальной информации по этим университетам" + "---")

if __name__ == "__main__":
    main()
