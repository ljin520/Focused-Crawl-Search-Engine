import heapq
import json
import json
import socket
import requests
import urllib.request
import collections
import re
import pickle
import nltk
import urllib.robotparser as robotparser
import time, datetime
from nltk.tokenize import word_tokenize
from lxml import etree
from nltk.stem import SnowballStemmer
from elasticsearch import Elasticsearch, helpers 


from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin,urlunparse,  urlsplit, urlunsplit



snowball = SnowballStemmer('english')
es = Elasticsearch(hosts=["http://127.0.0.1:9200"])
robotcheckers = {}


def keywords_related(text):
        token_arr = set()
        keywords = ['typhoon','submarine volcano','marine', 'disaters', 'maritime','sink','sewol','shipwreck','accident',]
        text = text.lower()
        tokens = word_tokenize(text)

        for token in tokens:
                stemmed = snowball.stem(token)
                token_arr.add(stemmed)

        for each in keywords:
                if each in token_arr:
                        return True
        return False

def normalization(url):
        if not url.startswith("http"): #
                url=urljoin("http://",url)
        if url.endswith(":80"):
                url = url[:-3]
        if url.endswith(":443"):
                url = url[:-4]
        if '#' in url:
                url = url.split('#',1)[0]

        parsed = list(urlparse(url)) 
        parsed[2] = re.sub("/{2,}", "/", parsed[2])
        cleaned = urlunparse(parsed)
        cleaned= resolve_url_helper(cleaned)
        idx = len(cleaned) - cleaned[::-1].index('/')
        back = cleaned[:idx].lower()
        frnt = cleaned[idx:]
        return back + frnt

def resolve_url_helper(url):
        parts = list(urlsplit(url))
        segments = parts[2].split('/')
        segments = [segment + '/' for segment in segments[:-1]] + [segments[-1]]
        resolved = []
        for segment in segments:
                if segment in ('../', '..'):
                        if resolved[1:]:
                                resolved.pop()
                elif segment not in ('./', '.'):
                        resolved.append(segment)
        parts[2] = ''.join(resolved)
        return urlunsplit(parts)



def countDocumentaions(index):
        es.indices.refresh(index)
        return int(es.cat.count(index, params={"format": "json"})[0]['count'])


def update_PageGraph(curr_url, outlinks):
        global PageGraph
        for outlink in outlinks:
                if outlink not in PageGraph:
                        PageGraph[outlink] = [curr_url]
                PageGraph[outlink].append(curr_url)
                        

PageGraph = {}
#seed_urls = ['https://en.wikipedia.org/wiki/Main_Page']
seed_urls = ['https://en.uncyclopedia.co/wiki/Main_Page']
#seed_urls = ['https://en.uncyclopedia.co/wiki/Main_Page','https://en.uncyclopedia.co/wiki/Small_Text','https://en.uncyclopedia.co/wiki/%27','https://en.uncyclopedia.co/wiki/Portal:Portals']
dq = collections.deque()
unsorted_queue = []
visited = set()
for seed in seed_urls:
        dq.appendleft(( seed, 0))

wiki = "https://en.wikipedia.org"
uncyclopedia = "https://en.uncyclopedia.co"
text = ''
count = 0
robotcheckers = {}
MAX_CRAWL = 30000


def web_crawl():
        start = datetime.datetime.now() 
        print('start: %s' % datetime.datetime.now())
        
        while dq:
                
                
                q_start = datetime.datetime.now()
                outlinks = set()
                time_used = datetime.datetime.now() - start 
                print('Time used: %s' % time_used)

                whole_text =''
                curURL = dq.pop()    #[URL,Deepth]

                topicSet = set()
                topic = ''
                for word in curURL[0].split("/")[-1].split("_"):
                        topicSet.add(word)
                        topic += word + " "
                        
                flag = False
                html = requests.get(curURL[0])
                soup = BeautifulSoup(html.text, 'lxml')
                depth = curURL[1]
                content = soup.find('div', {'id': 'mw-content-text'}).find_all('a', {'href': re.compile("^/wiki")})
                print(len(content))
                soup_time = datetime.datetime.now() - q_start

                # start to record the text related to the current context
                for paragragh in soup.find_all('p'):
                        curStringWords = paragragh.text
                        if flag == False:
                                for word in topicSet:
                                        if word in curStringWords:
                                                flag = True
                        else:
                                whole_text += curStringWords + "\n"

                
                if 'html' not in html.headers['content-type']:
                        tempStr1 = '- not html type!' + '\n'
                        time.sleep(0.5)
                        continue

                        
                canonical_start  = datetime.datetime.now()
                
                for link in content:
                        normalizatedURL = normalization(urljoin(curURL[0], link.get('href')))
                        outlinks.add(normalizatedURL)
                                
                normalization_time = datetime.datetime.now() - canonical_start

                print('normalization time: %s' % normalization_time)

                for link in outlinks:
                        if link not in unsorted_queue and link not in visited:
                                unsorted_queue.append(link)
                                dq.insert(0, (link, depth+1))
                                        
                inlink_start = datetime.datetime.now()

                for outlink in outlinks:
                        if outlink not in PageGraph:
                                PageGraph[outlink] = []
                        PageGraph[outlink].append(curURL[0])

                visited.add(curURL[0])
                inlink_time = datetime.datetime.now() - inlink_start
                print('construct inlink time: %s' % inlink_time)

                tempStr = ' outlinks '+ str(len(outlinks))+ ' deque '+str(len(dq))+' queue '+ str(len(unsorted_queue))+' visited_links '+str(len(visited))
                print(tempStr, end='\n') 

                print(unsorted_queue)
                print(len(dq),"-----------")
                if(len(dq) == 0):
                        print(unsorted_queue)
                        print('\n --Deque used up. Now adding new tuples and sorting\n')
                        output.write('\n --Deque used up. Now adding new tuples and sorting\n') 
                        sort_start = datetime.datetime.now()
                        tmp_q = collections.deque
                        for link in unsorted_queue:
                                if link not in tmp_q:
                                        heapq.heappush(tmp_q, ([len(PageGraph[link]), link]))
                        while tmp_q:
                                tmp_tupple = heapq.heappop(tmp_q)
                                dq.append((tmp_tupple[1], depth+1))
                        unsorted_queue.clear()
                        sort_time = datetime.datetime.now() - sort_start
                        print('sort time: %s' % sort_time)

                print(soup.title.string)
                es_start = datetime.datetime.now()
                inlink_list = []
                if curURL[0] in PageGraph:
                        inlink_list = PageGraph[curURL[0]]


                if not keywords_related(whole_text):
                        tempStr1 = " irrelevant page" + '\n'
                        continue

                outlink_list = []
                for each in outlinks:
                        outlink_list.append(each)
                        
                # build index into ES
                try:
                        es.index("mywebsites",{
                                'topic':topic,
                                'url': curURL[0],
                                'depth':depth,
                                'numberofoutlinks':len(outlinks),
                                'numberofinlinks':len(inlink_list),
                                'content': whole_text,
                                'inlinks': outlink_list,
                                'outlinks': outlink_list[:50],
                                })
                except KeyError:
                        print("cur Error")
                        
                        
                es_time = datetime.datetime.now() - es_start
                print('es time: %s' % es_time)
                print('oulinks length', len(outlinks))

                #set a limit to control time

                if countDocumentaions('mywebsites') > 30001:
                        break
                
                time.sleep(0.2)
                
web_crawl()
