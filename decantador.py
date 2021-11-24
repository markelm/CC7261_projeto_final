# Decantador

import socket

from argparse import ArgumentParser
from time import time
from random import randint
from parse import parse


argparser = ArgumentParser()

argparser.add_argument("hostname1", type=str) # host 1 = tanque de Glicerina
argparser.add_argument("portnumber1", type=int) 
argparser.add_argument("hostname2", type=str) # host 1 = secador de EtOH
argparser.add_argument("portnumber2", type=int)
argparser.add_argument("hostname3", type=str) # host 1 = tanque de Lavagem 
argparser.add_argument("portnumber3", type=int)

#argparser.add_argument("throughput", type=float)
#argparser.add_argument("intervalo", type=int)
#argparser.add_argument("perda", type=float)
args = argparser.parse_args()

hostname1 = args.hostname1
hostname2 = hostname1 if args.hostname2 is None else args.hostname2
hostname3 = hostname1 if args.hostname3 is None else args.hostname3

portnumber1 = args.portnumber1
#portnumber1 if args.portnumber2 is None else args.portnumber2
portnumber2 = args.portnumber2
#portnumber1 if args.portnumber3 is None else args.portnumber3
portnumber3 = args.portnumber3

capacidade = 10

#args.throughput
vazao = 3
#args.intervalo
intervalo = 5

conteudo = 0
onBreak = False
startTime = time()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  port = randint(49152, 65535) 
  s.bind(('localhost', port))
  s.listen()
  print("listening on port", port)

  while True:
    #conteudo >= vazao and 
    if not onBreak:
        startTime = time()
        onBreak = True

    elapsed = time() - startTime

    if elapsed >= intervalo and onBreak:
      processed = min(conteudo, vazao)
      conteudo -= processed
      saida = processed
      onBreak = False

      # Glicerina (3%)
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        c.connect((hostname1, portnumber1))
        #print(c)

        msg = f'{(saida * 0.03):.3f} Glicerina'
        print(msg)
        b_string = bytes(msg, 'utf-8')
        c.sendall(b_string)

      # EtOH (9%)
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        c.connect((hostname2, portnumber2))
        #print(c)

        msg = f'{(saida * 0.09):.3f} EtOH'
        print(msg)
        b_string = bytes(msg, 'utf-8')
        c.sendall(b_string)

      # Solucao (88%)
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        c.connect((hostname3, portnumber3))
        #print(c)

        msg = f'{(saida * 0.88):.3f} Solucao'
        print(msg)
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

          batch = float(parsed[0])
          produto = str(parsed[1])

          # todo: limitar capacidade
          conteudo += batch
          aceito = batch

          if conteudo > capacidade:
            excesso = conteudo - capacidade
            conteudo = capacidade
            aceito = batch - excesso

          msg = f"{aceito:.3f} Solucao"
          b_string = bytes(msg, "utf-8")
          conexao.sendall(b_string)

          #conexao.close()

          print(f'{produto}:', conteudo)

