# Extrato Grazielle

Visualização web do extrato (página estática, sem back-end).

O arquivo `index.html` é totalmente autônomo — todo o CSS, JavaScript e dados estão embutidos nele. Não há dependências externas (sem CDNs, sem imagens, sem APIs).

## Como publicar no GitHub Pages

### 1. Crie um repositório no GitHub
- Acesse https://github.com/new
- Nome sugerido: `extrato-grazielle`
- Marque como **Public** (Pages gratuito exige público em contas Free)
- **Não** marque "Add README" (já existe um aqui)

### 2. Faça o upload dos arquivos

**Opção A — pelo navegador (mais simples):**
1. No repositório recém-criado, clique em **"uploading an existing file"**.
2. Arraste todos os arquivos desta pasta (`index.html`, `.nojekyll`, `README.md`, `.gitignore`).
3. Clique em **Commit changes**.

**Opção B — via Git (linha de comando):**
```bash
cd "caminho/para/extrato grazielle"
git init
git add .
git commit -m "Publicação inicial do extrato"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/extrato-grazielle.git
git push -u origin main
```

### 3. Ative o GitHub Pages
1. No repositório, vá em **Settings → Pages**.
2. Em **Source**, selecione **Deploy from a branch**.
3. Branch: **main** / pasta: **/ (root)**. Clique **Save**.
4. Aguarde 1–2 minutos. O site ficará disponível em:
   `https://SEU_USUARIO.github.io/extrato-grazielle/`

## Arquivos da pasta

| Arquivo | Função |
|---|---|
| `index.html` | Página principal (cópia de `espelho_visualizacao.html` renomeada — o GitHub Pages serve `index.html` por padrão). |
| `espelho_visualizacao.html` | Arquivo original mantido como cópia de segurança. |
| `.nojekyll` | Desativa o processamento Jekyll do GitHub Pages (evita problemas com arquivos/pastas começando com `_`). |
| `.gitignore` | Ignora arquivos temporários do sistema. |
| `README.md` | Este arquivo. |

## Observações

- A página exporta CSV via JavaScript no próprio navegador — funciona normalmente no GitHub Pages.
- Como os dados estão embutidos no HTML, para atualizar o extrato basta gerar novamente o `espelho_visualizacao.html` localmente, sobrescrever o `index.html` no repositório e fazer commit.
- Tamanho do HTML: ~2,4 MB. Está dentro dos limites do GitHub Pages (1 GB por site, 100 MB por arquivo).
