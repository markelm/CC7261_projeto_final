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

hasStarted = False
startAll = time()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  portnumber = randint(49152, 65535)
  s.bind(('localhost', portnumber))
  s.listen()
  print(f"reator listening on port: {portnumber}", file=stderr)

  while True:
    elapsedAll = time() - startAll
    if hasStarted and elapsedAll >= args.timeout:
      break

    s.settimeout(1)
    if not hasStarted:
      s.settimeout(None)

    parte = min(conteudo['EtOH']/2, conteudo['NaOH'], conteudo['Oleo'])

    if hasStarted and not onBreak:
        startTime = time()
        onBreak = True

    elapsed = time() - startTime

    if elapsed >= intervalo and onBreak:
        parte = min(conteudo['EtOH']/2, conteudo['NaOH'], conteudo['Oleo'])
        saida = min(4*parte, vazao)
  
        if parte > 0:
          nciclos += 1

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
            
            parte = aceito / 4

            if parte > 0:
              print("---")
              print("reator: ciclo", nciclos)

              for entrada in conteudo:
                print(f"reator: {(conteudo[entrada]):.3f} {entrada}")

              conteudo["EtOH"] -= 2 * parte
              conteudo["NaOH"] -= parte
              conteudo["Oleo"] -= parte
    
              print(f"reator: {aceito:.3f} {produto}")
              print("---\n")

    else:
      try:
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
              startAll = time()
              hasStarted = True

            batch = float(parsed[0])
            entrada = str(parsed[1])

            conteudo[entrada] += batch

            #print(f"reator: {conteudo[entrada]} {entrada}")
      except OSError as msg:
        continue

