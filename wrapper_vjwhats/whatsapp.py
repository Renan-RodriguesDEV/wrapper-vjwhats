"""
Este módulo utiliza Selenium para interagir com o WhatsApp Web.

Última atualização: 24 de dezembro de 2025

Criado por: Renan Rodrigues (https://github.com/Renan-RodriguesDEV)
"""

import datetime
import os
from time import sleep

import pyperclip
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .elements import Elements
from .logger import setup_logger

logger = setup_logger("whatsapp_logger")


class WhatsApp:
    """
    Classe responsável por interagir com o WhatsApp Web via Selenium.

    Atributos:
        BASE_URL (str): URL base do WhatsApp Web.
        browser: Instância do Selenium WebDriver ativa.
        wait: Objeto WebDriverWait com tempo limite padrão.
        wait_img: WebDriverWait com tempo reduzido para operações com imagens.
        mobile (str): Número de telefone atualmente em uso.
    """

    def __init__(self, browser: WebDriver = None, time_out=300):
        """
        Inicializa a instância do WhatsApp.

        Args:
            browser: Instância do Selenium WebDriver.
            time_out (int): Tempo limite em segundos utilizado pelo WebDriverWait.
        """
        self.BASE_URL = "https://web.whatsapp.com/"
        self.browser = browser
        self.responses = {
            1: "Message sent successfully",
            2: "Failed to send the message",
            3: "An error occurred while trying to send the message",
            4: "The number is not registered on WhatsApp",
        }
        # self.browser.implicitly_wait(30)
        self.wait = WebDriverWait(self.browser, time_out)
        self.wait_img = WebDriverWait(self.browser, 10)
        self.wait_contact = WebDriverWait(self.browser, 30)
        self.login()
        self.mobile = ""

    def login(self):
        """
        Abre o WhatsApp Web e maximiza a janela do navegador.
        """
        self.browser.get(self.BASE_URL)
        self.browser.maximize_window()

    def catch_alert(self, seconds: int = 3):
        """
        Trata diálogos de alerta.

        Args:
            seconds (int): Tempo em segundos para aguardar o aparecimento do alerta.

        Returns:
            bool: True se um alerta estiver presente, False caso contrário.
        """
        try:
            WebDriverWait(self.browser, seconds).until(EC.alert_is_present())
            self.browser.switch_to.alert.accept()
            return True
        except Exception as e:
            logger.error(f"An exception occurred: {e}")
            return False

    def send_message(self, message: str) -> str:
        """
        Envia uma mensagem para o chat atual.

        Args:
            message (str): Texto que será enviado.

        Returns:
            str: Código de status indicando o resultado da operação.
        """
        try:
            # Define os XPaths da caixa de texto e do botão de número não encontrado
            inp_xpath = Elements.INPUT_MESSAGE  # UPDT 08-08
            nr_not_found_xpath = (
                Elements.NR_NOT_FOUND  # UPDT 08-08
            )
            # Aguarda até que apareça a caixa de texto OU o botão de erro
            elements = self.wait.until(
                lambda ctrl_self: ctrl_self.find_elements(By.XPATH, nr_not_found_xpath)
                or ctrl_self.find_elements(By.XPATH, inp_xpath)
            )
            # Percorre os elementos encontrados para identificar qual apareceu
            element = elements[0] if elements else None
            if element:
                # Se for a caixa de texto, envia a mensagem
                if element.aria_role == "textbox":
                    # Copia a mensagem para a área de transferência
                    pyperclip.copy(message)
                    # Simula Ctrl+V para colar a mensagem (melhor compatibilidade com emojis)
                    ActionChains(self.browser).key_down(Keys.CONTROL).send_keys(
                        "v"
                    ).key_up(Keys.CONTROL).perform()

                    sleep(1)
                    # Pressiona Enter para enviar a mensagem
                    element.send_keys(Keys.ENTER)
                    msg = 1  # Código de sucesso
                    sleep(2.5)
                    # Tenta capturar algum alerta que possa aparecer
                    self.catch_alert()
                # Se for um botão (erro de número não encontrado)
                elif element.aria_role == "button":
                    if element.text == "OK":
                        # Fecha o alerta de erro
                        element.send_keys(Keys.ENTER)
                        msg = 4  # Código de número inválido
        except (NoSuchElementException, Exception) as bug:
            # Registra qualquer erro que ocorrer
            logger.error(f"An exception occurred: {bug}")
            msg = 3  # Código de erro genérico
        finally:
            # Sempre registra o código final e retorna
            logger.info(f"{msg}")
            return self.responses.get(msg, "Unknown status code")

    def find_attachment(self):
        """
        Clica no botão de anexar arquivos do chat.
        """
        clipButton = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, Elements.ATTACHMENT_BUTTON)
            )  # novo XPath UPDT 19-09-2025
        )
        clipButton.click()

    def send_file(self, attachment: str, which: int, caption: str = None):
        """
        Envia um arquivo pelo chat.

        Args:
            attachment (str): Caminho do arquivo a ser enviado.
            which (int): Tipo do arquivo (1 documento, 2 imagem/vídeo).
        """
        response = 0
        logger.info(f"Sending file: {attachment}")
        try:
            filename = os.path.abspath(attachment)
            if caption:
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, Elements.INPUT_MESSAGE))
                ).click()
                pyperclip.copy(caption)
                ActionChains(self.browser).key_down(Keys.CONTROL).send_keys("v").key_up(
                    Keys.CONTROL
                ).perform()
            self.find_attachment()

            if which == 1:
                logger.info("Sending a document...")
                xpath = Elements.ALL_INPUT_FILE
                try:
                    WebDriverWait(self.browser, 5000).until(
                        EC.element_to_be_clickable((By.XPATH, Elements.DOCUMENT_BUTTON))
                    ).click()
                    logger.info("Clicked on Documento button.")
                except Exception as e:
                    logger.error(f"Error clicking on Documento: {e}")
            elif which == 2:
                logger.info("Sending an image or video...")
                xpath = Elements.IMAGE_INPUT_FILE
                try:
                    WebDriverWait(self.browser, 5000).until(
                        EC.element_to_be_clickable((By.XPATH, Elements.IMAGE_BUTTON))
                    ).click()
                    logger.info("Clicked on Image button.")
                except Exception as e:
                    logger.error(f"Error clicking on Image: {e}")

            sendButton = self.wait.until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            sendButton.send_keys(filename)
            sleep(2)
            self.send_attachment()
            sleep(5)
            response = 1
            logger.info(f"Attachment has been successfully sent to {self.mobile}")
        except (NoSuchElementException, Exception) as bug:
            response = 2
            logger.error(f"Failed to send a message to {self.mobile} - {bug}")
        finally:
            logger.info("send_file() finished running!")
            return self.responses.get(response, "Unknown status code")

    def send_attachment(self):
        """
        Aciona o botão de envio para concluir o anexo.
        """
        self.wait.until_not(
            EC.presence_of_element_located((By.XPATH, Elements.SENDING_MESSAGE_CLOCK))
        )
        sendButton = self.wait.until(
            EC.presence_of_element_located((By.XPATH, Elements.SEND_BUTTON))
        )
        # TODO:Descomentar se quiser fechar a pré-visualização antes de enviar, apenas para testes sem envios
        # ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
        sendButton.click()
        sleep(2)
        self.wait.until_not(
            EC.presence_of_element_located((By.XPATH, Elements.SENDING_MESSAGE_CLOCK))
        )

    def get_images_sent(self, limit_images: int = 0):
        """
        Recupera e baixa as imagens enviadas hoje no chat atual.
        """
        n_images = 0
        try:
            # Seleciona e clica em "Dados do perfil" para acessar as mídias
            dadosButton = self.wait.until(
                EC.presence_of_element_located((By.XPATH, Elements.DATA_PROFILE_BUTTON))
            )
            dadosButton.click()
            logger.info(
                'Data profile button clicked, waiting for "Mídia, links e docs" button...'
            )
            # Aguarda o carregamento do botão de mídia, links e documentos. E clica nele
            dadosButton = self.wait.until(
                EC.presence_of_element_located((By.XPATH, Elements.MEDIA_DOCS))
            )
            dadosButton.click()
            logger.info(
                '"Mídia, links e docs" button clicked, waiting for media list to load...'
            )

            # Aguarda o carregamento da lista de mídias carregadas com "Neste mês"
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, Elements.THIS_MONTH))
            )
            logger.info("Media list loaded, waiting for the first image to appear...")

            # Verifica se a primeira imagem está presente
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, Elements.FIRST_IMAGE))
            )
            # Verifica se a primeira imagem está visível
            self.wait.until(
                EC.element_to_be_clickable((By.XPATH, Elements.FIRST_IMAGE))
            )
            sleep(5)
            # Clica na primeira imagem para abrir a visualização
            self.browser.find_elements(By.XPATH, Elements.IMAGE_SELECTOR)[0].click()
            logger.info("First image clicked, waiting for the image view to load...")

            # Adiciona espera explícita para garantir que a visualização carregou
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, Elements.DOWNLOAD_BUTTON))
            )
            # btn de anterior
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, Elements.NEXT_IMAGE_BUTTON))
            )
            sleep(2)  # Espera adicional para garantir

            # Loop para baixar as imagens
            while True:
                logger.info(f"Processing image {n_images}...")

                # Verifica se o elemento de imagens está presente
                images = self.wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, Elements.IMAGE_LIST))
                )
                # Se não houver imagens, encerra o loop
                if len(images) == 0:
                    logger.warning("No images found in the media list.")
                    break
                btn_anterior = self.browser.find_element(
                    By.XPATH, Elements.NEXT_IMAGE_BUTTON
                )

                # Verifica se o botão está desativado; caso esteja, encerra o loop porque a lista acabou
                if btn_anterior.get_attribute("aria-disabled") == "true":
                    logger.warning("O botão 'Anterior' está DESATIVADO.")
                    break
                try:
                    # Aguarda o carregamento do texto "Hoje às" na imagem
                    self.wait_img.until(
                        EC.presence_of_element_located((By.XPATH, Elements.HAS_TODAY))
                    )
                    logger.info(f'Text "Hoje às" found in image {n_images}')
                    # Clica no botão de download
                    downloadButton = self.wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, Elements.DOWNLOAD_BUTTON)
                        )
                    )
                    downloadButton.click()
                    logger.info(
                        f"Image {n_images} downloaded successfully.",
                    )
                    # Passa para a próxima imagem
                    nextButton = self.wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, Elements.NEXT_IMAGE_BUTTON)
                        )
                    )
                    nextButton.click()
                    n_images += 1
                    if limit_images != 0 and n_images >= limit_images:
                        logger.info(f"Limite de {limit_images} imagens alcançado.")
                        break
                    sleep(0.5)
                except TimeoutException:
                    logger.error(f'Text "Hoje às" not found in image {n_images}')
                    break

            logger.info("All images have been processed.")
            # Saindo da visualização de imagens
            self.browser.find_element(By.XPATH, Elements.CLOSE_BUTTON).click()
            conversas = self.browser.find_element(
                By.XPATH, Elements.CONVERSATIONS_BUTTON
            )
            # Voltando para a tela principal
            for _ in range(2):
                conversas.send_keys(Keys.ESCAPE)
                logger.info("Returning to the main screen...")
                sleep(0.5)
        except Exception as err:
            logger.error(f"An exception occurred: {str(err)}")
            timestemp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.browser.save_screenshot(f"logs/error_{timestemp}.png")
        finally:
            return n_images

    def clear_search_box(self):
        """
        Limpa o campo de busca usado para procurar contatos ou mensagens.
        """
        search_box_xpath = (
            Elements.SEARCH_BOX_EDIT  # UPDT 08-08
        )
        search_box = self.wait.until(
            EC.presence_of_element_located((By.XPATH, search_box_xpath))
        )
        search_box.click()
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.BACKSPACE)

    def find_by_username(self, username: str) -> bool:
        """
        Localiza um contato pelo nome ou número.

        Args:
            username (str): Nome ou número que será pesquisado.

        Returns:
            bool: True se o contato for encontrado, False caso contrário.
        """
        search_box = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, Elements.SEARCH_BOX)
            )  ## UPDT 08-08
        )
        self.clear_search_box()
        search_box.send_keys(username)
        search_box.send_keys(Keys.ENTER)
        try:
            opened_chat = self.wait.until(
                EC.presence_of_element_located((By.XPATH, Elements.DATA_PROFILE_BUTTON))
            )
            if opened_chat:
                logger.info(f'Successfully fetched chat "{username}"')
                return True
        except NoSuchElementException:
            logger.error(f'It was not possible to fetch chat "{username}"')
            return False

    def start_conversation(self, mobile: str):
        """
        Tenta abrir uma nova conversa com o número informado. Expira após 30 segundos.

        Args:
            mobile (str): Número que será pesquisado.

        Returns:
            bool: True se o contato for encontrado, False caso contrário.
        """

        self.browser.get(
            f"https://web.whatsapp.com/send?phone={mobile}&text&type=phone_number&app_absent=1"
        )

        try:
            opened_chat = self.wait_contact.until(
                EC.presence_of_element_located((By.XPATH, Elements.DATA_PROFILE_BUTTON))
            )
            if opened_chat:
                logger.info(f'Successfully fetched chat "{mobile}"')
                return True
        except NoSuchElementException:
            logger.error(f'It was not possible to fetch chat "{mobile}"')
            return False
