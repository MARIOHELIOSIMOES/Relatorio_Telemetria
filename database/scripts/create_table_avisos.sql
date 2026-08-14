CREATE TABLE tele.avisos
(
    id                  SERIAL PRIMARY KEY,

    titulo              VARCHAR(200) NOT NULL,

    texto               TEXT NOT NULL,

    usuario_id          INTEGER NOT NULL,

    data_criacao        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    ativo               BOOLEAN NOT NULL DEFAULT TRUE,

    data_inativacao     TIMESTAMP,

    usuario_inativacao  INTEGER,

    CONSTRAINT fk_aviso_usuario
        FOREIGN KEY(usuario_id)
        REFERENCES tele.usuarios(id),

    CONSTRAINT fk_aviso_usuario_inativacao
        FOREIGN KEY(usuario_inativacao)
        REFERENCES tele.usuarios(id)
);