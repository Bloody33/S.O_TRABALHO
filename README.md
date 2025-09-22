# 🖥️ Simulador de Processos - Task Manager

Este projeto é um **simulador de gerenciamento de processos** com interface gráfica baseada em **Qt (PySide6)**.  
Ele permite criar processos que consomem memória e CPU, gerenciar múltiplos threads, monitorar consumo de recursos em tempo real (CPU, memória, disco e rede) e visualizar informações detalhadas do sistema.

---

## 🚀 Funcionalidades

- 📌 **Criação de processos simulados** com:
  - Nome personalizado
  - Definição de uso de memória (MB)
  - Quantidade de threads
  - Consumo de CPU (opcional)
  - Prioridade (Baixa, Média, Alta)

- ⏸️ **Gerenciamento dos processos:**
  - Pausar e retomar execução
  - Encerrar processo a qualquer momento
  - Visualização de threads associadas

- 📊 **Dashboard em tempo real:**
  - Uso da CPU (%)
  - Consumo de memória (%)
  - Utilização de disco (%)
  - Tráfego de rede (upload/download em KB/s)

- 🖥️ **Configuração do PC:**
  - Exibe informações detalhadas do hardware:
    - Sistema operacional e versão
    - Processador e núcleos físicos/lógicos
    - Frequência da CPU
    - Memória total e disponível
    - Disco total e utilizado

---

## 📦 Tecnologias Utilizadas

- [Python 3.x](https://www.python.org/)
- [PySide6](https://doc.qt.io/qtforpython/) → Interface gráfica
- [psutil](https://pypi.org/project/psutil/) → Monitoramento do sistema
- [multiprocessing / threading] → Criação e controle de processos simulados
- [platform] → Identificação do sistema operacional

---

## ⚙️ Instalação

Clone este repositório e instale as dependências:

```bash
git clone https://github.com/seuusuario/simulador-processos.git
cd simulador-processos

pip install -r requirements.txt
```

### 📄 Exemplo de `requirements.txt`:
```
PySide6
psutil
```

---

## ▶️ Como Executar

```bash
python simulador.py
```

A janela principal será aberta exibindo o **Dashboard de Processos**.

---

## 📖 Uso

1. Abra o programa (`python simulador.py`).
2. Defina os parâmetros do processo:
   - Nome do processo
   - Quantidade de memória (MB)
   - Número de threads
   - Se deve consumir CPU
   - Nível de prioridade
3. Clique em **Adicionar Processo**.
4. Acompanhe os processos em tempo real:
   - Pausar/Retomar
   - Encerrar
   - Visualizar uso de memória e threads
5. Clique em **Configuração do PC** para detalhes do sistema.

---

## 📷 Demonstração (prints sugeridos)

- Tela principal do Dashboard
- Exemplo de processos rodando
- Janela de Configuração do PC

---

## 🛠️ Melhorias Futuras

- Implementar agendamento de processos
- Simulação de deadlocks e escalonamento
- Exportar logs de processos para arquivo
- Suporte a múltiplas janelas de monitoramento

---

## 📜 Licença

Este projeto é distribuído sob a licença MIT.  
Sinta-se livre para usar, modificar e contribuir. 🚀
