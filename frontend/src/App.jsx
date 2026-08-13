import { useState } from "react";
import "./App.css";

import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import DocumentDetails from "./pages/DocumentDetails";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [loggedIn, setLoggedIn] = useState(
    Boolean(localStorage.getItem("access_token"))
  );

  const [currentPage, setCurrentPage] = useState("dashboard");
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);

  async function handleLogin(event) {
    event.preventDefault();

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage(data.message || "ورود ناموفق بود");
        return;
      }

      localStorage.setItem(
        "access_token",
        data.access_token
      );

      setLoggedIn(true);
      setCurrentPage("dashboard");
      setSelectedDocumentId(null);
      setMessage("");
    } catch (error) {
      setMessage("اتصال به سرور برقرار نشد");
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("access_token");

    setLoggedIn(false);
    setCurrentPage("dashboard");
    setSelectedDocumentId(null);

    setEmail("");
    setPassword("");
    setMessage("");
  }

  function openDocuments() {
    setCurrentPage("documents");
    setSelectedDocumentId(null);
  }

  function openDocument(documentId) {
    setSelectedDocumentId(documentId);
    setCurrentPage("document-details");
  }

  function backToDocuments() {
    setSelectedDocumentId(null);
    setCurrentPage("documents");
  }

  function backToDashboard() {
    setSelectedDocumentId(null);
    setCurrentPage("dashboard");
  }

  if (loggedIn) {
    if (
      currentPage === "document-details" &&
      selectedDocumentId !== null
    ) {
      return (
        <DocumentDetails
          documentId={selectedDocumentId}
          onBack={backToDocuments}
          onLogout={handleLogout}
        />
      );
    }

    if (currentPage === "documents") {
      return (
        <Documents
          onBack={backToDashboard}
          onLogout={handleLogout}
          onOpenDocument={openDocument}
        />
      );
    }

    return (
      <Dashboard
        onLogout={handleLogout}
        onOpenDocuments={openDocuments}
      />
    );
  }

  return (
    <main className="auth-page">
      <section className="login-card">
        <div className="brand">
          <div className="brand-mark">S</div>

          <div>
            <h1>Studyio</h1>
            <p>دستیار مطالعه هوشمند</p>
          </div>
        </div>

        <div className="login-header">
          <h2>خوش آمدی</h2>
          <p>برای ادامه وارد حساب خودت شو</p>
        </div>

        <form onSubmit={handleLogin}>
          <label htmlFor="email">ایمیل</label>

          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) =>
              setEmail(event.target.value)
            }
            placeholder="example@email.com"
            required
          />

          <label htmlFor="password">رمز عبور</label>

          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
            placeholder="رمز عبور"
            required
          />

          <button
            type="submit"
            disabled={loading}
          >
            {loading
              ? "در حال ورود..."
              : "ورود"}
          </button>
        </form>

        {message && (
          <p
            className="message"
            role="alert"
          >
            {message}
          </p>
        )}
      </section>
    </main>
  );
}

export default App;