from flask import Flask, request, jsonify
import folium
from folium.plugins import MarkerCluster, MeasureControl, MiniMap, Fullscreen
import random

app = Flask(__name__)

# Российские города с координатами
CITIES = {
    'Москва': {'coords': [55.7558, 37.6176], 'color': '#FF0000', 'icon': 'star'},
    'Санкт-Петербург': {'coords': [59.9390, 30.3158], 'color': '#0000FF', 'icon': 'university'},
    'Новосибирск': {'coords': [55.0302, 82.9204], 'color': '#008000', 'icon': 'tree-conifer'},
    'Екатеринбург': {'coords': [56.8380, 60.5973], 'color': '#FFA500', 'icon': 'industry'},
    'Казань': {'coords': [55.7961, 49.1064], 'color': '#800080', 'icon': 'mosque'},
    'Нижний Новгород': {'coords': [56.3269, 44.0065], 'color': '#00FFFF', 'icon': 'home'},
    'Челябинск': {'coords': [55.1644, 61.4368], 'color': '#FF69B4', 'icon': 'industry'},
    'Самара': {'coords': [53.1959, 50.1002], 'color': '#8B4513', 'icon': 'plane'},
    'Омск': {'coords': [54.9893, 73.3682], 'color': '#2E8B57', 'icon': 'road'},
    'Ростов-на-Дону': {'coords': [47.2224, 39.7187], 'color': '#DC143C', 'icon': 'ship'},
    'Уфа': {'coords': [54.7351, 55.9587], 'color': '#FFD700', 'icon': 'oil'},
    'Красноярск': {'coords': [56.0153, 92.8932], 'color': '#4B0082', 'icon': 'mountain'},
    'Пермь': {'coords': [58.0105, 56.2502], 'color': '#00CED1', 'icon': 'factory'},
    'Воронеж': {'coords': [51.6615, 39.2003], 'color': '#FF4500', 'icon': 'education'},
    'Волгоград': {'coords': [48.7080, 44.5133], 'color': '#2F4F4F', 'icon': 'tower'},
    'Краснодар': {'coords': [45.0355, 38.9753], 'color': '#32CD32', 'icon': 'sun'},
    'Саратов': {'coords': [51.5336, 46.0342], 'color': '#8A2BE2', 'icon': 'road'},
    'Тюмень': {'coords': [57.1530, 65.5343], 'color': '#FF6347', 'icon': 'oil'},
    'Тольятти': {'coords': [53.5088, 49.4192], 'color': '#4682B4', 'icon': 'car'},
    'Ижевск': {'coords': [56.8526, 53.2115], 'color': '#D2691E', 'icon': 'industry'},
    'Барнаул': {'coords': [53.3548, 83.7699], 'color': '#5F9EA0', 'icon': 'wheat'},
    'Ульяновск': {'coords': [54.3142, 48.4031], 'color': '#6495ED', 'icon': 'plane'},
    'Иркутск': {'coords': [52.2896, 104.2806], 'color': '#DA70D6', 'icon': 'lake'},
    'Хабаровск': {'coords': [48.4802, 135.0719], 'color': '#FF8C00', 'icon': 'east'},
    'Ярославль': {'coords': [57.6261, 39.8845], 'color': '#7CFC00', 'icon': 'historic'},
    'Владивосток': {'coords': [43.1155, 131.8855], 'color': '#1E90FF', 'icon': 'anchor'},
    'Махачкала': {'coords': [42.9831, 47.5047], 'color': '#FF1493', 'icon': 'sun'},
    'Томск': {'coords': [56.4846, 84.9482], 'color': '#00BFFF', 'icon': 'education'},
    'Кемерово': {'coords': [55.3547, 86.0873], 'color': '#228B22', 'icon': 'industry'},
    'Новокузнецк': {'coords': [53.7596, 87.1216], 'color': '#FFDAB9', 'icon': 'industry'},
    'Рязань': {'coords': [54.6294, 39.7417], 'color': '#8FBC8F', 'icon': 'historic'},
    'Астрахань': {'coords': [46.3497, 48.0408], 'color': '#B22222', 'icon': 'ship'},
    'Пенза': {'coords': [53.1959, 45.0183], 'color': '#ADFF2F', 'icon': 'home'},
    'Набережные Челны': {'coords': [55.7436, 52.3959], 'color': '#FF00FF', 'icon': 'industry'},
    'Липецк': {'coords': [52.6088, 39.5992], 'color': '#DAA520', 'icon': 'industry'},
    'Тула': {'coords': [54.1931, 37.6173], 'color': '#CD5C5C', 'icon': 'industry'},
    'Киров': {'coords': [58.6036, 49.6680], 'color': '#9ACD32', 'icon': 'home'},
    'Чебоксары': {'coords': [56.1463, 47.2511], 'color': '#FFB6C1', 'icon': 'home'},
    'Калининград': {'coords': [54.7104, 20.4522], 'color': '#87CEEB', 'icon': 'ship'},
    'Брянск': {'coords': [53.2436, 34.3634], 'color': '#6B8E23', 'icon': 'home'},
    'Курск': {'coords': [51.7304, 36.1926], 'color': '#F08080', 'icon': 'home'},
    'Иваново': {'coords': [57.0004, 40.9739], 'color': '#BA55D3', 'icon': 'industry'},
    'Магнитогорск': {'coords': [53.4072, 58.9790], 'color': '#B0C4DE', 'icon': 'industry'},
    'Тверь': {'coords': [56.8587, 35.9176], 'color': '#FFFAFA', 'icon': 'historic'},
    'Ставрополь': {'coords': [45.0445, 41.9691], 'color': '#F0E68C', 'icon': 'sun'},
    'Белгород': {'coords': [50.5956, 36.5873], 'color': '#ADD8E6', 'icon': 'home'},
    'Сочи': {'coords': [43.5855, 39.7231], 'color': '#98FB98', 'icon': 'umbrella'},
}


def create_russian_map(selected_city=None):
    """Создаем карту с российскими источниками"""

    if selected_city and selected_city in CITIES:
        center_lat, center_lon = CITIES[selected_city]['coords']
        zoom = 10
    else:
        center_lat, center_lon = 61.5240, 105.3188
        zoom = 3

    # Создаем базовую карту с российскими тайлами
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        min_zoom=3,
        max_zoom=15,
        max_bounds=True,
        min_lat=40,
        max_lat=82,
        min_lon=20,
        max_lon=190,
        control_scale=True,
        zoom_control=True,
        scrollWheelZoom=True
    )

    # Добавляем российские тайл-слои
    # 1. Основной слой - российский стиль
    folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        name='Карта России',
        attr='© OpenStreetMap contributors',
        overlay=False,
        control=True
    ).add_to(m)

    # 2. Топографическая карта (нейтральный источник)
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        name='Топографическая',
        attr='OpenTopoMap',
        overlay=False,
        control=True
    ).add_to(m)

    # 3. Чистая карта без подписей
    folium.TileLayer(
        tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
        name='Контурная',
        attr='Stadia Maps',
        overlay=False,
        control=True
    ).add_to(m)

    # Контур России с градиентом
    russia_bounds = [
        [41.0, 19.0], [41.0, 190.0], [82.0, 190.0],
        [82.0, 19.0], [41.0, 19.0]
    ]

    # Красивый градиент для России
    folium.Polygon(
        locations=russia_bounds,
        color='#1E3A8A',
        weight=3,
        fill=True,
        fill_color='#3B82F6',
        fill_opacity=0.15,
        tooltip='🇷🇺 Российская Федерация'
    ).add_to(m)

    # Добавляем кластер маркеров
    marker_cluster = MarkerCluster(
        name="Города России",
        overlay=True,
        control=False
    ).add_to(m)

    # Добавляем все города
    for city_name, city_data in CITIES.items():
        is_selected = city_name == selected_city

        popup_html = f'''
        <div style="min-width: 250px; font-family: Arial, sans-serif;">
            <div style="background: linear-gradient(135deg, {city_data['color']}, #FFFFFF);
                        padding: 15px; border-radius: 10px 10px 0 0; color: white; text-align: center;">
                <h3 style="margin: 0; font-size: 18px;">{city_name}</h3>
            </div>
            <div style="padding: 15px; background: white;">
                <p><strong>📍 Координаты:</strong><br>
                Широта: {city_data['coords'][0]:.4f}<br>
                Долгота: {city_data['coords'][1]:.4f}</p>
                <p><strong>🎯 Статус:</strong> {'Выбранный город' if is_selected else 'Крупный город России'}</p>
                <div style="margin-top: 10px; text-align: center;">
                    <button onclick="window.location.href='/?city={city_name}'" 
                            style="background: {city_data['color']}; color: white; 
                                   border: none; padding: 8px 15px; 
                                   border-radius: 5px; cursor: pointer;">
                        Показать на карте
                    </button>
                </div>
            </div>
        </div>
        '''

        if is_selected:
            # Особый маркер для выбранного города
            folium.Marker(
                location=city_data['coords'],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"★ {city_name} ★ (выбран)",
                icon=folium.Icon(
                    color='red',
                    icon='star',
                    prefix='fa',
                    icon_color='white',
                    icon_size=(30, 30)
                )
            ).add_to(m)

            # Анимированный круг вокруг города
            folium.Circle(
                location=city_data['coords'],
                radius=15000,
                color=city_data['color'],
                fill=True,
                fill_color=city_data['color'],
                fill_opacity=0.2,
                weight=3
            ).add_to(m)

            # Линии от города к границам
            for angle in range(0, 360, 45):
                import math
                lat_offset = math.sin(math.radians(angle)) * 5
                lon_offset = math.cos(math.radians(angle)) * 5

                folium.PolyLine(
                    locations=[
                        city_data['coords'],
                        [city_data['coords'][0] + lat_offset, city_data['coords'][1] + lon_offset]
                    ],
                    color=city_data['color'],
                    weight=1,
                    opacity=0.5,
                    dash_array='5, 10'
                ).add_to(m)
        else:
            # Обычные маркеры
            folium.CircleMarker(
                location=city_data['coords'],
                radius=8,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=city_name,
                color=city_data['color'],
                fill=True,
                fill_color=city_data['color'],
                fill_opacity=0.8,
                weight=2
            ).add_to(marker_cluster)

    # Добавляем мини-карту с исправленной атрибуцией
    minimap_tile_layer = folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='© OpenStreetMap contributors'
    )

    MiniMap(
        tile_layer=minimap_tile_layer,
        position='bottomright',
        width=150,
        height=150
    ).add_to(m)

    # Добавляем полноэкранный режим
    Fullscreen(
        position='topleft',
        title='Полноэкранный режим',
        title_cancel='Выйти из полноэкранного режима'
    ).add_to(m)

    # Добавляем линейку
    MeasureControl(
        position='topleft',
        primary_length_unit='kilometers',
        secondary_length_unit='meters',
        primary_area_unit='sqkilometers',
        secondary_area_unit='hectares'
    ).add_to(m)

    # Добавляем кнопку для печати (используем локальную иконку или убираем)
    # from folium.plugins import FloatImage
    # FloatImage(
    #     'https://img.icons8.com/color/48/000000/print.png',
    #     bottom=10,
    #     left=10,
    #     width='48px',
    #     height='48px'
    # ).add_to(m)

    # Добавляем управление слоями
    folium.LayerControl(collapsed=False, position='topright').add_to(m)

    return m


@app.route('/')
def index():
    city = request.args.get('city', '').strip()

    # Создаем карту
    m = create_russian_map(city if city in CITIES else None)
    map_html = m._repr_html_()

    # Генерируем HTML
    html = f'''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🇷🇺 Карта России - Найди свой город</title>
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
            }}

            .container {{
                display: flex;
                flex-direction: column;
                height: 100vh;
                background: white;
                box-shadow: 0 0 30px rgba(0, 0, 0, 0.3);
            }}

            /* ШАПКА С ПОИСКОМ */
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

            /* БОЛЬШАЯ КНОПКА ПОИСКА */
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
                background: linear-gradient(45deg, #ff5252, #ff4081);
                color: white;
                border: none;
                border-radius: 50px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 12px;
                box-shadow: 0 6px 20px rgba(255, 82, 82, 0.4);
                transition: all 0.3s;
                min-width: 200px;
                justify-content: center;
            }}

            #search-btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(255, 82, 82, 0.6);
                background: linear-gradient(45deg, #ff4081, #ff5252);
            }}

            #search-btn:active {{
                transform: translateY(-1px);
            }}

            .quick-search {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                justify-content: center;
            }}

            .quick-btn {{
                padding: 10px 20px;
                background: rgba(255, 255, 255, 0.15);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s;
                font-size: 14px;
            }}

            .quick-btn:hover {{
                background: rgba(255, 255, 255, 0.3);
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

            /* ПАНЕЛЬ ИНФОРМАЦИИ */
            .info-panel {{
                position: absolute;
                top: 20px;
                left: 20px;
                width: 300px;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                z-index: 1000;
            }}

            .city-info {{
                text-align: center;
                margin-bottom: 20px;
            }}

            .city-name {{
                font-size: 24px;
                font-weight: bold;
                color: #1a237e;
                margin-bottom: 10px;
            }}

            .city-coords {{
                font-size: 14px;
                color: #666;
                margin-bottom: 15px;
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

            .stats {{
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
            }}

            .stat-item {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
                font-size: 14px;
            }}

            .stat-value {{
                font-weight: bold;
                color: #1a237e;
            }}

            /* ПАНЕЛЬ С ГОРОДАМИ */
            .cities-panel {{
                position: absolute;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                width: 90%;
                max-width: 800px;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 15px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
                z-index: 1000;
                max-height: 150px;
                overflow-y: auto;
            }}

            .cities-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
                gap: 8px;
            }}

            .city-item {{
                padding: 8px 12px;
                background: #e3f2fd;
                border-radius: 8px;
                cursor: pointer;
                text-align: center;
                font-size: 13px;
                transition: all 0.3s;
                border: 1px solid transparent;
            }}

            .city-item:hover {{
                background: #bbdefb;
                transform: translateY(-2px);
                border-color: #1a237e;
            }}

            /* ФУТЕР */
            .footer {{
                background: #1a237e;
                color: white;
                padding: 15px;
                text-align: center;
                font-size: 14px;
            }}

            /* АДАПТИВНОСТЬ */
            @media (max-width: 1024px) {{
                .info-panel {{
                    width: 250px;
                }}

                #search-btn {{
                    min-width: 150px;
                    padding: 15px 30px;
                }}
            }}

            @media (max-width: 768px) {{
                .header-top {{
                    flex-direction: column;
                    text-align: center;
                    gap: 15px;
                }}

                .search-box {{
                    flex-direction: column;
                }}

                #search-btn {{
                    width: 100%;
                }}

                .info-panel {{
                    display: none;
                }}

                .cities-panel {{
                    width: 95%;
                    max-height: 120px;
                }}

                .cities-grid {{
                    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
                }}
            }}

            /* СКРОЛЛБАР */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}

            ::-webkit-scrollbar-track {{
                background: #f1f1f1;
                border-radius: 4px;
            }}

            ::-webkit-scrollbar-thumb {{
                background: linear-gradient(135deg, #1a237e, #3949ab);
                border-radius: 4px;
            }}

            /* АНИМАЦИИ */
            @keyframes slideIn {{
                from {{ opacity: 0; transform: translateY(30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            .slide-in {{
                animation: slideIn 0.5s ease-out;
            }}

            /* ВСПЛЫВАЮЩИЕ УВЕДОМЛЕНИЯ */
            .notification {{
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, #4CAF50, #2E7D32);
                color: white;
                padding: 15px 25px;
                border-radius: 10px;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
                z-index: 2000;
                display: none;
                animation: slideIn 0.3s ease-out;
            }}

            .notification.error {{
                background: linear-gradient(135deg, #f44336, #c62828);
            }}
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body>
        <div class="container slide-in">
            <!-- ШАПКА -->
            <div class="header">
                <div class="header-top">
                    <div class="logo">
                        <div class="logo-icon">
                            <i class="fas fa-map-marked-alt"></i>
                        </div>
                        <div class="logo-text">
                            <h1>🇷🇺 Карта России</h1>
                            <p>Найдите свой город на карте нашей страны</p>
                        </div>
                    </div>

                    <div style="color: #bbdefb; font-size: 14px;">
                        <i class="fas fa-users"></i> {len(CITIES)} городов доступно
                    </div>
                </div>

                <div class="search-container">
                    <div class="search-title">
                        <i class="fas fa-search-location"></i>
                        ПОИСК ГОРОДА В РОССИИ
                    </div>

                    <div class="search-box">
                        <input type="text" 
                               id="city-input" 
                               placeholder="Введите название вашего города..."
                               value="{city}"
                               autocomplete="off"
                               list="cities-list">

                        <button id="search-btn" onclick="searchCity()">
                            <i class="fas fa-search"></i>
                            НАЙТИ ГОРОД
                        </button>
                    </div>

                    <div class="quick-search">
                        <div class="quick-btn" onclick="searchCityByName('Москва')">
                            <i class="fas fa-star"></i> Москва
                        </div>
                        <div class="quick-btn" onclick="searchCityByName('Санкт-Петербург')">
                            <i class="fas fa-university"></i> Санкт-Петербург
                        </div>
                        <div class="quick-btn" onclick="searchCityByName('Новосибирск')">
                            <i class="fas fa-tree"></i> Новосибирск
                        </div>
                        <div class="quick-btn" onclick="searchCityByName('Екатеринбург')">
                            <i class="fas fa-industry"></i> Екатеринбург
                        </div>
                        <div class="quick-btn" onclick="searchCityByName('Казань')">
                            <i class="fas fa-mosque"></i> Казань
                        </div>
                    </div>
                </div>
            </div>

            <!-- ОСНОВНОЙ КОНТЕНТ -->
            <div class="main-content">
                <div class="map-container">
                    <div id="map">{map_html}</div>

                    <!-- ПАНЕЛЬ ИНФОРМАЦИИ -->
                    <div class="info-panel">
                        <div class="city-info">
                            <div class="city-name" id="current-city-name">
                                {city if city in CITIES else 'Вся Россия'}
                            </div>
                            <div class="city-coords" id="current-city-coords">
                                {f"Широта: {CITIES[city]['coords'][0]:.4f}, Долгота: {CITIES[city]['coords'][1]:.4f}" if city in CITIES else 'Выберите город для просмотра координат'}
                            </div>
                        </div>

                        <div class="controls">
                            <button class="control-btn" onclick="zoomIn()">
                                <i class="fas fa-search-plus"></i> Приблизить
                            </button>
                            <button class="control-btn" onclick="zoomOut()">
                                <i class="fas fa-search-minus"></i> Отдалить
                            </button>
                            <button class="control-btn" onclick="resetMap()">
                                <i class="fas fa-globe-europe"></i> Вся Россия
                            </button>
                            <button class="control-btn" onclick="showAllCities()">
                                <i class="fas fa-city"></i> Все города
                            </button>
                        </div>

                        <div class="stats">
                            <div class="stat-item">
                                <span>Городов на карте:</span>
                                <span class="stat-value">{len(CITIES)}</span>
                            </div>
                            <div class="stat-item">
                                <span>Выбран город:</span>
                                <span class="stat-value">{'Да' if city in CITIES else 'Нет'}</span>
                            </div>
                        </div>
                    </div>

                    <!-- ПАНЕЛЬ С ГОРОДАМИ -->
                    <div class="cities-panel">
                        <div class="cities-grid" id="cities-grid">
                            {' '.join([f'<div class="city-item" onclick="searchCityByName(\'{name}\')">{name}</div>' for name in sorted(CITIES.keys())])}
                        </div>
                    </div>
                </div>
            </div>

            <!-- ФУТЕР -->
            <div class="footer">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>© 2025 Карта России - Все города Российской Федерации</div>
                    <div>🇷🇺 Сделано в России</div>
                    <div><i class="fas fa-heart" style="color: #ff5252;"></i> Для всех россиян</div>
                </div>
            </div>

            <!-- УВЕДОМЛЕНИЯ -->
            <div class="notification" id="notification"></div>

            <!-- DATALIST ДЛЯ АВТОДОПОЛНЕНИЯ -->
            <datalist id="cities-list">
                {' '.join([f'<option value="{name}">' for name in CITIES.keys()])}
            </datalist>
        </div>

        <script>
            // ОСНОВНЫЕ ФУНКЦИИ
            function searchCity() {{
                const input = document.getElementById('city-input');
                const city = input.value.trim();

                if (!city) {{
                    showNotification('Введите название города', 'error');
                    input.focus();
                    return;
                }}

                const cities = {list(CITIES.keys())};
                const foundCity = cities.find(c => 
                    c.toLowerCase() === city.toLowerCase() ||
                    c.toLowerCase().includes(city.toLowerCase())
                );

                if (foundCity) {{
                    window.location.href = '/?city=' + encodeURIComponent(foundCity);
                }} else {{
                    showNotification('Город не найден. Попробуйте другой.', 'error');
                    // Предлагаем похожие города
                    const similar = cities.filter(c => 
                        c.toLowerCase().includes(city.toLowerCase().substring(0, 3))
                    ).slice(0, 5);

                    if (similar.length > 0) {{
                        setTimeout(() => {{
                            showNotification('Возможно вы искали: ' + similar.join(', '));
                        }}, 1000);
                    }}
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
                    showNotification('Карта приближена');
                }}
            }}

            function zoomOut() {{
                const iframe = document.querySelector('#map iframe');
                if (iframe && iframe.contentWindow && iframe.contentWindow.map) {{
                    iframe.contentWindow.map.zoomOut();
                    showNotification('Карта отдалена');
                }}
            }}

            function resetMap() {{
                window.location.href = '/';
            }}

            function showAllCities() {{
                document.getElementById('cities-grid').scrollIntoView({{
                    behavior: 'smooth'
                }});
                showNotification('Показаны все города России');
            }}

            // УВЕДОМЛЕНИЯ
            function showNotification(message, type = 'success') {{
                const notification = document.getElementById('notification');
                notification.textContent = message;
                notification.className = 'notification';
                notification.classList.add(type);
                notification.style.display = 'block';

                setTimeout(() => {{
                    notification.style.display = 'none';
                }}, 3000);
            }}

            // АВТОДОПОЛНЕНИЕ
            const cityInput = document.getElementById('city-input');
            const cities = {list(CITIES.keys())};

            cityInput.addEventListener('input', function() {{
                const value = this.value.toLowerCase();
                if (value.length > 2) {{
                    // Можно добавить динамическое автодополнение
                }}
            }});

            // ПОИСК ПО ENTER
            cityInput.addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    searchCity();
                }}
            }});

            // ФОКУС НА ПОЛЕ ВВОДА ПРИ ЗАГРУЗКЕ
            window.addEventListener('load', function() {{
                if (!'{city}') {{
                    cityInput.focus();
                }}

                // Скрываем стандартные элементы управления картой
                setTimeout(() => {{
                    const controls = document.querySelector('.leaflet-control-container');
                    if (controls) {{
                        controls.style.opacity = '0.9';
                    }}

                    // Анимация для кнопки поиска
                    const searchBtn = document.getElementById('search-btn');
                    searchBtn.style.animation = 'pulse 2s infinite';
                }}, 1000);
            }});

            // ОБНОВЛЕНИЕ ИНФОРМАЦИИ О ГОРОДЕ
            function updateCityInfo() {{
                const city = '{city}';
                if (city && {str(city in CITIES).lower()}) {{
                    document.getElementById('current-city-name').textContent = city;
                    const coords = {CITIES[city]['coords'] if city in CITIES else [0, 0]};
                    document.getElementById('current-city-coords').textContent = 
                        `Широта: ${{coords[0].toFixed(4)}}, Долгота: ${{coords[1].toFixed(4)}}`;

                    // Подсветка выбранного города в списке
                    const cityItems = document.querySelectorAll('.city-item');
                    cityItems.forEach(item => {{
                        if (item.textContent === city) {{
                            item.style.background = '#1a237e';
                            item.style.color = 'white';
                            item.style.fontWeight = 'bold';
                        }}
                    }});
                }}
            }}

            updateCityInfo();
        </script>
    </body>
    </html>
    '''

    return html


@app.route('/api/cities')
def api_cities():
    """API для получения списка городов"""
    return jsonify({
        'success': True,
        'cities': list(CITIES.keys()),
        'count': len(CITIES)
    })


@app.route('/api/city/<city_name>')
def api_city(city_name):
    """API для получения информации о городе"""
    if city_name in CITIES:
        return jsonify({
            'success': True,
            'city': city_name,
            'coordinates': CITIES[city_name]['coords'],
            'color': CITIES[city_name]['color']
        })
    return jsonify({'success': False, 'error': 'Город не найден'}), 404


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
