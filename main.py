import os
from espeak import espeak
from tkinter import *
from bs4 import BeautifulSoup
import tkinter as tk
import urllib
import re, collections
import pickle


lis=map(chr,range(97,123))
lis=list(lis)
lis.append("'")

class TrieNode:
    def __init__(self):
        self.val = None
        self.pointers={}
        self.end=0


class Trie:

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        self.recInsert(word, self.root)
        return

    def recInsert(self, word, node):
        if word[:1] not in node.pointers:
            newNode=TrieNode()
            newNode.val=word[:1]
            node.pointers[word[:1]]=newNode
            self.recInsert(word, node)
        else:
            nextNode = node.pointers[word[:1]]
            if len(word[1:])==0:
                node.end=1
                return
            return self.recInsert(word[1:], nextNode)

    def search(self, word):
        if len(word)==0:
            return False
        return self.recSearch(word,self.root)

    def recSearch(self, word, node):
        if word[:1] not in node.pointers:
            return False
        else:
            nextNode = node.pointers[word[:1]]
            if len(word[1:])==0:
                if nextNode.end == 1:
                    return True
                else:
                    return False
            return self.recSearch(word[1:],nextNode)

    def startsWith(self, prefix):
        if len(prefix)==0:
            return True
        return self.recSearchPrefix(prefix,self.root)

    def recSearchPrefix(self, word, node):
        if word[:1] not in node.pointers:
            return False
        else:
            if len(word[1:])==0:
                return True
            nextNode = node.pointers[word[:1]]
            return self.recSearchPrefix(word[1:],nextNode)
            
    
    def findAll(self,node,word,sugg):
    	for c in lis:
    		if c in node.pointers:
    			if node.pointers[c].end==1:
    				sugg.append(word+str(c))
    			self.findAll(node.pointers[c],word+str(c),sugg)
    	return
    	        

    def didUMean(self,word,sugg):
    	if self.startsWith(word):
    		top=self.root
    		for c in word:
    			top=top.pointers[c]
    		self.findAll(top,word,sugg)
    	else:
    		return
    	         

'''
trie=Trie()

file = open('words.txt','r')
dict=file.readlines()
for words in dict:
	trie.insert(words.lower())
file.close()

pickle.dump(trie,open("save.p", "wb"))
'''


trie = pickle.load(open( "save.p", "rb"))

class EditDist:
	def __init__(self):
		pass


def util(word):
	os.system('espeak -s 120 '+word)
	word=word.lower()
	if trie.search(word):
		print("Found")
		urlStr='http://www.dictionary.com/browse/'+word+'?s=t'
		url=urllib.request.urlopen(urlStr)
		content = url.read()
		soup = BeautifulSoup(content)
		for script in soup(["script", "style"]):
		    script.extract()
		text = soup.get_text()
		lines = (line.strip() for line in text.splitlines())
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
		res=[chunk for chunk in chunks if chunk]

		try:
			res=res[res.index('Share')+1:]
			res=res[res.index('Share')+1:]
		except ValueError:
			pass
	
		try:
			res=res[:res.index('About')]
		except ValueError:
			pass
	
		try:
			nearbyInd=res.index('Nearby words for '+word)
			nearbyWords=res[nearbyInd:]
			res=res[:nearbyInd]
		except ValueError:
			pass	
	
		try:
			relatedInd=res.index('Related Words')
			relatedWords=res[relatedInd:]
			res=res[:relatedInd]
		except ValueError:
			pass
		
		try:
			res=res[:res.index('Word Value for '+word)]
		except ValueError:
			pass
		
		try:
			difficulty=res[-1]
			res=res[:-5]
		except ValueError:
			pass				
	
		for i in range(len(res)):
			print(i,res[i])
		text = '\n'.join(chunk for chunk in res)

		#print(text)
	
	else:
		print("Not Found\nDid You Mean:")
		os.system("espeak -s 120 'Not Found. Did You Mean:'")
		sugg=[]
		trie.didUMean(word,sugg)
		sugg.sort(key = lambda s: len(s))
		text = '\n'.join(chunk for chunk in sugg[:min(len(sugg),10)])
		
	return text

def showSearchResults():
	key=entry.get()
	text=util(key)
	content_text.insert('1.0',text)

if __name__ == '__main__':
	PROGRAM_NAME="Dictionary"

	root = Tk()
	root.geometry('500x500')
	root.title(PROGRAM_NAME)
	entry = Entry(root, width=10)       
	entry.pack()
	button = Button(root, text='Search', width=25, command=showSearchResults)
	button.pack()

	content_text = Text(root, wrap='word')
	content_text.pack(expand='yes', fill='both')
	scroll_bar = Scrollbar(content_text)
	content_text.configure(yscrollcommand=scroll_bar.set)
	scroll_bar.config(command=content_text.yview)
	scroll_bar.pack(side='right', fill='y')

	root.mainloop()
      
