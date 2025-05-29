import os
import sys
import pytest
from datetime import datetime

def executar_testes():
    """
    Função para executar todos os testes do projeto.
    
    Uso:
        python run_tests.py          # Executa todos os testes
        python run_tests.py -v       # Executa os testes com mais detalhes (verbose)
        python run_tests.py <nome>   # Executa um teste específico
    """
    print("==== Iniciando testes do E-commerce Analytics ====")
    print(f"Data atual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Usuário: {os.getenv('USER', 'vitordoliveira')}")
    print("=================================================")
    
    # Obter os argumentos passados para o script
    args = sys.argv[1:]
    
    # Se houver argumentos, passar para o pytest
    if len(args) > 0:
        exit_code = pytest.main(args)
    else:
        # Senão, executar todos os testes no modo verbose
        exit_code = pytest.main(['-v', 'tests'])
    
    # Retornar o código de saída do pytest
    return exit_code

if __name__ == "__main__":
    sys.exit(executar_testes())