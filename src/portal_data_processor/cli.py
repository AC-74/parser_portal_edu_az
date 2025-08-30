import argparse
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import requests
import base64
from urllib.parse import urlparse

import pandas as pd
from jinja2 import Environment, FileSystemLoader

from .client import process_and_enrich_data, get_all_specialties

# Константа для локального файла-заполнителя
PLACEHOLDER_IMAGE = "images/placeholder.png"

def get_image_as_base64(url: str) -> str:
    """
    Загружает изображение по URL и возвращает его в виде строки Base64 Data URI.
    В случае ошибки возвращает путь к локальному заполнителю.
    """
    if not url or not url.startswith('http'):
        return PLACEHOLDER_IMAGE

    try:
        # Используем более полный набор заголовков для имитации браузера
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': f"{urlparse(url).scheme}://{urlparse(url).netloc}/"
        }

        print(f"Загрузка изображения: {url}")
        response = requests.get(url, stream=True, headers=headers, allow_redirects=True, timeout=20)
        response.raise_for_status()

        # Проверяем, что контент не пустой
        content = response.content
        if not content:
            print(f"Предупреждение: Пустой ответ от {url}")
            return PLACEHOLDER_IMAGE

        encoded_string = base64.b64encode(content).decode('utf-8')
        content_type = response.headers.get('content-type', 'image/jpeg')

        return f"data:{content_type};base64,{encoded_string}"

    except requests.exceptions.RequestException as e:
        print(f"Ошибка загрузки изображения {url}: {e}")
        return PLACEHOLDER_IMAGE

def generate_html_report(df: pd.DataFrame, output_path: Path):
    template_dir = Path(__file__).parent
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report_template.html")

    universities_data = {}
    all_specialties = set()

    # Группируем по университетам для более эффективной обработки
    for uni_id, group in df.groupby("University_ATIS_ID"):
        first_row = group.iloc[0]

        # Скачиваем и кодируем фото ОДИН раз для каждого университета
        photo_data_uri = get_image_as_base64(first_row["Photo_URL"])

        universities_data[uni_id] = {
            "name": first_row["University"],
            "description": first_row["Description"],
            "address": first_row["Address"],
            "latitude": first_row["Latitude"],
            "longitude": first_row["Longitude"],
            "photo_url": photo_data_uri,
            "distance": first_row["distance"],
            "programs": []
        }

        for _, row in group.iterrows():
            program_data = {
                "Specialty": row["Specialty"],
                "Specialty_Name_AZ": row["Specialty_Name_AZ"],
                "Tuition_Fee": row["Tuition_Fee"],
                "Tuition_Fee_Numeric": float(row["Tuition_Fee"]) if isinstance(row["Tuition_Fee"], (int, float)) else float("inf")
            }
            universities_data[uni_id]["programs"].append(program_data)
            all_specialties.add(row["Specialty"])

    # Сортировка программ по стоимости
    for uni_id in universities_data:
        universities_data[uni_id]["programs"] = sorted(universities_data[uni_id]["programs"], key=lambda x: x["Tuition_Fee_Numeric"])

    rendered_html = template.render(
        report_date=datetime.now().strftime("%d.%m.%Y"),
        universities=universities_data,
        all_specialties=sorted(list(all_specialties))
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    print("HTML-отчет сгенерирован.")


def main():
    ap = argparse.ArgumentParser(description="Обработка данных портала edu.az.")
    ap.add_argument("--data-dir", type=Path, default=Path("."), help="Путь к директории с JSON-файлами.")
    ap.add_argument("--min-price", type=float, help="Минимальная стоимость обучения для фильтрации.")
    ap.add_argument("--max-price", type=float, help="Максимальная стоимость обучения для фильтрации.")
    ap.add_argument("--specialties", type=str, help="Список специальностей для фильтрации, разделенных запятыми (на русском языке).")
    ap.add_argument("--list-specialties", action="store_true", help="Вывести список всех доступных специальностей и выйти.")
    ap.add_argument("--output-html", type=Path, default=Path("programs_report.html"), help="Путь для сохранения итогового HTML-отчета.")
    args = ap.parse_args()

    if args.list_specialties:
        print("--- Доступные специальности ---")
        try:
            specialties = get_all_specialties(args.data_dir)
            for s in specialties:
                print(s)
        except FileNotFoundError as e:
            print(f"Ошибка: {e}")
        return

    print("--- Этап 1: Обработка и обогащение данных ---")
    selected_specialties_list = [s.strip() for s in args.specialties.split(",")] if args.specialties else None

    try:
        final_df = process_and_enrich_data(
            data_dir=args.data_dir,
            min_price=args.min_price,
            max_price=args.max_price,
            selected_specialties=selected_specialties_list
        )
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        return

    if final_df.empty:
        print("Не найдено программ, соответствующих заданным критериям.")
        return

    print(f"Найдено {len(final_df)} программ после всех фильтров.")

    print("--- Этап 2: Генерация интерактивного HTML-отчета ---")
    generate_html_report(final_df, args.output_html)

    print(f"\nРабота завершена. Отчет сохранен в: {args.output_html.resolve()}")


if __name__ == "__main__":
    main()
