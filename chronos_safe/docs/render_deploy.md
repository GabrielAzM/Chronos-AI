# Deploy no Render

Este projeto foi preparado para ficar simples de avaliar no Render.

## Objetivo

Subir o CHRONOS-SAFE como uma aplicacao web unica, sem build frontend separado.

## O que ja esta pronto

O repositorio possui:

- [render.yaml](/c:/Users/0100cit9207/Downloads/Chronos-simulator/render.yaml)

Ele configura:

- `rootDir: chronos_safe`
- instalacao com `python -m pip install -e .`
- servidor com `uvicorn`
- `healthCheckPath: /health`
- navegador desativado em producao
- modo CPU
- `REBOUND` desativado por padrao no deploy web

Esse perfil de deploy foi otimizado para:

- subir mais rapido;
- falhar menos no build;
- entregar a demo 3D e a validacao Apophis sem depender de `torch` ou `rebound`;
- manter a interface compreensivel para avaliacao.

## Antes de subir

Checklist rapido:

1. confirme que o repositorio esta atualizado no GitHub;
2. confirme que o arquivo [render.yaml](/c:/Users/0100cit9207/Downloads/Chronos-simulator/render.yaml) esta no diretorio raiz do repositorio;
3. se quiser favicon, coloque `chronosfav.png` em `chronos_safe/chronos_safe/apps/api/static/`;
4. confirme que a interface local abre com `python run.py`.

## Passo a passo no Render

### Opcao recomendada: Blueprint via `render.yaml`

1. Suba o repositorio no GitHub.
2. Entre em `https://render.com/`.
3. Clique em `New +`.
4. Clique em `Blueprint`.
5. Conecte sua conta do GitHub ao Render, se ainda nao estiver conectada.
6. Selecione o repositorio `Chronos-simulator`.
7. O Render vai detectar o arquivo `render.yaml`.
8. Confirme a criacao do servico.
9. Aguarde o build e o primeiro deploy.
10. Abra a URL publica gerada pelo Render.

### Opcao manual: criar Web Service sem Blueprint

Se quiser configurar manualmente no painel:

1. Clique em `New +`.
2. Clique em `Web Service`.
3. Selecione o repositorio.
4. Preencha:

- `Name`: `chronos-safe`
- `Root Directory`: `chronos_safe`
- `Runtime`: `Python 3`
- `Build Command`: `python -m pip install -e .`
- `Start Command`: `python -m uvicorn chronos_safe.apps.api.main:app --host 0.0.0.0 --port $PORT`

5. Adicione estas variaveis de ambiente:

- `CHRONOS_OPEN_BROWSER=false`
- `CHRONOS_DEVICE=cpu`
- `CHRONOS_USE_REBOUND_IF_AVAILABLE=false`
- `CHRONOS_LOG_LEVEL=INFO`

6. Defina o `Health Check Path` como:

```text
/health
```

7. Crie o servico e aguarde o deploy.

## O que o avaliador deve fazer ao abrir

1. Clicar em `1. Ver demo 3D`.
2. Observar a orbita 3D.
3. Clicar em `2. Rodar teste Apophis`.
4. Ler o painel `Relatorio guiado`.

## Por que isso funciona bem para avaliacao

O deploy foi pensado para uma pessoa leiga conseguir usar sem treinamento previo.

Na pratica, a interface deixa escondido o modo avancado e destaca apenas:

- a visualizacao 3D;
- o caso Apophis;
- o resumo interpretado das metricas.

Assim, o avaliador entende rapidamente:

- o que esta sendo simulado;
- qual e o caso de validacao mais importante;
- como o sistema compara o modo hibrido com a referencia fisica.

## O que fica disponivel no deploy web

No perfil padrao do Render, o foco e demonstracao e validacao.

Fica pronto para uso:

- interface web;
- visualizacao 3D;
- validacao Apophis;
- simulacao com fallback;
- relatorio guiado.

Pode ficar indisponivel ou limitado no deploy web padrao:

- treino de modelos;
- carregamento de checkpoints PyTorch;
- uso de `REBOUND` compilado no servidor.

Isso e intencional. O deploy publico foi otimizado para avaliacao, nao para treino pesado.

## Persistencia de arquivos no Render

Por padrao, trate o filesystem do Web Service como temporario.

Isso significa que arquivos gerados em runtime, como:

- relatorios;
- datasets;
- checkpoints;
- caches;

podem nao sobreviver a novo deploy, restart ou troca de instancia.

Para demonstracao publica, isso nao e um problema.
Para uso persistente, o recomendado e:

- anexar um disco persistente, se seu plano suportar;
- ou armazenar artefatos fora do servico web.

## Como validar se o deploy deu certo

Assim que o Render subir a aplicacao:

1. abra `/health` e confirme que a resposta esta `ok`;
2. abra `/`;
3. clique em `1. Ver demo 3D`;
4. confirme que o grafico 3D aparece;
5. clique em `2. Rodar teste Apophis`;
6. confirme que o `Relatorio guiado` aparece com metricas e semaforo.

## Quando fizer uma nova versao

Fluxo recomendado:

1. commit local;
2. push para o GitHub;
3. aguardar auto deploy do Render;
4. abrir a URL publica;
5. validar `demo 3D + Apophis`.

## Observacao sobre REBOUND

O deploy padrao nao depende de `rebound` para funcionar.

Se o ambiente conseguir instalar `rebound`, o sistema usa o baseline fisico oficial automaticamente.

Se nao conseguir, o backend continua operando com o motor de referencia em NumPy, o que permite demonstracao e avaliacao funcional.
