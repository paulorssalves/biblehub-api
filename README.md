# Biblehub scraper

- purpose: to scrape Biblehub for words in Koine Greek, get their definitions (if available) and examples (if available) 

- TODO:
    - **THE ESSENTIAL** is to be able to normalize the words out of their accents and get their lemmas

    - refactor code to submit functions to class instead of the other way around
    - return some sort of warning if the word that is returned by the scraper is not exactly the word entered
    - return some error or work around it if no word is found
        - like a list of words that had no return
    - Insert also the name of the book, the chapter and the versicle *for each example*.
