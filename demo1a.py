#! c:\python34\python3
#!/usr/bin/env python
##demo code provided by Steve Cope at www.steves-internet-guide.com
##email steve@steves-internet-guide.com
##Free to use for any purpose
##If you like and use this code you can
##buy me a drink here https://www.paypal.me/StepenCope
"""
Creates multiple Connections to a broker 
and sends and receives messages. Support SSL and Normal connections
uses the loop_start and stop functions just like a single client
Shows number of thread used
"""
import ctypes
import string
import hashlib
from multiprocessing.sharedctypes import Value
from os import kill
import paho.mqtt.client as mqtt
import time
import json
import threading
import multiprocessing
import logging
import random
import desafios
#Note haven't included keys,client_id,client andcname as they are added later in the script

cur_tid = -1
cur_challenge = -1
clients=[
{"init_msg":[],"status":"init","vote_list":[],"leader": False,"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['init_1','vote_1','challenge_1'],"pub_topic":['init_1','init_2','vote_1','vote_2','challenge_1']},#voltar challenge2
{"init_msg":[],"status":"init","vote_list":[],"leader": False,"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['init_2','vote_2','challenge_2'],"pub_topic":['init_2','init_1','vote_2','vote_1','challenge_1']}
]
nclients=len(clients)
message="test message"
listaDesafios = [desafios.Challenge(0, 1)]
out_queue=[] #use simple array to get printed messages in some form of order

def brute(tdata: desafios.Challenge, thread_id, s: multiprocessing.Value, kill_threads: multiprocessing.Value):
    finish=0
    resultado=False
    res = ""
    while(finish==0 and kill_threads.value == 0):

        res = ''.join(random.choices(string.ascii_lowercase +
                                string.digits, k = 7))
        ct=desafios.Challenge(tdata.transactionID,tdata.challenge,seed=str(res))
        
        resultado=ct.check_seed(ct.seed)

        if(resultado):
            break
            
       
    if(resultado):
      #   vars(ct)["clientID"]=clientID
        kill_threads.value = 1
        s.value = res   
        




def on_log(client, userdata, level, buf):
   print(buf)
def on_message(client, userdata, message):
   # time.sleep(1)
   
   if(message.topic=="init_1"):
      msg=str(message.payload.decode("utf-8"))
      print("recebido no topico init_1")
      if msg not in clients[0]["init_msg"]:
         clients[0]["init_msg"].append(msg)
      if(len(clients[0]["init_msg"])==nclients):
         clients[0]["status"]='election'
   elif(message.topic=="init_2"):
      msg=str(message.payload.decode("utf-8"))
      print("recebido no topico init_2")
      if msg not in clients[1]["init_msg"]:
         clients[1]["init_msg"].append(msg)
      if(len(clients[1]["init_msg"])==nclients):
         clients[1]["status"]='election'
   
   elif (message.topic=="vote_1"):
      msg=str(message.payload.decode("utf-8")).split(',')
      # print("recebido no topico vote_1 ",msg)
      vote=msg[-1]
      if(len(clients[0]["vote_list"])<nclients):
         clients[0]["vote_list"].append(int(vote))
      # print('aqui',clients[0]["vote_list"],len(clients[0]["vote_list"]))
      # if(len(clients[0]["vote_list"])==nclients):
      #    total=0
      #    for element in clients[0]["vote_list"]:
      #       total+=int(element)
      #    print("listavotos",clients[0]["vote_list"])
      #    print(total)
   elif (message.topic=="vote_2"):
         msg=str(message.payload.decode("utf-8")).split(',')
         # print("recebido no topico vote_2 ",msg)
         vote=msg[-1]
         if(len(clients[1]["vote_list"])<nclients):
            clients[1]["vote_list"].append(int(vote))
         # print('aqui',clients[1]["vote_list"],len(clients[1]["vote_list"]))
         # if(len(clients[1]["vote_list"])==nclients):
         #    total=0
         #    for element in clients[1]["vote_list"]:
         #       total+=int(element)
         #    print("listavotos",clients[1]["vote_list"])
         #    print(total)
   elif (message.topic=="challenge_1"):
      msg=json.loads(message.payload.decode("utf-8"))
      global cur_tid
      global cur_challenge
      if cur_tid == -1:
         print('received on ppd/challenge ',msg)
         clients[0]["status"]='running'
         # challenge=desafios.Challenge(transactionID=msg["transactionID"],challenge=msg["challenge"],clientID=msg["clientID"])
         # cur_challenge = challenge.challenge
         # cur_tid = int(msg["transactionID"])
         # processes = []
         # manager = multiprocessing.Manager()
         # s = manager.Value(ctypes.c_wchar_p, 'aaa')
         # kill_threads = manager.Value('i', 0)
         # for i in range(10):
         #    p = multiprocessing.Process(target=brute, args=(challenge,i, s, kill_threads))
         #    processes.append(p)
         #    p.start()
               
         # for proc in processes:
         #       proc.join()
         # ct=desafios.Challenge(cur_tid,challenge.challenge,clientID=challenge.clientID,seed=s.value)
         # obj = vars(ct).copy()
         # obj.__delitem__("challenge")
         # client.publish("ppd/seed",json.dumps(obj), qos=2)
         # print("Just published ", obj, " to topic ppd/seed")

   # elif(message.topic=="test2"):
   #    print("recebido no topico test2")
   #    if msg not in clients[1]["init_msg"]:
   #       clients[1]["init_msg"].append(msg)
   #    print(len(clients[1]["init_msg"]))   
   # print(clients[0]["cname"])
   # print('--',client)
   # print(msg)
   # out_queue.append(msg)
def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        for i in range(nclients):
           if clients[i]["client"]==client:
              topic=clients[i]["sub_topic"]
              break
        for j in topic:      
            client.subscribe(j)
    else:
        print("Bad connection Returned code=",rc)
        client.loop_stop()  
def on_disconnect(client, userdata, rc):
   pass
   #print("client disconnected ok")
def on_publish(client, userdata, mid):
   # time.sleep(1)
   print("In on_pub callback mid= "  ,mid)


def Create_connections():
   for i in range(nclients):
      cname="client"+str(i)
      t=int(time.time())
      client_id =cname+str(t) #create unique client_id
      client = mqtt.Client(client_id)             #create new instance
      clients[i]["client"]=client 
      clients[i]["client_id"]=client_id
      clients[i]["cname"]=cname
      broker=clients[i]["broker"]
      port=clients[i]["port"]
      try:
         client.connect(broker,port)           #establish connection
      except:
         print("Connection Failed to broker ",broker)
         continue
      
      #client.on_log=on_log #this gives getailed logging
      client.on_connect = on_connect
      client.on_disconnect = on_disconnect
      #client.on_publish = on_publish
      client.on_message = on_message
      client.loop_start()
      while not client.connected_flag:
         time.sleep(0.05)

def check_state():
   count=0
   for i in range(nclients):
      if(clients[i]['status']=='election'):
         count+=1
      else: 
         break
   if(count==nclients):
      for j in range(nclients):
         print(clients[j]["client_id"] +" " + clients[j]['status'])
      return 1
   else:
      return 0

def election():
   count=0
   for i in range(nclients):
      if(len(clients[i]['vote_list'])==nclients):
         count+=1
      else: 
         break
   if(count==nclients):
      total=0
      for element in clients[0]["vote_list"]:
         total+=element
      print("listavotos 0",clients[0]["vote_list"])
      print("listavotos 1",clients[1]["vote_list"])
      print(total%10)
      clients[total%10]["leader"]=True
      return 2
   else:
      return 1


mqtt.Client.connected_flag=False #create flag in class
no_threads=threading.active_count()
print("current threads =",no_threads)
print("Creating  Connections ",nclients," clients")

   
Create_connections()
state ="init"
print("All clients connected ")
time.sleep(5)
#

no_threads=threading.active_count()
print("current threads =",no_threads)
print("Publishing ")
Run_Flag=True
estado=1
try:
   while Run_Flag:
      i=0
      # estado=check_state()
      if (estado==0):
         for i in range(nclients):
            client=clients[i]["client"]
            pub_topic=clients[i]["pub_topic"]
            # counter=str(count).rjust(6,"0")
            msg="client "+ str(i) + " "+clients[i]["client_id"]
            if client.connected_flag:
               for j in pub_topic[:nclients]:
                  print('? ',j)
                  client.publish(j,msg)
                  time.sleep(0.1)
               print("publishing client "+ str(i))
               print('--',clients[i]['status'])
            i+=1
      elif(estado ==1):
         estado=election()
         for i in range(nclients):
            client=clients[i]["client"]
            pub_topic=clients[i]["pub_topic"]
            vote=random.randint(0, 1)
            msg="client"+ str(i) + ","+ clients[i]["client_id"]+","+str(vote)
            if client.connected_flag:
               for j in pub_topic[nclients:2*nclients]:
                  # print('! ',j)
                  client.publish(j,msg)
                  print("publish on"+j+' '+msg)
                  time.sleep(0.1)
               # print("publishing client "+ str(i))
               # print(clients[i]['status'])
            i+=1
      elif(estado ==2):
         for i in range(nclients):
            client=clients[i]["client"]
            pub_topic=clients[i]["pub_topic"]
            if(clients[i]["leader"]==True):
               listaDesafios[-1].clientID=clients[i]["client_id"]
               for j in pub_topic[2*nclients:]:   
                  client.publish(j, json.dumps(vars((listaDesafios[-1]))))
                  print("Just published ", json.dumps(vars((listaDesafios[-1]))), " to topic "+ j) 
                  print(clients[i]["client_id"])
      time.sleep(1)#now print messages
      # print("queue length=",len(out_queue))
      # for x in range(len(out_queue)):
      #    print(out_queue.pop())
      # count+=1
      #time.sleep(5)#wait
except KeyboardInterrupt:
   print("interrupted  by keyboard")

#client.loop_stop() #stop loop
for client in clients:
   client.disconnect()
   client.loop_stop()
#allow time for allthreads to stop before existing
time.sleep(10)


