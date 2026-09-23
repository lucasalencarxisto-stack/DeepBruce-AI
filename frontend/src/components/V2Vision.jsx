import "./V2Vision.css";


const features = [
  {
    icon: "🎙",
    status: "PLANNED",
    title: "Natural Voice",
    description:
      "Conversa contínua com STT, DeepBruce e TTS local ou dedicado.",
  },
  {
    icon: "🧙",
    status: "CONCEPT",
    title: "Living Avatar",
    description:
      "Bruce deixa de ser apenas uma marca e se torna uma presença visual reativa.",
  },
  {
    icon: "🧠",
    status: "RESEARCH",
    title: "DeepBruce SLM",
    description:
      "Modelo Transformer experimental para estudo de tokenizer, attention e next-token prediction.",
  },
  {
    icon: "⚡",
    status: "PLANNED",
    title: "Native Client",
    description:
      "Cliente C++ dedicado à camada de voz, áudio, avatar e performance local.",
  },
  {
    icon: "💾",
    status: "PLANNED",
    title: "Persistent Memory",
    description:
      "Conversas persistentes e arquitetura com banco NoSQL e repository layer.",
  },
  {
    icon: "📊",
    status: "RESEARCH",
    title: "AI Evaluation",
    description:
      "Métricas para intent routing, entidades, ambiguidades e respostas não suportadas.",
  },
];


function V2Vision({
  onBack,
  onToggleTheme,
  theme,
}) {
  return (
    <main className="vision-page">
      <header className="vision-nav">
        <div className="brand">
          <img
            className="brand-logo"
            src="/assets/Logotipo.png"
            alt="DeepBruce AI"
          />
        </div>

        <div className="vision-actions">
          <button
            type="button"
            className="theme-toggle"
            onClick={onToggleTheme}
          >
            {theme === "dark"
              ? "☀"
              : "☾"}
          </button>

          <button
            type="button"
            className="vision-back"
            onClick={onBack}
          >
            ← V1.5
          </button>
        </div>
      </header>

      <section className="vision-hero">
        <span className="section-kicker">
          THE NEXT SPELL
        </span>

        <h1>
          DeepBruce
          <span>
            {" "}V2
          </span>
        </h1>

        <p className="vision-lead">
          From assistant to embodied intelligence.
        </p>

        <p>
          V1.5 gives Bruce a mind.
          V2 gives Bruce a presence.
        </p>

        <span className="vision-badge">
          CONCEPT / ROADMAP
        </span>
      </section>

      <section className="vision-grid">
        {features.map((feature) => (
          <article
            className="vision-card"
            key={feature.title}
          >
            <div className="vision-icon">
              {feature.icon}
            </div>

            <span className="vision-status">
              {feature.status}
            </span>

            <h2>
              {feature.title}
            </h2>

            <p>
              {feature.description}
            </p>
          </article>
        ))}
      </section>

      <section className="vision-evolution">
        <div>
          <span>
            V1.5
          </span>

          <h2>
            A mind.
          </h2>

          <p>
            Chat · RAG · Ollama ·
            Entity Resolution · Voice Lite
          </p>
        </div>

        <strong>
          →
        </strong>

        <div>
          <span>
            V2
          </span>

          <h2>
            A presence.
          </h2>

          <p>
            Voice · Avatar · SLM ·
            Persistence · Native Client
          </p>
        </div>
      </section>
    </main>
  );
}


export default V2Vision;