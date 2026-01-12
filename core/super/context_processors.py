from core.super.models import Cart

def cart_count_processor(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            # Retornamos el conteo de items (productos únicos)
            return {'cart_count': cart.get_item_count()}
        except Cart.DoesNotExist:
            return {'cart_count': 0}
    return {'cart_count': 0}