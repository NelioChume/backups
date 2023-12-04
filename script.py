import subprocess
import json
import os
from datetime import datetime

# Função para fazer backup de bases de dados em um contêiner MySQL
def backup_user_databases(container_name, backup_dir):
    try:
        # Verifica se o MySQL está instalado e ativo
        subprocess.run(["lxc", "exec", container_name, "--", "systemctl", "is-active", "mysql"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("----------------------------------------")
        print(f"Fazendo backup de bases de dados no contêiner {container_name}...")

        # Lista as bases de dados do usuário
        user_databases_raw = subprocess.run(["lxc", "exec", container_name, "--", "mysql", "-sN", "-e", "SHOW DATABASES;"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        user_databases = [db for db in user_databases_raw.stdout.decode("utf-8").split("\n") if db and db not in ['information_schema', 'mysql', 'performance_schema', 'sys']]

        # Faz backup de cada base de dados do usuário
        for db in user_databases:
            current_datetime = datetime.now().strftime('%d%m%Y_%H%M%S')
            backup_file = os.path.join(backup_dir, f"bk_{db}_{current_datetime}.sql")
            subprocess.run(["lxc", "exec", container_name, "--", "mysqldump", db], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            print(f"Backup da base de dados {db} concluído. Arquivo: {backup_file}")
    except subprocess.CalledProcessError:
        pass  # MySQL não está instalado ou ativo, não faz nada

# Função principal
def main():
    # Obtém nomes dos contêineres que têm o MySQL instalado e ativo
    containers_raw = subprocess.run(["lxc", "list", "--format", "json"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    containers_data = json.loads(containers_raw.stdout.decode("utf-8"))
    containers = [container["name"] for container in containers_data if container["status"] == "Running"]

    # Diretório de destino para os backups
    backup_dir = "/caminho/do/backup"

    # Cria o diretório de backup se não existir
    os.makedirs(backup_dir, exist_ok=True)

    # Itera sobre a lista de contêineres e faz backup das bases de dados do usuário
    for container_name in containers:
        backup_user_databases(container_name, backup_dir)

    print("----------------------------------------")

# Chama a função main se este script for o programa principal
if __name__ == "__main__":
    main()
