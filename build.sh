#!/bin/bash

# Instalar setuptools primeiro (necessário para distutils)
pip install setuptools>=65.5.0

# Instalar dependências comuns
pip install -r requirements.txt

# Instalar dependências específicas para o Vercel
pip install -r requirements-vercel.txt

# Garantir que o requests seja instalado
pip install requests==2.28.2

# Verificar se o módulo requests foi instalado
pip show requests 