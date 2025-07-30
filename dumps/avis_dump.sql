-- Insere agendamentos válidos em horários permitidos (úteis, entre 08:00 e 18:00)
INSERT INTO agendamento (numero_processo, data_inicio, data_fim, data_cadastro) VALUES
('000001-00.2024.4.01.0001', '2025-07-28 09:00', '2025-07-28 10:00', '2025-07-25 10:00'),
('000002-00.2024.4.01.0002', '2025-07-28 10:00', '2025-07-28 11:00', '2025-07-25 10:10'),
('000003-00.2024.4.01.0003', '2025-07-28 14:00', '2025-07-28 15:00', '2025-07-25 10:20'),
('000004-00.2024.4.01.0004', '2025-07-29 08:00', '2025-07-29 09:00', '2025-07-25 10:30'),
('000005-00.2024.4.01.0005', '2025-07-29 17:00', '2025-07-29 18:00', '2025-07-25 10:40');

-- Insere participantes para cada agendamento com códigos únicos
INSERT INTO participante (nome, cpf, agendamento_id, presente, codigo_unico) VALUES
-- Agendamento 1
('João Silva', '123.456.789-00', 1, true, '8f3d9a2e'),
('Maria Santos', '987.654.321-00', 1, true, '4b7c5d1a'),
('Pedro Oliveira', '111.222.333-44', 1, false, '2e6f8b9c'),
('Ana Paula', '444.555.666-77', 1, true, '9a3c5e7d'),

-- Agendamento 2
('Carlos Ferreira', '222.333.444-55', 2, true, '1d5b8f4a'),
('Lucia Mendes', '555.666.777-88', 2, true, '7e2c9d6b'),
('Roberto Souza', '888.999.000-11', 2, true, '3f8a4c2e'),
('Julia Costa', '123.321.456-78', 2, false, '6b9d5a3f'),

-- Agendamento 3
('Fernando Lima', '777.888.999-00', 3, true, '5c7a2e8b'),
('Patricia Santos', '666.555.444-33', 3, true, '8d4f6a1c'),
('Marcos Pereira', '333.222.111-00', 3, true, '2b5e9c7d'),
('Clara Oliveira', '999.888.777-66', 3, false, '4a8c3b6e'),

-- Agendamento 4
('Ricardo Alves', '444.333.222-11', 4, true, '7d1f5b9a'),
('Amanda Costa', '111.999.888-77', 4, true, '3e8b6c2a'),
('Bruno Silva', '222.888.777-66', 4, false, '9c4d7a5f'),
('Carla Santos', '555.444.333-22', 4, true, '1b6e8d4c'),

-- Agendamento 5
('Eduardo Martins', '666.777.888-99', 5, true, '5a9f2c7b'),
('Beatriz Lima', '999.000.111-22', 5, true, '8c3e6d4a'),
('Gabriel Santos', '777.666.555-44', 5, true, '2d7b5f9e'),
('Daniela Costa', '444.555.666-88', 5, false, '6f1a4c8b');