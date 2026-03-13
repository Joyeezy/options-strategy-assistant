#!/bin/zsh

set -euo pipefail

PROJECT_DIR="/Users/linjiong/Documents/Playground/options-strategy-assistant"
PROJECT_VENV="${PROJECT_DIR}/.venv"
FALLBACK_VENV="/Users/linjiong/Documents/Playground/finance-query-local/.venv"
PORT_FILE="${PROJECT_DIR}/.streamlit-active-port"

cd "$PROJECT_DIR"

DEFAULT_PORT="8512"
PORT="${DEFAULT_PORT}"
LOCAL_URL=""
SERVER_ADDRESS="0.0.0.0"
STREAMLIT_BIN=""
PYTHON_BIN=""

print_lan_urls() {
  local interfaces=("en0" "en1")
  local lan_ip=""
  for interface in "${interfaces[@]}"; do
    lan_ip="$(ipconfig getifaddr "$interface" 2>/dev/null || true)"
    if [ -n "$lan_ip" ]; then
      echo "同一局域网其他电脑可访问： http://${lan_ip}:${PORT}"
    fi
  done
}

current_url() {
  echo "http://localhost:${PORT}"
}

port_owner_cwd() {
  local port="$1"
  lsof -a -ti "tcp:${port}" -sTCP:LISTEN 2>/dev/null | head -n 1 | while read -r pid; do
    if [ -n "${pid}" ]; then
      lsof -a -p "${pid}" -d cwd 2>/dev/null | tail -n 1 | awk '{print $NF}'
    fi
  done
}

is_project_running_on_port() {
  local port="$1"
  local owner
  owner="$(port_owner_cwd "${port}")"
  [ "${owner}" = "${PROJECT_DIR}" ]
}

pick_port() {
  if [ -f "${PORT_FILE}" ]; then
    local remembered_port
    remembered_port="$(cat "${PORT_FILE}" 2>/dev/null || true)"
    if [ -n "${remembered_port}" ] && is_project_running_on_port "${remembered_port}"; then
      PORT="${remembered_port}"
      return 0
    fi
  fi

  local candidate
  for candidate in "${DEFAULT_PORT}" 8513 8514 8515 8516 8517 8518 8519 8520; do
    if ! lsof -ti "tcp:${candidate}" >/dev/null 2>&1; then
      PORT="${candidate}"
      return 0
    fi
    if is_project_running_on_port "${candidate}"; then
      PORT="${candidate}"
      return 0
    fi
  done

  echo "8512-8520 端口都已被占用，请先关闭一个本地服务后重试。"
  read -r "?按回车关闭窗口..."
  exit 1
}

pick_runtime() {
  if [ -x "${PROJECT_VENV}/bin/streamlit" ] && [ -x "${PROJECT_VENV}/bin/python" ]; then
    STREAMLIT_BIN="${PROJECT_VENV}/bin/streamlit"
    PYTHON_BIN="${PROJECT_VENV}/bin/python"
    return 0
  fi

  if [ -x "${FALLBACK_VENV}/bin/streamlit" ] && [ -x "${FALLBACK_VENV}/bin/python" ]; then
    STREAMLIT_BIN="${FALLBACK_VENV}/bin/streamlit"
    PYTHON_BIN="${FALLBACK_VENV}/bin/python"
    return 0
  fi

  return 1
}

pick_port
LOCAL_URL="$(current_url)"

if is_project_running_on_port "${PORT}"; then
  echo "期权策略助手已经在运行，正在打开浏览器..."
  echo "本机地址：${LOCAL_URL}"
  print_lan_urls
  open "$LOCAL_URL"
  exit 0
fi

if ! pick_runtime; then
  echo "未找到可用的 Python/Streamlit 运行环境。"
  echo "建议先在项目目录执行："
  echo "cd ${PROJECT_DIR}"
  echo "python3 -m venv .venv"
  echo "source .venv/bin/activate"
  echo "pip install -e \".[dev]\""
  echo ""
  echo "如果你本机已有财务查询系统的虚拟环境，也可以保留它作为本地备用运行时。"
  read -r "?按回车关闭窗口..."
  exit 1
fi

echo "正在启动期权策略助手..."
echo "项目目录：$PROJECT_DIR"
echo "本机地址：${LOCAL_URL}"
print_lan_urls

if [ "${STREAMLIT_BIN}" = "${FALLBACK_VENV}/bin/streamlit" ]; then
  echo "当前使用共享运行环境：${FALLBACK_VENV}"
fi

(
  sleep 2
  open "$LOCAL_URL"
) >/dev/null 2>&1 &

echo "${PORT}" > "${PORT_FILE}"
exec "${PYTHON_BIN}" -m streamlit run app.py --server.address "${SERVER_ADDRESS}" --server.port "${PORT}"
