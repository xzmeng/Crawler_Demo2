# a crawler to get about 260 sets of sample pictures on girldelta
import requests
import os
from bs4 import BeautifulSoup
from multiprocessing import Pool


SAVE_DIR = 'D:/tmp/girls_delta'


def get_all_girls():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Referer': "http://cash.girlsdelta.com/gallery/"
    }
    url = 'http://cash.girlsdelta.com/gallery/'
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    li_s = soup.find_all('li')
    for li in li_s:
        a = li.find('a')
        p = li.find('p')
        girl_url = a['href']
        girl_name = a['title']
        date = p.find(attrs={'class': 'date'}).string
        yield (girl_url, girl_name, str(date))


def download_one_girl(girl_info):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Referer': "http://cash.girlsdelta.com/gallery/"
    }
    origin_url = 'http://cash.girlsdelta.com/gallery/delta/'
    r = requests.get(girl_info[0], headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    result = soup.select('#gallery')[0]
    a_s = result.find_all('a')
    url_s = []
    for a in a_s:
        url = a['href']
        url_s.append(url)
    print(url_s)
    image_num = len(url_s)
    # save
    girl_path = os.path.join(SAVE_DIR, girl_info[1] + ' ' + girl_info[2])
    if os.path.exists(girl_path):
        if len(os.listdir(girl_path)) == image_num:
            print(girl_path + ' is already downloaed.')
            return
        else:
            print(girl_path + ' is already existed but not fully downloaded.Downloading...')
    else:
        os.mkdir(girl_path)

    error_flag = False
    save_flag = False
    count = 0
    for url in url_s:
        r = requests.get(origin_url + url, headers=headers)
        print(origin_url + url)
        if r.status_code == 200:
            with open(os.path.join(girl_path, str(count) + '.jpg'), 'wb') as f:
                f.write(r.content)
            save_flag = True
        else:
            print('error:', r.status_code)
            error_flag = True
        count += 1
    if save_flag and not error_flag:
        print('Successfully download', girl_path)
    else:
        print('Problem occurs:', girl_path)


# if not os.path.exists(SAVE_DIR):
#     os.makedirs(SAVE_DIR)
# download_one_girl(next(get_all_girls()))
def main(girl_info_list, pid):
    down_num = len(girl_info_list)
    count = 0
    for girl_info in girl_info_list:
        print('Process ' + str(pid) + ' count ' + str(count) + '.')
        download_one_girl(girl_info)
        count += 1


if __name__ == '__main__':
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    infos = []
    for girl_info in get_all_girls():
        infos.append(girl_info)
    girl_num = len(infos)
    batch = 20
    p_num = girl_num // 20 + 1
    pool = Pool(p_num)
    for i in range(p_num):
        offset = i*batch
        if offset + batch < girl_num:
            end = offset + batch
        else:
            end = girl_num
        pool.apply_async(main, args=(infos[offset:end], i))
    pool.close()
    pool.join()