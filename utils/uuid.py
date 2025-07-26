import uuid

def gerar_codigo_unico():
    return str(uuid.uuid4())[:8]