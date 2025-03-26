import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
from app import app, gerar_danfe_api

class TestIntegracaoFSist(unittest.TestCase):
    """Testes de integração para verificar a funcionalidade da aplicação FSist em um navegador"""
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial para os testes de integração"""
        # Configurar o Chrome em modo headless
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
        except:
            # Fallback para Firefox se Chrome não estiver disponível
            print("Chrome não disponível, tentando Firefox")
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            cls.driver = webdriver.Firefox(options=firefox_options)
            
        cls.driver.implicitly_wait(10)
        
        # Iniciar a aplicação Flask (assumindo que está rodando em outro processo)
        cls.base_url = "http://127.0.0.1:5000"
        
    @classmethod
    def tearDownClass(cls):
        """Limpar após todos os testes"""
        cls.driver.quit()
        
    def test_01_pagina_inicial_carrega(self):
        """Teste para verificar se a página inicial carrega corretamente"""
        self.driver.get(self.base_url)
        
        # Verificar se o título da página está correto
        self.assertIn("FSist - Baixar XML", self.driver.title)
        
        # Verificar se o formulário de consulta está presente
        form = self.driver.find_element(By.TAG_NAME, "form")
        self.assertIsNotNone(form)
        
        # Verificar se os campos principais estão presentes
        self.assertIsNotNone(self.driver.find_element(By.ID, "chaveInput"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "captchaInput"))
        
    def test_02_validacao_chave_acesso(self):
        """Teste para verificar a validação da chave de acesso"""
        self.driver.get(self.base_url)
        
        # Obter os elementos do formulário
        chave_input = self.driver.find_element(By.ID, "chaveInput")
        captcha_input = self.driver.find_element(By.ID, "captchaInput")
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        
        # Preencher com dados inválidos
        chave_input.clear()
        chave_input.send_keys("12345")  # Chave muito curta
        captcha_input.clear()
        captcha_input.send_keys("ABCDE")
        
        # Enviar o formulário
        submit_button.click()
        
        # Verificar se exibe a mensagem de erro
        time.sleep(1)  # Pequena pausa para garantir que a página seja atualizada
        page_source = self.driver.page_source
        self.assertIn("A chave deve conter exatamente 44 dígitos", page_source)
        
    def test_03_consulta_chave_valida(self):
        """Teste para verificar o processo de consulta com chave válida"""
        self.driver.get(self.base_url)
        
        # Obter os elementos do formulário
        chave_input = self.driver.find_element(By.ID, "chaveInput")
        captcha_input = self.driver.find_element(By.ID, "captchaInput")
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        
        # Preencher com dados válidos
        chave_input.clear()
        chave_input.send_keys("35220911111111111111550010000012341234567890")  # Chave válida
        captcha_input.clear()
        captcha_input.send_keys("ABCDE")
        
        # Enviar o formulário
        submit_button.click()
        
        # Verificar se redirecionou para a página de resultado
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Resultado da Consulta')]"))
        )
        
        # Verificar se os detalhes do documento estão presentes
        self.assertIn("Dados do Documento", self.driver.page_source)
        self.assertIn("Dados do Emitente", self.driver.page_source)
        
    def test_04_navegacao_menu(self):
        """Teste para verificar a navegação pelo menu principal"""
        self.driver.get(self.base_url)
        
        # Lista de páginas para testar
        paginas = [
            {"link": "Histórico de Hoje", "texto_esperado": "Histórico de Hoje"},
            {"link": "Converter XML para PDF", "texto_esperado": "Converter XML para PDF"},
            {"link": "Contato", "texto_esperado": "Contato"}
        ]
        
        # Testar cada link do menu
        for pagina in paginas:
            # Voltar para a página inicial antes de cada teste
            self.driver.get(self.base_url)
            
            # Clicar no link do menu
            link = self.driver.find_element(By.LINK_TEXT, pagina["link"])
            link.click()
            
            # Verificar se carregou a página correta
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{pagina['texto_esperado']}')]"))
            )
            
    def test_05_historico_exibe_consultas(self):
        """Teste para verificar se o histórico mostra as consultas realizadas"""
        # Realizar uma consulta primeiro
        self.test_03_consulta_chave_valida()
        
        # Navegar para a página de histórico
        self.driver.get(f"{self.base_url}/historico")
        
        # Verificar se a tabela de histórico está presente
        tabela = self.driver.find_element(By.CLASS_NAME, "key-history-table")
        self.assertIsNotNone(tabela)
        
        # Verificar se a chave consultada aparece no histórico
        self.assertIn("35220911111111111111550010000012341234567890", self.driver.page_source)
        
    def test_gerar_pdf_api(self):
        """Testa a geração de PDF usando a API do MeuDanfe"""
        # Ler o arquivo XML de teste
        with open('nota.xml', 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # Tentar gerar o PDF
        success, result = gerar_danfe_api(xml_content)
        
        # Verificar se a API retornou sucesso
        self.assertTrue(success, f"Falha ao gerar PDF: {result}")
        
        # Verificar se o resultado é uma string base64 válida
        self.assertTrue(len(result) > 0, "PDF vazio retornado")
        
        # Tentar salvar o PDF
        import base64
        pdf_path = 'app/uploads/teste.pdf'
        with open(pdf_path, 'wb') as f:
            f.write(base64.b64decode(result))
        
        # Verificar se o arquivo foi criado
        self.assertTrue(os.path.exists(pdf_path), "PDF não foi salvo")
        self.assertTrue(os.path.getsize(pdf_path) > 0, "PDF salvo está vazio")

if __name__ == "__main__":
    unittest.main() 