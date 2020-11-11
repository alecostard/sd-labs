import sys
from Replica import Replica

NPEERS = 4

def main():
    check_input()
    local_replica = Replica(int(sys.argv[1]), npeers=NPEERS)
    Replica.print_help()
    local_replica.start()
    

def check_input():
    if len(sys.argv) != 2:
        print("Programa espera um argumento inteiro.")
        print(f"\tpython {sys.argv[0]} n")
        sys.exit(1)

if __name__ == "__main__":
    main()