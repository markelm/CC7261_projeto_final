# Tanque de lavagem, secador e tanque com saida (perda 0.0)

import socket

from argparse import ArgumentParser
from parse import parse
from random import randint
from sys import stderr
from time import time

argparser = ArgumentParser()
argparser.add_argument("hostname", type=str) # host = tanque biodisel ou etanol
argparser.add_argument("portnumber", type=int) # port = tanque biodisel ou etanol
argparser.add_argument("throughput", type=float)
argparser.add_argument("intervalo", type=int)
argparser.add_argument("perda", type=float)

argparser.add_argument("role", type=str)
argparser.add_argument("produto", type=str)

argparser.add_argument("timeout", type=int)
args = argparser.parse_args()

vazao = args.throughput
conteudo = 0
onBreak = False
startTime = time()

hasStarted = False
start_all = time()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  port = randint(49152, 65535) 
  s.bind(('localhost', port))
  s.listen()
  print(f"{args.role} de {args.produto} listening on port: {port}", file=stderr)

  while True:
    elapsed_all = time() - start_all
    if hasStarted and elapsed_all >= args.timeout:
      break

    #conteudo >= vazao and 
    if not onBreak:
      startTime = time()
      onBreak = True

    elapsed = time() - startTime

    if elapsed >= args.intervalo and onBreak:
      print(f"{args.role}: {conteudo:.3f} {args.produto}")

      processed = min(conteudo, vazao)
      conteudo -= processed
      saida = processed - processed*args.perda
      onBreak = False

      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        # secador -> tanque biodisel ou etanol
        c.connect((args.hostname, args.portnumber))
        #print(c)

        msg = f'{saida:.3f} {args.produto}'
        #print(f"{args.role}:", msg)
        b_string = bytes(msg, 'utf-8')
        c.sendall(b_string)

    else:
      conexao, addr = s.accept()
      with conexao:
        # print("client connected: ", addr)
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

          if not hasStarted:
            start_all = time()
            hasStarted = True

          batch = float(parsed[0])
          produto = str(parsed[1])

          conteudo += batch

          #print(f'{produto}:', conteudo)

