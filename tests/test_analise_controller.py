# tests/test_analise_controller.py
import os
import pytest
import polars as pl
from src.controllers.analise_controller import AnaliseController
from src.models.obter_dados_ecommerce import ObterDadosEcommerce

class TestAnaliseController:
    """Testes para a classe AnaliseController."""
    
    def setup_method(self):
        """Configuração para cada teste."""
        # Garantir que os diretórios necessários existam
        diretorios = [
            os.path.join('data', 'raw'),
            os.path.join('data', 'processed'),
            os.path.join('exports', 'powerbi')
        ]
        
        for diretorio in diretorios:
            os.makedirs(diretorio, exist_ok=True)
            
        self.controller = AnaliseController()
        self.gerador = ObterDadosEcommerce()
        # Gerar dados para testes - removido parâmetro nome_arquivo
        self.arquivo_teste = self.gerador.gerar_dados_sinteticos(15)
        # Importante: verificar se o caminho é absoluto para evitar erros de duplicação
        if not os.path.isabs(self.arquivo_teste):
            self.arquivo_teste = os.path.abspath(self.arquivo_teste)
        
    def test_processar_dados_vendas(self):
        """Testa o processamento dos dados de vendas."""
        # Verificar se o arquivo existe
        assert os.path.exists(self.arquivo_teste), f"Arquivo de teste não encontrado: {self.arquivo_teste}"
        
        # Processar os dados
        resultado = self.controller.processar_dados_vendas(
            self.arquivo_teste, 
            salvar_processado=True, 
            exportar_powerbi=False
        )
        
        # Verificar se o processamento retornou um dicionário
        assert isinstance(resultado, dict)
        
        # Verificar se dados foram processados
        assert 'dados_processados' in resultado
        df_processado = resultado['dados_processados']
        
        # Verificar se o DataFrame processado tem as colunas esperadas
        assert 'total_value' in df_processado.columns
        
        # Verificar se foram gerados alguns arquivos
        assert 'arquivos_gerados' in resultado
        assert len(resultado['arquivos_gerados']) > 0
        
    def test_analisar_vendas_por_periodo(self):
        """Testa a análise de vendas por período."""
        # Verificar se o arquivo existe
        assert os.path.exists(self.arquivo_teste), f"Arquivo de teste não encontrado: {self.arquivo_teste}"
        
        # Carregar os dados
        df = pl.read_csv(self.arquivo_teste)
        
        # Verificar colunas necessárias
        assert 'date' in df.columns, f"Coluna 'date' não encontrada. Colunas disponíveis: {df.columns}"
        assert 'price' in df.columns, f"Coluna 'price' não encontrada. Colunas disponíveis: {df.columns}"
        assert 'quantity' in df.columns, f"Coluna 'quantity' não encontrada. Colunas disponíveis: {df.columns}"
        
        # Converter a coluna 'date' para o tipo Date para poder usar operações de data
        # Atualizado para suportar o formato que inclui horas
        df_processado = df.with_columns([
            # Converter a coluna de string para datetime usando o formato correto com horas
            pl.col('date').str.strptime(pl.Date, format='%Y-%m-%d %H:%M:%S').alias('date'),
            # Calcular o valor total
            (pl.col('price') * pl.col('quantity')).alias('total_value')
        ])
        
        # Realizar análise por período
        analises = self.controller.analisar_vendas_por_periodo(
            df_processado,
            'date',
            'total_value'
        )
        
        # Verificar se retornou um dicionário de análises
        assert isinstance(analises, dict)
        
        # Verificar se contém pelo menos uma análise
        assert len(analises) > 0
        for key, value in analises.items():
            assert isinstance(value, pl.DataFrame)
            
    def test_exportar_analise_para_powerbi(self):
        """Testa a exportação de análises para Power BI."""
        # Verificar se o arquivo existe
        assert os.path.exists(self.arquivo_teste), f"Arquivo de teste não encontrado: {self.arquivo_teste}"
        
        # Garantir que o diretório de exportação existe
        export_dir = os.path.join('exports', 'powerbi')
        os.makedirs(export_dir, exist_ok=True)
        
        # Carregar os dados
        df = pl.read_csv(self.arquivo_teste)
        
        # Verificar colunas necessárias
        assert 'price' in df.columns, f"Coluna 'price' não encontrada. Colunas disponíveis: {df.columns}"
        assert 'quantity' in df.columns, f"Coluna 'quantity' não encontrada. Colunas disponíveis: {df.columns}"
        assert 'product_category' in df.columns, f"Coluna 'product_category' não encontrada. Colunas disponíveis: {df.columns}"
        
        # Processar os dados
        df_processado = df.with_columns([
            (pl.col('price') * pl.col('quantity')).alias('total_value')
        ])
        
        # Criar análises manualmente para testar apenas a exportação
        # Corrigido: groupby -> group_by
        analises = {
            'vendas_por_categoria': df_processado.group_by('product_category').agg(
                pl.sum('total_value').alias('total_vendas')
            )
        }
        
        # Exportar para Power BI
        arquivos_exportados = self.controller.exportar_analise_para_powerbi(analises)
        
        # Verificar se foram gerados arquivos
        assert len(arquivos_exportados) > 0
        
        # Verificar se os arquivos existem
        for _, caminho in arquivos_exportados:
            assert os.path.exists(caminho), f"Arquivo exportado não encontrado: {caminho}"
            
    def teardown_method(self):
        """Limpeza após cada teste."""
        # Remover arquivos temporários criados durante os testes
        diretorios = [
            os.path.join('data', 'raw'),
            os.path.join('data', 'processed'),
            os.path.join('exports', 'powerbi')
        ]
        
        for diretorio in diretorios:
            if os.path.exists(diretorio):
                for arquivo in os.listdir(diretorio):
                    # Não remover arquivos específicos que podem ser necessários para outros testes
                    if arquivo.startswith('ecommerce_') and arquivo.endswith('.csv') and not arquivo.endswith('195957.csv'):
                        try:
                            os.remove(os.path.join(diretorio, arquivo))
                        except:
                            pass