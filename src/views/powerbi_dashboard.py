"""
Módulo para geração de dashboards do Power BI.
Fornece funcionalidades para criar templates, temas e tabelas auxiliares para dashboards.

Autor: Vitor Oliveira
Data: 2025-05-28
"""

import os
import json
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import polars as pl

# Configuração de logging
logger = logging.getLogger('ecommerce_analytics.powerbi_dashboard')

class PowerBIDashboard:
    """
    Classe para criação de dashboards e elementos relacionados ao Power BI.
    
    Fornece métodos para gerar templates PBIX, temas personalizados e
    tabelas auxiliares que facilitam a criação de dashboards no Power BI.
    """
    
    def __init__(self, output_path: Optional[str] = None):
        """
        Inicializa o gerador de dashboards com o diretório de saída.
        
        Args:
            output_path (str, optional): Diretório para salvar os arquivos.
                                       Se None, usa o diretório padrão.
        """
        self.output_path = output_path or os.path.join('exports', 'powerbi_templates')
        os.makedirs(self.output_path, exist_ok=True)
        logger.info(f"PowerBIDashboard inicializado com diretório: {self.output_path}")
        
        # Definir estrutura básica para um tema do Power BI
        self.tema_base = {
            "name": "E-commerce Analytics Theme",
            "dataColors": [
                "#01B8AA", "#374649", "#FD625E", "#F2C80F", 
                "#5F6B6D", "#8AD4EB", "#FE9666", "#A66999"
            ],
            "backgroundColor": "#FFFFFF",
            "foregroundColor": "#3A3A3A",
            "tableAccentColor": "#01B8AA"
        }
    
    def gerar_pbix_template(self, nome_dashboard: str, arquivos_dados: List[str]) -> str:
        """
        Gera um template de referência para criação de dashboard no Power BI.
        
        Como o PBIX é um formato binário, este método gera na verdade um arquivo 
        de metadados JSON que descreve como o dashboard deve ser criado manualmente.
        
        Args:
            nome_dashboard (str): Nome do dashboard a ser criado.
            arquivos_dados (List[str]): Lista de caminhos para os arquivos de dados.
            
        Returns:
            str: Caminho para o arquivo de template gerado.
            
        Raises:
            ValueError: Se a lista de arquivos estiver vazia.
        """
        logger.info(f"Gerando template para dashboard: {nome_dashboard}")
        
        # Validar entrada
        if not arquivos_dados:
            logger.error("Lista de arquivos vazia")
            raise ValueError("A lista de arquivos de dados não pode estar vazia")
        
        # Verificar se os arquivos existem
        for arquivo in arquivos_dados:
            if not os.path.exists(arquivo):
                logger.warning(f"Arquivo não encontrado: {arquivo}")
                print(f"Aviso: Arquivo não encontrado: {arquivo}")
        
        try:
            # Criar estrutura de metadados para o template
            metadados = {
                "nome_dashboard": nome_dashboard,
                "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "criado_por": os.getenv('USERNAME', 'vitordoliveira'),
                "arquivos_dados": []
            }
            
            # Adicionar informações sobre os arquivos de dados
            for arquivo in arquivos_dados:
                if os.path.exists(arquivo):
                    tamanho = os.path.getsize(arquivo)
                    nome_base = os.path.basename(arquivo)
                    extensao = os.path.splitext(arquivo)[1].lower()
                    
                    metadados["arquivos_dados"].append({
                        "arquivo": nome_base,
                        "caminho": arquivo,
                        "tamanho_bytes": tamanho,
                        "formato": extensao,
                        "ultima_modificacao": datetime.fromtimestamp(
                            os.path.getmtime(arquivo)
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            # Adicionar instruções de uso para o Power BI
            metadados["instrucoes"] = [
                "1. Abra o Power BI Desktop",
                "2. Clique em 'Obter Dados' e selecione o formato adequado",
                "3. Importe cada um dos arquivos de dados listados",
                "4. Importe o tema personalizado em Exibição > Temas",
                "5. Configure as relações entre as tabelas conforme necessário",
                "6. Crie as visualizações seguindo as recomendações"
            ]
            
            # Adicionar recomendações para visualizações
            metadados["visualizacoes_recomendadas"] = [
                {"tipo": "Gráfico de linhas", "uso": "Tendências de vendas ao longo do tempo"},
                {"tipo": "Gráfico de barras", "uso": "Comparação de categorias"},
                {"tipo": "Gráfico de pizza", "uso": "Distribuição percentual entre categorias"},
                {"tipo": "Cartão", "uso": "KPIs e métricas principais"},
                {"tipo": "Mapa", "uso": "Distribuição geográfica das vendas"}
            ]
            
            # Adicionar recomendações de DAX (linguagem de fórmulas do Power BI)
            metadados["formulas_dax_recomendadas"] = [
                {"nome": "Total de Vendas", "formula": "SUM(Vendas[valor_total])"},
                {"nome": "Média de Vendas", "formula": "AVERAGE(Vendas[valor_total])"},
                {"nome": "Contagem de Clientes", "formula": "DISTINCTCOUNT(Vendas[customer_id])"},
                {"nome": "Vendas MoM", "formula": "CALCULATE([Total de Vendas], DATEADD(Vendas[date], -1, MONTH))"}
            ]
            
            # Salvar metadados como JSON
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"{nome_dashboard.replace(' ', '_').lower()}_template_{timestamp}.json"
            caminho_arquivo = os.path.join(self.output_path, nome_arquivo)
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(metadados, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Template de dashboard gerado: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            logger.error(f"Erro ao gerar template de dashboard: {str(e)}")
            raise RuntimeError(f"Erro ao gerar template de dashboard: {str(e)}")
    
    def gerar_tema_powerbi(self, 
                          nome_tema: str = "E-commerce Analytics Theme", 
                          cores_primarias: Optional[List[str]] = None) -> str:
        """
        Gera um arquivo de tema personalizado para o Power BI.
        
        Args:
            nome_tema (str): Nome do tema a ser gerado.
            cores_primarias (List[str], optional): Lista de cores primárias em formato hex.
                                               Se None, usa cores padrão.
            
        Returns:
            str: Caminho para o arquivo de tema gerado.
            
        Raises:
            ValueError: Se as cores fornecidas tiverem formato inválido.
        """
        logger.info(f"Gerando tema personalizado para Power BI: {nome_tema}")
        
        try:
            # Criar cópia do tema base
            tema = self.tema_base.copy()
            tema["name"] = nome_tema
            
            # Substituir cores primárias se fornecidas
            if cores_primarias:
                # Validar formato das cores (hexadecimal)
                for cor in cores_primarias:
                    if not (cor.startswith('#') and len(cor) == 7):
                        logger.error(f"Formato de cor inválido: {cor}")
                        raise ValueError(f"Formato de cor inválido: {cor}. Use o formato hexadecimal (#RRGGBB)")
                
                # Atualizar cores no tema
                tema["dataColors"] = cores_primarias[:8]  # Limitar a 8 cores
            
            # Salvar tema como JSON
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"{nome_tema.replace(' ', '_').lower()}_{timestamp}.json"
            caminho_arquivo = os.path.join(self.output_path, nome_arquivo)
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(tema, f, indent=2)
            
            logger.info(f"Tema personalizado gerado: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            logger.error(f"Erro ao gerar tema personalizado: {str(e)}")
            raise RuntimeError(f"Erro ao gerar tema personalizado: {str(e)}")
    
    def criar_calendario_powerbi(self, 
                                data_inicio: str, 
                                data_fim: str, 
                                nome_arquivo: str = "calendario") -> str:
        """
        Cria uma tabela de calendário para uso no Power BI.
        
        Args:
            data_inicio (str): Data de início no formato 'YYYY-MM-DD'.
            data_fim (str): Data de fim no formato 'YYYY-MM-DD'.
            nome_arquivo (str): Nome do arquivo de saída (sem extensão).
            
        Returns:
            str: Caminho para o arquivo de calendário gerado.
            
        Raises:
            ValueError: Se as datas forem inválidas.
        """
        logger.info(f"Criando tabela de calendário de {data_inicio} a {data_fim}")
        
        try:
            # Converter strings para datetime
            try:
                dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
                dt_fim = datetime.strptime(data_fim, '%Y-%m-%d')
            except ValueError as e:
                logger.error(f"Formato de data inválido: {str(e)}")
                raise ValueError(f"Formato de data inválido. Use o formato 'YYYY-MM-DD': {str(e)}")
            
            # Verificar se a data de início é anterior à data de fim
            if dt_inicio > dt_fim:
                logger.warning("Data de início posterior à data de fim. Invertendo datas.")
                dt_inicio, dt_fim = dt_fim, dt_inicio
            
            # Gerar lista de datas
            datas = []
            data_atual = dt_inicio
            
            # Limitar a 10 anos (3650 dias) para evitar tabelas muito grandes
            max_dias = 3650
            dias_totais = (dt_fim - dt_inicio).days
            if dias_totais > max_dias:
                logger.warning(f"Intervalo de datas muito grande ({dias_totais} dias). Limitando a {max_dias} dias.")
                dt_fim = dt_inicio + timedelta(days=max_dias)
            
            while data_atual <= dt_fim:
                datas.append(data_atual)
                data_atual += timedelta(days=1)
            
            # Criar DataFrame
            dados_calendario = []
            for data in datas:
                dados_calendario.append({
                    'Data': data,
                    'Ano': data.year,
                    'Mês': data.month,
                    'Dia': data.day,
                    'DiaSemana': data.weekday(),
                    'NomeDiaSemana': data.strftime('%A'),
                    'NomeMes': data.strftime('%B'),
                    'Trimestre': (data.month - 1) // 3 + 1,
                    'Semestre': 1 if data.month <= 6 else 2,
                    'DiaAno': int(data.strftime('%j')),
                    'Semana': int(data.strftime('%W')),
                    'DataTexto': data.strftime('%Y-%m-%d'),
                    'AnoMes': data.strftime('%Y-%m'),
                    'AnoTrimestre': f"{data.year}-Q{(data.month - 1) // 3 + 1}",
                    'FimSemana': data.weekday() >= 5,
                    'DiaUtil': data.weekday() < 5
                })
            
            # Criar DataFrame do pandas
            df = pd.DataFrame(dados_calendario)
            
            # Definir 'Data' como índice, mas manter como coluna também
            df = df.set_index('Data', drop=False)
            
            # Salvar como CSV
            if not nome_arquivo.lower().endswith('.csv'):
                nome_arquivo = f"{nome_arquivo}.csv"
                
            caminho_arquivo = os.path.join(self.output_path, nome_arquivo)
            df.to_csv(caminho_arquivo, index=False)
            
            logger.info(f"Tabela de calendário criada com {len(df)} registros: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            logger.error(f"Erro ao criar tabela de calendário: {str(e)}")
            raise RuntimeError(f"Erro ao criar tabela de calendário: {str(e)}")
    
    def criar_hierarquia_produtos(self, 
                                 df: pd.DataFrame,
                                 col_categoria: str = 'product_category',
                                 col_produto: str = 'product_id',
                                 nome_arquivo: str = 'hierarquia_produtos') -> str:
        """
        Cria uma tabela de hierarquia de produtos para uso no Power BI.
        
        Args:
            df (pd.DataFrame): DataFrame com dados de produtos.
            col_categoria (str): Nome da coluna de categoria de produto.
            col_produto (str): Nome da coluna de ID do produto.
            nome_arquivo (str): Nome do arquivo de saída (sem extensão).
            
        Returns:
            str: Caminho para o arquivo de hierarquia gerado.
            
        Raises:
            ValueError: Se as colunas necessárias não estiverem presentes no DataFrame.
        """
        logger.info("Criando tabela de hierarquia de produtos")
        
        # Verificar se as colunas necessárias existem
        for col in [col_categoria, col_produto]:
            if col not in df.columns:
                logger.error(f"Coluna '{col}' não encontrada no DataFrame")
                raise ValueError(f"Coluna '{col}' não encontrada no DataFrame")
        
        try:
            # Obter produtos únicos com suas categorias
            produtos_unicos = df[[col_produto, col_categoria]].drop_duplicates()
            
            # Contar ocorrências de cada produto (para estatística)
            contagem_produtos = df[col_produto].value_counts().reset_index()
            contagem_produtos.columns = [col_produto, 'contagem']
            
            # Juntar as informações
            hierarquia = produtos_unicos.merge(contagem_produtos, on=col_produto, how='left')
            
            # Criar coluna para o Power BI exibir a hierarquia
            hierarquia['hierarquia'] = hierarquia[col_categoria]
            
            # Salvar como CSV
            if not nome_arquivo.lower().endswith('.csv'):
                nome_arquivo = f"{nome_arquivo}.csv"
                
            caminho_arquivo = os.path.join(self.output_path, nome_arquivo)
            hierarquia.to_csv(caminho_arquivo, index=False)
            
            logger.info(f"Tabela de hierarquia de produtos criada com {len(hierarquia)} registros: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            logger.error(f"Erro ao criar tabela de hierarquia de produtos: {str(e)}")
            raise RuntimeError(f"Erro ao criar tabela de hierarquia de produtos: {str(e)}")
    
    def criar_mapa_regiao(self, 
                         df: pd.DataFrame,
                         col_regiao: str = 'state',
                         nome_arquivo: str = 'mapa_regiao') -> str:
        """
        Cria uma tabela de mapeamento de regiões para uso em visualizações geográficas.
        
        Nota: Em um sistema real, este método usaria dados geográficos precisos.
        Para este exemplo, usamos dados fictícios para estados brasileiros.
        
        Args:
            df (pd.DataFrame): DataFrame com dados contendo regiões.
            col_regiao (str): Nome da coluna de região/estado.
            nome_arquivo (str): Nome do arquivo de saída (sem extensão).
            
        Returns:
            str: Caminho para o arquivo de mapeamento gerado.
            
        Raises:
            ValueError: Se a coluna de região não estiver presente no DataFrame.
        """
        logger.info("Criando tabela de mapeamento de regiões")
        
        # Verificar se a coluna de região existe
        if col_regiao not in df.columns:
            logger.error(f"Coluna '{col_regiao}' não encontrada no DataFrame")
            raise ValueError(f"Coluna '{col_regiao}' não encontrada no DataFrame")
        
        try:
            # Dados geográficos fictícios para exemplificar
            # Em um sistema real, usaríamos coordenadas precisas
            mapa_estados = {
                'SP': {'latitude': -23.5505, 'longitude': -46.6333, 'regiao': 'Sudeste'},
                'RJ': {'latitude': -22.9068, 'longitude': -43.1729, 'regiao': 'Sudeste'},
                'MG': {'latitude': -19.9167, 'longitude': -43.9345, 'regiao': 'Sudeste'},
                'RS': {'latitude': -30.0346, 'longitude': -51.2177, 'regiao': 'Sul'},
                'PR': {'latitude': -25.4284, 'longitude': -49.2733, 'regiao': 'Sul'},
                'SC': {'latitude': -27.5954, 'longitude': -48.5480, 'regiao': 'Sul'},
                'BA': {'latitude': -12.9714, 'longitude': -38.5014, 'regiao': 'Nordeste'},
                'PE': {'latitude': -8.0476, 'longitude': -34.8770, 'regiao': 'Nordeste'},
                'CE': {'latitude': -3.7172, 'longitude': -38.5433, 'regiao': 'Nordeste'},
                'GO': {'latitude': -16.6864, 'longitude': -49.2643, 'regiao': 'Centro-Oeste'},
                'DF': {'latitude': -15.7801, 'longitude': -47.9292, 'regiao': 'Centro-Oeste'},
                'MT': {'latitude': -15.5989, 'longitude': -56.0949, 'regiao': 'Centro-Oeste'},
                'AM': {'latitude': -3.1190, 'longitude': -60.0217, 'regiao': 'Norte'},
                'PA': {'latitude': -1.4558, 'longitude': -48.4902, 'regiao': 'Norte'}
            }
            
            # Obter regiões únicas do DataFrame
            regioes_unicas = df[col_regiao].dropna().unique()
            
            # Criar dados de mapeamento
            dados_mapa = []
            for regiao in regioes_unicas:
                regiao_str = str(regiao).upper()  # Converter para string e maiúsculo
                
                # Buscar dados geográficos ou usar valores padrão
                if regiao_str in mapa_estados:
                    dados = mapa_estados[regiao_str]
                    dados_mapa.append({
                        'estado': regiao,
                        'estado_nome': self._obter_nome_estado(regiao_str),
                        'latitude': dados['latitude'],
                        'longitude': dados['longitude'],
                        'regiao': dados['regiao']
                    })
                else:
                    # Para estados não mapeados, atribuir coordenadas fictícias
                    logger.warning(f"Estado não mapeado: {regiao_str}")
                    dados_mapa.append({
                        'estado': regiao,
                        'estado_nome': regiao_str,
                        'latitude': 0.0,
                        'longitude': 0.0,
                        'regiao': 'Não categorizado'
                    })
            
            # Criar DataFrame
            df_mapa = pd.DataFrame(dados_mapa)
            
            # Salvar como CSV
            if not nome_arquivo.lower().endswith('.csv'):
                nome_arquivo = f"{nome_arquivo}.csv"
                
            caminho_arquivo = os.path.join(self.output_path, nome_arquivo)
            df_mapa.to_csv(caminho_arquivo, index=False)
            
            logger.info(f"Tabela de mapeamento de regiões criada com {len(df_mapa)} registros: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            logger.error(f"Erro ao criar tabela de mapeamento de regiões: {str(e)}")
            raise RuntimeError(f"Erro ao criar tabela de mapeamento de regiões: {str(e)}")
    
    def _obter_nome_estado(self, sigla: str) -> str:
        """
        Retorna o nome completo do estado a partir da sigla.
        
        Args:
            sigla (str): Sigla do estado.
            
        Returns:
            str: Nome completo do estado ou a própria sigla se não encontrado.
        """
        mapa_nomes = {
            'AC': 'Acre',
            'AL': 'Alagoas',
            'AP': 'Amapá',
            'AM': 'Amazonas',
            'BA': 'Bahia',
            'CE': 'Ceará',
            'DF': 'Distrito Federal',
            'ES': 'Espírito Santo',
            'GO': 'Goiás',
            'MA': 'Maranhão',
            'MT': 'Mato Grosso',
            'MS': 'Mato Grosso do Sul',
            'MG': 'Minas Gerais',
            'PA': 'Pará',
            'PB': 'Paraíba',
            'PR': 'Paraná',
            'PE': 'Pernambuco',
            'PI': 'Piauí',
            'RJ': 'Rio de Janeiro',
            'RN': 'Rio Grande do Norte',
            'RS': 'Rio Grande do Sul',
            'RO': 'Rondônia',
            'RR': 'Roraima',
            'SC': 'Santa Catarina',
            'SP': 'São Paulo',
            'SE': 'Sergipe',
            'TO': 'Tocantins'
        }
        
        return mapa_nomes.get(sigla, sigla)

# Se executado como script
if __name__ == "__main__":
    # Configuração de logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("POWER BI DASHBOARD GENERATOR - TESTE".center(60))
    print("=" * 60)
    print(f"Data e Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Usuário: {os.getenv('USERNAME', 'vitordoliveira')}")
    print("-" * 60)
    
    # Demonstração rápida
    dashboard = PowerBIDashboard()
    
    # 1. Gerar tema personalizado
    print("\n1. Gerando tema personalizado para Power BI...")
    caminho_tema = dashboard.gerar_tema_powerbi(
        "E-commerce Insights Theme", 
        ["#3366CC", "#DC3912", "#FF9900", "#109618", "#990099", "#0099C6", "#DD4477", "#66AA00"]
    )
    print(f"Tema gerado: {caminho_tema}")
    
    # 2. Criar tabela de calendário
    print("\n2. Criando tabela de calendário...")
    data_inicio = "2025-01-01"
    data_fim = "2025-12-31"
    caminho_calendario = dashboard.criar_calendario_powerbi(data_inicio, data_fim, "calendario_2025")
    print(f"Tabela de calendário criada: {caminho_calendario}")
    
    # 3. Gerar template PBIX (na verdade, o arquivo de metadados)
    print("\n3. Gerando template para dashboard...")
    arquivos_teste = [caminho_calendario]
    caminho_template = dashboard.gerar_pbix_template("E-commerce Sales Dashboard", arquivos_teste)
    print(f"Template gerado: {caminho_template}")
    
    print("\nProcesso concluído com sucesso!")