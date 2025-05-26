az login

[2] *  Microsoft Azure Sponsorship  5f11f4d0-5a98-4781-b993-3325488ef8e0  rpamaker.com

## Create the Group
az group create --name AzureFunctionsQuickstart-rg --location eastus

## Create storage
az storage account create --name capabilityzeta --location eastus --resource-group AzureFunctionsQuickstart-rg --sku Standard_LRS

az functionapp create --resource-group AzureFunctionsQuickstart-rg --consumption-plan-location westeurope --runtime python --runtime-version 3.11 --functions-version 4 --name capability-zeta --os-type linux --storage-account capabilityzeta

func azure functionapp publish capability-zeta
