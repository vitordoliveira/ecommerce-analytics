#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
E-commerce Analytics - Utilitário de Limpeza de Projeto
Autor: Vitor Oliveira (https://github.com/vitordoliveira)
Data de Atualização: 2025-05-29

Este script realiza a limpeza de arquivos temporários e caches Python,
além de gerenciar arquivos redundantes mantendo apenas as versões mais recentes.
"""

import os
import shutil
import glob
import re
import argparse
from datetime import datetime


def limpar_arquivos_temporarios(dry_run=False, force_all=False, verbose=True):
    """
    Limpa arquivos temporários e caches Python.
    
    Args:
        dry_run (bool): Se True, apenas simula a limpeza sem remover arquivos
        force_all (bool): Se True, remove todos os arquivos nos diretórios especificados
        verbose (bool): Se True, exibe mensagens detalhadas durante a execução
    
    Returns:
        tuple: (arquivos_removidos, bytes_liberados) - Contagem de arquivos removidos e espaço liberado
    """
    arquivos_removidos = 0
    bytes_liberados = 0
    
    # Remover diretórios de cache
    caches = glob.glob('**/__pycache__', recursive=True) + ['.pytest_cache']
    for cache in caches:
        if os.path.exists(cache):
            if not dry_run:
                tamanho = get_dir_size(cache)
                shutil.rmtree(cache)
                bytes_liberados += tamanho
                arquivos_removidos += 1
            if verbose:
                acao = "Seria removido" if dry_run else "Removido"
                print(f"🗑️  {acao}: {cache}")
    
    # Diretórios para gerenciar arquivos
    diretorios = ['data/processed', 'data/temp', 'exports/powerbi', 'exports/reports/figures']
    
    # Padrão para identificar timestamps em nomes de arquivos (YYYYMMDD_HHMMSS)
    timestamp_pattern = re.compile(r'_(\d{8}_\d{6})')
    
    for dir_path in diretorios:
        if not os.path.exists(dir_path):
            if verbose:
                print(f"ℹ️  Diretório não encontrado: {dir_path}")
            continue
        
        if force_all:
            # Remover todos os arquivos
            for arquivo in os.listdir(dir_path):
                caminho = os.path.join(dir_path, arquivo)
                if os.path.isfile(caminho):
                    if not dry_run:
                        tamanho = os.path.getsize(caminho)
                        os.remove(caminho)
                        bytes_liberados += tamanho
                        arquivos_removidos += 1
                    if verbose:
                        acao = "Seria removido" if dry_run else "Removido"
                        print(f"🗑️  {acao}: {caminho}")
        else:
            # Agrupar arquivos por tipo
            arquivos = {}
            for arquivo in os.listdir(dir_path):
                caminho = os.path.join(dir_path, arquivo)
                if os.path.isfile(caminho):
                    # Tentar encontrar um timestamp no nome do arquivo
                    match = timestamp_pattern.search(arquivo)
                    
                    # Se não encontrar um timestamp padrão, usar outra estratégia
                    if match:
                        base_name = arquivo.split(match.group(0))[0]
                    else:
                        # Estratégia alternativa: remover números do final do nome
                        base_name = re.sub(r'_\d+$', '', os.path.splitext(arquivo)[0])
                    
                    ext = os.path.splitext(arquivo)[1]
                    key = f"{base_name}{ext}"
                    
                    if key not in arquivos:
                        arquivos[key] = []
                    arquivos[key].append((caminho, os.path.getmtime(caminho)))
            
            # Manter apenas o arquivo mais recente de cada tipo
            for key, files in arquivos.items():
                if len(files) > 1:
                    # Ordenar por data de modificação (mais recente primeiro)
                    files.sort(key=lambda x: x[1], reverse=True)
                    
                    # Manter o primeiro arquivo (mais recente)
                    for caminho, _ in files[1:]:
                        if not dry_run:
                            tamanho = os.path.getsize(caminho)
                            os.remove(caminho)
                            bytes_liberados += tamanho
                            arquivos_removidos += 1
                        if verbose:
                            acao = "Seria removido" if dry_run else "Removido"
                            print(f"🗑️  {acao} (redundante): {caminho}")
    
    return arquivos_removidos, bytes_liberados


def get_dir_size(path):
    """Calcula o tamanho total de um diretório em bytes."""
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size


def format_bytes(size):
    """Formata bytes para uma representação legível (KB, MB, GB)."""
    power = 2**10  # 1024
    n = 0
    labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {labels[n]}"


def main():
    """Função principal para execução do script."""
    parser = argparse.ArgumentParser(description='Limpa arquivos temporários e caches do projeto.')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Simula a limpeza sem remover arquivos')
    parser.add_argument('--force-all', action='store_true',
                        help='Remove todos os arquivos dos diretórios especificados')
    parser.add_argument('--quiet', action='store_true',
                        help='Executa em modo silencioso (sem mensagens)')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("\n====== E-commerce Analytics - Limpeza de Projeto ======")
        print(f"Data e hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Usuário: {os.getenv('USER', 'vitordoliveira')}")
        print("="*56)
        
        if args.dry_run:
            print("MODO SIMULAÇÃO: Nenhum arquivo será removido realmente")
        if args.force_all:
            print("MODO FORÇA TOTAL: Todos os arquivos nos diretórios alvo serão removidos")
        print()
    
    inicio = datetime.now()
    arquivos_removidos, bytes_liberados = limpar_arquivos_temporarios(
        dry_run=args.dry_run,
        force_all=args.force_all,
        verbose=not args.quiet
    )
    
    if not args.quiet:
        print("\n====== Resumo da Limpeza ======")
        print(f"Arquivos/diretórios removidos: {arquivos_removidos}")
        print(f"Espaço liberado: {format_bytes(bytes_liberados)}")
        print(f"Tempo de execução: {(datetime.now() - inicio).total_seconds():.2f} segundos")
        
        if args.dry_run:
            print("\nExecute sem a opção --dry-run para realizar a limpeza efetivamente.")
        
        print("\nLimpeza concluída!")


if __name__ == "__main__":
    main()