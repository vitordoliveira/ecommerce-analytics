#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
E-commerce Analytics - Configuração de Ambiente
Autor: Vitor Oliveira (https://github.com/vitordoliveira)
Data de Criação: 2025-05-26
Última Atualização: 2025-05-28 19:40:52
"""

import os
import sys
import subprocess
from datetime import datetime

def banner():
    """Exibe o banner do projeto."""
    print("=" * 80)
    print("E-COMMERCE ANALYTICS - CONFIGURAÇÃO DE AMBIENTE".center(80))
    print("=" * 80)
    print(f"Data e hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Usuário: {os.getenv('USERNAME', 'vitordoliveira')}")
    print("-" * 80)

def verificar_requisitos():
    """Verifica se os requisitos do sistema estão atendidos."""
    print("\n[1/3] Verificando requisitos do sistema...")
    
    # Verificar versão do Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ ERRO: Este projeto requer Python 3.8 ou superior.")
        print(f"   Versão atual: {python_version.major}.{python_version.minor}.{python_version.micro}")
        return False
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} - OK")
    
    # Verificar se pip está instalado
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        print("✅ Pip - OK")
    except subprocess.CalledProcessError:
        print("❌ ERRO: Pip não está instalado ou não está funcionando corretamente.")
        return False
    
    return True

def instalar_dependencias():
    """Instala as dependências do projeto a partir do requirements.txt."""
    print("\n[2/3] Instalando dependências...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ ERRO: Arquivo requirements.txt não encontrado.")
        return False
    
    # Instalar os pacotes
    try:
        print("\nInstalando pacotes do requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Todas as dependências foram instaladas com sucesso")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERRO: Falha ao instalar dependências: {e}")
        return False
    
    return True

def criar_ambiente_local():
    """Cria apenas arquivos de configuração local se não existirem."""
    print("\n[3/3] Configurando ambiente local...")
    
    # Criar arquivo .env se não existir
    if not os.path.exists('.env'):
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(f"""# Arquivo de configuração do E-commerce Analytics
# Criado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Configurações gerais
AMBIENTE=desenvolvimento
DEBUG=True
LOG_LEVEL=INFO

# Configurações de dados
DIRETORIO_DADOS=data
DIRETORIO_EXPORTS=exports

# Configurações de usuário
USUARIO_ATUAL={os.getenv('USERNAME', 'vitordoliveira')}
DATA_INSTALACAO={datetime.now().strftime('%Y-%m-%d')}
""")
        print("✅ Arquivo .env criado")
    else:
        print("✅ Arquivo .env já existe (não modificado)")
    
    # Verificar existência de diretórios temporários essenciais
    for dir_path in ['data/temp', 'logs']:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ Diretório {dir_path} criado")
        else:
            print(f"✅ Diretório {dir_path} já existe")
    
    return True

def verificar_importacoes():
    """Verifica se as importações principais funcionam."""
    print("\nVerificando importações das bibliotecas principais...")
    
    importacoes = [
        ("polars", "pl"),
        ("pandas", "pd"),
        ("matplotlib.pyplot", "plt"),
        ("plotly.express", "px")
    ]
    
    falhas = 0
    for modulo, alias in importacoes:
        try:
            exec(f"import {modulo} as {alias}")
            print(f"✅ {modulo} - OK")
        except ImportError:
            print(f"❌ {modulo} - Falha na importação")
            falhas += 1
    
    if falhas > 0:
        print(f"\n⚠️ {falhas} bibliotecas não puderam ser importadas.")
        print("   Tente reinstalar as dependências com: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Função principal para executar a configuração do ambiente."""
    banner()
    
    print("\nBem-vindo ao configurador de ambiente do E-commerce Analytics!")
    print("Este script configurará o ambiente para execução do projeto.")
    print("Nota: A estrutura de pastas do projeto já deve existir (clone do GitHub).")
    
    # Perguntar se o usuário quer continuar
    resposta = input("\nDeseja prosseguir com a configuração? [S/n]: ")
    if resposta.lower() == 'n':
        print("\nConfiguração cancelada pelo usuário.")
        return 1
    
    # Executar os passos
    steps = [
        verificar_requisitos,
        instalar_dependencias,
        criar_ambiente_local
    ]
    
    total_steps = len(steps)
    successful_steps = 0
    
    for step_func in steps:
        if step_func():
            successful_steps += 1
        else:
            print(f"\n⚠️  Passo {successful_steps + 1}/{total_steps} falhou.")
            if input("\nDeseja continuar mesmo assim? [s/N]: ").lower() != 's':
                break
    
    # Verificar importações apenas se todos os passos foram concluídos
    if successful_steps == total_steps:
        verificar_importacoes()
    
    # Mostrar resultado final
    if successful_steps == total_steps:
        print("\n" + "=" * 80)
        print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO! 🎉".center(80))
        print("=" * 80)
        print("\nVocê já pode executar o sistema com o comando:")
        print("\n    python main.py")
        print("\nBoa análise de dados!")
        return 0
    else:
        print("\n" + "=" * 80)
        print("⚠️  CONFIGURAÇÃO INCOMPLETA".center(80))
        print("=" * 80)
        print(f"\n{successful_steps} de {total_steps} passos foram concluídos.")
        print("\nPor favor, corrija os problemas e tente novamente.")
        return 1

if __name__ == "__main__":
    sys.exit(main())