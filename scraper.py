import requests
from bs4 import BeautifulSoup as bs4
import bs4 as bs
import pandas as pd

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
    **IT IS NECESSARY TO SHOW SOME WARNING IF ANOTHER WORD (other than the desired one) IS PICKED**
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

def fetch_group_as_string(group, single_list=False):
    """
    Transforma grupo de strings em uma lista em uma só string.
    Deste modo, o arquivo .csv final não fica cheio
    de colchetes.
    """

    strings = ""
    if single_list==True:
        for i in range(len(group)): 
            strings+=group[i]
            if i < (len(group) - 1): 
                strings+="\n\n"
        return strings
    else:
        for i in range(len(group)):
            for j in range(len(group[i])):
                strings+=group[i][j]
                if (j == 0):
                    strings+="\n\n"
                else:
                    strings+="\n"
            if (i < len(group)-1):
                strings+="\n"

        return strings

class Word:
    def __init__(self, data_dict):
        self.data = data_dict
        self.concordances = self.data["concordances"]
        self.name = self.concordances["Original Word"]
        self.examples = self.data["examples"]
        self.category = self.concordances["Part of Speech"]
        self.transliteration = self.concordances["Transliteration"]
        self.phonetics = self.concordances["Phonetic Spelling"]
        self.definition = self.concordances["Definition"]

if __name__ == "__main__": 

    REQUEST_NUMBER = 68

    f = pd.read_csv("greek_words.csv", header=None,names=["word(s)"])

    head = f.head(REQUEST_NUMBER)

    for cell in head.iteritems():
        for word in cell[1]:

            link = get_link(BASE_URL, word)
            soup = get_entry_soup(link)
            word = Word(get_word_data(soup))
            print (word.name)

            dc = {
                "word": word.name,
                "phonetics": word.transliteration + "\n" + word.phonetics,
                "category": word.category,
                "meaning": word.definition,
                "greek": fetch_group_as_string([tuple[0] for tuple in word.examples], single_list=True),
                "english": fetch_group_as_string([tuple[1] for tuple in word.examples], single_list=True)
            }

            words_dataframe = pd.DataFrame.from_dict(dc, orient="index")
            words_dataframe = words_dataframe.transpose()
            words_dataframe.to_csv("output.csv",encoding="utf-8",mode="a",header=False, index=False) 