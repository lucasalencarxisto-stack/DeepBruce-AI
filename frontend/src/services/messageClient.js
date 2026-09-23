const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL
    ?.replace(/\/$/, "") || "";

export async function streamMessage(
  message,
  {
    conversationId = null,
    onRoute,
    onClarification,
    onSources,
    onToken,
    onFallback,
    onDone,
    onError,
  } = {}
) {
  const payload = {
    message,
  };

  if (conversationId) {
    payload.conversation_id = conversationId;
  }

  const response = await fetch(
  `${API_BASE_URL}/api/message`,
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errorMessage = "Erro ao enviar mensagem.";

    try {
      const data = await response.json();

      if (data?.message) {
        errorMessage = data.message;
      }
    } catch {
      // Mantém mensagem padrão.
    }

    throw new Error(errorMessage);
  }

  if (!response.body) {
    throw new Error(
      "O servidor não retornou um stream."
    );
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let buffer = "";
  let receivedDone = false;

  const handlers = {
    onRoute,
    onClarification,
    onSources,
    onToken,
    onFallback,
    onDone,
    onError,
  };

  try {
    while (true) {
      const {
        value,
        done,
      } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(
        value,
        {
          stream: true,
        }
      );

      const events = buffer.split("\n\n");

      buffer = events.pop() ?? "";

      for (const rawEvent of events) {
        const eventName = processSseEvent(
          rawEvent,
          handlers
        );

        if (eventName === "done") {
          receivedDone = true;
        }
      }
    }

    buffer += decoder.decode();

    if (buffer.trim()) {
      const eventName = processSseEvent(
        buffer,
        handlers
      );

      if (eventName === "done") {
        receivedDone = true;
      }
    }

    if (!receivedDone) {
      throw new Error(
        "A conexão com o DeepBruce foi encerrada antes da conclusão da resposta."
      );
    }
  } finally {
    reader.releaseLock();
  }
}


function processSseEvent(
  rawEvent,
  handlers
) {
  const lines = rawEvent
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  let eventName = null;
  let dataText = "";

  for (const line of lines) {
    if (line.startsWith("event:")) {
      eventName = line
        .slice("event:".length)
        .trim();
    }

    if (line.startsWith("data:")) {
      const value = line
        .slice("data:".length)
        .trim();

      dataText += value;
    }
  }

  if (!eventName) {
    return null;
  }

  let data = {};

  if (dataText) {
    try {
      data = JSON.parse(dataText);
    } catch {
      handlers.onError?.({
        code: "invalid_sse_payload",
        message: (
          "O servidor retornou um evento inválido."
        ),
      });

      return;
    }
  }

  switch (eventName) {
    case "route":
      handlers.onRoute?.(data);
      break;

    case "clarification":
      handlers.onClarification?.(data);
      break;

    case "sources":
      handlers.onSources?.(
        data.sources ?? []
      );
      break;

    case "token":
      handlers.onToken?.(
        data.content ?? ""
      );
      break;

    case "fallback":
      handlers.onFallback?.(data);
      break;

    case "error":
      handlers.onError?.(data);
      break;

    case "done":
      handlers.onDone?.();
      break;

    default:
      break;
  }

  return eventName;
}

export async function resetConversation(
    conversationId
  ) {
    if (!conversationId) {
      return;
    }

    const response = await fetch(
  `${API_BASE_URL}/api/conversation/${
    encodeURIComponent(
      conversationId
    )
  }`,
      {
      method: "DELETE",
      }
    );
    if (!response.ok) {
      throw new Error(
        "Não é possível reiniciar a conversa"
      );
    }
  }
