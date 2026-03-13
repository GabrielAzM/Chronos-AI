# Como Rodar o CHRONOS-SAFE

Este guia mostra o passo a passo para instalar e executar o projeto localmente.

Se voce nao quer estudar fisica orbital nem treinar modelos agora, siga apenas a secao `Rota rapida para avaliacao`.

Todos os comandos de instalacao abaixo assumem que voce esta dentro da pasta:

```text
C:\Users\0100cit9207\Downloads\Chronos-simulator\chronos_safe
```

Se voce estiver um nivel acima, em:

```text
C:\Users\0100cit9207\Downloads\Chronos-simulator
```

entre primeiro na pasta correta:

```powershell
cd chronos_safe
```

## 1. Entrar na pasta do projeto

Abra o terminal na raiz do projeto:

```powershell
cd C:\Users\0100cit9207\Downloads\Chronos-simulator\chronos_safe
```

## Rota rapida para avaliacao

Esse e o caminho mais curto para alguem que so quer entender o sistema.

1. Instale o projeto:

```powershell
python -m pip install -e ".[ml,science,dev]"
```

2. Rode a interface:

```powershell
python run.py
```

3. Abra no navegador:

```text
http://127.0.0.1:8000/
```

4. Dentro da interface, use somente isto:

- `1. Ver demo 3D`
- `2. Rodar teste Apophis`

5. Leia o painel `Relatorio guiado`.

Se o objetivo for deploy no Render, leia tambem [docs/render_deploy.md](/c:/Users/0100cit9207/Downloads/Chronos-simulator/chronos_safe/docs/render_deploy.md).

## 2. Criar um ambiente virtual

Recomendado usar Python `3.11` ou `3.12`.

No Windows:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

Se voce so tiver Python `3.13`, o projeto ainda pode rodar parcialmente, mas a stack cientifica completa pode exigir ajustes extras.

## 3. Atualizar o pip

```powershell
python -m pip install --upgrade pip
```

## 4. Instalar dependencias

Instalacao minima:

```powershell
python -m pip install -e .
```

Instalacao para treino:

```powershell
python -m pip install -e ".[ml,dev]"
```

Instalacao recomendada no Windows:

```powershell
python -m pip install -e ".[ml,science,dev]"
```

Isso instala a interface web, treino, dados e ferramentas de desenvolvimento.

## 5. Instalar REBOUND separadamente

`REBOUND` ficou separado de `science` porque em muitos ambientes Windows ele exige compilacao C/C++.

Tente assim:

```powershell
python -m pip install -r requirements-rebound.txt
```

Se funcionar, o projeto passa a usar `REBOUND IAS15` automaticamente.

Se falhar com erro como:

```text
Microsoft Visual C++ 14.0 or greater is required
```

voce pode continuar sem `rebound`. O projeto ainda roda com o backend de referencia em NumPy.

## 6. Rodar os testes

```powershell
python -m pytest -q
```

## 7. Gerar dataset generalista

```powershell
python -m chronos_safe.apps.cli.main generate-generalist `
  --output-dir data/processed/generalist `
  --num-samples 128 `
  --min-bodies 2 `
  --max-bodies 6 `
  --dt-days 1.0
```

Arquivos gerados:

- `data/processed/generalist/dataset.npz`
- `data/processed/generalist/manifest.json`
- `data/processed/generalist/scaler.json`

## 8. Gerar dataset especialista

```powershell
python -m chronos_safe.apps.cli.main generate-specialist `
  --output-dir data/processed/specialist `
  --fixture-name apophis/apophis_fixture.json `
  --num-samples 64 `
  --dt-days 1.0
```

Arquivos gerados:

- `data/processed/specialist/dataset.npz`
- `data/processed/specialist/manifest.json`
- `data/processed/specialist/scaler.json`

## 9. Treinar o modelo generalista

```powershell
python -m chronos_safe.apps.cli.main train-generalist `
  --dataset-dir data/processed/generalist `
  --output-dir models/checkpoints/generalist `
  --epochs 20 `
  --batch-size 16
```

Arquivos esperados:

- `models/checkpoints/generalist/model.pt`
- `models/checkpoints/generalist/ood_guard.json`
- `models/checkpoints/generalist/scaler.json`
- `models/checkpoints/generalist/training_manifest.json`

## 10. Fazer fine-tuning especialista

```powershell
python -m chronos_safe.apps.cli.main train-specialist `
  --dataset-dir data/processed/specialist `
  --output-dir models/checkpoints/specialist `
  --base-checkpoint models/checkpoints/generalist/model.pt `
  --epochs 10 `
  --batch-size 16
```

## 11. Rodar uma simulacao hibrida

Sem modelo treinado:

```powershell
python -m chronos_safe.apps.cli.main simulate `
  --fixture-name apophis/apophis_fixture.json `
  --steps 30 `
  --dt-days 1.0 `
  --output-path reports/validation/simulation.json
```

Com modelo treinado:

```powershell
python -m chronos_safe.apps.cli.main simulate `
  --fixture-name apophis/apophis_fixture.json `
  --steps 30 `
  --dt-days 1.0 `
  --checkpoint-path models/checkpoints/specialist/model.pt `
  --scaler-path models/checkpoints/specialist/scaler.json `
  --ood-guard-path models/checkpoints/specialist/ood_guard.json `
  --output-path reports/validation/simulation.json
```

## 12. Rodar a validacao Apophis

```powershell
python -m chronos_safe.apps.cli.main validate-apophis `
  --steps 180 `
  --dt-days 1.0
```

Com modelo treinado:

```powershell
python -m chronos_safe.apps.cli.main validate-apophis `
  --steps 180 `
  --dt-days 1.0 `
  --checkpoint-path models/checkpoints/specialist/model.pt `
  --scaler-path models/checkpoints/specialist/scaler.json `
  --ood-guard-path models/checkpoints/specialist/ood_guard.json
```

Relatorios gerados:

- `reports/validation/apophis_validation.json`
- `reports/validation/apophis_validation_summary.txt`

## 13. Subir a interface web

Forma mais simples:

```powershell
python run.py
```

Endereco padrao:

```text
http://127.0.0.1:8000/
```

Se voce estiver na pasta externa `Chronos-simulator`, tambem pode usar:

```powershell
python run.py
```

Nesse caso, o launcher externo encaminha automaticamente para `chronos_safe\run.py`.

Se quiser subir sem abrir o navegador:

```powershell
$env:CHRONOS_OPEN_BROWSER="false"
python run.py
```

Forma manual:

```powershell
uvicorn chronos_safe.apps.api.main:app --reload
```

## 14. Usar a interface web

Ao abrir `http://127.0.0.1:8000/`, voce tera uma dashboard com:

- visualizacao 3D de orbitas no navegador;
- modo avaliacao rapida com demo 3D e teste Apophis em um clique;
- secao avancada recolhida para geracao de datasets, treino e simulacao manual;
- validacao Apophis com leitura guiada das metricas;
- catalogo automatico de fixtures, checkpoints, scalers e relatorios.

### O que o avaliador deve fazer

Se a pessoa estiver avaliando a plataforma e nao a pesquisa inteira:

1. abrir a pagina;
2. clicar em `1. Ver demo 3D`;
3. clicar em `2. Rodar teste Apophis`;
4. ler o `Relatorio guiado`.

### O que o caso Apophis mostra

O teste Apophis existe para mostrar, de forma concreta, quatro coisas:

- se a simulacao hibrida acompanha a referencia fisica;
- quanto erro acumulado aparece ao longo do rollout;
- se houve drift fisico relevante;
- se o sistema precisou acionar fallback.

## 15. Problemas comuns

### `torch` nao instala no Windows

Se aparecer erro de caminho longo, habilite Windows Long Paths ou use um caminho curto para o ambiente virtual.

### `rebound` nao instala no Windows

Se falhar por compilador C++, continue sem ele por enquanto. O sistema usa o backend NumPy de referencia.

### `chronos` nao foi reconhecido

Use o entrypoint direto:

```powershell
python -m chronos_safe.apps.cli.main <comando>
```

### `pip install` falhou com `Fatal error in launcher`

Use sempre:

```powershell
python -m pip install -e ".[ml,science,dev]"
```

em vez de:

```powershell
pip install -e ".[ml,science,dev]"
```
