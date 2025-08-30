import pandas as pd
from pathlib import Path

# --- Константы для фильтрации (те же, что и в client.py) ---
LANG_RU_ID = 14
FORM_AYANI_ID = 2
LEVEL_MAGISTRATURA_ID = 3

def test_selection():
    """
    Эта функция проверяет, что фильтрация данных в файле
    foreigner_specialities.json работает корректно.
    """
    print("--- Запуск теста на корректность выборки данных ---")
    
    specialities_path = Path("foreigner_specialities.json")
    
    if not specialities_path.exists():
        print(f"ОШИБКА: Тестовый файл не найден: {specialities_path.resolve()}")
        return

    print(f"Загрузка данных из: {specialities_path.resolve()}")
    df = pd.read_json(specialities_path)
    
    print(f"Всего записей в исходном файле: {len(df)}")
    
    # --- Применение фильтров ---
    mask = (
        (df["educationLevelId"] == LEVEL_MAGISTRATURA_ID) &
        (df["educationFormId"] == FORM_AYANI_ID) &
        (df["educationLanguageId"] == LANG_RU_ID)
    )
    filtered_df = df[mask]
    
    print(f"Найдено записей после фильтрации: {len(filtered_df)}")
    
    print("\n--- Проверка уникальных значений в отфильтрованных данных ---")
    
    correct_selection = True
    
    # Проверка Уровня образования
    levels = filtered_df["educationLevelId"].unique()
    print(f"Уникальные ID уровней образования: {levels}")
    if list(levels) != [LEVEL_MAGISTRATURA_ID]:
        print(f"ОШИБКА: Найдены лишние уровни образования! Ожидался только ID {LEVEL_MAGISTRATURA_ID}.")
        correct_selection = False

    # Проверка Формы обучения
    forms = filtered_df["educationFormId"].unique()
    print(f"Уникальные ID форм обучения: {forms}")
    if list(forms) != [FORM_AYANI_ID]:
        print(f"ОШИБКА: Найдены лишние формы обучения! Ожидался только ID {FORM_AYANI_ID}.")
        correct_selection = False
        
    # Проверка Языка обучения
    languages = filtered_df["educationLanguageId"].unique()
    print(f"Уникальные ID языков обучения: {languages}")
    if list(languages) != [LANG_RU_ID]:
        print(f"ОШИБКА: Найдены лишние языки обучения! Ожидался только ID {LANG_RU_ID}.")
        correct_selection = False
        
    print("\n--- Итог теста ---")
    if correct_selection:
        print("✅ УСПЕХ: Все фильтры применены корректно. Выбраны только очные магистерские программы на русском языке.")
    else:
        print("❌ ПРОВАЛ: Фильтрация работает некорректно. В выборку попали лишние данные.")
        
    if not filtered_df.empty:
        print("\n--- Пример первых 5 отфильтрованных записей ---")
        print(filtered_df.head().to_string())

if __name__ == "__main__":
    test_selection()