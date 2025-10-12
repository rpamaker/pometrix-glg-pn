# To Deploy the app for the first time:

az login

[2] *  Microsoft Azure Sponsorship  5f11f4d0-5a98-4781-b993-3325488ef8e0  rpamaker.com

<!-- ## Create the Group -->
<!-- az group create --name AzureFunctionsQuickstart-rg --location eastus -->

## Create storage
az storage account create --name capabilityglg --location eastus --resource-group AzureFunctionsQuickstart-rg --sku Standard_LRS

az functionapp create --resource-group AzureFunctionsQuickstart-rg --consumption-plan-location westeurope --runtime python --runtime-version 3.11 --functions-version 4 --name capability-glg --os-type linux --storage-account capabilityglg

func azure functionapp publish capability-glg

## Result:
Invoke url: https://capability-glg.azurewebsites.net/api/http_trigger
Formulario splitter: https://capability-glg.azurewebsites.net/api/pdfsplitter


# Agrego webform con pdf splitter

## Claude prompt:
create a new end point /pdfsplitter
It should respond a webpage. When I go in the browser to https://capability-glg.azurewebsites.net/api/pdfsplitter it should render a webpage. The web page will be just a webform. 
A button to upload a file.
The webform fields will be 
- desde pagina.
- hasta pagina.
Then an "SPLIT" button.
The button will be "disable" until a file is selected to upload and the fields have some value.

(file upload selection validation: the file should be a pdf)

When the SPLIT button it hit it should generate a pdf with the split of the original pdf from page (desde pagina) to page (hasta pagina), and it should download the splitter pdf.

Try to mantain the pront end as vallina as possible (html, javascript, jquery). You can propose front end libraries if needed, no problem, but try to avoid getting complex. Also the project structure make it as simple as possible.

