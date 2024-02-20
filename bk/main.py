import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Diretório onde os backups serão armazenados localmente e remotamente
local_backup_dir = os.getenv('LOCAL_BACKUP_DIR')
remote_backup_dir = os.getenv('REMOTE_BACKUP_DIR')

# Containers LXC/LXD excluídos
excluded_containers = ["postgres", "monitor", "proxy"]

# Bancos de dados excluídos
excluded_databases = {
    "mysql": ['information_schema', 'mysql', 'performance_schema', 'sys'],
    "postgres": ['postgres', 'template0', 'template1']
}

def run_command(command):
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        print(f"Erro ao executar o comando: {' '.join(command)}")

def backup_mysql(container_name):
    try:
        output = subprocess.check_output(["lxc", "exec", container_name, "--", "bash", "-c",
                                          "mysql -e 'show databases;'"]).decode()
        databases = output.split("\n")[1:-1]  # Remove a primeira e a última linha

        for db in databases:
            if db not in excluded_databases["mysql"]:
                backup_database(container_name, "mysql", db)
    except subprocess.CalledProcessError:
        print(f"Erro ao fazer backup do MySQL no container {container_name}.")

def backup_postgres(container_name):
    try:
        output = subprocess.check_output(["lxc", "exec", container_name, "--", "bash", "-c",
                                          "psql -U postgres -l | awk '{print $1}' | grep -vE '(template0|template1|postgres)'"]).decode()
        databases = output.split("\n")[2:-1]  # Remove as primeiras duas linhas e a última linha

        for db in databases:
            backup_database(container_name, "postgres", db)
    except subprocess.CalledProcessError:
        print(f"Erro ao fazer backup do Postgres no container {container_name}.")

def backup_database(container_name, db_type, db_name):
    try:
        timestamp = datetime.now().strftime("%d-%m-%Y")
        backup_file = f"bk_{db_name}_{timestamp}.sql.gz"
        backup_path = os.path.join(local_backup_dir, backup_file)

        if db_type == "mysql":
            command = ["lxc", "exec", container_name, "--", "bash", "-c",
                       f"mysqldump {db_name} | gzip > {backup_path}"]
        elif db_type == "postgres":
            command = ["lxc", "exec", container_name, "--", "bash", "-c",
                       f"pg_dump -U postgres {db_name} | gzip > {backup_path}"]

        run_command(command)
        print(f"Backup do banco de dados {db_name} ({db_type}) no container {container_name} concluído com sucesso.")
    except Exception as e:
        print(f"Erro ao fazer backup do banco de dados {db_name} ({db_type}) no container {container_name}: {e}")

def main():
    try:
        containers = subprocess.check_output(["lxc", "list", "--format", "csv", "--columns", "n"]).decode().split("\n")
        for container in containers:
            if container and container not in excluded_containers:
                backup_mysql(container)
                backup_postgres(container)
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
