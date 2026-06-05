# -*- coding: utf-8 -*-
"""
auto_commit.py - Publica o HTML do extrato no GitHub Pages automaticamente.

O que faz:
  1. (Opcional) copia um HTML de origem para o repositorio local
     (gera index.html e espelho_visualizacao.html lado a lado).
  2. Detecta se a pasta e um repo git; se nao for, inicializa.
  3. Faz git add, commit e push.
  4. Se nada mudou, nao cria commit vazio.

Requisitos:
  - Git instalado (ou via GitHub Desktop, que embute o git).
  - Credenciais no Windows Credential Manager (login via GitHub Desktop ja basta).

Uso:
  python auto_commit.py
  python auto_commit.py --source "C:\\caminho\\novo_index.html"
  python auto_commit.py --message "Atualizacao 2026-06-05"

Em outro script:
  from auto_commit import publicar
  publicar(source_html=r"C:\\...\\index.html", message="Atualizacao")
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURACAO PADRAO - ajuste se mudar de maquina/repositorio
# ============================================================
REPO_DIR        = Path(r"C:\Users\lucas\Downloads\se2 - sistema\EXTRATO\extrato grazielle")
DEFAULT_SOURCE  = Path(r"C:\Users\lucas\Downloads\se2 - sistema\EXTRATO\extrato grazielle\index.html")
REMOTE_URL      = "https://github.com/lucasabnersd-ai/extrato-grazielle.git"
BRANCH          = "main"
PUBLISHED_NAMES = ["index.html", "espelho_visualizacao.html"]
USER_EMAIL      = "lucas.abnersd@gmail.com"
USER_NAME       = "lucas-abnersd"

# Caminho do git.exe - preenchido em runtime por _localizar_git().
GIT_EXE = "git"
# ============================================================


def _localizar_git():
    """Acha o git.exe: PATH > Program Files > GitHub Desktop embutido."""
    achado = shutil.which("git")
    if achado:
        return achado

    candidatos = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        os.path.expandvars(r"%LocalAppData%\Programs\Git\cmd\git.exe"),
    ]

    # GitHub Desktop - pasta de versao muda a cada update
    for pattern in [
        r"%LocalAppData%\GitHubDesktop\app-*\resources\app\git\cmd\git.exe",
        r"%LocalAppData%\GitHubDesktop\app-*\resources\app\git\mingw64\bin\git.exe",
        r"%LocalAppData%\GitHubDesktop\app-*\resources\app\git\mingw32\bin\git.exe",
    ]:
        for p in sorted(glob.glob(os.path.expandvars(pattern)), reverse=True):
            candidatos.append(p)

    for c in candidatos:
        if c and os.path.isfile(c):
            return c

    raise RuntimeError(
        "git.exe nao encontrado.\n"
        "  - Se usa GitHub Desktop: abra-o uma vez (ele instala/atualiza o git).\n"
        "  - Senao, instale Git for Windows: https://git-scm.com/download/win"
    )


def _run(cmd, cwd=None, check=True, quiet=False):
    """Executa um comando e devolve (returncode, stdout, stderr)."""
    if not quiet:
        print(f"  $ {' '.join(cmd)}")
    try:
        res = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        raise RuntimeError(f"Executavel nao encontrado: {cmd[0]}")
    if not quiet:
        if res.stdout.strip():
            print(res.stdout.rstrip())
        if res.stderr.strip():
            print(res.stderr.rstrip())
    if check and res.returncode != 0:
        raise RuntimeError(
            f"Comando falhou (codigo {res.returncode}): {' '.join(cmd)}\n"
            f"stderr: {res.stderr.strip()}"
        )
    return res.returncode, res.stdout, res.stderr


def _git_versao():
    try:
        res = subprocess.run(
            [GIT_EXE, "--version"],
            capture_output=True, text=True, check=True,
        )
        return res.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _eh_repo_git(repo_dir):
    return (Path(repo_dir) / ".git").exists()


def _inicializar_repo(repo_dir):
    """Init + remote + fetch + reset, mantendo arquivos locais para o proximo commit."""
    print(f"\n[INIT] '{repo_dir}' nao e repo git ainda. Configurando...")
    _run([GIT_EXE, "init"], cwd=repo_dir)
    _run([GIT_EXE, "checkout", "-B", BRANCH], cwd=repo_dir, check=False)

    _run([GIT_EXE, "config", "user.email", USER_EMAIL], cwd=repo_dir)
    _run([GIT_EXE, "config", "user.name", USER_NAME], cwd=repo_dir)

    rc, helper, _ = _run(
        [GIT_EXE, "config", "--get", "credential.helper"],
        cwd=repo_dir, check=False, quiet=True,
    )
    if not helper.strip():
        _run([GIT_EXE, "config", "credential.helper", "manager"],
             cwd=repo_dir, check=False)

    rc, _, _ = _run(
        [GIT_EXE, "remote", "get-url", "origin"],
        cwd=repo_dir, check=False, quiet=True,
    )
    if rc != 0:
        _run([GIT_EXE, "remote", "add", "origin", REMOTE_URL], cwd=repo_dir)
    else:
        _run([GIT_EXE, "remote", "set-url", "origin", REMOTE_URL], cwd=repo_dir)

    rc, _, _ = _run([GIT_EXE, "fetch", "origin", BRANCH], cwd=repo_dir, check=False)
    if rc != 0:
        print("  AVISO: 'git fetch' falhou. Push pode pedir credenciais agora.")

    rc, _, _ = _run(
        [GIT_EXE, "reset", "--mixed", f"origin/{BRANCH}"],
        cwd=repo_dir, check=False,
    )
    if rc != 0:
        print("  Branch remoto inexistente ou inalcancavel; fara push inicial.")
    print("[INIT] OK\n")


def _copiar_origem(source, repo_dir):
    src = Path(source)
    if not src.is_file():
        print(f"  AVISO: arquivo de origem nao encontrado: {src}")
        return False
    for nome in PUBLISHED_NAMES:
        dst = Path(repo_dir) / nome
        if str(src.resolve()).casefold() == str(dst.resolve()).casefold():
            print(f"  Origem ja e o destino: {dst.name} (copia ignorada)")
            continue
        shutil.copy2(src, dst)
        print(f"  Copiado: {src.name} -> {dst}")
    return True


def _ha_mudancas(repo_dir):
    rc, out, _ = _run(
        [GIT_EXE, "status", "--porcelain"],
        cwd=repo_dir, check=False, quiet=True,
    )
    return bool(out.strip())


def _resumo_mudancas(repo_dir):
    rc, out, _ = _run(
        [GIT_EXE, "status", "--short"],
        cwd=repo_dir, check=False, quiet=True,
    )
    return out.strip()


def publicar(source_html=None, message=None, repo_dir=None):
    """
    Retorna:
      0 sucesso
      1 erro
      2 nada a publicar
    """
    repo = Path(repo_dir) if repo_dir else REPO_DIR
    source = Path(source_html) if source_html else DEFAULT_SOURCE

    print("=" * 60)
    print(f"  Publicando extrato em: {repo}")
    print(f"  Remote:               {REMOTE_URL}")
    print(f"  Branch:               {BRANCH}")
    print("=" * 60)

    # Localizar o git (PATH > Program Files > GitHub Desktop)
    global GIT_EXE
    try:
        GIT_EXE = _localizar_git()
    except RuntimeError as exc:
        print(f"\nERRO: {exc}")
        return 1
    print(f"\n[i] Usando git em: {GIT_EXE}")
    ver = _git_versao()
    if ver:
        print(f"[i] {ver}")

    if not repo.is_dir():
        print(f"\nERRO: pasta do repo nao existe: {repo}")
        return 1

    # 1) Copiar HTML novo (opcional)
    print("\n[1/4] Copiando HTML gerado...")
    if source and source.exists():
        _copiar_origem(source, repo)
    else:
        print(f"  Sem fonte ({source}) - vai usar os arquivos ja na pasta.")

    # 2) Inicializa repo se preciso
    if not _eh_repo_git(repo):
        _inicializar_repo(repo)
    else:
        rc, out, _ = _run(
            [GIT_EXE, "config", "user.email"],
            cwd=repo, check=False, quiet=True,
        )
        if not out.strip():
            _run([GIT_EXE, "config", "user.email", USER_EMAIL], cwd=repo)
            _run([GIT_EXE, "config", "user.name", USER_NAME], cwd=repo)

    # 3) git add + verifica se ha mudancas
    print("\n[2/4] git add .")
    _run([GIT_EXE, "add", "."], cwd=repo)

    if not _ha_mudancas(repo):
        print("\n  Nada mudou desde o ultimo commit. Nada a publicar.")
        return 2

    print("\n  Mudancas detectadas:")
    print("  " + _resumo_mudancas(repo).replace("\n", "\n  "))

    msg = message or f"Atualizacao automatica {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    print(f"\n[3/4] git commit -m \"{msg}\"")
    _run([GIT_EXE, "commit", "-m", msg], cwd=repo)

    # 4) push
    print(f"\n[4/4] git push origin {BRANCH}")
    try:
        _run([GIT_EXE, "push", "-u", "origin", BRANCH], cwd=repo)
    except RuntimeError as exc:
        print(f"\nERRO no push: {exc}")
        print("\nDicas:")
        print(" - Abra o GitHub Desktop uma vez para garantir login ativo.")
        print(" - Ou rode 'git push' manual nessa pasta para o Credential Manager")
        print("   pedir/salvar usuario e senha.")
        return 1

    print("\n" + "=" * 60)
    print("  PUBLICADO COM SUCESSO")
    print("  https://lucasabnersd-ai.github.io/extrato-grazielle/")
    print("  (O GitHub Pages leva ~1 min para refletir as mudancas.)")
    print("=" * 60)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Publica o extrato no GitHub Pages.")
    parser.add_argument("--source",  help="Caminho do HTML de origem.")
    parser.add_argument("--message", help="Mensagem do commit.")
    parser.add_argument("--repo",    help="Pasta do repositorio local.")
    args = parser.parse_args()

    try:
        rc = publicar(
            source_html=args.source,
            message=args.message,
            repo_dir=args.repo,
        )
    except Exception as exc:
        print(f"\nERRO FATAL: {exc}")
        import traceback
        traceback.print_exc()
        return 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
