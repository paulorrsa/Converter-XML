# Conversor XML para DANFE e Excel

Aplicação web desenvolvida em Flask para converter arquivos XML de notas fiscais eletrônicas (NFe) em DANFE (PDF) e relatórios em Excel.

## Funcionalidades

- Conversão de XML para DANFE (PDF)
- Geração de relatórios em Excel a partir de XMLs
- Visualização de informações das notas fiscais
- Download individual ou em lote dos PDFs gerados

## Requisitos

- Python 3.7 ou superior
- Flask e outras dependências listadas no arquivo `requirements.txt`

## Instalação Local

1. Clone este repositório:

```bash
git clone https://github.com/paulorrsa/conversor-xml.git
cd conversor-xml
```

2. Crie e ative um ambiente virtual:

```bash
# Criação
python -m venv venv

# Ativação (Windows)
venv\Scripts\activate

# Ativação (Linux/Mac)
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Execute a aplicação:

```bash
python app.py
```

5. Acesse a aplicação em `http://localhost:5000`

## Implantação em Produção

A aplicação está configurada para ser facilmente implantada em serviços como Heroku, Render, Railway ou PythonAnywhere:

### Heroku

```bash
heroku create nome-do-app
git push heroku main
```

### Render/Railway

Basta conectar o repositório GitHub e configurar:

- Runtime: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

## API do DANFE

A aplicação utiliza a API do MeuDanfe para geração dos PDFs. O serviço é chamado pela função `gerar_danfe_api` em `danfe_api.py`.

## Estrutura do Projeto

- `app.py`: Arquivo principal com as rotas e lógica da aplicação
- `danfe_api.py`: Funções para interação com a API de geração de DANFE
- `app/templates/`: Templates HTML
- `app/static/`: Arquivos estáticos (CSS, JS, imagens)
- `app/uploads/`: Pasta para arquivos temporários

## Tecnologias Utilizadas

- Flask: Framework web
- Pandas: Processamento de dados para relatórios
- XlsxWriter: Geração de planilhas Excel
- ElementTree: Processamento de XML
- Bootstrap: Framework CSS para interface

## Contribuições

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request
