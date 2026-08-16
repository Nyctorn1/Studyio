import { useEffect, useState } from "react";

function DocumentDetails({ documentId, onBack, onLogout }) {
  const [document, setDocument] = useState(null);

  const [loading, setLoading] = useState(true);
  const [fileLoading, setFileLoading] = useState(false);

  const [documentMessage, setDocumentMessage] = useState("");
  const [aiMessage, setAiMessage] = useState("");

  const [fileUrl, setFileUrl] = useState("");

  const [language, setLanguage] = useState("fa");

  const [summary, setSummary] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [askLoading, setAskLoading] = useState(false);

  useEffect(() => {
    let objectUrl = null;

    async function loadDocument() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setDocumentMessage("لطفاً ابتدا وارد حساب شوید");
        setLoading(false);
        return;
      }

      setLoading(true);
      setDocumentMessage("");
      setAiMessage("");
      setDocument(null);
      setFileUrl("");
      setFileLoading(false);
      setSummary("");
      setAnswer("");
      setQuestion("");

      try {
        const response = await fetch(
          `/api/documents/${documentId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const data = await response.json();

        if (!response.ok) {
          setDocumentMessage(
            data.message || "دریافت سند ناموفق بود"
          );
          return;
        }

        setDocument(data.document);

        if (data.document.file_type === "pdf") {
          setFileLoading(true);

          const fileResponse = await fetch(
            `/api/documents/${documentId}/file`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          if (!fileResponse.ok) {
            let errorMessage =
              "دریافت فایل PDF ناموفق بود";

            try {
              const errorData =
                await fileResponse.json();

              errorMessage =
                errorData.message || errorMessage;
            } catch (error) {
              // Ignore invalid error response.
            }

            setDocumentMessage(errorMessage);
            return;
          }

          const blob = await fileResponse.blob();

          objectUrl = URL.createObjectURL(blob);
          setFileUrl(objectUrl);
        }
      } catch (error) {
        setDocumentMessage(
          "اتصال به سرور برقرار نشد"
        );
      } finally {
        setLoading(false);
        setFileLoading(false);
      }
    }

    loadDocument();

    return () => {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [documentId]);

  function handleDownload() {
    if (!fileUrl || !document) {
      return;
    }

    const link = window.document.createElement("a");

    link.href = fileUrl;

    link.download =
      document.original_filename ||
      document.title ||
      "document.pdf";

    window.document.body.appendChild(link);
    link.click();
    link.remove();
  }

  async function handleSummarize() {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setAiMessage("لطفاً ابتدا وارد حساب شوید");
      return;
    }

    setSummaryLoading(true);
    setAiMessage("");
    setSummary("");

    try {
      const response = await fetch(
        `/api/documents/${documentId}/summarize`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            language,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setAiMessage(
          data.message || "خلاصه‌سازی ناموفق بود"
        );
        return;
      }

      setSummary(data.summary || "");
    } catch (error) {
      setAiMessage(
        "اتصال به سرور برقرار نشد"
      );
    } finally {
      setSummaryLoading(false);
    }
  }

  async function handleAsk(event) {
    event.preventDefault();

    const token = localStorage.getItem("access_token");

    if (!token) {
      setAiMessage("لطفاً ابتدا وارد حساب شوید");
      return;
    }

    if (!question.trim()) {
      setAiMessage("لطفاً سؤال خود را وارد کنید");
      return;
    }

    setAskLoading(true);
    setAiMessage("");
    setAnswer("");

    try {
      const response = await fetch(
        `/api/documents/${documentId}/ask`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            question: question.trim(),
            language,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setAiMessage(
          data.message || "پاسخ‌گویی ناموفق بود"
        );
        return;
      }

      setAnswer(data.answer || "");
    } catch (error) {
      setAiMessage(
        "اتصال به سرور برقرار نشد"
      );
    } finally {
      setAskLoading(false);
    }
  }

  const isBusy = summaryLoading || askLoading;

  return (
    <main className="document-details-page">
      <header className="dashboard-header">
        <div className="brand">
          <div className="brand-mark">S</div>

          <div>
            <h1>Studyio</h1>
            <p>دستیار مطالعه هوشمند</p>
          </div>
        </div>

        <div className="documents-actions">
          <button
            type="button"
            onClick={onBack}
          >
            بازگشت
          </button>

          <button
            type="button"
            className="logout-button"
            onClick={onLogout}
          >
            خروج
          </button>
        </div>
      </header>

      <section className="document-details-content">
        {loading && (
          <div className="document-state-card">
            <div className="state-icon">📄</div>

            <h3>در حال دریافت سند...</h3>

            <p>
              لطفاً چند لحظه صبر کن.
            </p>
          </div>
        )}

        {!loading && documentMessage && (
          <div className="document-state-card error">
            <div className="state-icon">⚠️</div>

            <h3>مشکلی پیش آمد</h3>

            <p>{documentMessage}</p>

            <button
              type="button"
              onClick={onBack}
            >
              بازگشت به اسناد
            </button>
          </div>
        )}

        {!loading && document && (
          <>
            <section className="document-hero">
              <div className="document-hero-icon">
                {document.file_type === "pdf"
                  ? "📄"
                  : "📝"}
              </div>

              <div className="document-hero-info">
                <p className="eyebrow">
                  سند من
                </p>

                <h2>{document.title}</h2>

                <div className="document-meta">
                  <span>
                    {document.file_type === "pdf"
                      ? "PDF"
                      : "متن"}
                  </span>

                  <span>•</span>

                  <span>
                    {document.characters.toLocaleString(
                      "fa-IR"
                    )}{" "}
                    کاراکتر
                  </span>
                </div>
              </div>

              {document.file_type === "pdf" &&
                fileUrl && (
                  <button
                    className="document-download-button"
                    type="button"
                    onClick={handleDownload}
                  >
                    ⬇ دانلود PDF
                  </button>
                )}
            </section>

            <section className="document-ai-panel">
              <div className="document-ai-header">
                <div className="document-ai-title">
                  <div className="ai-icon">
                    ✨
                  </div>

                  <div>
                    <p className="eyebrow">
                      دستیار هوشمند
                    </p>

                    <h3>
                      با این سند کار کن
                    </h3>

                    <p>
                      سند را خلاصه کن یا هر سؤالی
                      درباره محتوای آن بپرس.
                    </p>
                  </div>
                </div>

                <div className="language-control">
                  <label htmlFor="document-language">
                    زبان پاسخ
                  </label>

                  <select
                    id="document-language"
                    value={language}
                    onChange={(event) => {
                      setLanguage(
                        event.target.value
                      );
                      setAiMessage("");
                    }}
                    disabled={isBusy}
                  >
                    <option value="fa">
                      فارسی
                    </option>

                    <option value="en">
                      English
                    </option>
                  </select>
                </div>
              </div>

              {aiMessage && (
                <div
                  className="ai-message"
                  role="alert"
                >
                  <span>⚠️</span>
                  <span>{aiMessage}</span>
                </div>
              )}

              <div className="document-ai-grid">
                <div className="ai-action-card summary-action-card">
                  <div className="ai-action-icon">
                    ✨
                  </div>

                  <div>
                    <h4>خلاصه‌سازی سند</h4>

                    <p>
                      مهم‌ترین نکات این سند را
                      به‌صورت خلاصه دریافت کن.
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={handleSummarize}
                    disabled={isBusy}
                  >
                    {summaryLoading
                      ? "در حال خلاصه‌سازی..."
                      : "خلاصه کن"}
                  </button>
                </div>

                <form
                  className="ai-action-card ask-action-card"
                  onSubmit={handleAsk}
                >
                  <div className="ai-action-icon">
                    💬
                  </div>

                  <div>
                    <h4>سؤال از سند</h4>

                    <p>
                      سؤال خودت را بپرس تا بر اساس
                      همین سند جواب بگیری.
                    </p>
                  </div>

                  <textarea
                    id="document-question"
                    value={question}
                    onChange={(event) =>
                      setQuestion(
                        event.target.value
                      )
                    }
                    placeholder={
                      language === "fa"
                        ? "مثلاً فصل اول درباره چه موضوعاتی صحبت می‌کند؟"
                        : "For example: What are the main topics in this document?"
                    }
                    rows={4}
                    disabled={isBusy}
                  />

                  <button
                    type="submit"
                    disabled={
                      isBusy ||
                      !question.trim()
                    }
                  >
                    {askLoading
                      ? "در حال پاسخ‌گویی..."
                      : "پرسیدن سؤال"}
                  </button>
                </form>
              </div>

              {summary && (
                <article className="ai-result-card summary-result-card">
                  <div className="ai-result-header">
                    <div>
                      <p className="eyebrow">
                        نتیجه خلاصه‌سازی
                      </p>

                      <h4>
                        خلاصه سند
                      </h4>
                    </div>

                    <span className="result-icon">
                      ✨
                    </span>
                  </div>

                  <div className="ai-result-content">
                    {summary}
                  </div>
                </article>
              )}

              {answer && (
                <article className="ai-result-card answer-result-card">
                  <div className="ai-result-header">
                    <div>
                      <p className="eyebrow">
                        پاسخ دستیار
                      </p>

                      <h4>
                        پاسخ سؤال شما
                      </h4>
                    </div>

                    <span className="result-icon">
                      💬
                    </span>
                  </div>

                  <div className="ai-result-content">
                    {answer}
                  </div>
                </article>
              )}
            </section>

            <section className="document-content-section">
              <div className="document-section-header">
                <div>
                  <p className="eyebrow">
                    محتوای سند
                  </p>

                  <h3>
                    {document.file_type === "pdf"
                      ? "نمایش فایل PDF"
                      : "متن سند"}
                  </h3>
                </div>

                {document.file_type === "pdf" && (
                  <span className="document-type-badge">
                    PDF
                  </span>
                )}
              </div>

              {document.file_type === "pdf" ? (
                <article className="document-content-card pdf-document-card">
                  {fileLoading && (
                    <div className="document-file-loading">
                      <div className="state-icon">
                        📄
                      </div>

                      <h3>
                        در حال آماده‌سازی فایل...
                      </h3>

                      <p>
                        فایل PDF در حال بارگذاری
                        است.
                      </p>
                    </div>
                  )}

                  {!fileLoading && fileUrl && (
                    <div className="pdf-viewer">
                      <iframe
                        src={fileUrl}
                        title={
                          document.original_filename ||
                          document.title
                        }
                        width="100%"
                        height="800"
                      />
                    </div>
                  )}
                </article>
              ) : (
                <article className="document-content-card text-document-card">
                  <div className="document-content">
                    {document.content}
                  </div>
                </article>
              )}
            </section>
          </>
        )}
      </section>
    </main>
  );
}

export default DocumentDetails;