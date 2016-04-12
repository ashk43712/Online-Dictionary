import os
from espeak import espeak
from tkinter import *
from bs4 import BeautifulSoup,SoupStrainer
import tkinter as tk
import urllib
import re, collections
import pickle
import nltk


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


def train(features):
	model = collections.defaultdict(lambda: 1)
	for f in features:
		if model[f]>1 or trie.search(f):
			model[f]+=1
	return model
			
def words(text): 
	return re.findall('[a-z]+', text.lower()) 

NWORDS = train(words(open('big.txt','r').read()))


class EditDist:
	def __init__(self):
		pass

	alphabet='abcdefghijklmnopqrstuvwxyz'

	def edits1(self,word):
	   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
	   deletes    = [a + b[1:] for a, b in splits if b and trie.search(a+b[1:])]
	   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1 and trie.search(a+b[1]+b[0]+b[2:])]
	   replaces   = [a + c + b[1:] for a, b in splits for c in self.alphabet if b and trie.search(a+c+b[1:])]
	   inserts    = [a + c + b  for a, b in splits for c in self.alphabet if trie.search(a+c+b)]
	   return set(deletes + transposes + replaces + inserts)

	def knownEdits2(self,word):
	    return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if trie.search(e2))

	def known(self,words):
		return set(w for w in words if w in NWORDS)

	def correct(self,word):
	    candidates = self.known([word]) or self.known(self.edits1(word)) or self.knownEdits2(word) or [word]
	    sugg=list(candidates)
	    sugg.sort(key = lambda s: nltk.edit_distance(word,s))
	    
	    return sugg[:min(len(sugg),10)]


def util(word):
	os.system('espeak -s 120 '+word)
	word=word.lower()
	if trie.search(word):
		print("Found")
		urlStr='http://www.dictionary.com/browse/'+word+'?s=t'
		url=urllib.request.urlopen(urlStr)
		content = url.read()
		soup = BeautifulSoup(content)
	
		product = SoupStrainer('section',{'class': 'def-pbk ce-spot'})

		main=[p.get_text(strip=True) for p in soup.find_all(product)]

		for item in main:
			sep=re.split('(\d+)\.',item)
			for th in sep:
				print(th)
			print()
	
		chunks=[phrase for item in main for phrase in re.split('(\d+)\.',item)]
	
		res=[chunk for chunk in chunks if chunk]
			
		'''
		for i in range(len(res)):
			print(i,res[i])
		'''		
		
		text = '\n'.join(chunk for chunk in res)
		return text

	
	else:
		print("Not Found\nDid You Mean:")
		#os.system("espeak -s 120 'Not Found. Did You Mean:'")
		ed=EditDist()
		sugg=[]
		trie.didUMean(word,sugg)
		if len(sugg)!=0:
			sugg.sort(key = lambda s: len(s))
		else:
			sugg=ed.correct(word)		
		text = '\n'.join(chunk for chunk in sugg[:min(len(sugg),10)]) 
		return text
	
	
def showSearchResults():
	key=entry.get()
	text=util(key)
	content_text.insert('0.0',text)

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
