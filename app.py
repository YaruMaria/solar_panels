from flask import Flask, request, render_template_string
import folium

app = Flask(__name__)

# Словарь с координатами городов России
CITIES = {
    'Москва': [55.7558, 37.6173],
    'Санкт-Петербург': [59.9343, 30.3351],
    'Новосибирск': [55.0084, 82.9357],
    'Екатеринбург': [56.8389, 60.6057],
    'Нижний Новгород': [56.2965, 43.9361],
    'Казань': [55.7963, 49.1082],
    'Челябинск': [55.1599, 61.4026],
    'Омск': [54.9885, 73.3242],
    'Самара': [53.2415, 50.2212],
    'Ростов-на-Дону': [47.2357, 39.7015],
    'Уфа': [54.7382, 55.9846],
    'Красноярск': [56.0153, 92.8932],
    'Воронеж': [51.6755, 39.2089],
    'Пермь': [58.0105, 56.2502],
    'Волгоград': [48.7071, 44.5169],
}


def create_simple_map(city_name=None):
    """Простая карта России"""

    if city_name and city_name in CITIES:
        lat, lon = CITIES[city_name]
        zoom = 10
    else:
        lat, lon = 61.5240, 105.3188
        zoom = 3

    m = folium.Map(
        location=[lat, lon],
        zoom_start=zoom,
        min_zoom=3,
        max_zoom=15,
        max_bounds=True,
        min_lat=40,
        max_lat=82,
        min_lon=20,
        max_lon=190,
        tiles='CartoDB positron',
        control_scale=False,
        zoom_control=False,
        attributionControl=False
    )

    # Контур России
    russia_bounds = [
        [41.0, 19.0], [41.0, 190.0], [82.0, 190.0],
        [82.0, 19.0], [41.0, 19.0]
    ]

    folium.Polygon(
        locations=russia_bounds,
        color='#4285F4',
        weight=2,
        fill=True,
        fill_color='#4285F4',
        fill_opacity=0.05
    ).add_to(m)

    # Добавляем города
    for city, coords in CITIES.items():
        if city == city_name:
            # Особый маркер для выбранного города
            folium.Marker(
                coords,
                popup=f'<b>{city}</b>',
                icon=folium.Icon(color='green', icon='star')
            ).add_to(m)
        else:
            folium.CircleMarker(
                coords,
                radius=4,
                color='#EA4335',
                fill=True,
                popup=f'<b>{city}</b>'
            ).add_to(m)

    return m._repr_html_()


@app.route('/')
def home():
    city = request.args.get('city', '')

    map_html = create_simple_map(city)

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Карта России</title>
        <style>
            body {{ margin: 0; padding: 0; font-family: Arial; }}
            .header {{ 
                background: white; 
                padding: 15px; 
                border-bottom: 1px solid #ddd;
                display: flex;
                gap: 10px;
            }}
            input {{
                flex: 1;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }}
            button {{
                padding: 10px 20px;
                background: #4285F4;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            #map {{ width: 100vw; height: calc(100vh - 60px); }}
        </style>
    </head>
    <body>
        <div class="header">
            <input type="text" id="city" placeholder="Введите город..." value="{city}">
            <button onclick="search()">Найти</button>
            <button onclick="reset()">Сброс</button>
        </div>
        <div id="map">{map_html}</div>
        <script>
            function search() {{
                const city = document.getElementById('city').value;
                window.location.href = '/?city=' + encodeURIComponent(city);
            }}
            function reset() {{
                window.location.href = '/';
            }}
            document.getElementById('city').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') search();
            }});
        </script>
    </body>
    </html>
    '''

    return html


if __name__ == '__main__':
    app.run(debug=True, port=5000)