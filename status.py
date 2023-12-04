import subprocess
import json


# Função para listar bases de dados em um contêiner MySQL
def list_user_databases(container_name):
    # Verifica se o MySQL está instalado e ativo
    try:
        subprocess.run(["lxc", "exec", container_name, "--", "systemctl", "is-active", "mysql"], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("----------------------------------------")
        print(f"Listando bases de dados no contêiner {container_name}...")

        # Lista as bases de dados
        subprocess.run(["lxc", "exec", container_name, "--", "mysql", "-e", "SHOW DATABASES;"], check=True)

    except subprocess.CalledProcessError:
        pass  # MySQL não está instalado ou ativo, não faz nada


# Função principal
def main():
    # Obtém nomes dos contêineres que têm o MySQL instalado e ativo
    containers_raw = subprocess.run(["lxc", "list", "--format", "json"], check=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    containers_data = json.loads(containers_raw.stdout.decode("utf-8"))
    containers = [container["name"] for container in containers_data if container["status"] == "Running"]

    # Itera sobre a lista de contêineres e lista as bases de dados do usuário
    for container_name in containers:
        list_user_databases(container_name)

    print("----------------------------------------")


# Chama a função main se este script for o programa principal
if __name__ == "__main__":
    main()

