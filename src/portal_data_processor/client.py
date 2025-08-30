import json
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from haversine import haversine, Unit

# --- Константы для фильтрации ---
LANG_RU_ID = 14
FORM_AYANI_ID = 2
LEVEL_MAGISTRATURA_ID = 3

# Координаты станции метро "28 мая" в Баку (широта, долгота)
METRO_28_MAY_COORDS = (40.379722, 49.848889)

class PortalDataClient:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.translation_map = self._load_translations()

    def _load_translations(self) -> Dict[str, str]:
        """Загружает полный словарь переводов из JSON-файла."""
        translation_path = self.data_dir / "full_translation_map.json"
        if not translation_path.exists():
            # Возвращаем пустой словарь, если файл не найден,
            # чтобы избежать падения и позволить работать без переводов.
            print(f"Предупреждение: Файл переводов {translation_path} не найден. Переводы будут отсутствовать.")
            return {}
        with open(translation_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_translation(self, text: str, default: Optional[str] = None) -> str:
        """
        Получает перевод для текста. Если перевод не найден,
        возвращает сам текст или значение по умолчанию.
        """
        return self.translation_map.get(text, default if default is not None else text)

    def get_relevant_universities(self) -> List[str]:
        """
        Загружает данные о специальностях, фильтрует их по заданным критериям
        и возвращает уникальный список ID необходимых университетов.
        """
        specialities_path = self.data_dir / "foreigner_specialities.json"
        if not specialities_path.exists():
            raise FileNotFoundError(f"Не найден файл со специальностями: {specialities_path}")

        specialities_df = pd.read_json(specialities_path)

        mask = (
            (specialities_df["educationLevelId"] == LEVEL_MAGISTRATURA_ID) &
            (specialities_df["educationFormId"] == FORM_AYANI_ID) &
            (specialities_df["educationLanguageId"] == LANG_RU_ID)
        )
        filtered_df = specialities_df[mask]

        relevant_ids = filtered_df["enterprise_ATIS_ID"].unique().tolist()
        
        print(f"Найдено {len(relevant_ids)} уникальных университетов, предлагающих программы по заданным критериям.")
        return relevant_ids

    def _calculate_distance(self, lat1, lon1, lat2, lon2) -> float:
        """
        Рассчитывает расстояние между двумя точками по их координатам (в км).
        """
        return haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)

    def _load_university_details(self) -> Dict[str, Dict]:
        """
        Загружает детали университетов из university_details.json.
        """
        details_path = self.data_dir / "university_details.json"
        if not details_path.exists():
            print(f"Предупреждение: Файл {details_path} не найден. Детали университетов не будут загружены.")
            return {}
        with open(details_path, 'r', encoding='utf-8') as f:
            details = json.load(f)
        return {uni["ATIS_ID"]: uni for uni in details}

    def process_and_enrich_data(
        self,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        selected_specialties: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Загружает, объединяет, фильтрует и обогащает данные о программах.
        """
        specialities_df = pd.read_json(self.data_dir / "foreigner_specialities.json")
        enterprises_df = pd.read_json(self.data_dir / "atis_enterprisers.json")
        university_details = self._load_university_details()

        enterprises_df_renamed = enterprises_df.rename(columns={"ATIS_ID": "enterprise_ATIS_ID", "name": "university_name"})
        
        merged_df = pd.merge(
            specialities_df,
            enterprises_df_renamed[["enterprise_ATIS_ID", "university_name"]],
            on="enterprise_ATIS_ID",
            how="left"
        )

        mask = (
            (merged_df["educationLevelId"] == LEVEL_MAGISTRATURA_ID) &
            (merged_df["educationFormId"] == FORM_AYANI_ID) &
            (merged_df["educationLanguageId"] == LANG_RU_ID)
        )
        filtered_df = merged_df[mask].copy()

        if min_price is not None:
            filtered_df = filtered_df[filtered_df["entranceSpecialtyPaymentAmount"] >= min_price]
        if max_price is not None:
            filtered_df = filtered_df[filtered_df["entranceSpecialtyPaymentAmount"] <= max_price]

        if selected_specialties:
            inverted_map = {v: k for k, v in self.translation_map.items()}
            az_specialties = [inverted_map.get(name, name) for name in selected_specialties]
            filtered_df = filtered_df[filtered_df["name"].isin(az_specialties)]

        final_df = pd.DataFrame()
        final_df["University_ATIS_ID"] = filtered_df["enterprise_ATIS_ID"]
        final_df["University_Name_AZ"] = filtered_df["university_name"].str.strip()
        
        def format_university_name(az_name):
            ru_name = self.get_translation(az_name)
            description = self.get_translation(university_details.get(az_name, {}).get("description", ""))
            if ru_name and ru_name != az_name:
                return f"{ru_name} ({az_name})"
            return az_name
            
        final_df["University"] = final_df["University_Name_AZ"].apply(format_university_name)
        
        final_df["Specialty_Name_AZ"] = filtered_df["name"].str.strip()
        final_df["Specialty"] = final_df["Specialty_Name_AZ"].apply(lambda x: f"{self.get_translation(x)} ({x})")
        
        final_df["Language"] = "Русский (Rus dili)"
        final_df["Form"] = "Очная (Əyani)"
        final_df["Level"] = "Магистратура (Magistratura)"
        final_df["Tuition_Fee"] = filtered_df["entranceSpecialtyPaymentAmount"].apply(
            lambda x: int(x) if pd.notna(x) and x > 0 else "не указано"
        )

        def get_translated_detail(atis_id, key, default=""):
            detail = university_details.get(atis_id, {})
            original_text = detail.get(key, default)
            return self.get_translation(original_text)

        final_df["University_Name_RU"] = final_df["University_ATIS_ID"].apply(
            lambda x: get_translated_detail(x, "name", default="Неизвестно")
        )
        final_df["Description"] = final_df["University_ATIS_ID"].apply(
            lambda x: get_translated_detail(x, "description")
        )

        final_df["Address"] = final_df["University_ATIS_ID"].apply(lambda x: university_details.get(x, {}).get("address", "Неизвестно"))
        final_df["Latitude"] = final_df["University_ATIS_ID"].apply(lambda x: university_details.get(x, {}).get("latitude"))
        final_df["Longitude"] = final_df["University_ATIS_ID"].apply(lambda x: university_details.get(x, {}).get("longitude"))
        final_df["Photo_URL"] = final_df["University_ATIS_ID"].apply(lambda x: university_details.get(x, {}).get("photo_url", ""))

        def get_distance(row):
            if pd.isna(row["Latitude"]) or pd.isna(row["Longitude"]):
                return "Неизвестно"
            return round(self._calculate_distance(row["Latitude"], row["Longitude"], METRO_28_MAY_COORDS[0], METRO_28_MAY_COORDS[1]), 2)

        final_df["distance"] = final_df.apply(get_distance, axis=1)

        final_df = final_df.drop_duplicates(subset=["University_ATIS_ID", "Specialty_Name_AZ"]).sort_values(by=["University", "Specialty"]).reset_index(drop=True)
        
        return final_df

    def get_all_specialties(self) -> List[str]:
        """
        Загружает все специальности и возвращает их уникальный список на русском языке.
        """
        specialities_path = self.data_dir / "foreigner_specialities.json"
        if not specialities_path.exists():
            raise FileNotFoundError(f"Не найден файл со специальностями: {specialities_path}")
        specialities_df = pd.read_json(specialities_path)
        unique_az_specialties = specialities_df["name"].unique().tolist()
        
        ru_specialties = [f"{self.get_translation(az_name)} ({az_name})" for az_name in unique_az_specialties]
        return sorted(ru_specialties)

# --- Функции-обертки для обратной совместимости с CLI ---

def process_and_enrich_data(
    data_dir: Path,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    selected_specialties: Optional[List[str]] = None
) -> pd.DataFrame:
    client = PortalDataClient(data_dir)
    return client.process_and_enrich_data(min_price, max_price, selected_specialties)

def get_all_specialties(data_dir: Path) -> List[str]:
    client = PortalDataClient(data_dir)
    return client.get_all_specialties()

def get_relevant_universities(data_dir: Path) -> List[str]:
    client = PortalDataClient(data_dir)
    return client.get_relevant_universities()
