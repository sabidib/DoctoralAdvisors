#!/usr/bin/python

from scrapy.selector import Selector;
from optparse import OptionParser;
import sys;
import requests;
import json
import re;



class Node(object):
    def __init__(self,parent):
        self.parent = parent;
        self.children = [];
        self.processed = False;
        self.data = {};

    def addChild(self,node):
        self.children.append(node);
        return True

    def isProcessed(self):
        return self.processed;

    def isThereNextChild(self):
        for child in self.children:
            if(not child.processed):
                return True;
        return False;

    def setAsProcessed(self):
        self.processed = True;
        return True


    def setAsUnprocessed(self):
        self.processed = False;
        return True
    
    def getChildren(self):
        return self.children;
    
    def getParent(self):
        return self.parent;

    def getNextChild(self):
        for child in self.children:
            if(not child.processed):
                return child;
        return None;

    def setAllAsUnprocessed(self):
        self.setAsUnprocessed();
        for child in self.children:
            child.setAllAsUnprocessed();
        return



class DoctoralAdvisor():

    nameAndLinks = "//table[@class='infobox vcard']/tr/th/a[text()='Doctoral advisor']/../../td/a/@* | //table[@class='infobox vcard']/tr/th[text()='Academic advisors']/../td/a/@*";
    prepend ="http://en.wikipedia.org";

    def __init__(self,start_url_of_person,name_of_person):
        self.start_url = start_url_of_person
        self.name = name_of_person;

    def getAdvisorData(self,response):
        nameLink = Selector(text=response.text).xpath(self.nameAndLinks).extract()
        for m in [u'mw-redirect',"new"]:
            try:
                nameLink.remove(m);
            except:
                None;
        nameLinkSorted = [[j,i] for i,j in zip(nameLink[::2], nameLink[1::2])];
        return nameLinkSorted;



    def parseNode(self,response):
        node = response[1];
        response = response[0];

        advisorData = self.getAdvisorData(response);


        #print "\t-------------" + node.data['advisor'] + "----------------"
        if(len(advisorData) == 0):
            node.setAsProcessed();
            return;

        for advisor in advisorData:
            newNode = Node(node);
            newNode.data['advisor'] = advisor[0];
            #print "\t\t-------------" + advisor[0] + " was their advisor ----------------"
            newNode.data['wiki_page'] = self.prepend+advisor[1];
            node.addChild(newNode);

        while(node.isThereNextChild()):
            childNode = node.getNextChild();
            r = requests.get(childNode.data['wiki_page']);
            childNode.setAsProcessed();
            m = [r, childNode];
            self.parseNode(m);
        
        node.setAsProcessed();
        
        if(node.parent == None):
            return;

        return;




    def getAllAncestors(self):
        response = requests.get(self.start_url);

        item = Node(None); 
        advisorData = self.getAdvisorData(response);
        item.data["advisor"] = self.name;           
        item.data["wiki_page"] = self.start_url;

        for advisor in advisorData:
            newNode = Node(item);
            newNode.data['advisor'] = advisor[0];
            newNode.data['wiki_page'] = self.prepend+advisor[1];
            item.addChild(newNode);

        while(item.isThereNextChild()):
            childNode = item.getNextChild();
            r = requests.get(childNode.data['wiki_page']);
            childNode.setAsProcessed();
            m = [r, childNode];
            self.parseNode(m);

        item.setAllAsUnprocessed();
        print "Done!";
        return item;


def printAdvisors(node,d=0):
    while(node.isThereNextChild()):
        child = node.getNextChild();
        print d*"\t" + child.data['advisor'];
        child.setAsProcessed();
        printAdvisors(child,d+1)
    return;

def getDictionaryOfAdvisors(node,dictionary=None,n=0):
    if(dictionary == None):
        dictionary = {"name": node.data['advisor'], "wiki_page": node.data['wiki_page'] ,"advisor" : [] };
    while(node.isThereNextChild()):
        child = node.getNextChild();
        dictionary['advisor'].append({"name": child.data['advisor'], "wiki_page": child.data['wiki_page'] ,"advisor" : [] });
        child.setAsProcessed();
        getDictionaryOfAdvisors(child, dictionary['advisor'][-1],n+1);
    if(n == 0):
        return dictionary;

    return;

def parseArgs(argv):
    parser = OptionParser();
    parser.add_option("-o", "--output", default="", dest="output_file",help="output the file in json format.");
    parser.add_option("-p", "--print", action="store_true", default=False, dest="printData",help="Print the ancestors of person.");
    parser.add_option("-n", "--name", default="", dest="nameOfRoot",help="Name of root scientist.");
    options,args = parser.parse_args(argv);
    return options;



def main(argv):
    url = argv[0]
    options = parseArgs(argv);
    name = options.nameOfRoot

    if(not len(re.findall(r'https?://.*wikipedia.org*\S+', url)) ):
        print "\t" + url 
        print "\t" + "Is an invalid URL.";
        sys.exit(0);

    advisors = DoctoralAdvisor(url,name);
    root = advisors.getAllAncestors();

    if(options.printData):
        print root.data['advisor'] + " advisors were:"
        printAdvisors(root);
    if(options.output_file != ""):
        dictionary = getDictionaryOfAdvisors(root);
        with open(options.output_file, 'wb') as fp:
            json.dump(dictionary, fp)

if __name__ == "__main__":
    main(sys.argv[1:])




