# Como Rodar o CHRONOS-SAFE

Este guia mostra o passo a passo para instalar e executar o projeto localmente.

## 1. Entrar na pasta do projeto

Abra o terminal na raiz do projeto:

```powershell
cd C:\Users\0100cit9207\Downloads\Chronos-simulator\chronos_safe
```

## 2. Criar um ambiente virtual

Recomendado usar Python `3.11` ou `3.12`.

No Windows:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

Se você só tiver Python `3.13`, o projeto ainda pode rodar parcialmente, mas a stack científica completa pode exigir ajustes extras.

## 3. Atualizar o `pip`

```powershell
python -m pip install --upgrade pip
```

## 4. Instalar dependências

Instalação mínima:

```powershell
python -m pip install -e .
```

Instalação para treino:

```powershell
python -m pip install -e ".[ml,dev]"
```

Instalação completa:

```powershell
python -m pip install -e ".[ml,science,dev]"
```

## 5. Rodar os testes

```powershell
python -m pytest -q
```

Se tudo estiver correto, a suíte deve passar.

## 6. Gerar dataset generalista

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

## 7. Gerar dataset especialista

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

## 8. Treinar o modelo generalista

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

## 9. Fazer fine-tuning especialista

```powershell
python -m chronos_safe.apps.cli.main train-specialist `
  --dataset-dir data/processed/specialist `
  --output-dir models/checkpoints/specialist `
  --base-checkpoint models/checkpoints/generalist/model.pt `
  --epochs 10 `
  --batch-size 16
```

## 10. Rodar uma simulação híbrida

Sem modelo treinado, o sistema ainda roda usando o integrador rápido com fallback físico quando necessário.

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

## 11. Rodar a validação Apophis

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

Relatórios gerados:

- `reports/validation/apophis_validation.json`
- `reports/validation/apophis_validation_summary.txt`

## 12. Subir a API

Forma mais simples, com interface visual:

```powershell
python run.py
```

Isso sobe o servidor e abre a dashboard web no navegador.

Endereco padrao:

```text
http://127.0.0.1:8000/
```

Se quiser subir sem abrir o navegador:

```powershell
$env:CHRONOS_OPEN_BROWSER="false"
python run.py
```

Forma manual, sem `run.py`:

```powershell
uvicorn chronos_safe.apps.api.main:app --reload
```

Testar healthcheck:

```powershell
curl http://127.0.0.1:8000/health
```

Testar simulação:

```powershell
curl -X POST http://127.0.0.1:8000/simulate `
  -H "Content-Type: application/json" `
  -d "{\"fixture_name\":\"apophis/apophis_fixture.json\",\"steps\":30,\"dt_days\":1.0}"
```

## 13. Usar a interface web

Ao abrir `http://127.0.0.1:8000/`, voce tera uma dashboard com:

- geracao de dataset generalista;
- geracao de dataset especialista;
- treino generalista;
- treino especialista;
- simulacao hibrida;
- validacao Apophis;
- catalogo automatico de fixtures, checkpoints, scalers e relatorios.

O painel final mostra o JSON de resposta de cada operacao.

## 14. Se o comando `chronos` estiver disponível

Depois da instalação editável, você também pode usar:

```powershell
chronos generate-generalist ...
chronos generate-specialist ...
chronos train-generalist ...
chronos train-specialist ...
chronos simulate ...
chronos validate-apophis ...
```

## 15. Problemas comuns

### `torch` não instala no Windows

Se aparecer erro de caminho longo, habilite Windows Long Paths ou use um ambiente com caminho curto.

### `rebound` não está instalado

O projeto continua funcionando com o backend de referência em NumPy, mas o baseline oficial com `IAS15` só fica disponível quando `REBOUND` estiver instalado.

### `chronos` não foi reconhecido

Use o entrypoint direto:

```powershell
python -m chronos_safe.apps.cli.main <comando>
```

### `pip install` falhou com `Fatal error in launcher`

Isso acontece quando o `pip.exe` do Windows aponta para um Python antigo que não existe mais.

Use sempre:

```powershell
python -m pip install -e ".[ml,science,dev]"
```

Em vez de:

```powershell
pip install -e .[ml,science,dev]
```
