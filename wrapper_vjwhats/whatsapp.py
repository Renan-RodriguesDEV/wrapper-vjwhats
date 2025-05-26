"""
whatsapp.py
Este módulo fornece a classe WhatsApp para automatizar interações com o WhatsApp Web utilizando Selenium WebDriver.
Funcionalidades principais:
- Inicialização e autenticação automática no WhatsApp Web.
- Envio de mensagens de texto para contatos ou grupos.
- Envio de arquivos (documentos, imagens, vídeos) via chat.
- Download de imagens enviadas no chat no dia atual.
- Busca e seleção de contatos por nome ou número.
- Limpeza de mensagens de um contato específico.
- Manipulação de alertas e elementos da interface do WhatsApp Web.
A classe WhatsApp encapsula métodos robustos para manipulação da interface web, tornando possível a automação de tarefas rotineiras no WhatsApp para integrações, bots ou sistemas de atendimento automatizado.
Requisitos:
- selenium
- Um driver compatível com o navegador (ex: chromedriver)

"""

# wrapper_vjwhats/whatsapp.py

import os
import random
import logging
from time import sleep
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver

LOGGER = logging.getLogger()


class WhatsApp:
    """
    A class to interact with WhatsApp Web using Selenium.

    Attributes:
        BASE_URL (str): The base URL for WhatsApp Web.
        browser: The Selenium WebDriver instance.
        wait: WebDriverWait instance with a timeout.
        wait_img: WebDriverWait instance with a shorter timeout for image operations.
        mobile (str): The mobile number currently being interacted with.
    """

    def __init__(self, browser: WebDriver = None, time_out=600):
        """
        Initialize the WhatsApp instance.

        Args:
            browser: The Selenium WebDriver instance.
            time_out (int): Timeout for WebDriverWait, in seconds.
        """
        self.BASE_URL = "https://web.whatsapp.com/"
        self.browser = browser
        self.wait = WebDriverWait(self.browser, time_out)
        self.wait_img = WebDriverWait(self.browser, 5)
        self.wait_contact = WebDriverWait(self.browser, 30)
        self.cli()
        self.login()
        self.mobile = ""

    def cli(self):
        """
        Configure the logger for command line interface.
        """
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s -- [%(levelname)s] >> %(message)s"
            )
        )
        LOGGER.addHandler(handler)
        LOGGER.setLevel(logging.INFO)

    def login(self):
        """
        Open WhatsApp Web and maximize the browser window.
        """
        self.browser.get(self.BASE_URL)
        self.browser.maximize_window()

    def catch_alert(self, seconds=3):
        """
        Handle alert dialogs.

        Args:
            seconds (int): Time to wait for an alert to appear, in seconds.

        Returns:
            bool: True if an alert was present, False otherwise.
        """
        try:
            WebDriverWait(self.browser, seconds).until(EC.alert_is_present())
            alert = self.browser.switch_to.alert.accept()
            return True
        except Exception as e:
            LOGGER.exception(f"An exception occurred: {e}")
            return False

    def send_message(self, message: str) -> str:
        """
        Send a message to the current chat.

        Args:
            message (str): The message to send.

        Returns:
            str: Status code indicating the result of the operation.
        """
        try:
            inp_xpath = "//div[@aria-placeholder='Digite uma mensagem']"  # UPDT 08-08
            nr_not_found_xpath = (
                '//*[@id="app"]/div/span[2]/div/span/div/div/div/div/div/div[2]/div/div'
            )
            ctrl_element = self.wait.until(
                lambda ctrl_self: ctrl_self.find_elements(By.XPATH, nr_not_found_xpath)
                or ctrl_self.find_elements(By.XPATH, inp_xpath)
            )
            for i in ctrl_element:
                if i.aria_role == "textbox":
                    for line in message.split("\n"):
                        i.send_keys(line)
                        ActionChains(self.browser).key_down(Keys.SHIFT).key_down(
                            Keys.ENTER
                        ).key_up(Keys.ENTER).key_up(Keys.SHIFT).perform()
                    sleep(1)
                    i.send_keys(Keys.ENTER)
                    msg = "1"
                    sleep(2.5)
                    try:
                        self.catch_alert()
                    except:
                        pass
                elif i.aria_role == "button":
                    if i.text == "OK":
                        i.send_keys(Keys.ENTER)
                        msg = "4"
        except (NoSuchElementException, Exception) as bug:
            LOGGER.exception(f"An exception occurred: {bug}")
            msg = "3"
        finally:
            LOGGER.info(f"{msg}")
            return msg

    def find_attachment(self):
        """
        Click the attachment button in the chat.
        """
        clipButton = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@title="Anexar"]'))
        )
        clipButton.click()

    def send_file(self, attachment: Path, which: int):
        """
        Send a file in the chat.

        Args:
            attachment (Path): Path to the file to send.
            which (int): Type of file (1 for document, 2 for image/video).
        """
        print(f"Sending file: {attachment}")
        try:
            filename = os.path.realpath(attachment)
            self.find_attachment()

            if which == 1:
                xpath = "//input[@accept='*']"
            elif which == 2:
                xpath = (
                    "//input[@accept='image/*,video/mp4,video/3gpp,video/quicktime']"
                )

            sendButton = self.wait.until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            sendButton.send_keys(filename)

            sleep(2)
            self.send_attachment()
            sleep(5)
            LOGGER.info(f"Attachment has been successfully sent to {self.mobile}")
        except (NoSuchElementException, Exception) as bug:
            LOGGER.exception(f"Failed to send a message to {self.mobile} - {bug}")
        finally:
            LOGGER.info("send_file() finished running!")

    def send_attachment(self):
        """
        Click the send button to send the attachment.
        """
        self.wait.until_not(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')
            )
        )
        sendButton = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Enviar']"))
        )
        sendButton.click()
        sleep(2)
        self.wait.until_not(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')
            )
        )

    def get_images_sent(self, ultima_imagem: int = 1):
        """
        Retrieve and download images sent today in the current chat.
        """
        n_images = 0
        try:
            dadosButton = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@title='Dados de perfil']")
                )
            )
            dadosButton.click()

            dadosButton = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[text()='Mídia, links e docs']")
                )
            )
            dadosButton.click()

            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[text()='Neste mês']"))
            )

            # Pega a primeira imagem da lista usando o xpath fornecido
            firstImg = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "(//div[@aria-label=' Imagem'])[1]")
                )
            )
            sleep(20)  # Aguarda o carregamento da imagem
            firstImg.click()
            sleep(random.randint(5, 8))

            while True:
                element_imagens = "(//div[contains(@aria-label, 'Lista de mídias')]/div[@role='listitem'])"

                images = self.wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, element_imagens))
                )
                total_images = len(images)

                if total_images == 0:
                    break

                firstImgButton = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, f"{element_imagens}[1]"))
                )
                firstImgButton.click()
                btn_anterior = self.browser.find_element(
                    By.XPATH, "//div[@aria-label='Anterior']"
                )

                # Verifica se o botão está desativado ou ativado
                if btn_anterior.get_attribute("aria-disabled") == "true":
                    print("O botão 'Anterior' está DESATIVADO.")
                    break
                try:
                    self.wait_img.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//div[contains(text(), 'Hoje às')]")
                        )
                    )
                    print(
                        'Texto "Hoje às" encontrado na Imagem Principal, continuando...',
                        end="\r",
                    )

                except:
                    print(
                        'Texto "Hoje às" não encontrado na Imagem Principal, saindo do loop...',
                        end="\r",
                    )
                    break

            sleep(random.randint(5, 8))
            images = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, element_imagens))
            )
            total_images = len(images)
            # Limita o número de imagens a serem baixadas
            if ultima_imagem != 1:
                ultima_imagem = total_images - ultima_imagem

            for i in range(total_images, ultima_imagem, -1):
                try:
                    imgButton = self.wait_img.until(
                        EC.presence_of_element_located(
                            (By.XPATH, f"{element_imagens}[{i}]")
                        )
                    )
                    imgButton.click()

                    try:
                        self.wait_img.until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//div[contains(text(), 'Hoje às')]")
                            )
                        )
                        print(f'Texto "Hoje às" encontrado na imagem {i}', end="\r")

                        downloadButton = self.wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, f"//button[@aria-label='Baixar']")
                            )
                        )

                        downloadButton.click()
                        print(
                            f"Download concluído, imagens já baixadas: {n_images}",
                            end="\r",
                        )
                        n_images += 1
                        sleep(0.5)
                    except TimeoutException:
                        print(f'Texto "Hoje às" não encontrado na imagem {i}')
                        break

                except Exception as e:
                    print(f"Erro na posição {i}:", e)
                    break

            print("Processo concluído")
            # exiting the image view
            self.browser.find_element(
                By.XPATH, "//button[@aria-label='Fechar']"
            ).click()
            conversas = self.browser.find_element(
                By.XPATH, "//button[@aria-label='Conversas']"
            )
            # go back to the main screen
            for _ in range(2):
                conversas.send_keys(Keys.ESCAPE)
                print("Voltando para a tela principal", end="\r")
                sleep(0.5)
        except Exception as e:
            LOGGER.exception(f"An exception occurred: {e}")
        finally:
            return n_images

    def clear_search_box(self):
        """
        Clear the search box.

        The search box is used to search for contacts or messages.
        """
        search_box_xpath = (
            '(//div[@contenteditable="true" and @role="textbox"])[1]'  # UPDT 08-08
        )
        search_box = self.wait.until(
            EC.presence_of_element_located((By.XPATH, search_box_xpath))
        )
        search_box.click()
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.BACKSPACE)

    def find_by_username(self, username: str) -> bool:
        """
        Locate a contact by username or number.

        Args:
            username (str): The username or number to search for.

        Returns:
            bool: True if the contact was found, False otherwise.
        """
        search_box = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "(//*[@role='textbox'])[1]")
            )  ## UPDT 08-08
        )
        self.clear_search_box()
        search_box.send_keys(username)
        search_box.send_keys(Keys.ENTER)
        try:
            opened_chat = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@title='Dados de perfil']")
                )
            )
            if opened_chat:
                LOGGER.info(f'Successfully fetched chat "{username}"')
                return True
        except NoSuchElementException:
            LOGGER.exception(f'It was not possible to fetch chat "{username}"')
            return False

    def start_conversation(self, mobile: str):
        """
        Tries to open a new conversation with the given number. Runs out after 30 seconds if not found.

        Args:
            mobile (str): The number to search for.

        Returns:
            bool: True if the contact was found, False otherwise.
        """

        self.browser.get(
            f"https://web.whatsapp.com/send?phone={mobile}&text&type=phone_number&app_absent=1"
        )

        try:
            opened_chat = self.wait_contact.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@title='Dados de perfil']")
                )
            )
            if opened_chat:
                LOGGER.info(f'Successfully fetched chat "{mobile}"')
                return True
        except NoSuchElementException:
            LOGGER.exception(f'It was not possible to fetch chat "{mobile}"')
            return False

    def clear_messages(self, contact):
        """
        Clear all messages in the chat with the given contact.

        Args:
            contact (str): The contact to clear messages for.
        """
        self.find_by_username(contact)
        buttons = self.wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//button[@title='Mais opções']")
            )
        )
        if len(buttons) >= 2:
            buttons[1].click()
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[text()='Limpar conversa']")
            )
        ).click()
        # timeout for loading the confirmation button
        sleep(random.randint(2, 5))
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[text()='Limpar conversa']")
            )
        ).click()
        # timeout for loading the confirmation deletion of messages
        sleep(random.randint(5, 10))
        LOGGER.info(f"All messages from {contact} have been cleared.")
