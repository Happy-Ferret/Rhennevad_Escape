#!/usr/bin/env python
import pygame.event
import pygame.key
import pygame.display
import pygame.image
import pygame.mixer
import pygame
import time
import os
import copy
from pygame.locals import *
import xml.etree.ElementTree as ET
pygame.display.init()
pygame.font.init()
pygame.mixer.init()
print "Desutezeoid arbitrary point and click engine v1.2.0"
print "parsing ENGSYSTEM.xml"
conftree = ET.parse("ENGSYSTEM.xml")
confroot = conftree.getroot()
screentag=confroot.find("screen")
print "populate keylist with null keyid, add any keys in initkeys."
initkeystag=confroot.find("initkeys")
keylist=list(["0"])
for initk in initkeystag.findall("k"):
	if (initk.attrib.get("keyid"))!="0":
		keylist.extend([initk.attrib.get("keyid")])

scrnx=int(screentag.attrib.get("x", "800"))
scrny=int(screentag.attrib.get("y", "600"))
titletag=confroot.find("title")
debugtag=confroot.find("debug")
DEBUG=int(debugtag.attrib.get("debug", "1"))
printkeys=int(debugtag.attrib.get("printkeys", "1"))
clickfields=int(debugtag.attrib.get("clickfields", "0"))
cfcolor=pygame.Color(debugtag.attrib.get("cfcolor", "#888888"))

beginref=(confroot.find("beginref")).text

globalcoretag=confroot.find("globalcore")
globalforkstag=confroot.find("globalforks")
print "config parsed."
titlebase=titletag.attrib.get("base", "Desutezeoid: ")
class clicktab:
	def __init__(self, box, reftype, ref, keyid, takekey, sfxclick, sound):
		self.box=box
		self.ref=ref
		self.keyid=keyid
		self.takekey=takekey
		self.reftype=reftype
		self.sfxclick=sfxclick
		self.sound=sound
class timeouttab:
	def __init__(self, seconds, keyid, postkey):
		self.keyid=keyid
		self.regtime=time.time()
		self.seconds=seconds
		self.postkey=postkey

#class keyobj:
#	def __init__(self, keyid):
#		self=keyid
def debugmsg(msg):
	if DEBUG==1:
		print msg
def keyprint():
	if printkeys==1:
		print keylist
keyprint()
prevpage="NULL"
#point this to your first screen c: no menu program really needed :o
curpage=beginref

screensurf=pygame.display.set_mode((scrnx, scrny))
quitflag=0
clicklist=list()

timeoutlist=list()
keybak=list(keylist)
forksanitycheck=0
forksanity=0
print "done. begin mainloop."
while quitflag==0:
	huris=0
	clicklist=list()
	time.sleep(0.1)
	pos = pygame.mouse.get_pos()
	#print "tic"
	if curpage!=prevpage:
		print "preparsing page"
		
		tree = ET.parse(curpage)
		root = tree.getroot()
		prevpage=curpage
		coretag=root.find('core')
		forktag=root.find('forks')
		print "parsing global core objects into page structure..."
		for glb in globalcoretag:
			coretag.append(copy.deepcopy(glb))
		print "parsing global fork objects into page structure..."
		for glb in globalforkstag:
			forktag.append(copy.deepcopy(glb))
		pageconf=root.find('pageconf')
		pagetitle=(pageconf.find('title')).text
		BGMstop=int(pageconf.attrib.get("BGMstop", "1"))
		if BGMstop==1:
			pygame.mixer.music.stop()
		BGon=int(pageconf.attrib.get("BGimg", "0"))
		BGMon=int(pageconf.attrib.get("BGM", "0"))
		if BGMon==1:
			BGMtrack=(pageconf.find('BGM')).text
			pygame.mixer.music.load(BGMtrack)
			pygame.mixer.music.play(-1)
		pygame.display.set_caption((titlebase + pagetitle), (titlebase + pagetitle))
		print ("Page title: '" + pagetitle + "'")
		if BGon==1:
			BGfile=(pageconf.find('BG')).text
			BG=pygame.image.load(BGfile)
		screensurf.fill((170, 170, 170))
		print "done. begin mainloop"
	if BGon==1:
		screensurf.blit(BG, (0, 0))
	#print keylist
	#print keybak
	#if keylist!=keybak or forksanitycheck==1:
	
	#debugmsg("keyid change detected. reparsing forks.")
	for fork in forktag.findall("ortrig"):
		#print "batchtrig"
		masterkey=fork.attrib.get("keyid")
		orflg=0
		for keyif in fork.findall("k"):
			ifpol=keyif.attrib.get("if")
			subkey=keyif.attrib.get("keyid")
			if subkey in keylist:
				if ifpol=="1":
					orflg=1
			elif not subkey in keylist:
				if ifpol=="0":
					orflg=1
		if orflg == 1:
			if not masterkey in keylist:
				keylist.extend([masterkey])
				#print keylist
				keyprint()
				forksanity=1
		else:
			if masterkey in keylist:
				keylist.remove(masterkey)
				#print keylist
				keyprint()
				forksanity=1
	for fork in forktag.findall("batchtrig"):
		#print "batchtrig"
		masterkey=fork.attrib.get("keyid")
		complist=[1] 
		for keyif in fork.findall("k"):
			ifpol=keyif.attrib.get("if")
			subkey=keyif.attrib.get("keyid")
			if subkey in keylist:
				if ifpol=="1":
					complist.extend([1])
				else:
					complist.extend([0])
			elif not subkey in keylist:
				if ifpol=="0":
					complist.extend([1])
				else:
					complist.extend([0])
		if len(set(complist)) == 1:
			if not masterkey in keylist:
				keylist.extend([masterkey])
				#print keylist
				keyprint()
				forksanity=1
		else:
			if masterkey in keylist:
				keylist.remove(masterkey)
				#print keylist
				keyprint()
				forksanity=1
	for fork in forktag.findall("batchset"):
		#print "batch"
		#print fork
		masterkey=fork.attrib.get("keyid")
		toggpol=fork.attrib.get("set")
		if masterkey in keylist:
			keylist.remove(masterkey)
			if toggpol=="1":
				for subkey in fork.findall("k"):
					subkeyid=subkey.attrib.get("keyid")
					if not subkeyid in keylist:
						keylist.extend([subkeyid])
						#print keylist
						keyprint()
				forksanity=1
			else:
				for subkey in fork.findall("k"):
					subkeyid=subkey.attrib.get("keyid")
					if subkeyid in keylist:
						keylist.remove(subkeyid)
						#print keylist
						keyprint()
				forksanity=1
	pagejumpflag=0
	for fork in forktag.findall("pagejump"):
		masterkey=fork.attrib.get("keyid")
		if masterkey in keylist:
			keylist.remove(masterkey)
			curpage=fork.attrib.get("page")
			print ("iref: loading page '" + f.ref + "'")
			pagejumpflag=1
			break
	for fork in forktag.findall("timeout"):
		masterkey=fork.attrib.get("keyid")
		if masterkey in keylist:
			notinlist=1
			for tif in timeoutlist:
				if tif.keyid==masterkey:
					notinlist=0
			if notinlist==1:
				seconds=float(fork.attrib.get("seconds"))
				postkey=fork.attrib.get("post", "0")
				timeoutlist.extend([timeouttab(seconds, masterkey, postkey)])
	for fork in forktag.findall("triggerlock"):
		masterkey=fork.attrib.get("keyid")
		triggerkey=fork.attrib.get("trigger")
		lockkey=fork.attrib.get("lock")
		if masterkey in keylist:
			#keylist.remove(masterkey)
			if lockkey not in keylist:
				if triggerkey not in keylist:
					keylist.extend([triggerkey])
					keylist.extend([lockkey])
	
				
	for fork in forktag.findall("sound"):
		masterkey=fork.attrib.get("keyid")
		soundname=fork.attrib.get("sound")
		if masterkey in keylist:
			keylist.remove(masterkey)
			soundobj=pygame.mixer.Sound(soundname)
			soundobj.play()
	if forksanity==1:
		forksanitycheck=1
		forksanity=0
		#skiploop=1
	else:
		forksanitycheck=0
	
	for tif in timeoutlist:
		if tif.keyid not in keylist:
			
			timeoutlist.remove(tif)
		elif ((time.time()) - tif.regtime) > tif.seconds:
			keylist.remove(tif.keyid)
			if tif.postkey not in keylist:
				if tif.postkey!="0":
					keylist.extend([tif.postkey])
			#print keylist
			keyprint()
			timeoutlist.remove(tif)		
		
	keybak=list(keylist)
	#print keylist
	for labref in coretag.findall("img"):
		keyid=labref.attrib.get('keyid', "0")
		takekey=labref.attrib.get('takekey', "0")
		onkey=labref.attrib.get('onkey', "0")
		offkey=labref.attrib.get('offkey', "0")
		hoverkey=labref.attrib.get('hoverkey', "0")
		clicksoundflg=int(labref.attrib.get('sfxclick', "0"))
		soundname=(labref.attrib.get('sound', "0"))
		if ((onkey=="0" and offkey=="0") or (onkey=="0" and offkey not in keylist) or (onkey in keylist and offkey=="0") or (onkey in keylist and offkey not in keylist)):
			imgx=int(labref.attrib.get("x"))
			imgy=int(labref.attrib.get("y"))
			imgcon=(labref.find("con")).text
			hovpic=int(labref.attrib.get("hovpic", "0"))
			act=labref.find("act")
			acttype=act.attrib.get("type", "none")
			pos = pygame.mouse.get_pos()
			imggfx=pygame.image.load(imgcon)
			clickref=screensurf.blit(imggfx, (imgx, imgy))
			if hoverkey!="0":
				if clickref.collidepoint(pos)==1:
					if not hoverkey in keylist:
						keylist.extend([hoverkey])
				else:
					if hoverkey in keylist:
						keylist.remove(hoverkey)
			if hovpic==1:
				hovcon=(labref.find("altcon")).text
				hovgfx=pygame.image.load(hovcon)
				if clickref.collidepoint(pos)==1:
					clickref=screensurf.blit(hovgfx, (imgx, imgy))
		
			if acttype!="none":
				pos = pygame.mouse.get_pos()
				if acttype=="iref":
					ref=act.attrib.get("ref")
					datstr=clicktab(clickref, "iref", ref, keyid, takekey, clicksoundflg, soundname)
					clicklist.extend([datstr])
				if acttype=="quit":
					ref=act.attrib.get("ref")
					datstr=clicktab(clickref, "quit", ref, keyid, takekey, clicksoundflg, soundname)
					clicklist.extend([datstr])
				if acttype=="key":
					ref=act.attrib.get("ref")
					datstr=clicktab(clickref, "key", ref, keyid, takekey, clicksoundflg, soundname)
					clicklist.extend([datstr])
	for labref in coretag.findall("box"):
		keyid=labref.attrib.get('keyid', "0")
		takekey=labref.attrib.get('takekey', "0")
		onkey=labref.attrib.get('onkey', "0")
		offkey=labref.attrib.get('offkey', "0")
		hoverkey=labref.attrib.get('hoverkey', "0")
		clicksoundflg=int(labref.attrib.get('sfxclick', "0"))
		soundname=(labref.attrib.get('sound', "0"))
		if ((onkey=="0" and offkey=="0") or (onkey=="0" and offkey not in keylist) or (onkey in keylist and offkey=="0") or (onkey in keylist and offkey not in keylist)):
			imgx=int(labref.attrib.get("x"))
			imgy=int(labref.attrib.get("y"))
			sizex=int(labref.attrib.get("sizex"))
			sizey=int(labref.attrib.get("sizey"))
			onhov=int(labref.attrib.get("onhov", "0"))
			hovcolor=pygame.Color(labref.attrib.get("HOVCOLOR", "#FFFFFF"))
			hovalpha=int(labref.attrib.get("hovalpha", "140"))
			boxalpha=int(labref.attrib.get("alpha", "100"))
			boxcolor=pygame.Color(labref.attrib.get("COLOR", "#FFFFFF"))
			#imgcon=(labref.find("con")).text
			act=labref.find("act")
			acttype=act.attrib.get("type", "none")
			pos = pygame.mouse.get_pos()
			#imggfx=pygame.image.load(imgcon)
			boxgfx=pygame.Surface((sizex, sizey))
			boxgfx.convert_alpha()
			#imggfx.fill(boxcolor)
			boxgfx.set_alpha(0)
			clickref=screensurf.blit(boxgfx, (imgx, imgy))
			if onhov==1 and clickref.collidepoint(pos)==1:
				boxgfx.fill(hovcolor)
				boxgfx.set_alpha(hovalpha)
				#skip blitting a second time if alpha is 0.
				if hovalpha!=0:
					clickref=screensurf.blit(boxgfx, (imgx, imgy))
			else:
				boxgfx.fill(boxcolor)
				boxgfx.set_alpha(boxalpha)
				#skip blitting a second time if alpha is 0.
				if boxalpha!=0:
					clickref=screensurf.blit(boxgfx, (imgx, imgy))
			if hoverkey!="0":
				if clickref.collidepoint(pos)==1:
					if not hoverkey in keylist:
						keylist.extend([hoverkey])
				else:
					if hoverkey in keylist:
						keylist.remove(hoverkey)		
			if acttype!="none":
				pos = pygame.mouse.get_pos()
				if acttype=="iref":
					ref=act.attrib.get("ref")
					datstr=clicktab(clickref, "iref", ref, keyid, takekey, clicksoundflg, soundname)
					clicklist.extend([datstr])
				if acttype=="quit":
					ref=act.attrib.get("ref")
					datstr=clicktab(clickref, "quit", ref, keyid, takekey, clicksoundflg, soundname)
					clicklist.extend([datstr])
				if acttype=="key":
					ref=act.attrib.get("ref")
					datstr=clicktab(clickref, "key", ref, keyid, takekey, clicksoundflg, soundname)
					clicklist.extend([datstr])
	for texref in coretag.findall("text"):
		onkey=texref.attrib.get('onkey', "0")
		offkey=texref.attrib.get('offkey', "0")
		if ((onkey=="0" and offkey=="0") or (onkey=="0" and offkey not in keylist) or (onkey in keylist and offkey=="0") or (onkey in keylist and offkey not in keylist)):
			labx=int(texref.attrib.get("x"))
			laby=int(texref.attrib.get("y"))
			size=int(texref.attrib.get("size"))
			FGCOL=pygame.Color(texref.attrib.get("FGCOLOR", "#FFFFFF"))
			BGCOL=pygame.Color(texref.attrib.get("BGCOLOR", "#000000"))
			transp=int(texref.attrib.get("transp", "0"))
			texfnt=pygame.font.SysFont(None, size)
			pixcnt1=laby
			pixjmp=(size+0)
			textcont=(texref.text + "\n")
			textchunk=""
			#this draws the text body line-per-line
			for texch in textcont:
				if texch=="\n":
					#if at newline, render line of text, clear textchunk, and add to pixcnt1
					if transp==0:
						texgfx=texfnt.render(textchunk, True, FGCOL, BGCOL)
					else:
						texgfx=texfnt.render(textchunk, True, FGCOL)
					screensurf.blit(texgfx, (labx, pixcnt1))
					pixcnt1 += pixjmp
					textchunk=""
				else:
					#if not at a newline yet, keep building textchunk.
					textchunk=(textchunk + texch)
			
			#clickref=screensurf.blit(labgfx, (labx, laby))
	for labref in coretag.findall("label"):
		keyid=labref.attrib.get('keyid', "0")
		takekey=labref.attrib.get('takekey', "0")
		onkey=labref.attrib.get('onkey', "0")
		offkey=labref.attrib.get('offkey', "0")
		hoverkey=labref.attrib.get('hoverkey', "0")
		clicksoundflg=int(labref.attrib.get('sfxclick', "0"))
		soundname=(labref.attrib.get('sound', "0"))
		if ((onkey=="0" and offkey=="0") or (onkey=="0" and offkey not in keylist) or (onkey in keylist and offkey=="0") or (onkey in keylist and offkey not in keylist)):
			labx=int(labref.attrib.get("x"))
			laby=int(labref.attrib.get("y"))
			size=int(labref.attrib.get("size"))
			FGCOL=pygame.Color(labref.attrib.get("FGCOLOR", "#FFFFFF"))
			BGCOL=pygame.Color(labref.attrib.get("BGCOLOR", "#000000"))
			labcon=(labref.find("con")).text
			act=labref.find("act")
			acttype=act.attrib.get("type", "none")
			transp=int(labref.attrib.get("transp", "0"))
			labfnt=pygame.font.SysFont(None, size)
			if transp==0:
				labgfx=labfnt.render(labcon, True, FGCOL, BGCOL)
			else:
				labgfx=labfnt.render(labcon, True, FGCOL)
			clickref=screensurf.blit(labgfx, (labx, laby))
			if hoverkey!="0":
				if clickref.collidepoint(pos)==1:
					if not hoverkey in keylist:
						keylist.extend([hoverkey])
				else:
					if hoverkey in keylist:
						keylist.remove(hoverkey)
			if acttype!="none":
				pos = pygame.mouse.get_pos()
			if acttype=="iref":
				ref=act.attrib.get("ref")
				datstr=clicktab(clickref, "iref", ref, keyid, takekey, clicksoundflg, soundname)
				clicklist.extend([datstr])
			if acttype=="quit":
				ref=act.attrib.get("ref")
				datstr=clicktab(clickref, "quit", ref, keyid, takekey, clicksoundflg, soundname)
				clicklist.extend([datstr])
			if acttype=="key":
				ref=act.attrib.get("ref")
				datstr=clicktab(clickref, "key", ref, keyid, takekey, clicksoundflg, soundname)
				clicklist.extend([datstr])
		#else:
			#time.sleep(0.04)
	if clickfields==1:
		for f in clicklist:
			pygame.draw.rect(screensurf, cfcolor, f.box, 1)
	eventhappen=0
	for event in pygame.event.get():
		#print "nominal"
		eventhappen=1
		if event.type == QUIT:
			quitflag=1
			print ("quit: OS or WM quit")
			break
		if event.type==MOUSEBUTTONDOWN:
			#print "nominal2"
			for f in clicklist:
				#print "nominal3"
				if f.box.collidepoint(event.pos)==1 and event.button==1:
					if f.sfxclick==1:
						clicksound=pygame.mixer.Sound(f.sound)
						clicksound.play()
					if f.keyid!="0":
						if not f.keyid in keylist:
							keylist.extend([f.keyid])
							#print keylist
							keyprint()
					if f.takekey!="0":
						if takekey in keylist and f.takekey!="0":
							keylist.remove(f.takekey)
							#print keylist
							keyprint()
					if f.reftype=="iref":
						curpage=f.ref
						print ("iref: loading page '" + f.ref + "'")
						break
					if f.reftype=="quit":
						print ("quit: onclick quit")
						quitflag=1
						break
	if eventhappen==0:
		time.sleep(0.1)

		
	pygame.display.update()
	pygame.event.pump()
	
