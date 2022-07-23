# Instruções
Nesse passo vamos criar o componente do MLflow que faz a limpeza inicial dos dados e gera o artefato de dados pré-processados. 
It implements in a reusable way the steps we implemented in the EDA notebook.

## Run 

```bash
mlflow run . -P input_artifact="week_08_eda/raw_data.csv:latest" \
             -P artifact_name="preprocessed_data.csv" \
             -P artifact_type="clean_data" \
             -P artifact_description="Data after preprocessing"\
             -P project_name="week_08_preprocessing"
```