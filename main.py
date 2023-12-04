import paramiko
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

LOGS_PATH = os.getenv('LOGS_PATH')

def check_mysql_status(ssh, container_name):
    # Comando para verificar o status do MySQL no contêiner
    command = f"sudo lxc exec {container_name} -- systemctl is-active mysql"
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    # 0 indica que o MySQL está ativo, outros valores indicam inatividade ou erro
    return exit_status == 0

def execute_mysql_checks(ssh, container_name, hostname):
    # Verifica o status do MySQL no contêiner
    mysql_active = check_mysql_status(ssh, container_name)

    # Realiza ação com base no status do MySQL
    if mysql_active:
        print(f"MySQL está ativo no contêiner {container_name}.")
        # Adicione aqui a lógica específica que deseja executar quando o MySQL está ativo.
    else:
        print(f"MySQL não está ativo no contêiner {container_name}.")
        # Adicione aqui a lógica específica que deseja executar quando o MySQL não está ativo.

def get_container_names(ssh):
    # Comando para obter a lista de contêineres em formato JSON
    command = "sudo lxc list --format=json"
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    # Se o comando foi bem-sucedido, analisa a lista de contêineres
    if exit_status == 0:
        containers = json.loads(stdout.read().decode())
        running_containers = [container["name"] for container in containers if container["status"].lower() == "running"]
        excluded_containers = ["postgres", "monitor", "proxy"]
        container_names = [container_name for container_name in running_containers if container_name not in excluded_containers]
        return container_names
    else:
        return []

def main():
    # Leitura dos objetos/servidores em nodes.json
    with open('nodes.json') as file:
        servers = json.load(file)

    for server in servers:
        hostname = server['hostname']
        username = server['username']
        password = server['password']
        port = server['port']

        # Conexão SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname, port=port, username=username, password=password)
            print(f"Conectado com sucesso ao servidor {hostname}")
        except paramiko.AuthenticationException as e:
            print(f"Falha na autenticação do servidor {hostname}: {str(e)}")
            log_file_path = os.path.join(LOGS_PATH, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"Erro ao autenticar no servidor {hostname}: {str(e)}\n")
            continue

        # Leitura dos nomes dos contêineres
        container_names = get_container_names(ssh)

        # Execução de verificações MySQL para cada contêiner
        for container_name in container_names:
            execute_mysql_checks(ssh, container_name, hostname)

        # Termino da sessão
        ssh.close()

if __name__ == "__main__":
    main()