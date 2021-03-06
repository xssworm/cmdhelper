__author__ = 'shenyubao'

import pickle
import os
import re
import sys
import urllib2,urllib,urllib2_file
from hashlib import md5

SECRET = "fc967we161f7d898ad257d62407373"
class CmdHelper:
    path = os.path.expanduser("~")+"/.cmdhelper"
    config = {}
    entites = []

    def __init__(self):
        self.load()
        pass

    def list(self):
        for i in range(len(self.entites)):
            print "[%3d] %-12s: %s" % (i+1,self.entites[i]["id"],self.entites[i]["value"])
        pass

    def list_config(self):
        for (k,v) in self.config.items():
            print "%-10s:%s" % (k,v)
        pass

    def get(self,id):
        is_num  = False
        command = ""
        if(re.match("^\d$",id)):
            is_num = True
        if(is_num):
            id = int(id) - 1
            command = self.entites[id]
        else:
            for i in range(len(self.entites)):
                if(self.entites[i]["id"] == id):
                    command = self.entites[i]
        return command
        pass

    def set(self,id,value,type="c"):
        is_exist = False
        for i in range(len(self.entites)):
            if(self.entites[i]["id"] == id):
                is_exist = True
                print("key replaces")
                self.entites[i]["value"] = value
                break

        if(not is_exist):
            self.entites.append({"id":id,"value":value,"type":type})

        self.save()
        pass

    def mark(self,id):
        self.set(id,os.getcwd(),"d")
        pass

    def delete(self,id):
        is_num = False
        if(re.match("^\d*$",id)):
            is_num = True

        if(is_num):
            real_id = int(id) - 1
            if(len(self.entites)  > real_id):
                del self.entites[real_id]
        else:
            for i in range(len(self.entites)):
                if(self.entites[i]["id"] == id):
                    del self.entites[i]
        self.save()

        pass


    def load(self):
        # Check if Config
        if (len(sys.argv) > 2 and sys.argv[1] == "set"):
            return

        # Get uid
        data_path = self.get_data_path()
        if os.path.exists(data_path) == False :
            return
        with open(data_path,'rb+') as f:
            self.entites = pickle.load(f)
        pass

    def save(self):
        data_path = self.get_data_path()
        if os.access(self.path,os.F_OK) == False:
            os.mkdir(self.path)

        with open(data_path,'wb+') as f:
            pickle.dump(self.entites,f)
        pass

    def set_config(self,key,value):
        config_path = "%s/config" % (self.path)
        config = {}
        if os.access(self.path,os.F_OK) == False:
            os.mkdir(self.path)

        if os.path.exists(config_path) :
            with open(config_path,'rb+') as f:
                config = pickle.load(f)

        config[key] = value
        with open(config_path,"wb+") as f:
            pickle.dump(config,f)
            print("Set success")

    def get_data_path(self):
        config_path = "%s/config" % (self.path)

        if os.path.exists(config_path) == False :
            print("Please set uid first(e.g.: ch set uid yubao1)")
            exit()

        with open(config_path,'rb+') as f:
            self.config = pickle.load(f)

        uid = self.config['uid']
        data_path = "%s/%s.data" % (self.path,uid)
        return data_path


    # Push & Pull
    def push(self):
        data_path =  self.get_data_path()
        if os.path.exists(data_path) == False :
            return

        host = self.config['host'] + '/dict/push'
        uid  = self.config['uid']
        pwd  = self.config['pwd']
        encry_pwd = md5(md5(SECRET+pwd).hexdigest() + SECRET).hexdigest()

        values = {'uid':uid,
                'pwd':encry_pwd,
                'upload':open(data_path)}

        try:
            the_page = urllib2.urlopen(host, values).read()
        except:
            print("Please check yout remote host")
            exit()

        print(the_page)


    def pull(self):
        host = self.config['host'] + '/dict/pull'
        uid  = self.config['uid']
        pwd  = self.config['pwd']
        encry_pwd = md5(md5(SECRET+pwd).hexdigest() + SECRET).hexdigest()

        values = {'uid':uid,
                'pwd':encry_pwd}

        try:
            data = urllib2.urlopen(host, values).read()
        except:
            print("Please check yout remote host")
            exit()

        try:
            self.entites = pickle.loads(data)
            self.save()
            print("Update Success")
            self.list()
        except:
            print(data)