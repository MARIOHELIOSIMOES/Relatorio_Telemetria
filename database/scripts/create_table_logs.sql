CREATE TABLE tele.logs
(
    id              SERIAL PRIMARY KEY,

    usuario_id      INTEGER,

    data_hora       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    acao            VARCHAR(300),

    ip              VARCHAR(50),

    detalhes        TEXT,

    CONSTRAINT fk_log_usuario
        FOREIGN KEY(usuario_id)
        REFERENCES tele.usuarios(id)
);