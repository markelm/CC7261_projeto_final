# Fonde produtos (Oleo, EtOH, NaOH, Agua)
#Tanque de lavagem e secador e tanque com saida

import socket

from argparse import ArgumentParser
from time import time
from random import randint
from parse import parse



argparser = ArgumentParser()
argparser.add_argument("hostname", type=str) #host = tanque biodisel ou etanol
argparser.add_argument("portnumber", type=int) #port = tanque biodisel ou etanol
argparser.add_argument("throughput", type=float)
argparser.add_argument("intervalo", type=int)

args = argparser.parse_args()

vazao = args.throughput
onBreak = False
startTime = time()

conteudo = {'NaOH': 0, 'EtOH': 0, 'Oleo': 0}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('localhost', randint(49152, 65535)))
    print(s)
    s.listen()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        # secador -> tanque biodisel ou etanol
        c.connect((args.hostname, args.portnumber))
        print(c)

        while True:
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
                entrada = str(parsed[1])

                conteudo[entrada] += batch

                print(f'{entrada}:', conteudo[entrada])

                parte = min(conteudo['EtOH']/2, conteudo['NaOH'], conteudo['Oleo'])

                if parte > 0 and not onBreak:
                    startTime = time()
                    onBreak = True

                elapsed = time() - startTime

                if elapsed >= args.intervalo and onBreak:

                    parte = min(conteudo['EtOH']/2, conteudo['NaOH'], conteudo['Oleo'])
                    saida = min(4*parte, vazao)

                    fator_reducao = saida/4
                    
                    conteudo['EtOH'] -= 2*fator_reducao
                    conteudo['NaOH'] -= fator_reducao
                    conteudo['Oleo'] -= fator_reducao

                    msg = f'{saida:.3f} Solucao'
                    print(msg, end=": ")
                    b_string = bytes(msg, 'utf-8')
                    c.sendall(b_string)
                    onBreak = False