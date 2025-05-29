import os
import pandas as pd
import polars as pl
import logging
from datetime import datetime, timedelta
import random
from typing import Optional, Dict, List

# Configuração de logging
logger = logging.getLogger('ecommerce_analytics.dados')

class ObterDadosEcommerce:
    """
    Classe para obter dados de amostra de e-commerce.
    Pode baixar dados públicos ou gerar dados sintéticos para testes.
    """
    
    def __init__(self, data_dir=None):
        """
        Inicializa o gerador com o diretório de destino.
        
        Args:
            data_dir (str, optional): Diretório para salvar os dados.
                                     Se None, usa o diretório padrão.
        """
        self.data_dir = data_dir or os.path.join('data', 'raw')
        os.makedirs(self.data_dir, exist_ok=True)
        logger.info(f"Inicializado gerador de dados com diretório: {self.data_dir}")
        
        # Inicializar dados de sementes para geração de dados
        self._inicializar_dados_sementes()
        
    def _inicializar_dados_sementes(self):
        """Inicializa dados de sementes para geração de dados sintéticos realistas."""
        # Categorias de produtos
        self.categorias = [
            'Eletrônicos', 'Roupas', 'Livros', 'Casa e Jardim', 
            'Esportes', 'Beleza', 'Brinquedos', 'Alimentos', 
            'Saúde', 'Ferramentas'
        ]
        
        # Métodos de pagamento
        self.metodos_pagamento = [
            'Cartão de Crédito', 'Boleto', 'Pix', 'PayPal', 
            'Apple Pay', 'Google Pay', 'Cartão de Débito'
        ]
        
        # Estados brasileiros
        self.estados = [
            'SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'PE', 'CE', 'GO',
            'DF', 'PA', 'AM', 'MA', 'ES', 'PB', 'RN', 'MT', 'MS', 'AL'
        ]
        
        # Mapear regiões para estados
        self.regiao_por_estado = {
            'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 
            'RR': 'Norte', 'TO': 'Norte',
            'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 
            'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 
            'SE': 'Nordeste',
            'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MT': 'Centro-Oeste',
            'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
            'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
        }
        
        # Nomes populares para geração de dados de clientes
        self.nomes = [
            "João", "Maria", "Pedro", "Ana", "Carlos", "Fernanda", "José", 
            "Mariana", "Paulo", "Juliana", "Lucas", "Amanda", "Ricardo", 
            "Patricia", "Miguel", "Camila", "Fernando", "Luiza", "Gabriel"
        ]
                      
        self.sobrenomes = [
            "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", 
            "Alves", "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins"
        ]
        
    def download_kaggle_dataset(self, dataset_url: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Baixa um dataset público do Kaggle.
        Nota: Requer configuração prévia da API do Kaggle.
        
        Args:
            dataset_url (str): URL do dataset no Kaggle.
            filename (str, optional): Nome do arquivo para salvar.
            
        Returns:
            Optional[str]: Caminho para o arquivo baixado ou None se falhar.
        """
        logger.info(f"Tentando baixar dataset do Kaggle: {dataset_url}")
        print("Tentando baixar dataset do Kaggle...")
        
        # Verificar se a URL é válida
        if "kaggle.com/datasets/" not in dataset_url:
            mensagem = "URL do Kaggle inválida. Use o formato: https://www.kaggle.com/datasets/owner/dataset"
            logger.error(mensagem)
            print(mensagem)
            return None
            
        # Informar sobre a necessidade da API do Kaggle
        print("Para usar este método, é necessário ter a API do Kaggle configurada:")
        print("1. Instale a API do Kaggle com 'pip install kaggle'")
        print("2. Configure suas credenciais conforme: https://github.com/Kaggle/kaggle-api")
        print("Alternativamente, use o método gerar_dados_sinteticos() para testes rápidos")
        
        try:
            # Tentar importar a API do Kaggle dinamicamente para evitar erros
            import importlib
            kaggle_spec = importlib.util.find_spec("kaggle")
            
            if kaggle_spec is None:
                logger.error("Biblioteca kaggle não está instalada")
                print("Erro: Biblioteca kaggle não está instalada. Instale com: pip install kaggle")
                return None
                
            kaggle = importlib.import_module("kaggle")
            
            # Extrair owner/dataset da URL
            if "kaggle.com/datasets/" in dataset_url:
                path_parts = dataset_url.split("kaggle.com/datasets/")[1].strip("/").split("/")
                if len(path_parts) >= 2:
                    dataset_path = f"{path_parts[0]}/{path_parts[1]}"
                    
                    # Criar diretório temporário para download
                    import tempfile
                    temp_dir = tempfile.mkdtemp()
                    
                    # Download do dataset
                    print(f"Baixando dataset: {dataset_path}")
                    kaggle.api.dataset_download_files(dataset_path, path=temp_dir, unzip=True)
                    
                    # Listar arquivos baixados
                    downloaded_files = os.listdir(temp_dir)
                    if not downloaded_files:
                        logger.error("Nenhum arquivo baixado")
                        print("Falha: Nenhum arquivo baixado")
                        return None
                    
                    # Encontrar arquivos CSV ou Parquet
                    data_files = [f for f in downloaded_files if f.endswith('.csv') or f.endswith('.parquet')]
                    if not data_files:
                        data_files = downloaded_files  # Se não houver CSV/Parquet, usar qualquer arquivo
                    
                    # Selecionar o arquivo a ser movido
                    file_to_move = data_files[0]  # Usar o primeiro arquivo encontrado
                    source_path = os.path.join(temp_dir, file_to_move)
                    
                    # Definir nome do arquivo de destino
                    if not filename:
                        filename = f"kaggle_{path_parts[0]}_{path_parts[1]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(file_to_move)[1]}"
                    
                    # Garantir que o nome do arquivo tenha extensão correta
                    if not any(filename.endswith(ext) for ext in ['.csv', '.parquet', '.json']):
                        filename += os.path.splitext(file_to_move)[1]
                    
                    # Mover arquivo para diretório de dados
                    import shutil
                    dest_path = os.path.join(self.data_dir, filename)
                    shutil.copy2(source_path, dest_path)
                    
                    logger.info(f"Dataset baixado com sucesso: {dest_path}")
                    print(f"Dataset baixado com sucesso: {dest_path}")
                    return dest_path
                else:
                    logger.error("URL do Kaggle mal formada")
                    print("URL do Kaggle mal formada")
            
        except ImportError:
            logger.error("API do Kaggle não instalada")
            print("API do Kaggle não instalada. Instale com: pip install kaggle")
            
        except Exception as e:
            logger.error(f"Erro ao baixar dataset do Kaggle: {str(e)}")
            print(f"Erro ao baixar dataset do Kaggle: {str(e)}")
            
        return None
        
    def gerar_dados_sinteticos(self, num_registros: int = 1000, 
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None) -> str:
        """
        Gera um conjunto de dados sintéticos de vendas de e-commerce.
        
        Args:
            num_registros (int): Número de registros a serem gerados.
            start_date (str, optional): Data de início no formato 'YYYY-MM-DD'.
            end_date (str, optional): Data de fim no formato 'YYYY-MM-DD'.
            
        Returns:
            str: Caminho para o arquivo gerado.
            
        Raises:
            ValueError: Se os parâmetros de data forem inválidos.
            IOError: Se houver erro ao salvar o arquivo.
        """
        try:
            logger.info(f"Gerando {num_registros} registros de dados sintéticos...")
            print(f"Gerando {num_registros} registros de dados sintéticos...")
            
            # Validar número de registros
            if num_registros <= 0:
                num_registros = 1000
                logger.warning(f"Número de registros inválido, usando valor padrão: {num_registros}")
            
            # Definir período de datas
            hoje = datetime.now()
            if not start_date:
                start_date = (hoje - timedelta(days=365)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = hoje.strftime('%Y-%m-%d')
                
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                
                # Verificar se as datas são válidas
                if end_datetime < start_datetime:
                    logger.warning("Data final é anterior à data inicial. Invertendo datas.")
                    start_datetime, end_datetime = end_datetime, start_datetime
            except ValueError as e:
                logger.error(f"Formato de data inválido: {str(e)}")
                raise ValueError(f"Formato de data inválido. Use o formato YYYY-MM-DD: {str(e)}")
            
            # Gerar dados
            dados = []
            for _ in range(num_registros):
                # Data da compra
                dias_aleatorios = random.randint(0, (end_datetime - start_datetime).days)
                data_compra = start_datetime + timedelta(days=dias_aleatorios)
                
                # Hora aleatória
                hora = random.randint(8, 23)
                minuto = random.randint(0, 59)
                segundo = random.randint(0, 59)
                data_compra = data_compra.replace(hour=hora, minute=minuto, second=segundo)
                
                # Informações do produto
                categoria = random.choice(self.categorias)
                preco = round(random.uniform(10.0, 500.0), 2)
                quantidade = random.randint(1, 5)
                
                # Status do pedido com distribuição ponderada
                status_pedido = random.choices(
                    ['Entregue', 'Em processamento', 'Enviado', 'Cancelado'],
                    weights=[0.7, 0.1, 0.15, 0.05],
                    k=1
                )[0]
                
                # Informações do cliente
                estado_cliente = random.choice(self.estados)
                regiao_cliente = self.regiao_por_estado.get(estado_cliente, 'Não definida')
                
                # Método de pagamento
                metodo_pagamento = random.choice(self.metodos_pagamento)
                
                # Frete
                valor_frete = round(random.uniform(5.0, 30.0), 2)
                
                # ID da transação
                id_transacao = f"TRX-{random.randint(100000, 999999)}"
                
                # Adicionar ao conjunto de dados
                dados.append({
                    'transaction_id': id_transacao,
                    'date': data_compra.strftime('%Y-%m-%d %H:%M:%S'),
                    'customer_id': f"CUST-{random.randint(1000, 9999)}",
                    'product_id': f"PROD-{random.randint(10000, 99999)}",
                    'product_category': categoria,
                    'price': preco,
                    'quantity': quantidade,
                    'total_value': round(preco * quantidade, 2),
                    'payment_method': metodo_pagamento,
                    'shipping_cost': valor_frete,
                    'state': estado_cliente,
                    'region': regiao_cliente,
                    'order_status': status_pedido
                })
            
            # Converter para DataFrame
            df = pd.DataFrame(dados)
            
            # Salvar como CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"ecommerce_sales_synthetic_{timestamp}.csv"
            output_path = os.path.join(self.data_dir, output_filename)
            
            df.to_csv(output_path, index=False)
            logger.info(f"Dados sintéticos gerados e salvos em: {output_path}")
            print(f"Dados sintéticos gerados e salvos em: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados sintéticos: {str(e)}", exc_info=True)
            raise RuntimeError(f"Erro ao gerar dados sintéticos: {str(e)}")

    def gerar_dados_clientes(self, num_clientes: int = 500) -> str:
        """
        Gera um conjunto de dados sintéticos de clientes.
        
        Args:
            num_clientes (int): Número de registros de clientes a serem gerados.
            
        Returns:
            str: Caminho para o arquivo gerado.
            
        Raises:
            ValueError: Se o número de clientes for inválido.
            IOError: Se houver erro ao salvar o arquivo.
        """
        try:
            logger.info(f"Gerando {num_clientes} registros de dados de clientes...")
            print(f"Gerando {num_clientes} registros de dados de clientes...")
            
            # Validar número de clientes
            if num_clientes <= 0:
                num_clientes = 500
                logger.warning(f"Número de clientes inválido, usando valor padrão: {num_clientes}")
            
            dados_clientes = []
            
            for i in range(1, num_clientes + 1):
                # ID do cliente
                customer_id = f"CUST-{i:04d}"
                
                # Nome do cliente
                nome = random.choice(self.nomes)
                sobrenome = random.choice(self.sobrenomes)
                nome_completo = f"{nome} {sobrenome}"
                
                # Email
                email = f"{nome.lower()}.{sobrenome.lower()}{random.randint(1, 999)}@example.com"
                
                # Localização
                estado = random.choice(self.estados)
                regiao = self.regiao_por_estado.get(estado, '')
                
                # Demografia
                idade = random.randint(18, 80)
                genero = random.choice(['M', 'F'])
                
                # Segmentação
                segmento = random.choices(['Regular', 'Premium', 'VIP'], weights=[0.7, 0.2, 0.1])[0]
                
                # Data de cadastro (entre 1 e 5 anos atrás)
                dias_atras = random.randint(30, 5*365)
                data_cadastro = datetime.now() - timedelta(days=dias_atras)
                
                # Adicionar cliente ao dataset
                dados_clientes.append({
                    'customer_id': customer_id,
                    'name': nome_completo,
                    'email': email,
                    'age': idade,
                    'gender': genero,
                    'state': estado,
                    'region': regiao,
                    'segment': segmento,
                    'registration_date': data_cadastro.strftime('%Y-%m-%d')
                })
            
            # Converter para DataFrame
            df = pd.DataFrame(dados_clientes)
            
            # Salvar como CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"ecommerce_customers_{timestamp}.csv"
            output_path = os.path.join(self.data_dir, output_filename)
            
            df.to_csv(output_path, index=False)
            logger.info(f"Dados de clientes gerados e salvos em: {output_path}")
            print(f"Dados de clientes gerados e salvos em: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados de clientes: {str(e)}", exc_info=True)
            raise RuntimeError(f"Erro ao gerar dados de clientes: {str(e)}")
    
    def verificar_dados(self, arquivo: str) -> Optional[Dict]:
        """
        Verifica a integridade e estatísticas básicas dos dados.
        
        Args:
            arquivo (str): Caminho para o arquivo a ser verificado.
            
        Returns:
            Optional[Dict]: Dicionário com estatísticas e informações sobre os dados.
        """
        try:
            logger.info(f"Verificando dados do arquivo: {arquivo}")
            
            # Verificar se o arquivo existe
            if not os.path.exists(arquivo):
                logger.error(f"Arquivo não encontrado: {arquivo}")
                print(f"Erro: Arquivo não encontrado: {arquivo}")
                return None
            
            # Determinar o formato do arquivo
            if arquivo.endswith('.csv'):
                df = pl.read_csv(arquivo)
            elif arquivo.endswith('.parquet'):
                df = pl.read_parquet(arquivo)
            else:
                logger.error(f"Formato de arquivo não suportado: {arquivo}")
                raise ValueError(f"Formato de arquivo não suportado: {arquivo}")
            
            # Coletar estatísticas
            num_registros = df.shape[0]
            num_colunas = df.shape[1]
            colunas = df.columns
            
            # Verificar valores ausentes
            valores_ausentes = {col: df[col].null_count() for col in colunas}
            
            # Verificar tipos de dados
            tipos_dados = {col: str(df[col].dtype) for col in colunas}
            
            # Estatísticas numéricas
            estatisticas_numericas = {}
            for col in colunas:
                if pl.datatypes.is_numeric(df[col].dtype):
                    estatisticas_numericas[col] = {
                        'min': df[col].min().item() if not df[col].is_empty() else None,
                        'max': df[col].max().item() if not df[col].is_empty() else None,
                        'media': df[col].mean().item() if not df[col].is_empty() else None,
                        'mediana': df[col].median().item() if not df[col].is_empty() else None
                    }
            
            # Compilar resultados
            resultado = {
                'arquivo': arquivo,
                'num_registros': num_registros,
                'num_colunas': num_colunas,
                'colunas': colunas,
                'valores_ausentes': valores_ausentes,
                'tipos_dados': tipos_dados,
                'estatisticas_numericas': estatisticas_numericas
            }
            
            logger.info(f"Verificação concluída: {num_registros} registros, {num_colunas} colunas")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao verificar dados: {str(e)}", exc_info=True)
            print(f"Erro ao verificar dados: {str(e)}")
            return None
    
    def combinar_arquivos(self, arquivos: List[str], coluna_chave: Optional[str] = None) -> Optional[str]:
        """
        Combina múltiplos arquivos em um único dataset.
        
        Args:
            arquivos (List[str]): Lista de caminhos de arquivos a combinar.
            coluna_chave (str, optional): Nome da coluna para junção (merge).
                                         Se None, concatena verticalmente.
            
        Returns:
            Optional[str]: Caminho para o arquivo combinado ou None se falhar.
        """
        try:
            if not arquivos or len(arquivos) < 2:
                logger.error("Pelo menos dois arquivos são necessários para combinar")
                print("Erro: Pelo menos dois arquivos são necessários para combinar")
                return None
            
            logger.info(f"Combinando {len(arquivos)} arquivos")
            print(f"Combinando {len(arquivos)} arquivos...")
            
            # Carregar todos os arquivos
            dfs = []
            for arquivo in arquivos:
                if not os.path.exists(arquivo):
                    logger.error(f"Arquivo não encontrado: {arquivo}")
                    print(f"Erro: Arquivo não encontrado: {arquivo}")
                    return None
                
                try:
                    # Carregar baseado na extensão
                    if arquivo.lower().endswith('.csv'):
                        df = pl.read_csv(arquivo)
                    elif arquivo.lower().endswith('.parquet'):
                        df = pl.read_parquet(arquivo)
                    else:
                        logger.error(f"Formato não suportado: {arquivo}")
                        print(f"Erro: Formato não suportado: {arquivo}")
                        continue
                    
                    dfs.append(df)
                    logger.info(f"Carregado {arquivo}: {df.shape[0]} registros")
                except Exception as e:
                    logger.error(f"Erro ao carregar {arquivo}: {str(e)}")
                    print(f"Erro ao carregar {arquivo}: {str(e)}")
                    return None
            
            if not dfs:
                logger.error("Nenhum arquivo foi carregado com sucesso")
                print("Erro: Nenhum arquivo foi carregado com sucesso")
                return None
            
            # Combinar DataFrames
            resultado = None
            
            if coluna_chave:
                # Merge baseado na coluna chave
                print(f"Realizando merge baseado na coluna '{coluna_chave}'...")
                
                # Verificar se todos os DFs têm a coluna chave
                for i, df in enumerate(dfs):
                    if coluna_chave not in df.columns:
                        logger.error(f"Coluna '{coluna_chave}' não encontrada no arquivo {i+1}")
                        print(f"Erro: Coluna '{coluna_chave}' não encontrada no arquivo {i+1}")
                        return None
                
                # Usar o primeiro DF como base
                resultado = dfs[0]
                
                # Merge com os demais DFs
                for i, df in enumerate(dfs[1:], 1):
                    try:
                        resultado = resultado.join(df, on=coluna_chave, how="left")
                        logger.info(f"Merge com arquivo {i+1} concluído")
                    except Exception as e:
                        logger.error(f"Erro no merge com arquivo {i+1}: {str(e)}")
                        print(f"Erro no merge com arquivo {i+1}: {str(e)}")
                        return None
            else:
                # Concatenação vertical
                print("Realizando concatenação vertical...")
                
                # Verificar se as colunas são compatíveis
                all_columns = set(dfs[0].columns)
                for i, df in enumerate(dfs[1:], 1):
                    df_columns = set(df.columns)
                    if df_columns != all_columns:
                        logger.warning(f"Arquivo {i+1} tem colunas diferentes")
                        print(f"Aviso: Arquivo {i+1} tem colunas diferentes")
                
                # Concatenar
                resultado = pl.concat(dfs, how="diagonal")
                logger.info(f"Concatenação concluída: {resultado.shape[0]} registros")
            
            # Salvar resultado
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"combined_data_{timestamp}.csv"
            output_path = os.path.join(self.data_dir, output_filename)
            resultado.write_csv(output_path)
            
            logger.info(f"Dados combinados salvos em: {output_path}")
            print(f"Dados combinados salvos em: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao combinar arquivos: {str(e)}", exc_info=True)
            print(f"Erro ao combinar arquivos: {str(e)}")
            return None

# Se executado como script
if __name__ == "__main__":
    # Configurar logging para execução standalone
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Obter data e hora atuais
    data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    usuario_atual = os.getenv('USERNAME', 'vitordoliveira')
    
    print(f"E-commerce Data Generator")
    print(f"Data: {data_atual}")
    print(f"Usuário: {usuario_atual}")
    print("-" * 50)
    
    # Número de registros a gerar
    try:
        num_registros = int(input("Número de registros a gerar (padrão: 5000): ") or "5000")
    except ValueError:
        print("Entrada inválida. Usando valor padrão de 5000 registros.")
        num_registros = 5000
    
    # Gerar dados
    gerador = ObterDadosEcommerce()
    arquivo_gerado = gerador.gerar_dados_sinteticos(num_registros)
    
    # Mostrar preview dos dados
    if arquivo_gerado:
        df = pl.read_csv(arquivo_gerado)
        print("\nVisualização dos dados gerados:")
        print(df.head())
        print(f"\nTotal de registros: {df.shape[0]}")
        
        # Verificar dados
        print("\nRealizando verificação dos dados...")
        estatisticas = gerador.verificar_dados(arquivo_gerado)
        if estatisticas:
            print(f"Verificação concluída com sucesso.")
            print(f"Número de registros: {estatisticas['num_registros']}")
            print(f"Número de colunas: {estatisticas['num_colunas']}")