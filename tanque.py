import socket

from argparse import ArgumentParser
from random import randint
from parse import parse
from time import perf_counter_ns, sleep


argparser = ArgumentParser()
args = argparser.parse_args()

conteudo = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.bind(('localhost', randint(49152, 65535)))
  print(s)

  # Communication with server 2


  s.listen()
  while True:
      conexao, addr = s.accept()
      with conexao:
      #print("client connected: ", addr)
        while True:
            dados = conexao.recv(1024)
            if not dados:
              break

            msg = dados.decode()
            # handle null-terminated strings
            msg = msg.replace("\x00", "")

            parsed = parse("{}", msg)
            if parsed is None:
              break

            batch = float(parsed[0])

            conteudo += batch

            print('Conteudo:',conteudo)