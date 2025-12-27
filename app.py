from flask import Flask, request, jsonify
import folium
from folium.plugins import MarkerCluster, MeasureControl, MiniMap, Fullscreen, HeatMap
import math

app = Flask(__name__)

# Добавляем данные по солнечной инсоляции для регионов России (кВтч/м²/день)
SOLAR_INSOLATION = {
    'Москва': {'coords': [55.7558, 37.6176], 'insolation': 2.5, 'color': '#FF6B6B'},
    'Санкт-Петербург': {'coords': [59.9390, 30.3158], 'insolation': 2.0, 'color': '#4ECDC4'},
    'Новосибирск': {'coords': [55.0302, 82.9204], 'insolation': 3.0, 'color': '#FFEAA7'},
    'Екатеринбург': {'coords': [56.8380, 60.5973], 'insolation': 2.8, 'color': '#DDA0DD'},
    'Казань': {'coords': [55.7961, 49.1064], 'insolation': 2.7, 'color': '#96CEB4'},
    'Сочи': {'coords': [43.5855, 39.7231], 'insolation': 3.5, 'color': '#FFD700'},
    'Владивосток': {'coords': [43.1155, 131.8855], 'insolation': 3.2, 'color': '#1E90FF'},
    'Красноярск': {'coords': [56.0153, 92.8932], 'insolation': 2.9, 'color': '#FF8C00'},
    'Ростов-на-Дону': {'coords': [47.2224, 39.7187], 'insolation': 3.1, 'color': '#32CD32'},
    'Волгоград': {'coords': [48.7080, 44.5133], 'insolation': 3.3, 'color': '#FF4500'},
    'Махачкала': {'coords': [42.9831, 47.5047], 'insolation': 3.4, 'color': '#FF1493'},
    'Калининград': {'coords': [54.7104, 20.4522], 'insolation': 2.3, 'color': '#87CEEB'},
    'Хабаровск': {'coords': [48.4802, 135.0719], 'insolation': 3.1, 'color': '#DC143C'},
    'Якутск': {'coords': [62.0278, 129.7315], 'insolation': 2.8, 'color': '#2F4F4F'},
    'Севастополь': {'coords': [44.6167, 33.5254], 'insolation': 3.6, 'color': '#FF6347'},
    'Астрахань': {'coords': [46.3497, 48.0408], 'insolation': 3.5, 'color': '#00CED1'},
    'Краснодар': {'coords': [45.0355, 38.9753], 'insolation': 3.3, 'color': '#7CFC00'},
    'Ставрополь': {'coords': [45.0445, 41.9691], 'insolation': 3.2, 'color': '#D2691E'},
    'Самара': {'coords': [53.1959, 50.1002], 'insolation': 2.9, 'color': '#8A2BE2'},
    'Уфа': {'coords': [54.7351, 55.9587], 'insolation': 2.7, 'color': '#FF00FF'},
}

# Зоны солнечной эффективности
SOLAR_ZONES = [
    {'name': 'Высокая эффективность', 'color': '#FFD700', 'min': 3.0, 'max': 4.0},
    {'name': 'Средняя эффективность', 'color': '#FFA500', 'min': 2.5, 'max': 3.0},
    {'name': 'Умеренная эффективность', 'color': '#87CEEB', 'min': 2.0, 'max': 2.5},
    {'name': 'Низкая эффективность', 'color': '#B0C4DE', 'min': 1.5, 'max': 2.0},
]


def calculate_solar_potential(city_data, panel_area=10, efficiency=0.18):
    """Рассчитывает потенциал солнечной энергии"""
    daily_kwh = city_data['insolation'] * panel_area * efficiency
    monthly_kwh = daily_kwh * 30
    yearly_kwh = daily_kwh * 365

    return {
        'daily': round(daily_kwh, 2),
        'monthly': round(monthly_kwh, 2),
        'yearly': round(yearly_kwh, 2),
        'savings': round(yearly_kwh * 5.5 / 1000, 2),  # Пример: 5.5 руб за кВтч
        'co2_reduction': round(yearly_kwh * 0.4 / 1000, 2),  # тонн CO2 в год
    }


def create_solar_map(selected_city=None):
    """Создаем карту солнечной энергии"""

    if selected_city and selected_city in SOLAR_INSOLATION:
        center_lat, center_lon = SOLAR_INSOLATION[selected_city]['coords']
        zoom = 10
    else:
        center_lat, center_lon = 61.5240, 105.3188
        zoom = 3

    # Создаем карту
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        min_zoom=3,
        max_zoom=15,
        control_scale=True,
        zoom_control=True,
        scrollWheelZoom=True,
        tiles='CartoDB positron'
    )

    # Добавляем слой тепловой карты солнечной инсоляции
    heat_data = []
    for city_name, data in SOLAR_INSOLATION.items():
        heat_data.append([data['coords'][0], data['coords'][1], data['insolation']])

    HeatMap(
        heat_data,
        name="Солнечная инсоляция",
        min_opacity=0.3,
        max_zoom=12,
        radius=30,
        blur=20,
        max_val=4.0,
        gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'yellow', 0.8: 'orange', 1: 'red'}
    ).add_to(m)

    # Добавляем зоны эффективности
    for zone in SOLAR_ZONES:
        folium.GeoJson(
            get_zone_geojson(zone),
            name=zone['name'],
            style_function=lambda x, zone_color=zone['color']: {
                'fillColor': zone_color,
                'color': zone_color,
                'weight': 1,
                'fillOpacity': 0.2
            }
        ).add_to(m)

    # Добавляем маркеры городов с солнечной информацией
    for city_name, city_data in SOLAR_INSOLATION.items():
        is_selected = city_name == selected_city
        solar_potential = calculate_solar_potential(city_data)

        # Определяем цвет маркера в зависимости от инсоляции
        marker_color = 'gray'
        if city_data['insolation'] >= 3.0:
            marker_color = 'red'  # Высокая
        elif city_data['insolation'] >= 2.5:
            marker_color = 'orange'  # Средняя
        elif city_data['insolation'] >= 2.0:
            marker_color = 'blue'  # Умеренная
        else:
            marker_color = 'gray'  # Низкая

        popup_html = f'''
        <div style="min-width: 300px; font-family: Arial, sans-serif;">
            <div style="background: linear-gradient(135deg, {city_data['color']}, #FFFFFF);
                        padding: 15px; border-radius: 10px 10px 0 0; color: white; text-align: center;">
                <h3 style="margin: 0; font-size: 20px;">☀️ {city_name}</h3>
                <p style="margin: 5px 0; font-size: 16px;">Солнечный потенциал</p>
            </div>
            <div style="padding: 15px; background: white;">
                <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <p style="margin: 5px 0; font-size: 18px; color: #ff8c00;">
                        <strong>Инсоляция:</strong> {city_data['insolation']} кВтч/м²/день
                    </p>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                    <div style="background: #e3f2fd; padding: 8px; border-radius: 5px; text-align: center;">
                        <div style="font-size: 12px; color: #666;">Дневная выработка</div>
                        <div style="font-size: 18px; font-weight: bold; color: #2196F3;">
                            {solar_potential['daily']} кВтч
                        </div>
                    </div>
                    <div style="background: #e8f5e8; padding: 8px; border-radius: 5px; text-align: center;">
                        <div style="font-size: 12px; color: #666;">Годовая выработка</div>
                        <div style="font-size: 18px; font-weight: bold; color: #4CAF50;">
                            {solar_potential['yearly']} кВтч
                        </div>
                    </div>
                </div>

                <div style="background: #fff3cd; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <p style="margin: 5px 0; color: #856404;">
                        <strong>💰 Годовая экономия:</strong> {solar_potential['savings']} тыс. руб
                    </p>
                    <p style="margin: 5px 0; color: #0c5460;">
                        <strong>🌿 Сокращение CO2:</strong> {solar_potential['co2_reduction']} тонн
                    </p>
                </div>

                <div style="text-align: center; margin-top: 10px;">
                    <button onclick="window.location.href='/?city={city_name}'" 
                            style="background: {city_data['color']}; color: white; 
                                   border: none; padding: 10px 20px; 
                                   border-radius: 5px; cursor: pointer; font-weight: bold;">
                        📍 Показать на карте
                    </button>
                </div>
            </div>
        </div>
        '''

        if is_selected:
            # Особый маркер для выбранного города
            folium.Marker(
                location=city_data['coords'],
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=f"☀️ {city_name} - {city_data['insolation']} кВтч/м²/день",
                icon=folium.Icon(
                    color='red',
                    icon='sun',
                    prefix='fa',
                    icon_color='white'
                )
            ).add_to(m)

            # Солнечные лучи вокруг города
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                lat_offset = math.sin(rad) * 0.5
                lon_offset = math.cos(rad) * 0.5

                folium.PolyLine(
                    locations=[
                        city_data['coords'],
                        [city_data['coords'][0] + lat_offset, city_data['coords'][1] + lon_offset]
                    ],
                    color='#FFD700',
                    weight=2,
                    opacity=0.6,
                    dash_array='10, 5'
                ).add_to(m)
        else:
            # Обычные маркеры
            folium.CircleMarker(
                location=city_data['coords'],
                radius=10 + city_data['insolation'] * 2,  # Размер зависит от инсоляции
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=f"{city_name}: {city_data['insolation']} кВтч/м²/день",
                color=marker_color,
                fill=True,
                fill_color=marker_color,
                fill_opacity=0.7,
                weight=2
            ).add_to(m)

    # Добавляем легенду
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 300px;
                background: white; padding: 15px; 
                border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.2);
                z-index: 1000; font-family: Arial;">
        <h4 style="margin-top: 0; color: #ff8c00;">☀️ Легенда солнечной карты</h4>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 15px; height: 15px; background: red; 
                       border-radius: 50%; margin-right: 10px;"></div>
            <span>Высокая эффективность (>3.0 кВтч)</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 15px; height: 15px; background: orange; 
                       border-radius: 50%; margin-right: 10px;"></div>
            <span>Средняя эффективность (2.5-3.0 кВтч)</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 15px; height: 15px; background: blue; 
                       border-radius: 50%; margin-right: 10px;"></div>
            <span>Умеренная эффективность (2.0-2.5 кВтч)</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 15px; height: 15px; background: gray; 
                       border-radius: 50%; margin-right: 10px;"></div>
            <span>Низкая эффективность (<2.0 кВтч)</span>
        </div>
        <hr style="margin: 10px 0;">
        <p style="font-size: 12px; color: #666; margin: 0;">
            💡 <strong>Данные:</strong> Среднегодовая солнечная инсоляция
        </p>
        <p style="font-size: 12px; color: #666; margin: 5px 0 0 0;">
            🏠 <strong>Расчет:</strong> Для 10м² панелей с КПД 18%
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Добавляем мини-карту
    MiniMap(
        tile_layer='CartoDB positron',
        position='bottomright',
        width=150,
        height=150
    ).add_to(m)

    # Добавляем полноэкранный режим
    Fullscreen(
        position='topleft',
        title='Полноэкранный режим'
    ).add_to(m)

    # Добавляем линейку
    MeasureControl(
        position='topleft',
        primary_length_unit='kilometers'
    ).add_to(m)

    # Добавляем управление слоями
    folium.LayerControl(collapsed=False, position='topright').add_to(m)

    return m


def get_zone_geojson(zone):
    """Возвращает GeoJSON для зоны"""
    # Упрощенный GeoJSON для демонстрации
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": zone['name']},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [40, 50], [40, 60], [50, 60], [50, 50], [40, 50]
                    ]]
                }
            }
        ]
    }


@app.route('/')
def index():
    city = request.args.get('city', '').strip()

    # Создаем карту
    m = create_solar_map(city if city in SOLAR_INSOLATION else None)
    map_html = m._repr_html_()

    # Получаем данные для выбранного города
    solar_data = None
    if city in SOLAR_INSOLATION:
        solar_data = calculate_solar_potential(SOLAR_INSOLATION[city])

    # Генерируем HTML
    html = f'''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>☀️ Солнечная карта России - Потенциал солнечной энергии</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Arial', sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                min-height: 100vh;
                color: #333;
            }}

            .container {{
                display: flex;
                flex-direction: column;
                height: 100vh;
                background: white;
                box-shadow: 0 0 30px rgba(0, 0, 0, 0.3);
            }}

            /* ШАПКА */
            .header {{
                background: linear-gradient(90deg, #1a237e, #283593);
                padding: 15px 25px;
                color: white;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            }}

            .header-top {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 15px;
            }}

            .logo {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}

            .logo-icon {{
                font-size: 40px;
                animation: pulse 2s infinite;
                color: #FFD700;
            }}

            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.1); }}
                100% {{ transform: scale(1); }}
            }}

            .logo-text h1 {{
                font-size: 24px;
                font-weight: bold;
                color: white;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }}

            .logo-text p {{
                font-size: 14px;
                opacity: 0.9;
                color: #bbdefb;
            }}

            /* ПОИСК */
            .search-container {{
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                border: 2px solid rgba(255, 255, 255, 0.2);
            }}

            .search-title {{
                font-size: 18px;
                margin-bottom: 15px;
                color: white;
                text-align: center;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }}

            .search-box {{
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
            }}

            #city-input {{
                flex: 1;
                padding: 18px 25px;
                border: none;
                border-radius: 50px;
                font-size: 18px;
                background: white;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                transition: all 0.3s;
            }}

            #city-input:focus {{
                outline: none;
                box-shadow: 0 6px 25px rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }}

            #search-btn {{
                padding: 18px 40px;
                background: linear-gradient(45deg, #FFD700, #FF8C00);
                color: #333;
                border: none;
                border-radius: 50px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 12px;
                box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
                transition: all 0.3s;
                min-width: 200px;
                justify-content: center;
            }}

            #search-btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(255, 140, 0, 0.6);
            }}

            .quick-search {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                justify-content: center;
            }}

            .quick-btn {{
                padding: 10px 20px;
                background: rgba(255, 215, 0, 0.2);
                color: white;
                border: 1px solid rgba(255, 215, 0, 0.3);
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s;
                font-size: 14px;
            }}

            .quick-btn:hover {{
                background: rgba(255, 215, 0, 0.4);
                transform: translateY(-2px);
            }}

            /* ОСНОВНОЙ КОНТЕНТ */
            .main-content {{
                flex: 1;
                display: flex;
                position: relative;
            }}

            .map-container {{
                flex: 1;
                position: relative;
                background: #e3f2fd;
            }}

            #map {{
                width: 100%;
                height: 100%;
            }}

            /* ПАНЕЛЬ СОЛНЕЧНЫХ ДАННЫХ */
            .solar-panel {{
                position: absolute;
                top: 20px;
                left: 20px;
                width: 350px;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                z-index: 1000;
            }}

            .city-header {{
                text-align: center;
                margin-bottom: 20px;
            }}

            .city-name {{
                font-size: 26px;
                font-weight: bold;
                color: #1a237e;
                margin-bottom: 5px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }}

            .solar-stats {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 20px;
            }}

            .stat-card {{
                background: white;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                text-align: center;
                transition: transform 0.3s;
            }}

            .stat-card:hover {{
                transform: translateY(-5px);
            }}

            .stat-value {{
                font-size: 24px;
                font-weight: bold;
                margin: 10px 0;
            }}

            .stat-label {{
                font-size: 12px;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            .insolation {{
                font-size: 36px;
                color: #FF8C00;
                font-weight: bold;
            }}

            .energy-color {{
                color: #2196F3;
            }}

            .money-color {{
                color: #4CAF50;
            }}

            .co2-color {{
                color: #0c5460;
            }}

            .calculator {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            }}

            .calculator h4 {{
                margin-bottom: 15px;
                color: #1a237e;
            }}

            .input-group {{
                margin-bottom: 10px;
            }}

            .input-group label {{
                display: block;
                margin-bottom: 5px;
                color: #666;
                font-size: 14px;
            }}

            .input-group input {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
            }}

            .calculate-btn {{
                width: 100%;
                padding: 12px;
                background: linear-gradient(45deg, #FFD700, #FF8C00);
                color: #333;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                margin-top: 10px;
            }}

            .controls {{
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}

            .control-btn {{
                padding: 12px;
                background: linear-gradient(135deg, #1a237e, #3949ab);
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                font-weight: bold;
                transition: all 0.3s;
            }}

            .control-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(26, 35, 126, 0.4);
            }}

            /* ФУТЕР */
            .footer {{
                background: #1a237e;
                color: white;
                padding: 15px;
                text-align: center;
                font-size: 14px;
            }}

            @media (max-width: 768px) {{
                .solar-panel {{
                    display: none;
                }}

                .search-box {{
                    flex-direction: column;
                }}

                #search-btn {{
                    width: 100%;
                }}
            }}
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body>
        <div class="container">
            <!-- ШАПКА -->
            <div class="header">
                <div class="header-top">
                    <div class="logo">
                        <div class="logo-icon">
                            <i class="fas fa-solar-panel"></i>
                        </div>
                        <div class="logo-text">
                            <h1>☀️ Солнечная карта России</h1>
                            <p>Оцените потенциал солнечной энергии в вашем регионе</p>
                        </div>
                    </div>

                    <div style="color: #bbdefb; font-size: 14px;">
                        <i class="fas fa-sun"></i> {len(SOLAR_INSOLATION)} солнечных регионов
                    </div>
                </div>

                <div class="search-container">
                    <div class="search-title">
                        <i class="fas fa-search-location"></i>
                        НАЙДИТЕ ВАШ ГОРОД ДЛЯ РАСЧЕТА
                    </div>

                    <div class="search-box">
                        <input type="text" 
                               id="city-input" 
                               placeholder="Введите ваш город для расчета солнечного потенциала..."
                               value="{city}"
                               autocomplete="off">

                        <button id="search-btn" onclick="searchCity()">
                            <i class="fas fa-sun"></i>
                            РАССЧИТАТЬ ПОТЕНЦИАЛ
                        </button>
                    </div>

                    <div class="quick-search">
                        {' '.join([f'<div class="quick-btn" onclick="searchCityByName(\'{city_name}\')"><i class="fas fa-city"></i> {city_name}</div>' for city_name in list(SOLAR_INSOLATION.keys())[:5]])}
                    </div>
                </div>
            </div>

            <!-- ОСНОВНОЙ КОНТЕНТ -->
            <div class="main-content">
                <div class="map-container">
                    <div id="map">{map_html}</div>

                    <!-- ПАНЕЛЬ СОЛНЕЧНЫХ ДАННЫХ -->
                    <div class="solar-panel">
                        <div class="city-header">
                            <div class="city-name">
                                {city if city in SOLAR_INSOLATION else 'Выберите город'}
                            </div>
                        </div>

                        {f'''
                        <div style="background: #fff3e0; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                            <p style="font-size: 18px; color: #e65100; text-align: center; margin: 0;">
                                ☀️ Солнечная инсоляция: 
                                <span style="font-weight: bold;">{SOLAR_INSOLATION[city]['insolation']} кВтч/м²/день</span>
                            </p>
                        </div>

                        <div class="solar-stats">
                            <div class="stat-card">
                                <div class="stat-label">ДНЕВНАЯ ВЫРАБОТКА</div>
                                <div class="stat-value energy-color">{solar_data['daily']} кВтч</div>
                                <div style="font-size: 12px; color: #666;">Для 10м² панелей</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">ГОДОВАЯ ВЫРАБОТКА</div>
                                <div class="stat-value energy-color">{solar_data['yearly']} кВтч</div>
                                <div style="font-size: 12px; color: #666;">Энергии в год</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">ГОДОВАЯ ЭКОНОМИЯ</div>
                                <div class="stat-value money-color">{solar_data['savings']} тыс.руб</div>
                                <div style="font-size: 12px; color: #666;">Стоимость энергии</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">СОКРАЩЕНИЕ CO2</div>
                                <div class="stat-value co2-color">{solar_data['co2_reduction']} тонн</div>
                                <div style="font-size: 12px; color: #666;">Экология в год</div>
                            </div>
                        </div>
                        ''' if city in SOLAR_INSOLATION else '''
                        <div style="text-align: center; padding: 30px; color: #666;">
                            <i class="fas fa-sun" style="font-size: 50px; color: #ffd700; margin-bottom: 20px;"></i>
                            <p style="font-size: 16px; margin-bottom: 10px;">Выберите город для просмотра</p>
                            <p style="font-size: 14px;">солнечного потенциала и расчетов</p>
                        </div>
                        '''}

                        <div class="calculator">
                            <h4><i class="fas fa-calculator"></i> Калькулятор солнечных панелей</h4>
                            <div class="input-group">
                                <label for="panel-area">Площадь панелей (м²)</label>
                                <input type="number" id="panel-area" value="10" min="1" max="100">
                            </div>
                            <div class="input-group">
                                <label for="efficiency">КПД панелей (%)</label>
                                <input type="number" id="efficiency" value="18" min="1" max="30" step="0.1">
                            </div>
                            <button class="calculate-btn" onclick="calculateSolar()">
                                <i class="fas fa-bolt"></i> ПЕРЕСЧИТАТЬ
                            </button>
                        </div>

                        <div class="controls">
                            <button class="control-btn" onclick="zoomIn()">
                                <i class="fas fa-search-plus"></i> Приблизить карту
                            </button>
                            <button class="control-btn" onclick="resetMap()">
                                <i class="fas fa-globe-europe"></i> Вся Россия
                            </button>
                            <button class="control-btn" onclick="showBestRegions()">
                                <i class="fas fa-star"></i> Лучшие регионы
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ФУТЕР -->
            <div class="footer">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>© 2025 Солнечная карта России - Потенциал возобновляемой энергии</div>
                    <div>🇷🇺 Энергия солнца для будущего России</div>
                    <div><i class="fas fa-leaf" style="color: #4CAF50;"></i> Чистая энергия для чистого будущего</div>
                </div>
            </div>
        </div>

        <script>
            // Основные функции
            function searchCity() {{
                const input = document.getElementById('city-input');
                const city = input.value.trim();

                if (city) {{
                    window.location.href = '/?city=' + encodeURIComponent(city);
                }}
            }}

            function searchCityByName(cityName) {{
                document.getElementById('city-input').value = cityName;
                searchCity();
            }}

            function zoomIn() {{
                const iframe = document.querySelector('#map iframe');
                if (iframe && iframe.contentWindow && iframe.contentWindow.map) {{
                    iframe.contentWindow.map.zoomIn();
                }}
            }}

            function resetMap() {{
                window.location.href = '/';
            }}

            function showBestRegions() {{
                // Показать регионы с лучшей инсоляцией
                alert('Лучшие регионы для солнечных панелей: Сочи, Махачкала, Астрахань, Краснодар');
            }}

            // Калькулятор солнечной энергии
            function calculateSolar() {{
                const panelArea = parseFloat(document.getElementById('panel-area').value);
                const efficiency = parseFloat(document.getElementById('efficiency').value) / 100;

                const city = '{city}';
                if (city && city in {list(SOLAR_INSOLATION.keys())}) {{
                    const insolation = {SOLAR_INSOLATION[city]['insolation'] if city in SOLAR_INSOLATION else 2.5};

                    // Расчеты
                    const daily = insolation * panelArea * efficiency;
                    const yearly = daily * 365;
                    const savings = (yearly * 5.5 / 1000).toFixed(2);
                    const co2 = (yearly * 0.4 / 1000).toFixed(2);

                    // Обновление данных
                    document.querySelectorAll('.stat-card')[0].querySelector('.stat-value').textContent = 
                        daily.toFixed(2) + ' кВтч';
                    document.querySelectorAll('.stat-card')[1].querySelector('.stat-value').textContent = 
                        yearly.toFixed(0) + ' кВтч';
                    document.querySelectorAll('.stat-card')[2].querySelector('.stat-value').textContent = 
                        savings + ' тыс.руб';
                    document.querySelectorAll('.stat-card')[3].querySelector('.stat-value').textContent = 
                        co2 + ' тонн';

                    alert('Расчет обновлен для новых параметров!');
                }} else {{
                    alert('Сначала выберите город для расчета');
                }}
            }}

            // Автоматический фокус на поле ввода
            window.addEventListener('load', function() {{
                if (!'{city}') {{
                    document.getElementById('city-input').focus();
                }}
            }});

            // Поиск по Enter
            document.getElementById('city-input').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    searchCity();
                }}
            }});
        </script>
    </body>
    </html>
    '''

    return html


@app.route('/api/solar-data/<city_name>')
def get_solar_data(city_name):
    """API для получения данных по солнечной энергии"""
    if city_name in SOLAR_INSOLATION:
        solar_potential = calculate_solar_potential(SOLAR_INSOLATION[city_name])
        return jsonify({
            'success': True,
            'city': city_name,
            'insolation': SOLAR_INSOLATION[city_name]['insolation'],
            'potential': solar_potential
        })
    return jsonify({'success': False, 'error': 'Город не найден'}), 404


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)