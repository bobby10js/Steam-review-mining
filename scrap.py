import requests
from bs4 import BeautifulSoup
import json
import csv
import urllib.parse
import _thread

def review_extract(game_id,file_name):
    cursor="*"
    URL = "https://store.steampowered.com/appreviews/"+game_id+"?json=1&num_per_page=100&review_type=positive&purchase_type=steam&day_range=92233720368547760000&language=all&cursor=" #filter=recent,updated day_range=92233720368547760000
    cursor_lst=[]
    with open(file_name+'.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        header= ['id','language','review','num_reviews','votes_up','timestamp_created']
        writer.writerow(header)
        cnt = 0
        while(cursor!=None):
            if(cursor in cursor_lst):
                print("Duplicate Cursor")
                break                     # comment 'break' if you are okay with having duplicate pages/json file
            cursor_lst.append(cursor)
            page = requests.get(URL+urllib.parse.quote_plus(cursor))
            y = json.loads(page.content)
            for i in y["reviews"]:
                author= i["author"]
                p =  int(author['num_reviews'])/int(author['num_games_owned']) if author['num_games_owned']!=0 else 0
                if(p>=0.1 or int (author['num_reviews'])>40 or len(i['review'])>250):
                    writer.writerow([author['steamid'],i['language'],i['review'],author['num_reviews'],i['votes_up'],i['timestamp_created']])
                    cnt+=1 #,i['voted_up'],i['steam_purchase'],author['num_games_owned'], int(author['num_reviews'])/int(author['num_games_owned']) if author['num_games_owned']!=0 else 0 ,i['timestamp_updated']]
            cursor=y['cursor']
        print('\n',game_id+': Completed.\nCollected '+str(cnt)+' review(s)\nData written to '+game_id+'.csv')
        writer.writerow(["success tag"])


page_size= int(input("input page size"))
n=0
while(n<page_size):
    URL = "https://store.steampowered.com/contenthub/querypaginated/tags/TopSellers/render/?query=&start="+str(n)+"&count=15&cc=IN&l=english&v=4&tag=Interactive%20Fiction"
    page = requests.get(URL)
    res = json.loads(page.content)
    soup = BeautifulSoup(res["results_html"], "html.parser")
    cnt=0
    for i in soup.findAll("a",class_="tab_item"):
        name = "\""+i.find("div",class_="tab_item_name").text+"\""
        gameid = i["data-ds-appid"]
        print(name,gameid ,i["href"])
        _thread.start_new_thread( review_extract, (gameid,name) )
        cnt+=1
    print(cnt)
    n+=15
