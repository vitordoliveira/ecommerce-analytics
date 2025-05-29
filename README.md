# E-commerce Analytics

![E-commerce Analytics](https://img.shields.io/badge/Python-E--commerce%20Analytics-blue)
![Power BI](https://img.shields.io/badge/Integration-Power%20BI-yellow)
![Data Analysis](https://img.shields.io/badge/Data-Analysis-green)

Um sistema completo de análise de dados para e-commerce com integração ao Power BI, desenvolvido em Python.

## 📋 Visão Geral

Este projeto oferece uma solução completa para processamento, análise e visualização de dados de e-commerce. Com uma interface CLI amigável e colorida, o sistema permite:

- Importação e processamento de dados de e-commerce
- Geração de dados sintéticos para testes e demonstrações
- Análises automatizadas por período, categoria e região
- Integração completa com Microsoft Power BI
- Exportação de dashboards, modelos e relatórios personalizados
- Ferramentas auxiliares como temas personalizados e tabelas de calendário

## 🚀 Funcionalidades

### Processamento de Dados
- Importação de arquivos CSV ou geração de dados sintéticos
- Limpeza e transformação de dados
- Análises automáticas por diferentes dimensões
- Exportação dos dados processados

### Integração com Power BI
- Geração de dashboards prontos para uso
- Criação de tabelas auxiliares (calendário)
- Exportação de modelos completos
- Temas personalizados para visualizações
- Relatórios completos com documentação

### Interface de Usuário
- CLI com interface colorida e intuitiva
- Barras de progresso para operações longas
- Seleção interativa de arquivos e opções
- Configurações personalizáveis

## 📦 Estrutura do Projeto

```
ecommerce-analytics/
├── data/
│   ├── processed/    # Dados processados
│   └── raw/          # Dados brutos
├── exports/
│   ├── powerbi/      # Exportações para Power BI
│   ├── notebooks/    # Jupyter notebooks
│   └── reports/      # Relatórios gerados
├── src/
│   ├── controllers/  # Controladores de lógica
│   ├── models/       # Modelos de dados
│   └── views/        # Interfaces e exportadores
├── tests/            # Testes automatizados
├── main.py           # Script principal
├── configure.py      # Script de configuração
└── requirements.txt  # Dependências
```

## 🔧 Requisitos

- Python 3.8+
- Bibliotecas Python (instaláveis via `pip install -r requirements.txt`):
  - pandas
  - numpy
  - matplotlib
  - pyyaml
  - pytest (para testes)
  - jupyter (para notebooks)

## 🛠️ Instalação e Uso

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/vitordoliveira/ecommerce-analytics.git
   cd ecommerce-analytics
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Uso

Execute o script principal:
```bash
python main.py
```

#### Opções de linha de comando:
```bash
python main.py --file ARQUIVO_CSV  # Especificar arquivo de entrada
python main.py --action process    # Executar processamento direto
python main.py --no-color          # Desativar cores no terminal
python main.py --debug             # Habilitar logs de depuração
```

### Menu Principal

Ao executar o script, você terá acesso ao menu principal:

1. **Processar dados e realizar análises** - Importa/gera dados e executa análises
2. **Gerar dashboard do Power BI** - Cria um dashboard pronto para uso
3. **Exportar modelo completo para Power BI** - Gera um modelo completo
4. **Criar tabela de calendário para Power BI** - Tabela auxiliar para análises temporais
5. **Gerar tema personalizado para Power BI** - Cria um tema com cores personalizadas
6. **Exportar relatório completo** - Gera um relatório com dados e documentação
7. **Configurações** - Personaliza configurações do sistema
8. **Ajuda e documentação** - Exibe guia de ajuda

## 📊 Exemplo de Uso

### Processamento Básico

1. Execute `python main.py`
2. Selecione a opção 1 (Processar dados e realizar análises)
3. Escolha um arquivo CSV existente ou gere dados sintéticos
4. Visualize as análises geradas e os arquivos exportados

### Criação de Dashboard

1. Execute `python main.py`
2. Selecione a opção 2 (Gerar dashboard do Power BI)
3. Selecione os arquivos de dados a serem incluídos
4. Dê um nome ao dashboard
5. Importe o arquivo gerado no Power BI Desktop

## 🔍 Funcionalidades Detalhadas

### Análises Disponíveis

- **Análise por Período**: Vendas e métricas agrupadas por dia, semana, mês e ano
- **Análise por Categoria**: Desempenho de vendas por categoria e subcategoria de produtos
- **Análise Regional**: Distribuição geográfica das vendas e clientes

### Personalização do Power BI

- **Temas Personalizados**: Conjunto de cores e estilos alinhados com sua marca
- **Tabela de Calendário**: Dimensão temporal completa para análises avançadas
- **Modelos Pré-configurados**: Dashboards prontos para uso com medidas DAX

## 🧪 Testes

Execute os testes automatizados:
```bash
python run_tests.py
```

## 📈 Próximos Passos

- [ ] Implementar análise de cohort e LTV (Lifetime Value)
- [ ] Adicionar previsões com modelos de machine learning
- [ ] Interface web para visualização sem Power BI
- [ ] Suporte a outros formatos de dados (Excel, JSON, API)
- [ ] Integração com fontes de dados em tempo real

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## 👤 Autor

**Vitor Oliveira**
- GitHub: [vitordoliveira](https://github.com/vitordoliveira)

---

📧 Para mais informações, entre em contato.
