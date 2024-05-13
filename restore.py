from configparser import ConfigParser
from entities import Config, Error, Wallet

config = ConfigParser()
config.read('config.ini')
config_object = Config(**config['settings'])

import colorama
from colorama import Fore
from helpers import reader, octobrowser, chunks, worker
from time import sleep
from progress.bar import Bar
from typing import List
from threading import Thread
import shutil
from random import sample
from string import ascii_letters


def init_exit():
    input('\nPress Enter to close the program...')
    exit()


def setup_profiles(uuid_list, keplr_name, wallet_list: List[Wallet]):
    bar = Bar('Configuring', max=config_object.profiles_number)
    bar.start()

    for i in range(len(uuid_list)):
        uuid = uuid_list[i]

        result = octobrowser.run_profile(uuid, keplr_name)
        if isinstance(result, Error):
            bar.finish()
            return result

        wallet = wallet_list[i]

        worker(result, wallet, bar, config_object.driver_version)

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

    keplr_name = ''.join(sample(ascii_letters, 10))
    shutil.copytree('keplr', keplr_name)

    for i in range(len(profiles_list)):
        profiles_list[i] = profiles_list[i]['uuid']

    print(f'{Fore.GREEN}Verification completed! Starting the setup process...\n{Fore.RESET}')

    result = setup_profiles(profiles_list, keplr_name, wallet_list)
    if isinstance(result, Error):
        print(result)
        init_exit()

    print(f'\n{Fore.GREEN}All profiles are ready! Check for errors on them.{Fore.RESET}')
    init_exit()


if __name__ == '__main__':
    colorama.init()
    main()
