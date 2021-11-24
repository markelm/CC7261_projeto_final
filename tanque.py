#Glicerina, Biodisel

import socket

from argparse import ArgumentParser
from random import randint
from parse import parse



argparser = ArgumentParser()
args = argparser.parse_args()

conteudo = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  port = randint(49152, 65535)
  s.bind(('localhost', port))
  s.listen()
  print("Listening on port", port)

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

            parsed = parse("{} {}", msg)

            if parsed is None:
              break

            batch = float(parsed[0])
            produto = str(parsed[1])

            conteudo += batch

            print(f'{produto}:',conteudo)

