import json
from pathlib import Path
from typing import Dict, List

import pandas as pd

# --- Константы для фильтрации ---
LANG_RU_ID = 14
FORM_AYANI_ID = 2
LEVEL_MAGISTRATURA_ID = 3

def get_relevant_universities(data_dir: Path) -> List[str]:
    """
    Загружает данные о специальностях, фильтрует их по заданным критериям
    и возвращает уникальный список ID необходимых университетов.
    """
    specialities_path = data_dir / "foreigner_specialities.json"
    if not specialities_path.exists():
        raise FileNotFoundError(f"Не найден файл со специальностями: {specialities_path}")

    specialities_df = pd.read_json(specialities_path)

    # Фильтрация по критериям из starter.md
    mask = (
        (specialities_df["educationLevelId"] == LEVEL_MAGISTRATURA_ID) &
        (specialities_df["educationFormId"] == FORM_AYANI_ID) &
        (specialities_df["educationLanguageId"] == LANG_RU_ID)
    )
    filtered_df = specialities_df[mask]

    # Получаем уникальные ID университетов
    relevant_ids = filtered_df["enterprise_ATIS_ID"].unique().tolist()
    
    print(f"Найдено {len(relevant_ids)} уникальных университетов, предлагающих программы по заданным критериям.")
    return relevant_ids
