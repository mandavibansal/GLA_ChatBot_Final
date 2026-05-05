import Head from "next/head";
import { useEffect, useRef, useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const starterMessage = {
  role: "assistant",
  content: "Ask me anything about GLA University.",
  sources: [],
};

const exampleQuestions = [
  "What programmes are offered?",
  "Admission deadlines?",
  "Fees and Scholarships",
  "How many labs and faculty members?",
  "Campus life & clubs",
  "Hostel facilities"
];

const announcements = [
  {
    eyebrow: "Admissions 2026",
    title: "Applications are open for the upcoming intake.",
    detail: "Check the latest admissions timeline, eligibility, and document checklist before the deadline.",
    ctaLabel: "Apply now",
    prompt: "What is the latest admission deadline and eligibility criteria?",
  },
  {
    eyebrow: "NIRF Ranking",
    title: "See how GLA University is positioned in recent rankings.",
    detail: "Explore ranking highlights, category performance, and institutional achievements.",
    ctaLabel: "View ranking",
    prompt: "What does GLA University say about its NIRF ranking?",
  },
  {
    eyebrow: "Placements",
    title: "Placement highlights are one of the most searched updates.",
    detail: "Review recruiter mentions, placement support, and career outcomes shared by the university.",
    ctaLabel: "See placements",
    prompt: "What does GLA say about placements?",
  },
  {
    eyebrow: "Scholarship Exam",
    title: "Scholarship-related queries are trending right now.",
    detail: "Learn about scholarship exams, fee support, and merit-based opportunities.",
    ctaLabel: "Explore scholarships",
    prompt: "What scholarship exam or scholarship details are mentioned?",
  },
];

async function readResponsePayload(response) {
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    try {
      return await response.json();
    } catch {
      return null;
    }
  }

  try {
    return await response.text();
  } catch {
    return null;
  }
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatChatContent(content) {
  if (!content) {
    return "";
  }

  const lines = content.split(/\r?\n/);
  let html = "";
  let listOpen = false;

  const closeList = () => {
    if (listOpen) {
      html += "</ul>";
      listOpen = false;
    }
  };

  lines.forEach((line) => {
    const trimmed = line.trim();

    if (trimmed === "") {
      closeList();
      html += "<div class='h-2'></div>";
      return;
    }

    const escaped = escapeHtml(trimmed)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>");

    if (/^###\s+/.test(trimmed)) {
      closeList();
      html += `<h4 class='mb-2 text-sm font-semibold text-[#2e4f32]'>${escaped.replace(/^###\s+/, "")}</h4>`;
      return;
    }

    if (/^##\s+/.test(trimmed)) {
      closeList();
      html += `<h3 class='mb-2 text-base font-semibold text-[#2e4f32]'>${escaped.replace(/^##\s+/, "")}</h3>`;
      return;
    }

    if (/^#\s+/.test(trimmed)) {
      closeList();
      html += `<h2 class='mb-2 text-lg font-semibold text-[#1f4728]'>${escaped.replace(/^#\s+/, "")}</h2>`;
      return;
    }

    if (/^[-*]\s+/.test(trimmed)) {
      if (!listOpen) {
        html += "<ul class='ml-5 list-disc space-y-1 text-sm text-[#435046]'>";
        listOpen = true;
      }
      html += `<li>${escaped.replace(/^[-*]\s+/, "")}</li>`;
      return;
    }

    closeList();
    html += `<p class='mb-2 text-sm leading-7 text-[#445247]'>${escaped}</p>`;
  });

  closeList();
  return html;
}

export default function Home() {
  const [messages, setMessages] = useState([starterMessage]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeAnnouncement, setActiveAnnouncement] = useState(0);
  const [bannerDismissed, setBannerDismissed] = useState(false);
  const bottomRef = useRef(null);
  const trimmedInput = input.trim();
  const visibleMessages = messages.slice(1);
  const showWelcome = visibleMessages.length === 0;
  const currentAnnouncement = announcements[activeAnnouncement];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (bannerDismissed) {
      return undefined;
    }

    const rotationTimer = window.setInterval(() => {
      setActiveAnnouncement((currentIndex) => (currentIndex + 1) % announcements.length);
    }, 4000);

    return () => window.clearInterval(rotationTimer);
  }, [bannerDismissed]);

  const appendAssistantError = (detail) => {
    setError(detail);
    setMessages((currentMessages) => [
      ...currentMessages,
      {
        role: "assistant",
        content:
          "I couldn't fetch an answer because the backend request failed. Please verify the API server, then try again.",
        sources: [],
      },
    ]);
  };

  const sendMessage = async () => {
    const nextInput = input.trim();
    if (!nextInput || loading) {
      return;
    }

    setError("");
    setLoading(true);
    setInput("");

    const userMessage = { role: "user", content: nextInput };
    setMessages((currentMessages) => [...currentMessages, userMessage]);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: nextInput,
        }),
      });
      const payload = await readResponsePayload(response);

      if (!response.ok) {
        throw new Error(payload?.detail || "Chat request failed.");
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          content: payload?.answer,
          sources: payload?.sources || [],
        },
      ]);
    } catch (requestError) {
      const detail =
        requestError instanceof Error
          ? requestError.message
          : "The chatbot could not reach the backend. Please check that the FastAPI server is running.";
      appendAssistantError(detail);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = async (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      await sendMessage();
    }
  };

  const handleExampleClick = (question) => {
    setInput(question);
  };

  const clearChat = () => {
    if (loading) {
      return;
    }

    setMessages([starterMessage]);
    setInput("");
    setError("");
  };

  const handleAnnouncementJump = (index) => {
    setActiveAnnouncement(index);
  };

  const handleAnnouncementCta = () => {
    setInput(currentAnnouncement.prompt);
  };

  return (
    <>
      <Head>
        <title>GLA University Assistant</title>
        <meta
          name="description"
          content="A clean and vibrant GLA University chatbot for fast campus queries."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <main className="h-screen overflow-hidden px-3 py-3 sm:px-5 sm:py-5">
        <div className="relative mx-auto flex h-full max-w-[1500px] overflow-hidden rounded-[36px] border border-white/20 bg-[#123f2b] shadow-[0_40px_120px_rgba(21,61,36,0.36)]">
          <div
            className="pointer-events-none absolute -inset-6 scale-105 bg-cover bg-center"
            style={{
              backgroundImage: "url('/gla-campus-bg.jpeg')",
              filter: "blur(9px) saturate(0.72) brightness(0.82) hue-rotate(8deg)",
            }}
          />
          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(130deg,rgba(9,45,26,0.58),rgba(24,78,45,0.54),rgba(54,87,56,0.5))]" />
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_40%,rgba(255,255,255,0.16),transparent_24%),radial-gradient(circle_at_18%_16%,rgba(255,255,255,0.08),transparent_20%),radial-gradient(circle_at_85%_88%,rgba(147,170,138,0.16),transparent_22%)]" />

          <div className="relative flex min-w-0 flex-1 flex-col items-center justify-center px-4 py-4 sm:px-8">
            <div className="flex w-full max-w-[860px] flex-col overflow-hidden rounded-[34px] border border-white/30 bg-[linear-gradient(180deg,rgba(255,255,255,0.68),rgba(255,255,255,0.9))] shadow-[0_28px_80px_rgba(23,55,36,0.24)] backdrop-blur-2xl">
              {!bannerDismissed && (
                <section className="border-b border-white/40 bg-[linear-gradient(90deg,rgba(245,239,213,0.96),rgba(244,248,236,0.92),rgba(231,243,233,0.95))] px-4 py-4 text-[#28412f] sm:px-6">
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                    <div className="min-w-0 flex-1">
                      <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-[#8b6a17]">
                        {currentAnnouncement.eyebrow}
                      </p>
                      <p className="mt-1 text-sm font-semibold sm:text-base">
                        {currentAnnouncement.title}
                      </p>
                      <p className="mt-1 text-sm leading-6 text-[#526155]">
                        {currentAnnouncement.detail}
                      </p>
                    </div>

                    <div className="flex items-center gap-2 self-start">
                      <button
                        type="button"
                        onClick={handleAnnouncementCta}
                        className="rounded-full bg-[linear-gradient(90deg,#145f31,#c69a2d)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-white shadow-[0_10px_24px_rgba(20,95,49,0.22)] transition duration-200 hover:-translate-y-0.5 hover:brightness-110 hover:shadow-[0_16px_34px_rgba(20,95,49,0.34)]"
                      >
                        {currentAnnouncement.ctaLabel}
                      </button>
                      <button
                        type="button"
                        onClick={() => setBannerDismissed(true)}
                        className="flex h-9 w-9 items-center justify-center rounded-full border border-[#cfc8a8] bg-white/70 text-lg leading-none text-[#526155] transition hover:border-[#b48b2a] hover:text-[#28412f]"
                        aria-label="Dismiss announcements"
                      >
                        ×
                      </button>
                    </div>
                  </div>

                  <div className="mt-4 flex items-center gap-2">
                    {announcements.map((announcement, index) => (
                      <button
                        key={announcement.eyebrow}
                        type="button"
                        onClick={() => handleAnnouncementJump(index)}
                        className={`h-2.5 rounded-full transition ${
                          index === activeAnnouncement
                            ? "w-8 bg-[#1f6a37]"
                            : "w-2.5 bg-[#c8cfbf] hover:bg-[#9cab94]"
                        }`}
                        aria-label={`Show announcement ${index + 1}`}
                      />
                    ))}
                  </div>
                </section>
              )}

              <header className="flex items-center justify-between gap-3 border-b border-white/30 bg-[linear-gradient(90deg,rgba(9,62,34,0.96),rgba(25,84,49,0.92),rgba(114,108,62,0.88))] px-5 py-4 text-white sm:px-6">
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/18 text-sm font-semibold shadow-[0_10px_24px_rgba(255,255,255,0.18)]">
                    GLA
                  </div>
                  <div>
                    <p className="text-base font-semibold sm:text-lg">Talk to GLA Assistant</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={clearChat}
                    disabled={loading}
                    className="rounded-full bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-[#1e5f33] transition hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    Clear
                  </button>
                </div>
              </header>

              <div className="relative flex min-h-0 flex-1 flex-col bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.78),rgba(251,250,244,0.94)_42%,rgba(240,241,236,0.98)_100%)]">
                <div className="message-scrollbar flex-1 overflow-y-auto px-4 py-5 sm:px-8 sm:py-8">
                  {showWelcome ? (
                    <div className="flex min-h-[420px] flex-col items-center justify-center text-center">
                      <img
                        src="/gla-logo.png"
                        alt="GLA University logo"
                        className="h-28 w-28 object-contain drop-shadow-[0_20px_35px_rgba(29,70,43,0.28)] sm:h-32 sm:w-32"
                      />
                      <p className="mt-8 text-3xl font-semibold leading-tight text-[#1c2f23] sm:text-4xl">
                        Welcome to GLA University.
                        <br />
                        <span className="text-[#ab8324]">How may I help you today?</span>
                      </p>
                      <div className="mt-8 flex flex-wrap justify-center gap-3">
                        {exampleQuestions.map((question) => (
                          <button
                            key={question}
                            type="button"
                            onClick={() => handleExampleClick(question)}
                            className="rounded-full border border-[#d9d7c3] bg-white/85 px-4 py-2 text-sm text-[#3f4f42] transition hover:border-[#b48b2a] hover:text-[#1f3525]"
                          >
                            {question}
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="mx-auto flex w-full max-w-3xl flex-col gap-4">
                      <div className="self-center rounded-full bg-white/70 px-4 py-1 text-xs font-medium text-[#6b776d] shadow-sm">
                        Today
                      </div>

                      {visibleMessages.map((message, index) => {
                        const isUser = message.role === "user";
                        return (
                          <div
                            key={`${message.role}-${index}`}
                            className={`flex ${isUser ? "justify-end" : "justify-start"}`}
                          >
                            <div className="max-w-[82%]">
                              <div className={`mb-2 flex items-center gap-2 text-[11px] uppercase tracking-[0.16em] ${
                                isUser ? "justify-end text-white/80" : "justify-start text-slate-500"
                              }`}>
                                <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold tracking-[0.2em] ${
                                  isUser
                                    ? "bg-white/10 text-white"
                                    : "bg-[#e7f0e7] text-[#2d5a2f]"
                                }`}>
                                  {isUser ? "You" : "Assistant"}
                                </span>
                                <span className="text-[10px] text-slate-400">
                                  {isUser ? "Sent" : message.sources?.length ? "Answered with sources" : "Answered"}
                                </span>
                              </div>

                              <div
                                className={`rounded-[24px] px-4 py-4 text-sm leading-7 shadow-[0_18px_40px_rgba(24,52,35,0.1)] sm:px-5 ${
                                  isUser
                                    ? "rounded-br-md bg-[linear-gradient(90deg,#1a6936,#bd9730)] text-white"
                                    : "rounded-bl-md border border-white/70 bg-white/90 text-[#445247]"
                                }`}
                              >
                                {isUser ? (
                                  <p className="whitespace-pre-wrap">{message.content}</p>
                                ) : (
                                  <div
                                    className="max-w-none whitespace-pre-wrap"
                                    dangerouslySetInnerHTML={{
                                      __html: formatChatContent(message.content),
                                    }}
                                  />
                                )}
                              </div>

                              {!isUser && message.sources?.length > 0 && (
                                <div className="mt-3 flex flex-wrap gap-2">
                                  {message.sources.map((source) => (
                                    <span
                                      key={source}
                                      className="rounded-full border border-[#c8d9c0] bg-[#f3faf2] px-3 py-1 text-[11px] font-medium text-[#2a5730]"
                                    >
                                      {source}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}

                      {loading && (
                        <div className="flex justify-start">
                          <div className="max-w-sm animate-pulse rounded-[24px] rounded-bl-md border border-white/70 bg-white/90 px-4 py-4 shadow-[0_18px_40px_rgba(24,52,35,0.1)]">
                            <div className="mb-3 flex items-center gap-2">
                              <span className="h-3 w-16 rounded-full bg-slate-200" />
                              <span className="h-3 w-10 rounded-full bg-slate-200" />
                            </div>
                            <div className="space-y-3">
                              <div className="h-3 w-5/6 rounded-full bg-slate-200" />
                              <div className="h-3 w-4/5 rounded-full bg-slate-200" />
                              <div className="h-3 w-3/5 rounded-full bg-slate-200" />
                            </div>
                          </div>
                        </div>
                      )}

                      <div ref={bottomRef} />
                    </div>
                  )}
                </div>

                <div className="border-t border-white/60 bg-white/55 px-4 py-4 backdrop-blur-md sm:px-6">
                  {error && (
                    <p className="mx-auto mb-3 max-w-3xl rounded-2xl border border-red-300/40 bg-red-50/90 px-4 py-3 text-sm text-red-600">
                      {error}
                    </p>
                  )}

                  <div className="mx-auto max-w-3xl rounded-[28px] border border-[#dfdcc7] bg-white p-3 shadow-[0_24px_70px_rgba(32,66,43,0.12)]">
                    <textarea
                      value={input}
                      onChange={(event) => setInput(event.target.value)}
                      onKeyDown={handleKeyDown}
                      rows={3}
                      placeholder="Type your question here..."
                      className="min-h-[92px] w-full resize-none rounded-[22px] border border-[#e3e0cd] bg-[#fafaf5] px-4 py-3 text-sm text-[#3d4a40] outline-none transition focus:border-[#9a7b23] focus:ring-2 focus:ring-[#e4d9b0]"
                    />

                    <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
                      <div className="flex flex-wrap gap-2">
                        <button
                          type="button"
                          onClick={() => handleExampleClick(exampleQuestions[0])}
                          className="rounded-full border border-slate-200 bg-white px-3 py-2 text-xs text-slate-500 transition hover:border-[#9aa881] hover:text-[#28412f]"
                        >
                          Suggested prompt
                        </button>
                      </div>

                      <div className="flex items-center gap-3">
                        <button
                          type="button"
                          onClick={sendMessage}
                          disabled={loading || !trimmedInput}
                          className="rounded-2xl bg-[linear-gradient(90deg,#145f31,#c69a2d)] px-5 py-3 text-sm font-semibold text-white shadow-[0_10px_24px_rgba(20,95,49,0.22)] transition duration-200 hover:-translate-y-0.5 hover:brightness-110 hover:shadow-[0_16px_34px_rgba(20,95,49,0.34)] disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0 disabled:hover:brightness-100 disabled:hover:shadow-[0_10px_24px_rgba(20,95,49,0.22)]"
                        >
                          {loading ? "Sending..." : "Send"}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
