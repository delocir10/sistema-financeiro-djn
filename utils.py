def format_currency(value):
    """Formata um número float para o formato de moeda brasileiro (R$)."""
    if value is None:
        return "R$ 0,00"
    
    # Formata com 2 casas decimais e separador de milhar americano
    formatted = f"R$ {value:,.2f}"
    
    # Troca as vírgulas (milhar) por um placeholder, o ponto (decimal) por vírgula, e o placeholder por ponto
    formatted = formatted.replace(',', 'X')
    formatted = formatted.replace('.', ',')
    formatted = formatted.replace('X', '.')
    
    return formatted
