#!/usr/bin/env python3
"""
Este script testa a conexão com a API do Mercado Pago usando o SDK oficial
"""
import os
import json
import mercadopago

# Token de Acesso para o ambiente de teste
ACCESS_TOKEN = "TEST-2915071579656535-051412-4a9844add009320a3f088ee8af1a03bc-574627484"

def testar_conexao():
    """Testa a conexão básica com a API do Mercado Pago"""
    try:
        sdk = mercadopago.SDK(ACCESS_TOKEN)
        print("✓ SDK inicializado com sucesso")
        return sdk
    except Exception as e:
        print(f"✗ Erro ao inicializar SDK: {e}")
        return None

def criar_preferencia_pagamento(sdk):
    """Cria uma preferência de pagamento de teste"""
    if not sdk:
        return None
    
    # Dados da preferência (mínimo necessário)
    preference_data = {
        "items": [
            {
                "title": "Teste de integração",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 100.0
            }
        ]
    }
    
    try:
        result = sdk.preference().create(preference_data)
        print("✓ Preferência criada com sucesso")
        return result
    except Exception as e:
        print(f"✗ Erro ao criar preferência: {e}")
        return None

def analisar_resposta(response):
    """Analisa a resposta da API"""
    if not response:
        return
    
    print("\n=== ANÁLISE DA RESPOSTA ===")
    
    # Verificar status da resposta
    if "status" in response:
        print(f"Status code: {response['status']}")
    else:
        print("Status code não disponível")
    
    # Verificar se existe o campo response
    if "response" in response:
        print("Campo 'response' encontrado na resposta")
        preference = response["response"]
        
        # Verificar os campos disponíveis na preferência
        print(f"\nCampos disponíveis na preferência: {list(preference.keys())}")
        
        # Verificar campos importantes
        important_fields = ["id", "init_point", "sandbox_init_point"]
        for field in important_fields:
            if field in preference:
                value = preference[field]
                print(f"Campo '{field}': {value}")
            else:
                print(f"Campo '{field}' NÃO encontrado")
    else:
        print("Erro: Campo 'response' não encontrado na resposta")
        print(f"Campos disponíveis: {list(response.keys())}")
    
    # Imprimir a resposta completa formatada
    print("\n=== RESPOSTA COMPLETA ===")
    print(json.dumps(response, indent=2))

def main():
    print("=== TESTE DE INTEGRAÇÃO COM MERCADO PAGO ===")
    sdk = testar_conexao()
    if not sdk:
        print("Não foi possível continuar o teste sem o SDK inicializado")
        return
    
    print("\n--- Criando preferência de pagamento ---")
    response = criar_preferencia_pagamento(sdk)
    
    print("\n--- Analisando resposta ---")
    analisar_resposta(response)

if __name__ == "__main__":
    main()
