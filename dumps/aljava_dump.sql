-- Insere processos
INSERT INTO processo (id, numero, data_cadastro) VALUES (1, '000001-00.2024.4.01.0001', '2024-01-01T10:00:00');
INSERT INTO processo (id, numero, data_cadastro) VALUES (2, '000002-00.2024.4.01.0002', '2024-02-15T11:30:00');
INSERT INTO processo (id, numero, data_cadastro) VALUES (3, '000003-00.2024.4.01.0003', '2024-03-20T09:45:00');

-- Insere arquivos (com nomes como '1.pdf', '2.jpg', etc)
INSERT INTO arquivo (id, nome, caminho) VALUES (1, '1.pdf', '/midias/1.pdf');
INSERT INTO arquivo (id, nome, caminho) VALUES (2, '2.jpg', '/midias/2.jpg');
INSERT INTO arquivo (id, nome, caminho) VALUES (3, '3.mp3', '/midias/3.mp3');
INSERT INTO arquivo (id, nome, caminho) VALUES (4, '4.pdf', '/midias/4.pdf');

-- Relaciona os arquivos aos processos
INSERT INTO processo_arquivo (id, processo_id, arquivo_id) VALUES (1, 1, 1);  -- 1.pdf -> processo 1
INSERT INTO processo_arquivo (id, processo_id, arquivo_id) VALUES (2, 1, 2);  -- 2.jpg -> processo 1
INSERT INTO processo_arquivo (id, processo_id, arquivo_id) VALUES (3, 2, 3);  -- 3.mp3 -> processo 2
INSERT INTO processo_arquivo (id, processo_id, arquivo_id) VALUES (4, 3, 4);  -- 4.pdf -> processo 3
