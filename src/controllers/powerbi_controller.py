"""
Controlador para integração com o Power BI.
Gerencia a geração de dashboards, relatórios e modelos de dados.

Autor: Vitor Oliveira
Data: 2025-05-28
"""

import os
import polars as pl
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from src.views.powerbi_exporter import PowerBIExporter
from src.views.powerbi_dashboard import PowerBIDashboard
from src.views.powerbi_template import PowerBITemplate

# Configuração de logging
logger = logging.getLogger('ecommerce_analytics.powerbi')

class PowerBIController:
    """
    Controlador responsável pela integração com o Power BI.
    
    Esta classe coordena a geração de dashboards, relatórios, temas personalizados
    e modelos de dados otimizados para análise no Power BI.
    """
    
    def __init__(self):
        """
        Inicializa o controlador com as dependências necessárias.
        """
        self.exporter = PowerBIExporter()
        self.dashboard = PowerBIDashboard()
        self.template = PowerBITemplate()
        self.export_path = self.exporter.export_path
        
        logger.info("PowerBIController inicializado")
        logger.info(f"Diretório de exportação: {self.export_path}")
    
    def gerar_apenas_dashboard(self, 
                              arquivos_dados: List[str], 
                              nome_dashboard: str = "E-commerce Dashboard") -> Dict[str, Any]:
        """
        Gera um dashboard do Power BI a partir de arquivos de dados.
        
        Args:
            arquivos_dados (List[str]): Lista de caminhos para arquivos de dados.
            nome_dashboard (str): Nome a ser dado ao dashboard.
            
        Returns:
            Dict[str, Any]: Dicionário com os resultados da geração.
            
        Raises:
            ValueError: Se a lista de arquivos estiver vazia.
            FileNotFoundError: Se algum arquivo não for encontrado.
        """
        logger.info(f"Iniciando geração de dashboard '{nome_dashboard}' com {len(arquivos_dados)} arquivos")
        
        # Validar entrada
        if not arquivos_dados:
            logger.error("Lista de arquivos vazia")
            raise ValueError("A lista de arquivos de dados não pode estar vazia")
        
        # Verificar se os arquivos existem
        for arquivo in arquivos_dados:
            if not os.path.exists(arquivo):
                logger.error(f"Arquivo não encontrado: {arquivo}")
                raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")
        
        resultado = {
            'nome_dashboard': nome_dashboard,
            'arquivos_dados': arquivos_dados,
            'arquivos_gerados': []
        }
        
        try:
            # Gerar template PBIX
            logger.info("Gerando template de referência para dashboard")
            dashboard_path = self.dashboard.gerar_pbix_template(nome_dashboard, arquivos_dados)
            resultado['arquivos_gerados'].append(('dashboard_template', dashboard_path))
            logger.info(f"Template de dashboard gerado: {dashboard_path}")
            
            # Gerar tema personalizado
            logger.info("Gerando tema personalizado para o dashboard")
            nome_tema = f"{nome_dashboard} Theme"
            tema_path = self.dashboard.gerar_tema_powerbi(nome_tema)
            resultado['arquivos_gerados'].append(('dashboard_tema', tema_path))
            logger.info(f"Tema personalizado gerado: {tema_path}")
            
            # Gerar metadados do modelo
            logger.info("Gerando metadados do modelo")
            descricao = f"Dashboard de E-commerce - {nome_dashboard}"
            metadata_path = self.template.gerar_metadata_modelo(nome_dashboard, descricao, arquivos_dados)
            resultado['arquivos_gerados'].append(('dashboard_metadata', metadata_path))
            logger.info(f"Metadados do modelo gerados: {metadata_path}")
            
            # Gerar template de métricas
            logger.info("Gerando template de métricas")
            nome_template_metricas = f"{nome_dashboard} Metrics"
            metricas_path = self.template.gerar_template_metricas(nome_template_metricas)
            resultado['arquivos_gerados'].append(('dashboard_metricas', metricas_path))
            logger.info(f"Template de métricas gerado: {metricas_path}")
            
            # Gerar documentação
            logger.info("Gerando documentação do dashboard")
            doc_path = self.template.gerar_documentacao_markdown(
                nome_dashboard, 
                descricao, 
                [path for _, path in resultado['arquivos_gerados']]
            )
            resultado['arquivos_gerados'].append(('dashboard_documentacao', doc_path))
            logger.info(f"Documentação do dashboard gerada: {doc_path}")
            
            logger.info("Geração de dashboard concluída com sucesso")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao gerar dashboard: {str(e)}", exc_info=True)
            raise RuntimeError(f"Erro ao gerar dashboard: {str(e)}")
    
    def preparar_modelo_completo(self, 
                                df: pl.DataFrame, 
                                analises: Optional[Dict[str, Any]] = None,
                                nome_modelo: str = "E-commerce Analytics") -> Dict[str, Any]:
        """
        Prepara um modelo completo para o Power BI, incluindo dados e análises.
        
        Args:
            df (pl.DataFrame): DataFrame principal com os dados processados.
            analises (Dict[str, Any], optional): Dicionário com análises adicionais.
            nome_modelo (str): Nome a ser dado ao modelo.
            
        Returns:
            Dict[str, Any]: Dicionário com os resultados da geração do modelo.
            
        Raises:
            TypeError: Se o DataFrame não for do tipo correto.
        """
        logger.info(f"Iniciando preparação de modelo completo '{nome_modelo}'")
        
        # Validar entrada
        if not isinstance(df, pl.DataFrame):
            logger.error("O DataFrame principal deve ser do tipo polars.DataFrame")
            raise TypeError("O DataFrame principal deve ser do tipo polars.DataFrame")
        
        resultado = {
            'nome_modelo': nome_modelo,
            'arquivos_dados': [],
            'arquivos_suporte': []
        }
        
        try:
            # Exportar dados principais
            logger.info("Exportando dados principais")
            nome_arquivo_principal = f"{nome_modelo.lower().replace(' ', '_')}_dados_principais"
            caminho_principal = self.exporter.export_to_csv(df, nome_arquivo_principal)
            resultado['arquivos_dados'].append(('dados_principais', caminho_principal))
            logger.info(f"Dados principais exportados: {caminho_principal}")
            
            # Exportar análises, se fornecidas
            if analises:
                logger.info(f"Exportando análises")
                self._exportar_analises_aninhadas(analises, nome_modelo, resultado)
            
            # Verificar se existe coluna de data para criar calendário
            data_inicio = None
            data_fim = None
            
            # Tentar identificar datas de várias fontes possíveis
            if analises and isinstance(analises, dict):
                # Tentar obter datas de vendas_por_dia se existir
                if 'vendas_por_dia' in analises:
                    try:
                        df_dias = analises['vendas_por_dia']
                        data_inicio = df_dias['data'].min().strftime('%Y-%m-%d') if hasattr(df_dias, 'strftime') else str(df_dias['data'].min())
                        data_fim = df_dias['data'].max().strftime('%Y-%m-%d') if hasattr(df_dias, 'strftime') else str(df_dias['data'].max())
                    except Exception as e:
                        logger.warning(f"Não foi possível extrair datas de vendas_por_dia: {str(e)}")
                        
                # Tentar obter datas de vendas_por_periodo.periodo
                elif 'periodo' in analises and isinstance(analises['periodo'], dict) and 'vendas_por_dia' in analises['periodo']:
                    try:
                        df_dias = analises['periodo']['vendas_por_dia']
                        data_inicio = df_dias['data'].min().strftime('%Y-%m-%d') if hasattr(df_dias, 'strftime') else str(df_dias['data'].min())
                        data_fim = df_dias['data'].max().strftime('%Y-%m-%d') if hasattr(df_dias, 'strftime') else str(df_dias['data'].max())
                    except Exception as e:
                        logger.warning(f"Não foi possível extrair datas de periodo.vendas_por_dia: {str(e)}")
            
            # Se ainda não temos datas e o DataFrame principal tem coluna de data
            if (data_inicio is None or data_fim is None) and 'date' in df.columns:
                try:
                    if pl.datatypes.is_temporal(df['date'].dtype):
                        data_inicio = df['date'].min().strftime('%Y-%m-%d')
                        data_fim = df['date'].max().strftime('%Y-%m-%d')
                    else:
                        # Tentar converter para datetime
                        df_temp = df.with_columns(
                            pl.col('date').str.to_datetime(strict=False).alias('_temp_date')
                        )
                        data_inicio = df_temp['_temp_date'].min().strftime('%Y-%m-%d')
                        data_fim = df_temp['_temp_date'].max().strftime('%Y-%m-%d')
                except Exception as e:
                    logger.warning(f"Não foi possível extrair datas da coluna 'date': {str(e)}")
            
            # Gerar calendário se temos as datas
            if data_inicio and data_fim:
                logger.info(f"Gerando tabela de calendário de {data_inicio} a {data_fim}")
                try:
                    nome_calendario = f"{nome_modelo.lower().replace(' ', '_')}_calendario"
                    calendario_path = self.criar_calendario_powerbi(
                        data_inicio, data_fim, nome_calendario
                    )
                    resultado['arquivos_dados'].append(('calendario', calendario_path))
                    logger.info(f"Tabela de calendário gerada: {calendario_path}")
                except Exception as e:
                    logger.warning(f"Não foi possível gerar calendário: {str(e)}")
            
            # Gerar template PBIX
            logger.info("Gerando template de referência para o modelo")
            arquivos_para_template = [caminho for _, caminho in resultado['arquivos_dados']]
            dashboard_path = self.dashboard.gerar_pbix_template(nome_modelo, arquivos_para_template)
            resultado['arquivos_suporte'].append(('modelo_template', dashboard_path))
            logger.info(f"Template de modelo gerado: {dashboard_path}")
            
            # Gerar tema personalizado
            logger.info("Gerando tema personalizado para o modelo")
            nome_tema = f"{nome_modelo} Theme"
            # Escolher cores adequadas para análise de e-commerce
            cores_ecommerce = ["#3A86FF", "#FF006E", "#FB5607", "#FFBE0B", "#8338EC", "#06D6A0"]
            tema_path = self.dashboard.gerar_tema_powerbi(nome_tema, cores_ecommerce)
            resultado['arquivos_suporte'].append(('modelo_tema', tema_path))
            logger.info(f"Tema personalizado gerado: {tema_path}")
            
            # Gerar metadados do modelo
            logger.info("Gerando metadados do modelo")
            descricao = f"Modelo de análise de e-commerce - {nome_modelo}"
            metadata_path = self.template.gerar_metadata_modelo(
                nome_modelo, 
                descricao, 
                arquivos_para_template
            )
            resultado['arquivos_suporte'].append(('modelo_metadata', metadata_path))
            logger.info(f"Metadados do modelo gerados: {metadata_path}")
            
            # Gerar template de métricas
            logger.info("Gerando template de métricas específicas para e-commerce")
            nome_template_metricas = f"{nome_modelo} Metrics"
            metricas_path = self.template.gerar_template_metricas(
                nome_template_metricas,
                tipo_negocio="e-commerce"  # Especificar o tipo para métricas adequadas
            )
            resultado['arquivos_suporte'].append(('modelo_metricas', metricas_path))
            logger.info(f"Template de métricas gerado: {metricas_path}")
            
            # Gerar script DAX
            logger.info("Gerando script DAX")
            dax_path = self.template.gerar_script_medidas_dax(nome_template_metricas, metricas_path)
            resultado['arquivos_suporte'].append(('modelo_dax', dax_path))
            logger.info(f"Script DAX gerado: {dax_path}")
            
            # Gerar documentação
            logger.info("Gerando documentação do modelo")
            todos_arquivos = [path for _, path in resultado['arquivos_dados']] + [path for _, path in resultado['arquivos_suporte']]
            doc_path = self.template.gerar_documentacao_markdown(
                nome_modelo, 
                descricao, 
                todos_arquivos
            )
            resultado['arquivos_suporte'].append(('modelo_documentacao', doc_path))
            logger.info(f"Documentação do modelo gerada: {doc_path}")
            
            logger.info("Preparação de modelo completo concluída com sucesso")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao preparar modelo completo: {str(e)}", exc_info=True)
            raise RuntimeError(f"Erro ao preparar modelo completo: {str(e)}")
    
    def _exportar_analises_aninhadas(self, 
                                    analises: Dict[str, Any], 
                                    nome_base: str, 
                                    resultado: Dict[str, Any]) -> None:
        """
        Exporta análises de forma recursiva, lidando com estruturas aninhadas.
        
        Args:
            analises (Dict[str, Any]): Dicionário com análises, potencialmente aninhadas.
            nome_base (str): Nome base para os arquivos exportados.
            resultado (Dict[str, Any]): Dicionário de resultado para armazenar caminhos.
        """
        try:
            for nome, conteudo in analises.items():
                # Verificar se é um DataFrame
                if isinstance(conteudo, pl.DataFrame):
                    nome_arquivo = f"{nome_base.lower().replace(' ', '_')}_{nome}"
                    caminho = self.exporter.export_to_csv(conteudo, nome_arquivo)
                    resultado['arquivos_dados'].append((f'analise_{nome}', caminho))
                    logger.info(f"Análise '{nome}' exportada: {caminho}")
                
                # Verificar se é um dicionário aninhado
                elif isinstance(conteudo, dict):
                    # Verificar se contém DataFrames ou mais dicionários
                    if any(isinstance(v, pl.DataFrame) for v in conteudo.values()):
                        # Exportar DataFrames deste nível
                        for sub_nome, sub_conteudo in conteudo.items():
                            if isinstance(sub_conteudo, pl.DataFrame):
                                nome_arquivo = f"{nome_base.lower().replace(' ', '_')}_{nome}_{sub_nome}"
                                caminho = self.exporter.export_to_csv(sub_conteudo, nome_arquivo)
                                resultado['arquivos_dados'].append((f'analise_{nome}_{sub_nome}', caminho))
                                logger.info(f"Análise aninhada '{nome}.{sub_nome}' exportada: {caminho}")
                    else:
                        # Recursão para lidar com mais níveis de aninhamento
                        self._exportar_analises_aninhadas(conteudo, f"{nome_base}_{nome}", resultado)
        except Exception as e:
            logger.warning(f"Erro ao exportar análises aninhadas: {str(e)}")
    
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
            # Validar formato das datas
            try:
                datetime.strptime(data_inicio, '%Y-%m-%d')
                datetime.strptime(data_fim, '%Y-%m-%d')
            except ValueError as e:
                logger.error(f"Formato de data inválido: {str(e)}")
                raise ValueError(f"Formato de data inválido. Use o formato 'YYYY-MM-DD': {str(e)}")
            
            # Delegar para o dashboard (que contém a lógica de geração de calendário)
            caminho = self.dashboard.criar_calendario_powerbi(data_inicio, data_fim, nome_arquivo)
            logger.info(f"Tabela de calendário criada com sucesso: {caminho}")
            return caminho
            
        except Exception as e:
            logger.error(f"Erro ao criar tabela de calendário: {str(e)}", exc_info=True)
            raise RuntimeError(f"Erro ao criar tabela de calendário: {str(e)}")
    
    def gerar_tema_powerbi(self, 
                          nome_tema: str = "E-commerce Analytics Theme", 
                          cores_primarias: Optional[List[str]] = None) -> str:
        """
        Gera um tema personalizado para o Power BI.
        
        Args:
            nome_tema (str): Nome do tema a ser gerado.
            cores_primarias (List[str], optional): Lista de cores primárias em formato hexadecimal.
                                                Se None, usa as cores padrão.
            
        Returns:
            str: Caminho para o arquivo de tema gerado.
        """
        logger.info(f"Gerando tema personalizado '{nome_tema}'")
        
        try:
            # Validar cores primárias, se fornecidas
            if cores_primarias:
                for cor in cores_primarias:
                    if not cor.startswith('#') or len(cor) != 7:
                        logger.warning(f"Formato de cor inválido: {cor}. Deve ser hexadecimal (#RRGGBB).")
            
            # Delegar para o dashboard (que contém a lógica de geração de tema)
            caminho = self.dashboard.gerar_tema_powerbi(nome_tema, cores_primarias)
            logger.info(f"Tema personalizado gerado com sucesso: {caminho}")
            return caminho
            
        except Exception as e:
            logger.error(f"Erro ao gerar tema personalizado: {str(e)}", exc_info=True)
            raise RuntimeError(f"Erro ao gerar tema personalizado: {str(e)}")
    
    def gerar_visualizacoes(self, 
                           df: Union[pl.DataFrame, pd.DataFrame], 
                           prefix: str = "ecommerce_viz") -> List[str]:
        """
        Gera visualizações básicas a partir dos dados para análise rápida.
        
        Args:
            df (Union[pl.DataFrame, pd.DataFrame]): DataFrame com os dados para visualização.
            prefix (str): Prefixo para os nomes dos arquivos de imagem.
            
        Returns:
            List[str]: Lista de caminhos para as visualizações geradas.
            
        Raises:
            TypeError: Se o DataFrame não for do tipo correto.
        """
        logger.info(f"Gerando visualizações com prefixo '{prefix}'")
        
        # Validar entrada
        if not isinstance(df, (pl.DataFrame, pd.DataFrame)):
            logger.error("O DataFrame deve ser do tipo polars.DataFrame ou pandas.DataFrame")
            raise TypeError("O DataFrame deve ser do tipo polars.DataFrame ou pandas.DataFrame")
        
        try:
            # Converter para pandas se for polars
            if isinstance(df, pl.DataFrame):
                df_pandas = df.to_pandas()
            else:
                df_pandas = df
            
            # Delegar para o exporter (que contém a lógica de geração de visualizações)
            caminhos = self.exporter.create_summary_visualizations(df_pandas, prefix)
            logger.info(f"Geradas {len(caminhos)} visualizações")
            return caminhos
            
        except Exception as e:
            logger.error(f"Erro ao gerar visualizações: {str(e)}", exc_info=True)
            raise RuntimeError(f"Erro ao gerar visualizações: {str(e)}")
    
    def exportar_relatorio_completo(self, 
                                   df: pl.DataFrame, 
                                   analises: Dict[str, Any],
                                   nome_relatorio: str = "E-commerce Report") -> Dict[str, Any]:
        """
        Exporta um relatório completo com dados, análises, visualizações e documentação.
        
        Args:
            df (pl.DataFrame): DataFrame principal com os dados processados.
            analises (Dict[str, Any]): Dicionário com análises.
            nome_relatorio (str): Nome do relatório.
            
        Returns:
            Dict[str, Any]: Dicionário com os resultados da exportação.
        """
        logger.info(f"Exportando relatório completo: {nome_relatorio}")
        
        resultado = {
            'nome_relatorio': nome_relatorio,
            'arquivos_dados': [],
            'visualizacoes': [],
            'documentacao': []
        }
        
        try:
            # 1. Preparar modelo para Power BI
            modelo = self.preparar_modelo_completo(df, analises, nome_relatorio)
            resultado['arquivos_dados'] = modelo['arquivos_dados']
            resultado['documentacao'].append(('modelo_documentacao', next(path for name, path in modelo['arquivos_suporte'] if name == 'modelo_documentacao')))
            
            # 2. Gerar visualizações resumidas
            logger.info("Gerando visualizações para o relatório")
            prefix = nome_relatorio.lower().replace(' ', '_')
            caminhos_viz = self.gerar_visualizacoes(df, prefix)
            resultado['visualizacoes'] = [('viz_principal', caminho) for caminho in caminhos_viz]
            
            # 3. Gerar visualizações para análises principais
            try:
                # Análise por período
                if 'periodo' in analises and 'vendas_por_mes' in analises['periodo']:
                    viz_periodo = self.gerar_visualizacoes(
                        analises['periodo']['vendas_por_mes'], 
                        f"{prefix}_periodo"
                    )
                    resultado['visualizacoes'].extend([('viz_periodo', caminho) for caminho in viz_periodo])
                
                # Análise por categoria
                if 'categoria' in analises:
                    if isinstance(analises['categoria'], dict) and 'categorias' in analises['categoria']:
                        df_cat = analises['categoria']['categorias']
                    else:
                        df_cat = analises['categoria']
                        
                    viz_categoria = self.gerar_visualizacoes(
                        df_cat,
                        f"{prefix}_categoria"
                    )
                    resultado['visualizacoes'].extend([('viz_categoria', caminho) for caminho in viz_categoria])
            except Exception as e:
                logger.warning(f"Erro ao gerar visualizações para análises: {str(e)}")
            
            # 4. Gerar relatório em markdown com visualizações incorporadas
            logger.info("Gerando relatório final em markdown")
            
            # Extrair visualizações principais
            principais_viz = [caminho for _, caminho in resultado['visualizacoes']][:5]  # Limitar a 5 visualizações
            
            markdown_path = self.template.gerar_relatorio_markdown(
                nome_relatorio,
                f"Relatório completo de análise de e-commerce - {nome_relatorio}",
                df,
                analises,
                principais_viz
            )
            resultado['documentacao'].append(('relatorio_markdown', markdown_path))
            
            logger.info(f"Relatório completo exportado: {markdown_path}")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao exportar relatório completo: {str(e)}", exc_info=True)
            raise RuntimeError(f"Erro ao exportar relatório completo: {str(e)}")

# Se executado como script
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Cabeçalho
    print("=" * 60)
    print("POWER BI CONTROLLER - TESTE".center(60))
    print("=" * 60)
    print(f"Data e Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Usuário: {os.getenv('USERNAME', 'vitordoliveira')}")
    print("-" * 60)
    
    # Demonstração rápida
    controller = PowerBIController()
    
    print("\nFuncionalidades disponíveis:")
    print("1. Gerar dashboard a partir de arquivos de dados")
    print("2. Preparar modelo completo a partir de DataFrame")
    print("3. Criar tabela de calendário")
    print("4. Gerar tema personalizado")
    print("5. Gerar visualizações a partir de DataFrame")
    print("6. Exportar relatório completo (novo)")
    
    print("\nExemplo de uso em código:")
    print("from src.controllers.powerbi_controller import PowerBIController")
    print("controller = PowerBIController()")
    print("controller.criar_calendario_powerbi('2025-01-01', '2025-12-31', 'calendario_2025')")
    
    print("\nPara mais detalhes, consulte a documentação ou execute os exemplos específicos.")