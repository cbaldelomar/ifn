

/*
    Creación de base de datos del DW (esquema Staging, Dimensiones y FT, sps, usuario y accesos)
*/

USE master
GO

-- Create login if not exists
IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'my_login')
BEGIN
    PRINT 'Creating login'
    CREATE LOGIN my_login WITH PASSWORD = '123456', CHECK_POLICY = OFF;
    -- , CHECK_EXPIRATION = OFF
END
GO

-- Drop database if exists
IF DB_ID('IndicadoresDW') IS NOT NULL
BEGIN
    PRINT 'Dropping database'

    -- Change the database to single-user mode to force disconnect of all other sessions
    ALTER DATABASE IndicadoresDW SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    
    DROP DATABASE IndicadoresDW;
END
GO

PRINT 'Creating database'

-- Create database
CREATE DATABASE IndicadoresDW
    COLLATE SQL_Latin1_General_CP1_CI_AI
GO

USE IndicadoresDW
GO


/* 
 * SCHEMA: Staging 
 */

CREATE SCHEMA Staging AUTHORIZATION dbo
GO


PRINT 'Creating staging tables'

/* 
 * TABLE: Staging.Datos 
 */

CREATE TABLE Staging.Datos(
    Id             int               IDENTITY(1,1),
    Origen         varchar(20)       NOT NULL,
    Institucion    varchar(100)      NOT NULL,
    Indicador      varchar(100)      NOT NULL,
    Anio           int               NOT NULL,
    Mes            int               NOT NULL,
    Valor          numeric(20, 2)    NOT NULL,
    CONSTRAINT PK_Datos_Id PRIMARY KEY CLUSTERED (Id),
    CONSTRAINT AK_Datos_Origen_Institucion_Indicador_Anio_Mes UNIQUE (Origen, Institucion, Indicador, Anio, Mes)
)
GO


PRINT 'Creating DW tables'

/* 
 * TABLE: Origen 
 */

CREATE TABLE dbo.Origen(
    IdOrigen    int            IDENTITY(1,1),
    Nombre      varchar(20)    NOT NULL,
    CONSTRAINT PK_Origen_IdOrigen PRIMARY KEY CLUSTERED (IdOrigen),
    CONSTRAINT AK_Origen_Nombre UNIQUE (Nombre)
)
GO


/* 
 * TABLE: Institucion 
 */

CREATE TABLE dbo.Institucion(
    IdInstitucion    int             IDENTITY(1,1),
    Nombre           varchar(100)    NOT NULL,
    CONSTRAINT PK_Institucion_IdInstitucion PRIMARY KEY CLUSTERED (IdInstitucion),
    CONSTRAINT AK_Institucion_Nombre UNIQUE (Nombre)
)
GO


/* 
 * TABLE: Indicador 
 */

CREATE TABLE dbo.Indicador(
    IdIndicador    int             IDENTITY(1,1),
    Nombre         varchar(100)    NOT NULL,
    CONSTRAINT PK_Indicador_IdIndicador PRIMARY KEY CLUSTERED (IdIndicador),
    CONSTRAINT AK_Indicador_Nombre UNIQUE (Nombre)
)
GO


/* 
 * TABLE: Periodo 
 */

CREATE TABLE dbo.Periodo(
    IdPeriodo    int    IDENTITY(1,1),
    Anio         int    NOT NULL,
    Mes          int    NOT NULL,
    CONSTRAINT PK_Periodo_IdPeriodo PRIMARY KEY CLUSTERED (IdPeriodo),
    CONSTRAINT AK_Periodo_Anio_Mes UNIQUE (Anio, Mes)
)
GO


/* 
 * TABLE: Valor 
 */
 
CREATE TABLE dbo.Valor(
    IdOrigen         int               NOT NULL,
    IdInstitucion    int               NOT NULL,
    IdIndicador      int               NOT NULL,
    IdPeriodo        int               NOT NULL,
    Monto            numeric(20, 2)    NOT NULL,
    CONSTRAINT PK_Valor_IdOrigen_IdInstitucion_IdIndicador_IdPeriodo PRIMARY KEY CLUSTERED (IdOrigen, IdInstitucion, IdIndicador, IdPeriodo),
    CONSTRAINT FK_Valor_Origen_IdOrigen FOREIGN KEY (IdOrigen) REFERENCES Origen(IdOrigen),
    CONSTRAINT FK_Valor_Institucion_IdInstitucion FOREIGN KEY (IdInstitucion) REFERENCES Institucion(IdInstitucion),
    CONSTRAINT FK_Valor_Indicador_IdIndicador FOREIGN KEY (IdIndicador) REFERENCES Indicador(IdIndicador),
    CONSTRAINT FK_Valor_Periodo_IdPeriodo FOREIGN KEY (IdPeriodo) REFERENCES Periodo(IdPeriodo)
)
GO

CREATE INDEX FK_Valor_Origen_IdOrigen ON Valor(IdOrigen)
CREATE INDEX FK_Valor_Institucion_IdInstitucion ON Valor(IdInstitucion)
CREATE INDEX FK_Valor_Indicador_IdIndicador ON Valor(IdIndicador)
CREATE INDEX FK_Valor_Periodo_IdPeriodo ON Valor(IdPeriodo)
GO


PRINT 'Creating SPs'
GO

/*
dbo.uspFill_DimIndicador
*/
CREATE OR ALTER PROCEDURE dbo.uspFill_DimIndicador
AS
    PRINT 'Procesando DimIndicador ...'

    SELECT DISTINCT
        TRIM(Indicador) AS Indicador
    INTO #Indicadores
    FROM Staging.Datos

    INSERT INTO dbo.Indicador(Nombre)
    SELECT Indicador
    FROM #Indicadores AS O
    WHERE NOT EXISTS(
        SELECT Nombre
        FROM dbo.Indicador
        WHERE Nombre = O.Indicador
    )

    DROP TABLE #Indicadores
GO

/*
dbo.uspFill_DimInstitucion
*/

CREATE OR ALTER PROCEDURE dbo.uspFill_DimInstitucion
AS
    PRINT 'Procesando DimInstitucion ...'

    SELECT DISTINCT
        TRIM(Institucion) AS Institucion
    INTO #Instituciones
    FROM Staging.Datos

    INSERT INTO dbo.Institucion(Nombre)
    SELECT Institucion
    FROM #Instituciones AS O
    WHERE NOT EXISTS(
        SELECT Nombre
        FROM dbo.Institucion
        WHERE Nombre = O.Institucion
    )

    DROP TABLE #Instituciones
GO

/*
EXEC dbo.uspFill_DimOrigen
*/
CREATE OR ALTER PROCEDURE dbo.uspFill_DimOrigen
AS
    PRINT 'Procesando DimOrigen ...'

    SELECT DISTINCT
        TRIM(Origen) AS Origen
    INTO #Origenes
    FROM Staging.Datos

    INSERT INTO dbo.Origen(Nombre)
    SELECT Origen
    FROM #Origenes AS O
    WHERE NOT EXISTS(
        SELECT Nombre
        FROM dbo.Origen
        WHERE Nombre = O.Origen
    )

    DROP TABLE #Origenes
GO

/*
EXEC dbo.uspFill_DimPeriodo
*/
CREATE OR ALTER PROCEDURE dbo.uspFill_DimPeriodo
AS
    PRINT 'Procesando DimPeriodo ...'

    SELECT DISTINCT Anio, Mes
    INTO #Periodos
    FROM Staging.Datos

    INSERT INTO dbo.Periodo(Anio, Mes)
    SELECT Anio, Mes
    FROM #Periodos AS O
    WHERE NOT EXISTS(
        SELECT Anio, Mes
        FROM dbo.Periodo
        WHERE Anio = O.Anio
            AND Mes = O.Mes
    )
    ORDER BY Anio, Mes

    DROP TABLE #Periodos
GO

/*
EXEC dbo.uspFill_FTValor
*/
CREATE OR ALTER PROCEDURE dbo.uspFill_FTValor
AS
    PRINT 'Procesando FTValor ...'

    SELECT
        O.IdOrigen,
        I.IdInstitucion,
        N.IdIndicador,
        P.IdPeriodo,
        S.Valor
    INTO #Valores
    FROM Staging.Datos AS S
    INNER JOIN dbo.Origen AS O
        ON S.Origen = O.Nombre
    INNER JOIN dbo.Institucion AS I
        ON S.Institucion = I.Nombre
    INNER JOIN dbo.Indicador AS N
        ON S.Indicador = N.Nombre
    INNER JOIN dbo.Periodo AS P
        ON S.Anio = P.Anio AND S.Mes = P.Mes


    MERGE dbo.Valor AS T
    USING #Valores AS S
        ON T.IdOrigen = S.IdOrigen
            AND T.IdInstitucion = S.IdInstitucion
            AND T.IdIndicador = S.IdIndicador
            AND T.IdPeriodo = S.IdPeriodo

    WHEN MATCHED AND T.Monto != S.Valor
    THEN
        UPDATE SET T.Monto = S.Valor

    WHEN NOT MATCHED
    THEN
        INSERT (IdOrigen, IdInstitucion, IdIndicador, IdPeriodo, Monto)
        VALUES (S.IdOrigen, S.IdInstitucion, S.IdIndicador, S.IdPeriodo, S.Valor);
GO

/*
Permisos
*/
PRINT 'Creating user'
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE type = 'S' AND name = 'my_user')
BEGIN
    CREATE USER my_user FOR LOGIN my_login;
END
GO

PRINT 'Creating rol'
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE type = 'R' AND name = 'LoadDataRole')
BEGIN
    CREATE ROLE LoadDataRole
END
GO

GRANT INSERT ON Staging.Datos TO LoadDataRole;
GRANT DELETE ON Staging.Datos TO LoadDataRole;
-- FOR TRUNCATE
GRANT ALTER ON Staging.Datos TO LoadDataRole;

GRANT EXEC ON dbo.uspFill_DimOrigen TO LoadDataRole
GRANT EXEC ON dbo.uspFill_DimInstitucion TO LoadDataRole
GRANT EXEC ON dbo.uspFill_DimIndicador TO LoadDataRole
GRANT EXEC ON dbo.uspFill_DimPeriodo TO LoadDataRole
GRANT EXEC ON dbo.uspFill_FTValor TO LoadDataRole;
GO

-- Add role to user
ALTER ROLE LoadDataRole ADD MEMBER my_user;
GO