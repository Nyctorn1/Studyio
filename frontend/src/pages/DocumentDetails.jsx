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
          <button onClick={onBack}>
            بازگشت
          </button>

          <button
            className="logout-button"
            onClick={onLogout}
          >
            خروج
          </button>
        </div>
      </header>

      <section className="document-details-content">
        {loading && (
          <p className="documents-status">
            در حال دریافت سند...
          </p>
        )}

        {!loading && documentMessage && (
          <p className="documents-status">
            {documentMessage}
          </p>
        )}

        {!loading && document && (
          <>
            <div className="document-details-header">
              <div>
                <p className="eyebrow">
                  جزئیات سند
                </p>

                <h2>{document.title}</h2>

                <p>
                  {document.file_type === "pdf"
                    ? "سند PDF"
                    : "سند متنی"}
                  {" • "}
                  {document.characters.toLocaleString(
                    "fa-IR"
                  )}{" "}
                  کاراکتر
                </p>
              </div>

              {document.file_type === "pdf" &&
                fileUrl && (
                  <button
                    type="button"
                    onClick={handleDownload}
                  >
                    دانلود PDF
                  </button>
                )}
            </div>

            <section className="document-ai-panel">
              <div className="document-ai-header">
                <div>
                  <p className="eyebrow">
                    دستیار هوشمند
                  </p>

                  <h3>
                    با این سند کار کن
                  </h3>
                </div>

                <select
                  value={language}
                  onChange={(event) => {
                    setLanguage(
                      event.target.value
                    );
                    setAiMessage("");
                  }}
                  disabled={
                    summaryLoading ||
                    askLoading
                  }
                >
                  <option value="fa">
                    فارسی
                  </option>

                  <option value="en">
                    English
                  </option>
                </select>
              </div>

              {aiMessage && (
                <p
                  className="documents-status"
                  role="alert"
                >
                  {aiMessage}
                </p>
              )}

              <div className="document-ai-actions">
                <button
                  type="button"
                  onClick={handleSummarize}
                  disabled={
                    summaryLoading ||
                    askLoading
                  }
                >
                  {summaryLoading
                    ? "در حال خلاصه‌سازی..."
                    : "خلاصه‌سازی سند"}
                </button>
              </div>

              {summary && (
                <article className="ai-result-card">
                  <p className="eyebrow">
                    خلاصه سند
                  </p>

                  <div className="ai-result-content">
                    {summary}
                  </div>
                </article>
              )}

              <form
                className="ask-document-form"
                onSubmit={handleAsk}
              >
                <label htmlFor="document-question">
                  سؤال از سند
                </label>

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
                  disabled={
                    summaryLoading ||
                    askLoading
                  }
                />

                <button
                  type="submit"
                  disabled={
                    askLoading ||
                    summaryLoading ||
                    !question.trim()
                  }
                >
                  {askLoading
                    ? "در حال پاسخ‌گویی..."
                    : "پرسیدن سؤال"}
                </button>
              </form>

              {answer && (
                <article className="ai-result-card">
                  <p className="eyebrow">
                    پاسخ دستیار
                  </p>

                  <div className="ai-result-content">
                    {answer}
                  </div>
                </article>
              )}
            </section>

            {document.file_type === "pdf" ? (
              <article className="document-content-card">
                {fileLoading && (
                  <p className="documents-status">
                    در حال دریافت فایل PDF...
                  </p>
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
              <article className="document-content-card">
                <div className="document-content">
                  {document.content}
                </div>
              </article>
            )}
          </>
        )}
      </section>
    </main>
  );
}

export default DocumentDetails;
