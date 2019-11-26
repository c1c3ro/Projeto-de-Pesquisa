from __future__ import unicode_literals
from pydub import AudioSegment
from os import path
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import timedelta, date
import speech_recognition as sr
import os
import youtube_dl
import json
import glob
import datetime
import shutil


def pegar_links():
    k = 1
    info = {}
    url = 'https://g1.globo.com/busca/?q=meu+bairro+na+tv'
    g1 = 'https://globoplay.globo.com/v/'
    n = int(input("Digite o numero de paginas: "))  # A quantidade de videos dependerá do numero de paginas
    for i in range(1, n + 1):
        j = 0
        print('Pegando informacoes da pagina ' + str(i))
        if (i != 1):
            url = url + '&page=' + str(i)
        html_page = urlopen(url)
        soup = BeautifulSoup(html_page, 'html.parser')
        links = soup.find_all('div', class_="widget--info__media-container")
        titles = soup.find_all('div', class_="widget--info__title product-color")
        dates = soup.find_all('div', class_="widget--info__meta")

        # Verificando os links, titulos e datas e armazenando num dicionário:

        for link in links:
            title = titles[j].text
            title = title.strip()
            if ((title.upper().find("MEU BAIRRO NA TV")) < 0):
                j += 1
                continue
            link = link.find('a').get('href')
            index = link.find('%2Fv%2')
            link = g1 + link[index + 7:index + 14]
            date1 = dates[j].text
            if (date1.find("dia") > 0):
                t1 = int(''.join(filter(str.isdigit, date1)))
                date1 = date.today() - timedelta(days=t1)
                date1 = date1.strftime("%d/%m/%Y")
            if (date1.find("hora") > 0):
                date1 = date.today()
                date1 = date1.strftime("%d/%m/%Y")
            info['video ' + str(k)] = {
                'titulo': title,
                'link': link,
                'data': date1
            }
            j += 1
            k += 1

    # Armazenando num arquivo Json para posterior analise e retornando o dicionário para trabalharmos com os links:

    with open('videosInfo.json', 'a') as outfile:
        json.dump(info, outfile, ensure_ascii=False)
    return info


def armazena_transcricao(data, novoArquivo, path):
    print('Armazenando num arquivo json...')
    ArquivoJson = novoArquivo[:-4] + '.json'
    with open(ArquivoJson, 'a') as outfile:
        json.dump(data, outfile, ensure_ascii=False)
    ArquivoFolder = novoArquivo[:-4]
    pathCreate = path + os.sep + ArquivoFolder
    os.mkdir(pathCreate)
    path1 = path + os.sep + novoArquivo
    path2 = path + os.sep + ArquivoJson
    shutil.move(path1, pathCreate)
    shutil.move(path2, pathCreate)
    return 1


# Funcao para mostrar o status do download
def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


# Funcao que recebe o link do video e baixa-o
def baixar_midia(url, path):
    print('Baixando...')
    ydl_opts = {
        'format': 'best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'noPlaylist': True,
        'progress_hooks': [my_hook],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 1


# Função que receberá o nome do arquivo na pasta e mostrará sua transcrição,
# no caso, ele irá receber cada "sub-audio" por vez e mostrando sua respectiva transcrição
def transcribe(fileToTranscribe, k):
    print('Transcrevendo parte {}'.format(k + 1))
    AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), fileToTranscribe)
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)
    return (r.recognize_google(audio, language="pt-BR"))


def converter(novoArquivo):
    # Recebe o nome do arquivo baixado e quebra o audio em pedaços menores
    newAudio1 = AudioSegment.from_wav(novoArquivo)
    i = int(int(newAudio1.duration_seconds) / 120)
    j = int(int(newAudio1.duration_seconds) % 120)
    k = int(0)
    Transcription = {}
    while k < i:
        part = 'part' + str(k) + '.wav'
        newAudio = AudioSegment.from_wav(novoArquivo)
        t1 = k * 120 * (1000)
        t2 = t1 + (120000)
        newAudio = newAudio[t1:t2]
        newAudio.export(part, format="wav")  # Exporta o sub-audio na pasta atual
        Transcription[part] = transcribe(part, k)  # Chama a função para transcrever este sub-audio e armazena num dicionario
        os.remove(part)  # Deleta o sub-audio depois que o transcreveu
        if k == (i - 1):
            k += 1
            part = 'part' + str(k) + '.wav'
            newAudio = AudioSegment.from_wav(novoArquivo)
            t1 = t2
            t2 = t2 + (j * 1000)
            newAudio = newAudio[t1:t2]
            newAudio.export(part, format="wav")
            Transcription[part] = transcribe(part, k)
            os.remove(part)
            continue
        k += 1
    return Transcription


def main():
    caminho = os.path.dirname(os.path.realpath(__file__))
    info = {}
    info = pegar_links()
    i = 0
    for video in info:
        i += 1
        try:
            baixar_midia(info[video]['link'], caminho)
            # Procurando o arquivo .wav
            files = os.listdir(caminho)
            for j in files:
                if j.endswith('.wav'):
                    Novo_arquivo = j
        except:
            print('Nao foi possivel baixar o video %d.' % (i))
            return -1
        try:
            Transcricao = converter(Novo_arquivo)
        except:
            print('Nao foi possivel transcrever o video %d.' % (i))
            return -1
        armazena_transcricao(Transcricao, Novo_arquivo, caminho)
        print("Processado %d video(s)." % (i))
    return 0


# chama a funcao main
main()