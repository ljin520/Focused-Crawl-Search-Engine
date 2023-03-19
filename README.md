# A first-level heading
## A second-level heading
### A third-level heading

# Focused-Crawl-Search-Engine
 Implement a simple search engine using web pages extracted from focused crawl. Seeds URL is Wiki and Uncyclopedia.
  
##Basic Idea for Web Crawl

-BFS Ideal
 ```
 seeds = [A]
 

q = []
for seed in seeds:
    q.add([q,0])

depth = 0
while q:
    length = len(q)
    for i in range(length):
        curURL,depth = q.pop()
        curLinks =  getAllLinks(curURL)
        curText = getTextofPage(curURL)
            
        for eachURL in curLinks:
            q.append([eachURL,depth])
        
        if isTopics(curText) == True:
            es.index(curURL)

        if countDocuments() > 20001:
            break
        
    depth += 1
 
 ```

