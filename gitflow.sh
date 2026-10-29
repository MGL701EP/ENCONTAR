#!/usr/bin/env bash
# gitflow.sh — Automatiza el flujo del tutorial "GitHub con Visual Studio Code"
# (EdumasterRD): configurar, clonar, subir cambios, traer cambios y trabajar con ramas.
#
# Uso:  ./gitflow.sh <comando> [argumentos]
#   configurar "Nombre" correo@ejemplo.com   git config --global user.name / user.email
#   clonar <url-del-repo.git> [carpeta]       git clone (equivale a "Git: Clone" en VS Code)
#   subir "mensaje" [archivo ...]              git add + commit + push a la rama actual
#   traer                                      git pull de la rama actual
#   estado                                     rama actual, cambios pendientes, ramas
#   rama-nueva <nombre>                        crea la rama, se cambia a ella y la sube
#   cambiar <nombre>                           cambia a una rama (local o remota)
#   fusionar <rama> [destino=main]             lleva una rama terminada a main y sube
set -euo pipefail

LOCK=""
rojo()  { printf '\033[31m%s\033[0m\n' "$*" >&2; }
verde() { printf '\033[32m%s\033[0m\n' "$*"; }
info()  { printf '\033[36m» %s\033[0m\n' "$*"; }
morir() { rojo "ERROR: $*"; exit 1; }

limpiar() { [ -n "$LOCK" ] && rm -f "$LOCK"; return 0; }
trap limpiar EXIT

requiere_git() { command -v git >/dev/null || morir "Git no está instalado. Descárgalo de https://git-scm.com"; }

requiere_repo() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 \
    || morir "No estás dentro de un repositorio Git. Entra a la carpeta del proyecto (cd ...)."
  # Bloqueo para evitar dos ejecuciones simultáneas sobre el mismo repositorio
  LOCK="$(git rev-parse --git-dir)/gitflow.lock"
  if [ -e "$LOCK" ]; then
    LOCK_ANT="$LOCK"; LOCK=""
    morir "Ya hay otra ejecución en curso (existe $LOCK_ANT). Si no es así, borra ese archivo."
  fi
  : > "$LOCK"
}

requiere_identidad() {
  git config user.name >/dev/null && git config user.email >/dev/null \
    || morir "Falta tu identidad. Ejecuta: $0 configurar \"Tu Nombre\" tu@correo.com"
}

rama_actual() { git symbolic-ref --quiet --short HEAD || morir "No estás en ninguna rama (HEAD separado)."; }

existe_remota() { git ls-remote --exit-code --heads origin "$1" >/dev/null 2>&1; }

cmd_configurar() {
  [ $# -eq 2 ] || morir "Uso: configurar \"Nombre\" correo@ejemplo.com"
  [[ "$2" == *@*.* ]] || morir "El correo '$2' no parece válido."
  git config --global user.name "$1"
  git config --global user.email "$2"
  git config --global init.defaultBranch main
  verde "Identidad configurada: $(git config --global user.name) <$(git config --global user.email)>"
}

cmd_clonar() {
  [ $# -ge 1 ] || morir "Uso: clonar <url.git> [carpeta]"
  local url="$1" dir="${2:-}"
  [[ "$url" == *.git || "$url" == git@* || -d "$url" ]] || { url="$url.git"; info "Añado .git al final: $url"; }
  [ -z "$dir" ] && dir="$(basename "$url" .git)"
  [ -e "$dir" ] && morir "La carpeta '$dir' ya existe; no clono encima para no pisar nada."
  info "Clonando $url en '$dir'"
  git clone "$url" "$dir"
  verde "Listo. Abre la carpeta '$dir' en VS Code (Archivo > Abrir carpeta)."
}

cmd_subir() {
  [ $# -ge 1 ] || morir "Uso: subir \"mensaje\" [archivo ...]"
  requiere_repo; requiere_identidad
  local msg="$1"; shift
  local rama; rama="$(rama_actual)"
  if [ $# -gt 0 ]; then info "git add $*"; git add -- "$@"; else info "git add ."; git add .; fi
  if git diff --cached --quiet; then
    info "No hay cambios nuevos que confirmar (no se crea un commit vacío)."
  else
    info "git commit -m \"$msg\""; git commit -q -m "$msg"
  fi
  # Traer primero lo que hayan subido otros para evitar rechazos en el push
  if existe_remota "$rama"; then
    info "Sincronizando con origin/$rama antes de subir"
    git pull --rebase --quiet origin "$rama" \
      || morir "Conflicto al integrar cambios remotos. Resuélvelo en VS Code, luego: git add <archivo> && git rebase --continue"
  fi
  if [ -n "$(git rev-list "origin/$rama..$rama" 2>/dev/null || echo nuevo)" ]; then
    info "git push origin $rama"; git push -q -u origin "$rama"
    verde "Subido a origin/$rama ($(git rev-parse --short HEAD))."
  else
    verde "origin/$rama ya está al día; nada que subir."
  fi
}

cmd_traer() {
  requiere_repo
  local rama; rama="$(rama_actual)"
  existe_remota "$rama" || morir "La rama '$rama' no existe en GitHub todavía. Súbela con: $0 subir \"mensaje\""
  [ -z "$(git status --porcelain --untracked-files=no)" ] \
    || morir "Tienes cambios sin confirmar. Súbelos primero ($0 subir \"mensaje\") o guárdalos con git stash."
  info "git pull origin $rama"; git pull --ff-only --quiet origin "$rama" \
    || morir "Tu rama y la remota divergieron. Usa '$0 subir \"mensaje\"', que integra con rebase."
  verde "Actualizado a $(git rev-parse --short HEAD)."
}

cmd_estado() {
  requiere_repo
  echo "Rama actual: $(rama_actual)"
  git fetch --quiet origin 2>/dev/null || rojo "(no se pudo contactar con origin)"
  git status --short --branch
  echo "Ramas:"; git branch -a
}

cmd_rama_nueva() {
  [ $# -eq 1 ] || morir "Uso: rama-nueva <nombre>"
  requiere_repo
  git check-ref-format --branch "$1" >/dev/null 2>&1 || morir "'$1' no es un nombre de rama válido."
  git show-ref --verify --quiet "refs/heads/$1" && morir "La rama '$1' ya existe. Usa: $0 cambiar $1"
  info "git switch -c $1"; git switch -q -c "$1"
  info "git push -u origin $1"; git push -q -u origin "$1"
  verde "Rama '$1' creada, activa y subida a GitHub."
}

cmd_cambiar() {
  [ $# -eq 1 ] || morir "Uso: cambiar <rama>"
  requiere_repo
  [ -z "$(git status --porcelain --untracked-files=no)" ] \
    || morir "Tienes cambios sin confirmar; súbelos antes de cambiar de rama."
  git fetch --quiet origin 2>/dev/null || true
  if git show-ref --verify --quiet "refs/heads/$1"; then git switch -q "$1"
  elif git show-ref --verify --quiet "refs/remotes/origin/$1"; then git switch -q --track "origin/$1"
  else morir "La rama '$1' no existe ni local ni en GitHub."; fi
  verde "Ahora estás en la rama: $(rama_actual)"
}

cmd_fusionar() {
  [ $# -ge 1 ] || morir "Uso: fusionar <rama> [destino=main]"
  requiere_repo; requiere_identidad
  local origen="$1" destino="${2:-main}"
  [ -z "$(git status --porcelain --untracked-files=no)" ] || morir "Tienes cambios sin confirmar."
  git show-ref --verify --quiet "refs/heads/$origen" || morir "La rama '$origen' no existe localmente."
  info "Cambiando a $destino y actualizándola"
  git switch -q "$destino"
  existe_remota "$destino" && git pull --ff-only --quiet origin "$destino"
  info "git merge $origen"
  git merge --no-edit "$origen" || morir "Conflicto en la fusión. Resuélvelo en VS Code y haz commit, o cancela con: git merge --abort"
  git push -q origin "$destino"
  verde "'$origen' fusionada en '$destino' y subida."
}

main() {
  requiere_git
  local c="${1:-}"; [ $# -gt 0 ] && shift
  case "$c" in
    configurar) cmd_configurar "$@" ;;
    clonar)     cmd_clonar "$@" ;;
    subir)      cmd_subir "$@" ;;
    traer)      cmd_traer "$@" ;;
    estado)     cmd_estado "$@" ;;
    rama-nueva) cmd_rama_nueva "$@" ;;
    cambiar)    cmd_cambiar "$@" ;;
    fusionar)   cmd_fusionar "$@" ;;
    *) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; [ -n "$c" ] && exit 1 || exit 0 ;;
  esac
}
main "$@"
