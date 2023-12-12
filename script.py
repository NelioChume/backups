import subprocess
import json
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

# Função para fazer backup de bases de dados em um contêiner MySQL
def backup_user_databases(container_name, backup_dir):
    try:
        # Verifica se o MySQL está instalado e ativo
        subprocess.run(["lxc", "exec", container_name, "--", "systemctl", "is-active", "mysql"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("----------------------------------------")
        logging.info(f"Fazendo backup de bases de dados no contêiner {container_name}...")

        # Lista as bases de dados do usuário
        user_databases_raw = subprocess.run(["lxc", "exec", container_name, "--", "mysql", "-sN", "-e", "SHOW DATABASES;"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        user_databases = [db for db in user_databases_raw.stdout.decode("utf-8").split("\n") if db and db not in ['information_schema', 'mysql', 'performance_schema', 'sys']]

        # Faz backup de cada base de dados do usuário
        for db in user_databases:
            current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f"bk_{db}_{current_datetime}.sql")
            with open(backup_file, 'w') as f:
                subprocess.Popen(["lxc", "exec", container_name, "--", "mysqldump", db], stdout=f, stderr=subprocess.PIPE, universal_newlines=True)
            logging.info(f"Backup da base de dados {db} concluído. Arquivo: {backup_file}")

    except subprocess.CalledProcessError as e:
        logging.error(f"Erro durante o backup no contêiner {container_name}: {e}")

# Função principal
def main():
    # Obtém nomes dos contêineres que têm o MySQL instalado e ativo
    containers_raw = subprocess.run(["lxc", "list", "--format", "json"], check=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    containers_data = json.loads(containers_raw.stdout.decode("utf-8"))
    containers = [container["name"] for container in containers_data if container["status"] == "Running"]

    # Diretório de destino para os backups
    backup_dir = "/caminho/do/backup"

    # Cria o diretório de backup se não existir
    os.makedirs(backup_dir, exist_ok=True)

    # Itera sobre a lista de contêineres e faz backup das bases de dados do usuário
    for container_name in containers:
        backup_user_databases(container_name, backup_dir)

    logging.info("----------------------------------------")

# Chama a função principal
if __name__ == "__main__":
    main()