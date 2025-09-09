# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Azure Functions project written in Python that processes JSON payloads with an `items` array structure. It sums all `VALOR_TOTAL_ITEM` values from the items and adds the result as a `total_suma` field to the response.

## Development Commands

### Local Development
- `func start` - Run the Azure Function locally for testing and debugging
- Activate virtual environment: `source .venv/bin/activate` (use `.venv\Scripts\activate` on Windows)
- Install dependencies: `pip install -r requirements.txt`

### Azure Functions Core Tools
The project requires Azure Functions Core Tools v4:
```bash
brew tap azure/functions
brew install azure-functions-core-tools@4
```

### Deployment
- `func azure functionapp publish capability-glg` - Deploy to Azure Function App

## Architecture

### Core Function (function_app.py)
- Single HTTP trigger endpoint at `/api/http_trigger`
- Anonymous authentication level
- Validates JSON payloads with an `items` array structure
- Sums all `VALOR_TOTAL_ITEM` values from each item
- Adds `total_suma` field with the calculated sum to the response
- Provides error responses for invalid JSON or missing `items` array

### Key Files
- `function_app.py` - Main application entry point with HTTP trigger
- `host.json` - Azure Functions host configuration with Application Insights
- `requirements.txt` - Python dependencies (azure-functions only)
- `Pipfile` - Pipenv configuration for Python 3.11
- `test/payload-testglg-*.json` - Sample JSON payload files for testing the function
- `test/response-testglg-*.json` - Expected response files showing total_suma calculations
- `azurelocations.json` - Azure locations data (likely reference data)

### Python Environment
- Target runtime: Python 3.11
- Uses azure-functions SDK
- Virtual environment in `.venv/` directory

## Testing
- Local testing via `func start` on localhost
- Test with sample data: `curl -X POST http://localhost:7071/api/http_trigger -H "Content-Type: application/json" -d @test/"payload-testglg-SKM_451i25082810511-2 copy.json"`
- Production endpoint: https://capability-glg.azurewebsites.net/api/http_trigger
- VSCode debugging supported via `.vscode/launch.json`

## Azure Configuration
- Resource Group: AzureFunctionsQuickstart-rg
- Storage Account: capabilityzeta
- Function App: capability-glg
- Region: eastus (with westeurope consumption plan)