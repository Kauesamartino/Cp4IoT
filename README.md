# Cp4IoT – API de Previsão de Patologias da Coluna Vertebral

API REST construída com Flask que expõe um modelo de **Random Forest** treinado para classificar patologias da coluna vertebral em três classes:

- **Normal**
- **Disk Hernia**
- **Spondylolisthesis**

## Estrutura do Repositório

```
Cp4IoT/
├── questao_01.csv          # Dataset original
├── train.py                # Script de treinamento do modelo
├── requirements.txt        # Dependências para treino e inferência
└── deploy_ml/
    ├── modelo.pkl          # Modelo treinado (Random Forest + LabelEncoder)
    ├── inference.py        # API Flask para inferência via HTTP
    ├── requirements.txt    # Dependências Python
    └── Dockerfile          # Imagem Docker para deploy
```

## Pré-requisitos

- Python 3.11+
- pip

## Treinamento do Modelo

```bash
pip install -r requirements.txt
python train.py
```

O modelo é salvo automaticamente em `deploy_ml/modelo.pkl`.

## Execução Local da API

```bash
cd deploy_ml
pip install -r requirements.txt
python inference.py
```

A API ficará disponível em `http://localhost:5000`.

### Endpoints

| Método | Rota       | Descrição                          |
|--------|------------|------------------------------------|
| GET    | `/health`  | Verifica se a API está no ar       |
| POST   | `/predict` | Realiza previsão com base nas features |

### Exemplo de Requisição

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"V1": 63.03, "V2": 22.55, "V3": 39.61, "V4": 40.48, "V5": 98.67, "V6": -0.25}'
```

### Exemplo de Resposta

```json
{
  "prediction": "Disk Hernia",
  "probabilities": {
    "Disk Hernia": 0.72,
    "Normal": 0.18,
    "Spondylolisthesis": 0.10
  }
}
```

## Execução com Docker

```bash
cd deploy_ml
docker build -t cp4iot-api .
docker run -p 5000:5000 cp4iot-api
```

## Deploy na Nuvem – Azure App Service (Container)

### Pré-requisitos

- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Docker](https://docs.docker.com/get-docker/)
- Conta Azure com acesso ao Azure Container Registry (ACR)

### Passo a Passo

```bash
# 1. Login na Azure
az login

# 2. Criar grupo de recursos
az group create --name cp4iot-rg --location brazilsouth

# 3. Criar Azure Container Registry
az acr create --resource-group cp4iot-rg --name cp4iotregistry --sku Basic --admin-enabled true

# 4. Fazer login no ACR
az acr login --name cp4iotregistry

# 5. Build e push da imagem
cd deploy_ml
docker build -t cp4iotregistry.azurecr.io/cp4iot-api:latest .
docker push cp4iotregistry.azurecr.io/cp4iot-api:latest

# 6. Criar App Service Plan
az appservice plan create \
  --name cp4iot-plan \
  --resource-group cp4iot-rg \
  --sku B1 \
  --is-linux

# 7. Criar Web App com o container
az webapp create \
  --resource-group cp4iot-rg \
  --plan cp4iot-plan \
  --name cp4iot-api \
  --deployment-container-image-name cp4iotregistry.azurecr.io/cp4iot-api:latest

# 8. Configurar credenciais do ACR na Web App
ACR_PASSWORD=$(az acr credential show --name cp4iotregistry --query "passwords[0].value" -o tsv)
az webapp config container set \
  --name cp4iot-api \
  --resource-group cp4iot-rg \
  --docker-custom-image-name cp4iotregistry.azurecr.io/cp4iot-api:latest \
  --docker-registry-server-url https://cp4iotregistry.azurecr.io \
  --docker-registry-server-user cp4iotregistry \
  --docker-registry-server-password "$ACR_PASSWORD"
```

Após o deploy, a API estará disponível em:

```
https://cp4iot-api.azurewebsites.net
```

Teste rápido:

```bash
curl https://cp4iot-api.azurewebsites.net/health
# {"status":"ok"}

curl -X POST https://cp4iot-api.azurewebsites.net/predict \
  -H "Content-Type: application/json" \
  -d '{"V1": 63.03, "V2": 22.55, "V3": 39.61, "V4": 40.48, "V5": 98.67, "V6": -0.25}'
```
