import subprocess
import json

def list_databases_in_containers():
    # Obtém nomes dos contêineres que têm o MySQL instalado e ativo
    containers_raw = subprocess.run(["lxc", "list", "--format", "json"], check=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    containers_data = json.loads(containers_raw.stdout.decode("utf-8"))
    containers = [container["name"] for container in containers_data if container["status"] == "Running"]

    # Itera sobre a lista de contêineres e lista as bases de dados do usuário
    for container_name in containers:
        try:
            # Verifica se o MySQL está instalado e ativo
            subprocess.run(["lxc", "exec", container_name, "--", "systemctl", "is-active", "mysql"], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("----------------------------------------")
            print(f"Listando bases de dados no contêiner {container_name}...")

            # Lista as bases de dados
            subprocess.run(["lxc", "exec", container_name, "--", "mysql", "-e", "SHOW DATABASES;"], check=True)

        except subprocess.CalledProcessError:
            pass  # MySQL não está instalado ou ativo, não faz nada

    print("----------------------------------------")

# Chama a função principal
if __name__ == "__main__":
    list_databases_in_containers()
