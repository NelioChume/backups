import paramiko
import json
import subprocess
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def backup_databases_in_containers():
    try:
        # Obtém nomes dos contêineres que têm o MySQL instalado e ativo
        containers_raw = subprocess.run(["lxc", "list", "--format", "json"], check=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        containers_data = json.loads(containers_raw.stdout.decode("utf-8"))
        containers = [container["name"] for container in containers_data if container["status"] == "Running"]

        # Diretório de destino para os backups
        backup_dir = "/home/nelio/bkTest"

        # Cria o diretório de backup se não existir
        os.makedirs(backup_dir, exist_ok=True)

        # Itera sobre a lista de contêineres e faz backup das bases de dados do usuário
        for container_name in containers:
            try:
                # Verifica se o MySQL está instalado e ativo
                subprocess.run(["lxc", "exec", container_name, "--", "systemctl", "is-active", "mysql"],
                               check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logging.info("----------------------------------------")
                logging.info(f"Fazendo backup de bases de dados no contêiner {container_name}...")

                # Lista as bases de dados do usuário
                user_databases_raw = subprocess.run(
                    ["lxc", "exec", container_name, "--", "mysql", "-sN", "-e", "SHOW DATABASES;"],
                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                user_databases = [db for db in user_databases_raw.stdout.decode("utf-8").split("\n") if db and
                                  db not in ['information_schema', 'mysql', 'performance_schema', 'sys']]

                # Faz backup de cada base de dados do usuário
                for db in user_databases:
                    current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
                    backup_file = os.path.join(backup_dir, f"bk_{db}_{current_datetime}.sql")
                    with open(backup_file, 'w') as f:
                        subprocess.Popen(["lxc", "exec", container_name, "--", "mysqldump", db], stdout=f,
                                         stderr=subprocess.PIPE, universal_newlines=True)
                    logging.info(f"Backup da base de dados {db} concluído. Arquivo: {backup_file}")

            except subprocess.CalledProcessError as e:
                pass

        logging.info("----------------------------------------")

    except subprocess.CalledProcessError:
        pass

def ssh_connect(command):
    # Cria uma instância do cliente SSH
    client = paramiko.SSHClient()

    with open('nodes.json') as file:
        servers = json.load(file)

    for server in servers:
        hostname = server['hostname']
        username = server['username']
        password = server['password']
        port = server['port']
        try:
            # Carrega as chaves do sistema (opcional, mas recomendado)
            client.load_system_host_keys()

            # Adiciona a chave do host automaticamente
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Conecta ao servidor SSH
            client.connect(hostname, port=port, username=username, password=password)

            # Exibe uma mensagem de sucesso
            print(f"Conexão SSH bem-sucedida para {hostname}!")

            # Executa o comando no servidor remoto
            stdin, stdout, stderr = client.exec_command(command)

            # Exibe a saída do comando
            print(f"Saída do comando '{command}':")
            print(stdout.read().decode())

        except Exception as e:
            # Exibe uma mensagem de erro se a conexão falhar
            print(f"Erro na conexão SSH para {hostname}: {str(e)}")

        finally:
            client.close()

def main():
    comando = backup_databases_in_containers()
    ssh_connect(comando)


if __name__ == "__main__":
    main()
