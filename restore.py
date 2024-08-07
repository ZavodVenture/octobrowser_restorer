from configparser import ConfigParser
from entities import Config, Error, Wallet

config = ConfigParser()
config.read('config.ini')
config_object = Config(**config['settings'])

import colorama
from webdriver_manager.chrome import ChromeDriverManager
from colorama import Fore
from helpers import reader, octobrowser, chunks, worker
from time import sleep
from progress.bar import Bar
from typing import List
from threading import Thread


def init_exit():
    input('\nPress Enter to close the program...')
    exit()


def launch_profiles(uuid_list):
    bar = Bar('Launching', max=config_object.profiles_number)
    bar.start()

    ws_list = []

    for uuid in uuid_list:
        result = octobrowser.run_profile(uuid)

        if isinstance(result, Error):
            bar.finish()
            return result

        ws_list.append(result)
        bar.next()
        sleep(3)

    bar.finish()
    return ws_list


def setup_profiles(ws_list, wallet_list: List[Wallet]):
    profile_tuple = [(ws_list[i], wallet_list[i]) for i in range(config_object.profiles_number)]
    profile_tuple = chunks(profile_tuple, config_object.thread_number)

    ChromeDriverManager(config_object.driver_version).install()

    bar = Bar('Configuring', max=config_object.profiles_number)

    bar.start()

    for group in profile_tuple:
        threads = []
        for profile in group:
            ws, wallet = profile
            threads.append(Thread(target=worker, args=(ws, wallet, bar, config_object.metamask_password, config_object.driver_version)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    bar.finish()


def main():
    print('Pre-launch verification...\n')

    wallet_list = reader.read_wallets()
    if isinstance(wallet_list, Error):
        print(wallet_list)
        init_exit()

    profiles_list = octobrowser.get_profiles()
    if isinstance(profiles_list, Error):
        print(profiles_list)
        init_exit()

    if len(profiles_list) != len(wallet_list):
        print(Error('Wallet reading error', 'The number of wallets doesn\'t equals to number of profiles in tag'))
        init_exit()

    first_profile_index = None
    for profile in profiles_list:
        if profile['title'] == str(config_object.first_profile):
            first_profile_index = profiles_list.index(profile)

    if first_profile_index is None:
        print(Error('Getting profiles error', f'Couldn\'t find profile {config_object.first_profile}'))
        init_exit()

    profiles_list = profiles_list[first_profile_index:first_profile_index + config_object.profiles_number]
    wallet_list = wallet_list[first_profile_index:first_profile_index + config_object.profiles_number]

    if len(profiles_list) != config_object.profiles_number:
        print(Error('Getting profiles error', 'Wrong first_profile and profiles_number'))
        init_exit()

    print(f'{Fore.GREEN}Verification completed! Launching profiles...\n{Fore.RESET}')

    for i in range(len(profiles_list)):
        profiles_list[i] = profiles_list[i]['uuid']

    ws_list = launch_profiles(profiles_list)
    print()
    if isinstance(ws_list, Error):
        print(ws_list)
        init_exit()

    print(f'{Fore.GREEN}Profiles have been successfully launched! Starting the setup process...{Fore.RESET}\n')

    setup_profiles(ws_list, wallet_list)

    print(f'\n{Fore.GREEN}All profiles are ready! Check for errors on them.{Fore.RESET}')
    init_exit()


if __name__ == '__main__':
    colorama.init()
    main()
