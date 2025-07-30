# INF0242-SmartAudience

SmartAudience é um bot do Telegram que gerencia audiências para a disciplina INF0242: Agentes Inteligentes e Sistemas Multi-Agentes da UFG.

## Funcionalidades

### Gerenciamento de Audiências
- Agendamento de audiências com validação de horários
- Verificação de conflitos de horários
- Sugestão automática de horários alternativos
- Listagem de agendamentos por período
- Consulta de agendamentos do dia
- Busca de agendamentos por número do processo

### Gestão de Participantes
- Cadastro de participantes com validação de CPF
- Controle de presença
- Identificação de participantes por tipo e código

### Documentação de Audiências
- Geração automática de termos de audiência em PDF
- Gestão de arquivos do processo
- Registro de impugnações
- Transcrição de audiências

## Tecnologias

- Python 3, uma linguagem de programação de alto nível e de propósito geral;
- Model Context Protocol (MCP), um protocolo que permite a criação e gerenciamento de contextos para modelos de IA;
- PyFPDF, uma biblioteca para geração de documentos PDF em Python;
- Python Telegram Bot, uma interface Python para a API do Telegram Bot;
- SQLite, um sistema de gerenciamento de banco de dados relacional leve e autocontido;
- Speech Recognition, uma biblioteca para reconhecimento de fala e conversão de áudio em texto.

# Integração

- Aljava, sistema de gerenciamento de mídias processuais da Justiça Federal no Rio Grande do Norte (JFRN);
- AVIS, sistema de agendamentos de audiências, vídeos e salas da JFRN.

## Diagrama Resumido do Projeto

```mermaid
flowchart TD
    %% Global entities
    Users["Telegram Users"]:::external
    TelegramAPI["Telegram Bot API"]:::external

    %% Bot Layer
    subgraph "SmartAudience Bot (Python 3.10, python-telegram-bot)" 
        direction TB
        Entry["main.py"]:::internal
        Handlers["Handlers Module"]:::internal
        Validator["Core Validation\n(utils/validator.py)"]:::util
        UUIDMod["UUID Utility\n(utils/uuid.py)"]:::util
        PDFGen["PDF Generator\n(PyFPDF)"]:::util
        Speech["Speech Recognition\n(speech_recognition)"]:::util
        MCPClient["MCP Client\n(Guardrails AI)"]:::internal
    end

    %% MCP Microservices
    subgraph "MCP Micro-services" 
        direction TB
        AljavaSvc["aljava_server\n(uvicorn + MCP, SQLite)"]:::mcp
        AvisSvc["avis_server\n(uvicorn + MCP, SQLite)"]:::mcp
        AudSvc["audiencia_server\n(uvicorn + MCP)"]:::mcp
    end

    %% Databases
    subgraph "SQLite Databases"
        direction TB
        AljavaDB["aljava.db"]:::db
        AvisDB["avis.db"]:::db
    end

    %% Static Storage & Dumps
    midias["Static Media Storage\n(midias/)"]:::util
    subgraph "DB Init Dumps"
        direction TB
        DumpAljava["aljava_dump.sql"]:::db
        DumpAvis["avis_dump.sql"]:::db
    end

    %% Connections
    Users -->|"messages"| TelegramAPI
    TelegramAPI -->|"webhook\nlong polling"| Entry

    Entry -->|"routes to"| Handlers

    Handlers -->|"validate data"| Validator
    Handlers -->|"generate uuid"| UUIDMod
    Handlers -->|"generate pdf"| PDFGen
    PDFGen -->|"store files"| midias
    Handlers -->|"send media"| TelegramAPI

    Handlers -->|"speech input"| Speech
    Speech -->|"text output"| Handlers

    Handlers -->|"AI suggestions"| MCPClient
    MCPClient -->|"RPC call"| AljavaSvc
    MCPClient -->|"RPC call"| AvisSvc
    MCPClient -->|"RPC call"| AudSvc

    AljavaSvc -->|"reads/writes"| AljavaDB
    AvisSvc -->|"reads/writes"| AvisDB

    DumpAljava -->|"init"| AljavaDB
    DumpAvis -->|"init"| AvisDB

    %% Click Events
    click Entry "https://github.com/anunciado/inf0242-smartaudience/blob/main/main.py"
    click Handlers "https://github.com/anunciado/inf0242-smartaudience/tree/main/handlers/"
    click Validator "https://github.com/anunciado/inf0242-smartaudience/blob/main/utils/validator.py"
    click UUIDMod "https://github.com/anunciado/inf0242-smartaudience/blob/main/utils/uuid.py"
    click PDFGen "https://github.com/anunciado/inf0242-smartaudience/blob/main/utils/pdf.py"
    click midias "https://github.com/anunciado/inf0242-smartaudience/tree/main/midias/"
    click DumpAljava "https://github.com/anunciado/inf0242-smartaudience/blob/main/dumps/aljava_dump.sql"
    click DumpAvis "https://github.com/anunciado/inf0242-smartaudience/blob/main/dumps/avis_dump.sql"
    click AljavaSvc "https://github.com/anunciado/inf0242-smartaudience/blob/main/servers/aljava_server.py"
    click AvisSvc "https://github.com/anunciado/inf0242-smartaudience/blob/main/servers/avis_server.py"
    click AudSvc "https://github.com/anunciado/inf0242-smartaudience/blob/main/servers/audiencia_server.py"
    click AljavaDB "https://github.com/anunciado/inf0242-smartaudience/blob/main/servers/aljava.db"
    click AvisDB "https://github.com/anunciado/inf0242-smartaudience/blob/main/servers/avis.db"

    %% Styles
    classDef external fill:#D0E6FF,stroke:#0288D1,color:#000
    classDef internal fill:#D0EFFF,stroke:#1565C0,color:#000
    classDef util fill:#E8F5E9,stroke:#43A047,color:#000
    classDef mcp fill:#FFF3E0,stroke:#FB8C00,color:#000
    classDef db fill:#ECEFF1,stroke:#78909C,color:#000
```

## Configuração do ambiente de desenvolvimento

1. Instale o python, na versão 3.10, através do [link](https://www.python.org/downloads/);
2. Clone este repositório https://github.com/anunciado/INF0242-SmartAudience.git em sua máquina local;
3. Abra o projeto em sua IDE de preferência, como sugestão utilize o Visual Studio Code ou PyCharm;
4. Crie um ambiente virtual com o comando:
```
. python -m venv venv
```
5. Ative o ambiente virtual com o comando:
* No windows:
```
venv\Scripts\activate
```
* No linux:
```
source venv/bin/activate
```
6. Instale as bibliotecas no seu ambiente virtual a partir do arquivo _requirements.txt_ com o comando:
```
pip install -r requirements.txt
```
7. Crie um arquivo _.env_ na raiz do projeto como no exemplo arquivo _.env.sample_ com os seguintes parâmetros, alterando o DRIVER_PATH, colocando o path pro driver e API_TOKEN, uma senha pessoa para acesso as rotas.
```
TELEGRAM_BOT_TOKEN=seutoken
```
9. Execute o projeto com o comando:
```
python main.py
```
10. Instale o Claude Desktop através do [link oficial](https://claude.ai/desktop)
11. você deve editar um arquivo de configuração localizado em:
```
code $env:AppData\Roaming\Claude\claude_desktop_config.json
```
12. Uma vez com o arquivo aberto, adicione a seguinte configuração JSON, certificando-se de ajustar o caminho para refletir a localização correta do servidor MCP:
```
{
    "mcpServers": {
        "aljava_server": {
            "command": "uv",
            "args": [
                "--directory",
                "C://INF0242-SmartAudience//servers",
                "run",
                "aljava_server.py"
            ]
        },
        "avis_server": {
            "command": "uv",
            "args": [
                "--directory",
                "C://INF0242-SmartAudience//servers",
                "run",
                "avis_server.py"
            ]
        },
        "audiencia_server": {
            "command": "uv",
            "args": [
                "--directory",
                "C://INF0242-SmartAudience//servers",
                "run",
                "audiencia_server.py"
            ]
        }
    }
}
```
13. Inicie o o Claude Desktop instalado.

## Contribuição:

1. `Mova` a issue a ser resolvida para a coluna _In Progress_ no [board do projeto].  
2. `Clone` este repositório https://github.com/anunciado/INF0242-SmartAudience.git.
3. `Crie` um branch a partir da branch _dev_.
4. `Commit` suas alterações.
5. `Realize` o push das alterações.