from extractors import Extract
import requests, os, m3u8
from tqdm import tqdm
from urllib.parse import urlparse, unquote


def launcher(url,path,name,resolution='high'):

        if 'video.sibnet.ru' in url:
            ini = Extract(url)
            ext, nom= ini.extracted, ini.name
            nom = nom if name==None else name
            Engine_http(ext,path=path,name=nom)

        elif 'sendvid.com' in url: 
            Engine_http(Extract(url).extracted,path,name=name) # name suggested

        elif 'yourupload.com' in url:
            ini = Extract(url)
            ext,ref = ini.extracted, ini.misc
            Engine_http(ext,path,headers={'Referer':ref},name=name)

        elif 'vidmoly.to' in url:
            ini = Extract(url)
            ext,headers = ini.extracted, ini.misc
            Engine_m3u8(ext,path,headers=headers,name=name,quality=resolution)

        elif 'vk.com' in url:
            ini = Extract(url,quality=resolution)
            ext,head = ini.extracted, ini.misc
            Engine_http(ext,path,name=name,headers=head)

        else:
            print('Invalid url syntax or Host not supported')
            

def downloader(vids,path=r'./pydowns',name=None,resolution='high'):

    if not os.path.exists(path):
        os.makedirs(path)

    if isinstance(vids,str):
        vids = vids.splitlines()
    
    c = 1
    for url in vids:
        print(f"\rDowloading : {c}/{len(vids)}")
        launcher(url,path,name,resolution)
        c+=1


def select_res(plays,quality):

    if quality == None or quality == 'high': # could've used max or sorted
        h,s = (0,0) 

        for re,solution in plays.keys():
            if int(re)*int(solution)>h*s:
                h,s=re,solution
        return (h,s)
    
    if quality == 'low':

        h,s = (7880,4320) # More than the highest resolution possible
        for re,solution in plays.keys():
            if int(re)*int(solution)<h*s:
                h,s=re,solution
        return (h,s)
    
    if quality == 'mid': # second best

        h,s = select_res(plays,quality='low')
        b,r = select_res(plays,quality='high')

        for re,solution in plays.keys():
            if re*solution > h*s and re*solution!=b*r:
                h,s = re,solution
        return (h,s)




def Engine_m3u8(url:str,path,quality=None,headers={},name=None):

    if not name:
        name = "video_unnamed"
    filename = name+'.ts'
    playlists = m3u8.load(url,headers=headers).playlists
    plays = {}
    for play in playlists:
        plays[play.stream_info.resolution] = play.uri

    resolution = select_res(plays,quality)
    print(f"Selected resolution : {resolution[0]}x{resolution[1]}")
    murl = plays[resolution]
    
    if not os.path.exists(path):
        os.makedirs(path)
    full_path = os.path.join(path, filename)

    fetch = m3u8.load(murl,headers=headers).segments
    segments = [seg.uri for seg in fetch]
    
    base = os.path.splitext(filename)[0]

    counter = 1
    while os.path.exists(full_path):
        filename = f"{base}_{counter}.ts"
        full_path = os.path.join(path, filename)
        counter += 1

    with open(full_path, 'wb') as f:
        # Download each segment and write it to the output file
        for segment_uri in tqdm(segments, desc="Downloading", unit="iB"):
            segment_url = segment_uri if segment_uri.startswith('http') else url.rsplit('/', 1)[0] + '/' + segment_uri
            response = requests.get(segment_url,headers=headers)
            f.write(response.content)

    print(f"Download completed: {full_path}")


def Engine_http(url:str,path,headers={},name=None):

    
    response = requests.get(url,headers=headers,stream=True)
    response.raise_for_status() 

    if name == None:
        if 'Content-Disposition' in response.headers:
            header = response.headers['Content-Disposition']
            filename = header.split('filename=')[1].strip('"')
        else:
            filename = os.path.basename(unquote(urlparse(url).path))
    else: filename = name

    url_extension = os.path.splitext(unquote(urlparse(url).path))[1]
    if not os.path.splitext(filename)[1]:
        filename += url_extension

    full_path = os.path.join(path, filename)
    base, ext = os.path.splitext(filename)
    
    counter = 2
    while os.path.exists(full_path):
        filename = f"{base}_{counter}{ext}"
        full_path = os.path.join(path, filename)
        counter += 1
    
    temp_path = full_path+'.temp'
    temp_file_size = 0
    if os.path.exists(temp_path):
        temp_file_size = os.path.getsize(temp_path)
    headers['Range'] = f'bytes={temp_file_size}-'
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))

    # Write the file to the custom path with progress bar
    if temp_file_size<total_size:
        with open(temp_path, 'wb') as file, tqdm(
            desc=filename,
            total=total_size,
            initial=temp_file_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                size = file.write(chunk)
                bar.update(size)
    
    os.rename(temp_path,full_path)
    print(f"File downloaded: {full_path}")
