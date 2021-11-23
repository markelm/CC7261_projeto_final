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
argparser.add_argument("perda", type=float)
args = argparser.parse_args()

vazao = args.throughput
conteudo = 0
onBreak = False
startTime = time()

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

                parsed = parse("{}", msg)
                if parsed is None:
                    break

                batch = float(parsed[0])

                conteudo += batch

                print('Conteudo:', conteudo)

                if conteudo >= vazao and not onBreak:
                    startTime = time()
                    onBreak = True

                elapsed = time() - startTime

                if elapsed >= args.intervalo and onBreak:
                    saida = vazao - vazao*args.perda
                    msg = f'{saida:.3f}'
                    print(msg, end=": ")
                    b_string = bytes(msg, 'utf-8')
                    c.sendall(b_string)
                    conteudo -= vazao
                    onBreak = False