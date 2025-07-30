import uuid

def gerar_codigo_unico():
    """
    Gera um código único aleatório usando UUID.

    Returns:
        str: Uma string contendo os primeiros 8 caracteres de um UUID v4.
              O UUID v4 é gerado aleatoriamente e garante alta probabilidade
              de unicidade.
    """
    return str(uuid.uuid4())[:8]