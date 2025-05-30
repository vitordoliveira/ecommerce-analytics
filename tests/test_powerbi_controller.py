import os
import pytest
import polars as pl
from datetime import datetime, timedelta
from src.controllers.powerbi_controller import PowerBIController
from src.models.obter_dados_ecommerce import ObterDadosEcommerce

class TestPowerBIController:
    """Testes para a classe PowerBIController."""
    
    def setup_method(self):
        """Configuração para cada teste."""
        self.controller = PowerBIController()
        self.gerador = ObterDadosEcommerce()
        # Gerar dados para testes - removido parâmetro nome_arquivo
        self.arquivo_teste = self.gerador.gerar_dados_sinteticos(15)
        # Verificar se o caminho é absoluto para evitar erros de duplicação
        if not os.path.isabs(self.arquivo_teste):
            self.arquivo_teste = os.path.abspath(self.arquivo_teste)
        self.df_teste = pl.read_csv(self.arquivo_teste)
        
    def test_criar_calendario_powerbi(self):
        """Testa a criação de uma tabela de calendário."""
        # Criar tabela de calendário
        data_inicio = "2025-01-01"
        data_fim = "2025-12-31"
        
        # Verificar se o método existe antes de chamá-lo
        assert hasattr(self.controller, 'criar_calendario_powerbi'), "Método criar_calendario_powerbi não existe"
        
        # Chamar o método normalmente agora que foi corrigido
        caminho_calendario = self.controller.criar_calendario_powerbi(
            data_inicio,
            data_fim,
            "teste_calendario"
        )
        
        # Verificar se o arquivo foi criado
        assert os.path.exists(caminho_calendario)
        
        # Carregar o calendário e verificar
        df_calendario = pl.read_csv(caminho_calendario)
        
        # Verificar se tem as colunas esperadas
        colunas_esperadas = ['Data', 'Dia', 'Mês', 'Ano', 'Nome do Mês']
        for coluna in colunas_esperadas:
            assert coluna in df_calendario.columns
            
        # Verificar número de registros (deve ter 365 dias para um ano)
        assert df_calendario.shape[0] == 365
        
    def test_gerar_dashboard_powerbi(self):
        """Testa a geração de um dashboard Power BI."""
        # Verificar se o método existe antes de chamá-lo
        assert hasattr(self.controller, 'gerar_dashboard_powerbi'), "Método gerar_dashboard_powerbi não existe"
        
        # Processar dados para teste
        df_processado = self.df_teste.with_columns([
            (pl.col('price') * pl.col('quantity')).alias('total_value')
        ])
        
        # Definir data de início/fim fixas para o teste
        # Isso evita problemas com formato de data no DataFrame
        data_inicio = "2025-01-01"
        data_fim = "2025-12-31"
        
        # Criar um dashboard usando os dados de teste
        resultado = self.controller.gerar_dashboard_powerbi(
            df_processado,
            data_inicio,
            data_fim,
            "teste_dashboard",
            usuario="vitordoliveiraagora"
        )
        
        # Verificar se um dicionário de resultados foi retornado
        assert isinstance(resultado, dict)
        
        # Verificar se o arquivo de template foi criado
        assert 'caminho_template' in resultado
        assert os.path.exists(resultado['caminho_template'])
        
        # Verificar se o arquivo contém as marcações esperadas
        with open(resultado['caminho_template'], 'r', encoding='utf-8') as f:
            conteudo = f.read()
            assert "Power BI Dashboard" in conteudo
            assert "vitordoliveiraagora" in conteudo  # O nome do usuário deve estar presente
        
    def teardown_method(self):
        """Limpeza após cada teste."""
        # Remover arquivos temporários criados durante os testes
        diretorios = [
            os.path.join('data', 'raw'),
            os.path.join('exports', 'powerbi')
        ]
        
        for diretorio in diretorios:
            if os.path.exists(diretorio):
                for arquivo in os.listdir(diretorio):
                    if arquivo.startswith('teste_') or (arquivo.startswith('ecommerce_') and not arquivo.endswith('195957.csv')):
                        try:
                            os.remove(os.path.join(diretorio, arquivo))
                        except:
                            pass