import { useEffect, useRef, useState } from "react";

function Documents({ onBack, onLogout, onOpenDocument }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const [showUpload, setShowUpload] = useState(false);
  const [uploadType, setUploadType] = useState("pdf");
  const [selectedFile, setSelectedFile] = useState(null);
  const [textTitle, setTextTitle] = useState("");
  const [textContent, setTextContent] = useState("");
  const [uploading, setUploading] = useState(false);

  const fileInputRef = useRef(null);

  async function loadDocuments() {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setMessage("لطفاً ابتدا وارد حساب شوید");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("/api/documents", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage(data.message || "دریافت اسناد ناموفق بود");
        return;
      }

      setDocuments(data.documents || []);
      setMessage("");
    } catch (error) {
      setMessage("اتصال به سرور برقرار نشد");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  function resetUploadForm() {
    setSelectedFile(null);
    setTextTitle("");
    setTextContent("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function closeUpload() {
    if (uploading) {
      return;
    }

    setShowUpload(false);
    resetUploadForm();
  }

  function handleFileChange(event) {
    const file = event.target.files?.[0];

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (file.type !== "application/pdf") {
      setMessage("فقط فایل PDF مجاز است");
      event.target.value = "";
      setSelectedFile(null);
      return;
    }

    setMessage("");
    setSelectedFile(file);
  }

  async function handleUpload(event) {
    event.preventDefault();

    const token = localStorage.getItem("access_token");

    if (!token) {
      setMessage("لطفاً ابتدا وارد حساب شوید");
      return;
    }

    const formData = new FormData();

    if (uploadType === "pdf") {
      if (!selectedFile) {
        setMessage("لطفاً یک فایل PDF انتخاب کنید");
        return;
      }

      formData.append("file", selectedFile);
    } else {
      if (!textContent.trim()) {
        setMessage("متن سند نمی‌تواند خالی باشد");
        return;
      }

      formData.append(
        "title",
        textTitle.trim() || "Untitled"
      );

      formData.append("text", textContent);
    }

    setUploading(true);
    setMessage("");

    try {
      const response = await fetch("/api/documents", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage(
          data.message || "افزودن سند ناموفق بود"
        );
        return;
      }

      await loadDocuments();

      setShowUpload(false);
      resetUploadForm();

      setMessage("سند با موفقیت اضافه شد");
    } catch (error) {
      setMessage("اتصال به سرور برقرار نشد");
    } finally {
      setUploading(false);
    }
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
        <div className="documents-header">
          <div>
            <p className="eyebrow">کتابخانه من</p>

            <h2>اسناد من</h2>

            <p>
              فایل‌ها و متن‌های خودت را اینجا ببین.
            </p>
          </div>

          <button
            className="add-document-button"
            onClick={() => {
              setMessage("");
              setShowUpload(true);
            }}
          >
            + افزودن سند
          </button>
        </div>

        {message && (
          <p className="documents-status">
            {message}
          </p>
        )}

        {showUpload && (
          <div className="upload-panel">
            <div className="upload-panel-header">
              <div>
                <p className="eyebrow">سند جدید</p>
                <h3>افزودن سند</h3>
              </div>

              <button
                type="button"
                onClick={closeUpload}
                disabled={uploading}
              >
                ×
              </button>
            </div>

            <div className="upload-tabs">
              <button
                type="button"
                className={
                  uploadType === "pdf"
                    ? "active"
                    : ""
                }
                onClick={() => {
                  setUploadType("pdf");
                  setMessage("");
                }}
                disabled={uploading}
              >
                📄 آپلود PDF
              </button>

              <button
                type="button"
                className={
                  uploadType === "text"
                    ? "active"
                    : ""
                }
                onClick={() => {
                  setUploadType("text");
                  setMessage("");
                }}
                disabled={uploading}
              >
                📝 افزودن متن
              </button>
            </div>

            <form onSubmit={handleUpload}>
              {uploadType === "pdf" ? (
                <div className="file-upload-area">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={handleFileChange}
                    disabled={uploading}
                  />

                  {selectedFile && (
                    <div className="selected-file">
                      <span>📄</span>

                      <div>
                        <strong>
                          {selectedFile.name}
                        </strong>

                        <p>
                          {(
                            selectedFile.size /
                            1024 /
                            1024
                          ).toFixed(2)}{" "}
                          MB
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <>
                  <label htmlFor="text-title">
                    عنوان سند
                  </label>

                  <input
                    id="text-title"
                    type="text"
                    value={textTitle}
                    onChange={(event) =>
                      setTextTitle(event.target.value)
                    }
                    placeholder="مثلاً فیزیک فصل اول"
                    disabled={uploading}
                  />

                  <label htmlFor="text-content">
                    متن سند
                  </label>

                  <textarea
                    id="text-content"
                    value={textContent}
                    onChange={(event) =>
                      setTextContent(event.target.value)
                    }
                    placeholder="متن درسی خودت را اینجا وارد کن..."
                    rows={8}
                    disabled={uploading}
                  />
                </>
              )}

              <div className="upload-actions">
                <button
                  type="button"
                  onClick={closeUpload}
                  disabled={uploading}
                >
                  انصراف
                </button>

                <button
                  type="submit"
                  disabled={uploading}
                >
                  {uploading
                    ? "در حال افزودن..."
                    : "افزودن سند"}
                </button>
              </div>
            </form>
          </div>
        )}

        {loading && (
          <p className="documents-status">
            در حال دریافت اسناد...
          </p>
        )}

        {!loading &&
          !message &&
          documents.length === 0 && (
            <div className="empty-documents">
              <div className="card-icon">
                📚
              </div>

              <h3>هنوز سندی نداری</h3>

              <p>
                اولین سند خودت را اضافه کن تا
                مطالعه را شروع کنیم.
              </p>

              <button
                className="add-document-button"
                onClick={() => setShowUpload(true)}
              >
                + افزودن اولین سند
              </button>
            </div>
          )}

        {!loading &&
          documents.length > 0 && (
            <div className="documents-grid">
              {documents.map((document) => (
                <article
                  className="document-card"
                  key={document.id}
                >
                  <div className="card-icon">
                    {document.file_type === "pdf"
                      ? "📄"
                      : "📝"}
                  </div>

                  <h3>{document.title}</h3>

                  <p className="document-type">
                    {document.file_type === "pdf"
                      ? "سند PDF"
                      : "سند متنی"}
                  </p>

                  <button
                    onClick={() =>
                      onOpenDocument(document.id)
                    }
                  >
                    مشاهده سند
                  </button>
                </article>
              ))}
            </div>
          )}
      </section>
    </main>
  );
}

export default Documents;
