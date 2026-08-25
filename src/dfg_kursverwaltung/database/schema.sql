PRAGMA foreign_keys = ON;


-- ============================================================
-- DFG-Kursverwaltung
-- SQLite-Datenbankschema
-- Schema-Version: 5
-- ============================================================


-- ------------------------------------------------------------
-- Schema-Metadaten
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS schema_info (
    version INTEGER NOT NULL
);


-- ------------------------------------------------------------
-- Personen
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS personen (
    id TEXT PRIMARY KEY,

    nachname TEXT NOT NULL,
    vorname TEXT NOT NULL,

    geburtsdatum TEXT,

    email TEXT,

    strasse TEXT,
    hausnummer TEXT,
    plz TEXT,
    ort TEXT,

    organisation TEXT,

    mitglied INTEGER NOT NULL DEFAULT 0,
    ist_teilnehmer INTEGER NOT NULL DEFAULT 0,
    ist_instruktor INTEGER NOT NULL DEFAULT 0,
    aktiv INTEGER NOT NULL DEFAULT 1,

    bemerkungen TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    CHECK (mitglied IN (0, 1)),
    CHECK (ist_teilnehmer IN (0, 1)),
    CHECK (ist_instruktor IN (0, 1)),
    CHECK (aktiv IN (0, 1))
);


-- ------------------------------------------------------------
-- Telefonnummern
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS telefonnummern (
    id TEXT PRIMARY KEY,

    person_id TEXT NOT NULL,

    typ TEXT NOT NULL,
    nummer_e164 TEXT NOT NULL,

    ist_primaer INTEGER NOT NULL DEFAULT 0,

    bemerkungen TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (person_id)
        REFERENCES personen(id)
        ON DELETE CASCADE,

    CHECK (
        typ IN (
            'mobile',
            'private',
            'business',
            'other'
        )
    ),

    CHECK (ist_primaer IN (0, 1))
);


CREATE UNIQUE INDEX IF NOT EXISTS
    idx_telefonnummern_primaer
ON telefonnummern(person_id)
WHERE ist_primaer = 1;


-- ------------------------------------------------------------
-- Drohnen
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS drohnen (
    id TEXT PRIMARY KEY,

    person_id TEXT NOT NULL,

    hersteller TEXT,
    modell TEXT NOT NULL,

    seriennummer TEXT,

    bemerkungen TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (person_id)
        REFERENCES personen(id)
        ON DELETE CASCADE
);


-- ------------------------------------------------------------
-- Lehrgangstypen
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS lehrgangstypen (
    id TEXT PRIMARY KEY,

    bezeichnung TEXT NOT NULL
        COLLATE NOCASE UNIQUE,

    aktiv INTEGER NOT NULL DEFAULT 1,

    bemerkungen TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    CHECK (aktiv IN (0, 1))
);


-- ------------------------------------------------------------
-- Lehrgänge
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS lehrgaenge (
    id TEXT PRIMARY KEY,

    lehrgangstyp_id TEXT NOT NULL,

    bezeichnung TEXT NOT NULL,
    beschreibung TEXT,

    bemerkungen TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (lehrgangstyp_id)
        REFERENCES lehrgangstypen(id)
        ON DELETE RESTRICT
);


-- ------------------------------------------------------------
-- Standorte / Ausführungsorte
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS standorte (
    id TEXT PRIMARY KEY,

    bezeichnung TEXT NOT NULL,

    strasse TEXT,
    hausnummer TEXT,

    plz TEXT,
    ort TEXT,

    kontakt_vorname TEXT,
    kontakt_nachname TEXT,

    telefon_e164 TEXT,
    email TEXT,
    webseite TEXT,

    bemerkungen TEXT,

    aktiv INTEGER NOT NULL DEFAULT 1,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    CHECK (aktiv IN (0, 1))
);


-- ------------------------------------------------------------
-- Kurstage
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS kurstage (
    id TEXT PRIMARY KEY,

    lehrgang_id TEXT NOT NULL,
    standort_id TEXT,

    datum TEXT NOT NULL,

    beginn TEXT,
    ende TEXT,

    bezeichnung TEXT,
    bemerkungen TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (lehrgang_id)
        REFERENCES lehrgaenge(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (standort_id)
        REFERENCES standorte(id)
        ON DELETE RESTRICT,

    CHECK (
        ende IS NULL
        OR beginn IS NULL
        OR ende > beginn
    )
);


-- ------------------------------------------------------------
-- Kurszuordnungen
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS kurszuordnungen (
    id TEXT PRIMARY KEY,

    person_id TEXT NOT NULL,
    kurstag_id TEXT NOT NULL,

    rolle TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'registered',

    bemerkungen TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (person_id)
        REFERENCES personen(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (kurstag_id)
        REFERENCES kurstage(id)
        ON DELETE RESTRICT,

    CHECK (
        rolle IN (
            'participant',
            'instructor'
        )
    ),

    CHECK (
        status IN (
            'registered',
            'attended',
            'absent',
            'cancelled'
        )
    ),

    UNIQUE (
        person_id,
        kurstag_id
    )
);


-- ------------------------------------------------------------
-- Prüfungsergebnisse
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pruefungsergebnisse (
    id TEXT PRIMARY KEY,

    person_id TEXT NOT NULL,
    lehrgang_id TEXT NOT NULL,

    bestanden INTEGER NOT NULL,

    note TEXT,

    bemerkungen TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (person_id)
        REFERENCES personen(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (lehrgang_id)
        REFERENCES lehrgaenge(id)
        ON DELETE RESTRICT,

    CHECK (bestanden IN (0, 1)),

    UNIQUE (
        person_id,
        lehrgang_id
    )
);


-- ============================================================
-- Indizes
-- ============================================================

CREATE INDEX IF NOT EXISTS
    idx_personen_name
ON personen(nachname, vorname);


CREATE INDEX IF NOT EXISTS
    idx_personen_ort
ON personen(ort);


CREATE INDEX IF NOT EXISTS
    idx_personen_mitglied
ON personen(mitglied);


CREATE INDEX IF NOT EXISTS
    idx_personen_teilnehmer
ON personen(ist_teilnehmer);


CREATE INDEX IF NOT EXISTS
    idx_personen_instruktor
ON personen(ist_instruktor);


CREATE INDEX IF NOT EXISTS
    idx_telefonnummern_person
ON telefonnummern(person_id);


CREATE INDEX IF NOT EXISTS
    idx_drohnen_person
ON drohnen(person_id);


CREATE INDEX IF NOT EXISTS
    idx_lehrgangstypen_aktiv
ON lehrgangstypen(aktiv);


CREATE INDEX IF NOT EXISTS
    idx_lehrgaenge_lehrgangstyp
ON lehrgaenge(lehrgangstyp_id);


CREATE INDEX IF NOT EXISTS
    idx_standorte_bezeichnung
ON standorte(bezeichnung);


CREATE INDEX IF NOT EXISTS
    idx_standorte_ort
ON standorte(ort);


CREATE INDEX IF NOT EXISTS
    idx_standorte_aktiv
ON standorte(aktiv);


CREATE INDEX IF NOT EXISTS
    idx_kurstage_lehrgang
ON kurstage(lehrgang_id);


CREATE INDEX IF NOT EXISTS
    idx_kurstage_datum
ON kurstage(datum);


CREATE INDEX IF NOT EXISTS
    idx_kurstage_standort
ON kurstage(standort_id);


CREATE INDEX IF NOT EXISTS
    idx_kurszuordnungen_person
ON kurszuordnungen(person_id);


CREATE INDEX IF NOT EXISTS
    idx_kurszuordnungen_kurstag
ON kurszuordnungen(kurstag_id);


CREATE INDEX IF NOT EXISTS
    idx_kurszuordnungen_rolle
ON kurszuordnungen(rolle);


CREATE INDEX IF NOT EXISTS
    idx_pruefungsergebnisse_person
ON pruefungsergebnisse(person_id);


CREATE INDEX IF NOT EXISTS
    idx_pruefungsergebnisse_lehrgang
ON pruefungsergebnisse(lehrgang_id);