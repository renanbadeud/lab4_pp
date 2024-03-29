from collections import Counter
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

cur_tid = -1
cur_challenge = -1

winner=False

clients=[
{"init_msg":[],"status":"init","election_list":[],"voting_list":[],"leader": False,"running": False,"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['init','election','challenge','ppd/seed']},
{"init_msg":[],"status":"init","election_list":[],"voting_list":[],"leader": False,"running": False,"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['init','election','challenge','ppd/seed']},
{"init_msg":[],"status":"init","election_list":[],"voting_list":[],"leader": False,"running": False,"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['init','election','challenge','ppd/seed']},
{"init_msg":[],"status":"init","election_list":[],"voting_list":[],"leader": False,"running": False,"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['init','election','challenge','ppd/seed']},
{"init_msg":[],"status":"init","election_list":[],"voting_list":[],"leader": False,"running": False,"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['init','election','challenge','ppd/seed']},
{"init_msg":[],"status":"init","election_list":[],"voting_list":[],"leader": False,"running": False,"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['init','election','challenge','ppd/seed']},
{"init_msg":[],"status":"init","election_list":[],"voting_list":[],"leader": False,"running": False,"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['init','election','challenge','ppd/seed']},
{"init_msg":[],"status":"init","election_list":[],"voting_list":[],"leader": False,"running": False,"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['init','election','challenge','ppd/seed']},
{"init_msg":[],"status":"init","election_list":[],"voting_list":[],"leader": False,"running": False,"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['init','election','challenge','ppd/seed']},
{"init_msg":[],"status":"init","election_list":[],"voting_list":[],"leader": False,"running": False,"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['init','election','challenge','ppd/seed']}
]

nclients=len(clients)
listaDesafios = [desafios.Challenge(0, 1)]

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
   time.sleep(1)
   global winner
   global estado
   if(message.topic=="init" and estado==0):
      # print("client",client._client_id)
      msg=str(message.payload.decode("utf-8")).split(',')
      # print("recebido no topico init do client ",client._client_id.decode("utf-8"),msg)   
      for i in range (nclients):
         if(client._client_id.decode("utf-8")==clients[i]['client_id']):   
            break
      if(msg[-1] not in clients[i]['init_msg']):
            clients[i]["init_msg"].append(msg[-1])
            print("client ",client._client_id.decode("utf-8")," ",clients[i]["init_msg"])
      if(len(clients[i]["init_msg"])==nclients):
         clients[i]["status"]='election'
         # print(clients[i]["status"]) 
   
   elif (message.topic=="election" and estado==1):
      msg=str(message.payload.decode("utf-8")).split(',')
      # print("recebido no topico election do client ",client._client_id,msg)
      vote=msg[-1]
      for i in range (nclients):#descubro qual elemento da lista clients tem o id e altero ele
         if(client._client_id.decode("utf-8")==clients[i]['client_id']):   
            break

      if(len(clients[i]["election_list"])<nclients):
         if(vote not in clients[i]['election_list']):
            clients[i]["election_list"].append(int(vote))
            print("client ",client._client_id.decode("utf-8"),"electionlist ",clients[i]["election_list"]) 
         
   elif (message.topic=="challenge"):
      msg=json.loads(message.payload.decode("utf-8"))
      # print("recebido no topico challenge do client",client._client_id,msg)
      for i in range (nclients):#descubro qual elemento da lista clients tem o id e altero ele
         if(client._client_id.decode("utf-8")==clients[i]['client_id']):   
            break
      # print("client ",i,"msg ",msg)
      
      # if(clients[i]['running']==False):
      # print("recebido no topico challenge do client ",client._client_id.decode('utf-8'),msg)
      # clients[i]['running']=True
      clients[i].update(msg)  
      challenge=desafios.Challenge(transactionID=msg["transactionID"],challenge=msg['challenge'],clientID=client._client_id.decode("utf-8"))
      # print(challenge.clientID)
      cur_challenge = challenge.challenge
      cur_tid = int(msg["transactionID"])
      processes = []
      manager = multiprocessing.Manager()
      s = manager.Value(ctypes.c_wchar_p, 'aaa')
      kill_threads = manager.Value('i', 0)
      for i in range(5):
         p = multiprocessing.Process(target=brute, args=(challenge,i, s, kill_threads))
         processes.append(p)
         p.start()

      for proc in processes:
         proc.join()
      ct=desafios.Challenge(cur_tid,challenge.challenge,clientID=client._client_id.decode("utf-8"),seed=s.value)
      obj = vars(ct).copy()
      # print(client._client_id.decode("utf-8")," ",obj)
      obj.__delitem__("challenge")
      client.publish("ppd/seed",json.dumps(obj), qos=2)
      time.sleep(0.5)
      # print(client._client_id," published ", obj, " to topic ppd/seed")

   elif (message.topic=="ppd/seed" and winner==False):
      
      dcd_msg = json.loads(message.payload.decode("utf-8"))
      # print("recebido no topico ppd/seed do client ",client._client_id.decode('utf-8')," ",dcd_msg)
   
      tid = dcd_msg["transactionID"]
      seed = dcd_msg["seed"] 
      
      #checo se desafio nao foi resolvido e se seed é valida
      if listaDesafios[tid].clientID == -1 and listaDesafios[tid].check_seed(seed):   
         for i in range (nclients):#descubro qual elemento da lista clients tem o id e altero ele
            if(clients[i]['client_id']==dcd_msg['clientID']):   
               break

         if(len(clients[i]["voting_list"])<nclients):
            if(client._client_id.decode('utf-8') not in clients[i]['voting_list']):
               clients[i]["voting_list"].append(client._client_id.decode('utf-8'))
               # print("client ",clients[i]['client_id'],"votinglist ",clients[i]["voting_list"])
         
         #checo se todos os clients aceitaram a seed e ainda nao ha vencedor
         if(len(clients[i]['voting_list'])==nclients and winner==False):
            listaDesafios[tid].clientID = dcd_msg["clientID"]
            listaDesafios[tid].seed = seed
            obj = vars(listaDesafios[tid]).copy()
            print(json.dumps(obj))
            # print('winner',clients[i]['client_id'])
            ultimo_desafio = listaDesafios[-1]
            listaDesafios.append(desafios.Challenge(ultimo_desafio.transactionID+1, ultimo_desafio.challenge+1))
            obj = vars(listaDesafios[-1]).copy()
            # print('appended----',json.dumps(obj))
            winner=True
            # for i in range(nclients):
            #    clients[i]['running']=False
            estado=2 #volto ao estado 2 para publicar desafio   
         
      # time.sleep(0.5)
   
def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        for i in range(nclients):
           if clients[i]["client"]==client:
              topic=clients[i]["sub_topic"]
              break
        for j in topic:      
            client.subscribe(j,qos=2)
    else:
        print("Bad connection Returned code=",rc)
        client.loop_stop()  
def on_disconnect(client, userdata, rc):
   pass
   #print("client disconnected ok")
def on_publish(client, userdata, mid):
   print("In on_pub callback mid= "  ,mid)


def Create_connections():
   for i in range(nclients):
         # cname=str(i)
      t=int(time.time()* 1000)
      client_id =str(t) #create unique client_id
      client = mqtt.Client(client_id)             #create new instance
      clients[i]["client"]=client 
      clients[i]["client_id"]=client_id
      # clients[i]["cname"]=cname
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

def check_init_msg():
   time.sleep(1)
   count=0
   for i in range(nclients):
      if(clients[i]['status']=='election'):
         count+=1
      else: 
         break
   if(count==nclients):
      return 1
   else:
      return 0

def election():
   time.sleep(1)
   # print("entrou election")
   count=0
   for i in range(nclients):
      if(len(clients[i]['election_list'])==nclients):
         count+=1
      else: 
         break
   if(count==nclients):
      time.sleep(0.5)
      # print("client 0",clients[0]["vote_list"])
      # print("client 1",clients[1]["vote_list"])
      
      test_list=clients[0]["election_list"]
      res = []
      test_list1 = Counter(test_list) 
      temp = test_list1.most_common(1)[0][1] 
      for ele in test_list:
         if test_list.count(ele) == temp:
            res.append(ele)
         res = list(set(res)) 
      # print("leader",res,len(res))
      
      idx_leader = res[0]
      if (len(res)>1):
         for idx in res:  
               if (idx + int(clients[idx]["client_id"])) > idx_leader :
                     idx_leader = idx
      # print(idx_leader)
      print('leader',clients[idx_leader]["client_id"])   
      clients[idx_leader]["leader"]=True
      return 2
   else:
      return 1


mqtt.Client.connected_flag=False #create flag in class
no_threads=threading.active_count()
# print("current threads =",no_threads)
print("Creating  Connections ",nclients," clients")
Create_connections()
state ="init"
print("All clients connected ")
time.sleep(5)
#
no_threads=threading.active_count()
# print("current threads =",no_threads)
print("Publishing ")
Run_Flag=True
estado=0
try:
   while Run_Flag:
      i=0
      # print(estado)
      if (estado==0): #clients enviam ids aos demais
         estado=check_init_msg()
         for i in range(nclients):
            client=clients[i]["client"]
            msg=str(i) + ","+clients[i]["client_id"]
            if client.connected_flag:
               client.publish('init',msg,qos=2)
               # print("client "+ client._client_id.decode("utf-8")+ " published ", msg, "to topic election")
               time.sleep(1)
               # print(str(i) +" "+ client._client_id.decode("utf-8") + " published on topic init " + "msg: " +msg)
               # print('--',clients[i]['status'])
            i+=1
      elif(estado ==1): #elege lider
         estado=election()
         for i in range(nclients):
            client=clients[i]["client"]
            vote=random.randint(0, nclients-1)
            msg=clients[i]["client_id"]+","+str(vote)
            if client.connected_flag:
               client.publish('election',msg,qos=2)
               # print("client "+ client._client_id.decode("utf-8")+ " published ", msg, "to topic election")
               # print("publish on "+j+' '+msg)
               time.sleep(1)
               # print("publishing client "+ str(i))
               # print(clients[i]['status'])
            i+=1
      elif(estado ==2): #submete challenge
         time.sleep(0.5)
         for i in range(nclients):
            if(clients[i]["leader"]==True):
               break
            i+=1   
         client=clients[i]["client"]
         winner=False  
         client.publish("challenge", json.dumps(vars((listaDesafios[-1]))),qos=2)
         print("Leader "+ client._client_id.decode("utf-8")+ " published ", json.dumps(vars((listaDesafios[-1]))), "to topic challenge")
         time.sleep(1)
         estado=3
         # print("client "+str(i) +" "+ client._client_id.decode("utf-8") + " published on topic challenge " + "msg: " +json.dumps(vars((listaDesafios[-1]))))
         # print("Just published ", json.dumps(vars((listaDesafios[-1]))), " to topic "+ j) 
         # print(clients[i]["client_id"])
            
               
      elif(estado ==3): #aguarda para retornar ao estado 2 submeter novo challenge
         time.sleep(1)
         
         
except KeyboardInterrupt:
   print("interrupted  by keyboard")

#client.loop_stop() #stop loop
for client in clients:
   client.disconnect()
   client.loop_stop()
#allow time for allthreads to stop before existing
time.sleep(10)


