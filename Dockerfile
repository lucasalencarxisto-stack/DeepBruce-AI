# ──────────────────────────────────────────────────────────────────────────────
# [PT-BR] Dockerfile — backend Flask com Gunicorn (produção).
# [EN]    Dockerfile — Flask backend with Gunicorn (production).
# [ES]    Dockerfile — backend Flask con Gunicorn (producción).
# [中文]   Dockerfile — 使用 Gunicorn 的 Flask 后端（生产环境）。
# ──────────────────────────────────────────────────────────────────────────────

# [PT-BR] Imagem base leve do Python 3.12
# [EN]    Lightweight Python 3.12 base image
# [ES]    Imagen base ligera de Python 3.12
# [中文]   轻量级 Python 3.12 基础镜像
FROM python:3.12-slim

# [PT-BR] Evita .pyc e força stdout/stderr sem buffer
# [EN]    Avoid .pyc and force unbuffered stdout/stderr
# [ES]    Evita .pyc y fuerza stdout/stderr sin buffer
# [中文]   禁用 .pyc 并强制标准输出/错误无缓冲
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# [PT-BR] Atualiza pacotes mínimos e instala utilitários (curl p/ healthchecks)
# [EN]    Update minimal packages and install utilities (curl for healthchecks)
# [ES]    Actualiza paquetes mínimos e instala utilidades (curl para healthchecks)
# [中文]   更新最小包并安装工具（用于健康检查的 curl）
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# [PT-BR] Diretório de trabalho da aplicação
# [EN]    Application working directory
# [ES]    Directorio de trabajo de la aplicación
# [中文]   应用工作目录
WORKDIR /app

# [PT-BR] Copie primeiro os requisitos para aproveitar cache de camadas
# [EN]    Copy requirements first to leverage layer cache
# [ES]    Copiar requisitos primero para aprovechar la caché de capas
# [中文]   先复制依赖以利用分层缓存
COPY requirements.txt ./

# [PT-BR] Instala dependências Python (sem cache)
# [EN]    Install Python dependencies (no cache)
# [ES]    Instalar dependencias de Python (sin caché)
# [中文]   安装 Python 依赖（不使用缓存）
RUN pip install --no-cache-dir -r requirements.txt

# [PT-BR] Copia o restante do projeto
# [EN]    Copy the rest of the project
# [ES]    Copiar el resto del proyecto
# [中文]   复制项目其余文件
COPY . .

# [PT-BR] Cria usuário não-root (melhor prática em produção)
# [EN]    Create non-root user (best practice in production)
# [ES]    Crear usuario no root (mejor práctica en producción)
# [中文]   创建非 root 用户（生产最佳实践）
RUN useradd -m -u 10001 appuser
USER appuser

# [PT-BR] Exponha a porta do serviço (informativo)
# [EN]    Expose service port (informational)
# [ES]    Exponer puerto del servicio (informativo)
# [中文]   暴露服务端口（信息性）
EXPOSE 8000

# [PT-BR] Variáveis para tunar o Gunicorn em runtime (podem ser sobrescritas)
# [EN]    Variables to tune Gunicorn at runtime (can be overridden)
# [ES]    Variables para ajustar Gunicorn en runtime (se pueden sobrescribir)
# [中文]   运行时调优 Gunicorn 的环境变量（可被覆盖）
ENV GUNICORN_WORKERS=2 \
    GUNICORN_THREADS=2 \
    PORT=8000

# [PT-BR] Comando padrão: Gunicorn (gthread) servindo WSGI:app
# [EN]    Default command: Gunicorn (gthread) serving WSGI:app
# [ES]    Comando por defecto: Gunicorn (gthread) sirviendo WSGI:app
# [中文]   默认命令：使用 Gunicorn（gthread）服务 WSGI:app
#
# [PT-BR] Observação: garanta que exista WSGI.py expondo `app` e que o
#          requirements.txt inclua gunicorn, flask, httpx etc.
# [EN]    Note: ensure WSGI.py exposes `app` and requirements.txt includes
#          gunicorn, flask, httpx, etc.
# [ES]    Nota: asegúrese de que WSGI.py exponga `app` y que requirements.txt
#          incluya gunicorn, flask, httpx, etc.
# [中文]   注意：确保 WSGI.py 暴露 `app`，且 requirements.txt 包含 gunicorn、flask、httpx 等。
CMD sh -c 'gunicorn \
  -w ${GUNICORN_WORKERS:-2} \
  -k gthread --threads ${GUNICORN_THREADS:-2} \
  -b 0.0.0.0:${PORT:-8000} \
  --timeout 120 --graceful-timeout 30 --keep-alive 5 \
  wsgi:app'
