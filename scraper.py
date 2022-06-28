import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import json

from tomlkit import array

URL = "https://covid19.riau.go.id/pantauan_data_kasus"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}
FILEDIR = "./"
FILENAME = "covid19-data-riau"

start_time = time.time()
r = requests.get(URL, headers=HEADERS).text
soup = BeautifulSoup(r, "html.parser")

section_title = soup.find("div", class_="section-title").text.strip()
city_list = soup.find_all("a", attrs={"href": lambda txt: "corona.riau" in txt.lower()})
all_cases = soup.find_all("td", class_="text-right")
labels = soup.find_all("th", class_="text-center")
labels = [label.text.strip() for label in labels]
# print(labels)

cases = []
for i, case in enumerate(all_cases):
    cases.append(case.text.strip())
cases = np.array(cases).reshape((len(city_list), len(labels[3:]))) 
# print(cases.shape)
# print(cases[0])

data = {}
for i, city in enumerate(city_list):
    city_url = city["href"]
    city = city.text.strip()
    data[city] = {
        # "city": city,
        "city url": city_url,
        "cases": {
            "spesimen": dict(zip(labels[3:7], cases[i][:4])),
            "suspek": dict(zip(labels[7:11], cases[i][4:8])),
            "terkonfirmasi": dict(zip(labels[11:], cases[i][8:])),
        }
    }
    # print(labels[3:])
    # print(cases[i])
    # break

# print(data[0])

with open("{}.json".format(FILENAME), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

index = pd.Index([city.text.strip() for city in city_list])
columns = pd.MultiIndex.from_arrays(
    (['spesimen']*4 + ['suspek']*4 + ['terkonfirmasi']*4, labels[3:])
)
df = pd.DataFrame(cases, index=index, columns=columns)
print(df.head(20))

df.to_csv("{}.csv".format(FILENAME), index=True)

print("Finish in %s.3f seconds." % (time.time()-start_time))
