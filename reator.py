import socket

from argparse import ArgumentParser
from parse import parse
from random import randint
from sys import stderr
from time import time


argparser = ArgumentParser()
argparser.add_argument("hostname", type=str) #host = tanque biodisel ou etanol
argparser.add_argument("portnumber", type=int) #port = tanque biodisel ou etanol
#argparser.add_argument("throughput", type=float)
#argparser.add_argument("intervalo", type=int)

argparser.add_argument("timeout", type=int)
args = argparser.parse_args()

#args.throughput 
vazao = 5
intervalo = 1

nciclos = 0

onBreak = False
startTime = time()

conteudo = {'NaOH': 0, 'EtOH': 0, 'Oleo': 0}

has_started = False
start_all = time()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  portnumber = randint(49152, 65535)
  s.bind(('localhost', portnumber))
  s.listen()
  print(f"reator listening on port: {portnumber}", file=stderr)

  while True:
    elapsed_all = time() - start_all
    if has_started and elapsed_all >= args.timeout:
      break

    parte = min(conteudo['EtOH']/2, conteudo['NaOH'], conteudo['Oleo'])

    if parte > 0 and not onBreak:
        startTime = time()
        onBreak = True

    elapsed = time() - startTime

    if elapsed >= intervalo and onBreak:
        nciclos += 1
        parte = min(conteudo['EtOH']/2, conteudo['NaOH'], conteudo['Oleo'])
        saida = min(4*parte, vazao)

        fator_reducao = saida/4
        
        # subtração somente com confirmação do decantador
        # (pode estar cheio)
        #conteudo['EtOH'] -= 2*fator_reducao
        #conteudo['NaOH'] -= fator_reducao
        #conteudo['Oleo'] -= fator_reducao

        onBreak = False

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
            # reator -> decantador
            c.connect((args.hostname, args.portnumber))
            #print(c)

            msg = f'{saida:.3f} Solucao'
            #print("reator:", msg)
            b_string = bytes(msg, 'utf-8')
            c.sendall(b_string)

            #while True:
            dados = c.recv(1024)
            if not dados:
              break
  
            msg = dados.decode()
            # handle null-terminated strings
            msg = msg.replace("\x00", "")
    
            parsed = parse("{} {}", msg)
            if parsed is None:
              break
    
            aceito = float(parsed[0])
            produto = str(parsed[1])

            print("---")
            print("reator: ciclo", nciclos)

            for entrada in conteudo:
              print(f"reator: {(conteudo[entrada]):.3f} {entrada}")

            parte = aceito / 4
            conteudo["EtOH"] -= 2 * parte
            conteudo["NaOH"] -= parte
            conteudo["Oleo"] -= parte
    
            print(f"reator: {aceito:.3f} {produto}")
            print("---\n")

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

          if not has_started:
            start_all = time()
            has_started = True

          batch = float(parsed[0])
          entrada = str(parsed[1])

          conteudo[entrada] += batch

          #print(f"reator: {conteudo[entrada]} {entrada}")

