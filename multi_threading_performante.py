#built for python3 , below modules should be installed  
import requests
from bs4 import BeautifulSoup
import json
import csv
import urllib.parse
import threading
import time

data_queue=[] # main thread collect game name,id and push to the data_queue
id_name_queue=[] # "review_extract" thread(function) pop data data_queue collect all its review, filter them and push to the id_name_queue and "review_writer" pop data from id_name_queue and write them to appropriate csv files.
extraction_completed_flag = False # True if all game ids are  collected (the review are to be collected with the game id)
index=open("index.txt", "a+") # keeps successfully extracted review's game id 
log=open("log.txt", "a+") # for logging error and other important info

def review_extract(t_id): #extract reviews
    while(True):
        try:
            game_id,file_name = id_name_queue.pop(t_id) #each thread can only pop data a particular index to reduce data inconsistency
        except:#empty id_name_queue
            if(extraction_completed_flag): #no data left to be filled , so thread can stop
                print(t_id,"completed") 
                log.write(str(t_id)+"thread completed running\n")
                break
            else:
                print(t_id,"waiting") #wait till main thread fill id_name_queue
                time.sleep(1)    
                continue
        cursor="*"
        URL = "https://store.steampowered.com/appreviews/"+game_id+"?json=1&num_per_page=100&review_type=positive&purchase_type=steam&day_range=92233720368547760000&language=all&cursor=" 
        #https://partner.steamgames.com/doc/store/getreviews for api documentation
        cursor_lst=[]
        cnt = 0
        print('\n',t_id,game_id)
        data_queue.append([game_id,file_name,'id','language','review','num_reviews','votes_up','timestamp_created'])
        try:
            while(cursor!=None):
                if(cursor in cursor_lst):
                    print("Duplicate Cursor")
                    break                     # comment 'break' if you are okay with having duplicate pages/json file and you may end up in a loop
                cursor_lst.append(cursor)
                page = requests.get(URL+urllib.parse.quote_plus(cursor))
                y = json.loads(page.content)
                #https://partner.steamgames.com/doc/store/getreviews for json fields
                for i in y["reviews"]:
                    author= i["author"]
                    p =  int(author['num_reviews'])/int(author['num_games_owned']) if author['num_games_owned']!=0 else 0 # just a probability
                    if(p>=0.1 or int (author['num_reviews'])>40 or len(i['review'])>250):
                        data_queue.append([game_id,file_name,author['steamid'],i['language'],i['review'],author['num_reviews'],i['votes_up'],i['timestamp_created']])
                        cnt+=1 #,i['voted_up'],i['steam_purchase'],author['num_games_owned'], int(author['num_reviews'])/int(author['num_games_owned']) if author['num_games_owned']!=0 else 0 ,i['timestamp_updated']]
                cursor=y['cursor'] #requires to obtain next page
            print('Completed.\nCollected '+str(cnt)+' review(s)\nData written to '+game_id+'.csv')
            data_queue.append([game_id,file_name,"success tag"]) 
            index.write(file_name+","+game_id+","+str(cnt)+"\n") #write successful entries
        except:
            print('Error.\nCollected '+str(cnt)+' review(s)\nData written to '+game_id+'.csv')
            data_queue.append([game_id,file_name,"Error"]) #just a footer in csv denoting data is incomplete.
            log.write("Error in collecting reviews (steam game id):"+game_id+"\n") #write unsuccessful entries
 
def review_writer(): #thread writes reviews to the csv files
    while(True):
        if(data_queue==[]): #empty data_queue
            if(extraction_completed_flag and threading.active_count()<3):  #no data left to be filled ,  threading.active_count()=2 when all review_extract threads are done
                print("write completed")
                log.write("write completed\n")
                break
            else:
                print("write thread waiting, Active threads",threading.active_count()) #wait till  review_extract threads fill data_queue
                time.sleep(1)
        else:
            temp = data_queue.pop(0)
            # header= False if  os.path.exists(temp[0]+":"+temp[1]+'.csv') else ['id','language','review','num_reviews','votes_up','timestamp_created'] ,import os.path
            with open(temp[0]+":"+temp[1]+'.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                # if (header):
                #     writer.writerow(header)
                writer.writerow(temp[2:])

print('Run this in an empty directory to avoid confusions')
tag=input("Enter search tag(Url encoded):")
page_size= int(input("Enter Page Size: "))
t_no = int(input("Enter number of threads(depending on computational and network capacity)"))
start_time = time.time()
log.write("Initiated at:"+str(start_time)+'(s)\n')
n=0
threads = []
tw = threading.Thread(target=review_writer)
tw.start()
for t_id in range(t_no): # creates thread for review extraction
    thread = threading.Thread(target=review_extract,args=[t_id])
    threads.append(thread)
    thread.start()
log.write("Search tag:"+tag +"\n")
cnt=0
while(n<page_size): #starts to find game id for the corresponding search tag
    URL = "https://store.steampowered.com/contenthub/querypaginated/tags/TopSellers/render/?query=&start="+str(n)+"&count=15&cc=IN&l=english&v=4&tag="+tag
    page = requests.get(URL)
    res = json.loads(page.content)["results_html"]
    soup = BeautifulSoup(res, "html.parser")
    for i in soup.findAll("a",class_="tab_item"):
        name = "\""+i.find("div",class_="tab_item_name").text.replace("/","")+"\""
        game_id = i["data-ds-appid"]
        print(name,game_id ,i["href"])
        id_name_queue.append([game_id,name])
        cnt+=1
    n+=15
extraction_completed_flag=True
for t_id in threads:
    t_id.join()
tw.join()
elapsed_time = time.time() - start_time
print("Result genrated in:",elapsed_time)
print(len(id_name_queue), len(data_queue))
log.write("Result genrated in:"+str(elapsed_time)+'(s)\n')
log.write("Collected  reviews of "+str(cnt)+' game(s)\n')
log.write("Data left to be proccessed in Id_stack"+str(len(id_name_queue))+" :"+"Data_queue"+str(len(data_queue))+'\n') #both should be zero
tw.join()
log.close() 
index.close()
