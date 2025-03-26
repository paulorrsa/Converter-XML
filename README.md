# FSist Website Clone

Este é um clone do site da FSist, implementado usando Flask, um framework web Python.

## Requisitos

- Python 3.7 ou superior
- Flask e outras dependências listadas no arquivo `requirements.txt`

## Instalação

1. Clone este repositório:

```
git clone <url-do-repositorio>
```

2. Navegue até a pasta do projeto:

```
cd fsist-clone
```

3. Crie um ambiente virtual (opcional, mas recomendado):

```
python -m venv venv
```

4. Ative o ambiente virtual:

   - No Windows:

   ```
   venv\Scripts\activate
   ```

   - No macOS/Linux:

   ```
   source venv/bin/activate
   ```

5. Instale as dependências:

```
pip install -r requirements.txt
```

## Executando a aplicação

1. Para iniciar o servidor de desenvolvimento:

```
python app.py
```

2. Acesse o site no navegador:

```
http://localhost:5000
```

## Estrutura do Projeto

- `app.py`: Arquivo principal da aplicação Flask
- `app/templates/`: Contém todos os templates HTML
- `app/static/`: Arquivos estáticos (CSS, JavaScript, imagens)
  - `app/static/css/`: Arquivos CSS
  - `app/static/js/`: Arquivos JavaScript
  - `app/static/images/`: Imagens do site

## Páginas Implementadas

- **Home**: Página inicial com visão geral dos serviços
- **Sobre**: Informações sobre a empresa, história e equipe
- **Serviços**: Detalhes sobre os serviços oferecidos
- **Portfólio**: Casos de sucesso e projetos realizados
- **Preços**: Planos e valores dos serviços
- **Contato**: Formulário de contato e informações de contato

## Personalização

Para personalizar o site, você pode:

1. Modificar os arquivos HTML em `app/templates/`
2. Ajustar os estilos em `app/static/css/style.css`
3. Adicionar suas próprias imagens em `app/static/images/`

## Importante

Este site é apenas para fins educacionais e demonstração. Antes de usar em produção, certifique-se de:

1. Configurar corretamente a chave secreta da aplicação
2. Implementar o envio real de e-mails no formulário de contato
3. Configurar corretamente o tratamento de erros
4. Adicionar medidas de segurança adicionais

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
