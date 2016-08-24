# -*- coding: UTF-8 -*-

import sys
import argparse
import time
import urllib
import urllib2
from random import randint
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf8')

# Some User Agents
hds = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}, \
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]


def search_book_by_name(name):
    html_text = ""
    page_num = 0

    # url = "https://book.douban.com/subject_search?search_text=%E8%A7%A3%E5%BF%A7"
    base = "https://book.douban.com/subject_search?search_text="
    url_name = urllib.quote(name)
    url = base + url_name

    try:
        req = urllib2.Request(url, headers=hds[page_num % len(hds)])
        source_code = urllib2.urlopen(req).read()
        html_text = str(source_code)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e

    return html_text


def search_book_by_tag(tag, pages=1):
    # https://book.douban.com/tag/%E5%84%BF%E7%AB%A5%E6%96%87%E5%AD%A6
    # https://book.douban.com/tag/%E5%84%BF%E7%AB%A5%E6%96%87%E5%AD%A6?start=40&type=T
    # 40 is the page number, T means "综合排序"
    number_per_page = 20
    page_num = number_per_page * (pages - 1)

    base = "https://book.douban.com/tag/"
    suffix = urllib.quote(tag) + "?start=" + str(page_num) + "&type=T"

    url = base + suffix

    try:
        req = urllib2.Request(url, headers=hds[page_num % len(hds)])
        source_code = urllib2.urlopen(req).read()
        html_text = str(source_code)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e

    return html_text


def parse_book_urls(html_text, counter=1):
    urls = []
    tmp_counter = 0

    soup = BeautifulSoup(html_text, "html.parser")
    list_soup = soup.find('ul', {'class': 'subject-list'})

    if list_soup is not None:
        for book_info in list_soup.findAll('li'):
            tmp_counter += 1
            if tmp_counter > counter:
                break
            book_url = book_info.find('a', {'class': 'nbg'}).get('href')
            urls.append(book_url)

    return urls


def get_detail_by_url(url):
    # https://book.douban.com/subject/1433640/
    page_num = 0
    html_text = ""

    try:
        req = urllib2.Request(url, headers=hds[page_num % len(hds)])
        source_code = urllib2.urlopen(req).read()
        html_text = str(source_code)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e

    return html_text


def parse_book_details(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    book_html = soup.find('div', {'id': 'wrapper'})
    title = book_html.find('h1').find('span').string

    list_details = book_html.find(id='info').find_all('span', {'class': 'pl'})
    book = {}
    book['title'] = title
    if list_details is not None:
        counter = 1
        for item in list_details:
            if item.nextSibling.nextSibling.has_attr('href'):
                book[item.string.strip().strip(':')] = item.nextSibling.nextSibling.string
            else:
                book[item.string.strip().strip(':')] = item.nextSibling.string.strip()

    book['rating'] = book_html.find('strong', {'class':'rating_num'}).string.strip()

    book['rating_people'] = book_html.find('a', {'class': 'rating_people'}).find('span').string.strip()

    intros = book_html.find(id='link-report').find('div', {'class': 'intro'}).find_all('p')
    book['intro'] = ""
    if intros is not None:
        for intro in intros:
            book['intro'] = book['intro'] + intro.string + "\n"

    print book['title'], book['ISBN'], book['rating'], book['rating_people'], book['intro']


def get_args():
    parser = argparse.ArgumentParser(description='Douban Spider.')
    parser.add_argument('-n', '--name', type=str, default="计算机", help='Add a name which you are interested in.')
    parser.add_argument('-t', '--tag', type=str, default="计算机", help='Add a tag which you are interested in.')
    parser.add_argument('-s', '--spider', action='store_true', help='Spider all.')
    args = parser.parse_args()
    name = args.name
    tag = args.tag
    spider = args.spider
    return name, tag, spider


if __name__ == '__main__':
    name, tag, spider = get_args()
    if tag is not None:
        urls = parse_book_urls(search_book_by_tag(tag))
        if urls is not None:
            for url in urls:
                parse_book_details(get_detail_by_url(url))

    elif name is not None:
        urls = parse_book_urls(search_book_by_name(name))

        if urls is not None:
            for url in urls:
                parse_book_details(get_detail_by_url(url))


