import paramiko
import json
import subprocess

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
    ssh_connect('ls')

if __name__ == "__main__":
    main()
