#Glicerina, Biodisel

import socket

from argparse import ArgumentParser
from async_timeout import timeout
from parse import parse
from random import randint
from select import select
from sys import stderr
from time import time


argparser = ArgumentParser()
argparser.add_argument("produto", type=str)
argparser.add_argument("timeout", type=int)
args = argparser.parse_args()

conteudo = 0
hasStarted = False
start = time()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  port = randint(49152, 65535)
  s.bind(('localhost', port))
  s.listen()
  print(f"tanque de {args.produto} listening on port: {port}", file=stderr)

  while True:
    end = time()
    elapsed = end - start
    if hasStarted and elapsed >= args.timeout:
      break

    s.settimeout(6)
 
    if not hasStarted:
      s.settimeout(None)
	
    #rs, ws, xs = select([s], [], [], s_timeout)
    #for s_ in rs:

    #async with timeout(s_timeout):
      #await (conexao, addr) = s.accept()
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

          if not hasStarted:
            start = time()
            hasStarted = True

          batch = float(parsed[0])
          produto = str(parsed[1])

          conteudo += batch

          print(f"tanque: {conteudo:.3f} {args.produto}")

