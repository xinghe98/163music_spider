import requests
from tqdm import tqdm
import re
from queue import Queue
import threading
import os

playlist = Queue()
songs = Queue()


headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }

def playlist_url():
    play_list = input("请输入歌单ID:")
    url = 'https://music.163.com/playlist?id={}'.format(play_list)
    if os.path.exists('./music') == False:
      os.makedirs('./music')
      print('\n文件夹创建成功')
    else:
      print('\n文件夹已存在')
    playlist.put(url)

def get_page():
    while True:
        url = playlist.get()
        res = requests.get(url,headers = headers)
        id_list = re.findall(r'<a href="/song\?id=(\d+)">(.*?)</a>',res.text)
        if id_list:
          for item in id_list:
              songs.put(item)
        else:
          print('请输入正确的歌单id')
        playlist.task_done()

def download_music():
    while True:
      id,name = songs.get()
      url = 'http://music.163.com/song/media/outer/url?id={}.mp3'.format(id)
      try:
        res = requests.get(url,headers = headers,stream=True)
        file_size = int(res.headers['content-length'])/1024/1024
        pdar = tqdm(iterable=res.iter_content(1024*1024),ncols=70 ,total=file_size, desc=name, unit="M", unit_scale=True)
        with open(r'./music/%s.mp3' % (name), 'wb')as f:
            for chunk in pdar:
                f.write(chunk)
        pdar.close()
      except KeyError:
        print(name+'------该歌曲可能已经下架')
        pass
      songs.task_done()


if __name__ == "__main__":
   thread_list=[]
   t1 =  threading.Thread(target = playlist_url)
   thread_list.append(t1)
   t2 = threading.Thread(target=get_page)
   thread_list.append(t2)
   t3 = threading.Thread(target=download_music)
   thread_list.append(t3)
   for t in thread_list:
       t.setDaemon(True)
       t.start()
   t1.join()
   for q in [playlist,songs]:
       q.join()










