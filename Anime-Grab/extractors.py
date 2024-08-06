import requests,re

class Extract():
    def __init__(self,url:str,quality=None) -> None:
        
        self.url = url
        self.quality = quality
        self.extracted = None
        self.name = None
        self.misc = None

        if 'video.sibnet.ru' in url:
            if re.match(r'^https:\/\/video\.sibnet\.ru\/shell\.php\?videoid=\d+$',url):
                self.sibnet_extract()
        elif 'sendvid.com' in url: 
            if re.match(r'^https:\/\/sendvid\.com\/embed\/[a-zA-Z0-9]+$',url):
                self.sendvid_extract()
        elif 'yourupload.com' in url:
            if re.match(r'^https:\/\/www\.yourupload\.com\/embed\/[a-zA-Z0-9]+$',url):
                self.yourupload_extract()
        elif 'vidmoly.to' in url:
            if re.match(r'^https:\/\/vidmoly\.to\/embed-[a-zA-Z0-9]+\.html$',url):
                self.vidmoly_extract()
        elif 'vk.com' in url:
            if re.match(r'^https:\/\/vk\.com\/video_ext\.php\?oid=\d+&id=\d+$',url):
                self.vk_extract()
        else:
            print('Invalid url syntax or Host not supported')
            return None

    def sibnet_extract(self)->str:

        """
        Tries to extract direct watch or download link from Sibnet.ru

        PARAMS:
            url (str) : Sibnet video url [ex: https://video.sibnet.ru/shell.php?videoid=5244555 ]
        RETURNS:
            str : Direct https download link of the video
        """
        web = requests.get(self.url).text
        vid = re.findall(r'player\.src\(\[\{src: ["\']([^"\']+)["\']',web)[0] # find the specific video url
        nom = re.search(r'<meta property="og:title" content="([^"]*)"/>', web).group(1)
        req = requests.head(f'https://video.sibnet.ru{vid}',headers={'referer':self.url},allow_redirects=True) # generate the download url
        self.extracted = req.url
        self.name = nom

    def sendvid_extract(self)->str:

        """
        Tries to extract direct watch or download link from Sendvid.com

        PARAMS:
            url (str) : Sendvid embedded video url [ex: https://sendvid.com/embed/j7iv1ohf ]
        RETURNS:
            str : Direct https download link of the video
        """

        web = requests.get(self.url).text
        vid = re.search(r'<meta property="og:video" content="([^"]+)"', web).group(1)
        self.extracted = vid
        
        

    def yourupload_extract(self)->tuple:

        """
        Tries to extract direct watch or download link from yourupload.com

        PLEASE_NOTE : 
        The download link may not work without appropriate referer.
        As there is no way to define headers in the url, please 
        use curl, wget or a manager to download. 


        PARAMS:
            url (str) : yourupload embedded video url [ ex: https://www.yourupload.com/embed/GOj8Kt1t37s5 ]
        RETURNS:
            new (str) : Direct https download link of the video
            ref (str) : Referer to put in the header
        """


        web = requests.get(self.url.replace('embed','watch')).text
        fid = re.search(r'file=(\d+)', web).group(1)
        ref = f"https://www.yourupload.com/download?file={fid}"
        web2 = requests.get(ref).text
        token = re.search(r'data-url="([^"]+)"', web2).group(1).replace('&amp;','&') # /download?file=4941760&sendFile=truetoken=ac6d
        new = f"https://www.yourupload.com{token}"
        
        self.extracted = new
        self.misc = ref


    def vidmoly_extract(self)->list:

        """
        Tries to extract m3u8 from Vidmoly.to

        PARAMS:
            url (str) : Vidmoly embedded video url [ex: https://vidmoly.to/embed-zj4og0qhkgmx.html ]
        RETURNS:
            list : Parsed master.m3u8 of the video
        """

        headers = {
        'Sec-Fetch-Dest': 'iframe',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer':'https://vidmoly.to/',
    }

        web = requests.get(self.url,headers=headers).text
        vid = re.search(r'file:"([^"]+)"', web)
        while not vid:
            vid = re.search(r'file:"([^"]+)"', requests.get(self.url,headers=headers).text)
        self.extracted = vid.group(1)
        self.misc = headers


    def vk_extract(self):

        """
        Tries to extract m3u8 from Vk.com

        PARAMS:
            url (str) : Vk video url [ex: https://vk.com/video_ext.php?oid=755747641&id=456240670 ]
        RETURNS:
            tuple : (direct download link, http-header)
        """
         
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }

        web = requests.get(self.url,headers=headers).text
        
        if self.quality == 'high' or self.quality==None:
            vid = re.search(r'"url1080":"(.*?)"',web)
        elif self.quality == 'medium':
            vid = re.search(r'"url720":"(.*?)"',web)
        elif self.quality == 'low':
            vid = re.search(r'"url480":"(.*?)"',web)
        else:
            vid = None
        
        if vid:
            self.extracted = vid.group(1).replace('\\','')+'&video'
            self.misc = headers
        print("No match with given quality range. Try another ")
