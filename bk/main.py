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
        # Verificar se o comando mysql está disponível no container
        output = subprocess.check_output(["lxc", "exec", container_name, "--", "which", "mysql"]).decode().strip()
        if output:
            print(f"Backup do MySQL no container {container_name} iniciado.")
            for db in get_mysql_databases(container_name):
                backup_database(container_name, "mysql", db)
        else:
            print(f"O comando mysql não está disponível no container {container_name}.")
    except subprocess.CalledProcessError:
        print(f"Erro ao verificar a disponibilidade do MySQL no container {container_name}.")

def backup_postgres(container_name):
    try:
        # Verificar se o comando psql está disponível no container
        output = subprocess.check_output(["lxc", "exec", container_name, "--", "which", "psql"]).decode().strip()
        if output:
            print(f"Backup do Postgres no container {container_name} iniciado.")
            for db in get_postgres_databases(container_name):
                backup_database(container_name, "postgres", db)
        else:
            print(f"O comando psql não está disponível no container {container_name}.")
    except subprocess.CalledProcessError:
        print(f"Erro ao verificar a disponibilidade do Postgres no container {container_name}.")

def get_mysql_databases(container_name):
    output = subprocess.check_output(["lxc", "exec", container_name, "--", "bash", "-c",
                                      "mysql -e 'show databases;'"]).decode()
    databases = output.split("\n")[1:-1]  # Remove a primeira e a última linha
    return [db for db in databases if db not in excluded_databases["mysql"]]

def get_postgres_databases(container_name):
    output = subprocess.check_output(["lxc", "exec", container_name, "--", "bash", "-c",
                                      "psql -U postgres -l | awk '{print $1}' | grep -vE '(template0|template1|postgres)'"]).decode()
    databases = output.split("\n")[2:-1]  # Remove as primeiras duas linhas e a última linha
    return databases

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
