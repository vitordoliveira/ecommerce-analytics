import polars as pl
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Configuração de logging
logger = logging.getLogger('ecommerce_analytics.model')

# Constantes
DATE_FORMAT_DEFAULT = '%Y-%m-%d %H:%M:%S'
DATE_FORMATS_ALTERNATIVES = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
ANOMALY_THRESHOLD = 2.0  # Limiar para detecção de anomalias em valores totais

class EcommerceModel:
    """
    Modelo para processar dados de e-commerce usando Polars.
    
    Fornece métodos para carregar dados brutos, processar informações de vendas
    e salvar os resultados processados em formatos otimizados.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Inicializa o modelo com o caminho para os dados.
        
        Args:
            data_path (str, optional): Caminho para os dados brutos. 
                                      Se None, usa o caminho padrão.
        
        Raises:
            OSError: Se houver problemas ao criar diretórios necessários.
        """
        self.data_path = data_path or os.path.join('data', 'raw')
        self.processed_path = os.path.join('data', 'processed')
        
        # Garantir que os diretórios existam
        try:
            os.makedirs(self.data_path, exist_ok=True)
            os.makedirs(self.processed_path, exist_ok=True)
            logger.info(f"Diretórios de dados configurados: raw={self.data_path}, processed={self.processed_path}")
        except OSError as e:
            logger.error(f"Erro ao criar diretórios de dados: {str(e)}")
            raise OSError(f"Não foi possível criar os diretórios necessários: {str(e)}")
    
    def load_data(self, file_path: str) -> pl.DataFrame:
        """
        Carrega dados de um arquivo CSV ou Parquet.
        
        Args:
            file_path (str): Caminho do arquivo a ser carregado.
            
        Returns:
            pl.DataFrame: DataFrame do Polars com os dados carregados.
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado.
            ValueError: Se o formato do arquivo não for suportado.
            pl.PolarsError: Se houver erro durante a leitura do arquivo.
        """
        logger.info(f"Iniciando carregamento de dados do arquivo: {file_path}")
        
        # Verificar se o arquivo já é um caminho completo ou apenas um nome de arquivo
        if os.path.isabs(file_path) or ('data' + os.sep + 'raw' in file_path):
            # Usar o caminho como está se for absoluto ou já contiver data/raw
            path_to_load = file_path
        else:
            # Caso contrário, juntar com o caminho base
            path_to_load = os.path.join(self.data_path, file_path)
        
        # Verificar se o arquivo existe
        if not os.path.exists(path_to_load):
            logger.error(f"Arquivo não encontrado: {path_to_load}")
            raise FileNotFoundError(f"Arquivo não encontrado: {path_to_load}")
        
        logger.info(f"Carregando arquivo de: {path_to_load}")
        print(f"Carregando arquivo de: {path_to_load}")
        
        try:
            # Carregar baseado na extensão do arquivo
            if path_to_load.lower().endswith('.csv'):
                logger.info("Detectado formato CSV")
                df = pl.read_csv(path_to_load)
            elif path_to_load.lower().endswith('.parquet'):
                logger.info("Detectado formato Parquet")
                df = pl.read_parquet(path_to_load)
            elif path_to_load.lower().endswith('.json'):
                logger.info("Detectado formato JSON")
                df = pl.read_json(path_to_load)
            else:
                logger.error(f"Formato de arquivo não suportado: {path_to_load}")
                raise ValueError(f"Formato de arquivo não suportado. Use CSV, Parquet ou JSON: {path_to_load}")
            
            # Registrar informações sobre os dados carregados
            logger.info(f"Dados carregados com sucesso: {df.shape[0]} registros, {df.shape[1]} colunas")
            return df
            
        except pl.PolarsError as e:
            logger.error(f"Erro ao carregar dados: {str(e)}")
            raise pl.PolarsError(f"Erro ao carregar dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao carregar dados: {str(e)}")
            raise RuntimeError(f"Erro inesperado ao carregar dados: {str(e)}")
    
    def process_sales_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Processa dados de vendas de e-commerce.
        
        Este método realiza várias transformações nos dados brutos:
        1. Converte colunas de data para o formato correto
        2. Calcula ou valida a coluna total_value
        3. Realiza validações básicas nos dados
        4. Padroniza nomes de colunas
        5. Trata valores ausentes em colunas críticas
        
        Args:
            df (pl.DataFrame): DataFrame do Polars com dados brutos.
            
        Returns:
            pl.DataFrame: DataFrame processado.
            
        Raises:
            TypeError: Se o input não for um DataFrame do Polars.
            ValueError: Se o DataFrame estiver vazio ou não contiver colunas essenciais.
        """
        logger.info("Iniciando processamento de dados de vendas")
        
        # Validar o tipo de entrada
        if not isinstance(df, pl.DataFrame):
            logger.error("O argumento df deve ser um DataFrame do Polars")
            raise TypeError("O argumento df deve ser um DataFrame do Polars")
        
        # Validar se o DataFrame não está vazio
        if df.shape[0] == 0 or df.shape[1] == 0:
            logger.warning("DataFrame vazio ou sem colunas")
            return df  # Retornar o DataFrame vazio, não há nada para processar
        
        # Criar uma cópia para processamento
        processed_df = df.clone()
        logger.info(f"Iniciando processamento de {df.shape[0]} registros")
        
        # 1. Padronizar nomes de colunas (lowercase e substituir espaços por underscore)
        column_mapping = {col: col.lower().replace(' ', '_') for col in processed_df.columns}
        processed_df = processed_df.rename(column_mapping)
        logger.info("Nomes de colunas padronizados")
        
        # 2. Converter colunas de data para o formato correto (se existirem)
        date_columns = [col for col in processed_df.columns if 'date' in col.lower() or 'time' in col.lower()]
        logger.info(f"Detectadas {len(date_columns)} colunas de data: {date_columns}")
        
        for col in date_columns:
            logger.info(f"Processando coluna de data: {col}")
            try:
                # Tentar o formato padrão primeiro
                processed_df = processed_df.with_columns(
                    pl.col(col).str.to_datetime(DATE_FORMAT_DEFAULT, strict=False).alias(col)
                )
                logger.info(f"Coluna {col} convertida com formato padrão")
            except Exception as e:
                logger.warning(f"Erro ao converter coluna {col} com formato padrão: {str(e)}")
                
                # Tentar formatos alternativos
                for fmt in DATE_FORMATS_ALTERNATIVES:
                    try:
                        processed_df = processed_df.with_columns(
                            pl.col(col).str.to_datetime(fmt, strict=False).alias(col)
                        )
                        logger.info(f"Coluna {col} convertida com formato alternativo: {fmt}")
                        break
                    except Exception:
                        continue
        
        # 3. Verificar e tratar coluna total_value
        # 3.1 Caso não exista, calculá-la se possível
        if 'price' in processed_df.columns and 'quantity' in processed_df.columns:
            if 'total_value' not in processed_df.columns:
                logger.info("Calculando coluna total_value")
                processed_df = processed_df.with_columns(
                    (pl.col('price') * pl.col('quantity')).alias('total_value')
                )
                logger.info("Coluna total_value calculada com sucesso")
            else:
                # 3.2 Se já existe, verificar se há valores anômalos
                logger.info("Verificando valores da coluna total_value existente")
                try:
                    max_value = processed_df['total_value'].max()
                    max_expected = processed_df['price'].max() * processed_df['quantity'].max()
                    
                    # Se o valor máximo for muito maior que o esperado, recalcular
                    if max_value > max_expected * ANOMALY_THRESHOLD:
                        logger.warning(
                            f"Detectados valores anômalos em total_value: máximo={max_value}, "
                            f"esperado={max_expected}. Recalculando..."
                        )
                        print("Detectados valores potencialmente incorretos em total_value. Recalculando...")
                        processed_df = processed_df.with_columns(
                            (pl.col('price') * pl.col('quantity')).alias('total_value')
                        )
                    else:
                        logger.info("Valores em total_value validados e dentro dos limites esperados")
                except Exception as e:
                    logger.warning(f"Não foi possível validar os valores de total_value: {str(e)}")
                    print("Aviso: Não foi possível validar os valores de total_value")
        
        # 4. Tratar valores ausentes em colunas críticas
        critical_columns = ['order_id', 'product_id', 'customer_id']
        present_critical_columns = [col for col in critical_columns if col in processed_df.columns]
        
        if present_critical_columns:
            original_count = processed_df.shape[0]
            
            # 4.1 Contar registros com valores nulos em colunas críticas
            null_counts = {col: processed_df.filter(pl.col(col).is_null()).shape[0] for col in present_critical_columns}
            total_nulls = sum(null_counts.values())
            
            if total_nulls > 0:
                logger.warning(f"Detectados {total_nulls} valores nulos em colunas críticas: {null_counts}")
                print(f"Aviso: Detectados {total_nulls} valores nulos em colunas críticas")
                
                # 4.2 Remover registros com valores nulos em colunas críticas
                for col in present_critical_columns:
                    processed_df = processed_df.filter(~pl.col(col).is_null())
                
                removed = original_count - processed_df.shape[0]
                if removed > 0:
                    logger.info(f"Removidos {removed} registros com valores nulos em colunas críticas")
                    print(f"Removidos {removed} registros com valores nulos em colunas críticas")
        
        # 5. Validar outros campos importantes
        self._validate_numeric_columns(processed_df)
        
        logger.info(f"Processamento concluído: {processed_df.shape[0]} registros processados")
        return processed_df
    
    def _validate_numeric_columns(self, df: pl.DataFrame) -> None:
        """
        Valida colunas numéricas e registra avisos para valores negativos ou anômalos.
        
        Args:
            df (pl.DataFrame): DataFrame a ser validado.
        """
        # Colunas numéricas que não devem ser negativas
        non_negative_columns = ['price', 'quantity', 'total_value', 'shipping_cost']
        
        for col in non_negative_columns:
            if col in df.columns and pl.datatypes.is_numeric(df[col].dtype):
                try:
                    min_val = df[col].min()
                    if min_val < 0:
                        logger.warning(f"Detectados valores negativos na coluna {col}: mínimo={min_val}")
                        print(f"Aviso: Detectados valores negativos na coluna {col} (mínimo={min_val})")
                        
                        # Contar registros com valores negativos
                        neg_count = df.filter(pl.col(col) < 0).shape[0]
                        if neg_count > 0:
                            logger.info(f"{neg_count} registros contêm valores negativos na coluna {col}")
                except Exception as e:
                    logger.warning(f"Erro ao validar coluna {col}: {str(e)}")
    
    def save_processed_data(self, df: pl.DataFrame, filename: str) -> str:
        """
        Salva os dados processados em formato Parquet.
        
        Args:
            df (pl.DataFrame): DataFrame do Polars para salvar.
            filename (str): Nome do arquivo de saída.
            
        Returns:
            str: Caminho para o arquivo salvo.
            
        Raises:
            TypeError: Se o input não for um DataFrame do Polars.
            IOError: Se houver erro ao salvar o arquivo.
        """
        logger.info(f"Iniciando salvamento de dados processados: {filename}")
        
        # Validar o tipo de entrada
        if not isinstance(df, pl.DataFrame):
            logger.error("O argumento df deve ser um DataFrame do Polars")
            raise TypeError("O argumento df deve ser um DataFrame do Polars")
        
        try:
            # Extrair apenas o nome base do arquivo, sem o caminho
            base_filename = os.path.basename(filename)
            # Remover extensão
            base_name = os.path.splitext(base_filename)[0]
            
            # Criar nome do arquivo com timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"{base_name}_processed_{timestamp}.parquet"
            output_path = os.path.join(self.processed_path, output_filename)
            
            # Garantir que o diretório exista
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Salvar como Parquet (mais eficiente)
            df.write_parquet(output_path)
            logger.info(f"Dados processados salvos com sucesso em: {output_path}")
            print(f"Dados processados salvos em: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados processados: {str(e)}")
            raise IOError(f"Erro ao salvar dados processados: {str(e)}")
    
    def summarize_data(self, df: pl.DataFrame) -> Dict[str, Any]:
        """
        Gera um resumo estatístico dos dados processados.
        
        Args:
            df (pl.DataFrame): DataFrame do Polars para analisar.
            
        Returns:
            Dict[str, Any]: Dicionário com estatísticas resumidas do DataFrame.
            
        Raises:
            TypeError: Se o input não for um DataFrame do Polars.
        """
        logger.info("Gerando resumo estatístico dos dados")
        
        if not isinstance(df, pl.DataFrame):
            logger.error("O argumento df deve ser um DataFrame do Polars")
            raise TypeError("O argumento df deve ser um DataFrame do Polars")
        
        summary = {
            "num_registros": df.shape[0],
            "num_colunas": df.shape[1],
            "colunas": df.columns,
            "tipos_dados": {col: str(df[col].dtype) for col in df.columns},
            "valores_nulos": {col: df[col].null_count() for col in df.columns}
        }
        
        # Adicionar estatísticas para colunas numéricas
        summary["estatisticas"] = {}
        for col in df.columns:
            if pl.datatypes.is_numeric(df[col].dtype) and not df[col].is_empty():
                try:
                    summary["estatisticas"][col] = {
                        "min": df[col].min().item() if not df[col].null_count() == df.shape[0] else None,
                        "max": df[col].max().item() if not df[col].null_count() == df.shape[0] else None,
                        "media": df[col].mean().item() if not df[col].null_count() == df.shape[0] else None,
                        "mediana": df[col].median().item() if not df[col].null_count() == df.shape[0] else None,
                        "std": df[col].std().item() if not df[col].null_count() == df.shape[0] else None
                    }
                except Exception as e:
                    logger.warning(f"Não foi possível calcular estatísticas para coluna {col}: {str(e)}")
        
        # Adicionar informações sobre colunas de data
        summary["datas"] = {}
        for col in df.columns:
            if pl.datatypes.is_temporal(df[col].dtype) and not df[col].is_empty():
                try:
                    min_date = df[col].min()
                    max_date = df[col].max()
                    summary["datas"][col] = {
                        "min": min_date.strftime('%Y-%m-%d %H:%M:%S') if min_date else None,
                        "max": max_date.strftime('%Y-%m-%d %H:%M:%S') if max_date else None,
                        "intervalo_dias": (max_date - min_date).days if min_date and max_date else None
                    }
                except Exception as e:
                    logger.warning(f"Não foi possível calcular estatísticas de data para coluna {col}: {str(e)}")
        
        # Adicionar contagens para colunas categóricas (top 10 valores)
        summary["categorias"] = {}
        for col in df.columns:
            if df[col].dtype == pl.Utf8 and not df[col].is_empty():
                try:
                    valor_counts = df[col].value_counts().sort("counts", descending=True).head(10)
                    if valor_counts.shape[0] > 0:
                        summary["categorias"][col] = {
                            row[col]: row["counts"] for row in valor_counts.to_dicts()
                        }
                except Exception as e:
                    logger.warning(f"Não foi possível calcular contagens para coluna {col}: {str(e)}")
        
        logger.info(f"Resumo estatístico gerado: {summary['num_registros']} registros analisados")
        return summary

# Configuração de logging para uso standalone
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Este módulo não deve ser executado diretamente.")
    print("Utilize-o através da classe EcommerceModel em sua aplicação.")
    print("\nExemplo de uso:")
    print("from src.models.ecommerce_model import EcommerceModel")
    print("model = EcommerceModel()")
    print("df = model.load_data('vendas.csv')")
    print("df_processado = model.process_sales_data(df)")
    print("model.save_processed_data(df_processado, 'vendas.csv')")