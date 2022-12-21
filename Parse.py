import re
import requests
from bs4 import BeautifulSoup

url = "https://www.miit.ru/timetable"
headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 OPR/90.0.4480.117 (Edition Yx GX)"}

def parse_university():
    page = requests.get(url, headers)
    soup = BeautifulSoup(page.content, "html.parser")
    name_university = [i.text.strip() for i in soup.find_all("span", class_="info-block__header-text")]
    return name_university

def parse_group(name):
    page = requests.get(url, headers)
    soup = BeautifulSoup(page.content, "html.parser")
    groups = soup.find("span", text=re.compile(name)).findParent("div").find_next("div").find_all("a", text=re.compile('\W\w\d'))
    university_dict = {i.text.strip() : i.get("href") for i in groups}
    return university_dict

def parse_timetable(url_component):
    page = requests.get("https://www.miit.ru" + url_component, headers)
    soup = BeautifulSoup(page.content, "html.parser")
    tables = [i for i in soup.findAll("table", class_="table timetable__grid")]
    return (tables, "https://www.miit.ru" + url_component)

def set_text(dat):
    text = dat[0]
    for j in dat[1:]:
        if '\n' not in j[0]:
            text += "\n" + j
        else:
            text += j
    return text

def rewrite_space(text):
    dat = text.split(' ')
    txt = dat[0]
    sums = len(dat[0])
    for j in range(1, len(dat)):
        sums += len(dat[j]) + 1
        if (sums < 20):
            txt += " " + dat[j]
            continue
        else:
            txt += '\n' + dat[j]
            sums = -10000
    return txt

def split_text(text):
    if re.search(r'[\s\t\r]{2,}', text) is not None:
        dat = text.replace(re.search(r'[\s\t\r]{2,}', text)[0], '\n').split('\n')
    else:
        dat = text.split('\n')
    for i in range(len(dat)):
        if (len(dat[i]) > 20 and ' ' in dat[i]):
            dat[i] = rewrite_space(dat[i])
            break
    else:
        return set_text(dat)
    return split_text(set_text(dat))

def set_table(tables):
    matrix = [[]]
    rows = tables.findAll("tr")

    for i in rows[0].findAll("th"):
        matrix[0].append(i.text.strip().split("\n")[0])
    for i in rows[1:]:
        cols = []
        cols.append(i.find("td", class_="text-right").text.strip())
        for k in i.findAll("td", class_="timetable__grid-day"):
            dop = list(map(lambda d: "\n" + d.text.replace('\n', '').replace('\r', ''), k.findAll("a", class_="timetable-icon-link icon-location")))
            cols.append(k.find("div", class_="timetable__grid-day-lesson").text.strip() + "".join(dop))
        matrix.append(cols)

    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            matrix[i][j] = matrix[i][j].replace('\r', '').replace(';', ';\n')
    for i in range(len(matrix[0])):
        matrix[0][i] = matrix[0][i].replace(' ', '')

    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if (i != 0 and matrix[i][j] != ''):
                matrix[i][j] = split_text(matrix[i][j])

    return matrix

