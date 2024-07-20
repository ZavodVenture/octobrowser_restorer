from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from entities import Wallet
from random import sample
from string import ascii_letters, digits
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from sys import exc_info


def get_extensions(driver: webdriver.Chrome):
    try:
        driver.get('chrome://extensions/')

        script = '''ext_manager = document.getElementsByTagName('extensions-manager')[0].shadowRoot;
        item_list = ext_manager.getElementById('items-list').shadowRoot;
        container = item_list.getElementById('container');
        extension_list = container.getElementsByClassName('items-container')[1].getElementsByTagName('extensions-item');

        var extensions = {};

        for (i = 0; i < extension_list.length; i++) {
            console.log(extension_list[i]);
            name = extension_list[i].shadowRoot.getElementById('name').textContent;
            id = extension_list[i].id;
            extensions[name] = id;
        }

        return extensions;'''

        return driver.execute_script(script)
    except:
        exc_type, exc_value, exc_tb = exc_info()
        raise Exception(f'Can\'t get extensions list: exception at {exc_tb.tb_lineno}')


# koshminvlad@gmail.com
# 4SApW!j87MDPMWi


def get_metamask_status(driver: webdriver.Chrome, metamask_id):
    driver.get(f'chrome-extension://{metamask_id}/home.html')

    try:
        WebDriverWait(driver, 10).until(ec.url_changes(f'chrome-extension://{metamask_id}/home.html'))
    except TimeoutException:
        driver.get('about:blank')
        return 'unlocked'

    current_url = driver.current_url

    if 'unlock' in current_url:
        return 'locked'
    elif 'onboarding' in current_url:
        return 'new'
    else:
        raise Exception('Can\'t receive metamask state')


def import_metamask(driver: webdriver.Chrome, wallet: Wallet, password, metamask_id):
    try:
        driver.get(f'chrome-extension://{metamask_id}/home.html#onboarding/welcome')

        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//input[@data-testid="onboarding-terms-checkbox"]'))).click()
        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="onboarding-import-wallet"]'))).click()

        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="metametrics-no-thanks"]'))).click()

        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//input[@data-testid="import-srp__srp-word-0"]')))

        seed = wallet.seed_phrase.split(' ')

        for i in range(12):
            driver.find_element(By.XPATH, f'//input[@data-testid="import-srp__srp-word-{i}"]').send_keys(seed[i])

        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="import-srp-confirm"]'))).click()

        WebDriverWait(driver, 15).until(ec.element_to_be_clickable((By.XPATH, '//input[@data-testid="create-password-new"]'))).send_keys(password)
        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//input[@data-testid="create-password-confirm"]'))).send_keys(password)
        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//input[@data-testid="create-password-terms"]'))).click()
        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="create-password-import"]'))).click()

        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="onboarding-complete-done"]'))).click()
        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="pin-extension-next"]'))).click()
        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="pin-extension-done"]'))).click()

        sleep(1)

        driver.get('about:blank')
    except Exception as e:
        exc_type, exc_value, exc_tb = exc_info()
        raise Exception(f'Can\'t import metamask: exception at {exc_tb.tb_lineno}')


def restore_metamask(driver: webdriver.Chrome, wallet: Wallet, password, metamask_id):
    try:
        driver.get(f'chrome-extension://{metamask_id}/home.html#onboarding/unlock')

        WebDriverWait(driver, 15).until(ec.element_to_be_clickable((By.XPATH, '//a[@class="button btn-link unlock-page__link"]'))).click()

        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//input[@data-testid="import-srp__srp-word-0"]')))

        seed = wallet.seed_phrase.split(' ')

        for i in range(12):
            driver.find_element(By.XPATH, f'//input[@data-testid="import-srp__srp-word-{i}"]').send_keys(seed[i])

        url_before = driver.current_url

        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//input[@data-testid="create-vault-password"]'))).send_keys(password)
        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//input[@data-testid="create-vault-confirm-password"]'))).send_keys(
            password)
        WebDriverWait(driver, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="create-new-vault-submit-button"]'))).click()

        WebDriverWait(driver, 60).until(ec.url_changes(url_before))

        driver.get('about:blank')
    except:
        exc_type, exc_value, exc_tb = exc_info()
        raise Exception(f'Can\'t restore metamask: exception at {exc_tb.tb_lineno}')


def close_all_tabs(driver: webdriver.Chrome):
    try:
        try:
            WebDriverWait(driver, 15).until_not(ec.number_of_windows_to_be(1))
        except:
            pass

        windows = driver.window_handles
        for window in windows:
            driver.switch_to.window(window)
            if 'offscreen.html' in driver.current_url:
                driver.close()
        driver.switch_to.window(driver.window_handles[0])

        driver.switch_to.new_window()
        current = driver.current_window_handle
        windows = driver.window_handles
        windows.remove(current)

        for window in windows:
            driver.switch_to.window(window)
            driver.close()

        driver.switch_to.window(current)
        driver.get('about:blank')
    except Exception as e:
        exc_type, exc_value, exc_tb = exc_info()
        raise Exception(f'Can\'t close tabs: {type(e)} at {exc_tb.tb_lineno}')


def worker(ws, wallet: Wallet, bar, password, version):
    try:
        options = Options()
        options.add_experimental_option("debuggerAddress", f'127.0.0.1:{ws}')
        service = Service(executable_path=ChromeDriverManager(version).install())
        driver = webdriver.Chrome(options=options, service=service)

        try:
            driver.maximize_window()
        except:
            pass

        close_all_tabs(driver)

        metamask_id = get_extensions(driver).get('MetaMask')
        if not metamask_id:
            raise Exception('Can\'t find metamask id')

        password = password if password else ''.join(sample(ascii_letters + digits, 15))

        metamask_state = get_metamask_status(driver, metamask_id)

        if metamask_state == 'unlocked':
            driver.get('about:blank')
            return
        elif metamask_state == 'locked':
            restore_metamask(driver, wallet, password, metamask_id)
        elif metamask_state == 'new':
            import_metamask(driver, wallet, password, metamask_id)
    except Exception as e:
        print(e)
    finally:
        bar.next()
