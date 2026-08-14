CREATE TABLE if not exists tele.usuarios
(
    id              SERIAL PRIMARY KEY,

    nome            VARCHAR(150) NOT NULL,

    usuario         VARCHAR(50) NOT NULL UNIQUE,

    senha           VARCHAR(255) NOT NULL,

    email           VARCHAR(150),

    administrador   BOOLEAN NOT NULL DEFAULT FALSE,

    ativo           BOOLEAN NOT NULL DEFAULT TRUE,

    data_cadastro   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    ultimo_login    TIMESTAMP
);
CREATE INDEX idx_usuario
ON tele.usuarios(usuario);