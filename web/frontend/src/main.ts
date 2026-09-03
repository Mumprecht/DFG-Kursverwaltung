import "./style.css";

type HealthResponse = {
    status: string;
    application: string;
};

type Person = {
    id: string;

    nachname: string;
    vorname: string;

    geburtsdatum: string | null;
    email: string | null;

    strasse: string | null;
    hausnummer: string | null;
    plz: string | null;
    ort: string | null;

    organisation: string | null;

    mitglied: boolean;
    ist_teilnehmer: boolean;
    ist_instruktor: boolean;
    aktiv: boolean;

    bemerkungen: string | null;

    created_at: string | null;
    updated_at: string | null;
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

            <section class="persons-section">
                <h2>Personen</h2>

                <div id="personen-status" class="list-status">
                    Personen werden geladen …
                </div>

                <div id="personen-list"></div>
            </section>
        </section>
    </main>
`;

const statusElement =
    document.querySelector<HTMLSpanElement>("#backend-status");

const personenStatusElement =
    document.querySelector<HTMLDivElement>("#personen-status");

const personenListElement =
    document.querySelector<HTMLDivElement>("#personen-list");

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

function createRoleText(person: Person): string {
    const roles: string[] = [];

    if (person.ist_teilnehmer) {
        roles.push("Teilnehmer");
    }

    if (person.ist_instruktor) {
        roles.push("Instruktor");
    }

    if (roles.length === 0) {
        return "Keine Kursrolle";
    }

    return roles.join(", ");
}

function renderPersonen(personen: Person[]): void {
    if (!personenListElement) {
        return;
    }

    if (personen.length === 0) {
        personenListElement.innerHTML =
            `<p class="empty-state">Keine Personen vorhanden.</p>`;
        return;
    }

    personenListElement.innerHTML = `
        <div class="personen-table-wrapper">
            <table class="personen-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>E-Mail</th>
                        <th>Organisation</th>
                        <th>Fachliche Rolle</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${personen
                        .map(
                            (person) => `
                                <tr>
                                    <td>
                                        ${person.vorname}
                                        ${person.nachname}
                                    </td>
                                    <td>
                                        ${person.email ?? "–"}
                                    </td>
                                    <td>
                                        ${person.organisation ?? "–"}
                                    </td>
                                    <td>
                                        ${createRoleText(person)}
                                    </td>
                                    <td>
                                        ${person.aktiv ? "Aktiv" : "Inaktiv"}
                                    </td>
                                </tr>
                            `
                        )
                        .join("")}
                </tbody>
            </table>
        </div>
    `;
}

async function loadPersonen(): Promise<void> {
    if (!personenStatusElement) {
        return;
    }

    try {
        const response = await fetch(
            "http://localhost:3000/api/personen"
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const personen =
            (await response.json()) as Person[];

        personenStatusElement.textContent =
            `${personen.length} Person(en) geladen`;

        personenStatusElement.classList.remove(
            "error"
        );

        renderPersonen(personen);
    } catch (error) {
        console.error(error);

        personenStatusElement.textContent =
            "Personen konnten nicht geladen werden";

        personenStatusElement.classList.add(
            "error"
        );
    }
}

void checkBackend();
void loadPersonen();
