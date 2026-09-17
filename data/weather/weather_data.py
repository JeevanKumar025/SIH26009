import requests
import pandas as pd

url = "https://archive-api.open-meteo.com/v1/archive?latitude=21.55&longitude=79.69&start_date=2025-01-01&end_date=2026-01-01&daily=precipitation_sum,temperature_2m_max,temperature_2m_min"

response = requests.get(url)
data = response.json()

df = pd.DataFrame(data["daily"])

df.to_csv("data/weather/weather_dongribuzurg.csv", index=False)

print("Weather data saved successfully!")
print(df.head())