import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Diretório onde os backups serão armazenados localmente e remotamente
local_backup_dir = os.getenv('LOCAL_BACKUP_DIR')
remote_backup_dir = os.getenv('REMOTE_BACKUP_DIR')

# Lista de containers LXC/LXD para excluir
excluded_containers = ["postgres", "monitor", "proxy"]

# Lista de bancos de dados MySQL para excluir
excluded_mysql_databases = ['information_schema', 'mysql', 'performance_schema', 'sys']

def backup_mysql_databases(container_name):
    try:
        output = subprocess.check_output(["lxc", "exec", container_name, "--", "bash", "-c",
                                          "mysql -e 'show databases;'"]).decode()
        databases = output.split("\n")[1:-1]  # Remove a primeira e a última linha

        for db in databases:
            if db not in excluded_mysql_databases:
                timestamp = datetime.now().strftime("%d-%m-%Y")
                backup_file = f"bk_{db}_{timestamp}.sql.gz"
                backup_path = os.path.join(local_backup_dir, backup_file)
                subprocess.run(["lxc", "exec", container_name, "--", "bash", "-c",
                                f"mysqldump {db} | gzip > {backup_path}"])
                print(f"Backup do banco de dados {db} concluído com sucesso.")
    except subprocess.CalledProcessError:
        print(f"Erro ao fazer backup do banco de dados no container {container_name}.")

def main():
    try:
        containers = subprocess.check_output(["lxc", "list", "--format", "csv", "--columns", "n"]).decode().split("\n")
        for container in containers:
            if container and container not in excluded_containers:
                backup_mysql_databases(container)
    except subprocess.CalledProcessError:
        print("Erro ao listar os containers.")

def copy_backups_to_remote():
    try:
        subprocess.run(["rsync", "-av", local_backup_dir + "/", "usuario@servidor_remoto:" + remote_backup_dir])
        print("Backups copiados com sucesso para o servidor remoto.")
    except subprocess.CalledProcessError:
        print("Erro ao copiar backups para o servidor remoto.")

if __name__ == "__main__":
    main()
    copy_backups_to_remote()
