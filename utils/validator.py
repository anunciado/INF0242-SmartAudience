import re
from typing import Tuple

class InputValidator:
    """Classe para validação de CPFs e números de processo usando regex."""
    
    def __init__(self):
        # Padrões de regex para validação
        self._CPF_PATTERN = r'^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$'
        self._PROCESSO_PATTERN = r'^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$'
        
        # Compilação dos padrões regex para melhor performance
        self._cpf_regex = re.compile(self._CPF_PATTERN)
        self._processo_regex = re.compile(self._PROCESSO_PATTERN)
    
    def validar_cpf(self, cpf: str) -> Tuple[bool, str]:
        """
        Valida um CPF usando regex e validação de dígitos verificadores.
        
        Args:
            cpf: String contendo o CPF a ser validado
            
        Returns:
            Tupla (bool, str) onde:
            - bool: True se o CPF é válido, False caso contrário
            - str: Mensagem de erro ou CPF formatado
        """
        # Primeiro valida o formato usando regex
        if not self._cpf_regex.match(cpf):
            return False, "Formato de CPF inválido. Use: XXX.XXX.XXX-XX"
        
        # Remove caracteres não numéricos para validação dos dígitos
        numeros = ''.join(filter(str.isdigit, cpf))
        
        # Verifica se todos os dígitos são iguais
        if len(set(numeros)) == 1:
            return False, "CPF inválido: todos os dígitos são iguais"
        
        # Calcula o primeiro dígito verificador
        soma = 0
        for i in range(9):
            soma += int(numeros[i]) * (10 - i)
        resto = 11 - (soma % 11)
        digito1 = resto if resto < 10 else 0
        
        # Calcula o segundo dígito verificador
        soma = 0
        for i in range(10):
            soma += int(numeros[i]) * (11 - i)
        resto = 11 - (soma % 11)
        digito2 = resto if resto < 10 else 0
        
        # Verifica se os dígitos calculados são iguais aos do CPF
        if int(numeros[9]) != digito1 or int(numeros[10]) != digito2:
            return False, "CPF inválido: dígitos verificadores incorretos"
        
        # Formata o CPF
        cpf_formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        return True, cpf_formatado
    
    def validar_processo(self, processo: str) -> Tuple[bool, str]:
        """
        Valida um número de processo judicial usando regex.
        
        Args:
            processo: String contendo o número do processo a ser validado
            
        Returns:
            Tupla (bool, str) onde:
            - bool: True se o número do processo é válido, False caso contrário
            - str: Mensagem de erro ou número do processo formatado
        """
        # Valida o formato usando regex
        if not self._processo_regex.match(processo):
            return False, "Formato inválido. Use: NNNNNNN-DD.AAAA.J.TR.OOOO"

        return True, processo