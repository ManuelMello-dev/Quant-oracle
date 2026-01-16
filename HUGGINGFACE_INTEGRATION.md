# HuggingFace Integration for Quant Oracle

## Overview

The Quant Oracle now supports **local HuggingFace models** for AI-powered market analysis, eliminating the need for external API calls. This provides:

- **Zero API costs** - No per-request charges
- **Privacy** - All analysis happens locally
- **Offline capability** - Works without internet (after initial model download)
- **Customization** - Easy to swap models based on your needs

## Features

### 1. Automatic Model Selection

The system automatically chooses the best available model:

1. **HuggingFace models** (preferred) - Local, no API calls
2. **OpenAI API** (fallback) - If HuggingFace unavailable
3. **Rule-based analysis** (fallback) - If no models available

### 2. Supported Models

#### Recommended Models (Small & Efficient)

- **Qwen/Qwen2.5-3B-Instruct** (default) - 3B parameters, excellent performance
- **Qwen/Qwen3-0.6B** - Smallest, fastest, good for resource-constrained environments
- **Qwen/Qwen2.5-1.5B-Instruct** - Balanced size and capability

#### Alternative Models

- **meta-llama/Llama-3.1-8B-Instruct** - Larger, more capable
- **Qwen/Qwen2.5-7B-Instruct** - High-quality analysis

### 3. No Symbol Limit

The artificial 3-symbol limit has been removed. You can now analyze as many cryptocurrencies as you want:

```bash
# Analyze multiple symbols
python backend/oracle.py --symbols BTC/USD,ETH/USD,DOGE/USD,SOL/USD,XRP/USD,ADA/USD
```

## Installation

### 1. Install Dependencies

```bash
# Install transformers and torch
pip install transformers torch

# For GPU support (recommended)
pip install transformers torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. First Run (Model Download)

The first time you run the system, it will automatically download the model (~6GB for Qwen2.5-3B):

```bash
cd backend
python api/server.py
```

The model is cached locally and won't be downloaded again.

## Usage

### API Server

The API server automatically uses HuggingFace models:

```bash
cd backend
python api/server.py
```

### Direct Analysis

```python
from hf_llm_analyzer import HuggingFaceLLMAnalyzer
import pandas as pd

# Initialize analyzer
analyzer = HuggingFaceLLMAnalyzer("Qwen/Qwen2.5-3B-Instruct")

# Analyze data
analysis = analyzer.analyze_market_data(df, "BTC/USD")
print(analyzer.generate_report(analysis))
```

### API Endpoint

```bash
# Get AI-powered analysis
curl "http://localhost:8000/api/analyze?symbol=BTC/USD&use_llm=true"
```

## Configuration

### Change Model

Edit `backend/llm_analyzer.py`:

```python
# Use a different model
analyzer = LLMAnalyzer(model_name="Qwen/Qwen3-0.6B")

# Or use OpenAI instead
analyzer = LLMAnalyzer(model_name="gpt-4.1-mini", use_hf=False)
```

### Disable HuggingFace

If you want to use OpenAI API instead:

```python
analyzer = LLMAnalyzer(use_hf=False)
```

## Performance

### Model Sizes

| Model | Size | RAM Required | Speed | Quality |
|-------|------|--------------|-------|---------|
| Qwen3-0.6B | 1.2GB | 2GB | Very Fast | Good |
| Qwen2.5-1.5B | 3GB | 4GB | Fast | Very Good |
| Qwen2.5-3B | 6GB | 8GB | Medium | Excellent |
| Llama-3.1-8B | 16GB | 20GB | Slow | Outstanding |

### Hardware Recommendations

- **CPU only**: Qwen3-0.6B or Qwen2.5-1.5B
- **GPU (8GB VRAM)**: Qwen2.5-3B (recommended)
- **GPU (16GB+ VRAM)**: Llama-3.1-8B

## Deployment

### Railway

Add to `requirements.txt`:

```
transformers>=4.36.0
torch>=2.1.0
```

Set environment variable:

```bash
TRANSFORMERS_CACHE=/app/.cache/huggingface
```

### Docker

```dockerfile
FROM python:3.11

# Install dependencies
RUN pip install transformers torch

# Download model at build time (optional)
RUN python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; \
    AutoTokenizer.from_pretrained('Qwen/Qwen2.5-3B-Instruct'); \
    AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-3B-Instruct')"

# Copy application
COPY . /app
WORKDIR /app

CMD ["python", "backend/api/server.py"]
```

## Troubleshooting

### Out of Memory

Use a smaller model:

```python
analyzer = HuggingFaceLLMAnalyzer("Qwen/Qwen3-0.6B")
```

### Slow Generation

- Use GPU if available
- Reduce `max_new_tokens` in `hf_llm_analyzer.py`
- Use a smaller model

### Model Download Fails

```bash
# Set cache directory
export TRANSFORMERS_CACHE=/path/to/cache

# Download manually
python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; \
    AutoTokenizer.from_pretrained('Qwen/Qwen2.5-3B-Instruct'); \
    AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-3B-Instruct')"
```

## Comparison: HuggingFace vs OpenAI

| Feature | HuggingFace | OpenAI API |
|---------|-------------|------------|
| Cost | Free | $0.15-0.60 per 1M tokens |
| Privacy | 100% local | Data sent to OpenAI |
| Latency | 2-5s (GPU) | 1-3s |
| Quality | Very Good | Excellent |
| Offline | Yes | No |
| Setup | Complex | Simple |

## Migration from OpenAI

The system is backward compatible. If you're currently using OpenAI:

1. Install transformers: `pip install transformers torch`
2. Restart the server - it will automatically use HuggingFace
3. To force OpenAI: Set `use_hf=False` in `LLMAnalyzer`

## Future Enhancements

- [ ] Model quantization for smaller memory footprint
- [ ] Fine-tuned models for crypto-specific analysis
- [ ] Multi-model ensemble for higher accuracy
- [ ] Streaming responses for real-time analysis

## Support

For issues or questions:
- GitHub Issues: https://github.com/YOUR_USERNAME/quant-oracle/issues
- Documentation: See README.md

---

**Built with ❤️ for traders who value privacy and cost-efficiency**
