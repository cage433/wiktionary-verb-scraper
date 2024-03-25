import argparse
import csv
import unicodedata
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag

RUSSIAN_DIR = Path('/Users/alex/repos/russian/')


def query_pages_for_verb(verb):
    print(f"Asking for response for verb {verb}")
    url = f"https://en.wiktionary.org/wiki/{verb}#Conjugation.php"
    resp = requests.get(
        url,
        params={}
    ).text
    soup = BeautifulSoup(resp, 'html.parser')
    divs = soup.body.find("div", {"class": 'NavHead'})
    table = soup.body.find("div", {"class": 'NavContent'})
    rows = table.find_all('tr')
    type_row = [divs.contents[-1]]
    table = [
        [verb],
        type_row
    ]
    for row in rows:
        # print(row.contents)
        texts = []
        for term in row.children:
            if isinstance(term, Tag):
                if term.name == 'td':
                    term = term.contents[0]
                if isinstance(term, Tag):
                    texts.append(term.text.strip())
        texts = [sanitize(c).strip() for c in texts]
        table.append(texts)
    return table

def write_csv_file(path, table, quoting = None):
    with open(path, 'wt', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(table)

def extract_verb_data():
    with open(RUSSIAN_DIR / 'verbs.txt', 'rt', newline='', buffering=1) as fw:
        verbs = fw.read().splitlines()

    for i, row in enumerate(verbs):
        verb = row.split(' ')[2]
        table = query_pages_for_verb(verb)
        write_csv_file(RUSSIAN_DIR / "csvs" / f"{i}-{verb}.csv", table)


# def query_pages():
#     with open(RUSSIAN_DIR / verbs.txt', 'rt', newline='', buffering=1) as fw:
#         verbs = fw.read().splitlines()
#
#     for row in verbs[:2]:
#         verb = row.split(' ')[2]
#         print(f"Asking for response for verb {verb}")
#         url = f"https://en.wiktionary.org/wiki/{verb}#Conjugation.php"
#         resp = requests.get(
#             url,
#             params={}
#         ).text
#         soup = BeautifulSoup(resp, 'html.parser')
#         divs = soup.body.find("div", {"class": 'NavHead'})
#         print(divs.contents[-1])
#         table = soup.body.find("div", {"class": 'NavContent'})
#         rows = table.find_all('tr')
#         for row in rows:
#             # print(row.contents)
#             texts = []
#             for term in row.children:
#                 if isinstance(term, Tag):
#                     if term.name == 'td':
#                         term = term.contents[0]
#                     if isinstance(term, Tag):
#                         texts.append(term.text.strip())
#             texts = [sanitize(c).strip() for c in texts]
#             print(texts)


# def get_verb(doc):
#     print("Getting verb")
#     soup = BeautifulSoup(doc, 'html.parser')
#     columns = soup.findAll('td', {
#         'align': 'left'
#     })
#
#     forms = []
#     for item in columns:
#         forms += map(
#             lambda x: sanitize(x).strip(),
#             filter(lambda x: isinstance(x, str), item.contents)
#         )
#
#     try:
#         return {
#             'present_i': forms[0],
#             'present_thou': forms[4],
#             'present_it': forms[8],
#
#             'present_we': forms[13],
#             'present_you': forms[16],
#             'present_they': forms[19],
#
#             'past_male': forms[9],
#             'past_female': forms[10],
#             'past_neutral': forms[11],
#             'past_many': forms[14],
#             'imperative': forms[7]
#         }
#     except IndexError as ex:
#         print(ex, columns)
#         return None
#

def sanitize(word):
    return ''.join(filter(
        lambda x: unicodedata.category(x) != 'Mn' and x not in ['△', '*'],
        unicodedata.normalize('NFD', word)
    ))


# def get_progress(current, total):
#     return f'{round(current / total * 100)}%'

if __name__ == '__main__':
    extract_verb_data()

# def main(*args, **kwargs):
#     total_pages = 34704
#     with open(kwargs['filename'], 'w', newline='', buffering=1) as fw:
#         counter = 0
#         writer = None
#
#         for response in query_pages():
#             for elem in response['categorymembers']:
#                 page_id = elem['pageid']
#                 page = get_page(page_id)
#                 verb = get_verb(page)
#
#                 if verb is None:
#                     print(f'An error occured on page {page_id} processing')
#                     continue
#
#                 if counter == 0:
#                     writer = csv.DictWriter(fw, verb.keys())
#                     writer.writeheader()
#
#                 writer.writerow(verb)
#
#                 counter += 1
#                 print(f'{get_progress(counter, total_pages)} {elem}')
#

def argparser():
    parser = argparse.ArgumentParser(
        description='Scrape Russian verb forms from Wiktionary.',
        add_help=True
    )
    parser.add_argument(
        '--filename',
        type=str,
        default='verbs.csv',
        help='file to save verb forms to (default: verbs.csv)'
    )
    return parser


if __name__ == '__main__':
    main(**vars(argparser().parse_args()))
