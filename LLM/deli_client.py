import requests
import json


def search_law(query):
    LAW_VECTOR_API_URL = "" # Place your API URL here
    URL = "" # Place your API URL here
    params = {"question": query}
    res = requests.get(URL, params=params)
    res = json.loads(res.text)

    return res


if __name__ == "__main__":
    query = "《中华人民共和国劳动法》第四十三条规定？"
    print(search_law(query))
