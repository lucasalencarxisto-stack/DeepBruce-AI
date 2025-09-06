# ──────────────────────────────────────────────────────────────────────────────
# [PT-BR] Ponto de entrada WSGI para servidores de produção.
#         Importa a instância Flask criada em app/__init__.py.
# [EN]    WSGI entry point for production servers.
#         Imports the Flask instance created in app/__init__.py.
# [ES]    Punto de entrada WSGI para servidores de producción.
#         Importa la instancia de Flask creada en app/__init__.py.
# ──────────────────────────────────────────────────────────────────────────────

from app import app  # [PT-BR] Instância global do Flask
                     # [EN]    Global Flask instance
                     # [ES]    Instancia global de Flask
                     # [中文]   全局 Flask 应用实例（WSGI 入口）

# [PT-BR] Exponha a variável `app` para o servidor WSGI (Gunicorn, uWSGI, etc.).
# [EN]    Expose the `app` variable to the WSGI server (Gunicorn, uWSGI, etc.).
# [ES]    Exponga la variable `app` al servidor WSGI (Gunicorn, uWSGI, etc.).
# [中文]   将变量 `app` 暴露给 WSGI 服务器（Gunicorn、uWSGI 等）。
