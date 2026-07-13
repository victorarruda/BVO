<h1 align="center"> BVO - Baixador de Vídeos Online (OldSchool) </h1>

<p align="center">
  Um sistema CLI focado em máxima estabilidade e eficiência para criar cópias de segurança (backup local) de vídeos de centenas de plataformas, construído sobre o <code>yt-dlp</code>.
</p>

## Funcionalidades Principais

- **Compatibilidade Avançada (Impersonate):** O BVO utiliza a biblioteca `curl_cffi` para emular a comunicação padrão de navegadores (TLS), garantindo maior estabilidade em plataformas que exigem verificação do cliente (mitigando problemas como o Erro 403).
- **Gerenciamento Inteligente de Cookies:** Funciona lendo arquivos `cookies.txt` (via extensão do navegador) ou lendo os cookies diretamente do banco de dados do seu navegador (Chrome, Edge, Firefox, Brave, Opera) para permitir downloads autenticados de forma segura.
- **Sistema de Retomada Automática (Resume):** O script lembra qual foi o último download interrompido! Caso o aplicativo feche acidentalmente, ao reabrir ele perguntará se você deseja continuar baixando de onde parou.
- **Gerenciador Autônomo de Dependências:** O aplicativo verifica e instala pacotes ausentes na primeira inicialização, tornando a ferramenta "Plug & Play".
- **Total Compatibilidade:** Utiliza as bibliotecas e saídas padrão do Python, garantindo que o programa rode perfeitamente em Windows, Linux ou MacOS.

## Como usar

### Instalação Expressa (Winget)
Abra o PowerShell (Windows 10/11) e cole o comando abaixo para instalar todos os pré-requisitos (Python, FFmpeg e Git) automaticamente e em segundo plano:
```powershell
winget install Python.Python.3.12 Gyan.FFmpeg Git.Git -e --accept-package-agreements --accept-source-agreements
```
*(Após o término, feche e abra o PowerShell novamente para recarregar as variáveis de sistema).*

Em seguida, baixe e inicie o aplicativo com:
```powershell
git clone https://github.com/victorarruda/BVO.git
cd BVO
.\iniciar.bat
```

### Método Tradicional
1. **Pré-requisitos:**
   - Ter o [Python](https://www.python.org/downloads/) e o [Git](https://git-scm.com/) instalados no computador.
   - Ter o [FFmpeg](https://ffmpeg.org/download.html) instalado e adicionado ao `PATH` do sistema (obrigatório para a mesclagem de áudio/vídeo em alta qualidade).

2. **Executando:**
   - Dê um duplo-clique no arquivo `iniciar.bat` (Windows) ou execute `python baixar_vod.py` pelo terminal.
   - Na primeira inicialização, o aplicativo instalará todas as dependências em Python sozinho e o menu se abrirá.

## Arquivos Gerados
- `config.ini`: Salva as configurações locais, o sistema de retomada (Resume) e as preferências do seu navegador de extração.
- `historico_downloads.txt`: Um histórico completo com a data, o nome do arquivo baixado, o tamanho em MB e o link original.

## Tecnologias e Dependências
O BVO foi construído dependendo diretamente das seguintes bibliotecas e ferramentas de código aberto:

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**: O "motor" principal de extração e resolução de links. Um fork evoluído do clássico `youtube-dl`.
- **[curl-cffi](https://github.com/dexterador/curl-cffi)**: Essencial para garantir a comunicação fluida, emulando o tráfego TLS nativo de navegadores reais (como o Chrome v131).
- **[FFmpeg](https://ffmpeg.org/)**: Software externo mandatário para o *Muxing*. Ele é invocado invisivelmente pelo `yt-dlp` para mesclar os canais de Áudio e Vídeo em altíssima qualidade (arquivos separados pelos provedores de vídeo).

## Como contribuir (Help Wanted!)

O projeto é amigável para iniciantes no ecossistema Open Source! Se você deseja ajudar o BVO a evoluir, aqui está o que a comunidade mais precisa no momento:

- **[ ] Melhorias no FFmpeg (Integração Direta):**
  Hoje os scripts assumem que o FFmpeg já está na variável de sistema (PATH). Seria incrível implementar um verificador em Python que baixa a *build standalone* do FFmpeg silenciosamente se ele não for encontrado na pasta do script.
- **[ ] Internacionalização (i18n):**
  Traduzir o CLI e os menus do aplicativo (hoje 100% em português) para garantir acessibilidade global.

Basta dar um **Fork**, criar sua branch e mandar um **Pull Request**!

## Créditos e Agradecimentos

- **Idealização e Desenvolvimento Principal:** [Victor Arruda](https://github.com/victorarruda)
- **Time do `yt-dlp`:** Pelo esforço contínuo de manutenção para manter os protocolos de download das dezenas de plataformas estáveis e funcionais.
- **Comunidade Open Source:** Pelo suporte incansável na manutenção das dependências vitais para o projeto.

## Licenças

O código-fonte principal do BVO é distribuído sob a licença **Apache 2.0**. Os componentes de terceiros operam sob as seguintes licenças:
- **yt-dlp**: "The Unlicense" (Domínio Público).
- **curl-cffi**: MIT License.

*Aviso Legal: O BVO foi criado e deve ser utilizado estritamente para o propósito de realização de backups pessoais locais. O usuário é o único responsável por seguir os Termos de Serviço, agir de boa-fé e garantir o respeito aos direitos autorais dos criadores de conteúdo das respectivas plataformas de origem.*
