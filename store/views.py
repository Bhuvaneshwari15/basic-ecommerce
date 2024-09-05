# views.py

from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import Product, Category
from .utils import cartData, guestOrder

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()

    # Handle search query
    query = request.GET.get('q')
    if query:
        searched_products = bfs_search(products, query)
        context = {'products': searched_products, 'cartItems': cartItems}
    else:
        context = {'products': products, 'cartItems': cartItems}

    return render(request, 'store/store.html', context)

def bfs_search(products, query):
    # Perform BFS search on products by name
    matched_products = []
    queue = list(products)

    while queue:
        current_product = queue.pop(0)  # Dequeue
        # Search condition (case insensitive)
        if query.lower() in current_product.name.lower():
            matched_products.append(current_product)
        # You can add more conditions or search criteria here

    return matched_products

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Category.objects.create(name=name)
        return redirect('category_list')
    return render(request, 'category_form.html')

def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.save()
        return redirect('category_list')
    return render(request, 'category_form.html', {'category': category})

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'category_confirm_delete.html', {'category': category})

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()

    # Handle search query
    query = request.GET.get('q')
    if query:
        searched_products = Product.objects.filter(name__icontains=query)
        context = {'products': searched_products, 'cartItems': cartItems, 'query': query}
    else:
        context = {'products': products, 'cartItems': cartItems}

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # AJAX request, return JSON response
        data = {
            'products': list(searched_products.values()),  # Convert QuerySet to list for JSON serialization
            'cartItems': cartItems,
            'query': query
        }
        return JsonResponse(data)

    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    # Get the current customer or create a guest customer
    if request.user.is_authenticated:
        customer = request.user.customer
    else:
        customer, order = guestOrder(request, data)

    # Get the product object
    product = get_object_or_404(Product, id=productId)

    # Get or create the order for the current customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    # Get or create the order item for the given product in the current order
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    # Update the quantity based on the action (add or remove)
    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    # Delete the order item if quantity drops to zero or below
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)