##Fonte de produtos (Oleo, EtOH, NaOH, Agua)

import socket

from argparse import ArgumentParser
from random import randint
from time import sleep #, time


argparser = ArgumentParser()
argparser.add_argument("hostname", type=str)
argparser.add_argument("portnumber", type=int)
argparser.add_argument("throughput", type=float)
argparser.add_argument("intervalo", type=int)
argparser.add_argument("saida", type=str)

#argparser.add_argument("timeout", type=int)
args = argparser.parse_args()

vazao = args.throughput
#start = time()

while True:
  #elapsed = time() - start
  #if elapsed >= args.timeout:
    #break

  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((args.hostname, args.portnumber))
    #print(s) 

    sleep(args.intervalo)
    if args.saida == "Oleo":
      vazao = randint(1000, 2000) / 1000

    msg = f"{vazao:.3f} {args.saida}"
    print("fonte:", msg)
    b_string = bytes(msg, 'utf-8')
    s.sendall(b_string)

