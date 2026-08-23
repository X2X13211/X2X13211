from datetime import datetime, timedelta
import json
import os
import urllib.request

# Укажи свой цифровой ID на Stepik
STEPIK_USER_ID = "ТВОЙ_STEPIK_ID"

url = f"https://stepik.org/api/user-activities/{STEPIK_USER_ID}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

try:
  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    pins = data.get("user-activities", [{}])[0].get("pins", [])
except Exception as e:
  print(f"Error fetching Stepik data: {e}")
  pins = []

# Словарь активности: { 'YYYY-MM-DD': count }
activity_map = {}
# Stepik отдает пины от текущей даты назад
today = datetime.utcnow().date()
for i, count in enumerate(pins):
  day = today - timedelta(days=i)
  activity_map[day.isoformat()] = count

# Параметры SVG
box_size = 11
gap = 3
cols = 40  # количество недель отображения (~9 месяцев)
rows = 7
width = cols * (box_size + gap) + 40
height = rows * (box_size + gap) + 40

# Цветовая палитра Deep Burgundy
colors = {
    0: "#2A2A2A",  # Пустой день
    1: "#4A0013",  # Низкая активность
    2: "#800020",  # Средняя активность (#800020)
    3: "#B3002D",  # Высокая активность
    4: "#FF1A53",  # Максимальная активность
}


def get_color(count):
  if count == 0:
    return colors[0]
  elif count <= 2:
    return colors[1]
  elif count <= 5:
    return colors[2]
  elif count <= 10:
    return colors[3]
  return colors[4]


# Генерация SVG
rects = []
start_date = today - timedelta(days=(cols * 7) - 1)
# Выравнивание на понедельник
start_date -= timedelta(days=start_date.weekday())

curr = start_date
for c in range(cols):
  for r in range(rows):
    date_str = curr.isoformat()
    count = activity_map.get(date_str, 0)
    color = get_color(count)
    x = 20 + c * (box_size + gap)
    y = 20 + r * (box_size + gap)
    rects.append(
        f'<rect x="{x}" y="{y}" width="{box_size}" height="{box_size}"'
        f' fill="{color}" rx="2"><title>{date_str}: {count} steps</title></rect>'
    )
    curr += timedelta(days=1)

svg_content = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="{width}" height="{height}" rx="10" fill="#1C1C1C"/>
  <text x="20" y="14" fill="#800020" font-family="monospace" font-size="11" font-weight="bold">STEPIK ACTIVITY STREAM</text>
  {''.join(rects)}
</svg>"""

os.makedirs("assets", exist_ok=True)
with open("assets/stepik_heatmap.svg", "w", encoding="utf-8") as f:
  f.write(svg_content)
