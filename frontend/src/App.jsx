import {
  useRef,
  useState,
} from "react";

import { streamMessage } from "./services/messageClient";
import "./App.css";


function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("Online");
  const [error, setError] = useState("");
  const [
    conversationId,
    setConversationId,
  ] = useState(null);

  const chatRef = useRef(null);


  function scrollToChat() {
    chatRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }


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
            if (
              data.conversation_id
            ) {
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

            if (
              data.route === "chat"
            ) {
              setStatus(
                "Conversando..."
              );
            }

            if (
              data.route
              === "research"
            ) {
              setStatus(
                "Pesquisando..."
              );
            }

            if (
              data.route
              === "ambiguous"
            ) {
              setStatus(
                "Buscando contexto..."
              );
            }
          },

          onSources: (
            sources
          ) => {
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
                        clarification
                          .message,
                      clarification,
                    }
                  : item
              )
            );

            setStatus(
              "Aguardando contexto"
            );
          },

          onFallback: (
            fallback
          ) => {
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
              "Preciso de mais contexto"
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

      setError(
        errorMessage
      );

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


  function handleSubmit(
    event
  ) {
    event.preventDefault();
    sendMessage(message);
  }


  function handleClarification(
    query
  ) {
    sendMessage(query);
  }


  return (
    <div className="site-shell">

      {/* HERO */}
      <section className="hero">
        <div className="hero-overlay" />

        <nav className="topbar">
          <div className="brand">
            <span className="brand-star">
              ✦
            </span>

            <span>
              DeepBruce
              <strong>
                AI
              </strong>
            </span>
          </div>

          <div className="topbar-actions">
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

            <button
              type="button"
              className="nav-cta"
              onClick={
                scrollToChat
              }
            >
              Ask Bruce
            </button>
          </div>
        </nav>

        <div className="hero-content">
          <span className="hero-kicker">
            LOCAL RESEARCH
            INTELLIGENCE
          </span>

          <h1>
            DeepBruce
            <span>
              AI
            </span>
          </h1>

          <p className="hero-tagline">
            Knowledge beyond search.
          </p>

          <p className="hero-description">
            Converse, pesquise e
            explore conhecimento com
            inteligência artificial,
            RAG e fontes reais.
          </p>

          <div className="hero-actions">
            <button
              type="button"
              className="primary-button"
              onClick={
                scrollToChat
              }
            >
              Começar pesquisa
              <span>
                ✦
              </span>
            </button>

            <a
              className="secondary-button"
              href="#architecture"
            >
              Ver arquitetura
            </a>
          </div>

          <div className="hero-meta">
            <div>
              <strong>
                PT · EN · ES
              </strong>
              <span>
                Multilíngue
              </span>
            </div>

            <div>
              <strong>
                Wikipedia
              </strong>
              <span>
                Knowledge source
              </span>
            </div>

            <div>
              <strong>
                Ollama
              </strong>
              <span>
                Local AI
              </span>
            </div>
          </div>
        </div>

        <div className="scroll-hint">
          <span>
            EXPLORE
          </span>
          <i />
        </div>
      </section>


      {/* TRANSIÇÃO */}
      <section className="experience">
        <div className="experience-glow" />

        <div className="experience-content">
          <div className="experience-image">
            <img
              src="/assets/deepbruce-avatar.png"
              alt="DeepBruce, mago digital"
            />
          </div>

          <div className="experience-copy">
            <span className="section-kicker">
              MEET BRUCE
            </span>

            <h2>
              Ask.
              <br />
              Research.
              <br />
              <span>
                Discover.
              </span>
            </h2>

            <p>
              Bruce combina conversa,
              busca contextual e
              recuperação de conhecimento
              para transformar perguntas
              em respostas fundamentadas.
            </p>

            <div className="magic-line">
              <i />
              <span>
                ✦
              </span>
              <i />
            </div>
          </div>
        </div>
      </section>


      {/* CHAT */}
      <section
        className="chat-section"
        ref={chatRef}
      >
        <div className="chat-section-heading">
          <span className="section-kicker">
            KNOWLEDGE INTERFACE
          </span>

          <h2>
            Converse com
            <span>
              {" "}DeepBruce.
            </span>
          </h2>

          <p>
            Faça uma pergunta,
            converse normalmente ou
            explore um assunto através
            da Wikipédia.
          </p>
        </div>

        <div className="chat-frame">
          <header className="chat-header">
            <div className="bruce-identity">
              <div className="bruce-orb">
                ✦
              </div>

              <div>
                <strong>
                  DeepBruce
                </strong>

                <span>
                  Research intelligence
                </span>
              </div>
            </div>

            <div className="chat-status">
              <span
                className={`status-dot ${
                  status === "Erro"
                    ? "error"
                    : ""
                }`}
              />

              {status}
            </div>
          </header>


          <div className="chat-container">
            {messages.length === 0 && (
              <div className="empty-state">
                <div className="empty-star">
                  ✦
                </div>

                <span>
                  BRUCE IS READY
                </span>

                <h3>
                  O que você quer
                  descobrir hoje?
                </h3>

                <p>
                  Tente perguntar sobre
                  pessoas, ciência,
                  tecnologia, história
                  ou simplesmente converse
                  comigo.
                </p>

                <div className="suggestions">
                  <button
                    type="button"
                    onClick={() =>
                      sendMessage(
                        "Quem foi Alan Turing?"
                      )
                    }
                  >
                    Quem foi Alan Turing?
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      sendMessage(
                        "How does a black hole work?"
                      )
                    }
                  >
                    How does a black
                    hole work?
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      sendMessage(
                        "¿Quién fue Marie Curie?"
                      )
                    }
                  >
                    ¿Quién fue Marie Curie?
                  </button>
                </div>
              </div>
            )}


            {messages.map(
              (item) => (
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
                    } ${
                      item.route
                        ? `route-${item.route}`
                        : ""
                    }`}
                  >
                    {item.content && (
                      <div className="message-text">
                        {item.content}
                      </div>
                    )}


                    {item
                      .clarification
                      ?.options
                      ?.length
                      > 0 && (
                      <div className="clarification-options">
                        {item
                          .clarification
                          .options
                          .map(
                            (
                              option
                            ) => (
                              <button
                                key={
                                  option.query
                                }
                                type="button"
                                className="clarification-option"
                                disabled={
                                  loading
                                }
                                onClick={() =>
                                  handleClarification(
                                    option.query
                                  )
                                }
                              >
                                ✦{" "}
                                {
                                  option.label
                                }
                              </button>
                            )
                          )}
                      </div>
                    )}


                    {item.sources
                      ?.length
                      > 0 && (
                      <div className="sources">
                        <span className="sources-title">
                          ✦ SOURCES
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
              )
            )}


            {loading && (
              <div className="thinking">
                <span>
                  ✦
                </span>

                DeepBruce está
                processando...
              </div>
            )}
          </div>


          {error && (
            <div className="error-message">
              {error}
            </div>
          )}


          <form
            className="composer"
            onSubmit={
              handleSubmit
            }
          >
            <span className="composer-symbol">
              ✦
            </span>

            <input
              type="text"
              value={message}
              disabled={
                loading
              }
              placeholder="Ask DeepBruce anything..."
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
              Ask
              <span>
                →
              </span>
            </button>
          </form>
        </div>
      </section>


      {/* ARQUITETURA */}
      <section
        className="architecture"
        id="architecture"
      >
        <span className="section-kicker">
          UNDER THE SPELL
        </span>

        <h2>
          Magic outside.
          <br />
          <span>
            Engineering inside.
          </span>
        </h2>

        <div className="architecture-flow">
          <div>
            <span>
              01
            </span>
            <strong>
              Intent Router
            </strong>
            <p>
              Entende o caminho da
              mensagem.
            </p>
          </div>

          <i>
            →
          </i>

          <div>
            <span>
              02
            </span>
            <strong>
              Entity Resolver
            </strong>
            <p>
              Identifica entidades e
              ambiguidades.
            </p>
          </div>

          <i>
            →
          </i>

          <div>
            <span>
              03
            </span>
            <strong>
              Wikipedia RAG
            </strong>
            <p>
              Recupera e ranqueia
              conhecimento.
            </p>
          </div>

          <i>
            →
          </i>

          <div>
            <span>
              04
            </span>
            <strong>
              Ollama
            </strong>
            <p>
              Sintetiza a resposta final.
            </p>
          </div>
        </div>
      </section>


      <footer className="footer">
        <div className="brand">
          <span className="brand-star">
            ✦
          </span>

          <span>
            DeepBruce
            <strong>
              AI
            </strong>
          </span>
        </div>

        <span>
          Knowledge beyond search.
        </span>

        <span>
          Built with curiosity.
        </span>
      </footer>
    </div>
  );
}


export default App;