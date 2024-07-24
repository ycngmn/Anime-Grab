import re,requests,sys,os,time
from typing import Literal,List,Optional
import downloader
import extractors


class anime_sama():
    def __init__(self,
                 url:str = None,
                 resolution:Optional[Literal['high','mid','low']]=None,
                 preferred_source_order:List[Literal['sibnet.ru','sendvid.com','yourvid.com','vk.com','vidmoly.to']]=['sibnet.ru','sendvid.com','yourvid.com','vk.com','vidmoly.to'],
                 preferred_version:Literal['vf','vo']='vf',
                 path_to_download=r'./aniloads/anime-sama',
                 ) -> None:
            

            self.host = 'https://anime-sama.fr/'
            self.supported = ['sibnet.ru','sendvid.com','yourvid.com','vk.com','vidmoly.to']
            self.source = preferred_source_order+[source for source in self.supported if source not in preferred_source_order]
            self.language = preferred_version
            self.resolution =  resolution
            self.path = path_to_download.strip('/')
            os.makedirs(path_to_download,exist_ok=True)
            self.episode_count = None

    def verify_url(self,url):
        if re.match(r"https://anime-sama\.fr/catalogue/.*",url):
            if requests.get(url).status_code==200:
                return url
        return None
    
    def __fetch(self,url):
         
         url = url if url[-1]=='/' else url+'/'
         if self.verify_url(url):
            if 'vostfr' in url or 'vf' in url:  
                if self.language == 'vf' and 'vf' not in url:
                    if requests.get(url.replace('vostfr','vf')).status_code==200:
                        url = url.replace('vostfr','vf') # selects vf
                    
            web = requests.get(url).text
            episode_attr = re.search('episodes\.js\?filever=\d+',web).group(0)
            res = requests.get(url+episode_attr).text
            
            urls = re.findall(re.compile(r"https?://[^\s\"']+"),res)

            for i in range(len(self.source)):
                pref_list = [link for link in urls if self.source[i] in link] 
                if pref_list:                    
                    return pref_list
                else:
                     print("Sorry, couldn't find any extractable sources")
                     sys.exit()
         
    def validate_range(self,range):
        
        if isinstance(range,int) and range<=self.episode_count:
            return (range-1,range)
        elif isinstance(range,tuple):
            a,b = range
            if isinstance(a,int):
                if b == None and a<=self.episode_count:
                    return (a-1,a)
                if isinstance(b,int) and a<b and b<=self.episode_count:
                    return (a-1,b)
                else:
                    print(f"The range format is not corrent.\nThe numbers should be between 1 and {self.episode_count}")
                    sys.exit()
        elif range == None:
            return (None,None)

        else:
            print(f"The range format is not corrent.\nThe numbers should be between 1 and {self.episode_count}")
            sys.exit()
    
    def download(self,url,range=None,name=None,folder:str=None):
        
        pref_list = self.__fetch(url)
        self.episode_count = len(pref_list)
        range = self.validate_range(range)
        pref_list = pref_list[range[0]:range[1]]

        if folder: path = self.path+f'/{folder}'
        
        downloader(pref_list,path=path,name=name,resolution=self.resolution)
        

    def extract(self,url,range=None,mode:Literal['print','txt']='print') :

        pref_list = self.__fetch(url)
        self.episode_count = len(pref_list)
        range = self.validate_range(range)
        pref_list = pref_list[range[0]:range[1]]

        exts = [sibnet_extract(url)[0] for url in pref_list]

        if mode == 'print':
            for elt in exts:
                print(elt[0])
        else:
            file = f'{self.path}/{time.time()}.txt'
            for url in exts:
                with open(file,'a+',encoding='utf-8') as f:
                    f.write(url+'\n')
            
            print(f'File generated at {file}')

a = anime_sama(preferred_version='vf',preferred_source_order=['sibnet.ru','vk.com'])
print(a.extract('https://anime-sama.fr/catalogue/rent-a-girlfriend/saison1/vostfr/',mode='txt'))