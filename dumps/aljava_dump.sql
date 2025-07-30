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

-- Insere transcrições das audiências
INSERT INTO transcricao (id, texto, agendamento_id, data_cadastro) VALUES 
(1, 'Aos 28 dias do mês de julho de 2025, às 09:00 horas, na sala virtual de audiências, realizou-se a audiência do processo 000001-00.2024.4.01.0001. Presentes o MM. Juiz Federal Dr. João Silva, o autor Sr. Pedro Oliveira acompanhado de seu advogado Dr. Carlos Ferreira, e o réu Sr. Roberto Souza. Iniciados os trabalhos, foi proposto acordo entre as partes...', 1, '2025-07-28 09:45:00'),
(2, 'Em 28 de julho de 2025, às 10:00 horas, na sala virtual de audiências, teve início a audiência do processo 000002-00.2024.4.01.0002. Presentes a MM. Juíza Federal Dra. Maria Santos, a autora Sra. Lucia Mendes e seu advogado, e o representante do INSS. Após oitiva das testemunhas...', 2, '2025-07-28 10:55:00'),
(3, 'No dia 28 de julho de 2025, às 14:00 horas, iniciou-se a audiência do processo 000003-00.2024.4.01.0003. Presentes o MM. Juiz Federal Dr. Fernando Lima, o autor Sr. Marcos Pereira, seu advogado Dr. Patricia Santos, e o procurador federal. Foi realizada a oitiva das testemunhas arroladas...', 3, '2025-07-28 14:50:00'),
(4, 'Em 29 de julho de 2025, às 08:00 horas, realizou-se a audiência do processo 000004-00.2024.4.01.0004. Presentes o MM. Juiz Federal Dr. Ricardo Alves, o autor Sr. Bruno Silva e seu advogado, e o representante da União. Iniciados os trabalhos, procedeu-se à tentativa de conciliação...', 4, '2025-07-29 08:45:00'),
(5, 'Aos 29 dias do mês de julho de 2025, às 17:00 horas, na sala virtual de audiências, teve início a audiência do processo 000005-00.2024.4.01.0005. Presentes a MM. Juíza Federal Dra. Beatriz Lima, o autor Sr. Gabriel Santos e seu advogado, e o procurador do município. Foi realizada a instrução processual...', 5, '2025-07-29 17:55:00');

-- Insere impugnações
INSERT INTO impugnacao (id, texto, participante_id, agendamento_id, data_cadastro) VALUES
-- Impugnações da primeira audiência
(1, 'Impugno a transcrição na parte que menciona "acordo entre as partes", pois não houve consenso sobre os termos propostos.', 3, 1, '2025-07-28 09:50:00'),
(2, 'Solicito que conste em ata que o réu se recusou a apresentar documentação solicitada.', 2, 1, '2025-07-28 09:55:00'),

-- Impugnações da segunda audiência
(3, 'Impugno o depoimento da segunda testemunha por contradição com as provas documentais.', 6, 2, '2025-07-28 10:40:00'),
(4, 'Registro divergência quanto ao valor mencionado pelo representante do INSS.', 5, 2, '2025-07-28 10:45:00'),

-- Impugnações da terceira audiência
(5, 'Solicito correção do horário registrado do início da oitiva da primeira testemunha.', 10, 3, '2025-07-28 14:30:00'),
(6, 'Impugno a forma como foi conduzida a inquirição da testemunha principal.', 9, 3, '2025-07-28 14:35:00'),

-- Impugnações da quarta audiência
(7, 'Registro que não foram apresentados os cálculos atualizados conforme determinado.', 13, 4, '2025-07-29 08:30:00'),
(8, 'Impugno a proposta de acordo por não contemplar os juros devidos.', 14, 4, '2025-07-29 08:35:00'),

-- Impugnações da quinta audiência
(9, 'Solicito que conste em ata o protesto quanto à ausência de documentos essenciais.', 17, 5, '2025-07-29 17:40:00'),
(10, 'Impugno o indeferimento da oitiva da testemunha técnica.', 18, 5, '2025-07-29 17:45:00');