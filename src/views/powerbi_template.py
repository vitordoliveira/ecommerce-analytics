"""
Módulo para geração de templates do Power BI.
Fornece funcionalidades para criar modelos, scripts DAX e metadados para o Power BI.

Autor: Vitor Oliveira
Data: 2025-05-28
"""

import os
import json
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Any, Union

# Configuração de logging
logger = logging.getLogger('ecommerce_analytics.powerbi_template')

class PowerBITemplate:
    """
    Classe para geração de templates, modelos e scripts para o Power BI.
    
    Fornece métodos para criar metadados de modelos, scripts DAX para medidas
    e templates de métricas para uso no Power BI.
    """
    
    def __init__(self, output_path: Optional[str] = None):
        """
        Inicializa o gerador de templates com o diretório de saída.
        
        Args:
            output_path (str, optional): Diretório para salvar os arquivos.
                                       Se None, usa o diretório padrão.
        """
        self.output_path = output_path or os.path.join('exports', 'powerbi_templates')
        os.makedirs(self.output_path, exist_ok=True)
        logger.info(f"PowerBITemplate inicializado com diretório: {self.output_path}")
        
        # Definir as métricas padrão para e-commerce
        self.metricas_padrao = [
            {
                "nome": "Total de Vendas",
                "descricao": "Soma total das vendas",
                "formula": "SUM(Vendas[total_value])",
                "formato": "Moeda",
                "categoria": "Financeiro"
            },
            {
                "nome": "Número de Transações",
                "descricao": "Total de transações realizadas",
                "formula": "COUNTROWS(Vendas)",
                "formato": "Número Inteiro",
                "categoria": "Operacional"
            },
            {
                "nome": "Ticket Médio",
                "descricao": "Valor médio por transação",
                "formula": "DIVIDE([Total de Vendas], [Número de Transações], 0)",
                "formato": "Moeda",
                "categoria": "Financeiro"
            },
            {
                "nome": "Clientes Únicos",
                "descricao": "Número de clientes únicos",
                "formula": "DISTINCTCOUNT(Vendas[customer_id])",
                "formato": "Número Inteiro",
                "categoria": "Cliente"
            },
            {
                "nome": "Taxa de Crescimento MoM",
                "descricao": "Crescimento em relação ao mês anterior",
                "formula": """
                    VAR VendasMesAtual = CALCULATE([Total de Vendas], DATESPERIODSAMT(Calendario[Data], MAX(Calendario[Data]), 0, MONTH))
                    VAR VendasMesAnterior = CALCULATE([Total de Vendas], DATESPERIODSAMT(Calendario[Data], MAX(Calendario[Data]), -1, MONTH))
                    RETURN
                    IF(VendasMesAnterior <> 0, DIVIDE(VendasMesAtual - VendasMesAnterior, VendasMesAnterior), BLANK())
                """,
                "formato": "Percentual",
                "categoria": "Financeiro"
            }
        ]
    
    def gerar_metadata_modelo(self, 
                             nome_modelo: str, 
                             descricao: str, 
                             arquivos_dados: List[str]) -> str:
        """
        Gera um arquivo de metadados para um modelo do Power BI.
        
        Args:
            nome_modelo (str): Nome do modelo a ser criado.
            descricao (str): Descrição do modelo.
            arquivos_dados (List[str]): Lista de caminhos para os arquivos de dados.
            
        Returns:
            str: Caminho para o arquivo de metadados gerado.
            
        Raises:
            ValueError: Se a lista de arquivos estiver vazia.
        """
        logger.info(f"Gerando metadados para modelo: {nome_modelo}")
        
        # Validar entrada
        if not arquivos_dados:
            logger.error("Lista de arquivos vazia")
            raise ValueError("A lista de arquivos de dados não pode estar vazia")
        
        try:
            # Criar estrutura de metadados
            metadados = {
                "modelo": {
                    "nome": nome_modelo,
                    "descricao": descricao,
                    "versao": "1.0.0",
                    "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "criado_por": os.getenv('USERNAME', 'vitordoliveira'),
                    "conexoes": []
                },
                "tabelas": [],
                "relacoes": [],
                "medidas": []
            }
            
            # Adicionar informações sobre os arquivos de dados
            for i, arquivo in enumerate(arquivos_dados):
                if os.path.exists(arquivo):
                    nome_base = os.path.basename(arquivo)
                    nome_tabela = os.path.splitext(nome_base)[0]
                    extensao = os.path.splitext(arquivo)[1].lower()
                    
                    # Adicionar conexão
                    metadados["modelo"]["conexoes"].append({
                        "id": f"conexao_{i+1}",
                        "nome": f"Conexão {nome_tabela}",
                        "tipo": extensao.replace(".", "").upper(),
                        "caminho": arquivo
                    })
                    
                    # Obter estrutura da tabela
                    try:
                        colunas = []
                        if extensao.lower() == '.csv':
                            df = pd.read_csv(arquivo, nrows=5)
                            for col in df.columns:
                                colunas.append({
                                    "nome": col,
                                    "tipo": str(df[col].dtype),
                                    "descricao": ""
                                })
                        elif extensao.lower() == '.parquet':
                            try:
                                import pyarrow.parquet as pq
                                tabela = pq.read_metadata(arquivo)
                                for i, col in enumerate(tabela.schema.names):
                                    colunas.append({
                                        "nome": col,
                                        "tipo": str(tabela.schema.types[i]),
                                        "descricao": ""
                                    })
                            except ImportError:
                                logger.warning("Biblioteca pyarrow não encontrada para ler metadados de parquet")
                                colunas.append({
                                    "nome": "Metadados não disponíveis",
                                    "tipo": "Desconhecido",
                                    "descricao": "Instale pyarrow para ver metadados de arquivos parquet"
                                })
                    except Exception as e:
                        logger.warning(f"Não foi possível ler estrutura do arquivo {arquivo}: {str(e)}")
                        colunas.append({
                            "nome": "Erro ao ler estrutura",
                            "tipo": "Desconhecido",
                            "descricao": str(e)
                        })
                    
                    # Adicionar tabela
                    metadados["tabelas"].append({
                        "nome": nome_tabela,
                        "conexao_id": f"conexao_{i+1}",
                        "colunas": colunas
                    })
                    
                    # Sugerir relações baseadas em nomes comuns de colunas
                    if i > 0 and len(colunas) > 0:
                        for tabela_anterior in metadados["tabelas"][:-1]:
                            for col_atual in colunas:
                                for col_anterior in tabela_anterior["colunas"]:
                                    # Procurar colunas com nomes idênticos ou que contenham '_id'
                                    if col_atual["nome"] == col_anterior["nome"] or ('_id' in col_atual["nome"] and col_atual["nome"] in col_anterior["nome"]):
                                        metadados["relacoes"].append({
                                            "from_tabela": tabela_anterior["nome"],
                                            "from_coluna": col_anterior["nome"],
                                            "to_tabela": nome_tabela,
                                            "to_coluna": col_atual["nome"],
                                            "cardinalidade": "1:N",
                                            "ativa": True,
                                            "tipo": "Single",
                                            "filtro_cruzado": "Both",
                                            "sugerida": True
                                        })
                else:
                    logger.warning(f"Arquivo não encontrado: {arquivo}")
            
            # Adicionar medidas recomendadas
            for metrica in self.metricas_padrao:
                metadados["medidas"].append({
                    "nome": metrica["nome"],
                    "descricao": metrica["descricao"],
                    "expressao": metrica["formula"],
                    "formato": metrica["formato"]
                })
            
            # Salvar metadados como JSON
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"{nome_modelo.replace(' ', '_').lower()}_metadata_{timestamp}.json"
            caminho_arquivo = os.path.join(self.output_path, nome_arquivo)
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(metadados, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Metadados do modelo gerados: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            logger.error(f"Erro ao gerar metadados do modelo: {str(e)}")
            raise RuntimeError(f"Erro ao gerar metadados do modelo: {str(e)}")
    
    def gerar_template_metricas(self, nome_template: str = "E-commerce Metrics") -> str:
        """
        Gera um template de métricas para uso no Power BI.
        
        Args:
            nome_template (str): Nome do template a ser gerado.
            
        Returns:
            str: Caminho para o arquivo de template gerado.
        """
        logger.info(f"Gerando template de métricas: {nome_template}")
        
        try:
            # Criar estrutura do template
            template = {
                "nome": nome_template,
                "versao": "1.0.0",
                "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "criado_por": os.getenv('USERNAME', 'vitordoliveira'),
                "categorias": [
                    "Financeiro",
                    "Operacional",
                    "Cliente",
                    "Produto",
                    "Marketing"
                ],
                "metricas": self.metricas_padrao
            }
            
            # Adicionar métricas específicas para cada categoria
            metricas_adicionais = [
                {
                    "nome": "Produtos Vendidos",
                    "descricao": "Total de produtos vendidos",
                    "formula": "SUM(Vendas[quantity])",
                    "formato": "Número Inteiro",
                    "categoria": "Produto"
                },
                {
                    "nome": "Custo Total",
                    "descricao": "Soma de todos os custos",
                    "formula": "SUM(Vendas[cost_value])",
                    "formato": "Moeda",
                    "categoria": "Financeiro"
                },
                {
                    "nome": "Margem Bruta",
                    "descricao": "Margem bruta de lucro",
                    "formula": "DIVIDE([Total de Vendas] - [Custo Total], [Total de Vendas], 0)",
                    "formato": "Percentual",
                    "categoria": "Financeiro"
                },
                {
                    "nome": "Clientes Novos",
                    "descricao": "Novos clientes no período",
                    "formula": """
                        VAR MinDataCliente = 
                        CALCULATETABLE(SUMMARIZE(Vendas, Vendas[customer_id], "MinData", MIN(Vendas[date])))
                        RETURN
                        COUNTROWS(FILTER(MinDataCliente, [MinData] >= MIN(Calendario[Data]) && [MinData] <= MAX(Calendario[Data])))
                    """,
                    "formato": "Número Inteiro",
                    "categoria": "Cliente"
                },
                {
                    "nome": "Taxa de Conversão",
                    "descricao": "Taxa de conversão de visitas em vendas",
                    "formula": "DIVIDE([Número de Transações], [Total de Visitas], 0)",
                    "formato": "Percentual",
                    "categoria": "Marketing"
                },
                {
                    "nome": "Valor por Visita",
                    "descricao": "Valor médio gerado por visita",
                    "formula": "DIVIDE([Total de Vendas], [Total de Visitas], 0)",
                    "formato": "Moeda",
                    "categoria": "Marketing"
                },
                {
                    "nome": "Top Categorias",
                    "descricao": "Ranking de categorias de produtos",
                    "formula": """
                        RANKX(
                            ALL(Produtos[categoria]),
                            CALCULATE([Total de Vendas]),
                            ,
                            DESC
                        )
                    """,
                    "formato": "Número Inteiro",
                    "categoria": "Produto"
                }
            ]
            
            # Adicionar ao template
            template["metricas"].extend(metricas_adicionais)
            
            # Salvar template como JSON
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"{nome_template.replace(' ', '_').lower()}_{timestamp}.json"
            caminho_arquivo = os.path.join(self.output_path, nome_arquivo)
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Template de métricas gerado: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            logger.error(f"Erro ao gerar template de métricas: {str(e)}")
            raise RuntimeError(f"Erro ao gerar template de métricas: {str(e)}")
    
    def gerar_script_medidas_dax(self, nome_script: str, caminho_template: Optional[str] = None) -> str:
        """
        Gera um script DAX com medidas para o Power BI.
        
        Args:
            nome_script (str): Nome do script a ser gerado.
            caminho_template (str, optional): Caminho para um template de métricas.
                                              Se None, usa as métricas padrão.
            
        Returns:
            str: Caminho para o arquivo de script gerado.
            
        Raises:
            FileNotFoundError: Se o caminho_template for fornecido mas não existir.
        """
        logger.info(f"Gerando script DAX: {nome_script}")
        
        try:
            # Determinar quais métricas usar
            metricas = self.metricas_padrao
            
            if caminho_template and os.path.exists(caminho_template):
                # Se um caminho para template foi fornecido, carregá-lo
                try:
                    with open(caminho_template, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        if "metricas" in template_data:
                            metricas = template_data["metricas"]
                            logger.info(f"Métricas carregadas do template: {caminho_template}")
                except Exception as e:
                    logger.warning(f"Erro ao ler template de métricas: {str(e)}. Usando métricas padrão.")
            elif caminho_template:
                logger.error(f"Template não encontrado: {caminho_template}")
                raise FileNotFoundError(f"Template não encontrado: {caminho_template}")
            
            # Gerar conteúdo do script
            linhas = [
                "// DAX Measures for Power BI",
                f"// Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"// Script Name: {nome_script}",
                f"// Author: {os.getenv('USERNAME', 'vitordoliveira')}",
                "",
                "// INSTRUCTIONS:",
                "// 1. Open Power BI Desktop",
                "// 2. Go to the Home tab and click 'Enter Data'",
                "// 3. Copy and paste each measure separately",
                "// 4. Or use the DAX Editor extension to import this file directly",
                "",
                "// =============================================================",
                "// MEASURES",
                "// =============================================================",
                ""
            ]
            
            # Adicionar cada métrica como medida DAX
            for metrica in metricas:
                linhas.append(f"// {metrica['nome']}")
                linhas.append(f"// Description: {metrica['descricao']}")
                linhas.append(f"// Category: {metrica.get('categoria', 'General')}")
                linhas.append(f"// Format: {metrica.get('formato', 'Auto')}")
                linhas.append("")
                
                # Formatar a expressão DAX adequadamente
                formula = metrica['formula'].strip()
                if "\n" in formula:
                    # Se for uma expressão multilinhas, preservar a formatação
                    formula_lines = formula.split("\n")
                    formula_formatted = "\n".join([line.strip() for line in formula_lines])
                    linhas.append(f"{metrica['nome']} = \n{formula_formatted}")
                else:
                    # Se for uma expressão de linha única
                    linhas.append(f"{metrica['nome']} = {formula}")
                
                # Adicionar linhas em branco entre as medidas
                linhas.append("")
                linhas.append("// -------------------------------------------------------------")
                linhas.append("")
            
            # Adicionar informações finais
            linhas.append("// =============================================================")
            linhas.append(f"// End of Script: {nome_script}")
            linhas.append("// =============================================================")
            
            # Salvar como arquivo de texto
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"{nome_script.replace(' ', '_').lower()}_{timestamp}.dax"
            caminho_arquivo = os.path.join(self.output_path, nome_arquivo)
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write('\n'.join(linhas))
            
            logger.info(f"Script DAX gerado: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                raise
            logger.error(f"Erro ao gerar script DAX: {str(e)}")
            raise RuntimeError(f"Erro ao gerar script DAX: {str(e)}")
    
    def gerar_documentacao_modelo(self, 
                                 nome_modelo: str, 
                                 metadados_path: Optional[str] = None,
                                 metricas_path: Optional[str] = None) -> str:
        """
        Gera documentação completa para um modelo do Power BI.
        
        Args:
            nome_modelo (str): Nome do modelo a ser documentado.
            metadados_path (str, optional): Caminho para arquivo de metadados.
            metricas_path (str, optional): Caminho para arquivo de métricas.
            
        Returns:
            str: Caminho para o arquivo de documentação gerado.
        """
        logger.info(f"Gerando documentação para modelo: {nome_modelo}")
        
        try:
            # Carregar metadados se fornecidos
            metadados = None
            if metadados_path and os.path.exists(metadados_path):
                try:
                    with open(metadados_path, 'r', encoding='utf-8') as f:
                        metadados = json.load(f)
                        logger.info(f"Metadados carregados de: {metadados_path}")
                except Exception as e:
                    logger.warning(f"Erro ao ler metadados: {str(e)}")
            
            # Carregar métricas se fornecidas
            metricas = self.metricas_padrao
            if metricas_path and os.path.exists(metricas_path):
                try:
                    with open(metricas_path, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        if "metricas" in template_data:
                            metricas = template_data["metricas"]
                            logger.info(f"Métricas carregadas de: {metricas_path}")
                except Exception as e:
                    logger.warning(f"Erro ao ler métricas: {str(e)}")
            
            # Gerar conteúdo da documentação em markdown
            linhas = [
                f"# Documentação do Modelo: {nome_modelo}",
                "",
                f"**Data de geração:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
                f"**Autor:** {os.getenv('USERNAME', 'vitordoliveira')}",
                "",
                "## Introdução",
                "",
                f"Esta documentação descreve o modelo de dados '{nome_modelo}' para análise de dados de e-commerce no Power BI.",
                "O modelo foi projetado para fornecer insights sobre vendas, clientes, produtos e métricas de desempenho.",
                "",
                "## Estrutura do Modelo de Dados",
                ""
            ]
            
            # Adicionar informações sobre as tabelas
            if metadados and "tabelas" in metadados:
                linhas.append("### Tabelas")
                linhas.append("")
                
                for tabela in metadados["tabelas"]:
                    linhas.append(f"#### {tabela['nome']}")
                    linhas.append("")
                    linhas.append("| Coluna | Tipo de Dado | Descrição |")
                    linhas.append("| ------ | ------------ | --------- |")
                    
                    for coluna in tabela["colunas"]:
                        descricao = coluna.get("descricao", "")
                        linhas.append(f"| {coluna['nome']} | {coluna['tipo']} | {descricao} |")
                    
                    linhas.append("")
            else:
                linhas.append("### Tabelas")
                linhas.append("")
                linhas.append("Informações detalhadas sobre tabelas não estão disponíveis.")
                linhas.append("")
            
            # Adicionar informações sobre relações
            if metadados and "relacoes" in metadados and metadados["relacoes"]:
                linhas.append("### Relações")
                linhas.append("")
                linhas.append("| Tabela de Origem | Coluna de Origem | Tabela de Destino | Coluna de Destino | Cardinalidade | Sugerida |")
                linhas.append("| ---------------- | ---------------- | ----------------- | ----------------- | ------------- | -------- |")
                
                for relacao in metadados["relacoes"]:
                    sugerida = "Sim" if relacao.get("sugerida", False) else "Não"
                    linhas.append(f"| {relacao['from_tabela']} | {relacao['from_coluna']} | {relacao['to_tabela']} | {relacao['to_coluna']} | {relacao['cardinalidade']} | {sugerida} |")
                
                linhas.append("")
            else:
                linhas.append("### Relações")
                linhas.append("")
                linhas.append("Não foram definidas relações para este modelo.")
                linhas.append("")
            
            # Adicionar informações sobre as medidas
            linhas.append("## Medidas DAX")
            linhas.append("")
            
            # Agrupar medidas por categoria
            categorias = {}
            for metrica in metricas:
                categoria = metrica.get("categoria", "Geral")
                if categoria not in categorias:
                    categorias[categoria] = []
                categorias[categoria].append(metrica)
            
            # Adicionar cada categoria e suas medidas
            for categoria, lista_metricas in categorias.items():
                linhas.append(f"### Categoria: {categoria}")
                linhas.append("")
                
                for metrica in lista_metricas:
                    linhas.append(f"#### {metrica['nome']}")
                    linhas.append("")
                    linhas.append(f"**Descrição:** {metrica['descricao']}  ")
                    linhas.append(f"**Formato:** {metrica.get('formato', 'Auto')}  ")
                    linhas.append("")
                    linhas.append("```dax")
                    linhas.append(metrica['formula'])
                    linhas.append("```")
                    linhas.append("")
            
            # Adicionar instruções de uso
            linhas.append("## Instruções de Uso")
            linhas.append("")
            linhas.append("1. Importe os dados nas tabelas correspondentes do modelo")
            linhas.append("2. Verifique e estabeleça as relações entre as tabelas conforme definido")
            linhas.append("3. Adicione as medidas DAX listadas acima ao modelo")
            linhas.append("4. Crie visualizações usando as tabelas e medidas definidas")
            linhas.append("")
            linhas.append("## Notas Adicionais")
            linhas.append("")
            linhas.append("Este modelo foi gerado automaticamente e pode necessitar de ajustes conforme os requisitos específicos do projeto.")
            linhas.append("Consulte a documentação do Power BI para obter ajuda adicional na implementação deste modelo.")
            
            # Salvar como arquivo markdown
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"{nome_modelo.replace(' ', '_').lower()}_documentation_{timestamp}.md"
            caminho_arquivo = os.path.join(self.output_path, nome_arquivo)
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write('\n'.join(linhas))
            
            logger.info(f"Documentação do modelo gerada: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            logger.error(f"Erro ao gerar documentação do modelo: {str(e)}")
            raise RuntimeError(f"Erro ao gerar documentação do modelo: {str(e)}")

# Se executado como script
if __name__ == "__main__":
    # Configuração de logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("POWER BI TEMPLATE GENERATOR - TESTE".center(60))
    print("=" * 60)
    print(f"Data e Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Usuário: {os.getenv('USERNAME', 'vitordoliveirase')}")
    print("-" * 60)
    
    # Demonstração rápida
    template = PowerBITemplate()
    
    # 1. Gerar template de métricas
    print("\n1. Gerando template de métricas...")
    metricas_path = template.gerar_template_metricas("E-commerce KPIs")
    print(f"Template de métricas gerado: {metricas_path}")
    
    # 2. Gerar script DAX
    print("\n2. Gerando script DAX...")
    dax_path = template.gerar_script_medidas_dax("E-commerce KPIs", metricas_path)
    print(f"Script DAX gerado: {dax_path}")
    
    # 3. Gerar metadados de modelo
    print("\n3. Gerando metadados de modelo...")
    metadados_path = template.gerar_metadata_modelo(
        "E-commerce Sales Model", 
        "Modelo para análise de vendas de e-commerce", 
        [metricas_path]  # Usamos o próprio arquivo de métricas como exemplo
    )
    print(f"Metadados gerados: {metadados_path}")
    
    # 4. Gerar documentação do modelo
    print("\n4. Gerando documentação do modelo...")
    docs_path = template.gerar_documentacao_modelo(
        "E-commerce Sales Model",
        metadados_path,
        metricas_path
    )
    print(f"Documentação gerada: {docs_path}")
    
    print("\nProcesso concluído com sucesso!")