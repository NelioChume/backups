import subprocess
import json

# Função para verificar o estado do MySQL em um contêiner
def check_mysql_status(container_name):
    print("----------------------------------------")
    print(f"Verificando o estado do MySQL no contêiner {container_name}...")

    # Verifica se o MySQL está instalado
    try:
        subprocess.run(["lxc", "exec", container_name, "--", "which", "mysql"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"MySQL está instalado no contêiner {container_name}.")

        # Verifica se o serviço MySQL está em execução
        try:
            subprocess.run(["lxc", "exec", container_name, "--", "systemctl", "is-active", "mysql"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"MySQL está ativo no contêiner {container_name}.")
        except subprocess.CalledProcessError:
            print(f"MySQL não está ativo no contêiner {container_name}.")

    except subprocess.CalledProcessError:
        print(f"MySQL não está instalado no contêiner {container_name}.")

# Função principal
def main():
    # Obtém nomes dos contêineres que estão ligados
    containers_raw = subprocess.run(["lxc", "list", "--format", "json"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    containers_data = json.loads(containers_raw.stdout.decode("utf-8"))
    containers = [container["name"] for container in containers_data if container["status"] == "Running"]

    # Itera sobre a lista de contêineres e realiza verificações
    for container_name in containers:
        check_mysql_status(container_name)

    print("----------------------------------------")

# Chama a função main se este script for o programa principal
if __name__ == "__main__":
    main()
