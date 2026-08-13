function Dashboard({ onLogout, onOpenDocuments }) {
  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div className="brand">
          <div className="brand-mark">S</div>

          <div>
            <h1>Studyio</h1>
            <p>دستیار مطالعه هوشمند</p>
          </div>
        </div>

        <button
          className="logout-button"
          onClick={onLogout}
        >
          خروج
        </button>
      </header>

      <section className="dashboard-content">
        <div className="welcome-section">
          <p className="eyebrow">داشبورد مطالعه</p>

          <h2>خوش اومدی 👋</h2>

          <p>
            اسناد درسی خودت را اضافه کن و با کمک هوش مصنوعی مطالعه کن.
          </p>
        </div>

        <div className="dashboard-grid">
          <article className="dashboard-card">
            <div className="card-icon">📚</div>

            <h3>اسناد من</h3>

            <p>
              فایل‌ها و متن‌های درسی خودت را مدیریت کن.
            </p>

            <button onClick={onOpenDocuments}>
              مشاهده اسناد
            </button>
          </article>
        </div>
      </section>
    </main>
  );
}

export default Dashboard;
