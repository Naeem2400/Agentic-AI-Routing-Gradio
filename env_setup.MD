# Agentic AI Environment Setup

This folder is configured for the Agentic AI course environment.

## Files

- `requirements.txt`: packages from the tutorial, plus Jupyter notebook support.
- `requirements_versions.txt`: same package list, kept as a place to pin exact versions later.
- `.env`: API key placeholders.
- `venv/`: local Python virtual environment.

## Activate Environment

```bash
source venv/bin/activate
```

## Install Requirements

```bash
pip install -r requirements.txt
```

## Register Jupyter Kernel

```bash
python -m ipykernel install --user --name agentic-ai --display-name "Python (Agentic AI)"
```

## Start Jupyter Notebook

```bash
jupyter notebook
```
