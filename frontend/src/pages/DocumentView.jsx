import { useEffect, useState } from "react";

function DocumentView({ documentId, onBack, onLogout }) {
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    async function loadDocument() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setMessage("لطفاً ابتدا وارد حساب شوید");
        setLoading(false);
        return;
      }

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
          setMessage(
            data.message || "دریافت سند ناموفق بود"
          );
          return;
        }

        setDocument(data.document);
      } catch (error) {
        setMessage("اتصال به سرور برقرار نشد");
      } finally {
        setLoading(false);
      }
    }

    loadDocument();
  }, [documentId]);

  function getPdfUrl() {
    const token = localStorage.getItem("access_token");

    return `/api/documents/${documentId}/file?token=${encodeURIComponent(
      token || ""
    )}`;
  }

  return (
    <main className="documents-page">
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

      <section className="documents-content">
        {loading && (
          <p className="documents-status">
            در حال دریافت سند...
          </p>
        )}

        {!loading && message && (
          <p className="documents-status">
            {message}
          </p>
        )}

        {!loading && !message && document && (
          <>
            <div className="documents-header">
              <div>
                <p className="eyebrow">
                  کتابخانه من
                </p>

                <h2>{document.title}</h2>

                <p>
                  {document.file_type === "pdf"
                    ? "سند PDF"
                    : "سند متنی"}
                </p>
              </div>

              {document.file_type === "pdf" && (
                <a
                  className="add-document-button"
                  href={getPdfUrl()}
                  download={
                    document.original_filename ||
                    document.title
                  }
                >
                  دانلود PDF
                </a>
              )}
            </div>

            {document.file_type === "pdf" ? (
              <div className="document-viewer">
                <iframe
                  src={getPdfUrl()}
                  title={document.title}
                  className="pdf-viewer"
                />
              </div>
            ) : (
              <article className="text-document">
                <div className="text-document-content">
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

export default DocumentView;