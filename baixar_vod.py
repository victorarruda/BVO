"""
BVO - Baixador de Vídeos Online (V2.0 OldSchool)
Desenvolvido por: Victor Arruda (https://github.com/victorarruda/BVO)
"""
import sys
import os
import configparser
import subprocess
from datetime import datetime

YELLOW = '\033[93m'
GREEN = '\033[92m'
GRAY = '\033[90m'
RED = '\033[91m'
CYAN = '\033[96m'
RESET = '\033[0m'

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
    print(f"\n{YELLOW}{'=' * 80}")
    print(f"{YELLOW}{' ' * 30}HISTÓRICO DE DOWNLOADS")
    print(f"{YELLOW}{'=' * 80}")
    if not os.path.exists(arquivo_historico):
        print("Nenhum histórico encontrado.")
    else:
        with open(arquivo_historico, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
            if not linhas:
                print("Nenhum histórico encontrado.")
            else:
                print(f"{YELLOW}{'DATA':<21} | {'TAMANHO':<10} | {'TÍTULO'}")
                print(f"{YELLOW}{'-' * 80}")
                for linha in linhas:
                    partes = linha.strip().split(" | ")
                    if len(partes) >= 4:
                        data = partes[0]
                        url = partes[-1]
                        tamanho = partes[-2]
                        titulo = " - ".join(partes[1:-2])
                        titulo = titulo[:40] + "..." if len(titulo) > 40 else titulo
                        print(f"{GREEN}{data:<21}{RESET} | {YELLOW}{tamanho:<10}{RESET} | {titulo}")
                    else:
                        print(linha.strip())
    print(f"{YELLOW}{'=' * 80}")
    input("\nPressione Enter para voltar ao menu...")

def menu_config_browser(config):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{YELLOW}=======================================")
    print(f"{YELLOW} CONFIGURAÇÕES DE NAVEGADOR (COOKIES)")
    print(f"{YELLOW}=======================================\n")
    print("Se o YouTube bloquear seu download pedindo para confirmar")
    print("que você não é um robô, você pode permitir que o BVO leia")
    print("os cookies do seu navegador para evitar o bloqueio.\n")
    print("Qual navegador você costuma usar para assistir vídeos?")
    print(f"{GREEN}1{RESET} - Chrome")
    print(f"{GREEN}2{RESET} - Edge")
    print(f"{GREEN}3{RESET} - Firefox")
    print(f"{GREEN}4{RESET} - Brave")
    print(f"{GREEN}5{RESET} - Opera")
    print(f"{GREEN}6{RESET} - Nenhum (Desativar Extração)\n")
    
    nav_op = input("Escolha uma opção (Enter para voltar): ").strip()
    nav_map = {'1': 'chrome', '2': 'edge', '3': 'firefox', '4': 'brave', '5': 'opera', '6': ''}
    if nav_op in nav_map:
        config['Geral']['navegador_cookies'] = nav_map[nav_op]
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print(f"\n{GREEN}Configuração salva com sucesso!{RESET} Navegador definido para: {nav_map[nav_op].capitalize() if nav_map[nav_op] else 'Nenhum'}")
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
    print(f"{YELLOW}========================================")
    print(f" Link inserido: {url}")
    print(f"{YELLOW}========================================\n")
    print("O que você deseja fazer?")
    print(f"{GREEN}1{RESET} - Listar todos os arquivos/formatos disponíveis (Completo)")
    print(f"{GREEN}2{RESET} - Listar apenas as resoluções de vídeo e escolher o áudio manualmente")
    print(f"{GREEN}3{RESET} - Baixar a melhor qualidade (Vídeo + Áudio) automaticamente")
    
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
            
            if opcao == '1':
                print(f"\n{YELLOW}======================================================================================================================================================")
                print(f"{RED}[AVISO SOBRE TAMANHO E FORMATOS]")
                print(f"{YELLOW}1.{RESET} O tamanho exato pode não aparecer para streams contínuos (ex: m3u8).")
                print(f"{YELLOW}2.{RESET} Como saber se tem Áudio + Vídeo? Olhe as colunas VCODEC e ACODEC.")
                print(f"   Evite formatos marcados como {GRAY}'none'{RESET} ou {GRAY}'video/audio only'{RESET}.")
                print(f"{YELLOW}3.{RESET} Na dúvida, APENAS APERTE ENTER: a ferramenta escolherá a melhor")
                print("   qualidade (vídeo e áudio juntos) automaticamente.")
                print(f"{YELLOW}======================================================================================================================================================")
                print(f"{YELLOW}{'ID':<6} | {'EXT':<5} | {'RESOLUÇÃO':<13} | {'FPS':<4} | {'CH':<3} | {'TAMANHO':<10} | {'TBR':<6} | {'PROTO':<5} | {'VCODEC':<12} | {'VBR':<5} | {'ACODEC':<12} | {'ABR':<5} | {'ASR':<7} | {'INFO'}")
                print(f"{YELLOW}{'-' * 150}")
            else:
                print(f"\n{YELLOW}====================================================================================")
                print(f"{YELLOW}{'ID':<10} | {'RESOLUÇÃO':<15} | {'EXTENSÃO':<8} | {'VCODEC':<12} | {'ACODEC':<12} | {'TAMANHO'}")
                print(f"{YELLOW}{'-' * 84}")
            
            for f in formats:
                fid = str(f.get('format_id', 'N/A'))
                ext = str(f.get('ext', 'N/A'))
                res = str(f.get('resolution', f.get('format_note', 'N/A')))
                vcodec = str(f.get('vcodec', 'none'))[:12]
                acodec = str(f.get('acodec', 'none'))[:12]
                filesize = formatar_tamanho(f.get('filesize', f.get('filesize_approx', 0)))
                
                if opcao == '2' and (vcodec == 'none' or vcodec == 'images'):
                    continue # Na opção 2, ignora áudio puro e imagens
                    
                v_color = GRAY if vcodec == 'none' or 'only' in vcodec else RESET
                a_color = GRAY if acodec == 'none' or 'only' in acodec else RESET
                r_color = GRAY if vcodec == 'none' or vcodec == 'images' else RESET
                
                if opcao == '1':
                    fps = str(f.get('fps', ''))[:4] if f.get('fps') else ''
                    ch = str(f.get('audio_channels', '')) if f.get('audio_channels') else ''
                    tbr = f"{int(f.get('tbr', 0))}k" if f.get('tbr') else ""
                    proto = str(f.get('protocol', ''))[:5]
                    vbr = f"{int(f.get('vbr', 0))}k" if f.get('vbr') else ""
                    abr = f"{int(f.get('abr', 0))}k" if f.get('abr') else ""
                    asr = f"{int(f.get('asr', 0))}Hz" if f.get('asr') else ""
                    info = str(f.get('format_note', ''))[:20]
                    
                    print(f"{GREEN}{fid:<6}{RESET} | {ext:<5} | {r_color}{res:<13}{RESET} | {fps:<4} | {ch:<3} | {YELLOW}{filesize:<10}{RESET} | {tbr:<6} | {proto:<5} | {v_color}{vcodec:<12}{RESET} | {vbr:<5} | {a_color}{acodec:<12}{RESET} | {abr:<5} | {asr:<7} | {info}")
                else:
                    print(f"{GREEN}{fid:<10}{RESET} | {r_color}{res:<15}{RESET} | {ext:<8} | {v_color}{vcodec:<12}{RESET} | {a_color}{acodec:<12}{RESET} | {YELLOW}{filesize}")
            
            if opcao == '1':
                print(f"{YELLOW}======================================================================================================================================================{RESET}\n")
            else:
                print(f"{YELLOW}===================================================================================={RESET}\n")
            
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
        print(f"\n{RED}=======================================")
        print(f"{RED}[ERRO] Falha ao extrair formatos.")
        if "403" in error_msg or "Sign in" in error_msg or "bot" in error_msg.lower():
            print(f"{YELLOW}DICA: O YouTube exigiu autenticação! Volte ao menu inicial,")
            print(f"{YELLOW}vá na Opção 3 (Configurações) e ative os Cookies do navegador!")
        else:
            print(f"Detalhe: {error_msg}")
        print(f"{RED}=======================================")
        input("Pressione Enter para voltar...")
        return None

def executar_download(url, format_id, pasta_destino, arquivo_historico, imp_target, config):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n{GREEN}Iniciando o download com o formato selecionado: {format_id} ...{RESET}\n")
    
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
            print(f"{CYAN}Extraindo informações do vídeo...")
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
                    print(f"\n{RED}========================================")
                    print(f"{RED}[ERRO] O servidor de origem recusou a continuação do download (Erro 403).")
                    print(f"{YELLOW}Isso geralmente acontece quando um download pendente fica antigo e o link expira.")
                    print(f"{RED}========================================{RESET}\n")
                    resp = input("Deseja apagar o arquivo parcial corrompido/antigo e baixar do ZERO? (S/N): ").strip().upper()
                    if resp == 'S':
                        for ext in ['.part', '.ytdl', '']:
                            f = filepath + ext
                            if os.path.exists(f): os.remove(f)
                        print(f"\n{YELLOW}Reiniciando o download do zero...{RESET}\n")
                        ydl.process_info(info)
                    else:
                        print(f"\n{GRAY}Download cancelado pelo usuário.")
                        return
                else:
                    print(f"\n{RED}[ERRO YT-DLP]: {error_msg}")
                    return
                
            if filepath and os.path.exists(filepath):
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                size_str = f"{size_mb:.2f} MB"
            else:
                size_str = "Desconhecido"
            
        print(f"\n{GREEN}Download finalizado com sucesso!")
        log_download(title, size_str, url, arquivo_historico)
        
        config['Geral']['download_pendente'] = ''
        config['Geral']['formato_pendente'] = ''
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
            
    except Exception as e:
        print(f"\n{RED}Ocorreu um erro inesperado: {e}")
        
    print(f"\n{YELLOW}{'=' * 40}")
    input("Pressione Enter para voltar ao menu principal...")

def check_resume(config, pasta_destino, arquivo_historico, imp_target):
    url_pendente = config.get('Geral', 'download_pendente', fallback='')
    fmt_pendente = config.get('Geral', 'formato_pendente', fallback='')
    
    if url_pendente:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{YELLOW}========================================")
        print(f"{YELLOW} BVO - BAIXADOR DE VÍDEOS ONLINE (OldSchool) - V2")
        print(f"{YELLOW}========================================\n")
        print(f"{RED} ATENÇÃO: Foi detectado um download interrompido!")
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
    if os.name == 'nt':
        os.system('color 07')
        
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
        print(f"{YELLOW}========================================")
        print(f"{YELLOW} BVO - BAIXADOR DE VÍDEOS ONLINE (OldSchool) - V2")
        print(f"{GRAY} Repositório: (https://github.com/victorarruda/BVO)")
        print(f"{YELLOW}========================================\n")
        print(f"{GREEN}1{RESET} - Baixar um novo vídeo")
        print(f"{GREEN}2{RESET} - Ver histórico de downloads")
        print(f"{GREEN}3{RESET} - Configurações (Cookies/Bloqueios)")
        print(f"{GREEN}4{RESET} - Sair\n")
        
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
