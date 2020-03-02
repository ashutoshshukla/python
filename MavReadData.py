#!/usr/bin/env python
# coding: utf-8

# In[42]:


# ReadLogFiles
import pandas as pd
import json
import csv
import re
import sys

import re
try:
    regX = '(send|onReadData|readData).*sipMgr(UDP|TCP)Socket.*Len|nsMsg|nsAck|(m_payload.*((R|r)eceiverSessionStatus|(v|V)voipSessionInformation|chatSessionInformation|fileTransferSessionInformation|vvoipSessionTransferInformation|outboundSMSMessageRequest)|m_requestLine)|(GET.*channelCreateUrl)|(send websocket frame opcode)|handleChildExit|MSGTYPE_CCS_|sendCallSetupResponseToClient output buffer json|sendCall(Hold|Resume)SuccessRsp|printObject\(ReceiverSessionStatus.cpp:70|buildHttpRequestUrl|(open|close)Socket.*HttpClientWorker|start to parse (MSRP SEND|response|report)'        
    regXC = re.compile(regX)
except:
    print("Invalid regX")
    regXC=None

class ImsLogFormat:
    def __init__(self,time,service,pId,log):
        self.time=time
        self.service=service
        self.pId=pId
        self.log=log
        
ims_log_file = "Downloads/ucassa/sc_logs.log"
"""Read this api will read the document provided"""
#def read_log(ims_log_file, label=None, window="session"):

def readLog(logFile,label,window="sessions"):
    imsLog = open(logFile,errors='ignore')
    offset = 0
    TAG = label
    SVC = TAG
    
    try:
        regexTry = re.compile(regEx)
    except:
        print("Invalid Regex"%regexTry)
        regexTry=None
        
    bagOfSvcLog=[]
    
    try:
        pattern = re.compile(r'<.*' + TAG + '.*')
    except sre_constants.error:
        print("Invalid regex")
        pattern = None

    tagLine = []
    line = None
    
    for text in imsLog:
        #patten as per the label came in; expected label is svcName such as pcscfMgr/WEBGW_SVC/webrtc/REGMGR
        #this procedure is specifcally to idenitfy the processId; as per IMS log expectation is processId will always be
        #3rd value.
        if(pattern):     
            match = pattern.findall(text)
            if match:        
                tagLine = text.split(" ")
                line = tagLine
                pId = tagLine[3].split(":")[0]
                #print(pId)#"""processId identified for the provided service/SVC"""
                TAG = pId #"""pullout all the logs related to service/SVC as per it's pid"""            
                #"""pattern selection to choose and fill containers"""     
                try:
                    pattern_pid = re.compile(r'<.*' + TAG + '.*')
                except sre_constants.error:
                    print("Invalid regex")
                    pattern_pid = None
                    #"""Now Find all the lines belonging to pId"""
                if(pattern_pid):
                    match_pId = pattern_pid.findall(text)        
                    if(match_pId):
                        splitLine = text.split(" ")
                        time=splitLine[0]       
                        logO=ImsLogFormat(time,SVC,pId,match_pId)
                        bagOfSvcLog.append(logO)                        
                    else:
                        print("regex added on particular pId failed")
                else:
                    print("pattern did't match regex for pId")
        else:
            print("pattern did't match regex SVC")
    imsLog.close()
    return bagOfSvcLog
    


if __name__ == "__main__":
#    import argparse
    #parser = argparse.ArgumentParser(description='Create log file analysis')
    #parser.add_argument('--filepath',required=True, help='the path to log')
    #parser.add_argument('--service',required=True, help='service')
    #parser.add_argument('--window',required=False, help='Its optional, if session API implemented', default="session")
    #args = parser.parse_args()
    #readLog(logFile=args.filepath, label=args.service, window=args.window)    
    #this will be learnt as call scenario, webrtc, webGwSvcMgr, pcscfMgr
    procLogList = readLog(ims_log_file,"pcscfMgr")
    for el in procLogList:
        try:
            regXC = re.compile(regX)
        except:
            print("Invalid regX")
            regXC=None
        if(regXC):            
            found = regXC.findall(str(el.log))
            print(el.log)


# In[20]:


## database for storring all the lineInfo for successCases
import sqlite3


xconn = None

def deleteMapTable(db_filename):
    conn = sqlite3.connect(db_filename)
    conn.execute("DROP TABLE IF EXISTS LOG_ID_MAP")    
    conn.close()


def createMapTable(db_filename):
    conn = sqlite3.connect(db_filename)
    #print "xLogIDMapper_createMapTable: Opened database successfully";# -*- coding: utf-8 -*-

    
    conn.execute("Create Table IF NOT EXISTS LOG_ID_MAP        (id INTEGER PRIMARY KEY NOT NULL,       file_name           TEXT    NOT NULL,       func_name           TEXT    NOT NULL,       regex_str           TEXT    NOT NULL,       UNIQUE(file_name, func_name, regex_str))")
    
    conn.commit()
    conn.close()
    
def openMapTable(db_filename):
    global xconn
    xconn = sqlite3.connect(db_filename)
    #print "xLogIDMapper_openMapTable: Opened database successfully";# -*- coding: utf-8 -*-

def finalizeMapTable():
    global xconn
    xconn.commit()

def closeMapTable():
    global xconn    
    xconn.close()



def addLog(file_name, fucn_name, regex_str):
    global xconn
    
    cmd = "INSERT OR IGNORE INTO LOG_ID_MAP (id, file_name, func_name, regex_str) VALUES (NULL, ?, ?, ?)"
    
    xconn.execute(cmd, (file_name, fucn_name, regex_str))
    

def getId(file_name, func_name, regex_str):
    global xconn
   
    cur = xconn.cursor()    
    #print "xLogIDMapper_getId: Opened database successfully";# -*- coding: utf-8 -*-

    #print ("xLogIDMapper_getId: finding for ", file_name, func_name, regex_str)
    cmd = "SELECT id FROM LOG_ID_MAP WHERE file_name=? AND func_name=? AND regex_str=?"
    
    cur.execute(cmd, (file_name, func_name, regex_str))
    
    results = cur.fetchall()
    result = None

    if results:
        #print('xLogIDMapper_getLogId: found = ', results[0][0])
        result = results[0][0]
    cur.close()
    
    return result
    

def getLog(log_id):
    global xconn
    
    curr = xconn.cursor()    

    #print ("xLogIDMapper_getLog: finding log for ", log_id)
    cmd = "SELECT file_name, func_name, regex_str FROM LOG_ID_MAP WHERE id={lid}"
    
    curr.execute(cmd.format(lid=log_id))
    
    results = curr.fetchall()

    #print('xLogIDMapper_getLog: found = ', results)

    curr.close()
    
    return results
    


def printStats():
    global xconn
    
    curr = xconn.cursor()
    
    cmd = "SELECT * FROM LOG_ID_MAP"
    
    curr.execute(cmd)
    
    for row in curr:
        print (row)
    
    curr.close()
    






do_test = 0

if do_test:
    
    deleteMapTable("log_map.db") 
    createMapTable("log_map.db")
    openMapTable("log_map.db")
    
    addLog( "1.c", "func1", "hello")
    addLog( "1.c", "func2", "hello how")
    addLog( "2.c", "func3", "hello how are")
    addLog( "3.c", "func4", "hello (\d+)")
    addLog( "3.c", "func4", "hello (\d+)")

    finalizeMapTable()
    
    
    printStats()
    
    
    print (getId("1.c", "func1", "hello"))
    print (getId("1.c", "func2", "hello how"))
    print (getId("2.c", "func3", "hello how are"))
    print (getId("3.c", "func4", "hello (\d+)"))
    print (getId("3.c", "func4", "hello (\d+) dude"))
    
    closeMapTable()


# In[11]:


import re
regX = '(send|onReadData|readData).*sipMgr(UDP|TCP)Socket.*Len|nsMsg|nsAck|(m_payload.*((R|r)eceiverSessionStatus|(v|V)voipSessionInformation|chatSessionInformation|fileTransferSessionInformation|vvoipSessionTransferInformation|outboundSMSMessageRequest)|m_requestLine)|(GET.*channelCreateUrl)|(send websocket frame opcode)|handleChildExit|MSGTYPE_CCS_|sendCallSetupResponseToClient output buffer json|sendCall(Hold|Resume)SuccessRsp|printObject\(ReceiverSessionStatus.cpp:70|buildHttpRequestUrl|(open|close)Socket.*HttpClientWorker|start to parse (MSRP SEND|response|report)'
matches = []
for line in open('Downloads/ucassa/sc_logs.log'):
    if(re.findall(regX, line)):
        
    


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




