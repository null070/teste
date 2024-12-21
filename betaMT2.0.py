#!/usr/bin/env python3

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def send_notification(data, webhook_url):
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 200:
            print("Informações enviadas com sucesso.")
        else:
            print(f"Erro ao enviar informações: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar os dados: {e}")

def download_site(url, output_dir, webhook_url):
    # Verificar se o URL começa com 'http://' ou 'https://'. Se não, adicionar 'https://'.
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Erro ao acessar a URL: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # Salva o HTML da página
        with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

        # Baixar os recursos (links, scripts, imagens)
        for tag, attr in [('link', 'href'), ('script', 'src'), ('img', 'src')]:
            for resource in soup.find_all(tag):
                resource_url = resource.get(attr)
                if resource_url:
                    resource_url = urljoin(url, resource_url)
                    resource_name = os.path.basename(resource_url.split('?')[0])
                    resource_path = os.path.join(output_dir, resource_name)

                    # Verifique se é um diretório e crie um arquivo com nome único
                    if os.path.isdir(resource_path):
                        print(f"Erro: '{resource_path}' é um diretório, não pode salvar aqui.")
                    else:
                        try:
                            res = requests.get(resource_url)
                            if res.status_code == 200:
                                with open(resource_path, 'wb') as file:
                                    file.write(res.content)
                                resource[attr] = resource_name  # Atualiza o link no HTML
                            else:
                                print(f"Erro ao baixar {resource_url}: {res.status_code}")
                        except requests.exceptions.RequestException as e:
                            print(f"Erro ao processar {resource_url}: {e}")

        # Reescreve o HTML atualizado
        with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

        print(f"Interface do site salva em: {output_dir}")

        # Envia uma notificação ao servidor com os dados do download
        data = {"url": url, "output_dir": output_dir}
        send_notification(data, webhook_url)

    except Exception as e:
        print(f"Erro ao baixar o site: {e}")

def main():
    if len(sys.argv) < 2:
        print("Uso: script.py <URL> [<diretório de saída>] <webhook_url>")
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "site_baixado"
    webhook_url = input("Digite a URL do servidor para onde enviar os dados: ")
    
    download_site(url, output_dir, webhook_url)

if __name__ == "__main__":
    main()
