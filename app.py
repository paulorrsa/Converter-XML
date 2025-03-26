from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length
from datetime import datetime
import os
import random
import xml.etree.ElementTree as ET
from werkzeug.utils import secure_filename
from io import BytesIO
import zipfile
import requests
import base64
import tempfile
import sys
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['SECRET_KEY'] = 'fsist-secret-key'

# Função para verificar se estamos no ambiente Vercel
def is_vercel_env():
    return 'VERCEL' in os.environ

# Define a pasta de upload baseada no ambiente (Vercel ou local)
if is_vercel_env():
    app.config['UPLOAD_FOLDER'] = '/tmp'
else:
    app.config['UPLOAD_FOLDER'] = 'app/uploads'

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Context processors
@app.context_processor
def inject_now():
    return {'now': datetime.now}

# Formulário para consulta de chaves
class ChaveForm(FlaskForm):
    tipo_documento = RadioField('Tipo de Documento', choices=[('NFe', 'NFe'), ('CTe', 'CTe')], default='NFe')
    chave_acesso = StringField('Chave de Acesso', validators=[DataRequired(), Length(min=44, max=44, message="A chave deve conter exatamente 44 dígitos.")])
    captcha = StringField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Consultar')

@app.route('/')
def index():
    return redirect(url_for('converter_xml_para_danfe'))

@app.route('/consultar', methods=['POST'])
def consultar():
    form = ChaveForm()
    if form.validate_on_submit():
        chave = form.chave_acesso.data
        tipo = form.tipo_documento.data
        
        # Simulando processamento da consulta
        # Normalmente aqui consultaria a SEFAZ usando certificado digital
        
        # Adicionar à lista de chaves recentes
        nova_chave = {
            "id": len(chaves_recentes) + 1,
            "chave": chave,
            "tipo": tipo,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "status": "Baixado"
        }
        chaves_recentes.insert(0, nova_chave)
        
        # Redirecionar para a página de resultado
        return redirect(url_for('resultado', chave=chave))
    
    # Se houver erros de validação, voltar para a página inicial
    return render_template('index.html', form=form)

@app.route('/resultado/<chave>')
def resultado(chave):
    # Simular dados do documento baseado na chave
    documento = {
        "chave": chave,
        "tipo": "NFe" if chave.startswith("35") else "CTe",
        "emissao": "10/10/2023",
        "valor": "1.250,75",
        "emitente": {
            "cnpj": "11.111.111/0001-11",
            "razao_social": "EMPRESA DEMONSTRAÇÃO LTDA",
            "endereco": "Rua Exemplo, 123 - São Paulo/SP"
        }
    }
    
    return render_template('resultado.html', documento=documento)

@app.route('/xml_para_pdf', methods=['GET', 'POST'])
def xml_para_pdf():
    if request.method == 'POST':
        # Verificar se o arquivo foi enviado
        if 'xml_file' not in request.files:
            flash('Nenhum arquivo enviado', 'danger')
            return redirect(request.url)
        
        xml_file = request.files['xml_file']
        
        # Se o usuário não selecionou um arquivo
        if xml_file.filename == '':
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
        
        # Se há um arquivo e é permitido
        if xml_file and xml_file.filename.endswith('.xml'):
            # Simular processamento do arquivo
            flash('Arquivo XML convertido com sucesso!', 'success')
            
            # Redirecionamento com mensagem de sucesso
            return redirect(url_for('xml_para_pdf'))
    
    return render_template('xml_para_pdf.html')

@app.route('/download_xml/<chave>')
def download_xml(chave):
    # Esta rota simularia o download do XML
    # Em uma implementação real, geraria o arquivo XML e o enviaria como resposta
    flash('XML baixado com sucesso!', 'success')
    return redirect(url_for('resultado', chave=chave))

@app.route('/gerar_danfe/<chave>')
def gerar_danfe(chave):
    # Esta rota simularia a geração do DANFE
    # Em uma implementação real, geraria o PDF e o enviaria como resposta
    flash('DANFE gerado com sucesso!', 'success')
    return redirect(url_for('resultado', chave=chave))

@app.route('/gerar-relatorio-com-xmls', methods=['GET', 'POST'])
def gerar_relatorio():
    xml_data = None
    incluir_itens = False
    
    # Se for uma requisição POST, processar os arquivos enviados
    if request.method == 'POST':
        if 'xml_files' not in request.files:
            flash('Nenhum arquivo enviado', 'danger')
            return redirect(request.url)
        
        xml_files = request.files.getlist('xml_files')
        incluir_itens = request.form.get('incluir_itens') == 'on'
        
        if not xml_files or xml_files[0].filename == '':
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
        
        # Lista para armazenar os dados de todas as notas
        todas_notas = []
        
        # Processar cada arquivo XML
        for xml_file in xml_files:
            if xml_file and xml_file.filename.endswith('.xml'):
                # Salvar o arquivo temporariamente
                filename = secure_filename(xml_file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                xml_file.save(filepath)
                
                # Processar o arquivo XML
                nota_data = processar_xml(filepath)
                if nota_data:
                    todas_notas.append(nota_data)
                
                # Remover o arquivo temporário
                os.remove(filepath)
        
        if todas_notas:
            # Armazenar os dados na sessão para download posterior
            session['notas_processadas'] = todas_notas
            xml_data = todas_notas
            flash('XMLs processados com sucesso!', 'success')
        else:
            flash('Nenhum arquivo XML válido foi processado', 'danger')
            return redirect(request.url)
    
    return render_template('gerar_relatorio.html', xml_data=xml_data, incluir_itens=incluir_itens)

@app.route('/download-relatorio')
def download_relatorio():
    formato = request.args.get('formato', 'excel')
    incluir_itens = request.args.get('incluir_itens', 'false').lower() == 'true'
    
    # Recuperar dados da sessão
    notas = session.get('notas_processadas')
    if not notas:
        flash('Nenhum dado disponível para download. Por favor, processe os XMLs novamente.', 'warning')
        return redirect(url_for('gerar_relatorio'))
    
    # Gerar arquivo Excel ou CSV
    if formato == 'excel':
        return gerar_excel(notas, incluir_itens)
    else:
        return gerar_csv(notas, incluir_itens)

def gerar_excel(notas, incluir_itens):
    """Gera um arquivo Excel com os dados das notas"""
    # Criar DataFrames para as notas e itens - definir aqui para estar acessível no bloco try/except
    dados_notas = []
    dados_itens = []
    
    # Preencher os dados das notas e itens antes de qualquer processamento
    for nota in notas:
        # Dados da nota
        dados_notas.append({
            'Tipo': nota['tipo'],
            'Chave': nota['chave'],
            'Número': nota['numero'],
            'Série': nota['serie'],
            'Data Emissão': nota['data_emissao'],
            'Emitente': nota['emitente']['razao_social'],
            'CNPJ Emitente': nota['emitente']['cnpj_cpf'],
            'Destinatário': nota['destinatario']['razao_social'],
            'CNPJ Destinatário': nota['destinatario']['cnpj_cpf'],
            'Valor Total': nota['valor_total'],
            'Forma Pagamento': nota['pagamento']['forma'],
            'Frete': nota['frete']
        })
        
        # Dados dos itens (se solicitado)
        if incluir_itens:
            for item in nota['itens']:
                dados_itens.append({
                    'Tipo Nota': nota['tipo'],
                    'Chave Nota': nota['chave'],
                    'Número Nota': f"{nota['numero']}/{nota['serie']}",
                    'Número Item': item['numero'],
                    'Código': item['codigo'],
                    'Descrição': item['descricao'],
                    'Valor Total': item['valor_total']
                })
    
    try:
        # Verificar se podemos usar CSV simples primeiro
        try:
            logger.info("Tentando gerar CSV usando o módulo csv nativo")
            import csv
            from io import BytesIO, StringIO
            
            # Em qualquer ambiente, primeiro tentar CSV puro sem pandas
            if not incluir_itens or not dados_itens:
                # Apenas notas - gerar um único CSV
                output = BytesIO()
                
                # Adicionar BOM para compatibilidade com Excel
                output.write(u'\ufeff'.encode('utf-8'))
                
                # Criar um buffer intermediário
                csv_buffer = StringIO()
                
                # Escrever dados no CSV
                if dados_notas:
                    fieldnames = dados_notas[0].keys()
                    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(dados_notas)
                
                # Converter para bytes e adicionar ao output
                output.write(csv_buffer.getvalue().encode('utf-8'))
                output.seek(0)
                
                return send_file(
                    output,
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name='relatorio_notas.csv'
                )
            else:
                # Notas e itens - gerar um ZIP com dois CSVs
                output = BytesIO()
                
                with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # CSV para notas
                    notas_buffer = StringIO()
                    if dados_notas:
                        fieldnames = dados_notas[0].keys()
                        writer = csv.DictWriter(notas_buffer, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(dados_notas)
                    zipf.writestr('notas.csv', u'\ufeff' + notas_buffer.getvalue())
                    
                    # CSV para itens
                    itens_buffer = StringIO()
                    if dados_itens:
                        fieldnames = dados_itens[0].keys()
                        writer = csv.DictWriter(itens_buffer, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(dados_itens)
                    zipf.writestr('itens.csv', u'\ufeff' + itens_buffer.getvalue())
                
                output.seek(0)
                return send_file(
                    output,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name='relatorio_notas.zip'
                )
                
        except Exception as csv_error:
            # Se CSV falhar, tentar pandas
            logger.error(f"Erro ao gerar CSV com módulo nativo: {str(csv_error)}")
            logger.info("Tentando usar pandas...")
            
            # Importar pandas apenas se o CSV nativo falhar
            import pandas as pd
            import sys
            
            # Criar arquivo Excel na memória
            output = BytesIO()
            
            # Em ambiente Vercel ou se tivermos problema com numpy/pandas
            if is_vercel_env() or 'numpy.dtype size changed' in str(sys.exc_info()):
                # Opção 1: CSV na memória via pandas
                # Criar um arquivo ZIP contendo os CSVs gerados pelo pandas
                with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Converter DataFrame para CSV e adicionar ao ZIP
                    if dados_notas:
                        df_notas = pd.DataFrame(dados_notas)
                        csv_buffer = BytesIO()
                        df_notas.to_csv(csv_buffer, index=False, encoding='utf-8')
                        csv_buffer.seek(0)
                        zipf.writestr('notas.csv', csv_buffer.getvalue())
                    
                    # Adicionar itens se solicitado
                    if incluir_itens and dados_itens:
                        df_itens = pd.DataFrame(dados_itens)
                        itens_buffer = BytesIO()
                        df_itens.to_csv(itens_buffer, index=False, encoding='utf-8')
                        itens_buffer.seek(0)
                        zipf.writestr('itens.csv', itens_buffer.getvalue())
                
                # Configurar para download
                output.seek(0)
                return send_file(
                    output,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name='relatorio_notas.zip'
                )
            
            else:
                # Em ambiente local, usar XlsxWriter normalmente
                try:
                    # Tenta usar pandas/xlsxwriter normalmente
                    df_notas = pd.DataFrame(dados_notas)
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        # Salvar dados das notas
                        df_notas.to_excel(writer, sheet_name='Notas', index=False)
                        
                        # Formatar a planilha de notas
                        workbook = writer.book
                        worksheet = writer.sheets['Notas']
                        
                        # Formatos
                        header_format = workbook.add_format({
                            'bold': True,
                            'text_wrap': True,
                            'valign': 'top',
                            'bg_color': '#D9EAD3',
                            'border': 1
                        })
                        
                        # Aplicar formato ao cabeçalho
                        for col_num, value in enumerate(df_notas.columns.values):
                            worksheet.write(0, col_num, value, header_format)
                        
                        # Ajustar largura das colunas
                        for i, col in enumerate(df_notas.columns):
                            column_len = max(df_notas[col].astype(str).apply(len).max(), len(col)) + 2
                            worksheet.set_column(i, i, column_len)
                        
                        # Salvar dados dos itens (se houver)
                        if incluir_itens and dados_itens:
                            df_itens = pd.DataFrame(dados_itens)
                            df_itens.to_excel(writer, sheet_name='Itens', index=False)
                            
                            # Formatar a planilha de itens
                            worksheet_itens = writer.sheets['Itens']
                            
                            # Aplicar formato ao cabeçalho
                            for col_num, value in enumerate(df_itens.columns.values):
                                worksheet_itens.write(0, col_num, value, header_format)
                            
                            # Ajustar largura das colunas
                            for i, col in enumerate(df_itens.columns):
                                column_len = max(df_itens[col].astype(str).apply(len).max(), len(col)) + 2
                                worksheet_itens.set_column(i, i, column_len)
                    
                    # Preparar para download
                    output.seek(0)
                    return send_file(
                        output,
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True,
                        download_name='relatorio_notas.xlsx'
                    )
                except Exception as e:
                    logger.error(f"Erro ao gerar Excel com xlsxwriter: {str(e)}")
                    # Se falhar com xlsxwriter, tenta com pandas para CSV
                    df_notas = pd.DataFrame(dados_notas)
                    output = BytesIO()
                    df_notas.to_csv(output, index=False, encoding='utf-8')
                    output.seek(0)
                    return send_file(
                        output,
                        mimetype='text/csv',
                        as_attachment=True,
                        download_name='relatorio_notas.csv'
                    )
    
    except Exception as e:
        # Log do erro para facilitar diagnóstico
        logger.error(f"Erro ao gerar Excel: {str(e)}")
        
        # Em caso de erro, tentar formato CSV simples usando csv padrão como último recurso
        try:
            logger.info("Tentando fallback final para CSV")
            output = BytesIO()
            import csv
            
            # Adicionar BOM para compatibilidade com Excel
            output.write(u'\ufeff'.encode('utf-8'))
            
            # Criar um buffer intermediário
            csv_buffer = StringIO()
            
            # Escrever dados no CSV
            if dados_notas:
                fieldnames = dados_notas[0].keys()
                writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(dados_notas)
            
            # Converter para bytes e adicionar ao output
            output.write(csv_buffer.getvalue().encode('utf-8'))
            output.seek(0)
            
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name='relatorio_notas.csv'
            )
        except Exception as fallback_error:
            logger.error(f"Erro no fallback CSV: {str(fallback_error)}")
            # Informar o usuário sobre o erro de maneira amigável
            raise Exception(f"Não foi possível gerar o relatório. Por favor, tente novamente ou contate o suporte.")

def gerar_csv(notas, incluir_itens):
    """Gera arquivos CSV com os dados das notas"""
    import pandas as pd
    from io import BytesIO
    import zipfile
    
    # Criar DataFrames para as notas e itens
    dados_notas = []
    dados_itens = []
    
    for nota in notas:
        # Dados da nota
        dados_notas.append({
            'Tipo': nota['tipo'],
            'Chave': nota['chave'],
            'Número': nota['numero'],
            'Série': nota['serie'],
            'Data Emissão': nota['data_emissao'],
            'Emitente': nota['emitente']['razao_social'],
            'CNPJ Emitente': nota['emitente']['cnpj_cpf'],
            'Destinatário': nota['destinatario']['razao_social'],
            'CNPJ Destinatário': nota['destinatario']['cnpj_cpf'],
            'Valor Total': nota['valor_total'],
            'Forma Pagamento': nota['pagamento']['forma'],
            'Frete': nota['frete']
        })
        
        # Dados dos itens (se solicitado)
        if incluir_itens:
            for item in nota['itens']:
                dados_itens.append({
                    'Tipo Nota': nota['tipo'],
                    'Chave Nota': nota['chave'],
                    'Número Nota': f"{nota['numero']}/{nota['serie']}",
                    'Número Item': item['numero'],
                    'Código': item['codigo'],
                    'Descrição': item['descricao'],
                    'Valor Total': item['valor_total']
                })
    
    # Criar arquivo ZIP com os CSVs
    output = BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Salvar dados das notas
        df_notas = pd.DataFrame(dados_notas)
        notas_csv = df_notas.to_csv(index=False).encode('utf-8')
        zipf.writestr('notas.csv', notas_csv)
        
        # Salvar dados dos itens (se houver)
        if incluir_itens and dados_itens:
            df_itens = pd.DataFrame(dados_itens)
            itens_csv = df_itens.to_csv(index=False).encode('utf-8')
            zipf.writestr('itens.csv', itens_csv)
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/zip',
        as_attachment=True,
        download_name='relatorio_notas.zip'
    )

def processar_xml(filepath):
    """Processa o arquivo XML e extrai as informações relevantes"""
    try:
        # Iniciar um dicionário para armazenar os dados extraídos
        xml_data = {
            'chave': '',
            'tipo': '',
            'numero': '',
            'serie': '',
            'data_emissao': '',
            'nat_op': '',
            'valor_total': '0,00',
            'emitente': {
                'razao_social': '',
                'nome_fantasia': '',
                'cnpj_cpf': '',
                'ie': '',
                'endereco': '',
                'municipio': '',
                'uf': '',
            },
            'destinatario': {
                'razao_social': '',
                'cnpj_cpf': '',
                'ie': '',
                'endereco': '',
                'municipio': '',
                'uf': '',
                'email': '',
            },
            'itens': [],
            'pagamento': {
                'forma': 'Não informado',
                'valor': '0,00',
            },
            'frete': 'Não informado',
            'tributos': {
                'bc_icms': '0,00',
                'valor_icms': '0,00',
                'bc_icms_st': '0,00',
                'valor_icms_st': '0,00',
                'valor_produtos': '0,00',
                'valor_frete': '0,00',
                'valor_desconto': '0,00',
                'valor_nota': '0,00',
            },
            'protocolo': 'Não informado',
            'data_autorizacao': 'Não informado',
            'ambiente': 'Não informado',
        }
        
        try:
            # Fazer o parsing do arquivo XML
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            # Determinar namespace se existir
            ns = {}
            if '}' in root.tag:
                ns_uri = root.tag.split('}')[0].strip('{')
                ns = {'nfe': ns_uri}
            
            # Determinar o tipo do documento
            if 'NFe' in root.tag:
                xml_data['tipo'] = 'NFe'
            elif 'NFCe' in root.tag:
                xml_data['tipo'] = 'NFCe'
            elif 'CTe' in root.tag:
                xml_data['tipo'] = 'CTe'
            else:
                xml_data['tipo'] = 'Outro'
            
            # Tentar extrair as informações principais com ou sem namespace
            # Identificar os elementos principais do XML (NFe, infNFe, etc.)
            if ns:
                # Com namespace
                nfe = root.find('.//nfe:NFe', ns) if root.find('.//nfe:NFe', ns) is not None else root
                inf_nfe = nfe.find('.//nfe:infNFe', ns) if nfe is not None else None
                ide = inf_nfe.find('.//nfe:ide', ns) if inf_nfe is not None else None
                emit = inf_nfe.find('.//nfe:emit', ns) if inf_nfe is not None else None
                dest = inf_nfe.find('.//nfe:dest', ns) if inf_nfe is not None else None
                det_list = inf_nfe.findall('.//nfe:det', ns) if inf_nfe is not None else []
                total = inf_nfe.find('.//nfe:total/nfe:ICMSTot', ns) if inf_nfe is not None else None
                pag = inf_nfe.find('.//nfe:pag', ns) if inf_nfe is not None else None
                transp = inf_nfe.find('.//nfe:transp', ns) if inf_nfe is not None else None
                prot_nfe = root.find('.//nfe:protNFe', ns) if root.find('.//nfe:protNFe', ns) is not None else None
            else:
                # Sem namespace
                nfe = root.find('.//NFe') if root.find('.//NFe') is not None else root
                inf_nfe = nfe.find('.//infNFe') if nfe is not None else None
                ide = inf_nfe.find('.//ide') if inf_nfe is not None else None
                emit = inf_nfe.find('.//emit') if inf_nfe is not None else None
                dest = inf_nfe.find('.//dest') if inf_nfe is not None else None
                det_list = inf_nfe.findall('.//det') if inf_nfe is not None else []
                total = inf_nfe.find('.//total/ICMSTot') if inf_nfe is not None else None
                pag = inf_nfe.find('.//pag') if inf_nfe is not None else None
                transp = inf_nfe.find('.//transp') if inf_nfe is not None else None
                prot_nfe = root.find('.//protNFe') if root.find('.//protNFe') is not None else None
            
            # Extrair chave de acesso (ID da NFe)
            if inf_nfe is not None and 'Id' in inf_nfe.attrib:
                xml_data['chave'] = inf_nfe.attrib['Id'].replace('NFe', '')
            
            # Extrair número da nota
            if ide is not None:
                nNF = ide.find('.//nfe:nNF', ns) if ns else ide.find('.//nNF')
                if nNF is not None:
                    xml_data['numero'] = nNF.text
                
                serie = ide.find('.//nfe:serie', ns) if ns else ide.find('.//serie')
                if serie is not None:
                    xml_data['serie'] = serie.text
                
                dhEmi = ide.find('.//nfe:dhEmi', ns) if ns else ide.find('.//dhEmi')
                if dhEmi is not None:
                    data_str = dhEmi.text
                    xml_data['data_emissao'] = format_date(data_str)
                
                natOp = ide.find('.//nfe:natOp', ns) if ns else ide.find('.//natOp')
                if natOp is not None:
                    xml_data['nat_op'] = natOp.text
            
            # Extrair informações do emitente (fornecedor)
            if emit is not None:
                xNome = emit.find('.//nfe:xNome', ns) if ns else emit.find('.//xNome')
                if xNome is not None:
                    xml_data['emitente']['razao_social'] = xNome.text
                
                xFant = emit.find('.//nfe:xFant', ns) if ns else emit.find('.//xFant')
                if xFant is not None:
                    xml_data['emitente']['nome_fantasia'] = xFant.text
                
                CNPJ = emit.find('.//nfe:CNPJ', ns) if ns else emit.find('.//CNPJ')
                if CNPJ is not None:
                    xml_data['emitente']['cnpj_cpf'] = format_cnpj_cpf(CNPJ.text)
            
            # Extrair informações do destinatário
            if dest is not None:
                xNome = dest.find('.//nfe:xNome', ns) if ns else dest.find('.//xNome')
                if xNome is not None:
                    xml_data['destinatario']['razao_social'] = xNome.text
                
                CNPJ = dest.find('.//nfe:CNPJ', ns) if ns else dest.find('.//CNPJ')
                if CNPJ is not None:
                    xml_data['destinatario']['cnpj_cpf'] = format_cnpj_cpf(CNPJ.text)
            
            # Extrair valor total
            if total is not None:
                vNF = total.find('.//nfe:vNF', ns) if ns else total.find('.//vNF')
                if vNF is not None:
                    xml_data['valor_total'] = format_number(vNF.text)
                    xml_data['tributos']['valor_nota'] = xml_data['valor_total']
            
            # Extrair forma de pagamento
            if pag is not None:
                det_pag = pag.find('.//nfe:detPag', ns) if ns else pag.find('.//detPag')
                if det_pag is not None:
                    tPag = det_pag.find('.//nfe:tPag', ns) if ns else det_pag.find('.//tPag')
                    vPag = det_pag.find('.//nfe:vPag', ns) if ns else det_pag.find('.//vPag')
                    
                    if tPag is not None:
                        xml_data['pagamento']['forma'] = get_forma_pagamento(tPag.text)
                    
                    if vPag is not None:
                        xml_data['pagamento']['valor'] = format_number(vPag.text)
            
            # Extrair informações de transporte
            if transp is not None:
                mod_frete = transp.find('.//nfe:modFrete', ns) if ns else transp.find('.//modFrete')
                if mod_frete is not None:
                    xml_data['frete'] = get_modalidade_frete(mod_frete.text)
            
            # Extrair protocolo de autorização
            if prot_nfe is not None:
                inf_prot = prot_nfe.find('.//nfe:infProt', ns) if ns else prot_nfe.find('.//infProt')
                if inf_prot is not None:
                    n_prot = inf_prot.find('.//nfe:nProt', ns) if ns else inf_prot.find('.//nProt')
                    dh_recbto = inf_prot.find('.//nfe:dhRecbto', ns) if ns else inf_prot.find('.//dhRecbto')
                    
                    if n_prot is not None:
                        xml_data['protocolo'] = n_prot.text
                    
                    if dh_recbto is not None:
                        xml_data['data_autorizacao'] = format_date(dh_recbto.text)
            
            # Extrair itens/produtos
            for item in det_list:
                prod = item.find('.//nfe:prod', ns) if ns else item.find('.//prod')
                if prod is not None:
                    xProd = prod.find('.//nfe:xProd', ns) if ns else prod.find('.//xProd')
                    vProd = prod.find('.//nfe:vProd', ns) if ns else prod.find('.//vProd')
                    cProd = prod.find('.//nfe:cProd', ns) if ns else prod.find('.//cProd')
                    
                    produto = {
                        'numero': item.attrib.get('nItem', ''),
                        'codigo': cProd.text if cProd is not None else '',
                        'descricao': xProd.text if xProd is not None else '',
                        'valor_total': format_number(vProd.text) if vProd is not None else '0,00'
                    }
                    
                    xml_data['itens'].append(produto)
                    
            return xml_data
            
        except Exception as e:
            logger.error(f"Erro ao extrair informações: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"Erro ao processar XML: {str(e)}")
        return None

def get_text(element, tag, ns):
    """Obtém o texto de um elemento XML considerando namespace"""
    if element is None:
        return ''
    
    result = element.find(f'.//nfe:{tag}', ns)
    if result is None:
        result = element.find(f'.//{tag}')
    
    return result.text if result is not None else ''

def format_date(date_str):
    """Formata a data no padrão brasileiro"""
    if not date_str:
        return ''
    
    # Remover timezone se existir
    date_str = date_str.split('-0')[0] if '-0' in date_str else date_str.split('T')[0] if 'T' in date_str else date_str
    
    # Converter para o formato DD/MM/YYYY
    if 'T' in date_str:
        date_parts = date_str.split('T')
        date = date_parts[0].split('-')
        time = date_parts[1].split(':')
        return f"{date[2]}/{date[1]}/{date[0]} {time[0]}:{time[1]}"
    elif '-' in date_str:
        date = date_str.split('-')
        return f"{date[2]}/{date[1]}/{date[0]}"
    
    return date_str

def format_number(number_str):
    """Formata um número para o padrão brasileiro"""
    if not number_str:
        return '0,00'
    
    try:
        # Remove caracteres não numéricos exceto ponto e vírgula
        number_str = ''.join(c for c in number_str if c.isdigit() or c in '.,')
        
        # Se não houver separador decimal, adiciona ',00'
        if '.' not in number_str and ',' not in number_str:
            number_str = f"{number_str},00"
        
        # Converte para float, tratando diferentes formatos
        if ',' in number_str and '.' in number_str:
            # Formato 1.234,56
            number = float(number_str.replace('.', '').replace(',', '.'))
        elif ',' in number_str:
            # Formato 1234,56
            number = float(number_str.replace(',', '.'))
        else:
            # Formato 1234.56
            number = float(number_str)
        
        # Formata para o padrão brasileiro (1.234,56)
        return f"{number:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except ValueError:
        return '0,00'

def format_cnpj_cpf(document):
    """Formata CNPJ ou CPF"""
    if not document:
        return ''
    
    # CNPJ
    if len(document) == 14:
        return f"{document[:2]}.{document[2:5]}.{document[5:8]}/{document[8:12]}-{document[12:]}"
    # CPF
    elif len(document) == 11:
        return f"{document[:3]}.{document[3:6]}.{document[6:9]}-{document[9:]}"
    
    return document

def format_endereco(element, ns):
    """Formata o endereço a partir dos elementos XML"""
    if element is None:
        return ''
    
    # Determinar se é endereço do emitente ou destinatário
    ender_tag = 'enderEmit' if element.find('.//nfe:enderEmit', ns) is not None or element.find('./enderEmit') is not None else 'enderDest'
    
    logradouro = get_text(element, f'.//{ender_tag}/xLgr', ns) or get_text(element, f'.//{ender_tag}/xLgr') or ''
    numero = get_text(element, f'.//{ender_tag}/nro', ns) or get_text(element, f'.//{ender_tag}/nro') or ''
    complemento = get_text(element, f'.//{ender_tag}/xCpl', ns) or get_text(element, f'.//{ender_tag}/xCpl') or ''
    bairro = get_text(element, f'.//{ender_tag}/xBairro', ns) or get_text(element, f'.//{ender_tag}/xBairro') or ''
    municipio = get_text(element, f'.//{ender_tag}/xMun', ns) or get_text(element, f'.//{ender_tag}/xMun') or ''
    uf = get_text(element, f'.//{ender_tag}/UF', ns) or get_text(element, f'.//{ender_tag}/UF') or ''
    cep = get_text(element, f'.//{ender_tag}/CEP', ns) or get_text(element, f'.//{ender_tag}/CEP') or ''
    
    if cep and len(cep) == 8:
        cep = f"{cep[:5]}-{cep[5:]}"
    
    endereco = f"{logradouro}, {numero}"
    if complemento:
        endereco += f" - {complemento}"
    endereco += f", {bairro}, {municipio}/{uf}, CEP: {cep}"
    
    return endereco

def get_forma_pagamento(codigo):
    """Retorna a descrição da forma de pagamento conforme o código"""
    formas = {
        '01': 'Dinheiro',
        '02': 'Cheque',
        '03': 'Cartão de Crédito',
        '04': 'Cartão de Débito',
        '05': 'Crédito Loja',
        '10': 'Vale Alimentação',
        '11': 'Vale Refeição',
        '12': 'Vale Presente',
        '13': 'Vale Combustível',
        '15': 'Boleto Bancário',
        '16': 'Depósito Bancário',
        '17': 'PIX',
        '18': 'Transferência bancária',
        '19': 'Programa de fidelidade',
        '90': 'Sem pagamento',
        '99': 'Outros'
    }
    
    return formas.get(codigo, f'Forma de pagamento ({codigo})')

def get_modalidade_frete(codigo):
    """Retorna a descrição da modalidade de frete conforme o código"""
    modalidades = {
        '0': 'Contratação do Frete por conta do Remetente (CIF)',
        '1': 'Contratação do Frete por conta do Destinatário (FOB)',
        '2': 'Contratação do Frete por conta de Terceiros',
        '3': 'Transporte Próprio por conta do Remetente',
        '4': 'Transporte Próprio por conta do Destinatário',
        '9': 'Sem Transporte'
    }
    
    return modalidades.get(codigo, f'Modalidade de Frete ({codigo})')

def gerar_danfe_api(xml_content):
    """
    Gera o DANFE/DACTe usando a API do MeuDanfe.
    
    Args:
        xml_content (str): Conteúdo do arquivo XML em texto
        
    Returns:
        tuple: (sucesso, conteúdo_ou_erro)
            - Se sucesso=True, conteúdo_ou_erro contém o PDF em base64
            - Se sucesso=False, conteúdo_ou_erro contém a mensagem de erro
    """
    try:
        # URL da API do MeuDanfe
        url = 'https://ws.meudanfe.com/api/v1/get/nfe/xmltodanfepdf/API'
        headers = {'Content-Type': 'text/plain'}
        
        # Enviar o XML como texto puro no corpo da requisição
        response = requests.post(url, data=xml_content, headers=headers)
        
        if response.status_code == 200:
            # Remove aspas extras do base64 se houver
            pdf_base64 = response.text.strip('"')
            return True, pdf_base64
        else:
            return False, f'Erro na API: {response.status_code} - {response.text}'
            
    except Exception as e:
        return False, f'Erro ao gerar PDF: {str(e)}'

@app.route('/converter-xml-para-danfe', methods=['GET', 'POST'])
def converter_xml_para_danfe():
    if request.method == 'POST':
        if 'xml_files' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
            
        files = request.files.getlist('xml_files')
        if not files or files[0].filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
            
        # Garantir que o diretório de uploads existe
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        processed_files = []
        temp_files = []  # Lista para controlar arquivos temporários
        
        for file in files:
            if file and file.filename.endswith('.xml'):
                filename = secure_filename(file.filename)
                temp_path = os.path.join(tempfile.gettempdir(), filename)
                temp_files.append(temp_path)  # Adicionar à lista de controle
                
                try:
                    # Salva o arquivo temporariamente
                    file.save(temp_path)
                    
                    # Lê o conteúdo do XML
                    with open(temp_path, 'r', encoding='utf-8') as f:
                        xml_content = f.read()
                    
                    # Extrai os dados do XML
                    dados = processar_xml(temp_path)
                    if dados:
                        dados.update({
                            'nome': filename,
                            'temp_path': temp_path,  # Salvar o caminho temporário
                            'status': 'success',
                            'mensagem': 'Arquivo processado com sucesso',
                            'pdf_gerado': False
                        })
                        processed_files.append(dados)
                    else:
                        processed_files.append({
                            'nome': filename,
                            'status': 'error',
                            'mensagem': 'Erro ao processar o XML'
                        })
                        
                except Exception as e:
                    processed_files.append({
                        'nome': filename,
                        'status': 'error',
                        'mensagem': str(e)
                    })
        
        # Armazena os arquivos processados na sessão
        session['processed_files'] = processed_files
        session['temp_files'] = temp_files  # Salvar lista de arquivos temporários
        
        if not processed_files:
            flash('Nenhum arquivo XML válido foi processado', 'error')
        else:
            flash(f'{len(processed_files)} arquivo(s) processado(s) com sucesso', 'success')
            
        return render_template('xml_para_pdf.html', processed_files=processed_files)
        
    return render_template('xml_para_pdf.html')

@app.route('/visualizar-pdf/<filename>')
def visualizar_pdf(filename):
    """Retorna o PDF para visualização no navegador."""
    processed_files = session.get('processed_files', [])
    
    if is_vercel_env():
        # No Vercel, temos que regenerar o PDF
        # Encontra o arquivo correspondente ao filename
        file_data = next((f for f in processed_files if f.get('pdf_path') == filename), None)
        
        if not file_data:
            flash('Arquivo não encontrado', 'error')
            return redirect(url_for('converter_xml_para_danfe'))
        
        try:
            # Recupera o XML
            temp_path = file_data.get('temp_path')
            
            if not temp_path or not os.path.exists(temp_path):
                flash('Arquivo XML não encontrado', 'error')
                return redirect(url_for('converter_xml_para_danfe'))
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Gera o PDF
            success, result = gerar_danfe_api(xml_content)
            
            if success:
                # Decodifica o PDF
                pdf_content = base64.b64decode(result)
                
                # Cria um stream de memória
                pdf_stream = BytesIO(pdf_content)
                pdf_stream.seek(0)
                
                # Retorna o PDF para visualização no navegador
                return send_file(
                    pdf_stream,
                    mimetype='application/pdf',
                    as_attachment=False,
                    download_name=filename
                )
            else:
                flash(f'Erro ao gerar PDF: {result}', 'error')
                return redirect(url_for('converter_xml_para_danfe'))
                
        except Exception as e:
            flash(f'Erro ao gerar PDF: {str(e)}', 'error')
            return redirect(url_for('converter_xml_para_danfe'))
    else:
        # Em ambiente local, usamos o sistema de arquivos
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            filename,
            mimetype='application/pdf'
        )

@app.route('/gerar-pdf/<chave>')
def gerar_pdf(chave):
    """Gera o PDF para uma nota específica."""
    processed_files = session.get('processed_files', [])
    temp_files = session.get('temp_files', [])
    
    # Encontra o arquivo correspondente à chave
    file_data = next((f for f in processed_files if f.get('chave') == chave), None)
    file_index = next((i for i, f in enumerate(processed_files) if f.get('chave') == chave), None)
    
    if not file_data or file_index is None:
        flash('Arquivo não encontrado', 'error')
        return redirect(url_for('converter_xml_para_danfe'))
    
    try:
        # Recupera o XML do arquivo temporário
        temp_path = file_data.get('temp_path')
        
        if not temp_path or not os.path.exists(temp_path):
            flash('Arquivo XML não encontrado', 'error')
            return redirect(url_for('converter_xml_para_danfe'))
        
        with open(temp_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # Gera o PDF
        success, result = gerar_danfe_api(xml_content)
        
        if success:
            # Decodifica o PDF do base64
            pdf_content = base64.b64decode(result)
            
            # Define o nome do arquivo
            pdf_filename = f"{chave}.pdf"
            
            if is_vercel_env():
                # No Vercel, usamos BytesIO para manter o PDF em memória
                pdf_stream = BytesIO(pdf_content)
                
                # Atualiza o status do arquivo na sessão
                file_data['pdf_gerado'] = True
                file_data['pdf_path'] = pdf_filename
                processed_files[file_index] = file_data
                session['processed_files'] = processed_files
                session.modified = True
                
                # Configura o stream para ser lido do início
                pdf_stream.seek(0)
                
                # Retorna o PDF diretamente da memória
                return send_file(
                    pdf_stream,
                    mimetype='application/pdf',
                    as_attachment=False,
                    download_name=pdf_filename
                )
            else:
                # Em ambiente local, salvamos no sistema de arquivos
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
                
                # Garantir que o diretório existe
                os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_content)
                
                # Atualiza o status do arquivo na sessão
                file_data['pdf_gerado'] = True
                file_data['pdf_path'] = pdf_filename
                processed_files[file_index] = file_data
                session['processed_files'] = processed_files
                session.modified = True
                
                # Retorna o PDF do sistema de arquivos
                return send_file(
                    pdf_path,
                    mimetype='application/pdf'
                )
        else:
            flash(f'Erro ao gerar PDF: {result}', 'error')
            return redirect(url_for('converter_xml_para_danfe'))
            
    except Exception as e:
        flash(f'Erro ao gerar PDF: {str(e)}', 'error')
        return redirect(url_for('converter_xml_para_danfe'))
    finally:
        # Limpar arquivos temporários após o processamento
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        session.pop('temp_files', None)  # Remover lista de arquivos temporários

@app.route('/download-pdf/<filename>')
def download_pdf(filename):
    """Download de um PDF específico."""
    processed_files = session.get('processed_files', [])
    
    if is_vercel_env():
        # No Vercel, temos que regenerar o PDF
        # Encontra o arquivo correspondente ao filename
        file_data = next((f for f in processed_files if f.get('pdf_path') == filename), None)
        
        if not file_data:
            flash('Arquivo não encontrado', 'error')
            return redirect(url_for('converter_xml_para_danfe'))
        
        try:
            # Recupera o XML
            temp_path = file_data.get('temp_path')
            
            if not temp_path or not os.path.exists(temp_path):
                flash('Arquivo XML não encontrado', 'error')
                return redirect(url_for('converter_xml_para_danfe'))
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Gera o PDF
            success, result = gerar_danfe_api(xml_content)
            
            if success:
                # Decodifica o PDF
                pdf_content = base64.b64decode(result)
                
                # Cria um stream de memória
                pdf_stream = BytesIO(pdf_content)
                pdf_stream.seek(0)
                
                # Retorna o PDF como download
                return send_file(
                    pdf_stream,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=filename
                )
            else:
                flash(f'Erro ao gerar PDF: {result}', 'error')
                return redirect(url_for('converter_xml_para_danfe'))
                
        except Exception as e:
            flash(f'Erro ao gerar PDF: {str(e)}', 'error')
            return redirect(url_for('converter_xml_para_danfe'))
    else:
        # Em ambiente local, usamos o sistema de arquivos
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/download-all-pdfs')
def download_all_pdfs():
    """Download de todos os PDFs em um arquivo ZIP."""
    import zipfile
    import io
    
    processed_files = session.get('processed_files', [])
    memory_file = io.BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in processed_files:
            if file.get('pdf_gerado') and file.get('pdf_path'):
                pdf_filename = file['pdf_path']
                
                if is_vercel_env():
                    # No Vercel, temos que regenerar cada PDF
                    try:
                        # Recupera o XML
                        temp_path = file.get('temp_path')
                        
                        if temp_path and os.path.exists(temp_path):
                            with open(temp_path, 'r', encoding='utf-8') as f:
                                xml_content = f.read()
                            
                            # Gera o PDF novamente
                            success, result = gerar_danfe_api(xml_content)
                            
                            if success:
                                # Adiciona o PDF ao ZIP a partir do conteúdo em memória
                                pdf_content = base64.b64decode(result)
                                zf.writestr(pdf_filename, pdf_content)
                    except Exception as e:
                        flash(f"Erro ao gerar PDF {pdf_filename}: {str(e)}", "error")
                else:
                    # Em ambiente local, lemos do sistema de arquivos
                    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
                    if os.path.exists(pdf_path):
                        # Usar o nome do arquivo como nome no ZIP
                        arcname = os.path.basename(pdf_path)
                        zf.write(pdf_path, arcname)
    
    # Configurar o ponteiro de leitura para o início
    memory_file.seek(0)
    
    # Retornar o arquivo ZIP como resposta
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='danfes.zip'
    )

@app.route('/converter-xml-para-excel', methods=['GET', 'POST'])
def converter_xml_para_excel():
    if request.method == 'POST':
        if 'xml_files' not in request.files:
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
        
        xml_files = request.files.getlist('xml_files')
        incluir_itens = request.form.get('incluir_itens') == 'on'
        
        if not xml_files or xml_files[0].filename == '':
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
        
        # Lista para armazenar os dados de todas as notas
        todas_notas = []
        
        # Processar cada arquivo XML
        for xml_file in xml_files:
            if xml_file and xml_file.filename.endswith('.xml'):
                # Salvar o arquivo temporariamente
                filename = secure_filename(xml_file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                xml_file.save(filepath)
                
                # Processar o arquivo XML
                nota_data = processar_xml(filepath)
                if nota_data:
                    # Adicionar o nome do arquivo original
                    nota_data['arquivo_original'] = filename
                    todas_notas.append(nota_data)
                
                # Remover o arquivo temporário
                os.remove(filepath)
        
        if todas_notas:
            # Armazenar os dados na sessão para download posterior
            session['notas_processadas'] = todas_notas
            session['incluir_itens'] = incluir_itens
            flash('XMLs processados com sucesso!', 'success')
            
            # Renderizar a página com os dados ao invés de baixar automaticamente
            return render_template('xml_para_excel.html', notas=todas_notas, incluir_itens=incluir_itens, mostrar_relatorio=True)
        else:
            flash('Nenhum arquivo XML válido foi processado', 'danger')
            return redirect(request.url)
    
    return render_template('xml_para_excel.html', mostrar_relatorio=False)

@app.route('/download-excel')
def download_excel():
    """Download do arquivo Excel com os dados processados."""
    try:
        notas = session.get('notas_processadas')
        incluir_itens = session.get('incluir_itens', False)
        
        if not notas:
            flash('Nenhum dado disponível para download. Por favor, processe os XMLs novamente.', 'warning')
            return redirect(url_for('converter_xml_para_excel'))
        
        # Gerar e enviar o arquivo Excel
        return gerar_excel(notas, incluir_itens)
    except Exception as e:
        # Log do erro para diagnóstico
        logger.error(f"Erro ao processar download de Excel: {str(e)}")
        
        # Informar ao usuário
        flash(f'Erro ao gerar arquivo: {str(e)}', 'danger')
        return redirect(url_for('converter_xml_para_excel'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
else:
    # Garantir que a pasta uploads exista quando executado pelo Vercel
    if 'UPLOAD_FOLDER' in app.config and not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER']) 
