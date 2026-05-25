Sistema de Chatbot RAG Avancado para o INPE
Este projeto consiste no desenvolvimento de um sistema de chatbot inteligente baseado na arquitetura Retrieval Augmented Generation, conhecida como RAG. O objetivo principal e facilitar o acesso e a consulta a documentos tecnicos e relatórios institucionais do Instituto Nacional de Pesquisas Espaciais, o INPE.

O sistema integra quatro tecnicas avancadas de Recuperacao de Informacao que podem ser ativadas de forma modular atraves da interface. Essas tecnicas sao Hypothetical Document Embeddings, Multi Query Retrieval, Reranking com CrossEncoder e Knowledge Graph, que funciona como um Grafo de Conhecimento.

A arquitetura e composta por um backend construído em FastAPI, um frontend em HTML, CSS e JavaScript puro, persistencia de dados e autenticacao via Supabase, alem do processamento de linguagem de grande escala utilizando a infraestrutura de endpoints do NVIDIA NIM.

Estrutura Operacional das Tecnicas Avancadas
Baseline com FAISS: Realiza a busca vetorial por similaridade cossenoidal direta, utilizando os embeddings de 1024 dimensoes gerados pelo modelo NV Embed sobre os blocos de texto indexados de 400 tokens.

HyDE: O modelo de linguagem gera uma resposta hipotetica previa para a pergunta do usuario. O embedding dessa resposta hipotetica e utilizado para realizar a busca vetorial, aproximando o espaco semantico da consulta ao formato dos documentos tecnicos originais.

Multi Query Retrieval: O sistema gera tres variacoes linguisticas da pergunta original atraves do LLM, executa buscas vetoriais paralelas para cada variacao e consolida os resultados aplicando uma estrategia logica de deduplicao de conteudo.

Reranking: Funciona como um filtro de segundo estagio executado localmente. Apos a recuperacao inicial de oito candidatos pelo FAISS, um modelo CrossEncoder avalia o par pergunta e documento conjuntamente e reordena os trechos, selecionando os quatro melhores para o prompt final.

Knowledge Graph: Utiliza processamento de linguagem natural local via spaCy para extracao de entidades nomeadas e constroi um grafo de adjacencia dirigido com a biblioteca NetworkX. O subgrafo relacional das entidades presentes na pergunta e anexado ao prompt como contexto estruturado.

Pre requisitos do Sistema
Antes de iniciar a configuracao do ambiente, certifique se de que a sua maquina local possui os seguintes componentes instalados:

Docker Desktop configurado e ativo.

Git para clonagem e versionamento do repositorio.

Chave de API ativa da NVIDIA.

Projeto configurado no Supabase com as tabelas de historico e chaves de acesso geradas.

Configuracao do Ambiente Passo a Passo

Passo 1: Clonar o Repositorio
Abra o terminal do seu sistema operacional e execute o comando abaixo para baixar os arquivos do projeto para a sua maquina local:
git clone https://github.com/crazen/chatbotinpe.git
cd chatbotinpe

Passo 2: Configurar o Arquivo de Variaveis de Ambiente
Na raiz do diretorio clonado, crie um arquivo de texto com o nome exato de .env. Este arquivo contera as credenciais e chaves secretas necessarias para a comunicacao com os servicos externos. Adicione o seguinte conteudo interno, substituindo os valores ficticios pelas suas credenciais reais:

NVIDIA_API_KEY=sua_chave_nvidia_nim_aqui
SUPABASE_URL=https://seu_projeto.supabase.co
SUPABASE_KEY=sua_chave_anon_publica_do_supabase
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000
ENV=prod

Passo 3: Configurar os Recursos do WSL2 no Windows
Caso esteja executando o Docker em ambiente Windows com WSL2, e altamente recomendavel definir limites minimos de recursos para evitar o esgotamento de memoria durante a execucao do modelo CrossEncoder local.

Navegue ate a pasta de perfil do seu usuario no Windows, geralmente localizada em C:\Users\seu_usuario.

Verifique a existencia do arquivo .wslconfig. Caso nao exista, crie um arquivo com esse nome exato.

Insira as seguintes linhas de diretiva tecnica dentro do arquivo:
[wsl2]
memory=4GB
processors=4

Salve o arquivo e feche o editor.

Abra o terminal do PowerShell como Administrador e reinicie o subsistema de maquinas virtuais executando o comando:
wsl --shutdown

Inicialize novamente o aplicativo do Docker Desktop.

Execucao do Sistema via Docker Compose
Passo 1: Construcao da Imagem de Producao
Com o aplicativo Docker Desktop aberto e o motor de conteineres ativo, execute o comando abaixo na raiz do repositorio para baixar a imagem base do Python, instalar os pacotes do arquivo requirements.txt e realizar o download previo dos modelos locais do spaCy e SentenceTransformers:
docker compose build

O processo de build inicial pode demandar alguns minutos para baixar e processar os pacotes matematicos do PyTorch e os pesos das matrizes de atencao do CrossEncoder.

Passo 2: Inicializacao dos Servicos em Segundo Plano
Apos a conclusao bem sucedida do build, inicialize o conteiner de forma isolada utilizando a flag correspondente para execucao em segundo plano:
docker compose up -d

O Docker criara as redes virtuais internas e instanciara o conteiner nomeado como nimchat.

Passo 3: Verificacao dos Logs de Inicializacao
Para certificar se de que o servidor Uvicorn carregou os modulos com sucesso e esta pronto para receber conexoes na porta de rede, monitore os logs de execucao com o comando:
docker compose logs -f

Aguarde ate verificar a exibicao da linha de sucesso emitida pelo FastAPI:
INFO: Application startup complete.

Para sair do modo de visualizacao continua de logs e liberar o terminal, pressione a combinacao de teclas Ctrl + C. O conteiner permanecera executando de forma silenciosa.

Execucao dos Testes de Avaliacao Automatizados
O sistema conta com um ambiente automatizado para medicao empirica de latencia e qualidade RAG atraves do script eval_rag.py.

Para disparar os testes de bancada contra o conteiner ativo, garanta que possui as bibliotecas do ambiente virtual local ativas ou instaladas na sua maquina fisica e execute o comando:
python eval_rag.py

O script simulara o envio de perguntas padrao utilizando um token master de bypass de seguranca, testara individualmente e de forma combinada as oito configuracoes possiveis de tecnicas avancadas e exibira uma tabela de dados estruturada contendo os tempos em segundos e os indices lexicos exatos de Faithfulness e Answer Relevancy para cada rodada.
