import re,requests,sys,os,time
from typing import Literal,List
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) # to import from grandpa directory
from downloader import downloader
from extractors import Extract


class anime_sama():
    def __init__(self,
                 resolution:Literal['high','mid','low']=None,
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
            self.episode_count = None

    def verify_url(self,url):
        
        if re.match(r"^(https:\/\/)?(www\.)?anime-sama\.fr\/catalogue\/[^\/]+\/[^\/]+\/(vostfr|vf)\/?$",url):  # match - ex: anime-sama.fr/catalogue/example/saison1/vf
            if requests.get(url).status_code==200:
                return url
        if re.match(r"^(https?:\/\/)?(www\.)?anime-sama\.fr\/catalogue\/[^\/]+\/?$",url):
            a = requests.get(url)
            if a.status_code==200:
                web = a.text
                res = re.findall(r'panneauAnime\("([^"]*Saison[^"]*)", "([^"]+)"\);',web)
                dic = {name:url for name,url in res}

                if len(dic)>1:
                
                    count,txt = 1,""
                    for k in dic:
                        txt+=f"{count}. {k}\n"
                        count+=1

                    get = input("Please give the value of the season you want to process :\n"+txt)
                    while not isinstance(get,int) and (get>len(dic) or get<0) :
                        get = input("Wrorng value! Please enter a number corresponding to season's : ")
                    
                else:
                    get = 1

                print(f"Selected the Season {get}.")
                    
                return url.strip('/')+'/'+list(dic.values())[get-1]
    
    def __fetch(self,url):
         
         url = self.verify_url(url)
         if url:
            if 'vostfr' in url or 'vf' in url:  
                if self.language == 'vf' and 'vf' not in url:
                    if requests.get(url.replace('vostfr','vf')).status_code==200:
                        url = url.replace('vostfr','vf') # selects vf
            print('\n'+url)    

            web = requests.get(url).text
            episode_attr = re.search('episodes\.js\?filever=\d+',web).group(0)
            url = url if url[-1]=='/' else url+'/'
            res = requests.get(url+episode_attr).text
            
            urls = re.findall(re.compile(r"https?://[^\s\"']+"),res)

            for i in range(len(self.source)):
                pref_list = [link for link in urls if self.source[i] in link] 
                if pref_list: 
                    print(f"\n{len(pref_list)} {self.language} episodes found from {self.source[i]}!\n")                   
                    return pref_list
            print("Sorry, couldn't find any extractable sources")
            sys.exit()
         
    def validate_range(self, range):
        
        def invalid_range_error():
            print(f"The range format is not correct.\nThe numbers should be between 1 and {self.episode_count}")
            return None

        if range == None:
            return (None, None)

        if isinstance(range, int):
            if range <= self.episode_count:
                return (range - 1, range)
            invalid_range_error()

        if isinstance(range, tuple):

            if range == ():
                return (None,None)
            a, b = range
            if isinstance(a, int):
                if b is None and a <= self.episode_count:
                    return (a - 1, a)
                if isinstance(b, int) and a < b and b <= self.episode_count:
                    return (a - 1, b)
                if b == a and a <= self.episode_count:
                    return (a - 1, a)     
                if b == 'end':
                    return (a - 1, self.episode_count)
            if a == 'start':
                if b == 'end':
                    return (None, None)
                if isinstance(b, int) and b <= self.episode_count:
                    return (0, b)
            invalid_range_error()
        invalid_range_error()
    
    def download(self,url,range=None,name=None,folder:str=None):
        
        pref_list = self.__fetch(url)
        self.episode_count = len(pref_list)
        range = self.validate_range(range)
        pref_list = pref_list[range[0]:range[1]]

         
        path = self.path+'/'+folder if folder else self.path
        
        downloader(pref_list,path=path,name=name,resolution=self.resolution)
        

    def extract(self,url,range=None,mode:Literal['print','txt','return']='print') :

        pref_list = self.__fetch(url)
        self.episode_count = len(pref_list)
        range = self.validate_range(range)
        pref_list = pref_list[range[0]:range[1]]

        
        if mode == 'print':
            for url in pref_list:
                print(Extract(url).extracted) 
        if mode == 'txt':
            exts = [Extract(url).extracted for url in pref_list]
            os.makedirs(self.path,exist_ok=True)
            file = f'{self.path}/{time.time()}.txt'
            for url in exts:
                with open(file,'a+',encoding='utf-8') as f:
                    f.write(url+'\n')
            
            print(f'File generated at {file}')
        if mode == 'return':
            exts = [Extract(url).extracted for url in pref_list]
            return exts
