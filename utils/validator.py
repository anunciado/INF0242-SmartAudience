from typing import Tuple
from guardrails.hub import RegexMatch
from guardrails import Guard

class InputValidator:
    """Classe para validação de CPFs e números de processo usando Guardrails."""
    
    def __init__(self):
        # Padrões de regex para validação
        self._CPF_PATTERN = r'^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$'
        self._PROCESSO_PATTERN = r'^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$'
        
        # Criação dos validadores Guardrails
        self.cpf_validator = Guard().use(RegexMatch(self._CPF_PATTERN))
        self.processo_validator = Guard().use(RegexMatch(self._PROCESSO_PATTERN))
    
    def validar_cpf(self, cpf: str) -> Tuple[bool, str]:
        """
        Valida um CPF usando Guardrails e validação de dígitos verificadores.
        
        Args:
            cpf: String contendo o CPF a ser validado
            
        Returns:
            Tupla (bool, str) onde:
            - bool: True se o CPF é válido, False caso contrário
            - str: Mensagem de erro ou CPF formatado
        """
        # Primeiro valida o formato usando Guardrails
        validation_result = self.cpf_validator.validate(cpf)
        if not validation_result.validation_passed:
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
        Valida um número de processo judicial usando Guardrails.
        
        Args:
            processo: String contendo o número do processo a ser validado
            
        Returns:
            Tupla (bool, str) onde:
            - bool: True se o número do processo é válido, False caso contrário
            - str: Mensagem de erro ou número do processo formatado
        """
        # Valida o formato usando Guardrails
        validation_result = self.processo_validator.validate(processo)
        if not validation_result.validation_passed:
            return False, "Formato inválido. Use: NNNNNNN-DD.AAAA.J.TR.OOOO"
        
        # Divide o número do processo em suas partes
        partes = processo.replace('.', '-').split('-')
        
        try:
            numero_base = int(partes[0])
            digito = int(partes[1][:2])
            ano = int(partes[1][3:7])
            justica = int(partes[1][8])
            tribunal = int(partes[1][11:13])
            origem = int(partes[1][14:])
            
            # Validações básicas
            if ano < 1950 or ano > 2100:
                return False, "Ano do processo inválido"
            
            if justica not in range(1, 10):
                return False, "Código da Justiça inválido"
            
            if tribunal < 1:
                return False, "Código do Tribunal inválido"
                
            return True, processo
            
        except ValueError:
            return False, "Número do processo contém valores inválidos"
