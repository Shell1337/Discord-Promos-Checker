from colorama import Fore
from datetime import datetime
from threading import Thread, Lock
import tls_client, os, ctypes, time, random
from concurrent.futures import ThreadPoolExecutor, as_completed


class Stats:
    valid   = 0
    used    = 0
    invalid = 0
    error   = 0


class Console(object):
    def __init__(self) -> None:
        self.colors = {'red': Fore.RED, 'green': Fore.GREEN, 'yellow': Fore.YELLOW, 'blue': Fore.BLUE, 'magenta': Fore.MAGENTA, 'cyan': Fore.CYAN, 'white': Fore.WHITE, 'reset': Fore.RESET, 'bright_red': Fore.LIGHTRED_EX, 'bright_green': Fore.LIGHTGREEN_EX, 'bright_yellow': Fore.LIGHTYELLOW_EX, 'bright_blue': Fore.LIGHTBLUE_EX, 'bright_magenta': Fore.LIGHTMAGENTA_EX, 'bright_cyan': Fore.LIGHTCYAN_EX, 'bright_white': Fore.LIGHTWHITE_EX}


    def time(self) -> str:
        return datetime.now().strftime('%H:%M:%S')

    def clear(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def success(self, msg: str) -> None:
        print(f'{self.colors.get("cyan")}[{self.colors.get("white")}{self.time()}{self.colors.get("cyan")}] {self.colors.get("green")}[SUCC{self.colors.get("green")}] {self.colors.get("white")}{msg}{self.colors.get("reset")}')

    def error(self, msg: str) -> None:
        print(f'{self.colors.get("cyan")}[{self.colors.get("white")}{self.time()}{self.colors.get("cyan")}] {self.colors.get("red")}[ERRO{self.colors.get("red")}] {self.colors.get("white")}{msg}{self.colors.get("reset")}')

    def info(self, msg: str) -> None:
        print(f'{self.colors.get("cyan")}[{self.colors.get("white")}{self.time()}{self.colors.get("cyan")}] {self.colors.get("blue")}[INFO{self.colors.get("blue")}] {self.colors.get("white")}{msg}{self.colors.get("reset")}')

    def warning(self, msg: str) -> None:
        print(f'{self.colors.get("cyan")}[{self.colors.get("white")}{self.time()}{self.colors.get("cyan")}] {self.colors.get("yellow")}[WARN{self.colors.get("yellow")}] {self.colors.get("white")}{msg}{self.colors.get("reset")}')

    def input(self, msg: str) -> str:
        return input(f'{self.colors.get("cyan")}[{self.colors.get("white")}{self.time()}{self.colors.get("cyan")}] {self.colors.get("magenta")}[INPT{self.colors.get("magenta")}] {self.colors.get("white")}{msg}{self.colors.get("reset")}')
    
    def title(self, msg: str) -> None:
        ctypes.windll.kernel32.SetConsoleTitleW(msg)


class Checker(object):
    def __init__(self) -> None:
        self.folder_path = self.createCurrentFolder()
        self.lock   = Lock()
        self.client = tls_client.Session(client_identifier='chrome_120', random_tls_extension_order=True)


    def createCurrentFolder(self) -> str:
        folder_path = os.path.join(os.getcwd(), 'output', datetime.now().strftime('%d-%m-%Y__%H-%M-%S'))
        os.makedirs(folder_path, exist_ok=True)
        return folder_path


    def check(self, promo: str, proxies: list) -> None:
        try:
            _, code = promo.split('https://promos.discord.gg/') if "promos.discord.gg" in promo else promo.split('https://discord.com/billing/promotions/')
            self.client.proxies = {'http': f'http://{random.choice(proxies)}'}

            x = self.client.get(f'https://discord.com/api/v9/entitlements/gift-codes/{code}?country_code=US&with_application=false&with_subscription_plan=true')

            if '"uses"' in x.text:
                if x.json().get('uses') == 1:
                    with self.lock:
                        open(f'{self.folder_path}/used.txt', 'a+', encoding='utf-8').write(f'{promo}\n')
                        console.error(f"Used Promo Code: {promo[:-5]}***")
                        Stats.used += 1
                        console.title(f'Promo Checker | Valid: {Stats.valid} - Used: {Stats.used} - Invalid: {Stats.invalid} - Error: {Stats.error} | @homicide1337')
                        self.lock.release()
                        return False

                elif x.json().get('uses') == 0:
                    with self.lock:
                        open(f'{self.folder_path}/valid.txt', 'a+', encoding='utf-8').write(f'{promo}\n')
                        console.success(f"Valid Promo Code: {promo[:-5]}***")
                        Stats.valid += 1
                        console.title(f'Promo Checker | Valid: {Stats.valid} - Used: {Stats.used} - Invalid: {Stats.invalid} - Error: {Stats.error} | @homicide1337')
                        self.lock.release()
                        return True
                    
                elif x.json().get('message') == 'Unknown Gift Code':
                    with self.lock:
                        open(f'{self.folder_path}/invalid.txt', 'a+', encoding='utf-8').write(f'{promo}\n')
                        console.error(f"Invalid Promo Code: {promo[:-5]}***")
                        Stats.invalid += 1
                        console.title(f'Promo Checker | Valid: {Stats.valid} - Used: {Stats.used} - Invalid: {Stats.invalid} - Error: {Stats.error} | @homicide1337')
                        self.lock.release()
                        return False

                elif 'rate limited' in x.text.lower():
                    with self.lock:
                        console.info(f"Rate Limited: {promo[:-5]}*** | Sleeping for {x.json().get('retry_after')}s")
                        self.lock.release()
                        time.sleep(x.json().get('retry_after'))

                else:
                    with self.lock:
                        open(f'{self.folder_path}/error.txt', 'a+', encoding='utf-8').write(f'{promo}\n')
                        console.error(f"Unknown Error: {promo[:-5]}*** -> {x.text}")
                        Stats.error += 1
                        console.title(f'Promo Checker | Valid: {Stats.valid} - Used: {Stats.used} - Invalid: {Stats.invalid} - Error: {Stats.error} | @homicide1337')
                        self.lock.release()
                        return False

        except Exception as e:
            pass


def main():
    promos  = open('input/promos.txt', 'r', encoding='utf-8').read().splitlines()
    proxies = open('input/proxies.txt', 'r', encoding='utf-8').read().splitlines()

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(checker.check, promo, proxies) for promo in promos]
        for future in as_completed(futures):
            future.result()


if __name__ == '__main__':
    start   = time.time()
    console = Console()
    checker = Checker()
    console.clear()
    
    main()

    promos  = open('input/promos.txt', 'r', encoding='utf-8').read().splitlines()

    console.info(f"Checked {len(promos)} Promos in {time.time()-start} | Valid: {Stats.valid} - Used: {Stats.used} - Invalid: {Stats.invalid} - Error: {Stats.error} | @homicide1337")

    input()
