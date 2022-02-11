import requests
from bs4 import BeautifulSoup as bs4
import bs4 as bs

EXAMPLE_NUMBER=3

BASE_URL = "https://biblescan.com/searchgreek.php?q="
# word_query = "καί" # str(input("Input a greek word:")) 

def get_summary(page):
    """
    gets summary for the searches. If no results are found, returns None.
    """
    soup = bs4(page.content, "html.parser")
    summary = soup.find(class_="summary")
    if (summary.text.strip() == "No results found."):
        return None 
    else:
        return True

def get_link(BASE_URL, WORD_QUERY):
    """
    gets the link from a list of links in a query. Chooses the one which most resembles the given word.
    """
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
                return results[0]["href"]
    else:
        return ""

def get_entry_soup (ENTRY_LINK):
    """
    gets the HTML data for the link its fed 
    """
    page = requests.get(ENTRY_LINK)
    soup = bs4(page.content, "html5lib")
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

def get_greek_examples(soup, number):
    """
    grabs greek examples for the given word, after its page has been retrived
    """
    centbox = soup.find(id="centbox") 
    padcent = centbox.find(class_="padcent")
    p_tags = padcent.find_all("p")
    l = []
    for tag in p_tags:
        try:
            greek = tag.find("span", class_="greek3")
            l.append(greek.text)
        except AttributeError:
            break
    return l[:number] 

def get_english_examples(soup, number):
    """
    grabs english examples for the given word, after its page has been retrived
    """
    centbox = soup.find(id="centbox")
    padcent = centbox.find(class_="padcent")
    p_tags = padcent.find_all("p")
    translations = []
    for tag in p_tags:
        current = ""
        try:
            anchor = tag.find_next("a", title="Biblos Interlinear Bible")
            working = anchor.next
            while working.next.name is not "p":
                if type(working.next) == bs.element.Tag:
                    working = working.next
                    if working.text == working.next:
                        working = working.next
                        current+=working
                    else:
                        current+=working 
                else:
                    working = working.next
                    current+=working
        except AttributeError:
            break
        translations.append(current)
    return translations[:number]

def get_word_data(soup):
    concordances = get_greek_concordance(soup)
    greek_examples = get_greek_examples(soup,EXAMPLE_NUMBER)
    english_examples = get_english_examples(soup,EXAMPLE_NUMBER)

    return {
        "concordances": concordances,
        "examples": [(greek, english) for (greek, english) in zip(greek_examples, english_examples)]
    }

class Word:
    def __init__(self, data_dict):
        self.data = data_dict
        self.concordances = self.data["concordances"]
        self.name = self.concordances["Original Word"]
        self.examples = self.data["examples"]
    
    def category(self):
        return self.concordances["Part of Speech"]
    
    def transliteration(self):
        return self.concordances["Transliteration"]

    def category(self):
        return self.concordances["Part of Speech"]

    def phonetics(self):
        return self.concordances["Phonetic Spelling"]

    def definition(self):
        return self.concordances["Definition"]


if __name__ == "__main__": 
    link = get_link(BASE_URL, "καί")
    soup = get_entry_soup(link)
    word = Word(get_word_data(soup))
    print(word.definition())
    print(word.category())
    print(word.phonetics())
    print(word.transliteration())
    print(word.examples)
