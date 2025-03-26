import unittest
from app import app
import os

class TestFSistApp(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
    def test_index_route(self):
        """Teste para verificar se a página inicial carrega corretamente"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Baixar XML de NFe/CTe', response.data)
        self.assertIn(b'certificado digital', response.data)
        
    def test_historico_route(self):
        """Teste para verificar se a página de histórico carrega corretamente"""
        response = self.client.get('/historico')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hist\xc3\xb3rico de Hoje', response.data)
        
    def test_resultado_route(self):
        """Teste para verificar se a página de resultado carrega corretamente"""
        chave_teste = '35220911111111111111550010000012341234567890'
        response = self.client.get(f'/resultado/{chave_teste}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Resultado da Consulta', response.data)
        self.assertIn(chave_teste.encode(), response.data)
        
    def test_xml_para_pdf_route(self):
        """Teste para verificar se a página de conversão XML para PDF carrega corretamente"""
        response = self.client.get('/xml_para_pdf')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Converter XML para PDF', response.data)
        
    def test_consultar_form_invalido(self):
        """Teste para verificar validação do formulário com chave inválida"""
        response = self.client.post('/consultar', data={
            'tipo_documento': 'NFe',
            'chave_acesso': '12345', # Chave muito curta
            'captcha': 'ABCDE'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'A chave deve conter exatamente 44 d\xc3\xadgitos', response.data)
        
    def test_consultar_form_valido(self):
        """Teste para verificar processamento do formulário com chave válida"""
        response = self.client.post('/consultar', data={
            'tipo_documento': 'NFe',
            'chave_acesso': '35220911111111111111550010000012341234567890',
            'captcha': 'ABCDE'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Resultado da Consulta', response.data)
        
    def test_download_xml(self):
        """Teste para verificar a rota de download de XML"""
        chave_teste = '35220911111111111111550010000012341234567890'
        response = self.client.get(f'/download_xml/{chave_teste}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'XML baixado com sucesso', response.data)
        
    def test_gerar_danfe(self):
        """Teste para verificar a rota de geração de DANFE"""
        chave_teste = '35220911111111111111550010000012341234567890'
        response = self.client.get(f'/gerar_danfe/{chave_teste}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'DANFE gerado com sucesso', response.data)
        
    def test_xmls_compartilhados(self):
        """Teste para verificar a rota de XMLs compartilhados"""
        response = self.client.get('/xmls-compartilhados')
        self.assertEqual(response.status_code, 200)
        
    def test_rotas_adicionais(self):
        """Testes para outras rotas importantes"""
        rotas = [
            '/converter-xml-nfe-para-danfe',
            '/xmls-compartilhados',
            '/contato'
        ]
        
        for rota in rotas:
            response = self.client.get(rota)
            self.assertEqual(response.status_code, 200, f"Rota {rota} falhou")

if __name__ == '__main__':
    unittest.main() 