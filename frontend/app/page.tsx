const questions = [
  "How much money do I have?",
  "Where is my money going?",
  "What does a normal month cost me?",
  "What changed this month?",
];

export default function Home() {
  return (
    <main className="mx-auto min-h-screen max-w-5xl px-6 py-16">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">
        Local-first
      </p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight">Personal Finance</h1>
      <p className="mt-4 max-w-2xl text-lg text-slate-600">
        The foundation is running. Add sanitized bank fixtures to complete CSV ingestion, then
        build deterministic analytics on verified local data.
      </p>
      <section className="mt-12 grid gap-4 sm:grid-cols-2">
        {questions.map((question) => (
          <article key={question} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="font-medium">{question}</h2>
            <p className="mt-2 text-sm text-slate-500">Waiting for imported account data</p>
          </article>
        ))}
      </section>
    </main>
  );
}

