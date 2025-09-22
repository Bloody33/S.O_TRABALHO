# Simulador de Processos - Task Manager

Este projeto é um simulador de processos que imita o funcionamento de um gerenciador de tarefas, permitindo criar processos fictícios que consomem CPU, memória e threads. Ele também exibe informações do sistema em tempo real, como uso de CPU, memória, disco e rede.

## Funcionalidades
- Criar processos simulados com:
  - Nome
  - Memória (MB)
  - Quantidade de threads
  - Consumo de CPU opcional
  - Prioridade (Baixa, Média, Alta)
- Pausar, retomar e encerrar processos manualmente.
- Exibição em tempo real de:
  - CPU (%)
  - Memória (%)
  - Disco (%)
  - Rede (upload/download)
- Visualização da configuração do PC (sistema, processador, memória, disco etc.).

## Requisitos
- Python 3.8+
- Dependências listadas em `requirements.txt`

Instale as dependências com:
```bash
pip install -r requirements.txt
```

### Principais dependências
- PySide6
- psutil

## Execução
No terminal, execute:
```bash
python simulador.py
```

A interface gráfica será aberta com o Dashboard de Processos.

## Estrutura do Projeto
```
simulador.py      # Código principal do simulador
README.md         # Documentação do projeto
diagrama.md       # Código Mermaid com o diagrama UML simplificado
requirements.txt  # Dependências do projeto
```

## Observações
- Cada processo criado é um multiprocessing.Process, que internamente roda threads simuladas.
- A simulação não executa programas reais, apenas consome recursos de forma controlada.
- O código pode ser expandido para simular escalonadores, políticas de prioridade etc.

MAURICIO GUILHERME DA SILVA - 113586
GUSTAVO DE PAULA OLIVEIRA - 114044
MATHEUS ULRICH PONTES - 113367
