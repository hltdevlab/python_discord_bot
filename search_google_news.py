import requests
from bs4 import BeautifulSoup

def __extract(elem, name, css, attribute=None):
    try:
        target_elem = elem if css == "*" else elem.select_one(css)
        if target_elem:
            extracted = target_elem[attribute] if attribute else target_elem.text
            output = f"{name}: {extracted.strip()}"
            # print(output)
            return output

    except Exception as e:
        print(f"Error at extract() for {name}: {e}")

    return None


def __scrap_item(elem):
    output_arr = [
        __extract(elem, "title", '[role="heading"]'),
        __extract(elem, "content", '[role="heading"] + div'),
        __extract(elem, "datetime", '[role="heading"] + div + span + div'),
        __extract(elem, "source", 'g-img + span')
        # __extract(elem, "url", '*', attribute='href')
    ]
    output_arr = list(filter(lambda x: x != None, output_arr))
    # print(f"output_arr: {output_arr}")
    return "\n".join(output_arr)


def search_google_news(query):
    if query is None or query == '':
        query = 'Singapore news today'

    url = f"https://www.google.com.sg/search?q={query}&tbm=nws&num=10"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Referer': 'https://www.google.com.sg'
    }

    response = requests.get(url, headers=headers)
    # print(f"response: {response.content}")
    soup = BeautifulSoup(response.content, 'html.parser')
    # print(f"soup: {soup}")
    article_elems = soup.select('#search [data-hveid][data-ved] a')
    # print(f"article_elems: {len(article_elems)}")

    return list(map(lambda x: __scrap_item(x), article_elems))


def search_google_news_str(query):
    output_arr = search_google_news(query)
    return "\n\n".join(output_arr)


# results = search_google_news("Singapore news today")
# print(results)
