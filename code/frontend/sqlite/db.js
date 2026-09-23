import Database from 'better-sqlite3';

const db = new Database(
    'C:/Users/miary/Etude/EvalDev/Eval3/NewApp/data/base.db'
);

db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

db.exec(`
    CREATE TABLE IF NOT EXISTS ferier (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        libelle TEXT
    )
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS mois (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE
    )
`);

// db.exec(`DROP TABLE mois`);
// db.exec(`DROP TABLE ferier `);


// db.exec(`
//     INSERT OR IGNORE INTO mois (date) VALUES
//         ('Janvier'),
//         ('Fevrier'),
//         ('Mars'),
//         ('Avril'),
//         ('Mai'),
//         ('Juin'),
//         ('Juillet'),
//         ('Aout'),
//         ('Septembre'),
//         ('Octobre'),
//         ('Novembre'),
//         ('Decembre');
// `)

// db.exec(`DELETE FROM mois`);
// db.exec(`DELETE FROM sqlite_sequence WHERE name = 'mois'`);

console.log('Base SQLite initialisée');

export default db;