#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор отчёта по программам подготовки на русском языке
Без использования консоли - создаёт HTML отчёт напрямую
"""

import json
from datetime import datetime
from pathlib import Path

# Загружаем данные о программах
data_file = Path(__file__).parent / "foreigner_specialities2.json"
with open(data_file, 'r', encoding='utf-8') as f:
    programs = json.load(f)

# Загружаем данные об университетах
uni_file = Path(__file__).parent / "atis_enterprisers.json"
with open(uni_file, 'r', encoding='utf-8') as f:
    universities = json.load(f)

# Создаём словарь университетов для быстрого поиска
uni_dict = {uni['ATIS_ID']: uni for uni in universities}

# Сначала найдём все программы со специальностью 60213
specialty_60213_programs = []
for prog in programs:
    if prog.get('specialty_code') == '60213':
        uni_id = prog.get('enterprise_ATIS_ID')
        uni_info = uni_dict.get(uni_id, {})
        
        # Определяем язык
        lang_id = prog.get('educationLanguageId')
        if lang_id == 1:
            lang_name = 'Английский'
        elif lang_id == 2:
            lang_name = 'Азербайджанский'
        elif lang_id == 14:
            lang_name = 'Русский'
        else:
            lang_name = f'ID {lang_id}'
        
        specialty_60213_programs.append({
            'specialty_code': prog.get('specialty_code', 'N/A'),
            'name': prog.get('name', 'N/A'),
            'university': uni_info.get('shortName', uni_info.get('name', 'N/A')),
            'preparation_amount': prog.get('preparation_amount') or 0,
            'tuition_amount': prog.get('entranceSpecialtyPaymentAmount') or 0,
            'education_form': 'Очная' if prog.get('educationFormId') == 2 else 'Заочная',
            'education_level': prog.get('educationLevelId', 'N/A'),
            'language': lang_name,
            'language_id': lang_id,
            'ATIS_ID': prog.get('ATIS_ID', 'N/A'),
        })

# Фильтруем программы подготовки на русском языке
# educationLanguageId: 1 = английский, 2 = азербайджанский, 14 = русский
russian_prep_programs = []

for prog in programs:
    lang_id = prog.get('educationLanguageId')
    prep_amount = prog.get('preparation_amount')
    
    # Фильтр: русский язык (14) и есть стоимость подготовки
    if lang_id == 14 and prep_amount is not None and prep_amount > 0:
        # Получаем информацию об университете
        uni_id = prog.get('enterprise_ATIS_ID')
        uni_info = uni_dict.get(uni_id, {})
        
        russian_prep_programs.append({
            'specialty_code': prog.get('specialty_code', 'N/A'),
            'name': prog.get('name', 'N/A'),
            'university': uni_info.get('shortName', uni_info.get('name', 'N/A')),
            'preparation_amount': prep_amount,
            'tuition_amount': prog.get('entranceSpecialtyPaymentAmount') or 0,
            'education_form': 'Очная' if prog.get('educationFormId') == 2 else 'Заочная',
            'education_level': prog.get('educationLevelId', 'N/A'),
            'ATIS_ID': prog.get('ATIS_ID', 'N/A'),
        })

# Сортируем по стоимости подготовки (от меньшего к большему)
russian_prep_programs.sort(key=lambda x: x['preparation_amount'])

# Статистика
total_programs = len(russian_prep_programs)
min_price = min([p['preparation_amount'] for p in russian_prep_programs]) if russian_prep_programs else 0
max_price = max([p['preparation_amount'] for p in russian_prep_programs]) if russian_prep_programs else 0
avg_price = sum([p['preparation_amount'] for p in russian_prep_programs]) / total_programs if total_programs > 0 else 0

# Группируем по стоимости
price_groups = {}
for prog in russian_prep_programs:
    price = prog['preparation_amount']
    if price not in price_groups:
        price_groups[price] = []
    price_groups[price].append(prog)

# Генерируем HTML отчёт
html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчёт: Программы подготовки на русском языке</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.95;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .price-group {{
            margin-bottom: 40px;
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            border-left: 5px solid #667eea;
        }}
        
        .price-group h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .price-badge {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 0.9em;
        }}
        
        .programs-grid {{
            display: grid;
            gap: 20px;
        }}
        
        .program-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            border-left: 4px solid transparent;
        }}
        
        .program-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.12);
            border-left-color: #764ba2;
        }}
        
        .program-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
            gap: 20px;
        }}
        
        .program-title {{
            flex: 1;
        }}
        
        .program-title h3 {{
            color: #333;
            font-size: 1.3em;
            margin-bottom: 8px;
        }}
        
        .program-code {{
            color: #666;
            font-size: 0.9em;
            font-family: 'Courier New', monospace;
        }}
        
        .program-prices {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .price-tag {{
            background: #e8f5e9;
            color: #2e7d32;
            padding: 8px 15px;
            border-radius: 8px;
            font-weight: bold;
            white-space: nowrap;
        }}
        
        .price-tag.tuition {{
            background: #fff3e0;
            color: #e65100;
        }}
        
        .program-details {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }}
        
        .detail-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: #666;
            font-size: 0.95em;
        }}
        
        .detail-icon {{
            color: #667eea;
        }}
        
        .university-name {{
            font-weight: 600;
            color: #764ba2;
        }}
        
        .top-section {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 40px;
        }}
        
        .top-section h2 {{
            color: #d84315;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .highlight {{
            background: #fff;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        footer {{
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .stats {{
                grid-template-columns: 1fr;
            }}
            
            .program-header {{
                flex-direction: column;
            }}
            
            .program-prices {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 Программы подготовки на русском языке</h1>
            <p>Актуальные данные от {datetime.now().strftime('%d.%m.%Y')}</p>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Всего программ</div>
                <div class="stat-value">{total_programs}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Минимальная стоимость</div>
                <div class="stat-value">{min_price:,.0f} ₼</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Максимальная стоимость</div>
                <div class="stat-value">{max_price:,.0f} ₼</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Средняя стоимость</div>
                <div class="stat-value">{avg_price:,.0f} ₼</div>
            </div>
        </div>
        
        <div class="content">
"""

# Добавляем информацию о специальности 60213
if specialty_60213_programs:
    html_content += """
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 30px; border-radius: 15px; margin-bottom: 40px; color: white;">
                <h2 style="color: white; margin-bottom: 20px; font-size: 2em;">🎯 Специальность 60213 (History and theory of international relations)</h2>
"""
    for prog in specialty_60213_programs:
        prep_text = f"{prog['preparation_amount']:,.0f} AZN" if prog['preparation_amount'] > 0 else "Не указано"
        html_content += f"""
                <div style="background: rgba(255,255,255,0.95); color: #333; padding: 20px; border-radius: 10px; margin: 10px 0;">
                    <strong style="font-size: 1.2em;">{prog['name']}</strong><br>
                    🏛️ <strong>{prog['university']}</strong><br>
                    🌐 Язык обучения: <strong>{prog['language']}</strong> | 📖 {prog['education_form']}<br>
                    💰 Подготовка: <strong>{prep_text}</strong> | Обучение: <strong>{prog['tuition_amount']:,.0f} AZN</strong><br>
                    📋 Код: {prog['specialty_code']} | ID: {prog['ATIS_ID']}
                </div>
"""
    html_content += """
            </div>
"""

# Добавляем ТОП-10 самых дешёвых программ
if russian_prep_programs:
    html_content += """
            <div class="top-section">
                <h2>🏆 ТОП-10 самых дешёвых программ подготовки</h2>
"""
    for i, prog in enumerate(russian_prep_programs[:10], 1):
        html_content += f"""
                <div class="highlight">
                    <strong>#{i}. {prog['name']}</strong><br>
                    🏛️ {prog['university']}<br>
                    💰 Подготовка: <strong>{prog['preparation_amount']:,.0f} AZN</strong> | 
                    Обучение: {prog['tuition_amount']:,.0f} AZN<br>
                    📋 Код: {prog['specialty_code']}
                </div>
"""
    html_content += """
            </div>
"""

# Добавляем все программы, сгруппированные по стоимости
html_content += """
            <h2 style="margin-bottom: 30px; color: #333;">Все программы по стоимости</h2>
"""

for price in sorted(price_groups.keys()):
    progs = price_groups[price]
    html_content += f"""
            <div class="price-group">
                <h2>
                    <span class="price-badge">{price:,.0f} AZN</span>
                    <span style="font-weight: normal; font-size: 0.7em; color: #666;">({len(progs)} программ)</span>
                </h2>
                <div class="programs-grid">
"""
    
    for prog in progs:
        html_content += f"""
                    <div class="program-card">
                        <div class="program-header">
                            <div class="program-title">
                                <h3>{prog['name']}</h3>
                                <div class="program-code">Код: {prog['specialty_code']} | ID: {prog['ATIS_ID']}</div>
                            </div>
                            <div class="program-prices">
                                <div class="price-tag">Подготовка: {prog['preparation_amount']:,.0f} ₼</div>
                                <div class="price-tag tuition">Обучение: {prog['tuition_amount']:,.0f} ₼</div>
                            </div>
                        </div>
                        <div class="program-details">
                            <div class="detail-item">
                                <span class="detail-icon">🏛️</span>
                                <span class="university-name">{prog['university']}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-icon">📖</span>
                                <span>{prog['education_form']}</span>
                            </div>
                        </div>
                    </div>
"""
    
    html_content += """
                </div>
            </div>
"""

html_content += f"""
        </div>
        
        <footer>
            <p>Данные источника: foreigner_specialities2.json</p>
            <p>Отчёт создан: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
            <p>Всего найдено программ на русском языке с указанной стоимостью подготовки: {total_programs}</p>
        </footer>
    </div>
</body>
</html>
"""

# Сохраняем отчёт
output_file = Path(__file__).parent / "prep_prog_report.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Отчёт создан: {output_file}")
print(f"📊 Найдено программ: {total_programs}")
print(f"💰 Диапазон цен: {min_price:,.0f} - {max_price:,.0f} AZN")
print(f"📈 Средняя стоимость: {avg_price:,.0f} AZN")
