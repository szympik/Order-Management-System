const API_URL = 'http://localhost:8000';
let editingOrderId = null;

async function loadOrders() {
    try {
        const response = await fetch(`${API_URL}/orders`);
        const orders = await response.json();
        
        // Ustaw status na zielony jeśli połączenie działa
        document.getElementById('statusIndicator').textContent = '🟢';
        
        const tbody = document.getElementById('ordersBody');
        tbody.innerHTML = '';
        
        if (orders.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="no-orders">Brak zamówień</td></tr>';
            updateStats(0, 0);
            return;
        }
        
        let totalValue = 0;
        orders.forEach(order => {
            totalValue += parseFloat(order.price);
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${order.id}</td>
                <td>${order.user_name}</td>
                <td>${order.product}</td>
                <td>${parseFloat(order.price).toFixed(2)} zł</td>
                <td>${new Date(order.created_at).toLocaleString('pl-PL')}</td>
                <td>
                    <button class="btn-small btn-edit" onclick="editOrder(${order.id})">Edytuj</button>
                    <button class="btn-small btn-delete" onclick="deleteOrder(${order.id})">Usuń</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
        
        updateStats(orders.length, totalValue);
    } catch (error) {
        console.error('Błąd ładowania zamówień:', error);
        // Ustaw status na czerwony jeśli błąd połączenia
        document.getElementById('statusIndicator').textContent = '🔴';
        document.getElementById('ordersBody').innerHTML = '<tr><td colspan="6" class="no-orders">Brak połączenia z serwerem</td></tr>';
        updateStats(0, 0);
    }
}

function updateStats(count, total) {
    document.getElementById('totalOrders').textContent = count;
    document.getElementById('totalValue').textContent = total.toFixed(2) + ' zł';
}

async function createOrder(event) {
    event.preventDefault();
    
    const orderData = {
        user: document.getElementById('userName').value,
        product: document.getElementById('product').value,
        price: parseFloat(document.getElementById('price').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });
        
        if (response.ok) {
            document.getElementById('orderForm').reset();
            showSuccess('Zamówienie zostało dodane!');
            loadOrders();
        }
    } catch (error) {
        console.error('Błąd tworzenia zamówienia:', error);
        alert('Błąd podczas tworzenia zamówienia');
    }
}

async function editOrder(id) {
    try {
        const response = await fetch(`${API_URL}/orders`);
        const orders = await response.json();
        const order = orders.find(o => o.id === id);
        
        if (order) {
            editingOrderId = id;
            document.getElementById('editUserName').value = order.user_name;
            document.getElementById('editProduct').value = order.product;
            document.getElementById('editPrice').value = order.price;
            document.getElementById('editModal').classList.add('active');
        }
    } catch (error) {
        console.error('Błąd ładowania zamówienia:', error);
    }
}

function closeEditModal() {
    document.getElementById('editModal').classList.remove('active');
    editingOrderId = null;
}

async function saveEdit(event) {
    event.preventDefault();
    
    const orderData = {
        user: document.getElementById('editUserName').value,
        product: document.getElementById('editProduct').value,
        price: parseFloat(document.getElementById('editPrice').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/orders/${editingOrderId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });
        
        if (response.ok) {
            closeEditModal();
            showSuccess('Zamówienie zostało zaktualizowane!');
            loadOrders();
        }
    } catch (error) {
        console.error('Błąd aktualizacji zamówienia:', error);
        alert('Błąd podczas aktualizacji zamówienia');
    }
}

async function deleteOrder(id) {
    if (!confirm('Czy na pewno chcesz usunąć to zamówienie?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/orders/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showSuccess('Zamówienie zostało usunięte!');
            loadOrders();
        }
    } catch (error) {
        console.error('Błąd usuwania zamówienia:', error);
        alert('Błąd podczas usuwania zamówienia');
    }
}

function showSuccess(message) {
    const successDiv = document.getElementById('successMessage');
    successDiv.textContent = message;
    successDiv.classList.add('show');
    setTimeout(() => {
        successDiv.classList.remove('show');
    }, 3000);
}

// Inicjalizacja
document.addEventListener('DOMContentLoaded', () => {
    loadOrders();
    setInterval(loadOrders, 3000);
});
