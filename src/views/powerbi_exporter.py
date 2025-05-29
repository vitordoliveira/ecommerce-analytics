"""
Módulo para exportação de dados para o Power BI.
Fornece funcionalidades para converter DataFrames em formatos compatíveis com o Power BI.

Autor: Vitor Oliveira
Data: 2025-05-28
"""

import os
import pandas as pd
import polars as pl
import logging
from datetime import datetime
from typing import Union, List, Optional, Dict

# Configuração de logging
logger = logging.getLogger('ecommerce_analytics.powerbi_exporter')

class PowerBIExporter:
    """
    Classe para exportar dados para uso no Power BI.
    
    Fornece métodos para converter e exportar DataFrames para formatos
    compatíveis com o Power BI, como CSV e Excel.
    """
    
    def __init__(self, export_path: Optional[str] = None):
        """
        Inicializa o exportador com o caminho de destino.
        
        Args:
            export_path (str, optional): Caminho para exportar os arquivos.
                                       Se None, usa o caminho padrão.
        """
        self.export_path = export_path or os.path.join('exports', 'powerbi')
        os.makedirs(self.export_path, exist_ok=True)
        logger.info(f"PowerBIExporter inicializado com diretório: {self.export_path}")
    
    def export_to_csv(self, 
                     df: Union[pl.DataFrame, pd.DataFrame], 
                     filename: str,
                     include_timestamp: bool = True) -> str:
        """
        Exporta um DataFrame para CSV no formato adequado para o Power BI.
        
        Args:
            df (Union[pl.DataFrame, pd.DataFrame]): DataFrame a ser exportado.
            filename (str): Nome base do arquivo (sem extensão).
            include_timestamp (bool): Se True, adiciona timestamp ao nome do arquivo.
            
        Returns:
            str: Caminho do arquivo exportado.
            
        Raises:
            TypeError: Se o df não for um DataFrame do Polars ou Pandas.
            IOError: Se ocorrer um erro ao salvar o arquivo.
        """
        logger.info(f"Exportando DataFrame para CSV: {filename}")
        
        # Validar tipo de entrada
        if not isinstance(df, (pl.DataFrame, pd.DataFrame)):
            logger.error("O DataFrame deve ser do tipo polars.DataFrame ou pandas.DataFrame")
            raise TypeError("O DataFrame deve ser do tipo polars.DataFrame ou pandas.DataFrame")
        
        try:
            # Adicionar timestamp ao nome do arquivo se solicitado
            base_filename = filename
            if include_timestamp:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_filename = f"{filename}_{timestamp}"
            
            # Garantir que o nome termine com .csv
            if not base_filename.lower().endswith('.csv'):
                base_filename = f"{base_filename}.csv"
            
            # Caminho completo para o arquivo
            output_path = os.path.join(self.export_path, base_filename)
            
            # Exportar baseado no tipo do DataFrame
            if isinstance(df, pl.DataFrame):
                logger.info("Exportando DataFrame Polars")
                df.write_csv(output_path)
            else:  # pandas DataFrame
                logger.info("Exportando DataFrame Pandas")
                df.to_csv(output_path, index=False)
            
            logger.info(f"DataFrame exportado com sucesso para: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao exportar DataFrame para CSV: {str(e)}")
            raise IOError(f"Erro ao exportar DataFrame para CSV: {str(e)}")
    
    def export_to_excel(self, 
                       df: Union[pl.DataFrame, pd.DataFrame], 
                       filename: str,
                       include_timestamp: bool = True,
                       sheet_name: str = "Dados") -> str:
        """
        Exporta um DataFrame para Excel no formato adequado para o Power BI.
        
        Args:
            df (Union[pl.DataFrame, pd.DataFrame]): DataFrame a ser exportado.
            filename (str): Nome base do arquivo (sem extensão).
            include_timestamp (bool): Se True, adiciona timestamp ao nome do arquivo.
            sheet_name (str): Nome da planilha no arquivo Excel.
            
        Returns:
            str: Caminho do arquivo exportado.
            
        Raises:
            TypeError: Se o df não for um DataFrame do Polars ou Pandas.
            ImportError: Se a biblioteca openpyxl não estiver instalada.
            IOError: Se ocorrer um erro ao salvar o arquivo.
        """
        logger.info(f"Exportando DataFrame para Excel: {filename}")
        
        # Validar tipo de entrada
        if not isinstance(df, (pl.DataFrame, pd.DataFrame)):
            logger.error("O DataFrame deve ser do tipo polars.DataFrame ou pandas.DataFrame")
            raise TypeError("O DataFrame deve ser do tipo polars.DataFrame ou pandas.DataFrame")
        
        # Verificar se openpyxl está disponível sem importar
        try:
            # Verifica disponibilidade sem fazer import
            openpyxl_spec = __import__('importlib').util.find_spec('openpyxl')
            if openpyxl_spec is None:
                logger.error("Biblioteca openpyxl não encontrada")
                raise ImportError("Para exportar para Excel, instale a biblioteca openpyxl: pip install openpyxl")
        except ImportError:
            logger.error("Erro ao verificar disponibilidade de openpyxl")
            raise ImportError("Para exportar para Excel, instale a biblioteca openpyxl: pip install openpyxl")
        
        try:
            # Adicionar timestamp ao nome do arquivo se solicitado
            base_filename = filename
            if include_timestamp:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_filename = f"{filename}_{timestamp}"
            
            # Garantir que o nome termine com .xlsx
            if not base_filename.lower().endswith('.xlsx'):
                base_filename = f"{base_filename}.xlsx"
            
            # Caminho completo para o arquivo
            output_path = os.path.join(self.export_path, base_filename)
            
            # Converter para pandas se for polars
            if isinstance(df, pl.DataFrame):
                logger.info("Convertendo DataFrame Polars para Pandas para exportação Excel")
                df_pandas = df.to_pandas()
            else:
                df_pandas = df
            
            # Exportar usando pandas (que usa openpyxl internamente)
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df_pandas.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"DataFrame exportado com sucesso para Excel: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao exportar DataFrame para Excel: {str(e)}")
            raise IOError(f"Erro ao exportar DataFrame para Excel: {str(e)}")
    
    def export_multiple_sheets(self, 
                              dfs: Dict[str, Union[pl.DataFrame, pd.DataFrame]], 
                              filename: str,
                              include_timestamp: bool = True) -> str:
        """
        Exporta múltiplos DataFrames para um único arquivo Excel com várias planilhas.
        
        Args:
            dfs (Dict[str, Union[pl.DataFrame, pd.DataFrame]]): Dicionário de DataFrames onde
                as chaves são os nomes das planilhas.
            filename (str): Nome base do arquivo (sem extensão).
            include_timestamp (bool): Se True, adiciona timestamp ao nome do arquivo.
            
        Returns:
            str: Caminho do arquivo exportado.
            
        Raises:
            TypeError: Se algum df não for um DataFrame do Polars ou Pandas.
            ImportError: Se a biblioteca openpyxl não estiver instalada.
            IOError: Se ocorrer um erro ao salvar o arquivo.
        """
        logger.info(f"Exportando {len(dfs)} DataFrames para planilhas Excel: {filename}")
        
        if not dfs:
            logger.warning("Nenhum DataFrame fornecido para exportação")
            raise ValueError("O dicionário de DataFrames não pode estar vazio")
        
        # Verificar se openpyxl está disponível sem importar
        try:
            # Verifica disponibilidade sem fazer import
            openpyxl_spec = __import__('importlib').util.find_spec('openpyxl')
            if openpyxl_spec is None:
                logger.error("Biblioteca openpyxl não encontrada")
                raise ImportError("Para exportar para Excel, instale a biblioteca openpyxl: pip install openpyxl")
        except ImportError:
            logger.error("Erro ao verificar disponibilidade de openpyxl")
            raise ImportError("Para exportar para Excel, instale a biblioteca openpyxl: pip install openpyxl")
        
        try:
            # Adicionar timestamp ao nome do arquivo se solicitado
            base_filename = filename
            if include_timestamp:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_filename = f"{filename}_{timestamp}"
            
            # Garantir que o nome termine com .xlsx
            if not base_filename.lower().endswith('.xlsx'):
                base_filename = f"{base_filename}.xlsx"
            
            # Caminho completo para o arquivo
            output_path = os.path.join(self.export_path, base_filename)
            
            # Criar o arquivo Excel com múltiplas planilhas
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df in dfs.items():
                    # Validar tipo de DataFrame
                    if not isinstance(df, (pl.DataFrame, pd.DataFrame)):
                        logger.error(f"DataFrame para planilha '{sheet_name}' deve ser do tipo polars.DataFrame ou pandas.DataFrame")
                        raise TypeError(f"DataFrame para planilha '{sheet_name}' deve ser do tipo polars.DataFrame ou pandas.DataFrame")
                    
                    # Converter para pandas se for polars
                    if isinstance(df, pl.DataFrame):
                        logger.info(f"Convertendo DataFrame Polars para planilha '{sheet_name}'")
                        df_pandas = df.to_pandas()
                    else:
                        df_pandas = df
                    
                    # Exportar a planilha
                    df_pandas.to_excel(writer, sheet_name=sheet_name, index=False)
                    logger.info(f"Planilha '{sheet_name}' adicionada ao arquivo Excel")
            
            logger.info(f"Arquivo Excel com múltiplas planilhas criado com sucesso: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao exportar DataFrames para Excel: {str(e)}")
            raise IOError(f"Erro ao exportar DataFrames para Excel: {str(e)}")
    
    def create_summary_visualizations(self, 
                                     df: pd.DataFrame, 
                                     prefix: str = "summary_viz") -> List[str]:
        """
        Cria visualizações básicas resumindo os dados.
        
        Nota: Este método requer matplotlib e seaborn para funcionar.
        
        Args:
            df (pd.DataFrame): DataFrame do pandas com os dados.
            prefix (str): Prefixo para os nomes dos arquivos.
            
        Returns:
            List[str]: Lista de caminhos para as visualizações geradas.
            
        Raises:
            ImportError: Se matplotlib ou seaborn não estiverem instalados.
            ValueError: Se o DataFrame estiver vazio.
        """
        logger.info(f"Criando visualizações resumidas com prefixo '{prefix}'")
        
        if df.empty:
            logger.warning("DataFrame vazio, não é possível criar visualizações")
            raise ValueError("O DataFrame não pode estar vazio para criar visualizações")
        
        # Verificar se as bibliotecas de visualização estão disponíveis sem importar
        importlib = __import__('importlib')
        matplotlib_spec = importlib.util.find_spec('matplotlib')
        seaborn_spec = importlib.util.find_spec('seaborn')
        
        if matplotlib_spec is None or seaborn_spec is None:
            logger.error("Bibliotecas de visualização não encontradas")
            raise ImportError("Para criar visualizações, instale matplotlib e seaborn: pip install matplotlib seaborn")
        
        # Lista para armazenar os caminhos dos arquivos gerados
        output_files = []
        
        try:
            # Importações dinâmicas para evitar problemas com o Pylance
            plt = __import__('matplotlib.pyplot')
            sns = __import__('seaborn')
            
            # Criar diretório para visualizações
            viz_dir = os.path.join(self.export_path, 'visualizations')
            os.makedirs(viz_dir, exist_ok=True)
            logger.info(f"Diretório para visualizações: {viz_dir}")
            
            # Timestamp para os nomes dos arquivos
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 1. Histograma para colunas numéricas
            logger.info("Criando histogramas para colunas numéricas")
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            
            if numeric_cols:
                for col in numeric_cols[:5]:  # Limitar a 5 colunas para não gerar muitos arquivos
                    plt.figure(figsize=(10, 6))
                    sns.histplot(df[col], kde=True)
                    plt.title(f'Distribuição de {col}')
                    plt.tight_layout()
                    
                    # Salvar figura
                    fig_path = os.path.join(viz_dir, f"{prefix}_hist_{col}_{timestamp}.png")
                    plt.savefig(fig_path)
                    plt.close()
                    
                    output_files.append(fig_path)
                    logger.info(f"Histograma criado para coluna '{col}': {fig_path}")
            
            logger.info(f"Processo de criação de visualizações concluído. {len(output_files)} arquivos gerados.")
            return output_files
            
        except ImportError:
            logger.error("Bibliotecas de visualização não encontradas apesar da verificação prévia")
            raise ImportError("Para criar visualizações, instale matplotlib e seaborn: pip install matplotlib seaborn")
        except Exception as e:
            logger.error(f"Erro ao criar visualizações: {str(e)}")
            raise RuntimeError(f"Erro ao criar visualizações: {str(e)}")
    
    def format_dataframe_for_powerbi(self, df: Union[pl.DataFrame, pd.DataFrame]) -> Union[pl.DataFrame, pd.DataFrame]:
        """
        Formata um DataFrame para melhor compatibilidade com o Power BI.
        
        Realiza operações como:
        - Renomear colunas para remover espaços e caracteres especiais
        - Converter datas para formato adequado
        - Ajustar tipos de dados
        
        Args:
            df (Union[pl.DataFrame, pd.DataFrame]): DataFrame a ser formatado.
            
        Returns:
            Union[pl.DataFrame, pd.DataFrame]: DataFrame formatado (mesmo tipo do input).
            
        Raises:
            TypeError: Se o df não for um DataFrame do Polars ou Pandas.
        """
        logger.info("Formatando DataFrame para compatibilidade com Power BI")
        
        # Validar tipo de entrada
        if not isinstance(df, (pl.DataFrame, pd.DataFrame)):
            logger.error("O DataFrame deve ser do tipo polars.DataFrame ou pandas.DataFrame")
            raise TypeError("O DataFrame deve ser do tipo polars.DataFrame ou pandas.DataFrame")
        
        try:
            # Processamento específico para cada tipo de DataFrame
            if isinstance(df, pl.DataFrame):
                logger.info("Processando DataFrame do Polars")
                
                # Fazer uma cópia para não modificar o original
                formatted_df = df.clone()
                
                # 1. Renomear colunas: remover espaços e caracteres especiais
                new_columns = {col: col.replace(' ', '_').replace('-', '_').lower() for col in df.columns}
                formatted_df = formatted_df.rename(new_columns)
                
                # 2. Converter colunas de data para formato ISO
                date_columns = [col for col in formatted_df.columns if 'date' in col.lower() or 'time' in col.lower()]
                
                for col in date_columns:
                    if pl.datatypes.is_temporal(formatted_df[col].dtype):
                        # Já é uma coluna temporal, garantir formato ISO
                        formatted_df = formatted_df.with_columns(
                            pl.col(col).cast(pl.Datetime).dt.strftime("%Y-%m-%dT%H:%M:%S").alias(col)
                        )
                
                logger.info("DataFrame Polars formatado com sucesso")
                return formatted_df
                
            else:  # pandas DataFrame
                logger.info("Processando DataFrame do Pandas")
                
                # Fazer uma cópia para não modificar o original
                formatted_df = df.copy()
                
                # 1. Renomear colunas: remover espaços e caracteres especiais
                formatted_df.columns = [col.replace(' ', '_').replace('-', '_').lower() for col in formatted_df.columns]
                
                # 2. Converter colunas de data para formato ISO
                date_columns = [col for col in formatted_df.columns if 'date' in col.lower() or 'time' in col.lower()]
                
                for col in date_columns:
                    if pd.api.types.is_datetime64_any_dtype(formatted_df[col]):
                        formatted_df[col] = formatted_df[col].dt.strftime("%Y-%m-%dT%H:%M:%S")
                
                logger.info("DataFrame Pandas formatado com sucesso")
                return formatted_df
                
        except Exception as e:
            logger.error(f"Erro ao formatar DataFrame para Power BI: {str(e)}")
            raise RuntimeError(f"Erro ao formatar DataFrame para Power BI: {str(e)}")

# Se executado como script
if __name__ == "__main__":
    # Configuração de logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("POWER BI EXPORTER - TESTE".center(60))
    print("=" * 60)
    print(f"Data e Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Usuário: {os.getenv('USERNAME', 'vitordoliveira')}")
    print("-" * 60)
    
    # Demonstração com dados de exemplo
    print("\nCriando DataFrame de exemplo...")
    
    # Criar dados de exemplo
    data = {
        'ID': range(1, 6),
        'Nome Produto': ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Mouse'],
        'Preço': [1200.50, 800.75, 350.25, 150.00, 25.50],
        'Data Compra': ['2025-01-15', '2025-02-20', '2025-03-10', '2025-04-05', '2025-05-12'],
        'Quantidade': [1, 2, 1, 3, 5]
    }
    
    try:
        # Criar DataFrame
        df_pandas = pd.DataFrame(data)
        
        # Converter coluna de data
        df_pandas['Data Compra'] = pd.to_datetime(df_pandas['Data Compra'])
        
        print("\nDataFrame de exemplo criado:")
        print(df_pandas)
        
        # Inicializar exporter
        exporter = PowerBIExporter()
        
        # Exportar para CSV
        print("\nExportando para CSV...")
        csv_path = exporter.export_to_csv(df_pandas, "produtos_exemplo")
        print(f"Arquivo CSV exportado: {csv_path}")
        
        # Tentar exportar para Excel
        try:
            print("\nVerificando disponibilidade de openpyxl...")
            if __import__('importlib').util.find_spec('openpyxl') is not None:
                print("Exportando para Excel...")
                excel_path = exporter.export_to_excel(df_pandas, "produtos_exemplo")
                print(f"Arquivo Excel exportado: {excel_path}")
            else:
                print("Exportação para Excel não disponível. Instale openpyxl para habilitar esta funcionalidade.")
        except Exception as e:
            print(f"\nErro ao verificar/exportar para Excel: {str(e)}")
        
        print("\nProcesso concluído com sucesso!")
        
    except Exception as e:
        print(f"\nErro durante a execução: {str(e)}")