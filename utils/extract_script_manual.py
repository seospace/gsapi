from bs4 import BeautifulSoup as soup
import requests
import random


SUBLIME_SNIPPET = """
<snippet>
	<content><![CDATA[{0}${1}]]></content>
    <description> /{2}</description>
    <tabTrigger>{3}</tabTrigger>
</snippet>

"""

TABLES = [
    dict(html_name='table sectionedit4', var_name="SETUP"),  # The SETUP Section
    dict(html_name='table sectionedit6', var_name="STEP"),  # The STEP Section
    dict(html_name='table sectionedit8', var_name="VARIABLES"),  # Variables usable in SETUP and STEP Section
    dict(html_name='table sectionedit10', var_name="DATA_TYPES"),    # Data types (user input)
    dict(html_name='table sectionedit15', var_name="DATA_EXTRACTION"),    # Data Extraction
]

HTML = requests.get('https://docu.gsa-online.de/search_engine_ranker/script_manual').content
PARSER = soup(HTML, 'lxml')
RESULTS = []


def parse_table(data: dict):
    _html_name = data['html_name']

    rows = PARSER.findAll('div', **dict(class_=_html_name))[0].find('table').find_all('tr')[1:]

    _return = []

    for r in rows:
        a = r.find_all('td')
        v = a[0].text.rstrip()  # variable
        d = a[1].text.rstrip()\
            .replace('<', '&lt;')\
            .replace('>', '&gt;')\
            .replace("'", "&apos;")\
            .replace('"', "&quot;")\
            .replace("&", "&amp;")  # description
        _return.append({v: d})
        print(d)
    return _return


for table in TABLES:
    need = parse_table(table)
    print(table['var_name'], need)

    for x in need:
        for k, v in x.items():
            data = SUBLIME_SNIPPET.format((k+'=').lower(), '{1}', v, k).replace('\n', '').replace('\t', '')
            file_name = './sublime_snippets/{0}.sublime-snippet'.format(k
                                                                        .replace('\n', '')
                                                                        .replace('\t', '')
                                                                        .replace('/', '')
                                                                        .replace('\\', ''))
            # write snippet
            file = open(file_name, 'w+', encoding='utf-8')
            file.write(data)
            file.close()
            # write help
            file2_name = 'help_sublime_snippets.ini'
            file2 = open(file2_name, 'a', encoding='utf-8')
            file2.write(f"{k}\n{v}\n########################################\n")
            file2.close()
