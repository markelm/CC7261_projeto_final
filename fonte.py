##Fonde produtos (Oleo, EtOH, NaOH, Agua)

import socket

from argparse import ArgumentParser
from time import sleep


argparser = ArgumentParser()
argparser.add_argument("hostname", type=str)
argparser.add_argument("portnumber", type=int)
argparser.add_argument("throughput", type=float)
argparser.add_argument("intervalo", type=int)
argparser.add_argument("saida", type=str)
args = argparser.parse_args()

vazao = args.throughput


while True:
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((args.hostname, args.portnumber))
    print(s) 

    sleep(args.intervalo)
    msg = f"{vazao:.3f} {args.saida}"
    print(msg, end=": ")
    b_string = bytes(msg, 'utf-8')
    s.sendall(b_string)

