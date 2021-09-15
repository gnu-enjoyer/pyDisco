#cython: language_level=3
import re, urllib.request, os.path, youtube_dl

cpdef interrupt(msg, int code):
    print(msg)

    # ERROR codes:
    # 0 = none,
    # 1 = cython,
    # 2 = python

    if code == 0:
        input('press any key to continue')
        return

    input('press any key to close')
    exit(code)

cpdef read_config():
    # Leave return as PyObj, not bytes?
    cdef cfg = <bytes> 'config.txt'

    if os.path.exists(cfg):
        with open(cfg, 'r') as f:
            length = f.read()
            if len(length) > 60:
                interrupt("ERROR: config file malformed", 1)
            else:
                return length
    else:
        interrupt('ERROR: config file not found', 1)


def lst_valid(list lst) -> bool:
    cdef list lst2 = []
    if lst2 != lst: return True
    # Naughty but nice

def search(query) -> list:
    query = re.sub('[^A-Za-z0-9]+', '', query)
    query = query.replace(' ', '+')
    html = urllib.request.urlopen('https://www.youtube.com/results?search_query=' + query)
    cdef list video_ids = re.findall(r'watch\?v=(\S{11})', html.read().decode())

    return video_ids

def download(url, g_id) -> str:

    # Deprecated in favour of streaming

    if os.path.exists(g_id):
        os.remove(g_id)

    ydl_opts = {
        'format': 'best[filesize<50M]',
        'outtmpl': g_id
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        ydl.prepare_filename(info_dict)
        ydl.download([url])

    return info_dict['title']

def cy_init(client) -> bool:
    for x in client.guilds:
        client.playlist.add(
            x.id)
        print('Connected: ' + x.name)

    client.playlist = dict.fromkeys(client.playlist, [])

    return True