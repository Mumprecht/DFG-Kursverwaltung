export interface Person {
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
}
