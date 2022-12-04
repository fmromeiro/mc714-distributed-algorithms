import os
from tests import logical_clock, leader, mutual_exclusion

if __name__ == '__main__':
    test = os.getenv('DS_TEST', '').upper()
    if test == 'CLOCK':
        logical_clock.run()
    elif test == 'LEADER':
        leader.run()
    elif test == 'MUTEX':
        mutual_exclusion.run()
    else:
        print(f"Teste '{test}' não reconhecido, encerrando")