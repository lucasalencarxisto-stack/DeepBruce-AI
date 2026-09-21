import { useState } from "react";
import { streamMessage } from "./services/messageClient";
import "./App.css";


function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("Online");
  const [error, setError] = useState("");
  const [conversationId, setConversationId] =
    useState(null);


  async function sendMessage(
    text = message
  ) {
    const cleanMessage = (
      text || ""
    ).trim();

    if (!cleanMessage || loading) {
      return;
    }

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: cleanMessage,
    };

    const assistantId =
      crypto.randomUUID();

    const assistantMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      sources: [],
      clarification: null,
      fallback: null,
      route: null,
    };

    setMessages((current) => [
      ...current,
      userMessage,
      assistantMessage,
    ]);

    setMessage("");
    setLoading(true);
    setError("");
    setStatus("Pensando...");

    try {
      await streamMessage(
        cleanMessage,
        {
          conversationId,

          onRoute: (data) => {
            if (data.conversation_id) {
              setConversationId(
                data.conversation_id
              );
            }

            setMessages((current) =>
              current.map((item) =>
                item.id === assistantId
                  ? {
                      ...item,
                      route: data.route,
                    }
                  : item
              )
            );

            if (data.route === "chat") {
              setStatus(
                "Conversando..."
              );
            }

            if (
              data.route === "research"
            ) {
              setStatus(
                "Pesquisando na Wikipédia..."
              );
            }

            if (
              data.route === "ambiguous"
            ) {
              setStatus(
                "Preciso entender melhor..."
              );
            }
          },

          onSources: (sources) => {
            setMessages((current) =>
              current.map((item) =>
                item.id === assistantId
                  ? {
                      ...item,
                      sources,
                    }
                  : item
              )
            );
          },

          onToken: (token) => {
            setMessages((current) =>
              current.map((item) =>
                item.id === assistantId
                  ? {
                      ...item,
                      content:
                        item.content
                        + token,
                    }
                  : item
              )
            );
          },

          onClarification: (
            clarification
          ) => {
            setMessages((current) =>
              current.map((item) =>
                item.id === assistantId
                  ? {
                      ...item,
                      content:
                        clarification.message,
                      clarification,
                    }
                  : item
              )
            );

            setStatus(
              "Aguardando esclarecimento"
            );
          },

          onFallback: (fallback) => {
            setMessages((current) =>
              current.map((item) =>
                item.id === assistantId
                  ? {
                      ...item,
                      content:
                        fallback.message,
                      fallback,
                    }
                  : item
              )
            );

            setStatus(
              "Não consegui identificar a intenção"
            );
          },

          onError: (data) => {
            const errorMessage =
              data?.message
              ?? "Ocorreu um erro.";

            setError(errorMessage);

            setMessages((current) =>
              current.map((item) =>
                item.id === assistantId
                  ? {
                      ...item,
                      content:
                        item.content
                        || errorMessage,
                    }
                  : item
              )
            );

            setStatus("Erro");
          },

          onDone: () => {
            setStatus("Online");
          },
        }
      );
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Erro inesperado.";

      setError(errorMessage);

      setMessages((current) =>
        current.map((item) =>
          item.id === assistantId
            ? {
                ...item,
                content:
                  item.content
                  || errorMessage,
              }
            : item
        )
      );

      setStatus("Erro");
    } finally {
      setLoading(false);
    }
  }


  function handleSubmit(event) {
    event.preventDefault();

    sendMessage(message);
  }


  function handleClarification(
    query
  ) {
    sendMessage(query);
  }


  return (
    <main className="app">
      <header className="app-header">
        <div>
          <span className="app-kicker">
            LOCAL AI ASSISTANT
          </span>

          <h1>
            DeepBruce AI
          </h1>

          <p className="app-subtitle">
            Chat + Wikipedia RAG + Ollama
          </p>
        </div>

        <div className="status">
          <span
            className={`status-dot ${
              status === "Erro"
                ? "error"
                : ""
            }`}
          />

          <span>
            {status}
          </span>
        </div>
      </header>


      <section className="chat-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <h2>
              DeepBruce está online.
            </h2>

            <p>
              Converse normalmente ou faça
              uma pergunta para pesquisar
              na Wikipédia.
            </p>
          </div>
        )}


        {messages.map((item) => (
          <article
            key={item.id}
            className={`message-row ${
              item.role
            }`}
          >
            <span className="message-author">
              {item.role === "user"
                ? "Você"
                : "DeepBruce"}
            </span>

            <div
              className={`message-bubble ${
                item.role
              }`}
            >
              {item.content && (
                <div className="message-text">
                  {item.content}
                </div>
              )}


              {item.clarification
                ?.options?.length > 0 && (
                <div className="clarification-options">
                  {item.clarification.options.map(
                    (option) => (
                      <button
                        key={
                          option.query
                        }
                        type="button"
                        className="clarification-option"
                        disabled={loading}
                        onClick={() =>
                          handleClarification(
                            option.query
                          )
                        }
                      >
                        {option.label}
                      </button>
                    )
                  )}
                </div>
              )}


              {item.sources?.length > 0 && (
                <div className="sources">
                  <span className="sources-title">
                    FONTES
                  </span>

                  <div className="sources-grid">
                    {item.sources.map(
                      (
                        source,
                        index
                      ) => (
                        <a
                          key={
                            source.url
                            || index
                          }
                          className="source-card"
                          href={
                            source.url
                          }
                          target="_blank"
                          rel="noreferrer"
                        >
                          <strong>
                            {
                              source.title
                            }
                          </strong>

                          <span>
                            {
                              source.source
                              || "Wikipedia"
                            }
                          </span>
                        </a>
                      )
                    )}
                  </div>
                </div>
              )}
            </div>
          </article>
        ))}


        {loading && (
          <div className="thinking">
            DeepBruce está processando...
          </div>
        )}
      </section>


      {error && (
        <div className="error-message">
          {error}
        </div>
      )}


      <form
        className="composer"
        onSubmit={handleSubmit}
      >
        <input
          type="text"
          value={message}
          disabled={loading}
          placeholder="Pergunte alguma coisa ao DeepBruce..."
          onChange={(event) =>
            setMessage(
              event.target.value
            )
          }
        />

        <button
          type="submit"
          disabled={
            loading
            || !message.trim()
          }
        >
          Enviar
        </button>
      </form>
    </main>
  );
}


export default App;