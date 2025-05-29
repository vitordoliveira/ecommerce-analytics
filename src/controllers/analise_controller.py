"""
Controlador para análise de dados de e-commerce.
Coordena o processamento e análise de dados de vendas.

Autor: Vitor Oliveira
Data: 2025-05-28
"""

import os
import polars as pl
import logging
from datetime import datetime
from typing import Dict, Tuple, List, Optional, Any

from src.models.ecommerce_model import EcommerceModel
from src.views.powerbi_exporter import PowerBIExporter

# Configuração de logging
logger = logging.getLogger('ecommerce_analytics.controller')

class AnaliseController:
    """
    Controlador responsável por coordenar análises de dados de e-commerce.
    
    Esta classe integra os modelos e as visualizações, processando dados brutos
    e gerando análises específicas para insights de negócio.
    """
    
    def __init__(self):
        """
        Inicializa o controlador com as dependências necessárias.
        """
        self.model = EcommerceModel()
        self.powerbi_exporter = PowerBIExporter()
        self.processed_path = os.path.join('data', 'processed')
        os.makedirs(self.processed_path, exist_ok=True)
        logger.info("AnaliseController inicializado")
    
    def processar_dados_vendas(self, 
                               arquivo_entrada: Optional[str] = None, 
                               salvar_processado: bool = True,
                               exportar_powerbi: bool = False) -> Dict[str, Any]:
        """
        Processa dados de vendas de e-commerce a partir de um arquivo.
        
        Args:
            arquivo_entrada (str, optional): Caminho do arquivo de entrada.
                                           Se None, solicita a geração de dados.
            salvar_processado (bool): Se True, salva os dados processados.
            exportar_powerbi (bool): Se True, exporta os dados para Power BI.
            
        Returns:
            Dict[str, Any]: Dicionário com os resultados do processamento.
            
        Raises:
            FileNotFoundError: Se o arquivo de entrada não for encontrado.
            ValueError: Se os dados forem inválidos.
        """
        logger.info(f"Iniciando processamento de dados: arquivo={arquivo_entrada}")
        resultado = {
            'dados_processados': None,
            'resumo': None,
            'arquivos_gerados': []
        }
        
        try:
            # Se não foi fornecido arquivo, gerar dados sintéticos
            if not arquivo_entrada:
                logger.info("Arquivo de entrada não fornecido, solicitando geração de dados")
                from src.models.obter_dados_ecommerce import ObterDadosEcommerce
                gerador = ObterDadosEcommerce()
                arquivo_entrada = gerador.gerar_dados_sinteticos(5000)
                resultado['arquivos_gerados'].append(('dados_sinteticos', arquivo_entrada))
                logger.info(f"Dados sintéticos gerados: {arquivo_entrada}")
                
                # Gerar também dados de clientes para análises mais completas
                try:
                    arquivo_clientes = gerador.gerar_dados_clientes(1000)
                    if arquivo_clientes:
                        resultado['arquivos_gerados'].append(('dados_clientes', arquivo_clientes))
                        logger.info(f"Dados de clientes gerados: {arquivo_clientes}")
                except Exception as e:
                    logger.warning(f"Não foi possível gerar dados de clientes: {str(e)}")
            
            # Carregar dados
            logger.info(f"Carregando dados do arquivo: {arquivo_entrada}")
            df = self.model.load_data(arquivo_entrada)
            
            # Processar dados
            logger.info("Processando dados...")
            df_processado = self.model.process_sales_data(df)
            resultado['dados_processados'] = df_processado
            
            # Gerar resumo estatístico
            logger.info("Gerando resumo estatístico...")
            resumo = self.model.summarize_data(df_processado)
            resultado['resumo'] = resumo
            
            # Salvar dados processados
            if salvar_processado:
                logger.info("Salvando dados processados...")
                nome_arquivo = os.path.basename(arquivo_entrada)
                caminho_salvo = self.model.save_processed_data(df_processado, nome_arquivo)
                resultado['arquivos_gerados'].append(('dados_processados', caminho_salvo))
                logger.info(f"Dados processados salvos em: {caminho_salvo}")
            
            # Exportar para Power BI
            if exportar_powerbi:
                logger.info("Exportando dados para Power BI...")
                caminho_powerbi = self.powerbi_exporter.export_to_csv(
                    df_processado, 
                    f"ecommerce_processado_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                resultado['arquivos_gerados'].append(('powerbi_export', caminho_powerbi))
                logger.info(f"Dados exportados para Power BI: {caminho_powerbi}")
                
                # Exportar também template de métricas, se disponível
                try:
                    from src.views.powerbi_template import PowerBITemplate
                    powerbi_template = PowerBITemplate()
                    template_path = powerbi_template.gerar_template_metricas("E-commerce Analytics")
                    resultado['arquivos_gerados'].append(('powerbi_template', template_path))
                    logger.info(f"Template de métricas gerado: {template_path}")
                except Exception as e:
                    logger.warning(f"Não foi possível gerar template de métricas: {str(e)}")
            
            logger.info("Processamento de dados concluído com sucesso")
            return resultado
        
        except FileNotFoundError as e:
            logger.error(f"Arquivo não encontrado: {str(e)}")
            raise FileNotFoundError(f"Arquivo não encontrado: {str(e)}")
        except ValueError as e:
            logger.error(f"Dados inválidos: {str(e)}")
            raise ValueError(f"Dados inválidos: {str(e)}")
        except Exception as e:
            logger.error(f"Erro durante o processamento: {str(e)}", exc_info=True)
            raise RuntimeError(f"Erro durante o processamento: {str(e)}")
    
    def analisar_vendas_por_periodo(self, 
                                   df: pl.DataFrame, 
                                   coluna_data: str = 'date',
                                   coluna_valor: str = 'total_value') -> Dict[str, pl.DataFrame]:
        """
        Analisa vendas por diferentes períodos (dia, mês, ano).
        
        Args:
            df (pl.DataFrame): DataFrame com os dados de vendas.
            coluna_data (str): Nome da coluna com as datas.
            coluna_valor (str): Nome da coluna com os valores de venda.
            
        Returns:
            Dict[str, pl.DataFrame]: Dicionário com os DataFrames das análises.
            
        Raises:
            ValueError: Se as colunas especificadas não existirem no DataFrame.
            TypeError: Se o input não for um DataFrame do Polars.
        """
        logger.info(f"Iniciando análise de vendas por período: coluna_data={coluna_data}, coluna_valor={coluna_valor}")
        
        # Validar entrada
        if not isinstance(df, pl.DataFrame):
            logger.error("O argumento df deve ser um DataFrame do Polars")
            raise TypeError("O argumento df deve ser um DataFrame do Polars")
        
        # Verificar se as colunas existem
        if coluna_data not in df.columns:
            logger.error(f"Coluna de data '{coluna_data}' não encontrada no DataFrame")
            raise ValueError(f"Coluna de data '{coluna_data}' não encontrada no DataFrame")
        
        if coluna_valor not in df.columns:
            logger.error(f"Coluna de valor '{coluna_valor}' não encontrada no DataFrame")
            raise ValueError(f"Coluna de valor '{coluna_valor}' não encontrada no DataFrame")
        
        # Garantir que a coluna de data seja do tipo datetime
        try:
            # Converter se ainda não for datetime
            if not pl.datatypes.is_temporal(df[coluna_data].dtype):
                logger.info(f"Convertendo coluna {coluna_data} para datetime")
                df = df.with_columns(
                    pl.col(coluna_data).str.to_datetime(strict=False).alias(coluna_data)
                )
        except Exception as e:
            logger.error(f"Erro ao converter coluna de data: {str(e)}")
            raise ValueError(f"Não foi possível converter a coluna {coluna_data} para datetime: {str(e)}")
        
        analises = {}
        
        # 1. Análise por dia
        logger.info("Realizando análise de vendas por dia")
        try:
            vendas_por_dia = df.select([
                pl.col(coluna_data).dt.date().alias("data"),
                pl.col(coluna_valor).sum().alias("valor_total"),
                pl.col(coluna_valor).count().alias("num_transacoes")
            ]).group_by("data").agg([
                pl.col("valor_total"),
                pl.col("num_transacoes")
            ]).sort("data")
            
            # Adicionar ticket médio
            vendas_por_dia = vendas_por_dia.with_columns(
                (pl.col("valor_total") / pl.col("num_transacoes")).alias("ticket_medio")
            )
            
            analises['vendas_por_dia'] = vendas_por_dia
            logger.info(f"Análise por dia concluída: {vendas_por_dia.shape[0]} registros")
        except Exception as e:
            logger.warning(f"Erro na análise por dia: {str(e)}")
            print(f"Aviso: Não foi possível realizar a análise por dia: {str(e)}")
        
        # 2. Análise por mês
        logger.info("Realizando análise de vendas por mês")
        try:
            vendas_por_mes = df.select([
                pl.col(coluna_data).dt.year().alias("ano"),
                pl.col(coluna_data).dt.month().alias("mes"),
                pl.col(coluna_valor).sum().alias("valor_total"),
                pl.col(coluna_valor).count().alias("num_transacoes")
            ]).group_by(["ano", "mes"]).agg([
                pl.col("valor_total"),
                pl.col("num_transacoes")
            ]).sort(["ano", "mes"])
            
            # Adicionar coluna de mês-ano formatada para visualização
            vendas_por_mes = vendas_por_mes.with_columns([
                pl.concat_str([
                    pl.col("ano").cast(pl.Utf8),
                    pl.lit("-"),
                    pl.col("mes").cast(pl.Utf8).str.zfill(2)
                ]).alias("mes_ano"),
                (pl.col("valor_total") / pl.col("num_transacoes")).alias("ticket_medio")
            ])
            
            analises['vendas_por_mes'] = vendas_por_mes
            logger.info(f"Análise por mês concluída: {vendas_por_mes.shape[0]} registros")
        except Exception as e:
            logger.warning(f"Erro na análise por mês: {str(e)}")
            print(f"Aviso: Não foi possível realizar a análise por mês: {str(e)}")
        
        # 3. Análise por dia da semana
        logger.info("Realizando análise de vendas por dia da semana")
        try:
            vendas_por_dia_semana = df.select([
                pl.col(coluna_data).dt.weekday().alias("dia_semana"),
                pl.col(coluna_valor).sum().alias("valor_total"),
                pl.col(coluna_valor).count().alias("num_transacoes")
            ]).group_by("dia_semana").agg([
                pl.col("valor_total"),
                pl.col("num_transacoes")
            ]).sort("dia_semana")
            
            # Adicionar nomes dos dias da semana
            dias_semana = {
                0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 
                4: "Sexta", 5: "Sábado", 6: "Domingo"
            }
            
            vendas_por_dia_semana = vendas_por_dia_semana.with_columns([
                pl.col("dia_semana").map_dict(dias_semana).alias("nome_dia"),
                (pl.col("valor_total") / pl.col("num_transacoes")).alias("ticket_medio")
            ])
            
            analises['vendas_por_dia_semana'] = vendas_por_dia_semana
            logger.info(f"Análise por dia da semana concluída: {vendas_por_dia_semana.shape[0]} registros")
        except Exception as e:
            logger.warning(f"Erro na análise por dia da semana: {str(e)}")
            print(f"Aviso: Não foi possível realizar a análise por dia da semana: {str(e)}")
        
        # 4. Análise por trimestre (se houver dados suficientes)
        logger.info("Verificando possibilidade de análise por trimestre")
        try:
            # Verificar se há dados de pelo menos 3 meses
            meses_unicos = df.select(pl.col(coluna_data).dt.month()).unique().shape[0]
            
            if meses_unicos >= 3:
                logger.info(f"Realizando análise de vendas por trimestre (dados de {meses_unicos} meses disponíveis)")
                vendas_por_trimestre = df.select([
                    pl.col(coluna_data).dt.year().alias("ano"),
                    ((pl.col(coluna_data).dt.month() - 1) / 3 + 1).cast(pl.Int32).alias("trimestre"),
                    pl.col(coluna_valor).sum().alias("valor_total"),
                    pl.col(coluna_valor).count().alias("num_transacoes")
                ]).group_by(["ano", "trimestre"]).agg([
                    pl.col("valor_total"),
                    pl.col("num_transacoes")
                ]).sort(["ano", "trimestre"])
                
                vendas_por_trimestre = vendas_por_trimestre.with_columns([
                    pl.concat_str([
                        pl.col("ano").cast(pl.Utf8),
                        pl.lit("-Q"),
                        pl.col("trimestre").cast(pl.Utf8)
                    ]).alias("ano_trimestre"),
                    (pl.col("valor_total") / pl.col("num_transacoes")).alias("ticket_medio")
                ])
                
                analises['vendas_por_trimestre'] = vendas_por_trimestre
                logger.info(f"Análise por trimestre concluída: {vendas_por_trimestre.shape[0]} registros")
            else:
                logger.info(f"Análise por trimestre ignorada: apenas {meses_unicos} meses de dados disponíveis")
        except Exception as e:
            logger.warning(f"Erro na análise por trimestre: {str(e)}")
        
        logger.info(f"Análise de vendas por período concluída com {len(analises)} análises geradas")
        return analises
    
    def analisar_vendas_por_categoria(self, 
                                     df: pl.DataFrame, 
                                     coluna_categoria: str = 'product_category',
                                     coluna_valor: str = 'total_value') -> pl.DataFrame:
        """
        Analisa vendas por categoria de produto.
        
        Args:
            df (pl.DataFrame): DataFrame com os dados de vendas.
            coluna_categoria (str): Nome da coluna com as categorias.
            coluna_valor (str): Nome da coluna com os valores de venda.
            
        Returns:
            pl.DataFrame: DataFrame com a análise por categoria.
            
        Raises:
            ValueError: Se as colunas especificadas não existirem no DataFrame.
            TypeError: Se o input não for um DataFrame do Polars.
        """
        logger.info(f"Iniciando análise de vendas por categoria: coluna_categoria={coluna_categoria}")
        
        # Validar entrada
        if not isinstance(df, pl.DataFrame):
            logger.error("O argumento df deve ser um DataFrame do Polars")
            raise TypeError("O argumento df deve ser um DataFrame do Polars")
        
        # Verificar se as colunas existem
        if coluna_categoria not in df.columns:
            logger.error(f"Coluna de categoria '{coluna_categoria}' não encontrada no DataFrame")
            raise ValueError(f"Coluna de categoria '{coluna_categoria}' não encontrada no DataFrame")
        
        if coluna_valor not in df.columns:
            logger.error(f"Coluna de valor '{coluna_valor}' não encontrada no DataFrame")
            raise ValueError(f"Coluna de valor '{coluna_valor}' não encontrada no DataFrame")
        
        try:
            # Verificar se há subcategoria
            tem_subcategoria = 'product_subcategory' in df.columns
            
            # Agrupar por categoria e calcular estatísticas
            agg_exprs = [
                pl.col(coluna_valor).sum().alias("valor_total"),
                pl.col(coluna_valor).count().alias("num_transacoes"),
                pl.col(coluna_valor).mean().alias("ticket_medio")
            ]
            
            # Adicionar estatísticas de quantidade, se disponível
            if 'quantity' in df.columns:
                agg_exprs.append(pl.col('quantity').sum().alias("quantidade_total"))
            
            # Adicionar estatísticas de custo, se disponível
            if 'cost_value' in df.columns:
                agg_exprs.append(pl.col('cost_value').sum().alias("custo_total"))
            
            # Agrupar por categoria
            vendas_por_categoria = df.group_by(coluna_categoria).agg(agg_exprs).sort("valor_total", descending=True)
            
            # Adicionar porcentagem do total
            total_vendas = vendas_por_categoria["valor_total"].sum()
            
            # Colunas adicionais
            colunas_adicionais = [(pl.col("valor_total") / total_vendas * 100).round(2).alias("porcentagem")]
            
            # Adicionar margem, se houver custo
            if 'custo_total' in vendas_por_categoria.columns:
                colunas_adicionais.append(
                    ((pl.col("valor_total") - pl.col("custo_total")) / pl.col("valor_total") * 100).round(2).alias("margem_percentual")
                )
            
            vendas_por_categoria = vendas_por_categoria.with_columns(colunas_adicionais)
            
            # Análise por subcategoria, se disponível
            if tem_subcategoria:
                logger.info("Realizando análise por subcategoria")
                try:
                    # Agrupar por categoria e subcategoria
                    vendas_por_subcategoria = df.group_by([coluna_categoria, 'product_subcategory']).agg(agg_exprs)
                    vendas_por_subcategoria = vendas_por_subcategoria.sort(["valor_total"], descending=True)
                    
                    # Retornar ambas análises
                    logger.info(f"Análise por categoria e subcategoria concluída: {vendas_por_categoria.shape[0]} categorias, {vendas_por_subcategoria.shape[0]} subcategorias")
                    return {
                        'categorias': vendas_por_categoria, 
                        'subcategorias': vendas_por_subcategoria
                    }
                except Exception as e:
                    logger.warning(f"Erro na análise por subcategoria: {str(e)}")
            
            logger.info(f"Análise por categoria concluída: {vendas_por_categoria.shape[0]} categorias")
            return vendas_por_categoria
            
        except Exception as e:
            logger.error(f"Erro na análise por categoria: {str(e)}")
            raise RuntimeError(f"Erro ao analisar vendas por categoria: {str(e)}")
    
    def analisar_vendas_por_regiao(self, 
                                  df: pl.DataFrame, 
                                  coluna_regiao: Optional[str] = None,
                                  coluna_valor: str = 'total_value') -> pl.DataFrame:
        """
        Analisa vendas por região/estado.
        
        Args:
            df (pl.DataFrame): DataFrame com os dados de vendas.
            coluna_regiao (str, optional): Nome da coluna com as regiões.
                                          Se None, detecta automaticamente.
            coluna_valor (str): Nome da coluna com os valores de venda.
            
        Returns:
            pl.DataFrame: DataFrame com a análise por região.
            
        Raises:
            ValueError: Se as colunas especificadas não existirem no DataFrame.
            TypeError: Se o input não for um DataFrame do Polars.
        """
        logger.info(f"Iniciando análise de vendas por região")
        
        # Validar entrada
        if not isinstance(df, pl.DataFrame):
            logger.error("O argumento df deve ser um DataFrame do Polars")
            raise TypeError("O argumento df deve ser um DataFrame do Polars")
        
        # Detectar coluna de região se não especificada
        if coluna_regiao is None:
            # Tentar encontrar coluna adequada
            possiveis_colunas = ['region', 'state', 'city', 'country']
            for col in possiveis_colunas:
                if col in df.columns:
                    coluna_regiao = col
                    logger.info(f"Coluna de região detectada: {coluna_regiao}")
                    break
            
            if coluna_regiao is None:
                logger.error("Não foi possível detectar uma coluna de região")
                raise ValueError("Não foi possível detectar uma coluna de região. Especifique manualmente.")
        
        # Verificar se a coluna de região existe
        if coluna_regiao not in df.columns:
            logger.error(f"Coluna de região '{coluna_regiao}' não encontrada no DataFrame")
            raise ValueError(f"Coluna de região '{coluna_regiao}' não encontrada no DataFrame")
        
        # Verificar se a coluna de valor existe
        if coluna_valor not in df.columns:
            logger.error(f"Coluna de valor '{coluna_valor}' não encontrada no DataFrame")
            raise ValueError(f"Coluna de valor '{coluna_valor}' não encontrada no DataFrame")
        
        try:
            # Agrupar por região e calcular estatísticas
            vendas_por_regiao = df.select([
                pl.col(coluna_regiao),
                pl.col(coluna_valor).sum().alias("valor_total"),
                pl.col(coluna_valor).count().alias("num_transacoes"),
                pl.col(coluna_valor).mean().alias("ticket_medio")
            ]).group_by(coluna_regiao).agg([
                pl.col("valor_total"),
                pl.col("num_transacoes"),
                pl.col("ticket_medio")
            ]).sort("valor_total", descending=True)
            
            # Adicionar porcentagem do total
            total_vendas = vendas_por_regiao["valor_total"].sum()
            vendas_por_regiao = vendas_por_regiao.with_columns(
                (pl.col("valor_total") / total_vendas * 100).round(2).alias("porcentagem")
            )
            
            # Verificar se existe coluna de mapeamento regional (region -> state)
            if coluna_regiao == 'state' and 'region' in df.columns:
                try:
                    # Tentar adicionar mapeamento de regiões
                    mapeamento_regiao = {}
                    mapeamento_df = df.select(['state', 'region']).unique()
                    
                    for row in mapeamento_df.to_dicts():
                        if row['state'] and row['region']:
                            mapeamento_regiao[row['state']] = row['region']
                    
                    if mapeamento_regiao:
                        vendas_por_regiao = vendas_por_regiao.with_columns(
                            pl.col('state').map_dict(mapeamento_regiao).alias('macro_region')
                        )
                        logger.info(f"Mapeamento regional adicionado")
                except Exception as e:
                    logger.warning(f"Não foi possível adicionar mapeamento regional: {str(e)}")
            
            logger.info(f"Análise por região concluída: {vendas_por_regiao.shape[0]} regiões")
            return vendas_por_regiao
            
        except Exception as e:
            logger.error(f"Erro na análise por região: {str(e)}")
            raise RuntimeError(f"Erro ao analisar vendas por região: {str(e)}")
    
    def exportar_analise_para_powerbi(self, analises: Dict[str, pl.DataFrame]) -> List[Tuple[str, str]]:
        """
        Exporta análises para uso no Power BI.
        
        Args:
            analises (Dict[str, pl.DataFrame]): Dicionário com as análises.
            
        Returns:
            List[Tuple[str, str]]: Lista de tuplas (nome, caminho) dos arquivos exportados.
            
        Raises:
            ValueError: Se o dicionário de análises estiver vazio.
        """
        logger.info(f"Iniciando exportação de {len(analises)} análises para Power BI")
        
        if not analises:
            logger.warning("Nenhuma análise para exportar")
            return []
        
        arquivos_exportados = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for nome, df in analises.items():
            try:
                # Verificar se é um dicionário aninhado (como no caso de subcategorias)
                if isinstance(df, dict):
                    for sub_nome, sub_df in df.items():
                        nome_arquivo = f"analise_{nome}_{sub_nome}_{timestamp}"
                        caminho = self.powerbi_exporter.export_to_csv(sub_df, nome_arquivo)
                        arquivos_exportados.append((f"{nome}_{sub_nome}", caminho))
                        logger.info(f"Análise '{nome} - {sub_nome}' exportada para: {caminho}")
                else:
                    nome_arquivo = f"analise_{nome}_{timestamp}"
                    caminho = self.powerbi_exporter.export_to_csv(df, nome_arquivo)
                    arquivos_exportados.append((nome, caminho))
                    logger.info(f"Análise '{nome}' exportada para: {caminho}")
            except Exception as e:
                logger.error(f"Erro ao exportar análise '{nome}': {str(e)}")
                print(f"Erro ao exportar análise '{nome}': {str(e)}")
        
        logger.info(f"Exportação concluída: {len(arquivos_exportados)} arquivos gerados")
        return arquivos_exportados
    
    def salvar_analises(self, analises: Dict[str, pl.DataFrame]) -> List[Tuple[str, str]]:
        """
        Salva as análises em formato Parquet.
        
        Args:
            analises (Dict[str, pl.DataFrame]): Dicionário com as análises.
            
        Returns:
            List[Tuple[str, str]]: Lista de tuplas (nome, caminho) dos arquivos salvos.
        """
        logger.info(f"Salvando {len(analises)} análises")
        
        if not analises:
            logger.warning("Nenhuma análise para salvar")
            return []
        
        arquivos_salvos = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for nome, df in analises.items():
            try:
                # Verificar se é um dicionário aninhado (como no caso de subcategorias)
                if isinstance(df, dict):
                    for sub_nome, sub_df in df.items():
                        nome_arquivo = f"analise_{nome}_{sub_nome}_{timestamp}.parquet"
                        caminho = os.path.join(self.processed_path, nome_arquivo)
                        sub_df.write_parquet(caminho)
                        arquivos_salvos.append((f"{nome}_{sub_nome}", caminho))
                        logger.info(f"Análise '{nome} - {sub_nome}' salva em: {caminho}")
                else:
                    nome_arquivo = f"analise_{nome}_{timestamp}.parquet"
                    caminho = os.path.join(self.processed_path, nome_arquivo)
                    df.write_parquet(caminho)
                    arquivos_salvos.append((nome, caminho))
                    logger.info(f"Análise '{nome}' salva em: {caminho}")
            except Exception as e:
                logger.error(f"Erro ao salvar análise '{nome}': {str(e)}")
                print(f"Erro ao salvar análise '{nome}': {str(e)}")
        
        logger.info(f"Salvamento concluído: {len(arquivos_salvos)} arquivos gerados")
        return arquivos_salvos
    
    def gerar_dashboard_powerbi(self, 
                               df: pl.DataFrame, 
                               analises: Dict[str, pl.DataFrame],
                               nome_dashboard: str = "E-commerce Sales Dashboard") -> str:
        """
        Gera um dashboard do Power BI usando os dados processados e análises.
        
        Args:
            df (pl.DataFrame): DataFrame com dados processados.
            analises (Dict[str, pl.DataFrame]): Dicionário com análises.
            nome_dashboard (str): Nome do dashboard a ser gerado.
            
        Returns:
            str: Caminho para o template de dashboard gerado.
        """
        logger.info(f"Gerando dashboard do Power BI: {nome_dashboard}")
        
        try:
            # Exportar dados e análises para CSV (formato reconhecido pelo Power BI)
            logger.info("Exportando dados para CSV")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Exportar dados base
            arquivo_dados = self.powerbi_exporter.export_to_csv(
                df, 
                f"dashboard_dados_{timestamp}"
            )
            
            # Exportar análises
            arquivos_analises = self.exportar_analise_para_powerbi(analises)
            
            # Lista de todos os arquivos para o dashboard
            arquivos = [arquivo_dados] + [caminho for _, caminho in arquivos_analises]
            
            # Gerar dashboard
            from src.views.powerbi_dashboard import PowerBIDashboard
            powerbi_dashboard = PowerBIDashboard()
            
            # Gerar tema personalizado
            tema_path = powerbi_dashboard.gerar_tema_powerbi(
                nome_tema=f"{nome_dashboard} Theme",
                cores_primarias=["#01B8AA", "#374649", "#FD625E", "#F2C80F", "#5F6B6D", "#8AD4EB"]
            )
            
            # Gerar template PBIX
            template_path = powerbi_dashboard.gerar_pbix_template(
                nome_dashboard=nome_dashboard,
                arquivos_dados=arquivos
            )
            
            logger.info(f"Dashboard do Power BI gerado: {template_path}")
            print(f"Dashboard do Power BI gerado: {template_path}")
            print(f"Tema personalizado: {tema_path}")
            
            return template_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar dashboard do Power BI: {str(e)}")
            print(f"Erro ao gerar dashboard do Power BI: {str(e)}")
            raise RuntimeError(f"Erro ao gerar dashboard do Power BI: {str(e)}")

# Se executado como script
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Cabeçalho
    print("=" * 60)
    print("ANÁLISE DE DADOS DE E-COMMERCE".center(60))
    print("=" * 60)
    print(f"Data e Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Usuário: {os.getenv('USERNAME', 'vitordoliveira')}")
    print("-" * 60)
    
    # Inicializar controlador
    analise = AnaliseController()
    
    # Processar dados sintéticos
    print("\nProcessando dados sintéticos...")
    resultado = analise.processar_dados_vendas(None, True, True)
    
    # Mostrar resumo
    print("\nResumo dos dados processados:")
    print(f"- Registros: {resultado['resumo']['num_registros']}")
    print(f"- Colunas: {resultado['resumo']['num_colunas']}")
    
    # Realizar análises
    print("\nRealizando análises...")
    df_processado = resultado['dados_processados']
    
    # Análise por período
    print("\n1. Análise por período")
    analises_periodo = analise.analisar_vendas_por_periodo(df_processado)
    print(f"   Análises geradas: {', '.join(analises_periodo.keys())}")
    
    # Análise por categoria (se existir a coluna)
    analises = {'periodo': analises_periodo}
    
    if 'product_category' in df_processado.columns:
        print("\n2. Análise por categoria")
        analise_categoria = analise.analisar_vendas_por_categoria(df_processado)
        
        if isinstance(analise_categoria, dict):
            # Se retornou subcategorias
            print(f"   Categorias analisadas: {analise_categoria['categorias'].shape[0]}")
            print(f"   Subcategorias analisadas: {analise_categoria['subcategorias'].shape[0]}")
            analises['categoria'] = analise_categoria
        else:
            print(f"   Categorias analisadas: {analise_categoria.shape[0]}")
            analises['categoria'] = {'categorias': analise_categoria}
    
    # Análise por região (usando detecção automática)
    print("\n3. Análise por região")
    try:
        analise_regiao = analise.analisar_vendas_por_regiao(df_processado)
        print(f"   Regiões analisadas: {analise_regiao.shape[0]}")
        analises['regiao'] = analise_regiao
    except ValueError as e:
        print(f"   Não foi possível realizar análise por região: {str(e)}")
    
    # Exportar para Power BI
    print("\nExportando análises para Power BI...")
    arquivos_exportados = analise.exportar_analise_para_powerbi(analises)
    
    print("\nArquivos gerados:")
    for nome, caminho in arquivos_exportados:
        print(f"- {nome}: {os.path.basename(caminho)}")
    
    # Gerar dashboard
    print("\nGerando dashboard para Power BI...")
    try:
        dashboard_path = analise.gerar_dashboard_powerbi(df_processado, analises)
        print(f"Dashboard gerado: {os.path.basename(dashboard_path)}")
    except Exception as e:
        print(f"Não foi possível gerar dashboard: {str(e)}")
    
    print("\nProcesso concluído com sucesso!")