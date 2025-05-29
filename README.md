# E-commerce Analytics

![E-commerce Analytics](https://img.shields.io/badge/E--commerce-Analytics-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen)
![Polars](https://img.shields.io/badge/Polars-Data%20Processing-orange)
![Power BI](https://img.shields.io/badge/Power%20BI-Integration-yellow)

A comprehensive solution for e-commerce data analysis, with advanced data processing capabilities, in-depth analytics, and Microsoft Power BI integration.

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Detailed Usage Guide](#-detailed-usage-guide)
- [Power BI Integration](#-power-bi-integration)
- [Code Examples](#-code-examples)
- [Testing and Development](#-testing-and-development)
- [Author](#-author)
- [License](#-license)

## 🔍 Overview

E-commerce Analytics is a Python application designed to process, analyze, and visualize e-commerce sales data. The system allows users to import their own data or generate synthetic datasets for testing and demonstration purposes.

The tool performs detailed analyses by time periods, product categories, and geographic regions, exporting results in formats optimized for Microsoft Power BI, including pre-configured dashboards, custom themes, and auxiliary tables such as calendars.

## ✨ Key Features

- **Data Processing**:
  - Loading, cleaning, and transforming sales data
  - Synthetic data generation for demonstration and testing
  - Support for CSV and Parquet formats
  - High-performance data processing with Polars

- **Advanced Analytics**:
  - Sales analysis by period (day, week, month, quarter)
  - Sales by product category and subcategory
  - Geographic distribution of sales
  - Performance metrics (average ticket, growth rates, etc.)

- **Power BI Integration**:
  - Complete dashboard generation
  - Optimized data models
  - Custom themes
  - Calendar tables for time-based analysis
  - Metric templates with DAX formulas
  - Automatic model documentation

- **Visualizations and Reports**:
  - Data visualization generation
  - Comprehensive reports in markdown
  - Metrics and analysis documentation
  - Interactive visualizations

- **User-Friendly Interface**:
  - Colored and intuitive command-line interface
  - Interactive menus for all functionalities
  - Progress bars for long operations
  - Batch operations support via command arguments

## 🛠️ Requirements

- Python 3.8 or higher
- Core libraries:
  - polars: high-performance data processing
  - pandas: data manipulation
  - matplotlib and seaborn: data visualization
  - plotly: interactive visualizations
  - PyYAML: configuration file handling
- Microsoft Power BI Desktop (optional, for opening generated dashboards)

## 📥 Installation

### Method 1: Automatic Setup

1. Clone the repository:
```bash
git clone https://github.com/vitordoliveira/ecommerce-analytics.git
cd ecommerce-analytics
```
2. Run the configuration script:
```bash
python configure.py
```
The script will check requirements, install dependencies, and set up the environment.

### Method 2: Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/vitordoliveira/ecommerce-analytics.git
cd ecommerce-analytics
```
2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Create necessary directories:
```bash
mkdir -p data/raw data/processed exports/powerbi logs
```

## 🚀 Usage

### Interactive Interface

To start the program's interactive interface:

```bash
python main.py
```
This will open a menu with the following options:

1. Process data and perform analyses  
2. Generate Power BI dashboard  
3. Export complete model to Power BI  
4. Create calendar table for Power BI  
5. Generate custom theme for Power BI  
6. Export comprehensive report  
7. Settings  
8. Help and documentation  

### Command Line

You can also run specific actions via command line:

```bash
# Process data
python main.py --action process --file data/raw/sales.csv

# Generate dashboard
python main.py --action dashboard

# Export complete model
python main.py --action model

# Create calendar table
python main.py --action calendar

# Generate custom theme
python main.py --action theme

# Export comprehensive report
python main.py --action report

# Disable terminal colors
python main.py --no-color

# Enable debug logs
python main.py --debug
```

## 📂 Project Structure

```
ecommerce-analytics/
├── data/                   # Raw and processed data
│   ├── processed/          # Data after processing
│   └── raw/                # Original raw data
├── exports/                # Exported results
│   ├── powerbi/            # Files for Power BI
│   │   ├── dashboard/      # Dashboard templates
│   │   ├── templates/      # Templates and themes
│   │   └── teste_dashboard/# Test dashboard
│   ├── notebooks/          # Notebooks with examples
│   │   └── exemplo_analise_ecommerce.ipynb  # Example notebook
│   └── reports/            # Generated reports
│       └── figures/        # Visualizations for reports
│           └── sales_viz_time_trend_20250528_120636.html  # Example visualization
├── logs/                   # Log files
├── src/                    # Source code
│   ├── controllers/        # Controllers (MVC)
│   │   ├── analise_controller.py
│   │   └── powerbi_controller.py
│   ├── models/             # Data models (MVC)
│   │   ├── ecommerce_model.py
│   │   └── obter_dados_ecommerce.py
│   └── views/              # Views (MVC)
│       ├── powerbi_dashboard.py
│       ├── powerbi_exporter.py
│       └── powerbi_template.py
├── tests/                  # Unit tests
│   ├── __init__.py
│   ├── test_analise_controller.py
│   ├── test_obter_dados_ecommerce.py
│   └── test_powerbi_controller.py
├── venv/                   # Python virtual environment (not included in repository)
├── .env                    # Environment variables (created by configure.py)
├── .gitignore
├── cleanup.py              # Script to clean temporary files
├── configure.py            # Environment configuration script
├── main.py                 # Main script
├── README.md
├── requirements.txt        # Project dependencies
└── run_tests.py            # Test runner
```

## 📖 Detailed Usage Guide

1. **Data Processing**  
   The system can process e-commerce sales data in two ways:

   a) **Importing existing data**:
   - Load CSV files with sales data
   - The system will clean and transform the data
   - Metrics such as total sales value will be calculated

   b) **Generating synthetic data**:
   - If no data is available, the system can generate synthetic data
   - You can specify the number of records to generate
   - Synthetic data includes transactions with products, customers, dates, and values

2. **Automated Analyses**  
   After processing, the system performs automated analyses:

   - **Analysis by Period**:
     - Sales by day, week, month, and quarter
     - Temporal trends
     - Month-over-month growth

   - **Analysis by Category**:
     - Performance by product category
     - Sales distribution across categories
     - Ranking of best-selling products

   - **Analysis by Region**:
     - Geographic distribution of sales
     - Performance by state/region
     - Mapping of high-performance regions

3. **Power BI Integration**  
   The system offers several options for Power BI integration:

   - **Dashboard Generation**:
     - Creates a ready-to-use dashboard template
     - Includes custom themes
     - Generates dashboard documentation

   - **Complete Model Export**:
     - Creates an optimized data model
     - Includes dimensional and fact tables
     - Generates DAX scripts for common metrics

   - **Calendar Table**:
     - Creates a date table for temporal analysis
     - Includes dimensions such as day of week, month, quarter
     - Facilitates the creation of time filters in Power BI

   - **Custom Themes**:
     - Creates visual themes for Power BI
     - Customization of colors and styles
     - Visual consistency for your brand

4. **Report Export**  
   The system can generate comprehensive reports:

   - Reports in markdown format
   - Inclusion of generated visualizations
   - Detailed documentation of analyses
   - Data-driven recommendations

## 🔌 Power BI Integration

### Importing Data into Power BI

1. Open Power BI Desktop  
2. Click on "Get Data" > "Text/CSV"  
3. Navigate to the `/exports/powerbi/` folder and select the generated files  
4. Import the necessary tables  

### Applying Custom Themes

1. In Power BI, go to "View" > "Themes" > "Browse for themes"  
2. Select the JSON theme file generated by the system  
3. The theme will be applied to your report  

### Using Calendar Tables

1. Import the generated calendar table  
2. Establish relationships with your fact tables:  
   - Relate the "Date" column from the calendar table  
   - With date columns in your fact tables  

### Applying DAX Metrics

1. Open the DAX file generated by the system  
2. In Power BI, go to the "Data" view  
3. Create a "New Measure" for each DAX formula  
4. Copy and paste the formulas from the generated file  

## 💻 Code Examples

### Basic Data Processing
```python
from src.controllers.analise_controller import AnaliseController

# Initialize controller
analysis = AnaliseController()

# Process sales data (existing file)
result = analysis.processar_dados_vendas("data/raw/sales.csv")

# Access processed DataFrame
df = result['dados_processados']
print(f"Processed records: {df.shape[0]}")
```

### Power BI Dashboard Generation
```python
from src.controllers.powerbi_controller import PowerBIController
from src.controllers.analise_controller import AnaliseController

# Initialize controllers
analysis = AnaliseController()
powerbi = PowerBIController()

# Process data
result = analysis.processar_dados_vendas("data/raw/sales.csv")
df = result['dados_processados']

# Perform analyses
period_analyses = analysis.analisar_vendas_por_periodo(df)
category_analysis = analysis.analisar_vendas_por_categoria(df)

# Combine analyses
analyses = {
    'periodo': period_analyses,
    'categoria': category_analysis
}

# Generate Power BI dashboard
dashboard = powerbi.gerar_apenas_dashboard(
    [path for _, path in result['arquivos_gerados']],
    "E-commerce Sales"
)
```

### Custom Analysis
```python
import polars as pl
from src.controllers.analise_controller import AnaliseController

# Initialize controller
analysis = AnaliseController()

# Load data
df = pl.read_csv("data/processed/processed_sales.csv")

# Custom analysis: Top 5 products by revenue
top_products = df.group_by("product_id").agg([
    pl.sum("total_value").alias("total_revenue")
]).sort("total_revenue", descending=True).head(5)

print(top_products)
```

## 🧪 Testing and Development

### Running Tests

To run unit tests:

```bash
python run_tests.py
```

Or using pytest directly:

```bash
pytest tests/
```

### Creating New Tests

1. Create a new test file in `/tests/`  
2. Follow the naming pattern: `test_component_name.py`  
3. Implement tests using the pytest framework  

### Project Cleanup

To clean temporary files and caches:

```bash
python cleanup.py
```

## 👨‍💻 Author

Vitor Oliveira - [GitHub](https://github.com/vitordoliveira)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
