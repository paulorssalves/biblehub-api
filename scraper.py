import requests
from bs4 import BeautifulSoup as bs4

BASE_URL = "https://biblescan.com/searchgreek.php?q="
# word_query = "καί" # str(input("Input a greek word:")) 

def get_summary(page):
    soup = bs4(page.content, "html.parser")
    summary = soup.find(class_="summary")
    if (summary.text.strip() == "No results found."):
        return None 
    else:
        return True

def get_link(BASE_URL, WORD_QUERY):

    page = requests.get(BASE_URL+WORD_QUERY)

    if get_summary(page) == True:
        soup = bs4(page.content, "html.parser") 
        result_list = soup.find(class_="results")
        results = result_list.find_all("a")
        
        for index in range(len(results)):
            link = results[index]["href"]
            word = str(results[index].text.strip())
            if WORD_QUERY in word:
                return link
            else:
                return results[0]["href"], None
    else:
        return ""

def get_entry_soup (ENTRY_LINK):
    page = requests.get(ENTRY_LINK)
    soup = bs4(page.content, "html.parser")
    return soup

def get_greek_concordance(soup):
    strong_concordance = soup.find(id="leftbox")
    strong_categories = strong_concordance.find_all("span", class_="tophdg")

    strong_dict = {}
    for item in strong_categories:
        if "greek" in str(item.next_sibling):
            strong_dict[item.text.strip().replace(":","")] = item.next_sibling.text.strip()
        else:
            strong_dict[item.text.strip().replace(":", "")] = item.next_sibling
    return strong_dict

def get_englishman_concordance(soup):
    englishman_concordance = soup.find(id="centbox") 
    inner_div = englishman_concordance.find(class_="padcent")
    p_tags = inner_div.find_all("p")
    for index in range(len(p_tags)):
        if index <= 0:
            a = p_tags[index].find_all("a")
            greek_spans = p_tags[index].find_all("span", class_="greek3")
            itali_spans = p_tags[index].find_all("span", class_="itali")
            zipped = zip(greek_spans, itali_spans)
            for g_span, i_span in zipped:
                print("{}: {}{}{}".format(g_span.text, i_span.previous_sibling, i_span.text, i_span.next_sibling))

            """
            Aparentemente o jeito tem que ser da seguinte forma:
            - pegar o texto em grego
            - pegar <br> que o segue
            - pegar o <a> que segue o <br>
            - pegar todos os next_sibling que precedem o próximo <br> 
            """

        else:
            break

link = get_link(BASE_URL, "καί")
soup = get_entry_soup(link)
get_englishman_concordance(soup)