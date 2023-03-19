# Focused-Crawl-Search-Engine

 Implement a simple search engine using web pages extracted from focused crawl. Seeds URL includes Wiki and Uncyclopedia. 
 https://en.wikipedia.org/  
 https://en.uncyclopedia.co/
 
## Basic Idea for Web Crawl

 BFS Ideal:  Implement a single-threaded crawler to crawl the web with two parameters: number of links and depth (levels).
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
        
        numberofLinks = len(curLinks)
        
        for eachURL in curLinks:
            q.append([eachURL,depth])
        
        if isTopics(curText) == True:
            es.index(curURL)
            
        //Extract around 20,000 unique links
        if countDocuments() > 20001:
            break
   
   
    depth += 1
 
 ``` 
## Build a Search Engine based on Elasticsearch, BackEnd Flask

1. Install Elasticsearch: Download and install Elasticsearch from the official website.

2. Plan the data structure: Define the data structure of the documents. 

3. Index data: Index data by creating documents with unique identifiers and mapping each field with its corresponding data type.

4. Define the search query: Determine the search query parameters such as the fields to search, query type, and ranking criteria.

5. Query Elasticsearch: Use the Elasticsearch API to query the index based on the search query parameters.

6. build a web application to display results: Display the search results on a search page or application, including options for sorting and filtering the results.
