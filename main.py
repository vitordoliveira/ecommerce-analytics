#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
E-commerce Analytics - Script Principal
Autor: Vitor Oliveira (https://github.com/vitordoliveira)
Data de Criação: 2025-05-26
Última Atualização: 2025-05-29
"""

import os
import sys
import time
import logging
import argparse
import yaml
import platform
from datetime import datetime
from src.controllers.analise_controller import AnaliseController
from src.controllers.powerbi_controller import PowerBIController
from src.models.obter_dados_ecommerce import ObterDadosEcommerce

# Caminho para o arquivo de configuração
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.yaml')

# Constantes para cores no terminal (ANSI escape codes)
class Cores:
    RESET = "\033[0m"
    NEGRITO = "\033[1m"
    SUBLINHADO = "\033[4m"
    INVERTIDO = "\033[7m"
    
    PRETO = "\033[30m"
    VERMELHO = "\033[31m"
    VERDE = "\033[32m"
    AMARELO = "\033[33m"
    AZUL = "\033[34m"
    MAGENTA = "\033[35m"
    CIANO = "\033[36m"
    BRANCO = "\033[37m"
    
    FUNDO_PRETO = "\033[40m"
    FUNDO_VERMELHO = "\033[41m"
    FUNDO_VERDE = "\033[42m"
    FUNDO_AMARELO = "\033[43m"
    FUNDO_AZUL = "\033[44m"
    FUNDO_MAGENTA = "\033[45m"
    FUNDO_CIANO = "\033[46m"
    FUNDO_BRANCO = "\033[47m"
    
    @staticmethod
    def suporta_cores():
        """Verifica se o terminal suporta cores ANSI."""
        # Verifica sistemas Windows 10+ ou outros sistemas com suporte a cores
        if platform.system() == 'Windows':
            return os.environ.get('TERM') == 'xterm' or \
                   int(platform.release()) >= 10 or \
                   'WT_SESSION' in os.environ  # Windows Terminal
        return True  # Assume suporte em sistemas Unix/Linux/Mac

    @staticmethod
    def desativar_cores():
        """Desativa as cores no terminal."""
        for attr in dir(Cores):
            if not attr.startswith('__') and attr != 'desativar_cores' and attr != 'suporta_cores':
                setattr(Cores, attr, '')


# Configuração de log
def configurar_logging(nivel_log='INFO', arquivo_log=None):
    """
    Configura o sistema de logging da aplicação.
    
    Args:
        nivel_log (str): Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        arquivo_log (str, optional): Caminho para o arquivo de log personalizado
    
    Returns:
        logging.Logger: Logger configurado
    """
    os.makedirs('logs', exist_ok=True)
    
    if arquivo_log is None:
        arquivo_log = f'logs/ecommerce_analytics_{datetime.now().strftime("%Y%m%d")}.log'
    
    # Converter string de nível para constante de logging
    nivel_numerico = getattr(logging, nivel_log.upper(), logging.INFO)
    
    logging.basicConfig(
        level=nivel_numerico,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(arquivo_log),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('ecommerce_analytics')

# Carregar configurações
def carregar_configuracoes():
    """
    Carrega configurações do arquivo YAML.
    
    Returns:
        dict: Configurações carregadas ou valores padrão
    """
    config_padrao = {
        'geral': {
            'diretorio_dados': os.path.join('data', 'raw'),
            'diretorio_processados': os.path.join('data', 'processed'),
            'diretorio_powerbi': os.path.join('exports', 'powerbi'),
            'diretorio_logs': 'logs',
            'formato_data': '%Y-%m-%d',
            'registros_padrao': 5000,
            'usar_cores': True
        },
        'powerbi': {
            'tema_padrao': 'E-commerce Analytics Theme',
            'cores_tema': ['#3A86FF', '#FF006E', '#FB5607', '#FFBE0B', '#8338EC', '#06D6A0']
        },
        'analise': {
            'analises_padrao': ['periodo', 'categoria', 'regiao'],
            'timeout_analise': 300  # segundos
        }
    }
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config_usuario = yaml.safe_load(f)
                
            # Mesclar configurações do usuário com padrões
            if config_usuario:
                for secao, valores in config_usuario.items():
                    if secao in config_padrao:
                        config_padrao[secao].update(valores)
                    else:
                        config_padrao[secao] = valores
    except Exception as e:
        print(f"Erro ao carregar arquivo de configuração: {str(e)}")
        print("Usando configurações padrão.")
    
    return config_padrao

# Salvar configurações
def salvar_configuracoes(config):
    """
    Salva configurações em arquivo YAML.
    
    Args:
        config (dict): Configurações a serem salvas
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {str(e)}")
        return False

# Funções de interface do usuário
def limpar_tela():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_cabecalho():
    """Exibe o cabeçalho da aplicação."""
    limpar_tela()
    print(f"{Cores.FUNDO_AZUL}{Cores.BRANCO}{Cores.NEGRITO}")
    print("=" * 80)
    print("E-COMMERCE ANALYTICS".center(80))
    print("=" * 80)
    print(f"{Cores.RESET}")
    print(f"{Cores.AZUL}Execução iniciada em: {Cores.AMARELO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Cores.RESET}")
    print(f"{Cores.AZUL}Usuário: {Cores.AMARELO}{os.getenv('USERNAME', os.getenv('USER', 'vitordoliveira'))}{Cores.RESET}")
    print("-" * 80)

def exibir_menu_principal():
    """Exibe o menu principal da aplicação."""
    print(f"\n{Cores.NEGRITO}{Cores.VERDE}MENU PRINCIPAL{Cores.RESET}\n")
    print(f"{Cores.AMARELO}== Dados e Análises =={Cores.RESET}")
    print(f"{Cores.CIANO}1.{Cores.RESET} Processar dados e realizar análises")
    
    print(f"\n{Cores.AMARELO}== Power BI =={Cores.RESET}")
    print(f"{Cores.CIANO}2.{Cores.RESET} Gerar dashboard do Power BI")
    print(f"{Cores.CIANO}3.{Cores.RESET} Exportar modelo completo para Power BI")
    print(f"{Cores.CIANO}4.{Cores.RESET} Criar tabela de calendário para Power BI")
    print(f"{Cores.CIANO}5.{Cores.RESET} Gerar tema personalizado para Power BI")
    print(f"{Cores.CIANO}6.{Cores.RESET} Exportar relatório completo (novo)")
    
    print(f"\n{Cores.AMARELO}== Sistema =={Cores.RESET}")
    print(f"{Cores.CIANO}7.{Cores.RESET} Configurações")
    print(f"{Cores.CIANO}8.{Cores.RESET} Ajuda e documentação")
    print(f"{Cores.CIANO}0.{Cores.RESET} Sair")

def exibir_barra_progresso(progresso, total, descricao="Processando", tamanho=40):
    """
    Exibe uma barra de progresso no terminal.
    
    Args:
        progresso (int): Valor atual do progresso
        total (int): Valor total para 100%
        descricao (str): Descrição do processo
        tamanho (int): Tamanho da barra em caracteres
    """
    porcentagem = min(100, int(100 * progresso / total))
    completo = int(tamanho * progresso / total)
    barra = f"{Cores.VERDE}{'█' * completo}{Cores.RESET}{'░' * (tamanho - completo)}"
    
    # Limpa linha atual e imprime a barra
    print(f"\r{Cores.AZUL}{descricao}: {Cores.RESET}{barra} {Cores.AMARELO}{porcentagem}%{Cores.RESET}", end="")
    if progresso >= total:
        print()  # Nova linha quando completo

def selecionar_arquivo_csv(diretorio, mensagem="Escolha um arquivo para processar", permitir_gerar=True):
    """
    Permite ao usuário selecionar um arquivo CSV de um diretório.
    
    Args:
        diretorio (str): Caminho do diretório com os arquivos
        mensagem (str): Mensagem a ser exibida para o usuário
        permitir_gerar (bool): Se True, permite a opção de gerar novos dados
        
    Returns:
        str: Caminho do arquivo selecionado ou None se optar por gerar novos dados
    """
    os.makedirs(diretorio, exist_ok=True)
    arquivos_csv = [f for f in os.listdir(diretorio) if f.endswith('.csv')]
    
    if arquivos_csv:
        print(f"\n{Cores.VERDE}Encontrados {len(arquivos_csv)} arquivos CSV no diretório:{Cores.RESET}")
        for i, arquivo in enumerate(arquivos_csv):
            tamanho = os.path.getsize(os.path.join(diretorio, arquivo)) / 1024  # KB
            data_mod = datetime.fromtimestamp(os.path.getmtime(os.path.join(diretorio, arquivo)))
            data_str = data_mod.strftime('%Y-%m-%d %H:%M')
            print(f"{Cores.CIANO}[{i+1}]{Cores.RESET} {arquivo} {Cores.AZUL}({tamanho:.1f} KB - {data_str}){Cores.RESET}")
        
        opcoes = f"(1-{len(arquivos_csv)}"
        if permitir_gerar:
            opcoes += ", 0 para gerar novos dados"
        opcoes += "): "
        
        try:
            escolha = int(input(f"\n{Cores.AMARELO}{mensagem} {opcoes}{Cores.RESET}"))
            if escolha > 0 and escolha <= len(arquivos_csv):
                arquivo_entrada = os.path.join(diretorio, arquivos_csv[escolha-1])
                print(f"{Cores.VERDE}Selecionado: {os.path.basename(arquivo_entrada)}{Cores.RESET}")
                return arquivo_entrada
            elif escolha == 0 and permitir_gerar:
                print(f"{Cores.AZUL}Gerando novos dados sintéticos...{Cores.RESET}")
                return None
            else:
                print(f"{Cores.VERMELHO}Opção inválida. Gerando novos dados sintéticos...{Cores.RESET}")
                return None
        except ValueError:
            print(f"{Cores.VERMELHO}Entrada inválida. Gerando novos dados sintéticos...{Cores.RESET}")
            return None
    else:
        print(f"\n{Cores.AMARELO}Nenhum arquivo CSV encontrado no diretório.{Cores.RESET}")
        if permitir_gerar:
            print(f"{Cores.AZUL}Será necessário gerar novos dados.{Cores.RESET}")
        return None

def confirmar_acao(mensagem="Deseja continuar?"):
    """
    Solicita confirmação do usuário para uma ação.
    
    Args:
        mensagem (str): Mensagem a ser exibida
        
    Returns:
        bool: True se confirmado, False caso contrário
    """
    while True:
        resposta = input(f"\n{Cores.AMARELO}{mensagem} (s/n): {Cores.RESET}").lower()
        if resposta in ["s", "sim", "y", "yes"]:
            return True
        elif resposta in ["n", "nao", "não", "no"]:
            return False
        print(f"{Cores.VERMELHO}Por favor, responda com 's' ou 'n'.{Cores.RESET}")

def exibir_resultado(titulo, dados):
    """
    Exibe resultados de forma formatada.
    
    Args:
        titulo (str): Título da seção
        dados (dict): Dicionário com os dados a serem exibidos
    """
    print(f"\n{Cores.FUNDO_VERDE}{Cores.PRETO} {titulo} {Cores.RESET}\n")
    for chave, valor in dados.items():
        print(f"{Cores.VERDE}{chave}:{Cores.RESET} {valor}")

# Funções de processamento divididas para melhor organização
def gerar_dados_sinteticos(num_registros, logger):
    """
    Gera dados sintéticos para análise.
    
    Args:
        num_registros (int): Número de registros a gerar
        logger (logging.Logger): Logger para registrar eventos
        
    Returns:
        str: Caminho do arquivo gerado
    """
    logger.info(f"Gerando {num_registros} registros de dados sintéticos")
    
    # Simular barra de progresso durante a geração
    for i in range(10):
        exibir_barra_progresso(i+1, 10, "Gerando dados")
        time.sleep(0.1)
        
    gerador = ObterDadosEcommerce()
    arquivo_entrada = gerador.gerar_dados_sinteticos(num_registros)
    print(f"{Cores.VERDE}Dados gerados: {os.path.basename(arquivo_entrada)}{Cores.RESET}")
    logger.info(f"Dados gerados: {arquivo_entrada}")
    
    return arquivo_entrada

def realizar_analise_periodo(analise_controller, df_processado, logger):
    """
    Realiza análise de vendas por período.
    
    Args:
        analise_controller (AnaliseController): Controlador de análises
        df_processado (DataFrame): Dados processados
        logger (logging.Logger): Logger para registrar eventos
        
    Returns:
        dict: Resultado da análise por período
    """
    # Identificar colunas relevantes
    colunas_data = [col for col in df_processado.columns if 'date' in col.lower()]
    colunas_valor = [col for col in df_processado.columns if 'value' in col.lower() or 'price' in col.lower()]
    
    if not (colunas_data and colunas_valor):
        print(f"{Cores.AMARELO}Não foi possível identificar colunas de data e valor para análise de período.{Cores.RESET}")
        logger.warning("Colunas de data ou valor não encontradas para análise de período")
        return {}
    
    print(f"\n{Cores.AZUL}Realizando análise de vendas por período...{Cores.RESET}")
    logger.info("Iniciando análise de vendas por período")
    
    # Simular barra de progresso durante a análise
    for i in range(3):
        exibir_barra_progresso(i+1, 3, "Analisando períodos")
        time.sleep(0.2)
        
    analises_periodo = analise_controller.analisar_vendas_por_periodo(
        df_processado, 
        coluna_data=colunas_data[0], 
        coluna_valor=colunas_valor[0]
    )
    
    # Mostrar resumo das análises
    print(f"\n{Cores.VERDE}Análise por período concluída:{Cores.RESET}")
    for nome_analise, df_analise in analises_periodo.items():
        print(f"\n{Cores.AMARELO}Período: {nome_analise}{Cores.RESET}")
        print(f"{Cores.CIANO}{df_analise.head()}{Cores.RESET}")
        logger.info(f"Análise de período '{nome_analise}' concluída com {df_analise.shape[0]} registros")
    
    return analises_periodo

def realizar_analise_categoria(analise_controller, df_processado, logger):
    """
    Realiza análise de vendas por categoria.
    
    Args:
        analise_controller (AnaliseController): Controlador de análises
        df_processado (DataFrame): Dados processados
        logger (logging.Logger): Logger para registrar eventos
        
    Returns:
        dict or DataFrame: Resultado da análise por categoria
    """
    if 'product_category' not in df_processado.columns:
        print(f"{Cores.AMARELO}Coluna 'product_category' não encontrada para análise de categoria.{Cores.RESET}")
        logger.warning("Coluna de categoria não encontrada para análise")
        return {}
    
    print(f"\n{Cores.AZUL}Realizando análise de vendas por categoria...{Cores.RESET}")
    logger.info("Iniciando análise de vendas por categoria")
    
    # Simular barra de progresso durante a análise
    for i in range(3):
        exibir_barra_progresso(i+1, 3, "Analisando categorias")
        time.sleep(0.2)
        
    analise_categoria = analise_controller.analisar_vendas_por_categoria(df_processado)
    
    # Verificar se o retorno é um dicionário (pode conter subcategorias) ou DataFrame
    if isinstance(analise_categoria, dict):
        print(f"\n{Cores.VERDE}Análise por categoria concluída:{Cores.RESET}")
        print(f"{Cores.AMARELO}Categorias: {analise_categoria['categorias'].shape[0]}{Cores.RESET}")
        if 'subcategorias' in analise_categoria:
            print(f"{Cores.AMARELO}Subcategorias: {analise_categoria['subcategorias'].shape[0]}{Cores.RESET}")
            print(f"{Cores.CIANO}{analise_categoria['subcategorias'].head()}{Cores.RESET}")
    else:
        print(f"\n{Cores.VERDE}Análise por categoria concluída:{Cores.RESET}")
        print(f"{Cores.CIANO}{analise_categoria.head()}{Cores.RESET}")
        logger.info(f"Análise de categorias concluída com {analise_categoria.shape[0]} registros")
    
    return analise_categoria

def realizar_analise_regiao(analise_controller, df_processado, logger):
    """
    Realiza análise de vendas por região.
    
    Args:
        analise_controller (AnaliseController): Controlador de análises
        df_processado (DataFrame): Dados processados
        logger (logging.Logger): Logger para registrar eventos
        
    Returns:
        DataFrame or None: Resultado da análise por região
    """
    print(f"\n{Cores.AZUL}Realizando análise de vendas por região...{Cores.RESET}")
    logger.info("Iniciando análise de vendas por região")
    
    # Simular barra de progresso durante a análise
    for i in range(3):
        exibir_barra_progresso(i+1, 3, "Analisando regiões")
        time.sleep(0.2)
        
    try:
        analise_regiao = analise_controller.analisar_vendas_por_regiao(df_processado)
        print(f"\n{Cores.VERDE}Análise por região concluída:{Cores.RESET}")
        print(f"{Cores.CIANO}{analise_regiao.head()}{Cores.RESET}")
        logger.info(f"Análise de regiões concluída com {analise_regiao.shape[0]} registros")
        return analise_regiao
    except Exception as e:
        print(f"\n{Cores.AMARELO}Não foi possível realizar análise por região: {str(e)}{Cores.RESET}")
        logger.warning(f"Não foi possível realizar análise por região: {str(e)}")
        return None

def exportar_analises_para_powerbi(analise_controller, analises, logger):
    """
    Exporta análises para uso no Power BI.
    
    Args:
        analise_controller (AnaliseController): Controlador de análises
        analises (dict): Dicionário com as análises
        logger (logging.Logger): Logger para registrar eventos
        
    Returns:
        list: Lista de arquivos exportados
    """
    if not analises:
        return []
    
    print(f"\n{Cores.AZUL}Exportando análises para Power BI...{Cores.RESET}")
    
    for i in range(4):
        exibir_barra_progresso(i+1, 4, "Exportando análises")
        time.sleep(0.1)
        
    arquivos_exportados = analise_controller.exportar_analise_para_powerbi(analises)
    
    print(f"\n{Cores.VERDE}Análises exportadas:{Cores.RESET}")
    for nome, caminho in arquivos_exportados:
        print(f"{Cores.AMARELO}- {nome}:{Cores.RESET} {os.path.basename(caminho)}")
        logger.info(f"Análise '{nome}' exportada para {caminho}")
    
    return arquivos_exportados

def processar_dados_e_analisar(analise_controller, arquivo_entrada, config, logger):
    """
    Processa dados e realiza análises.
    
    Args:
        analise_controller (AnaliseController): Controlador de análises
        arquivo_entrada (str): Caminho do arquivo de entrada
        config (dict): Configurações da aplicação
        logger (logging.Logger): Logger para registrar eventos
        
    Returns:
        dict: Resultado do processamento
    """
    print(f"\n{Cores.FUNDO_AZUL}{Cores.BRANCO} PROCESSAMENTO DE DADOS {Cores.RESET}\n")
    logger.info("Iniciando processamento de dados")
    
    # Verificar se é necessário gerar dados
    if not arquivo_entrada:
        num_registros = config['geral']['registros_padrao']
        try:
            num_registros = int(input(f"{Cores.AMARELO}Quantos registros deseja gerar? (padrão: {num_registros}): {Cores.RESET}") or num_registros)
        except ValueError:
            print(f"{Cores.VERMELHO}Valor inválido. Usando o padrão de {num_registros} registros.{Cores.RESET}")
        
        arquivo_entrada = gerar_dados_sinteticos(num_registros, logger)
    
    print(f"\n{Cores.AZUL}Iniciando processamento dos dados...{Cores.RESET}")
    
    # Processar os dados
    for i in range(5):
        exibir_barra_progresso(i+1, 5, "Processando dados")
        time.sleep(0.2)
        
    resultado = analise_controller.processar_dados_vendas(
        arquivo_entrada, 
        salvar_processado=True, 
        exportar_powerbi=True
    )
    
    df_processado = resultado['dados_processados']
    
    # Mostrar informações do resultado
    print(f"\n{Cores.VERDE}Processamento concluído!{Cores.RESET}")
    print(f"{Cores.AZUL}Número de registros processados: {Cores.AMARELO}{df_processado.shape[0]}{Cores.RESET}")
    print(f"{Cores.AZUL}Colunas disponíveis: {Cores.AMARELO}{', '.join(df_processado.columns)}{Cores.RESET}")
    logger.info(f"Processados {df_processado.shape[0]} registros com {len(df_processado.columns)} colunas")
    
    # Inicializar dicionário de análises
    analises = {}
    
    # Realizar análises configuradas
    analises_ativas = config['analise']['analises_padrao']
    
    # Análise por período
    if 'periodo' in analises_ativas:
        analises_periodo = realizar_analise_periodo(analise_controller, df_processado, logger)
        if analises_periodo:
            analises['periodo'] = analises_periodo
    
    # Análise por categoria
    if 'categoria' in analises_ativas:
        analise_categoria = realizar_analise_categoria(analise_controller, df_processado, logger)
        if analise_categoria:
            analises['categoria'] = analise_categoria
    
    # Análise por região
    if 'regiao' in analises_ativas:
        analise_regiao = realizar_analise_regiao(analise_controller, df_processado, logger)
        if analise_regiao is not None:
            analises['regiao'] = analise_regiao
    
    # Exportar análises para Power BI
    exportar_analises_para_powerbi(analise_controller, analises, logger)
    
    # Mostrar arquivos gerados
    print(f"\n{Cores.VERDE}Arquivos gerados durante o processamento:{Cores.RESET}")
    for tipo, caminho in resultado['arquivos_gerados']:
        print(f"{Cores.AMARELO}- {tipo}:{Cores.RESET} {os.path.basename(caminho)}")
    
    print(f"\n{Cores.FUNDO_VERDE}{Cores.PRETO} O PROCESSO FOI CONCLUÍDO COM SUCESSO! {Cores.RESET}")
    logger.info("Processamento de dados concluído com sucesso")
    
    # Adicionar análises ao resultado
    resultado['analises'] = analises
    
    return resultado

def gerar_dashboard_powerbi(powerbi_controller, analise_controller, arquivo_entrada, config, logger):
    """
    Gera um dashboard do Power BI.
    
    Args:
        powerbi_controller (PowerBIController): Controlador do Power BI
        analise_controller (AnaliseController): Controlador de análises
        arquivo_entrada (str, optional): Arquivo de entrada opcional
        config (dict): Configurações da aplicação
        logger (logging.Logger): Logger para registrar eventos
    """
    print(f"\n{Cores.FUNDO_AZUL}{Cores.BRANCO} GERAÇÃO DE DASHBOARD POWER BI {Cores.RESET}\n")
    logger.info("Iniciando geração de dashboard Power BI")
    
    # Verificar se existem arquivos CSV em exports/powerbi
    powerbi_dir = config['geral']['diretorio_powerbi']
    os.makedirs(powerbi_dir, exist_ok=True)
    arquivos_powerbi = [os.path.join(powerbi_dir, f) for f in os.listdir(powerbi_dir) if f.endswith('.csv')]
    
    if not arquivos_powerbi:
        print(f"{Cores.AMARELO}Nenhum arquivo CSV encontrado na pasta de exports do Power BI.{Cores.RESET}")
        logger.warning("Nenhum arquivo CSV encontrado para dashboard")
        
        if confirmar_acao("Deseja processar dados primeiro?"):
            print(f"{Cores.AZUL}Processando dados primeiro...{Cores.RESET}")
            logger.info("Processando dados antes de gerar dashboard")
            
            # Processar os dados primeiro
            resultado = processar_dados_e_analisar(analise_controller, arquivo_entrada, config, logger)
            df_processado = resultado['dados_processados']
            arquivos_gerados = [caminho for _, caminho in resultado['arquivos_gerados'] if caminho.endswith('.csv')]
            
            # Gerar o dashboard com os arquivos gerados
            print(f"\n{Cores.AZUL}Gerando dashboard com os dados processados...{Cores.RESET}")
            nome_dashboard = input(f"{Cores.AMARELO}Digite um nome para o dashboard (padrão: E-commerce Dashboard): {Cores.RESET}") or "E-commerce Dashboard"
            
            # Simular barra de progresso durante a geração do dashboard
            for i in range(5):
                exibir_barra_progresso(i+1, 5, "Gerando dashboard")
                time.sleep(0.15)
                
            resultado_dashboard = powerbi_controller.gerar_apenas_dashboard(arquivos_gerados, nome_dashboard)
            
            print(f"\n{Cores.VERDE}Arquivos de dashboard gerados:{Cores.RESET}")
            for tipo, caminho in resultado_dashboard['arquivos_gerados']:
                print(f"{Cores.AMARELO}- {tipo}:{Cores.RESET} {os.path.basename(caminho)}")
                logger.info(f"Arquivo de dashboard '{tipo}' gerado: {caminho}")
        else:
            print(f"{Cores.AZUL}Operação cancelada. Voltando ao menu principal...{Cores.RESET}")
            logger.info("Geração de dashboard cancelada pelo usuário")
            return
    
    else:
        print(f"{Cores.VERDE}Encontrados {len(arquivos_powerbi)} arquivos CSV para usar no dashboard:{Cores.RESET}")
        for i, arquivo in enumerate(arquivos_powerbi):
            tamanho = os.path.getsize(arquivo) / 1024  # KB
            data_mod = datetime.fromtimestamp(os.path.getmtime(arquivo))
            data_str = data_mod.strftime('%Y-%m-%d %H:%M')
            print(f"{Cores.CIANO}[{i+1}]{Cores.RESET} {os.path.basename(arquivo)} {Cores.AZUL}({tamanho:.1f} KB - {data_str}){Cores.RESET}")
        
        arquivos_selecionados = []
        selecao = input(f"\n{Cores.AMARELO}Selecione os números dos arquivos a incluir (separados por vírgula, ou 'todos'): {Cores.RESET}")
        
        if selecao.lower() == 'todos':
            arquivos_selecionados = arquivos_powerbi
            logger.info(f"Selecionados todos os {len(arquivos_powerbi)} arquivos para dashboard")
        else:
            try:
                indices = [int(idx.strip()) for idx in selecao.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(arquivos_powerbi):
                        arquivos_selecionados.append(arquivos_powerbi[idx-1])
                logger.info(f"Selecionados {len(arquivos_selecionados)} arquivos para dashboard")
            except ValueError:
                print(f"{Cores.VERMELHO}Seleção inválida. Usando todos os arquivos.{Cores.RESET}")
                arquivos_selecionados = arquivos_powerbi
                logger.warning("Seleção inválida, usando todos os arquivos")
        
        # Gerar o dashboard com os arquivos selecionados
        print(f"\n{Cores.AZUL}Gerando dashboard com {len(arquivos_selecionados)} arquivos...{Cores.RESET}")
        nome_dashboard = input(f"{Cores.AMARELO}Digite um nome para o dashboard (padrão: E-commerce Dashboard): {Cores.RESET}") or "E-commerce Dashboard"
        
        # Simular barra de progresso durante a geração do dashboard
        for i in range(5):
            exibir_barra_progresso(i+1, 5, "Gerando dashboard")
            time.sleep(0.15)
            
        resultado_dashboard = powerbi_controller.gerar_apenas_dashboard(arquivos_selecionados, nome_dashboard)
        
        print(f"\n{Cores.VERDE}Arquivos de dashboard gerados:{Cores.RESET}")
        for tipo, caminho in resultado_dashboard['arquivos_gerados']:
            print(f"{Cores.AMARELO}- {tipo}:{Cores.RESET} {os.path.basename(caminho)}")
            logger.info(f"Arquivo de dashboard '{tipo}' gerado: {caminho}")
    
    print(f"\n{Cores.FUNDO_VERDE}{Cores.PRETO} DASHBOARD GERADO COM SUCESSO! {Cores.RESET}")
    logger.info("Dashboard Power BI gerado com sucesso")

def exportar_modelo_completo(powerbi_controller, analise_controller, arquivo_entrada, config, logger):
    """
    Exporta um modelo completo para o Power BI.
    
    Args:
        powerbi_controller (PowerBIController): Controlador do Power BI
        analise_controller (AnaliseController): Controlador de análises
        arquivo_entrada (str, optional): Arquivo de entrada opcional
        config (dict): Configurações da aplicação
        logger (logging.Logger): Logger para registrar eventos
    """
    print(f"\n{Cores.FUNDO_AZUL}{Cores.BRANCO} EXPORTAÇÃO DE MODELO COMPLETO PARA POWER BI {Cores.RESET}\n")
    logger.info("Iniciando exportação de modelo completo para Power BI")
    
    # Processar os dados se ainda não tiver feito
    print(f"{Cores.AZUL}Processando dados para o modelo...{Cores.RESET}")
    
    # Simular barra de progresso durante o processamento
    for i in range(4):
        exibir_barra_progresso(i+1, 4, "Processando dados")
        time.sleep(0.15)
        
    resultado = analise_controller.processar_dados_vendas(
        arquivo_entrada, 
        salvar_processado=True, 
        exportar_powerbi=False
    )
    
    df_processado = resultado['dados_processados']
    logger.info(f"Dados processados: {df_processado.shape[0]} registros")
    
    # Preparar modelo completo
    nome_modelo = input(f"{Cores.AMARELO}Digite um nome para o modelo (padrão: E-commerce Analytics): {Cores.RESET}") or "E-commerce Analytics"
    
    # Realizar análises para incluir no modelo
    analises = {}
    analises_ativas = config['analise']['analises_padrao']
    
    # Análise por período
    if 'periodo' in analises_ativas:
        analises_periodo = realizar_analise_periodo(analise_controller, df_processado, logger)
        if analises_periodo:
            analises['periodo'] = analises_periodo
    
    # Análise por categoria
    if 'categoria' in analises_ativas:
        analise_categoria = realizar_analise_categoria(analise_controller, df_processado, logger)
        if analise_categoria:
            analises['categoria'] = analise_categoria
    
    # Análise por região
    if 'regiao' in analises_ativas:
        analise_regiao = realizar_analise_regiao(analise_controller, df_processado, logger)
        if analise_regiao is not None:
            analises['regiao'] = analise_regiao
    
    # Preparar o modelo completo
    print(f"\n{Cores.AZUL}Preparando modelo completo...{Cores.RESET}")
    
    # Simular barra de progresso durante a preparação do modelo
    for i in range(5):
        exibir_barra_progresso(i+1, 5, "Preparando modelo")
        time.sleep(0.15)
        
    resultado_modelo = powerbi_controller.preparar_modelo_completo(
        df_processado,
        analises=analises,
        nome_modelo=nome_modelo
    )
    
    print(f"\n{Cores.FUNDO_VERDE}{Cores.PRETO} MODELO COMPLETO EXPORTADO! {Cores.RESET}")
    logger.info(f"Modelo completo '{nome_modelo}' exportado com sucesso")
    
    print(f"\n{Cores.VERDE}Arquivos de dados:{Cores.RESET}")
    for nome, caminho in resultado_modelo['arquivos_dados']:
        print(f"{Cores.AMARELO}- {nome}:{Cores.RESET} {os.path.basename(caminho)}")
        logger.info(f"Arquivo de dados '{nome}' gerado: {caminho}")
        
    print(f"\n{Cores.VERDE}Arquivos de suporte:{Cores.RESET}")
    for nome, caminho in resultado_modelo['arquivos_suporte']:
        print(f"{Cores.AMARELO}- {nome}:{Cores.RESET} {os.path.basename(caminho)}")
        logger.info(f"Arquivo de suporte '{nome}' gerado: {caminho}")

def criar_tabela_calendario(powerbi_controller, config, logger):
    """
    Cria uma tabela de calendário para o Power BI.
    
    Args:
        powerbi_controller (PowerBIController): Controlador do Power BI
        config (dict): Configurações da aplicação
        logger (logging.Logger): Logger para registrar eventos
    """
    print(f"\n{Cores.FUNDO_AZUL}{Cores.BRANCO} CRIAÇÃO DE TABELA DE CALENDÁRIO {Cores.RESET}\n")
    logger.info("Iniciando criação de tabela de calendário")
    
    # Obter intervalo de datas do usuário
    ano_atual = datetime.now().year
    data_inicio_padrao = f"{ano_atual}-01-01"
    data_fim_padrao = f"{ano_atual}-12-31"
    
    data_inicio = input(f"{Cores.AMARELO}Data de início (YYYY-MM-DD) [padrão: {data_inicio_padrao}]: {Cores.RESET}") or data_inicio_padrao
    data_fim = input(f"{Cores.AMARELO}Data de fim (YYYY-MM-DD) [padrão: {data_fim_padrao}]: {Cores.RESET}") or data_fim_padrao
    nome_arquivo = input(f"{Cores.AMARELO}Nome do arquivo (sem extensão) [padrão: calendario]: {Cores.RESET}") or "calendario"
    
    try:
        print(f"\n{Cores.AZUL}Criando tabela de calendário...{Cores.RESET}")
        logger.info(f"Criando tabela de calendário de {data_inicio} a {data_fim}")
        
        # Simular barra de progresso durante a criação da tabela
        for i in range(5):
            exibir_barra_progresso(i+1, 5, "Gerando calendário")
            time.sleep(0.1)
            
        calendario_path = powerbi_controller.criar_calendario_powerbi(data_inicio, data_fim, nome_arquivo)
        print(f"\n{Cores.VERDE}Tabela de calendário criada com sucesso: {os.path.basename(calendario_path)}{Cores.RESET}")
        logger.info(f"Tabela de calendário gerada: {calendario_path}")
    except Exception as e:
        print(f"\n{Cores.VERMELHO}Erro ao criar tabela de calendário: {str(e)}{Cores.RESET}")
        print(f"{Cores.AMARELO}Certifique-se de usar o formato de data correto (YYYY-MM-DD){Cores.RESET}")
        logger.error(f"Erro ao criar tabela de calendário: {str(e)}")

def gerar_tema_powerbi(powerbi_controller, config, logger):
    """
    Gera um tema personalizado para o Power BI.
    
    Args:
        powerbi_controller (PowerBIController): Controlador do Power BI
        config (dict): Configurações da aplicação
        logger (logging.Logger): Logger para registrar eventos
    """
    print(f"\n{Cores.FUNDO_AZUL}{Cores.BRANCO} GERAÇÃO DE TEMA PERSONALIZADO {Cores.RESET}\n")
    logger.info("Iniciando geração de tema personalizado para Power BI")
    
    nome_tema = input(f"{Cores.AMARELO}Digite um nome para o tema (padrão: {config['powerbi']['tema_padrao']}): {Cores.RESET}") or config['powerbi']['tema_padrao']
    
    cores_personalizadas = None
    if confirmar_acao("Deseja personalizar as cores do tema?"):
        print(f"\n{Cores.AZUL}Para cada cor, insira um código hexadecimal (ex: #3498DB) ou deixe em branco para usar o padrão.{Cores.RESET}")
        cores_personalizadas = []
        cores_padrao = config['powerbi']['cores_tema']
        
        for i, cor_padrao in enumerate(cores_padrao):
            cor = input(f"{Cores.AMARELO}Cor {i+1} [padrão: {cor_padrao}]: {Cores.RESET}") or cor_padrao
            cores_personalizadas.append(cor)
            logger.info(f"Cor personalizada {i+1}: {cor}")
    
    print(f"\n{Cores.AZUL}Gerando tema personalizado...{Cores.RESET}")
    
    # Simular barra de progresso durante a geração do tema
    for i in range(3):
        exibir_barra_progresso(i+1, 3, "Gerando tema")
        time.sleep(0.1)
        
    try:
        tema_path = powerbi_controller.gerar_tema_powerbi(nome_tema, cores_personalizadas)
        print(f"\n{Cores.VERDE}Tema personalizado gerado com sucesso: {os.path.basename(tema_path)}{Cores.RESET}")
        print(f"{Cores.AZUL}Para aplicar: No Power BI, vá em Visualizar > Temas > Procurar temas{Cores.RESET}")
        logger.info(f"Tema personalizado gerado: {tema_path}")
    except Exception as e:
        print(f"\n{Cores.VERMELHO}Erro ao gerar tema personalizado: {str(e)}{Cores.RESET}")
        logger.error(f"Erro ao gerar tema personalizado: {str(e)}")

def exportar_relatorio_completo(powerbi_controller, analise_controller, arquivo_entrada, config, logger):
    """
    Exporta um relatório completo com dados, análises, visualizações e documentação.
    
    Args:
        powerbi_controller (PowerBIController): Controlador do Power BI
        analise_controller (AnaliseController): Controlador de análises
        arquivo_entrada (str, optional): Arquivo de entrada opcional
        config (dict): Configurações da aplicação
        logger (logging.Logger): Logger para registrar eventos
    """
    print(f"\n{Cores.FUNDO_AZUL}{Cores.BRANCO} EXPORTAÇÃO DE RELATÓRIO COMPLETO {Cores.RESET}\n")
    logger.info("Iniciando exportação de relatório completo")
    
    # Processar os dados se necessário
    print(f"{Cores.AZUL}Processando dados para o relatório...{Cores.RESET}")
    
    # Simular barra de progresso durante o processamento
    for i in range(4):
        exibir_barra_progresso(i+1, 4, "Processando dados")
        time.sleep(0.15)
    
    resultado = processar_dados_e_analisar(analise_controller, arquivo_entrada, config, logger)
    df_processado = resultado['dados_processados']
    analises = resultado['analises']
    
    # Definir nome do relatório
    nome_relatorio = input(f"{Cores.AMARELO}Digite um nome para o relatório (padrão: E-commerce Report): {Cores.RESET}") or "E-commerce Report"
    
    print(f"\n{Cores.AZUL}Gerando relatório completo...{Cores.RESET}")
    logger.info(f"Gerando relatório completo: {nome_relatorio}")
    
    # Simular barra de progresso durante a geração do relatório
    for i in range(5):
        exibir_barra_progresso(i+1, 5, "Gerando relatório")
        time.sleep(0.2)
    
    try:
        resultado_relatorio = powerbi_controller.exportar_relatorio_completo(
            df_processado,
            analises,
            nome_relatorio
        )
        
        print(f"\n{Cores.FUNDO_VERDE}{Cores.PRETO} RELATÓRIO COMPLETO EXPORTADO! {Cores.RESET}")
        logger.info(f"Relatório completo '{nome_relatorio}' exportado com sucesso")
        
        print(f"\n{Cores.VERDE}Arquivos de dados:{Cores.RESET}")
        for nome, caminho in resultado_relatorio['arquivos_dados']:
            print(f"{Cores.AMARELO}- {nome}:{Cores.RESET} {os.path.basename(caminho)}")
            
        if 'visualizacoes' in resultado_relatorio:
            print(f"\n{Cores.VERDE}Visualizações:{Cores.RESET}")
            for nome, caminho in resultado_relatorio['visualizacoes']:
                print(f"{Cores.AMARELO}- {nome}:{Cores.RESET} {os.path.basename(caminho)}")
        
        if 'documentacao' in resultado_relatorio:
            print(f"\n{Cores.VERDE}Documentação:{Cores.RESET}")
            for nome, caminho in resultado_relatorio['documentacao']:
                print(f"{Cores.AMARELO}- {nome}:{Cores.RESET} {os.path.basename(caminho)}")
                
        # Mostrar mensagem com local do relatório principal
        for nome, caminho in resultado_relatorio.get('documentacao', []):
            if nome == 'relatorio_markdown':
                print(f"\n{Cores.AZUL}Relatório principal disponível em: {Cores.AMARELO}{caminho}{Cores.RESET}")
                break
                
    except Exception as e:
        print(f"\n{Cores.VERMELHO}Erro ao exportar relatório completo: {str(e)}{Cores.RESET}")
        logger.error(f"Erro ao exportar relatório completo: {str(e)}")

def exibir_ajuda(logger):
    """Exibe a documentação de ajuda da aplicação."""
    print(f"\n{Cores.FUNDO_AZUL}{Cores.BRANCO} AJUDA E DOCUMENTAÇÃO {Cores.RESET}\n")
    logger.info("Exibindo documentação de ajuda")
    
    print(f"{Cores.VERDE}E-commerce Analytics - Guia Rápido{Cores.RESET}\n")
    
    print(f"{Cores.AMARELO}Funcionalidades Principais:{Cores.RESET}")
    print(f"{Cores.AZUL}1. Processamento de Dados{Cores.RESET}")
    print("   - Importa ou gera dados de e-commerce")
    print("   - Realiza limpeza e transformação")
    print("   - Executa análises básicas (vendas por período, região, etc.)")
    
    print(f"\n{Cores.AZUL}2. Integração com Power BI{Cores.RESET}")
    print("   - Gera dashboards prontos para importação")
    print("   - Cria tabelas auxiliares (calendário)")
    print("   - Exporta temas personalizados")
    print("   - Fornece documentação para uso no Power BI")
    
    print(f"\n{Cores.AMARELO}Fluxo de Trabalho Recomendado:{Cores.RESET}")
    print("1. Processar dados e realizar análises")
    print("2. Criar tabela de calendário para Power BI")
    print("3. Gerar dashboard ou exportar modelo completo")
    print("4. Aplicar tema personalizado no Power BI")
    print("5. Exportar relatório completo para documentação")
    
    print(f"\n{Cores.AMARELO}Arquivos Gerados:{Cores.RESET}")
    print("- CSVs de dados processados: /data/processed/")
    print("- Arquivos para Power BI: /exports/powerbi/")
    print("- Logs e relatórios: /logs/")
    print("- Visualizações: /exports/powerbi/viz/")
    print("- Documentação: /exports/docs/")
    
    print(f"\n{Cores.AMARELO}Para mais informações:{Cores.RESET}")
    print("- Documentação completa: README.md")
    print("- GitHub: https://github.com/vitordoliveira")
    
    print(f"\n{Cores.AMARELO}Linha de Comando:{Cores.RESET}")
    print("O script suporta os seguintes argumentos:")
    print("  --no-color: Desativa cores no terminal")
    print("  --debug: Ativa logs de depuração")
    print("  --file ARQUIVO: Especifica um arquivo de entrada")
    print("  --action AÇÃO: Executa uma ação específica (process, dashboard, etc.)")
    print("  --help: Exibe esta ajuda")
    
    input(f"\n{Cores.VERDE}Pressione ENTER para voltar ao menu principal...{Cores.RESET}")

def exibir_configuracoes(analise_controller, powerbi_controller, config, logger):
    """
    Exibe e permite alterar as configurações da aplicação.
    
    Args:
        analise_controller (AnaliseController): Controlador de análises
        powerbi_controller (PowerBIController): Controlador do Power BI
        config (dict): Configurações da aplicação
        logger (logging.Logger): Logger para registrar eventos
    """
    print(f"\n{Cores.FUNDO_AZUL}{Cores.BRANCO} CONFIGURAÇÕES {Cores.RESET}\n")
    logger.info("Acessando configurações")
    
    # Diretórios
    print(f"{Cores.AMARELO}== Diretórios =={Cores.RESET}")
    dados_dir = config['geral']['diretorio_dados']
    processados_dir = config['geral']['diretorio_processados']
    powerbi_dir = config['geral']['diretorio_powerbi']
    
    print(f"{Cores.AZUL}Diretório de dados brutos:{Cores.RESET} {dados_dir}")
    print(f"{Cores.AZUL}Diretório de dados processados:{Cores.RESET} {processados_dir}")
    print(f"{Cores.AZUL}Diretório de saída do Power BI:{Cores.RESET} {powerbi_dir}")
    
    # Formato de data
    print(f"\n{Cores.AMARELO}== Formato de Data =={Cores.RESET}")
    formato_data = config['geral']['formato_data']
    print(f"{Cores.AZUL}Formato de data atual:{Cores.RESET} {formato_data}")
    
    # Configuração de análises
    print(f"\n{Cores.AMARELO}== Análises Ativas =={Cores.RESET}")
    analises_ativas = config['analise']['analises_padrao']
    print(f"{Cores.AZUL}Análises configuradas:{Cores.RESET} {', '.join(analises_ativas)}")
    
    # Estatísticas
    print(f"\n{Cores.AMARELO}== Estatísticas =={Cores.RESET}")
    
    # Contar arquivos nos diretórios
    num_dados = len([f for f in os.listdir(dados_dir) if f.endswith('.csv')]) if os.path.exists(dados_dir) else 0
    num_processados = len([f for f in os.listdir(processados_dir) if f.endswith('.csv') or f.endswith('.parquet')]) if os.path.exists(processados_dir) else 0
    num_exports = len([f for f in os.listdir(powerbi_dir) if f.endswith('.csv')]) if os.path.exists(powerbi_dir) else 0
    
    print(f"{Cores.AZUL}Arquivos de dados brutos:{Cores.RESET} {num_dados}")
    print(f"{Cores.AZUL}Arquivos processados:{Cores.RESET} {num_processados}")
    print(f"{Cores.AZUL}Arquivos exportados para Power BI:{Cores.RESET} {num_exports}")
    
    # Opções
    print(f"\n{Cores.AMARELO}== Opções =={Cores.RESET}")
    print(f"{Cores.CIANO}1.{Cores.RESET} Limpar arquivos temporários")
    print(f"{Cores.CIANO}2.{Cores.RESET} Redefinir configurações para padrão")
    print(f"{Cores.CIANO}3.{Cores.RESET} Salvar configurações atuais")
    print(f"{Cores.CIANO}4.{Cores.RESET} Alternar uso de cores")
    print(f"{Cores.CIANO}0.{Cores.RESET} Voltar ao menu principal")
    
    try:
        opcao = int(input(f"\n{Cores.AMARELO}Escolha uma opção: {Cores.RESET}"))
        
        if opcao == 1:
            if confirmar_acao("Tem certeza que deseja limpar arquivos temporários?"):
                # Limpar arquivos temporários
                temp_dir = os.path.join('data', 'temp')
                if os.path.exists(temp_dir):
                    count = 0
                    for arquivo in os.listdir(temp_dir):
                        os.remove(os.path.join(temp_dir, arquivo))
                        count += 1
                    print(f"{Cores.VERDE}Arquivos temporários removidos com sucesso! ({count} arquivos){Cores.RESET}")
                    logger.info(f"Removidos {count} arquivos temporários")
                else:
                    print(f"{Cores.AMARELO}Diretório de arquivos temporários não encontrado.{Cores.RESET}")
                    logger.warning("Diretório de arquivos temporários não encontrado")
        
        elif opcao == 2:
            if confirmar_acao("Tem certeza que deseja redefinir as configurações?"):
                # Criar um novo objeto de configuração padrão
                config_padrao = carregar_configuracoes()
                # Substituir a configuração atual
                config.clear()
                config.update(config_padrao)
                # Salvar as configurações padrão
                if salvar_configuracoes(config):
                    print(f"{Cores.VERDE}Configurações redefinidas para padrão!{Cores.RESET}")
                    logger.info("Configurações redefinidas para padrão")
                else:
                    print(f"{Cores.VERMELHO}Erro ao salvar configurações padrão.{Cores.RESET}")
                    logger.error("Erro ao salvar configurações padrão")
        
        elif opcao == 3:
            # Salvar configurações atuais
            if salvar_configuracoes(config):
                print(f"{Cores.VERDE}Configurações salvas com sucesso!{Cores.RESET}")
                logger.info("Configurações salvas com sucesso")
            else:
                print(f"{Cores.VERMELHO}Erro ao salvar configurações.{Cores.RESET}")
                logger.error("Erro ao salvar configurações")
        
        elif opcao == 4:
            # Alternar uso de cores
            config['geral']['usar_cores'] = not config['geral']['usar_cores']
            print(f"{Cores.VERDE}Uso de cores {('ativado' if config['geral']['usar_cores'] else 'desativado')}!{Cores.RESET}")
            logger.info(f"Uso de cores {('ativado' if config['geral']['usar_cores'] else 'desativado')}")
            
            if not config['geral']['usar_cores']:
                Cores.desativar_cores()
            
            # Salvar configuração
            salvar_configuracoes(config)
            
    except ValueError:
        print(f"{Cores.VERMELHO}Opção inválida.{Cores.RESET}")
        logger.warning("Opção inválida na tela de configurações")
    
    input(f"\n{Cores.VERDE}Pressione ENTER para voltar ao menu principal...{Cores.RESET}")

def exibir_proximos_passos():
    """Exibe informações sobre os próximos passos após o processamento."""
    print(f"\n{Cores.FUNDO_AZUL}{Cores.BRANCO} PRÓXIMOS PASSOS {Cores.RESET}\n")
    
    print(f"{Cores.VERDE}Para utilizar os resultados no Power BI:{Cores.RESET}")
    print(f"{Cores.AMARELO}1.{Cores.RESET} Abra o Power BI Desktop")
    print(f"{Cores.AMARELO}2.{Cores.RESET} Importe os arquivos gerados na pasta 'exports/powerbi'")
    print(f"{Cores.AMARELO}3.{Cores.RESET} Se disponível, aplique o tema personalizado")
    print(f"{Cores.AMARELO}4.{Cores.RESET} Crie seus dashboards e análises ou use o template gerado")
    
    print(f"\n{Cores.VERDE}Dicas para melhores resultados:{Cores.RESET}")
    print("- Utilize a tabela de calendário para filtros de data")
    print("- Estabeleça relacionamentos entre as tabelas")
    print("- Aplique as medidas DAX recomendadas")
    print("- Consulte a documentação gerada para referência")
    
    input(f"\n{Cores.AMARELO}Pressione ENTER para continuar...{Cores.RESET}")

def parse_args():
    """
    Analisa os argumentos de linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos analisados
    """
    parser = argparse.ArgumentParser(description='E-commerce Analytics - Análise de dados de e-commerce')
    
    parser.add_argument('--no-color', action='store_true', help='Desativar cores no terminal')
    parser.add_argument('--debug', action='store_true', help='Ativar logs de depuração')
    parser.add_argument('--file', type=str, help='Especificar um arquivo de entrada')
    parser.add_argument('--action', type=str, choices=['process', 'dashboard', 'model', 'calendar', 'theme', 'report'],
                        help='Executar uma ação específica')
    
    return parser.parse_args()

def main():
    """
    Função principal que executa o fluxo completo de análise de e-commerce.
    """
    # Analisar argumentos de linha de comando
    args = parse_args()
    
    # Carregar configurações
    config = carregar_configuracoes()
    
    # Configurar logging
    nivel_log = 'DEBUG' if args.debug else 'INFO'
    logger = configurar_logging(nivel_log)
    
    # Verificar suporte a cores e preferências
    if args.no_color or not config['geral']['usar_cores'] or not Cores.suporta_cores():
        Cores.desativar_cores()
        logger.info("Cores desativadas")
    else:
        # Habilitar cores ANSI no Windows
        if platform.system() == 'nt':
            os.system('color')
        logger.info("Cores ativadas")
    
    # Inicializar controladores
    analise_controller = AnaliseController()
    powerbi_controller = PowerBIController()
    
    # Verificar se existe um arquivo específico fornecido como argumento
    arquivo_entrada = args.file
    
    # Executar ação específica se fornecida
    if args.action:
        logger.info(f"Executando ação específica: {args.action}")
        
        if args.action == 'process':
            processar_dados_e_analisar(analise_controller, arquivo_entrada, config, logger)
        elif args.action == 'dashboard':
            gerar_dashboard_powerbi(powerbi_controller, analise_controller, arquivo_entrada, config, logger)
        elif args.action == 'model':
            exportar_modelo_completo(powerbi_controller, analise_controller, arquivo_entrada, config, logger)
        elif args.action == 'calendar':
            criar_tabela_calendario(powerbi_controller, config, logger)
        elif args.action == 'theme':
            gerar_tema_powerbi(powerbi_controller, config, logger)
        elif args.action == 'report':
            exportar_relatorio_completo(powerbi_controller, analise_controller, arquivo_entrada, config, logger)
        
        return 0
    
    # Loop principal do menu interativo
    while True:
        exibir_cabecalho()
        exibir_menu_principal()
        
        try:
            opcao = int(input(f"\n{Cores.AMARELO}Escolha uma opção: {Cores.RESET}"))
            logger.info(f"Opção selecionada: {opcao}")
        except ValueError:
            print(f"{Cores.VERMELHO}Opção inválida. Por favor, digite um número.{Cores.RESET}")
            logger.warning("Entrada inválida no menu principal")
            time.sleep(1.5)
            continue
        
        # Sair do programa se a opção for 0
        if opcao == 0:
            print(f"{Cores.VERDE}Saindo do programa...{Cores.RESET}")
            logger.info("Programa encerrado normalmente")
            return 0
        
        # Para opções que exigem dados de entrada
        arquivo_entrada = None
        if opcao in [1, 2, 3, 6]:
            arquivo_entrada = selecionar_arquivo_csv(config['geral']['diretorio_dados'])
        
        # Executar a opção escolhida
        try:
            if opcao == 1:
                # Processar dados e realizar análises
                resultado = processar_dados_e_analisar(analise_controller, arquivo_entrada, config, logger)
                exibir_proximos_passos()
                
            elif opcao == 2:
                # Gerar dashboard do Power BI
                gerar_dashboard_powerbi(powerbi_controller, analise_controller, arquivo_entrada, config, logger)
                exibir_proximos_passos()
                
            elif opcao == 3:
                # Exportar modelo completo para Power BI
                exportar_modelo_completo(powerbi_controller, analise_controller, arquivo_entrada, config, logger)
                exibir_proximos_passos()
            
            elif opcao == 4:
                # Criar tabela de calendário para Power BI
                criar_tabela_calendario(powerbi_controller, config, logger)
                exibir_proximos_passos()
                
            elif opcao == 5:
                # Gerar tema personalizado para Power BI
                gerar_tema_powerbi(powerbi_controller, config, logger)
                exibir_proximos_passos()
                
            elif opcao == 6:
                # Exportar relatório completo (novo)
                exportar_relatorio_completo(powerbi_controller, analise_controller, arquivo_entrada, config, logger)
                exibir_proximos_passos()
                
            elif opcao == 7:
                # Configurações
                exibir_configuracoes(analise_controller, powerbi_controller, config, logger)
                
            elif opcao == 8:
                # Ajuda e documentação
                exibir_ajuda(logger)
                
            else:
                print(f"{Cores.VERMELHO}Opção inválida. Por favor, escolha uma opção válida.{Cores.RESET}")
                logger.warning(f"Opção inválida selecionada: {opcao}")
                time.sleep(1.5)
                
        except Exception as e:
            print(f"\n{Cores.FUNDO_VERMELHO}{Cores.BRANCO} ERRO: Ocorreu um problema durante o processamento: {str(e)} {Cores.RESET}")
            logger.error(f"Erro durante a execução: {str(e)}", exc_info=True)
            if confirmar_acao("Deseja ver o rastreamento completo do erro?"):
                import traceback
                traceback.print_exc()
            input(f"\n{Cores.AMARELO}Pressione ENTER para continuar...{Cores.RESET}")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Cores.AMARELO}Operação interrompida pelo usuário. Saindo...{Cores.RESET}")
        logging.getLogger('ecommerce_analytics').info("Programa interrompido pelo usuário (KeyboardInterrupt)")
        sys.exit(0)