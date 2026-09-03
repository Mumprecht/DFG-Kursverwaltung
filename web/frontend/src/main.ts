import "./style.css";

type HealthResponse = {
    status: string;
    application: string;
};

const app = document.querySelector<HTMLDivElement>("#app");

if (!app) {
    throw new Error("Element #app wurde nicht gefunden.");
}

app.innerHTML = `
    <main class="page">
        <section class="card">
            <h1>DFG-Kursverwaltung</h1>
            <p class="subtitle">
                Webanwendung
            </p>

            <div class="status-box">
                <span class="status-label">Backend-Status</span>
                <span id="backend-status" class="status-value pending">
                    Wird geprüft …
                </span>
            </div>
        </section>
    </main>
`;

const statusElement =
    document.querySelector<HTMLSpanElement>("#backend-status");

async function checkBackend(): Promise<void> {
    if (!statusElement) {
        return;
    }

    try {
        const response = await fetch(
            "http://localhost:3000/api/health"
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            (await response.json()) as HealthResponse;

        statusElement.textContent =
            `${data.application}: ${data.status}`;

        statusElement.classList.remove(
            "pending",
            "error"
        );

        statusElement.classList.add(
            "success"
        );
    } catch (error) {
        console.error(error);

        statusElement.textContent =
            "Backend nicht erreichbar";

        statusElement.classList.remove(
            "pending",
            "success"
        );

        statusElement.classList.add(
            "error"
        );
    }
}

void checkBackend();
