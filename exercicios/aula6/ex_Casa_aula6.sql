CREATE TABLE autor(
    autor_id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL
);

CREATE TABLE livro (
    livro_id INTEGER PRIMARY KEY, 
    nome TEXT NOT NULL, 
    nota FLOAT NOT NULL,
    autor_id INTEGER NOT NULL,

    FOREIGN KEY (autor_id) REFERENCES autor(autor_id)
);