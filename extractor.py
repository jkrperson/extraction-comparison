import requests, justext, csv

from goose3 import Goose
from readability import Document
from newspaper import fulltext, Article
from html.parser import HTMLParser
from difflib import SequenceMatcher

from readability.cleaners import normalize_spaces

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

results_csv = open("result.csv", "w")
results_writer = csv.writer(results_csv, delimiter="|", quotechar="$")
results_writer.writerow(["News #", "Justext", "Goose", "Readability", "Newspaper"])
counter = 0

with open('news.csv' , 'r') as news_csv:
    news_csv_reader = csv.reader(news_csv, delimiter="|", quotechar="$")
    for row in news_csv_reader:
        
        if row[0] != "0":
            counter += 1
            print(counter)
            response = requests.get(url=row[1],headers=headers )

            orig_content = row[2]

            # Justext    
            paragraphs = justext.justext(response.content, justext.get_stoplist("Tagalog"))
            justext_content = ""
            for paragraph in paragraphs:
                if paragraph.class_type == 'good':
                    justext_content += paragraph.text + "\n"

            # Goose
            g = Goose()
            article =g.extract(raw_html=response.content)
            goose_content = article.cleaned_text

            # Readabilty
            doc = Document(response.text)
            readiblity_content = strip_tags(normalize_spaces(doc.summary())).strip()

            # Newspaper
            try:
                newspaper_content = fulltext(response.text, language='tl')
            except AttributeError:
                newspaper_content = ""

            # Similarity Checking
            j = similar(justext_content, orig_content)
            g = similar(goose_content, orig_content)
            r = similar(readiblity_content, orig_content)
            n = similar(newspaper_content, orig_content)
            
            results_writer.writerow([counter, j, g, r, n])
