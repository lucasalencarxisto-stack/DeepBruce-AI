export async function streamRagMessage(
  message,
  {
    onSources,
    onToken,
    onDone,
    onError,
  } = {},
) {
  const response = await fetch("/api/rag/chat", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      message,
    }),
  });

  if (!response.ok) {
    throw new Error(
      `RAG request failed: HTTP ${response.status}`,
    );
  }

  if (!response.body) {
    throw new Error(
      "Streaming response is not available.",
    );
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let buffer = "";

  try {
    while (true) {
      const { value, done } =
        await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(
        value,
        {
          stream: true,
        },
      );

      const events = buffer.split("\n\n");

      // O último pedaço pode vir incompleto.
      buffer = events.pop() ?? "";

      for (const rawEvent of events) {
        processSseEvent(
          rawEvent,
          {
            onSources,
            onToken,
            onDone,
            onError,
          },
        );
      }
    }

    // Processa algum evento restante
    // quando o stream termina.
    if (buffer.trim()) {
      processSseEvent(
        buffer,
        {
          onSources,
          onToken,
          onDone,
          onError,
        },
      );
    }
  } finally {
    reader.releaseLock();
  }
}


function processSseEvent(
  rawEvent,
  handlers,
) {
  const lines = rawEvent.split("\n");

  let eventName = "";
  let dataText = "";

  for (const line of lines) {
    if (line.startsWith("event:")) {
      eventName = line
        .slice("event:".length)
        .trim();
    }

    if (line.startsWith("data:")) {
      dataText += line
        .slice("data:".length)
        .trim();
    }
  }

  if (!eventName) {
    return;
  }

  let data = {};

  if (dataText) {
    try {
      data = JSON.parse(dataText);
    } catch {
      data = {};
    }
  }

  switch (eventName) {
    case "sources":
      handlers.onSources?.(
        data.sources ?? [],
      );
      break;

    case "token":
      handlers.onToken?.(
        data.content ?? "",
      );
      break;

    case "done":
      handlers.onDone?.();
      break;

    case "error":
      handlers.onError?.(
        data,
      );
      break;

    default:
      break;
  }
}