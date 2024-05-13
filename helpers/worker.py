from entities import Wallet, Error
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service
from progress.bar import Bar
from time import sleep
from restore import config_object
from random import sample
from string import ascii_letters, digits
from webdriver_manager.chrome import ChromeDriverManager
import sys


def open_success_page(driver: webdriver.Chrome):
    driver.get('about:blank')
    script = '''let div = document.createElement("div");
div.textContent = "Profile is ready!";
div.style.fontSize = "36px";
div.style.fontWeight = "bold";
div.style.color = "green";
div.style.position = "absolute";
div.style.top = "50%";
div.style.left = "50%";
div.style.transform = "translate(-50%, -50%)";
document.body.appendChild(div);'''
    driver.execute_script(script)


def open_error_page(driver: webdriver.Chrome, error):
    driver.get('about:blank')
    script = f'''let div = document.createElement("div");
div.textContent = "An error occurred! {error}";
div.style.fontSize = "36px";
div.style.fontWeight = "bold";
div.style.color = "red";
div.style.position = "absolute";
div.style.top = "50%";
div.style.left = "50%";
div.style.transform = "translate(-50%, -50%)";
document.body.appendChild(div);'''
    driver.execute_script(script)


def get_exts(driver):
    driver.get('chrome://extensions/')

    sleep(5)

    script = '''ext_manager = document.getElementsByTagName('extensions-manager')[0].shadowRoot;
    item_list = ext_manager.getElementById('items-list').shadowRoot;
    container = item_list.getElementById('container');
    extension_list = container.getElementsByClassName('items-container')[1].getElementsByTagName('extensions-item');

    var extensions = [];

    for (i = 0; i < extension_list.length; i++) {
        console.log(extension_list[i]);
        name = extension_list[i].shadowRoot.getElementById('name').textContent;
        id = extension_list[i].id;
        extensions.push({'id': id, 'name': name});
    }

    return extensions;'''

    return driver.execute_script(script)


def import_new(driver, wallet):
    WebDriverWait(driver, 5).until(
        ec.element_to_be_clickable((By.XPATH, '//*[@id="onboarding__terms-checkbox"]'))).click()
    WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="onboarding-import-wallet"]'))).click()
    WebDriverWait(driver, 1)
    WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="metametrics-i-agree"]'))).click()

    WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.ID, 'import-srp__srp-word-0')))

    seed = wallet.seed_phrase.split(' ')

    if len(seed) != 12:
        open_error_page(driver, Error('Seed length error', 'The length of one of the seed-phrases is not equal to 12'))
        return

    for j in range(12):
        driver.find_element(By.ID, f'import-srp__srp-word-{j}').send_keys(seed[j])

    WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="import-srp-confirm"]'))).click()

    password = config_object.metamask_password if config_object.metamask_password else ''.join(
        sample(ascii_letters + digits, 30))

    WebDriverWait(driver, 20).until(
        ec.presence_of_element_located((By.XPATH, '//input[@data-testid="create-password-new"]'))).send_keys(password)
    WebDriverWait(driver, 20).until(
        ec.presence_of_element_located(((By.XPATH, '//input[@data-testid="create-password-confirm"]')))).send_keys(
        password)
    WebDriverWait(driver, 20).until(
        ec.presence_of_element_located((By.XPATH, '//input[@data-testid="create-password-terms"]'))).click()

    WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="create-password-import"]'))).click()

    driver.implicitly_wait(5)

    while 1:
        try:
            sleep(5)
            driver.find_element(By.XPATH, '//div[@class="loading-overlay"]')
        except:
            break
        else:
            driver.refresh()
            continue

    WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="onboarding-complete-done"]'))).click()
    WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="pin-extension-next"]'))).click()
    WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable((By.XPATH, '//button[@data-testid="pin-extension-done"]'))).click()


def import_metamask(driver, wallet):
    try:
        metamask_id = [i['id'] for i in get_exts(driver) if 'MetaMask' in i['name']][0]
    except IndexError:
        raise 'No metamask'

    driver.get(f'chrome-extension://{metamask_id}/home.html')

    sleep(3)
    driver.refresh()

    try:
        WebDriverWait(driver, 5).until(
            ec.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div[3]/a'))).click()
    except:
        import_new(driver, wallet)
        return

    sleep(1)

    split = wallet.seed_phrase.split(' ')

    if len(split) != 12:
        open_error_page(driver, Error('Seed length error', 'The length of one of the seed-phrases is not equal to 12'))
        return

    for index in range(12):
        driver.find_element(By.ID, f'import-srp__srp-word-{index}').send_keys(split[index])

    password = config_object.metamask_password if config_object.metamask_password else ''.join(
        sample(ascii_letters + digits, 30))

    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="confirm-password"]').send_keys(password)

    WebDriverWait(driver, 30).until(
        ec.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/form/button'))).click()

    sleep(3)


def import_keplr(driver, wallet):
    try:
        extensions = get_exts(driver)

        try:
            martin_id = [ex['id'] for ex in extensions if 'Keplr' in ex['name']][0]
        except IndexError:
            raise Exception('Keplr extension not found')

        driver.get(f'chrome-extension://{martin_id}/register.html')

        WebDriverWait(driver, 20).until(ec.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div/div/div/div[3]/div[3]/button'))).click()
        WebDriverWait(driver, 20).until(ec.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div[2]/div/div/div/div[1]/div/div[5]/button'))).click()
        WebDriverWait(driver, 20).until(ec.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div[3]/div/div/form/div[3]/div/div/div[1]//input')))

        sleep(2)

        inputs = driver.find_elements(By.XPATH,
                                      '//*[@id="app"]/div/div[2]/div/div/div[3]/div/div/form/div[3]/div/div/div[1]//input')

        seed = wallet.seed_phrase.split(' ')

        for j in range(12):
            inputs[j].send_keys(seed[j])

        WebDriverWait(driver, 20).until(ec.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div[3]/div/div/form/div[6]/div/button'))).click()

        inp = WebDriverWait(driver, 20).until(ec.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div[4]/div/div/form/div/div[1]/div[2]/div/div/input')))
        sleep(2)
        inp.send_keys('Wallet')

        meta_password = config_object.metamask_password if config_object.metamask_password else ''.join(
            sample(ascii_letters + digits, 30))

        WebDriverWait(driver, 20).until(ec.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div[4]/div/div/form/div/div[3]/div[2]/div/div/input'))).send_keys(
            meta_password)
        WebDriverWait(driver, 20).until(ec.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div[4]/div/div/form/div/div[5]/div[2]/div/div/input'))).send_keys(
            meta_password)

        WebDriverWait(driver, 20).until(ec.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div[4]/div/div/form/div/div[7]/button'))).click()
        WebDriverWait(driver, 60).until(ec.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div/div/div/div[9]/div/button'))).click()

        driver.get('about:blank')
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        line_number = exc_traceback.tb_lineno
        raise Exception(f'error on {line_number}')


def worker(ws, wallet: Wallet, bar: Bar, version=None):
    try:
        options = Options()
        options.add_experimental_option("debuggerAddress", f'127.0.0.1:{ws}')
        ver = version if version else '120.0.6099.71'
        service = Service(executable_path=ChromeDriverManager(ver).install())
        driver = webdriver.Chrome(options=options, service=service)

        tabs = driver.window_handles
        curr = driver.current_window_handle
        for tab in tabs:
            if tab == curr:
                continue
            driver.switch_to.window(tab)
            driver.close()
        driver.switch_to.window(curr)
        driver.get('about:blank')

        import_metamask(driver, wallet)
        import_keplr(driver, wallet)

        open_success_page(driver)
    except Exception as e:
        print(e)
    finally:
        bar.next()
