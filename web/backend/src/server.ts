import express from "express";
import cors from "cors";

const app = express();
const port = 3000;

app.use(cors());
app.use(express.json());

app.get("/api/health", (_req, res) => {
    res.json({
        status: "ok",
        application: "DFG-Kursverwaltung",
    });
});

app.listen(port, () => {
    console.log(
        `DFG-Kursverwaltung Backend läuft auf http://localhost:${port}`
    );
});
