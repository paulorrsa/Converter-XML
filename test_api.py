from app import gerar_danfe_api
import base64
import os

def test_api():
    # Ler o arquivo XML de teste
    with open('nota.xml', 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    # Tentar gerar o PDF
    print("Enviando XML para a API...")
    success, result = gerar_danfe_api(xml_content)
    
    if success:
        print("PDF gerado com sucesso!")
        # Salvar o PDF
        pdf_path = 'app/uploads/teste.pdf'
        with open(pdf_path, 'wb') as f:
            f.write(base64.b64decode(result))
        print(f"PDF salvo em: {pdf_path}")
        print(f"Tamanho do arquivo: {os.path.getsize(pdf_path)} bytes")
    else:
        print(f"Erro ao gerar PDF: {result}")

if __name__ == '__main__':
    test_api() 