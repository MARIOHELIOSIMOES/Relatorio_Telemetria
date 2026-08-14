CREATE TABLE tele.relatorios
(
    id              SERIAL PRIMARY KEY,

    usuario_id      INTEGER NOT NULL,

    data_hora       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    turno           CHAR(1) NOT NULL,

    descricao       TEXT NOT NULL,

    CONSTRAINT fk_relatorio_usuario
        FOREIGN KEY(usuario_id)
        REFERENCES tele.usuarios(id)
);