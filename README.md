# PDF Catalog Analyzer

A comprehensive tool for extracting structured data from PDF catalogs using AI-powered text extraction and computer vision techniques.

## Features

- **Intelligent Text Extraction**: Automatically detects text-rich vs image-based pages
- **AI-Powered Data Extraction**: Uses OpenAI GPT-4 and Google Gemini for structured data extraction
- **Computer Vision Support**: Handles scanned documents and complex layouts
- **Memory-Safe Processing**: Prevents system crashes with large documents
- **Automotive Specialization**: Specialized prompts for automotive parts catalogs

## Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

### API Keys

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### Usage Levels

1. **Simple Text Extraction**: `02_simple_pdf_analyzer.ipynb` - Basic PDF text extraction
2. **AI-Powered Analysis**: `01_pdf_catalog_analyzer.ipynb` - Full AI extraction with vision
3. **Production Agent**: `03_professional_pdf_analyzer.ipynb` - Enterprise AI agent architecture

Place your PDF files in the `pdfs/` directory and run the notebooks.

## Project Structure

```
pdf-catalog-analyzer/
├── notebooks/
│   ├── 01_pdf_catalog_analyzer.ipynb    # Comprehensive AI-powered analyzer
│   ├── 02_simple_pdf_analyzer.ipynb     # Basic text extraction
│   └── 03_professional_pdf_analyzer.ipynb # Production AI agent architecture
├── pdfs/                                 # Input PDF files
├── output/                              # CSV and Excel exports
├── extracted_data/                      # JSON data and analysis
├── temp/                               # Temporary image files
├── requirements.txt
└── README.md
```

## Approach

### 1. Intelligent Page Analysis
- Automatically classifies pages as product data vs introductory content
- Recommends optimal extraction strategy per page
- Focuses processing on relevant content

### 2. Hybrid Extraction Strategy
- **Text Extraction**: Fast processing for text-based pages
- **Vision Extraction**: AI analysis of page images for complex layouts
- **Multi-Engine OCR**: Advanced OCR engines for scanned content

### 3. Memory Safety
- On-demand model loading to prevent memory exhaustion
- Configurable page limits for large documents
- Automatic cleanup of temporary resources

## Technical Details

### AI Models Supported
- **OpenAI GPT-4**: High-quality text and vision analysis
- **Google Gemini**: Fast, cost-effective processing
- **Advanced OCR**: TrOCR, PaddleOCR, EasyOCR support

### Output Formats
- Structured JSON data
- CSV files for analysis
- Excel spreadsheets
- Quality control reports

## Use Cases

- **Automotive Parts Catalogs**: Specialized extraction for vehicle compatibility data
- **Industrial Catalogs**: Technical specifications and part numbers
- **Product Catalogs**: General merchandise with pricing and descriptions

## Safety Features

The system includes memory monitoring and safe processing modes to prevent kernel panics and system crashes when processing large documents.

## License

This project is a proof of concept demonstration of modern document AI techniques.