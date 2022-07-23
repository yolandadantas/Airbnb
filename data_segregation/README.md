# Instruções

Nessa etapa realizaremos a divisão do nosso banco em treinamento e teste. Com a execução do comando abaixo, teremos 30% dos nossos dados separados para teste e o restante para treinamento. Note a importância de manter a nomenclatura escolhida para os artefatos, uma vez que, ao longo do pipeline, um artefato anterior é chamado para a criação do artefato que será utilizado na etapa seguinte.

## Run 

```bash
mlflow run . -P input_artifact="week_08_preprocessing/preprocessed_data.csv:latest" \
             -P artifact_root="data" \
             -P artifact_type="trainvaltest_data" \
             -P test_size=0.3 \
             -P stratify="price" \
             -P random_state="13"
```
