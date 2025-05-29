#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Testes simples para o controlador de análise de e-commerce.
Autor: Vitor Oliveira (https://github.com/vitordoliveira)
Data de Criação: 2025-05-26
"""

import os
import sys
import polars as pl
from src.controllers.analise_controller import AnaliseController
from src.models.obter_dados_ecommerce import ObterDadosEcommerce

def test_fluxo_basico():
    """Testa o fluxo básico do controlador com dados sintéticos."""
    print("Teste de Fluxo Básico do Controlador")
    print("-" * 50)
    
    # Gerar dados de teste
    print("Gerando dados sintéticos para teste...")
    gerador = ObterDadosEcommerce()
    arquivo_teste = os.path.basename(gerador.gerar_dados_sinteticos(500))
    
    # Inicializar controlador
    controller = AnaliseController()
    
    # Processar dados
    print(f"Processando dados de teste: {arquivo_teste}")
    resultado = controller.processar_dados_vendas(arquivo_teste, 
                                                  salvar_processado=True, 
                                                  exportar_powerbi=True)
    
    # Verificar resultado
    df = resultado['dados_processados']
    
    # Testes simples
    assert df is not None, "DataFrame processado não deveria ser None"
    assert isinstance(df, pl.DataFrame), "Resultado deveria ser um DataFrame do Polars"
    assert df.shape[0] > 0, "DataFrame não deveria estar vazio"
    assert len(resultado['arquivos_gerados']) > 0, "Deveria ter gerado arquivos"
    
    print(f"Número de registros processados: {df.shape[0]}")
    print(f"Colunas disponíveis: {', '.join(df.columns)}")
    print(f"Arquivos gerados: {len(resultado['arquivos_gerados'])}")
    
    print("\nTESTE CONCLUÍDO COM SUCESSO!")
    
    return True

if __name__ == "__main__":
    # Executar teste
    try:
        success = test_fluxo_basico()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)