# -*- coding: utf-8 -*-
#!/bin/env python
from __future__ import unicode_literals
import youtube_dl
import json
import os
import glob
import datetime


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
    return

def baixar_midia(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'noPlaylist' : True,
        'progress_hooks': [my_hook],
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return
    
def converter(nome_arquivo_baixado):
    #coloque aqui seu codigo
    return
    
def main():
    #coloque aqui seu codigo pra ler os links do json e substitula pelas duas linhas provisorias abaixo
    links = []
    links.append("https://globoplay.globo.com/v/7989259")

    for i in range(0,len(links),1):
        baixar_midia(links[i])
        converter("variavel com o nome aqui")
        print("Processado %d video(s)." % (i+1))
    
    return 0
    

# chama a funcao main
main()
