import os
import base64
import requests
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gerar_danfe_api(xml_content):
    """
    Gera o DANFE usando a API do MeuDanfe.
    
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
        
        logger.info("Enviando XML para a API do MeuDanfe...")
        logger.info(f"Tamanho do XML: {len(xml_content)} bytes")
        logger.info(f"Primeiros 200 caracteres do XML: {xml_content[:200]}...")
        
        # Enviar o XML como texto puro no corpo da requisição
        response = requests.post(url, data=xml_content, headers=headers)
        
        if response.status_code == 200:
            # Remove aspas extras do base64 se houver
            pdf_base64 = response.text.strip('"')
            logger.info("PDF gerado com sucesso!")
            logger.info(f"Tamanho do PDF em base64: {len(pdf_base64)} bytes")
            return True, pdf_base64
        else:
            error_msg = f'Erro na API: {response.status_code} - {response.text}'
            logger.error(error_msg)
            return False, error_msg
            
    except Exception as e:
        error_msg = f'Erro ao gerar PDF: {str(e)}'
        logger.error(error_msg)
        return False, error_msg

def test_api():
    """
    Testa a geração de DANFE com um arquivo XML de exemplo.
    """
    logger.info("\n=== Iniciando teste da API do MeuDanfe ===\n")
    
    # Criar diretório de uploads se não existir
    upload_dir = Path("app/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Diretório de uploads criado/verificado: {upload_dir}")
    
    # Ler arquivo XML de teste
    xml_file = "nota.xml"
    logger.info(f"\nLendo arquivo XML: {xml_file}")
    
    try:
        with open(xml_file, "r", encoding='utf-8') as f:
            xml_content = f.read()
            logger.info(f"Arquivo XML lido com sucesso ({len(xml_content)} bytes)")
            
            logger.info("\nIniciando geração do PDF...")
            success, result = gerar_danfe_api(xml_content)
            
            if success:
                # Salvar o PDF gerado
                pdf_file = "danfe_teste.pdf"
                pdf_content = base64.b64decode(result)
                with open(pdf_file, "wb") as f:
                    f.write(pdf_content)
                logger.info(f"\nPDF salvo com sucesso: {pdf_file}")
                
                # Gerar URL para visualização no navegador
                browser_url = f"data:application/pdf;base64,{result}"
                logger.info("\nURL para visualizar no navegador:")
                logger.info(browser_url[:100] + "...")
            else:
                logger.error(f"\nNão foi possível gerar o PDF: {result}")
                
    except FileNotFoundError:
        logger.error(f"\nArquivo XML não encontrado: {xml_file}")
    except Exception as e:
        logger.error(f"\nErro ao testar API: {str(e)}")
        
    logger.info("\n=== Teste concluído ===")

if __name__ == "__main__":
    test_api() 