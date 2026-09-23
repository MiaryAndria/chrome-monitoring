import express from 'express';
import cors from 'cors';
import db from './db.js';

const app = express();

app.use(cors());
app.use(express.json());

app.post('/api/ferier', (req, res) => {
    const { libelle, date } = req.body;

    try {
        const stmt = db.prepare(`
            INSERT OR REPLACE INTO ferier
            (libelle, date)
            VALUES (?, ?)
        `);

        stmt.run(libelle, date);
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.get('/api/ferier/:id', (req, res) => {
    const { id } = req.params;

    const ferier = db.prepare(`
        SELECT *
        FROM ferier
        WHERE id = ?
    `).get(id);

    res.json(ferier);
});

app.get('/api/ferier', (req, res) => {
    const rows = db.prepare('SELECT * FROM ferier').all();
    res.json(rows);
});

app.put('/api/ferier/:id', (req, res) => {
    const { id } = req.params;
    const { libelle, date_debut,date_fin } = req.body;

    try {
        const result = db.prepare(`
            UPDATE ferier
            SET libelle = ?, date =?
            WHERE id = ?
        `).run(libelle, date_debut, id);

        res.json({
            success: true,
            message: 'Jour férié mis à jour',
            changes: result.changes
        });
    } catch (e) {
        res.status(500).json({
            error: e.message
        });
    }
});

app.delete('/delete/:id', (req, res) => {
    const { id } = req.params;
    try {
        const stmt = db.prepare(`
            DELETE FROM ferier
            WHERE id = ?
        `);

        const result = stmt.run(id);
        res.json({
            success: true,
            changes: result.changes
        });
    } catch (e) {
        res.status(500).json({
            error: e.message
        });
    }
});

app.delete('/api/reset', (req, res) => {
    try {
        db.exec(`
            DELETE FROM ferier;
            DELETE FROM sqlite_sequence WHERE name = 'ferier'
        `);

        res.json({
            success: true,
            message: 'Données réinitialisées'
        });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.get('/api/liste/mois', (req, res) => {
    const rows = db.prepare('SELECT * FROM mois').all();
    res.json(rows);
})

app.listen(4000, () => {
    console.log('Serveur Express + SQLite sur port 4000');
});