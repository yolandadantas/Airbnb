# Instruções

Nesta etapa do pipeline realizamos testes determinísticos e não-determinísticos sobre nosso dado processado, para checar se ele cumpre os requisitos esperados antes de iniciarmos a modelagem.

## Run 

```bash
mlflow run . -P reference_artifact="week_08_data_segregation/train_data.csv:latest" \
             -P sample_artifact="week_08_data_segregation/test_data.csv:latest" \
             -P ks_alpha=0.05 \
```
