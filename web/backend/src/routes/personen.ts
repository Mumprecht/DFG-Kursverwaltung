import { Router } from "express";
import type { Person } from "../models/person.js";

const router = Router();

const personen: Person[] = [
    {
        id: "test-person-1",
        nachname: "Muster",
        vorname: "Anna",
        geburtsdatum: "2000-05-10",
        email: "anna.muster@example.com",
        strasse: "Musterstrasse",
        hausnummer: "10",
        plz: "8000",
        ort: "Zürich",
        organisation: null,
        mitglied: true,
        ist_teilnehmer: true,
        ist_instruktor: false,
        aktiv: true,
        bemerkungen: null,
        created_at: null,
        updated_at: null,
    },
    {
        id: "test-person-2",
        nachname: "Beispiel",
        vorname: "Peter",
        geburtsdatum: null,
        email: "peter.beispiel@example.com",
        strasse: null,
        hausnummer: null,
        plz: null,
        ort: null,
        organisation: "DFG Pfannenstiel",
        mitglied: true,
        ist_teilnehmer: false,
        ist_instruktor: true,
        aktiv: true,
        bemerkungen: null,
        created_at: null,
        updated_at: null,
    },
];

router.get("/", (_req, res) => {
    res.json(personen);
});

export default router;
