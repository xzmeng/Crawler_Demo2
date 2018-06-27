# 爬取 www.27270.com 上的图片
# 爬取 首页 > 娱乐周边 > 电影海报 下的约 35 * 93(页）= 3255套图片
import requests
import re
import os
from bs4 import BeautifulSoup
# from multiprocessing import Pool


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Referer': "http://www.27270.com"
}
SAVE_DIR = 'D:/tmp/27270.com/haibao/'


def get_all_pages():  # 获取电影海报的所有列表页面，改变/haibao/可以爬取其他类别
    url = 'http://www.27270.com/ent/haibao/'
    r = requests.get(url, headers=HEADERS)
    r.encoding = 'gbk'
    soup = BeautifulSoup(r.text, 'lxml')
    last_page = soup.select('body > div:nth-of-type(2) > div.NewPages > ul > li:nth-of-type(14) > a')
    page_name = last_page[0]['href']
    page_prefix = re.match('(.*_).*?.html', page_name).group(1)
    total_num = int(re.match('.*_(.*?).html', page_name).group(1))
    for i in range(1, total_num + 1):
        yield url + page_prefix + str(i) + '.html'


def get_movies_in_one_page(page_url):  # 获取一个列表页面内所有电影的 (url,名称)
    r = requests.get(page_url, headers=HEADERS)
    r.encoding = 'gbk'
    soup = BeautifulSoup(r.text, 'lxml')
    movie_list = soup.select('body > div:nth-of-type(2) > div:nth-of-type(7) > ul > li')
    for li in movie_list:
        tag_a = li.select('a')[0]
        movie_url = tag_a['href']
        movie_title = tag_a['title']
        yield (movie_url, movie_title)


def get_all_movies():
    for page_url in get_all_pages():
        for movie in get_movies_in_one_page(page_url):
            yield movie


def get_one_image(image_page_url):   # 获取一个图片页中的图片文件（图片没有命名规则，需要遍历所有图片页获取）
    r = requests.get(image_page_url, headers=HEADERS)
    r.encoding = 'gbk'
    soup = BeautifulSoup(r.text, 'lxml')
    image_url = soup.select('#picBody img')[0]['src']
    r2 = requests.get(image_url, headers=HEADERS, timeout=10)
    if r2.status_code==200:
        return r2.content
    else:
        print(r2.status_code)
        return None

def save_one_movie_images(movie):  # 遍历一个电影的所有图片页面并保存图片
    movie_url, movie_name = movie[0], movie[1]
    movie_dir = os.path.join(SAVE_DIR, movie_name)
    r = requests.get(movie_url, headers=HEADERS, timeout=10)
    if r.status_code != 200:
        print(r.status_code)
        return
    r.encoding = 'gbk'
    soup = BeautifulSoup(r.text, 'lxml')
    tag_a = soup.select('#pageinfo > a')[0]
    print(movie_name, tag_a.string)
    total_num = int(re.match('共(.*?)页: ', tag_a.string).group(1))
    if os.path.exists(movie_dir):
        if len(os.listdir(movie_dir)) == total_num:
            print(movie_name + ' is already downloaded.')
            return
        else:
            print(movie_name + ' is already existed but not totally downloaded.Downloading...')
    else:
        os.mkdir(movie_dir)

    for i in range(1, total_num+1):
        image_page_url = movie_url.replace('.html', '_' + str(i) + '.html')
        content = get_one_image(image_page_url)
        if content is None:
            continue
        with open(os.path.join(movie_dir, str(i) + '.jpg'), 'wb') as f:
            f.write(content)
    print('Successfully download ' + movie_name + '.')


def main(download_list, num):
    count = 0
    print(num)
    try:
        for i in download_list:
            print('Process ', num, 'downloading no.', count)
            count += 1
            save_one_movie_images(i)
    except e:
        print(e)
    print('Process', num, 'end, count is', count)


if __name__ == '__main__':
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    all_movies = []
    print('正在加载所有电影的列表...')
    for movie in get_all_movies():
        all_movies.append(movie)
    movie_num = len(all_movies)
    print('一共找到' + str(movie_num) + '部电影，开始下载.')

    for movie in all_movies:
        save_one_movie_images(movie)

    # batch = 200
    # p_num = movie_num // batch + 1
    # print('p_num:', p_num)
    # pool = Pool(p_num)
    # for i in range(p_num):
    #     offset = i*batch
    #     if offset + batch < movie_num:
    #         end = offset + batch
    #     else:
    #         end = movie_num
    #     pool.apply_async(main, args=(all_movies[offset:end], i))
    # pool.close()
    # pool.join()



