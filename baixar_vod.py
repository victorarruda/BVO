"""
BVO - Baixador de Vídeos Online (V2.0 OldSchool)
Desenvolvido por: Victor Arruda (https://github.com/victorarruda/BVO)
"""
import sys
import os
import configparser
import subprocess
from datetime import datetime

CONFIG_FILE = "config.ini"

def ensure_dependencies():
    packages = {'yt-dlp': 'yt_dlp', 'curl-cffi': 'curl_cffi'}
    for pkg, module in packages.items():
        try:
            __import__(module)
        except ImportError:
            print(f"O pacote {pkg} não foi encontrado. Instalando...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            print(f"Instalação do {pkg} concluída com sucesso.")

ensure_dependencies()

import yt_dlp

def load_config():
    config = configparser.ConfigParser(interpolation=None)
    if not os.path.exists(CONFIG_FILE):
        config['Geral'] = {
            'pasta_destino': '.',
            'arquivo_historico': 'historico_downloads.txt',
            'download_pendente': '',
            'formato_pendente': '',
            'navegador_cookies': ''
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
    else:
        config.read(CONFIG_FILE, encoding='utf-8')
        if not config.has_option('Geral', 'navegador_cookies'):
            config.set('Geral', 'navegador_cookies', '')
    return config

def log_download(title, size_str, url, arquivo_historico):
    title_safe = title.replace(" | ", " - ").replace("|", "-")
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"{data_atual} | {title_safe} | {size_str} | {url}\n"
    with open(arquivo_historico, 'a', encoding='utf-8') as f:
        f.write(linha)

def listar_historico(arquivo_historico):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "=" * 80)
    print(" " * 30 + "HISTÓRICO DE DOWNLOADS")
    print("=" * 80)
    if not os.path.exists(arquivo_historico):
        print("Nenhum histórico encontrado.")
    else:
        with open(arquivo_historico, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
            if not linhas:
                print("Nenhum histórico encontrado.")
            else:
                print(f"{'DATA':<21} | {'TAMANHO':<10} | {'TÍTULO'}")
                print("-" * 80)
                for linha in linhas:
                    partes = linha.strip().split(" | ")
                    if len(partes) >= 4:
                        data = partes[0]
                        url = partes[-1]
                        tamanho = partes[-2]
                        titulo = " - ".join(partes[1:-2])
                        titulo = titulo[:40] + "..." if len(titulo) > 40 else titulo
                        print(f"{data:<21} | {tamanho:<10} | {titulo}")
                    else:
                        print(linha.strip())
    print("=" * 80)
    input("\nPressione Enter para voltar ao menu...")

def menu_config_browser(config):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=======================================")
    print(" CONFIGURAÇÕES DE NAVEGADOR (COOKIES)")
    print("=======================================\n")
    print("Se o YouTube bloquear seu download pedindo para confirmar")
    print("que você não é um robô, você pode permitir que o BVO leia")
    print("os cookies do seu navegador para burlar o bloqueio.\n")
    print("Qual navegador você costuma usar para assistir vídeos?")
    print("1 - Chrome")
    print("2 - Edge")
    print("3 - Firefox")
    print("4 - Brave")
    print("5 - Opera")
    print("6 - Nenhum (Desativar Extração)\n")
    
    nav_op = input("Escolha uma opção (Enter para voltar): ").strip()
    nav_map = {'1': 'chrome', '2': 'edge', '3': 'firefox', '4': 'brave', '5': 'opera', '6': ''}
    if nav_op in nav_map:
        config['Geral']['navegador_cookies'] = nav_map[nav_op]
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print(f"\nConfiguração salva com sucesso! Navegador definido para: {nav_map[nav_op].capitalize() if nav_map[nav_op] else 'Nenhum'}")
        input("Pressione Enter para continuar...")

def construir_opcoes_ytdlp(config, imp_target):
    ydl_opts = {
        'impersonate': imp_target,
        'quiet': True,
        'no_warnings': True
    }
    nav_cookie = config.get('Geral', 'navegador_cookies', fallback='')
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = "cookies.txt"
    elif nav_cookie:
        ydl_opts['cookiesfrombrowser'] = (nav_cookie, None, None, None)
    return ydl_opts

def formatar_tamanho(bytes_size):
    if not bytes_size: return "N/A"
    mb = bytes_size / (1024 * 1024)
    return f"{mb:.2f}MB"

def menu_selecionar_formato(url, config, imp_target):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Link inserido: {url}")
    print("\nO que você deseja fazer?")
    print("1 - Listar todos os arquivos/formatos disponíveis (Completo)")
    print("2 - Listar apenas as resoluções de vídeo e escolher o áudio manualmente")
    print("3 - Baixar a melhor qualidade (Vídeo + Áudio) automaticamente")
    
    opcao = input("\nDigite a opção desejada (1, 2 ou 3): ").strip()
    if opcao not in ['1', '2', '3']:
        return None
        
    if opcao == '3':
        return "bestvideo+bestaudio/best"
        
    print("\nExtraindo informações do vídeo na nuvem, aguarde...\n")
    ydl_opts = construir_opcoes_ytdlp(config, imp_target)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            if os.name == 'nt':
                os.system('color 07')
                
            print("\n==========================================================================")
            print(f"{'ID':<10} | {'RESOLUÇÃO':<15} | {'EXTENSÃO':<8} | {'VCODEC':<15} | {'TAMANHO'}")
            print("-" * 74)
            
            for f in formats:
                fid = str(f.get('format_id', 'N/A'))
                ext = str(f.get('ext', 'N/A'))
                res = str(f.get('resolution', f.get('format_note', 'N/A')))
                vcodec = str(f.get('vcodec', 'none'))
                filesize = formatar_tamanho(f.get('filesize', f.get('filesize_approx', 0)))
                
                if opcao == '2' and (vcodec == 'none' or vcodec == 'images'):
                    continue # Na opção 2, ignora áudio puro e imagens
                    
                print(f"{fid:<10} | {res:<15} | {ext:<8} | {vcodec:<15} | {filesize}")
            print("==========================================================================\n")
            
            fid = input("Digite o ID do formato desejado (Enter para melhor): ").strip()
            if not fid:
                return "bestvideo+bestaudio/best"
                
            if opcao == '2':
                add_audio = input("Deseja embutir o melhor áudio disponível neste vídeo? (S/N): ").strip().upper()
                if add_audio == 'S':
                    return f"{fid}+bestaudio"
                    
            return fid
            
    except Exception as e:
        error_msg = str(e)
        print("\n=======================================")
        print("[ERRO] Falha ao extrair formatos.")
        if "403" in error_msg or "Sign in" in error_msg or "bot" in error_msg.lower():
            print("DICA: O YouTube exigiu autenticação! Volte ao menu inicial,")
            print("vá na Opção 3 (Configurações) e ative os Cookies do navegador!")
        else:
            print(f"Detalhe: {error_msg}")
        print("=======================================")
        input("Pressione Enter para voltar...")
        return None

def executar_download(url, format_id, pasta_destino, arquivo_historico, imp_target, config):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\nIniciando o download com o formato selecionado: {format_id} ...\n")
    
    config['Geral']['download_pendente'] = url
    config['Geral']['formato_pendente'] = format_id
    with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
        
    ydl_opts = construir_opcoes_ytdlp(config, imp_target)
    ydl_opts['format'] = format_id
    ydl_opts['outtmpl'] = os.path.join(pasta_destino, "%(title)s.%(ext)s")
    ydl_opts['quiet'] = False # Mostra o progresso nativo no console
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Extraindo informações do vídeo...")
            info = ydl.extract_info(url, download=False)
            title = info.get('title', url)
            
            filepath = ""
            req_downloads = info.get('requested_downloads', [])
            if req_downloads:
                filepath = req_downloads[0].get('filepath', '')
            else:
                filepath = ydl.prepare_filename(info)
                
            try:
                ydl.process_info(info)
            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e)
                if "403" in error_msg or "Forbidden" in error_msg:
                    print("\n========================================")
                    print("[ERRO] O servidor de origem recusou a continuação do download (Erro 403).")
                    print("Isso geralmente acontece quando um download pendente fica antigo e o link expira.")
                    print("========================================\n")
                    resp = input("Deseja apagar o arquivo parcial corrompido/antigo e baixar do ZERO? (S/N): ").strip().upper()
                    if resp == 'S':
                        for ext in ['.part', '.ytdl', '']:
                            f = filepath + ext
                            if os.path.exists(f): os.remove(f)
                        print("\nReiniciando o download do zero...\n")
                        ydl.process_info(info)
                    else:
                        print("\nDownload cancelado pelo usuário.")
                        return
                else:
                    print(f"\n[ERRO YT-DLP]: {error_msg}")
                    return
                
            if filepath and os.path.exists(filepath):
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                size_str = f"{size_mb:.2f} MB"
            else:
                size_str = "Desconhecido"
            
        print("\nDownload finalizado com sucesso!")
        log_download(title, size_str, url, arquivo_historico)
        
        config['Geral']['download_pendente'] = ''
        config['Geral']['formato_pendente'] = ''
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
            
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
        
    print("\n" + "=" * 40)
    input("Pressione Enter para voltar ao menu principal...")

def check_resume(config, pasta_destino, arquivo_historico, imp_target):
    url_pendente = config.get('Geral', 'download_pendente', fallback='')
    fmt_pendente = config.get('Geral', 'formato_pendente', fallback='')
    
    if url_pendente:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("========================================")
        print(" BVO - BAIXADOR DE VÍDEOS ONLINE (OldSchool) V2")
        print("========================================\n")
        print(f" ATENÇÃO: Foi detectado um download interrompido!")
        print(f" URL: {url_pendente}")
        
        resp = input("\nDeseja retomar este download de onde parou? (S/N): ").strip().upper()
        if resp == 'S':
            executar_download(url_pendente, fmt_pendente, pasta_destino, arquivo_historico, imp_target, config)
        else:
            config['Geral']['download_pendente'] = ''
            config['Geral']['formato_pendente'] = ''
            with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
                config.write(configfile)

def main():
    config = load_config()
    arquivo_historico = config.get('Geral', 'arquivo_historico', fallback='historico_downloads.txt')
    pasta_destino = config.get('Geral', 'pasta_destino', fallback='.')

    try:
        from yt_dlp.networking.impersonate import ImpersonateTarget
        imp_target = ImpersonateTarget(client='chrome', version='131')
    except ImportError:
        imp_target = 'Chrome-131'

    check_resume(config, pasta_destino, arquivo_historico, imp_target)

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("========================================")
        print(" BVO v2 - BAIXADOR DE VÍDEOS ONLINE (OldSchool)")
        print(" Desenvolvido por: Victor Arruda (https://github.com/victorarruda/BVO)")
        print("========================================\n")
        print("1 - Baixar um novo vídeo")
        print("2 - Ver histórico de downloads")
        print("3 - Configurações (Cookies/Bloqueios)")
        print("4 - Sair\n")
        
        escolha = input("Escolha uma opção: ").strip()
        
        if escolha == '4':
            break
        elif escolha == '2':
            listar_historico(arquivo_historico)
        elif escolha == '3':
            menu_config_browser(config)
        elif escolha == '1':
            url = input("\nCole o link do vídeo e aperte Enter (ou vazio para voltar):\n> ").strip()
            if not url: continue
            
            format_id = menu_selecionar_formato(url, config, imp_target)
            if format_id:
                executar_download(url, format_id, pasta_destino, arquivo_historico, imp_target, config)

if __name__ == "__main__":
    main()
